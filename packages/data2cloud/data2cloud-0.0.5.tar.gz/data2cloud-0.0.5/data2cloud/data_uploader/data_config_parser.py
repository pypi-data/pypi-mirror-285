from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from jsonschema import validate
import pandas as pd


@dataclass
class DataType:
    type: str
    location: str


@dataclass
class DataVersion:
    source: str
    versions: List[str]
    is_new_source: Optional[bool] = True


@dataclass
class Meta:
    col_order: int
    col_name: str
    col_type: str
    col_name_desc: str
    col_unit: str
    col_desc: str


@dataclass
class DataConfig:
    source: str
    target_table: str
    """ target ods table name, default to ods_{vender}_{source} if ignored"""
    source_name: str
    meta_table:str
    meta: List[Meta]

@dataclass
class MatrixConfig:
    source: str
    source_col_prefix:Union[str,List[str]]
    eff_date_col:str
    firm_col:str
    target_code_prefix: Optional[str] = None
    filter:str = ""
    unit_filter :List[str]  = field(default_factory=list)
    deduplicate_by_eff_date:bool = False


class DataConfigParser:

    versions: List[str]

    def __init__(self, config_file: str):
        self._config_file = config_file
        schema_file = f"{Path(__file__).resolve().parent.parent}/schemas/json/data-config-schema.json"
        schema = json.load(open(schema_file, encoding="utf-8", mode="r"))
        config_data= json.load(open(config_file, encoding="utf-8", mode="r"))
        validate(instance=config_data, schema=schema)
        self._config_json=config_data
        self.vender = self._config_json["vender"]
        self.meta_table = self._config_json["meta_table"]
        self.data_type = DataType(
            self._config_json["data_type"]["type"], self._config_json["data_type"]["location"]
        )
        self.data_versions = {
            x["source"]: DataVersion(x["source"], x["versions"])
            for x in self._config_json["data_versions"]
        }
        self._parse_data_config()
        self._parse_matrix_config()
        
    def _parse_data_config(self):
        self.data_configs: Dict[str, DataConfig] = {}
        for d in self._config_json["data"]:
            source = d["source"]
            # default ods name if not set the target table
            target_table = d.get("target_table", f"ods_{self.vender}_{d["source"]}")
            source_name = d["source_name"]
            meta = [
                Meta(
                    m["col_order"],
                    m["col_name"],
                    m["col_type"],
                    m["col_name_desc"],
                    m.get("col_unit", "unknown"),
                    m.get("col_desc", "no desc"),
                )
                for m in d["meta"]
            ]
            self.data_configs[source] = DataConfig(
                source, target_table, source_name, self.meta_table, meta
            )

    def _parse_matrix_config(self):
        matrix= self._config_json.get("matrix",[])
        self.matrix_configs: Dict[str, MatrixConfig] = {}
        if matrix:
            for m in matrix:
                self.matrix_configs[m["source"]] = MatrixConfig(
                    m["source"],
                    source_col_prefix=m.get("source_col_prefix"),
                    eff_date_col=m.get("eff_date_col")
                    ,firm_col=m.get("firm_col"),
                    target_code_prefix=m.get("target_code_prefix", m["source"]),
                    filter=m.get("filter"),
                    unit_filter=m.get("unit_filter"),
                    deduplicate_by_eff_date=m.get("deduplicate_by_eff_date",False)
                )

    def get_matrix(self, source) -> Optional[MatrixConfig]:   
        m = self.matrix_configs.get(source) 
        return m

    def get_config(self, source: str)->DataConfig:
        config = self.data_configs.get(source)
        if not config:
            raise Exception(f"not data config found for '{source}'")
        return config

    def get_versions(self,source:str)->DataVersion:
        vers = self.data_versions.get(source)
        if not vers:
            raise Exception(f"no version info found for source:'{source}'")
        return vers

    def get_meta_table_create_sql(self):
        return f"""
                CREATE TABLE IF NOT EXISTS {self.meta_table} (
                source_name STRING COMMENT '该表在数据源中的名称',
                ods_table_name STRING COMMENT '数据在MaxCompute里的ods表名',
                col_order STRING COMMENT '序号',
                col_name STRING COMMENT '字段',
                col_dtype STRING COMMENT '数据类型',
                col_name_ch STRING COMMENT '字段标题',
                col_unit STRING COMMENT '单位',
                col_desc STRING COMMENT '字段说明'
            ) 
            PARTITIONED BY (source STRING);"""
    def get_meta_sql(self,source):
        self.meta_fields = [
            "col_order",
            "col_name",
            "col_type",
            "col_name_desc",
            "col_unit",
            "col_desc",
        ]
        config = self.get_config(source)
        values_clause = {}
        for x in config.meta:
                values_clause[x.col_name] = (
                    f"({','.join(f'"{str(getattr(x, attr))}"' for attr in self.meta_fields)})"
                )
        matrix_meta_sql = f"(SELECT * FROM (VALUES\n{','.join(values_clause.values())}\n) AS ({', '.join(self.meta_fields)}))"
        return matrix_meta_sql

    def get_meta_df(self,source:str):
        config = self.get_config(source)
        return pd.DataFrame(config.meta)

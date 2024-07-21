##@resource_reference{"manifest.py"}

from typing import List
from odps.models import Table
from odps.errors import NoSuchObject
from data2cloud.cloud.maxcompute import SqlRunner, MaxcomputeSetup as MC
from .data_config_parser import DataConfig, DataConfigParser, DataVersion, Meta


class DataUploader:

    versions: List[str]

    def __init__(self, config_file: str):

        self.parser = DataConfigParser(config_file)

    def _get_field_definition(self, meta: List[Meta]):

        defining_fields = ",\n".join(
            [f"{col.col_name} STRING COMMENT '{col.col_name_desc}'" for col in meta]
        )
        # print(defining_fields)
        return defining_fields

    def _get_fields(self, meta: List[Meta]):
        fields = ",".join([f"{col.col_name}" for col in meta])
        # print(fields)
        return fields

    def _get_ext_tbl_name(self, config: DataConfig, version: str):
        ext_tbl_name = f"ods_{self.parser.vender}_{config.source}_{version}_external"
        return ext_tbl_name

    def _get_create_tbl_ext_sql(self, config: DataConfig, version: str):
        ext_tbl_name = self._get_ext_tbl_name(config, version)
        sql = f"""drop table if exists {ext_tbl_name};
        create external table {ext_tbl_name}
            (
            {self._get_field_definition(config.meta)}
            )
            stored by 'com.aliyun.odps.CsvStorageHandler' 
            with serdeproperties (
            'odps.text.option.use.quote' = 'true',
            'odps.sql.text.schema.mismatch.mode' = 'error',
            'odps.text.option.header.lines.count' = '1'
            ) 
            location '{self.parser.data_type.location}/{config.source}/{version}/'
            lifecycle 1;
        """
        return sql

    def _get_create_tbl_ods_sql(self, config: DataConfig):
        sql_create = f"""
            create table if not exists {config.target_table}
            (
            {self._get_field_definition(config.meta)}
            )
            COMMENT '{config.source_name}'
            partitioned by (pt STRING)
            lifecycle 36500;
            """
        return sql_create

    @property
    def o(self):
        return MC().default_odps

    def _check_new_version(self, source: str) -> DataVersion:
        src_vers = self.parser.get_versions(source)
        config = self.parser.get_config(source)
        new_vers = DataVersion(source, src_vers.versions.copy())
        tgt_tbl_name = config.target_table
        try:
            if self.o.exist_table(tgt_tbl_name):
                table: Table = self.o.get_table(f"{tgt_tbl_name}")
                new_vers.is_new_source = False
                for version in list(new_vers.versions):
                    if table.exist_partition(f"pt={version}"):
                        new_vers.versions.remove(version)
            else:
                new_vers.is_new_source = True
        except ConnectionError:
            print("connection time out, please try again!")
            # set versions to empty
            new_vers.is_new_source = False
            new_vers = DataVersion(source, [])
        return new_vers

    def _upload_version(self, config: DataConfig, version: str):
        print(
            f"start upload for source: {config.source_name}[{config.source}] to table:{config.target_table}, version:{version}..."
        )
        create_sql = self._get_create_tbl_ext_sql(config, version)
        SqlRunner(create_sql).run()
        ext_tbl_name = self._get_ext_tbl_name(config, version)
        fields = self._get_fields(config.meta)
        insert_sql = f"""
            INSERT OVERWRITE TABLE {config.target_table} partition (pt='{version}') 
            select {fields}
            from  {ext_tbl_name};"""
        runner = SqlRunner(insert_sql)
        runner.run()
        stat = runner.get_summary()
        print(f"upload done: total {stat[0].outputs[0].rows:,} records")

    def _create_new_source(self, config: DataConfig):
        # upload meta to meta table
        meta_table_create = self.parser.get_meta_table_create_sql()
        SqlRunner(meta_table_create).run()
        sql_meta = self.parser.get_meta_sql(config.source)
        sql_meta_for_table = f"""
        INSERT OVERWRITE TABLE {config.meta_table} partition (source = '{config.source}')  
        select '{config.source_name}' as source_name
        ,'{config.target_table}' as ods_table_name
        ,{','.join(self.parser.meta_fields)} from {sql_meta};
        """
        # print(sql_meta_for_table)
        SqlRunner(sql_meta_for_table).run()
        sql_ods = self._get_create_tbl_ods_sql(config)
        SqlRunner(sql_ods).run()

    def upload(self, source: str):
        """check the source's versions in datasource,if source is new, create new table, if new versions found, upload to maxcompute"""
        new_vers = self._check_new_version(source)
        config = self.parser.get_config(source)
        if new_vers.is_new_source:
            print(
                f"target ods table not found for source:{config.source_name}[{config.source}], create new ods table:{config.target_table} ... "
            )
            self._create_new_source(config)
        if new_vers.versions:
            print(
                f"!!!new versions found for {config.source_name}[{config.source}]: {new_vers.versions}"
            )
            for v in new_vers.versions:
                self._upload_version(config, v)
        else:
            print(f"no new version found for {config.source_name}[{config.source}]")

    def upload_all(self):
        for s in self.parser.data_configs:
            self.upload(s)

from typing import List

from .data_config_parser import (
    DataConfigParser,
)
from data2cloud.cloud.maxcompute import SqlRunner


class MatrixImporter:
    def __init__(
        self,
        config_file: str,
    ):
        self.parser = DataConfigParser(config_file)

    def import_matrix(self, source: str):
        m = self.parser.get_matrix(source)
        if m:
            gen = MatrixGenerator(source, self.parser)
            gen.dup_check()
            gen.insert_index_data()
        else:
            print(f"maxtrix config for '{source}' not found!")

    def test_import(self, source: str, sql_only=True):
        m = self.parser.get_matrix(source)
        if m:
            gen = MatrixGenerator(source, self.parser)
            if sql_only:
                print(gen.get_import_sql())
                print(gen.get_dup_check_sql())
            else:
                gen.dup_check()
                return gen.gen_test_table()
        else:
            print(f"maxtrix config for '{source}' not found!")

    def import_all(self):
        for m in self.parser.matrix_configs:
            self.import_matrix(m)


class MatrixGenerator:
    def __init__(self, source: str, parser: DataConfigParser):
        self.parser = parser
        self.source = source
        matrix = parser.get_matrix(source)
        if matrix:
            self.matrix = matrix
        else:
            raise Exception("maxtrix config for '{source}' not found!")
        self.data_config = parser.get_config(source)
        self.ods_table_name = self.data_config.target_table
        self.__init_matrix_info()

    def __init_matrix_info(self):
        # find all col_name start with index_prefix, if index_prefix is array, use each element as index_prefix
        self.index_prefix: List[str] = (
            self.matrix.source_col_prefix
            if isinstance(self.matrix.source_col_prefix, list)
            else [self.matrix.source_col_prefix]
        )
        self.index_codes = []
        for pre in self.index_prefix:
            # filter source codes
            for x in self.data_config.meta:
                if x.col_name.startswith(pre):
                    if self.matrix.unit_filter:
                        if x.col_unit in self.matrix.unit_filter:
                            self.index_codes.append(x.col_name)
                    else:
                        self.index_codes.append(x.col_name)
        self.index_codes = list(set(self.index_codes))
        self.index_fields = [x.lower() for x in self.index_codes]

    def get_com_dim_sql(self):
        dim_scpt = """
         (
            select full_stock_id, stock_id,market,company_name_cn from dim_china_listed_company where
            pt = MAX_PT('dim_china_listed_company') AND 
            market in ('上海','深圳','北京')
        )
        """
        return dim_scpt

    def get_src_data_sql(self, fields: List[str]):
        src_raw_scpt = f"""
        (
            select LPAD({self.matrix.firm_col},6,'0') AS stock_id
                ,to_char(to_date({self.matrix.eff_date_col},'yyyy-mm-dd'),'yyyymmdd') eff_date
                ,{",".join(fields)}
                FROM    {self.ods_table_name}
                WHERE   pt = MAX_PT('{self.ods_table_name}') {f' and {self.matrix.filter}' if self.matrix.filter else ""}
        )
        """
        src_with_eff_year = f"""
            (SELECT  
                    CASE SUBSTR(eff_date,5,4)
                    WHEN  '0630' then concat(SUBSTR(eff_date,1,4),'S1')
                    WHEN  '0331' then concat(SUBSTR(eff_date,1,4),'Q1')
                    WHEN  '0101' then concat(cast(SUBSTR(eff_date,1,4)-1 as int),'')
                    WHEN  '1231' then concat(SUBSTR(eff_date,1,4),'')
                    WHEN  '0930' then concat(SUBSTR(eff_date,1,4),'Q3')
                    else null
                    END AS eff_year
                    ,* from {src_raw_scpt} )
        """
        dedup_script = f"""
            (select * from (
                select *
                ,row_number() over(partition by stock_id,eff_year order by eff_date desc) as rn
                from  {src_with_eff_year}
                )
            where rn = 1)
        """
        src_scpt = (
            dedup_script if self.matrix.deduplicate_by_eff_date else src_with_eff_year
        )

        return src_scpt

    def get_unpivot_sql(self):
        ## unpivot index_fields max 100 eachtime, need split
        unpivot_datas = []
        for i in range(0, len(self.index_fields), 100):
            unpivot_fields = ",".join(self.index_fields[i : i + 100])
            unpivot_datas.append(
                f"""
            select stock_id,eff_year,eff_date,source_code,measure_value 
                from {self.get_src_data_sql(self.index_fields[i : i + 100])}
                unpivot (measure_value for source_code in (
                    {unpivot_fields}
                ))
            """
            )
        unpivot_data = " (" + "union all ".join(unpivot_datas) + "\n)"
        return unpivot_data

    def get_matrix_data_sql(self):
        matrix_data = f"""
        select full_stock_id,a.stock_id,market,company_name_cn
            ,b.source_code
            ,CONCAT_WS('_','{self.matrix.target_code_prefix}',LPAD(c.col_order,3,'0')) as measure_code
            ,c.col_name_desc as measure_name
            ,c.col_unit as measure_unit
            ,b.measure_value
            ,b.eff_date
            ,b.eff_year
            ,'{self.matrix.source}'
            ,'{self.ods_table_name}'
            FROM {self.get_com_dim_sql()} a 
            join {self.get_unpivot_sql()} b on a.stock_id = b.stock_id and b.measure_value is not null 
            join {self.parser.get_meta_sql(self.source)} c on  trim(TOLOWER(b.source_code)) = trim(TOLOWER(c.col_name))                    
        """
        return matrix_data

    def get_import_sql(self):
        insert_tbl = "INSERT OVERWRITE TABLE dwd_cn_lst_com_measure PARTITION(eff_year,category,source)"
        return f"{insert_tbl}\n{self.get_matrix_data_sql()};"

    def get_dup_check_sql(self):
        dup_check = f"""
                select stock_id,source_code,eff_year,count(1) cnt from {self.get_unpivot_sql()}
            GROUP  by stock_id,eff_year,source_code having(count(1)>1);
        """
        return dup_check

    def dup_check(self):
        ## duplicate check , if duplicate , return error
        dup_check = self.get_dup_check_sql()
        # print(dup_check)
        i = 0
        with SqlRunner(dup_check).run().open_reader() as reader:
            for rcd in reader:
                print(rcd)
                i = i + 1
                # only print first 100
                if i > 100:
                    print("...only print first 100")
                    break
        if i > 0:
            raise ValueError("duplicate record found")

    def gen_test_table(self):
        test_tbl = """
        drop table if exists tmp_measure_import_test;
        create table tmp_measure_import_test lifecycle 1 as 
        """
        test_table = f"{test_tbl}\n{self.get_matrix_data_sql()};"
        s = SqlRunner(test_table)
        s.run()
        s.get_summary()
        print(s.get_summary())
        return s.to_pandas()

    def insert_index_data(self):
        print(
            f"start to import from {self.data_config.source_name}:{self.data_config.target_table}, matrix list:{self.index_codes}..."
        )
        r = SqlRunner(self.get_import_sql())
        r.run()
        s = r.get_summary()
        print(f"done:import total {s[0].outputs[0].rows} records")
        return s

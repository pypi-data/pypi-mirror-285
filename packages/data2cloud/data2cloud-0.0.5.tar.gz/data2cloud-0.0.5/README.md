# upload oss data to maxcompute

## initialize maxcompute account

- Install Aliyun CLI: [Install guide](https://help.aliyun.com/zh/cli/installation-guide)
- run the aliyun configure command to setup account

``` configure
$ aliyun configure
Configuring profile 'default' ...
Aliyun Access Key ID [None]: <Your AccessKey ID>
Aliyun Access Key Secret [None]: <Your AccessKey Secret>
Default Region Id [None]: cn-zhangjiakou
Default output format [json]: json
Default Language [zh]: zh
```

## define data source

define data source:

```json
{
    "$schema": "./json_schemas/data-config-schema.json",
    "vender": "csmar",
    "meta_table": "metadata_csmar",
    "data_type": {
        "type": "oss",
        "location": "oss://oss-cn-zhangjiakou-internal.aliyuncs.com/dteam2022-data/source_data/csmar"
    },
    "data_versions": [
        {
            "source": "cg_ybasic",
            "versions": [
                "20240506"
            ]
        }
    ],
    "data": [
       {
            "source": "cg_ybasic",
            "target_table": "ods_csmar_cg_ybasic",
            "source_name": "治理综合信息文件",
            "meta": [
                {
                    "col_order": 1,
                    "col_name": "Stkcd",
                    "col_type": "Nvarchar",
                    "col_name_desc": "证券代码",
                },
                {
                    "col_order": 2,
                    "col_name": "Reptdt",
                    "col_type": "Datetime",
                    "col_name_desc": "统计截止日期",

                },
                {
                    "col_order": 4,
                    "col_name": "Y0301b",
                    "col_type": "decimal",
                    "col_name_desc": "股本结构是否变化",
                    "col_desc": "1=未变化，2=有变化。"
                },
                {
                    "col_order": 16,
                    "col_name": "ManagerHoldsharesRatio",
                    "col_type": "decimal",
                    "col_name_desc": "总经理持股比例",
                    "col_unit": "%"
                },
                ...
            ]
        }, 
    ],
    "matrix": [{
            "source": "cg_ybasic",
            "target_code_prefix": "cg_ybasic",
            "source_col_prefix": "Y",
            "eff_date_col": "Reptdt",
            "firm_col": "stkcd"
        }
    ]
}
```

## upload data and import matrix

```python
from pathlib import Path
from data2cloud.data_uploader import DataUploader, MatrixImporter, DataConfigParser

config_file = f"{Path(__file__).resolve().parent}/datasource/csmar.json"
uploader = DataUploader(config_file)
uploader.upload("cg_ybasic") # uploader.upload_all()
# import matrix
m_importer = MatrixImporter(config_file)
m_importer.import_matrix("cg_ybasic")
```

import os
from setuptools import setup, find_namespace_packages
from setuptools.command.install import install
import shutil

name = "data2cloud"
description = "upload data from oss to maxcompute and import to matrix lib table"
url = "https://github.com/Digital-Transformation-Research-Center/data2cloud"  # 项目网址
# 依赖包列表
install_requires = ["pandas>=1.3.5", "pyodps>=0.11.6", "jsonschema>=4.22"]
package_data = {f"{name}.schemas.json": ["*.json"]}
project_folder = os.path.dirname(os.path.abspath(__file__))
data_files = [
    (
        f"/{project_folder}/json_schemas",
        ["data2cloud/schemas/json/data-config-schema.json"],
    )
]
author = "t2wei"  # 作者名
author_email = "t2wei@me.com"  # 作者邮箱

# git action workflow yml文件中定义的版本号,来自于tag
version = os.getenv("PACKAGE_VERSION", "0.0.1-alpha")
# 自动发现所有包
packages = find_namespace_packages(".", include=[name + "*"])
print(f"packages:{packages}")
if not version:
    raise Exception("no version info found!")
print(f"version: {version};")


setup(
    name=name,  # 包的名称，应与项目目录名一致，且符合PyPI的要求
    version=version,  # 版本号
    author=author,
    author_email=author_email,
    description=description,
    long_description=open("README.md").read(),  # 详细描述，通常从README文件读取
    long_description_content_type="text/markdown",  # 如果README是Markdown格式
    url=url,
    packages=packages,
    include_package_data=True,
    classifiers=[  # 分类信息，帮助用户在PyPI上找到你的包
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
    python_requires=">=3.7",  # 指定Python版本要求
    package_data=package_data,
    data_files=data_files,
)

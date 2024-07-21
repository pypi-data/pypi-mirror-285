from typing import List, Optional
from odps.models import Instance
import pandas as pd

from .instance_parser import InstanceParser, SqlExecutionSummary
from .initialize_maxcompute import _MaxcomputeSetup as mc


class SqlRunner:
    """
    DataSubTask是一个可运行的ODPS任务的抽象类
        `script` 任务脚本
        `instance` 根据创建任务类型,返回odps对应实例,sql返回Instance,security返回{}
        `taskRunner` 任务运行需要的ODPS实例
        `is_wait` 任务是否允许同步执行True or 异步执行 False
        `is_terminated()` 方法用于获取该任务是否结束
        `is_successful()` 方法用于获取该任务是否成功
        `get_task_result()` 方法用于获取该任运行后的详情, 统一接口 TaskResult
    """

    def __init__(self, script: str):
        self.__script = script
        self.__is_waited = False
        # 运行结果容器, 在子类run方法中被赋值, 跟odps类型绑定, 当前支持返回Instance或者{}
        self.instance: Optional[Instance] = None
        # 运行状态, none 还未运行, false 运行中, true 运行结束, 通过is_terminated访问
        self.__terminated: Optional[bool] = None
        # 运行结果, none 还未运行, false 运行失败, true 运行成功, 通过is_successful访问
        self.__successful: Optional[bool] = None
        # 用于记录是否刷新过任务结果
        # self.__is_updated: Optional[bool] = None
        self.hints = {"odps.sql.submit.mode": "script"}

    @property
    def is_waited(self) -> bool:
        """是否同步任务"""
        return self.__is_waited

    @property
    def script(self) -> str:
        """脚本内容"""
        return self.__script

    @property
    def taskRunner(self):
        """运行环境"""
        return mc().default_odps

    def is_terminated(self) -> Optional[bool]:
        """
        运行状态 none 还未运行, false 运行中, true 运行结束
        """
        # 如果self.__terminated=True则不再更新
        if not self.__terminated:
            if isinstance(self.instance, dict):
                self.__terminated = True
            elif isinstance(self.instance, Instance):
                self.__terminated = self.instance.is_terminated()
        return self.__terminated

    def is_successful(self) -> Optional[bool]:
        """
        运行结果 none 未运行结束, false 运行失败, true 运行成功
        """
        # 如果self.__successful已赋值则不再更新
        if self.__successful is None:
            if self.is_terminated() == True:
                if isinstance(self.instance, Instance):
                    self.__successful = self.instance.is_successful()
                elif isinstance(self.instance, dict):
                    # 授权任务 成功返回{} 失败返回{'result':error_message}
                    self.__successful = False if self.instance else True
        return self.__successful

    def run(self, drop_empty_output=True) -> Instance:
        try:
            if self.hints:
                self.instance = self.taskRunner.execute_sql(
                    self.script, hints=self.hints
                )
            else:
                self.instance = self.taskRunner.execute_sql(self.script)
        except ConnectionError:
            print("connection time out, please try again!")
        # drop the partition/table if rows = 0
        if drop_empty_output:
            summary = self.get_summary()
            drop_sql: List[str] = []
            for s in summary:
                for p in s.outputs_partitions:
                    if p.rows == 0:
                        if p.partition_value:
                            pt_cond = " , ".join(
                                [f"{k}='{v}'" for k, v in p.partition_value]
                            )
                            drop_sql.append(
                                f"alter table {p.table_name} drop partition ({pt_cond}) ;"
                            )
                        else:
                            drop_sql.append(f"drop table if exists {p.table_name};")
            if drop_sql:
                print("!!!drop empty output:")
                for sql in drop_sql:
                    print(sql + "...")
                    self.taskRunner.execute_sql(sql)
        return self.instance

    def get_summary(self) -> List[SqlExecutionSummary]:
        if self.instance:
            self.__summary: List[SqlExecutionSummary] = InstanceParser(
                self.instance
            ).get_sql_execution_summary()
        else:
            self.__summary = []
        return self.__summary

    def to_pandas(self, limit: int = 0) -> pd.DataFrame:
        if not self.instance:
            self.run()
        if self.instance:
            reader = self.instance.open_reader()
            if reader.count == 0:  # type: ignore
                return pd.DataFrame("no record")
            else:
                return (
                    reader.to_pandas(count=limit) if limit > 0 else reader.to_pandas()
                )
        else:
            return pd.DataFrame("no record")

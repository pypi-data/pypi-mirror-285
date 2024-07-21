from dataclasses import dataclass, field
from datetime import timedelta
import json
from typing import Dict, List, Tuple
from odps.models import Instance


@dataclass
class TableStat:
    table_name: str
    is_partition_table: bool = False
    partition_count: int = 0
    size: int = 0
    rows: int = 0


@dataclass
class PartitionStat:
    table_name: str
    partition_value: List[Tuple[str, str]] = field(default_factory=list)
    """ 按分区层次从高到低列出各级分区 (name,value) """
    size: int = 0
    rows: int = 0


@dataclass
class SqlExecutionSummary:
    inputs: List[TableStat]
    """`inputs` 运行日志解析得到的运行过程输入表信息,如果有分区,则是合并之后的结果,partitions字段为空"""
    outputs: List[TableStat]
    """`outputs` 运行日志解析得到的运行过程输出表信息,如果有分区,则是合并之后的结果,partitions字段为空"""
    cost_cpu: int
    cost_memory: int
    # result: Any
    input_partitions: List[PartitionStat]
    """ 运行日志解析得到的运行过程所有输入表分区信息,如果不是分区表,则和inputs一致"""
    outputs_partitions: List[PartitionStat]
    """ 运行日志解析得到的运行过程所有输出表分区信息,如果不是分区表,则和outputs一致"""


class InstanceParser:
    def __init__(self, instance: Instance):
        self.instance = instance
        self.id = self.instance.id
        self.logview = self.instance.get_logview_address()
        self.is_terminated = self.instance.is_terminated()
        self.is_successful = self.instance.is_successful()
        # GTC+8
        self.start_time = self.instance.start_time + timedelta(hours=8)  # type: ignore
        self.end_time = (
            self.instance.end_time + timedelta(hours=8)  # type: ignore
            if self.instance.is_terminated()
            else None
        )
        self.execute_time = str(
            self.instance.end_time - self.instance.start_time  # type: ignore
        ).split(".")[
            0
        ]  # type: ignore

    def get_sql_execution_summary(self) -> List[SqlExecutionSummary]:
        """
        如果有多个sql语句,返回一个list
        """
        sql_summary = []
        for task in self.instance.get_task_names():
            # 如果没有print 或者 错误信息 result返回空字符串''
            # result = self.instance.get_task_result(task)
            summary = self._get_task_summary(task)
            cost_cpu = summary.get("cost_cpu") or 0
            cost_memory = summary.get("cost_memory") or 0
            input_partitions = self._get_partition_stat(summary, True)
            output_partitions = self._get_partition_stat(summary, False)
            inputs = self._merge_partitions(input_partitions)
            outputs = self._merge_partitions(output_partitions)
            sql_summary.append(
                SqlExecutionSummary(
                    inputs,
                    outputs,
                    cost_cpu,
                    cost_memory,
                    input_partitions,
                    output_partitions,
                )
            )
        return sql_summary

    def _merge_partitions(self, stats: List[PartitionStat]) -> List[TableStat]:
        """merge partitions of each table and return table level stats"""
        table_stats: Dict[str, TableStat] = {}
        for x in stats:
            if x.table_name in table_stats:
                s = table_stats[x.table_name]
                s.partition_count += 1
                s.size = x.size + table_stats[x.table_name].size
                s.rows = x.rows + table_stats[x.table_name].rows
            else:
                is_partition_table = len(x.partition_value) > 0
                table_stats[x.table_name] = TableStat(
                    x.table_name,
                    is_partition_table,
                    partition_count=1 if is_partition_table else 0,
                    size=x.size,
                    rows=x.rows,
                )
        return list(table_stats.values())

    def _get_task_summary(self, task: str) -> Dict:
        detail = self.instance.get_task_detail2(task)
        if "mapReduce" in detail:
            summary = json.loads(detail["mapReduce"].get("jsonSummary"))
        return summary

    def _get_partition_stat(self, summary: Dict, input=True) -> List[PartitionStat]:
        result = []
        stats = summary.get("inputs") if input else summary.get("outputs")
        if stats:
            for key in stats:
                table_name = key.split("/")[0]
                partitions = [
                    x.split("=") for x in key.split("/")[1:]
                ]  # non-partition table will be []
                size = stats[key][1]
                rows = stats[key][0]
                result.append(PartitionStat(table_name, partitions, size, rows))
        return result

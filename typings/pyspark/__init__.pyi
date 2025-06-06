from typing import Any, Optional, List, Dict, Union

class SparkConf:
    def set(self, key: str, value: str) -> 'SparkConf': ...
    def setAll(self, pairs: List[tuple]) -> 'SparkConf': ...
    def get(self, key: str) -> str: ...

class SparkContext:
    def textFile(self, path: str) -> Any: ...
    def parallelize(self, data: List[Any]) -> Any: ...

class SparkSession:
    @staticmethod
    def builder() -> 'Builder': ...
    
    class Builder:
        def appName(self, name: str) -> 'Builder': ...
        def config(self, key: str, value: str) -> 'Builder': ...
        def master(self, master: str) -> 'Builder': ...
        def getOrCreate(self) -> 'SparkSession': ...
    
    def createDataFrame(self, data: List[Any], schema: Optional[Any] = None) -> 'DataFrame': ...
    def sql(self, query: str) -> 'DataFrame': ...
    def stop(self) -> None: ...

class DataFrame:
    def show(self, n: int = 20, truncate: bool = True) -> None: ...
    def select(self, *cols: Union[str, Any]) -> 'DataFrame': ...
    def filter(self, condition: Any) -> 'DataFrame': ...
    def withColumn(self, colName: str, col: Any) -> 'DataFrame': ...
    def groupBy(self, *cols: Any) -> 'GroupedData': ...
    def write(self) -> 'DataFrameWriter': ...
    
class GroupedData:
    def agg(self, *exprs: Dict[str, str]) -> 'DataFrame': ...
    def count(self) -> 'DataFrame': ...

class DataFrameWriter:
    def mode(self, saveMode: str) -> 'DataFrameWriter': ...
    def save(self, path: str) -> None: ...
    def parquet(self, path: str) -> None: ...
    def json(self, path: str) -> None: ...
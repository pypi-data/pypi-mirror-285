from pyspark.sql import DataFrame

from mx_stream_core.infrastructure.spark import spark
from mx_stream_core.infrastructure.delta import get_delta_path

from .base import BaseDataSource


class SparkDeltaDataSource(BaseDataSource):
    def __init__(self, table_name: str, schema) -> None:
        self.table_name = table_name
        self.schema = schema

    def get(self) -> DataFrame:
        try:
            return spark.read.format('delta').load(get_delta_path(self.table_name))
        except Exception as e:
            return spark.createDataFrame(data=[], schema=self.schema)

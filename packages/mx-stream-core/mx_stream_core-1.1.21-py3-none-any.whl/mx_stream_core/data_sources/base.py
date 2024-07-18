from pyspark.sql import DataFrame


class BaseDataSource:
    def get(self) -> DataFrame:
        raise NotImplementedError('Not implemented')

    def foreach(self, func):
        raise NotImplementedError('Not implemented')

    def awaitTermination(self):
        raise NotImplemented('Not implemented')

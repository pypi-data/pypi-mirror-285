from typing import Any

from pureml_evaluate.metrics.metric_base import MetricBase


class PercentOfNulls(MetricBase):
    name: Any = "percent_of_nulls"
    input_type: Any = "dataframe"
    output_type: Any = None
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, **kwargs):

        data_columns = data.columns
        data_columns = data_columns.tolist()

        columns_result = {}
        for i in data_columns:
            columns_result[i] = data[i].isnull().sum() / len(data[i]) * 100

        return {self.name: columns_result}

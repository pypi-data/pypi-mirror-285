from typing import Any

from pureml_evaluate.metrics.metric_base import MetricBase


class MixedDataTypes(MetricBase):
    name: Any = "mixed_data_types"
    input_type: Any = "dataframe"
    output_type: Any = None
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, **kwargs):
        data = data.to_pandas()
        data_columns = data.columns
        data_columns = data_columns.tolist()

        mixed_data_columns = {}
        for column in data_columns:
            unique_types = data[column].apply(lambda x: type(x).__name__).unique()

            if len(unique_types) > 1:
                string_ratio = data[column].apply(lambda x: isinstance(x, str)).mean()
                numeric_ratio = 1 - string_ratio

                mixed_data_columns[column] = {
                    "string_ratio": string_ratio,
                    "numeric_ratio": numeric_ratio,
                }

        return {self.name: mixed_data_columns}


# completed

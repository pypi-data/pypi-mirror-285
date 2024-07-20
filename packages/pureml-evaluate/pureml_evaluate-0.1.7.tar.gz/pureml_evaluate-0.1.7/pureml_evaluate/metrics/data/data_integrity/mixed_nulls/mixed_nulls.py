from typing import Any

import pandas as pd

from pureml_evaluate.metrics.metric_base import MetricBase


class MixedNulls(MetricBase):
    name: Any = "mixed_nulls"
    input_type: Any = "dataframe"
    output_type: Any = pd.DataFrame
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, **kwargs):
        mixed_nulls_info = []

        for column in data.columns:
            none_values = self.find_none_values(data[column])
            none_count = len(none_values)
            total_count = len(data[column])
            none_percentage = (none_count / total_count) * 100

            mixed_nulls_info.append(
                {
                    "Column": column,
                    "None_Value": none_values,
                    "Count": none_count,
                    "Percentage": none_percentage,
                }
            )

        result_df = pd.DataFrame(mixed_nulls_info)

        return {self.name: result_df}

    def find_none_values(self, column):
        none_values = column[column.isnull()]

        # Check for string representations of null values
        if column.dtype == "object":
            none_values = none_values.append(
                column[column.astype(str).str.lower().isin(["null", "na", "nan"])]
            )

        return none_values

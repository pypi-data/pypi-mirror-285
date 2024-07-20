from typing import Any

from pureml_evaluate.metrics.metric_base import MetricBase


class ColumnInfoCheck(MetricBase):
    name: Any = "column_info_check"
    input_type: Any = "dataframe"
    output_type: Any = dict
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, n_top_columns=10, **kwargs):
        column_info = {}

        for column in data.columns:
            column_info[column] = self.get_column_logical_type(data[column])

        # Select the top columns based on feature importance
        top_columns = dict(list(column_info.items())[:n_top_columns])

        return {self.name: top_columns}

    def get_column_logical_type(self, column):
        if column.dtype == "int64":
            return "numerical feature"

        if column.dtype == "float64":
            return "numerical feature"
        if column.dtype == "datetime64[ns]":
            return "date"
        if column.dtype == "object":
            if self.is_label_column(column):
                return "label"
            else:
                return "categorical feature"
        if column.dtype == "bool":
            return "boolean"

        return "other"

    def is_label_column(self, column):
        if column.nunique() == 2:
            return True
        return False

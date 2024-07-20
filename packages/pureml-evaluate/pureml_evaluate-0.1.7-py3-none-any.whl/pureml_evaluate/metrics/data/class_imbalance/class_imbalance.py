from typing import Any

from pureml_evaluate.metrics.metric_base import MetricBase

class ClassImbalance(MetricBase):
    name: Any = "class_imbalance"
    input_type: Any = "dataframe"
    output_type: Any = None

    def parse_data(self, data):
        return data

    def compute(self, data, n_top_labels=5, ignore_nan=True, **kwargs):
        class_imbalance = {}

        for column in data.columns:
            class_counts = data[column].value_counts(normalize=True, dropna=ignore_nan)
            class_counts = class_counts.round(2)
            class_imbalance[column] = class_counts.head(n_top_labels).to_dict()

        return {self.name: class_imbalance}

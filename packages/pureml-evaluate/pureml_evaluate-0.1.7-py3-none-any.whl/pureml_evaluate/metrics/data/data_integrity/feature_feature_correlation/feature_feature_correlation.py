from typing import Any

import pandas as pd

from pureml_evaluate.metrics.metric_base import MetricBase


class FeatureFeatureCorrelation(MetricBase):
    name: Any = "feature_feature_correlation"
    input_type: Any = "dataframe"
    output_type: Any = pd.DataFrame
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, **kwargs):
        correlation_matrix = data.corr()

        return {self.name: correlation_matrix}

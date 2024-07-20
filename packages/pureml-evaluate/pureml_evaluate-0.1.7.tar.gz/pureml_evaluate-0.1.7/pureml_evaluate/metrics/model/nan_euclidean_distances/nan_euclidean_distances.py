from typing import Any, Dict

import numpy as np
from sklearn.metrics.pairwise import nan_euclidean_distances

from pureml_evaluate.metrics.metric_base import MetricBase


class NanEuclideanDistances(MetricBase):
    name: Any = "nan_euclidean_distances"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(
        self, X, Y=None, squared=False, missing_values=np.nan, copy=True, **kwargs
    ):

        distance = nan_euclidean_distances(
            X=X, Y=Y, squared=squared, missing_values=missing_values, copy=copy
        )

        return {self.name: distance}

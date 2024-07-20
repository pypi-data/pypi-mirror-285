from typing import Any, Dict

from sklearn.metrics import pairwise_distances_argmin_min

from pureml_evaluate.metrics.metric_base import MetricBase


class PairwiseDistancesArgminMin(MetricBase):
    name: Any = "pairwise_distances_argmin_min"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y, axis=1, metric="euclidean", metric_kwargs=None, **kwargs):

        argmin, distances = pairwise_distances_argmin_min(
            X=X, Y=Y, axis=axis, metric=metric, metric_kwargs=metric_kwargs
        )

        return {self.name: {"argmin": argmin, "distances": distances}}

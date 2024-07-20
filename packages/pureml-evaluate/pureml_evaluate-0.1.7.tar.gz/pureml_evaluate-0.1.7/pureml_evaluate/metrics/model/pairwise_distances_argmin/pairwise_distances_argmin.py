from typing import Any

from sklearn.metrics import pairwise_distances_argmin

from pureml_evaluate.metrics.metric_base import MetricBase


class PairwiseDistancesArgmin(MetricBase):
    name: Any = "pairwise_distances_argmin"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Any = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y, axis=1, metric="euclidean", metric_kwargs=None, **kwargs):

        distance = pairwise_distances_argmin(
            X=X, Y=Y, metric=metric, metric_kwargs=metric_kwargs
        )

        return {self.name: distance}

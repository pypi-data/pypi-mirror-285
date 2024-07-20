from typing import Any, Dict

from sklearn.metrics.pairwise import euclidean_distances

from pureml_evaluate.metrics.metric_base import MetricBase


class EuclideanDistances(MetricBase):
    name: Any = "euclidean_distances"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(
        self,
        X,
        Y=None,
        Y_norm_squared=None,
        squared=False,
        X_norm_squared=None,
        **kwargs
    ):

        distance = euclidean_distances(
            X=X,
            Y=Y,
            Y_norm_squared=Y_norm_squared,
            squared=squared,
            X_norm_squared=X_norm_squared,
        )

        return {self.name: distance}

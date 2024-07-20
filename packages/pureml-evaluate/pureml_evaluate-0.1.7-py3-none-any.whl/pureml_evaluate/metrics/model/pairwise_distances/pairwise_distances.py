from typing import Any, Dict

from sklearn.metrics import pairwise_distances

from pureml_evaluate.metrics.metric_base import MetricBase


class PairwiseDistances(MetricBase):
    name: Any = "pairwise_distances"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(
        self,
        X,
        Y=None,
        metric="euclidean",
        n_jobs=None,
        force_all_finite=True,
        **kwargs
    ):

        distance = pairwise_distances(
            X=X, Y=Y, metric=metric, n_jobs=n_jobs, force_all_finite=force_all_finite
        )

        return {self.name: distance}

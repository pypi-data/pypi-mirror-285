from typing import Any, Dict

from sklearn.metrics import pairwise_distances_chunked

from pureml_evaluate.metrics.metric_base import MetricBase


class PairwiseDistancesChunked(MetricBase):
    name: Any = "pairwise_distances_chunked"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(
        self,
        X,
        Y=None,
        reduce_func=None,
        metric="euclidean",
        n_jobs=None,
        working_memory=None,
        **kwargs
    ):

        result = pairwise_distances_chunked(
            X=X,
            Y=Y,
            reduce_func=reduce_func,
            metric=metric,
            n_jobs=n_jobs,
            working_memory=working_memory,
        )

        return {self.name: result}

from typing import Any, Dict

from sklearn.metrics.pairwise import cosine_distances

from pureml_evaluate.metrics.metric_base import MetricBase


class CosineDistances(MetricBase):
    name: Any = "cosine_distances"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y=None, **kwargs):
        if Y is None:
            score = cosine_distances(X)
        else:
            score = cosine_distances(X, Y)

        return {self.name: score}

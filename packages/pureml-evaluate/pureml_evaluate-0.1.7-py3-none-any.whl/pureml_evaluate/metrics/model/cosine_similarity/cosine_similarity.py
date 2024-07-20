from typing import Any, Dict

from sklearn.metrics.pairwise import cosine_similarity

from pureml_evaluate.metrics.metric_base import MetricBase


class CosineSimilarity(MetricBase):
    name: Any = "cosine_similarity"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y=None, dense_output=True):

        if Y is None:
            score = cosine_similarity(X, dense_output=dense_output)
        else:
            score = cosine_similarity(X, Y, dense_output=dense_output)

        return {self.name: score}

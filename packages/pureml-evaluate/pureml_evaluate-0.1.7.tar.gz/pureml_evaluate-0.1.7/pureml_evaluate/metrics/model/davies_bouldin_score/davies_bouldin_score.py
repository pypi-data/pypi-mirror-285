from typing import Any, Dict

from sklearn.metrics import davies_bouldin_score

from pureml_evaluate.metrics.metric_base import MetricBase


class DaviesBouldinScore(MetricBase):
    name: Any = "davies_bouldin_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, labels, **kwargs):

        score = davies_bouldin_score(X=X, labels=labels)

        score = {self.name: float(score)}

        return score

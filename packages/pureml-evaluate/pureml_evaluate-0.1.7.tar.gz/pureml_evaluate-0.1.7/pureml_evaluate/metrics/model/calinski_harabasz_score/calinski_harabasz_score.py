from typing import Any, Dict

from sklearn.metrics import calinski_harabasz_score

from pureml_evaluate.metrics.metric_base import MetricBase


class CalinskiHarabaszScore(MetricBase):
    name: Any = "calinski_harabasz_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, labels, **kwargs):

        score = calinski_harabasz_score(X=X, labels=labels)

        score = {self.name: float(score)}

        return score

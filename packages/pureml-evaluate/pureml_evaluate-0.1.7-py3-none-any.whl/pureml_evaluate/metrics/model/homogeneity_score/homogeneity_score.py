from typing import Any, Dict

from sklearn.metrics import homogeneity_score

from pureml_evaluate.metrics.metric_base import MetricBase


class HomogeneityScore(MetricBase):
    name: Any = "homogeneity_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, labels_true, labels_pred, **kwargs):

        score = homogeneity_score(labels_true=labels_true, labels_pred=labels_pred)

        return {self.name: float(score)}

from typing import Any, Dict

from sklearn.metrics import fowlkes_mallows_score

from pureml_evaluate.metrics.metric_base import MetricBase


class FowlkesMallowsScore(MetricBase):
    name: Any = "fowlkes_mallows_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, labels_true, labels_pred, sparse=False, **kwargs):

        score = fowlkes_mallows_score(
            labels_true=labels_true, labels_pred=labels_pred, sparse=sparse
        )

        return {self.name: float(score)}

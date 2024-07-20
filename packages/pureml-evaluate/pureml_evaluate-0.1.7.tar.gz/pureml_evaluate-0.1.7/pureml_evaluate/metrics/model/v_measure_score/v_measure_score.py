from typing import Any, Dict

from sklearn.metrics import v_measure_score

from pureml_evaluate.metrics.metric_base import MetricBase


class VMeasureScore(MetricBase):
    name: Any = "v_measure_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, labels_true, labels_pred, beta=1.0, **kwargs):

        score = v_measure_score(
            labels_true=labels_true, labels_pred=labels_pred, beta=beta
        )

        return {self.name: float(score)}

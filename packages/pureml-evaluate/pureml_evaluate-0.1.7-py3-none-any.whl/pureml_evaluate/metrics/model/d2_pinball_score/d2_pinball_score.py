from typing import Any, Dict

from sklearn.metrics import d2_pinball_score

from pureml_evaluate.metrics.metric_base import MetricBase


class D2PinballScore(MetricBase):
    name: Any = "d2_pinball_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, alpha=0.5, sample_weight=None, **kwargs):

        score = d2_pinball_score(
            y_true=references,
            y_pred=predictions,
            alpha=alpha,
            sample_weight=sample_weight,
        )

        score = {self.name: {"value": float(score)}}

        return score

from typing import Any, Dict

from sklearn.metrics import brier_score_loss

from pureml_evaluate.metrics.metric_base import MetricBase


class BrierScoreLoss(MetricBase):
    name: Any = "brier_score_loss"
    input_type: Any = "int"
    output_type: Any = "float"
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(
        self,
        references,
        predictions=None,
        prediction_scores=None,
        sample_weight=None,
        pos_label=1,
        **kwargs
    ):

        if prediction_scores is None and predictions is None:
            score = None
        elif predictions is None:
            score = brier_score_loss(
                y_true=references,
                y_prob=prediction_scores,
                sample_weight=sample_weight,
                pos_label=pos_label,
            )
            score = float(score)
        elif prediction_scores is None:
            score = brier_score_loss(
                y_true=references,
                y_prob=predictions,
                sample_weight=sample_weight,
                pos_label=pos_label,
            )
            score = float(score)

        score = {self.name: {"value": float(score)}}

        return score

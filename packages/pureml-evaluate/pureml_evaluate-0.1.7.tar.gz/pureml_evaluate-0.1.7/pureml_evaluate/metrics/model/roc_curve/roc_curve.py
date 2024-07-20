from typing import Any, Dict

from sklearn.metrics import roc_curve

from pureml_evaluate.metrics.metric_base import MetricBase


class RocCurve(MetricBase):
    name: Any = "roc_curve"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self,
        references,
        predictions=None,
        prediction_scores=None,
        pos_label=None,
        sample_weight=None,
        **kwargs
    ):

        if prediction_scores is None and predictions is None:
            fpr, tpr, thresholds = None
        elif predictions is None:
            fpr, tpr, thresholds = roc_curve(
                y_true=references,
                y_score=prediction_scores,
                pos_label=pos_label,
                sample_weight=sample_weight,
            )

        elif prediction_scores is None:
            fpr, tpr, thresholds = roc_curve(
                y_true=references,
                y_score=predictions,
                pos_label=pos_label,
                sample_weight=sample_weight,
            )

        score = {self.name: {"fpr": fpr, "tpr": tpr, "thresholds": thresholds}}

        return score

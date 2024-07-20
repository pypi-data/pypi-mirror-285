from typing import Any, Dict

from sklearn.metrics import precision_recall_curve

from pureml_evaluate.metrics.metric_base import MetricBase


class PrecisionRecallCurve(MetricBase):

    name: Any = "precision_recall_curve"
    input_type: Any = "float"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self,
        references,
        predictions=None,
        prediction_scores=None,
        sample_weight=None,
        pos_label=None,
        **kwargs
    ):

        if prediction_scores is None and predictions is None:
            score = None
        elif predictions is None:
            score = precision_recall_curve(
                y_true=references,
                probas_pred=prediction_scores,
                sample_weight=sample_weight,
                pos_label=pos_label,
            )
            score = score
        elif prediction_scores is None:
            score = precision_recall_curve(
                y_true=references,
                probas_pred=predictions,
                sample_weight=sample_weight,
                pos_label=pos_label,
            )
            score = score

        score = {
            self.name: {
                "Precision": score[0],
                "Recall": score[1],
                "Thresholds": score[2],
            }
        }

        return score

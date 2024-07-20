from typing import Any, Dict

from sklearn.metrics import balanced_accuracy_score

from pureml_evaluate.metrics.metric_base import MetricBase


class BalancedAccuracyScore(MetricBase):
    name: Any = "balanced_accuracy_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, sample_weight=None, **kwargs):

        score = balanced_accuracy_score(
            y_true=references, y_pred=predictions, sample_weight=sample_weight
        )

        score = {self.name: {"value": float(score)}}

        return score

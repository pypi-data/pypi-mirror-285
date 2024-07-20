from typing import Any, Dict

from sklearn.metrics import hamming_loss

from pureml_evaluate.metrics.metric_base import MetricBase


class HammingLoss(MetricBase):
    name: Any = "hamming_loss"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, sample_weight=None, **kwargs):

        score = hamming_loss(
            y_true=references, y_pred=predictions, sample_weight=sample_weight
        )

        score = {self.name: float(score)}

        return score

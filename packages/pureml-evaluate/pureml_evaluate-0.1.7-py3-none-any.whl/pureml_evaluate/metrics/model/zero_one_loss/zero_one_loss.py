from typing import Any, Dict

from sklearn.metrics import zero_one_loss

from pureml_evaluate.metrics.metric_base import MetricBase


class ZeroOneLoss(MetricBase):
    name: Any = "zero_one_loss"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self, references, predictions, normalize=True, sample_weight=None, **kwargs
    ):

        score = zero_one_loss(
            y_true=references,
            y_pred=predictions,
            normalize=normalize,
            sample_weight=sample_weight,
        )

        score = {self.name: float(score)}

        return score

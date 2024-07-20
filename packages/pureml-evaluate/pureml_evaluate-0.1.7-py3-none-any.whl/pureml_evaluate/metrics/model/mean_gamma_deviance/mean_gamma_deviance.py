from typing import Any, Dict

from sklearn.metrics import mean_gamma_deviance

from pureml_evaluate.metrics.metric_base import MetricBase


class MeanGammaDeviance(MetricBase):
    name: Any = "mean_gamma_deviance"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, sample_weight=None, **kwargs):

        score = mean_gamma_deviance(
            y_true=references, y_pred=predictions, sample_weight=sample_weight
        )

        score = {self.name: {"value": float(score)}}

        return score

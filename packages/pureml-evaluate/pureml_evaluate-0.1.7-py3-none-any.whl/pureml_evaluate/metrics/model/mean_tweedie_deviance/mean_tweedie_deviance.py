from typing import Any, Dict

from sklearn.metrics import mean_tweedie_deviance

from pureml_evaluate.metrics.metric_base import MetricBase


class MeanTweedieDeviance(MetricBase):
    name: Any = "mean_tweedie_deviance"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, power=0, sample_weight=None, **kwargs):

        score = mean_tweedie_deviance(
            y_true=references, y_pred=predictions, power=0, sample_weight=sample_weight
        )

        score = {self.name: float(score)}

        return score

from typing import Any, Dict

from sklearn.metrics import max_error

from pureml_evaluate.metrics.metric_base import MetricBase


class MaxError(MetricBase):
    name: Any = "max_error"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, **kwargs):

        score = max_error(y_true=references, y_pred=predictions)

        score = {self.name: {"value": float(score)}}

        return score

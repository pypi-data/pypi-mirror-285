from typing import Any, Dict

from sklearn.metrics import mean_absolute_percentage_error

from pureml_evaluate.metrics.metric_base import MetricBase


class MeanAbsolutePercentageError(MetricBase):
    name: Any = "mean_absolute_percentage_error"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self, references, predictions, sample_weight=None, multioutput=None, **kwargs
    ):

        score = mean_absolute_percentage_error(
            y_true=references,
            y_pred=predictions,
            sample_weight=sample_weight,
            multioutput=multioutput,
        )

        score = {self.name: {"value": score}}

        return score

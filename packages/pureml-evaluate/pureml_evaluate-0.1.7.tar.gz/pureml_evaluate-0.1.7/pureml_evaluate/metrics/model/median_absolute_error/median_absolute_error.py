from typing import Any, Dict

from sklearn.metrics import median_absolute_error

from pureml_evaluate.metrics.metric_base import MetricBase


class MedianAbsoluteError(MetricBase):
    name: Any = "median_absolute_error"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self,
        references,
        predictions,
        normalize=True,
        sample_weight=None,
        multioutput="uniform_average",
        **kwargs
    ):

        score = median_absolute_error(
            y_true=references,
            y_pred=predictions,
            sample_weight=sample_weight,
            multioutput=multioutput,
        )

        score = {self.name: {"value": score}}

        return score

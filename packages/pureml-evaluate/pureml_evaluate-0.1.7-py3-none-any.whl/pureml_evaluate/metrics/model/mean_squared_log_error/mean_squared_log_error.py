from typing import Any, Dict

from sklearn.metrics import mean_squared_log_error

from pureml_evaluate.metrics.metric_base import MetricBase


class MeanSquaredLogError(MetricBase):
    name: Any = "mean_squared_log_error"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self,
        references,
        predictions,
        squared=True,
        sample_weight=None,
        multioutput=None,
        **kwargs
    ):

        score = mean_squared_log_error(
            y_true=references,
            y_pred=predictions,
            squared=squared,
            sample_weight=sample_weight,
            multioutput=multioutput,
        )

        score = {self.name: {"value": score}}

        return score

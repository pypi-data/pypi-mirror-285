from typing import Any, Dict

from sklearn.metrics import r2_score

from pureml_evaluate.metrics.metric_base import MetricBase


class R2Score(MetricBase):
    name: Any = "r2_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self,
        references,
        predictions,
        sample_weight=None,
        multioutput="uniform_average",
        **kwargs
    ):

        score = r2_score(
            y_true=references,
            y_pred=predictions,
            sample_weight=sample_weight,
            multioutput=multioutput,
        )

        score = {self.name: {"value": score}}

        return score

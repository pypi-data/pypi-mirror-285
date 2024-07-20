from typing import Any

from sklearn.metrics import accuracy_score

from pureml_evaluate.metrics.metric_base import MetricBase


class Accuracy(MetricBase):
    name: Any = "accuracy"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Any = {}

    def parse_data(self, data):

        return data

    def compute(
        self, references, predictions, normalize=True, sample_weight=None, **kwargs
    ):

        score = accuracy_score(
            y_true=references,
            y_pred=predictions,
            normalize=True,
            sample_weight=sample_weight,
        )

        # score = {
        #     self.name : float(score)
        #     }

        score = {self.name: {"value": float(score)}}

        return score

from typing import Any, Dict

from sklearn.metrics import recall_score

from pureml_evaluate.metrics.metric_base import MetricBase


class Recall(MetricBase):

    name: Any = "recall"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self,
        predictions,
        references,
        labels=None,
        pos_label=1,
        average="binary",
        sample_weight=None,
        zero_division="warn",
        **kwargs
    ):

        if "kwargs" in kwargs and "average" in kwargs["kwargs"]:
            average = kwargs["kwargs"]["average"]
        score = recall_score(
            y_true=references,
            y_pred=predictions,
            labels=labels,
            pos_label=pos_label,
            average=average,
            sample_weight=sample_weight,
            zero_division=zero_division,
        )

        # score = {
        #     self.name : float(score) if score.size == 1 else score
        #     }
        score = {self.name: {"value": float(score) if score.size == 1 else score}}

        return score

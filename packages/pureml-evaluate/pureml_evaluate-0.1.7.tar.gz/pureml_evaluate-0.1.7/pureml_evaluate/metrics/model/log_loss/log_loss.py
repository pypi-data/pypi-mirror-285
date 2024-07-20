from typing import Any, Dict

from sklearn.metrics import log_loss

from pureml_evaluate.metrics.metric_base import MetricBase


class LogLoss(MetricBase):

    name: Any = "log_loss"
    input_type: Any = "float"
    output_type: Any = None
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(
        self,
        references,
        predictions=None,
        prediction_scores=None,
        sample_weight=None,
        normalize=True,
        labels=None,
        **kwargs
    ):

        # prediction_scores = kwargs.get('prediction_scores',None) #To get prediction_scores from kwargs
        if "kwargs" in kwargs and "prediction_scores" in kwargs["kwargs"]:
            prediction_scores = kwargs["kwargs"]["prediction_scores"]
        if prediction_scores is None and predictions is None:
            score = None
        elif predictions is None:
            score = log_loss(
                y_true=references,
                y_pred=prediction_scores,
                sample_weight=sample_weight,
                normalize=normalize,
                labels=labels,
            )
            score = float(score)
        elif prediction_scores is None:
            score = log_loss(
                y_true=references,
                y_pred=predictions,
                sample_weight=sample_weight,
                normalize=normalize,
                labels=labels,
            )
            score = float(score)

        score = {self.name: {"value": score}}

        return score

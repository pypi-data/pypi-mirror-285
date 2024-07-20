from typing import Any, Dict

from sklearn.metrics import top_k_accuracy_score

from pureml_evaluate.metrics.metric_base import MetricBase


class TopKAccuracyScore(MetricBase):
    name: Any = "top_k_accuracy_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self,
        references,
        predictions=None,
        prediction_scores=None,
        normalize=True,
        sample_weight=None,
        **kwargs
    ):

        # prediction_scores = kwargs.get('prediction_scores',None)
        if "kwargs" in kwargs and "prediction_scores" in kwargs["kwargs"]:
            prediction_scores = kwargs["kwargs"]["prediction_scores"]
        if prediction_scores is None and predictions is None:
            score = None
        elif predictions is None:
            score = top_k_accuracy_score(
                y_true=references,
                y_score=prediction_scores,
                normalize=normalize,
                sample_weight=sample_weight,
            )
            score = float(score)
        elif prediction_scores is None:
            score = top_k_accuracy_score(
                y_true=references,
                y_score=predictions,
                normalize=normalize,
                sample_weight=sample_weight,
            )
            score = float(score)

        score = {self.name: {"value": score}}

        return score

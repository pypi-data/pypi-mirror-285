from typing import Any, Dict

from sklearn.metrics import explained_variance_score

from pureml_evaluate.metrics.metric_base import MetricBase


class ExplainedVarianceScore(MetricBase):
    name: Any = "explained_variance_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, sample_weight=None, **kwargs):

        score = explained_variance_score(
            y_true=references, y_pred=predictions, sample_weight=sample_weight
        )

        score = {self.name: {"value": float(score)}}

        return score

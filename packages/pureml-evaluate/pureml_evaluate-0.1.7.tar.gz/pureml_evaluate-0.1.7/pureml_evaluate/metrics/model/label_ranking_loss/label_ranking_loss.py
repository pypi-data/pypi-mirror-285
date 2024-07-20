from typing import Any, Dict

from sklearn.metrics import label_ranking_loss

from pureml_evaluate.metrics.metric_base import MetricBase


class LabelRankingLoss(MetricBase):
    name: Any = "label_ranking_loss"
    input_type: Any = "int"
    output_type: Any = "float"
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, references, scores, sample_weight=None, **kwargs):

        result = label_ranking_loss(
            y_true=references, y_score=scores, sample_weight=sample_weight
        )

        result = {self.name: float(result)}

        return result

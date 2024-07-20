from typing import Any, Dict

from sklearn.metrics import normalized_mutual_info_score

from pureml_evaluate.metrics.metric_base import MetricBase


class NormalizedMutualInfoScore(MetricBase):
    name: Any = "normalized_mutual_info_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, labels_true, labels_pred, average_method="arithmetic", **kwargs):

        score = normalized_mutual_info_score(
            labels_true=labels_true,
            labels_pred=labels_pred,
            average_method=average_method,
        )

        return {self.name: float(score)}

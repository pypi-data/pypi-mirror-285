from typing import Any, Dict

from sklearn.metrics import adjusted_mutual_info_score

from pureml_evaluate.metrics.metric_base import MetricBase


class AdjustedMutualInfoScore(MetricBase):
    name: Any = "adjusted_mutual_info_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, average_method="arithmetic", **kwargs):

        score = adjusted_mutual_info_score(
            labels_true=references,
            labels_pred=predictions,
            average_method=average_method,
        )

        score = {self.name: float(score)}

        return score

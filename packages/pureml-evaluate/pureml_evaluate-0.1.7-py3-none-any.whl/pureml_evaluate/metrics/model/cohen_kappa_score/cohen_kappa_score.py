from typing import Any, Dict

from sklearn.metrics import cohen_kappa_score

from pureml_evaluate.metrics.metric_base import MetricBase


class CohenKappaScore(MetricBase):
    name: Any = "cohen_kappa_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, sample_weight=None, **kwargs):

        score = cohen_kappa_score(
            y1=references, y2=predictions, sample_weight=sample_weight
        )

        score = {self.name: float(score)}

        return score

from typing import Any, Dict

from sklearn.metrics import coverage_error

from pureml_evaluate.metrics.metric_base import MetricBase


class CoverageError(MetricBase):
    name: Any = "coverage_error"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, references, predictions, sample_weight=None, **kwargs):

        score = coverage_error(
            y_true=references, y_score=predictions, sample_weight=sample_weight
        )

        score = {self.name: score}

        return score

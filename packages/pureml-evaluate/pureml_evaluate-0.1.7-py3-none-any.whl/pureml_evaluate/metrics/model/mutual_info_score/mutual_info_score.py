from typing import Any, Dict

from sklearn.metrics import mutual_info_score

from pureml_evaluate.metrics.metric_base import MetricBase


class MutualInfoScore(MetricBase):
    name: Any = "mutual_info_score"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, labels_true, labels_pred, contingency=None, **kwargs):

        if contingency is None:
            score = mutual_info_score(labels_true=labels_true, labels_pred=labels_pred)
        else:
            score = mutual_info_score(None, None, contingency=contingency)

        return {self.name: float(score)}

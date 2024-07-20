from typing import Any, Dict

from sklearn.metrics import auc, roc_curve

from pureml_evaluate.metrics.metric_base import MetricBase


class AUC(MetricBase):
    name: Any = "auc"
    input_type: Any = "float"
    output_type: Any = "float"
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(self, references, predictions, pos_label=1, **kwargs):

        fpr, tpr, thresholds = roc_curve(references, predictions, pos_label=pos_label)

        score = auc(x=fpr, y=tpr)

        score = {self.name: float(score)}

        return score

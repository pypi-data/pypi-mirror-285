from typing import Any, Dict

from sklearn.metrics.cluster import pair_confusion_matrix

from pureml_evaluate.metrics.metric_base import MetricBase


class PairConfusionMatrix(MetricBase):
    name: Any = "pair_confusion_matrix"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, labels_ture, labels_pred):

        score = pair_confusion_matrix(labels_true=labels_ture, labels_pred=labels_pred)

        return {self.name: score}

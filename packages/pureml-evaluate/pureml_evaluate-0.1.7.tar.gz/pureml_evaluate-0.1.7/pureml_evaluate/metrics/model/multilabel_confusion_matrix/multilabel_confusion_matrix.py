from typing import Any, Dict

from sklearn.metrics import multilabel_confusion_matrix

from pureml_evaluate.metrics.metric_base import MetricBase


class MultilabelConfusionMatrix(MetricBase):
    name: Any = "multilabel_confusion_matrix"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):

        return data

    def compute(
        self, references, predictions, labels=None, sample_weight=None, **kwargs
    ):

        score = multilabel_confusion_matrix(
            y_true=references,
            y_pred=predictions,
            labels=labels,
            sample_weight=sample_weight,
        )

        score = {self.name: score}

        return score

from typing import Any, Dict

from sklearn.metrics import confusion_matrix

from pureml_evaluate.metrics.metric_base import MetricBase


class ConfusionMatrix(MetricBase):
    name: Any = "confusion_matrix"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = {}

    def parse_data(self, data):

        return data

    def compute(
        self, references, predictions, normalize="true", sample_weight=None, **kwargs
    ):

        matrix = confusion_matrix(
            y_true=references,
            y_pred=predictions,
            normalize=normalize,
            sample_weight=sample_weight,
        )
        # print(type(matrix))
        matrix = {self.name: matrix.tolist()}

        # matrix  = {self.name: matrix} #To check with generating_confusion_matix Graphs
        return matrix

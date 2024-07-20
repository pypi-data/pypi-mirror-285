from typing import Any, Dict

from sklearn.metrics.pairwise import paired_cosine_distances

from pureml_evaluate.metrics.metric_base import MetricBase


class PairedCosineDistances(MetricBase):
    name: Any = "paired_cosine_distances"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y, **kwargs):

        distance = paired_cosine_distances(X=X, Y=Y)

        return {self.name: distance}

from typing import Any, Dict

from sklearn.metrics.pairwise import paired_distances

from pureml_evaluate.metrics.metric_base import MetricBase


class PairedDistances(MetricBase):
    name: Any = "paired_distances"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y, metric="euclidean", **kwargs):

        distance = paired_distances(X=X, Y=Y, metric=metric)

        return {self.name: distance}

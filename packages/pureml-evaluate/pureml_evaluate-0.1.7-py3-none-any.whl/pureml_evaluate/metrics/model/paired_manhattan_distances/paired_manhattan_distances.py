from typing import Any, Dict

from sklearn.metrics.pairwise import paired_manhattan_distances

from pureml_evaluate.metrics.metric_base import MetricBase


class PairedManhattanDistances(MetricBase):
    name: Any = "paired_manhattan_distances"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y, **kwargs):

        distance = paired_manhattan_distances(X=X, Y=Y)

        return {self.name: distance}

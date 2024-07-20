from typing import Any, Dict

from sklearn.metrics.pairwise import haversine_distances

from pureml_evaluate.metrics.metric_base import MetricBase


class HaversineDistances(MetricBase):
    name: Any = "haversine_distances"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y=None, **kwargs):

        distance = haversine_distances(X=X, Y=Y)

        return {self.name: distance}

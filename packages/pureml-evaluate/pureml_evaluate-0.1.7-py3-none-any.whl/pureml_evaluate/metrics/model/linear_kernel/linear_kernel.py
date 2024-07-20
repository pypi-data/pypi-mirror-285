from typing import Any, Dict

from sklearn.metrics.pairwise import linear_kernel

from pureml_evaluate.metrics.metric_base import MetricBase


class LinearKernel(MetricBase):
    name: Any = "linear_kernel"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y=None, dense_output=True, **kwargs):

        kernel = linear_kernel(X=X, Y=Y, dense_output=dense_output)

        return {self.name: kernel}

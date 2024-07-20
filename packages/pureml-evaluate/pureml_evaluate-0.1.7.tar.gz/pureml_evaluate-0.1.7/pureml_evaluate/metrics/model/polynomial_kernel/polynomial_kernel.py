from typing import Any, Dict

from sklearn.metrics.pairwise import polynomial_kernel

from pureml_evaluate.metrics.metric_base import MetricBase


class PolynomialKernel(MetricBase):
    name: Any = "polynomial_kernel"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y=None, degree=3, gamma=None, coef0=1, **kwargs):

        kernel = polynomial_kernel(X=X, Y=Y, degree=degree, gamma=gamma, coef0=coef0)

        return {self.name: kernel}

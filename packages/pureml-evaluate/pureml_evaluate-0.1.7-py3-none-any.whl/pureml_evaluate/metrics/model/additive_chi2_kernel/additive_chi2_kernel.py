from typing import Any, Dict

from sklearn.metrics.pairwise import additive_chi2_kernel

from pureml_evaluate.metrics.metric_base import MetricBase


class AdditiveChi2Kernel(MetricBase):
    name: Any = "additive_chi2_kernel"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y=None, **kwargs):

        if Y is None:
            score = additive_chi2_kernel(X=X, Y=X)
        else:
            score = additive_chi2_kernel(X=X, Y=Y)

        return {self.name: score}

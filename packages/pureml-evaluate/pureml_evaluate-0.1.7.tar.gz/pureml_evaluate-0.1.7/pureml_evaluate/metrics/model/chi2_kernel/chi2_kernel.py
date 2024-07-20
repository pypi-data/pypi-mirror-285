from typing import Any, Dict

from sklearn.metrics.pairwise import chi2_kernel

from pureml_evaluate.metrics.metric_base import MetricBase


class Chi2Kernel(MetricBase):
    name: Any = "chi2_kernel"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, X, Y=None, gamma=1.0, **kwargs):

        if Y is None:
            score = chi2_kernel(X=X, Y=X, gamma=gamma)
        else:
            score = chi2_kernel(X=X, Y=Y, gamma=gamma)

        return {self.name: score}

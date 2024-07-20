from typing import Any

import numpy as np
from scipy.stats import chi2_contingency

from pureml_evaluate.metrics.metric_base import MetricBase


class ChiSquaredStatistic(MetricBase):
    name: Any = "chi_squared_statistic"
    input_type: Any = "dataframe"
    output_type: Any = dict
    kwargs: dict = None

    def parse_data(self, data):
        return data

    def compute(self, reference, production, columns=None, **kwargs):
        if production is None:
            data1 = reference
            mid = len(reference) // 2
            data2 = data1[mid:]
            data1 = data1[:mid]
        else:
            data1 = reference
            data2 = production
        observed = np.stack([data1, data2], axis=1)
        chi2, p, dof, expected = chi2_contingency(observed)

        return {self.name: {"value": chi2}}

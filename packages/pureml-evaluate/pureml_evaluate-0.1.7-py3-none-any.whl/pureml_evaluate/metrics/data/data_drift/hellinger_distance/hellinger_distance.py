from math import sqrt
from typing import Any

import numpy as np

from pureml_evaluate.metrics.metric_base import MetricBase


class HellingerDistance(MetricBase):
    name: Any = "hellinger_distance"
    input_type: Any = "dataframe"
    output_type: Any = dict
    kwargs: dict = None

    def parse_data(self, data):
        # Check if data is already a numpy array
        if isinstance(data, np.ndarray):
            return data.ravel()

        # If data is a pandas dataframe, converting it to numpy array
        try:
            return data.values.ravel()
        except AttributeError:
            raise TypeError("Expected input to be a numpy array or pandas DataFrame.")

    def compute(self, reference, production, columns=None, **kwargs):

        # Parse the data
        p = self.parse_data(reference)

        if production is None:
            mid = len(p) // 2
            q = p[mid:]
            p = p[:mid]
        else:
            q = self.parse_data(production)

        # Ensure p and q are probability distributions (normalized histograms)
        bins = np.linspace(min(p.min(), q.min()), max(p.max(), q.max()), 25)
        p, _ = np.histogram(p, bins=bins, density=True)
        q, _ = np.histogram(q, bins=bins, density=True)

        # Calculate sum of squared differences
        sum_sq_diff = np.sum((np.sqrt(p) - np.sqrt(q)) ** 2)

        # Divide by sqrt(2)
        hellinger = sqrt(sum_sq_diff / 2)

        return {self.name: {"value": hellinger}}

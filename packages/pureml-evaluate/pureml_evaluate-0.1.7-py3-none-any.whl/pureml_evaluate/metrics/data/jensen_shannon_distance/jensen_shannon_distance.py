from typing import Any

import numpy as np
from scipy.stats import entropy

from pureml_evaluate.metrics.metric_base import MetricBase


class JensenShannonDistance(MetricBase):
    name: Any = "jensen_shannon_distance"
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

    def jensen_shannon_divergence(self, p, q):
        # Compute M
        m = 0.5 * (p + q)

        # Compute Jensen-Shannon divergence
        return 0.5 * (entropy(p, m) + entropy(q, m))

    def compute(self, reference, production, columns=None, **kwargs):
        data1 = self.parse_data(reference)

        if production is None:
            mid = len(data1) // 2
            data2 = data1[mid:]
            data1 = data1[:mid]
        else:
            data2 = self.parse_data(production)

        # Convert data1 and data2 to normalized histograms (probability distributions)
        bins = np.linspace(
            min(data1.min(), data2.min()), max(data1.max(), data2.max()), 25
        )
        p, _ = np.histogram(data1, bins=bins, density=True)
        q, _ = np.histogram(data2, bins=bins, density=True)

        # Compute Jensen-Shannon divergence
        js = self.jensen_shannon_divergence(p, q)

        return {self.name: {"value": js}}

from typing import Any

import numpy as np
from scipy.stats import wasserstein_distance

from pureml_evaluate.metrics.metric_base import MetricBase


class WassersteinDistance(MetricBase):
    name: Any = "wasserstein_distance"
    input_type: Any = "dataframe"
    output_type: Any = dict
    kwargs: dict = None

    def parse_data(self, data):
        # Assuming data is a pandas dataframe, converting it to numpy array
        if isinstance(data, np.ndarray):
            return data.ravel()

        # If data is a pandas dataframe, converting it to numpy array
        try:
            return data.values.ravel()
        except AttributeError:
            raise TypeError("Expected input to be a numpy array or pandas DataFrame.")

    def compute(self, reference, production, columns, **kwargs):

        # Parse the data
        data1 = self.parse_data(reference)

        if production is None:
            split = len(data1) // 2
            data2 = data1[split:]
            data1 = data1[:split]
        else:
            data2 = self.parse_data(production)

        bins = np.linspace(
            min(data1.min(), data2.min()), max(data1.max(), data2.max()), 25
        )
        p, _ = np.histogram(data1, bins=bins, density=True)
        q, _ = np.histogram(data2, bins=bins, density=True)

        # Compute Wasserstein distance
        result = wasserstein_distance(p, q)

        return {self.name: {"value": result}}

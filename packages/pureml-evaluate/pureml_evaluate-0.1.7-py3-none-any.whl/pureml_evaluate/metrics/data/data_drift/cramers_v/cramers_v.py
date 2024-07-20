from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from pureml_evaluate.metrics.metric_base import MetricBase


class CramersV(MetricBase):
    name: Any = "cramers_v"
    input_type: Any = "dataframe"
    output_type: Any = dict
    kwargs: dict = None

    # Cramer's V is only defined for DataFrames
    def parse_data(self, data: Any) -> pd.DataFrame:
        if isinstance(data, pd.DataFrame):
            return data.copy()
        elif isinstance(data, np.ndarray):
            return pd.DataFrame(data)
        else:
            raise TypeError(
                "Input data should be either a pandas dataframe or a numpy array."
            )

    def compute(
        self,
        reference: Any,
        production: Optional[Any] = None,
        columns=None,
        split_ratio: float = 0.5,
        **kwargs
    ) -> dict:
        data1 = self.parse_data(reference)

        if production is None:
            split_idx = int(len(data1) * split_ratio)
            data2 = data1.iloc[split_idx:].copy()
            data1 = data1.iloc[:split_idx].copy()
        else:
            data2 = self.parse_data(production)

        # Ensure dataframes are of the same shape
        if data1.shape != data2.shape:
            raise ValueError(
                "Reference and Production datasets must have the same shape"
            )

        # Compute Cramer's V for each pair of columns
        results = {}
        for col in data1.columns:
            # Convert columns to string to handle any type of data (categorical, numerical)
            series1 = data1[col].astype(str)
            series2 = data2[col].astype(str)

            cont_table = pd.crosstab(series1, series2)

            chi2, _, _, _ = chi2_contingency(cont_table)
            n = cont_table.sum().sum()
            phi2 = chi2 / n
            r, k = cont_table.shape
            cramers_v = np.sqrt(phi2 / min(r - 1, k - 1))
            results[col] = cramers_v

        return {self.name: {"value": results}}

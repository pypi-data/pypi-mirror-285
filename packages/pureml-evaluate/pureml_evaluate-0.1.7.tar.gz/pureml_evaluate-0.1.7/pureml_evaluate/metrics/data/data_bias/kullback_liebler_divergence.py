from typing import Dict

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from pureml_evaluate.metrics.metric_base import MetricBase

class KL(MetricBase):
    name: str = "kl"
    input: str = "dataframe"
    output: str = "dataframe"
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, feature: pd.Series, sensitive_facet_index: pd.Series):
        # """
        # Kullback-Liebler Divergence (KL) for multiple sensitive features.

        #     .. math::
        #     KL(Pa, Pd) = \sum_{x}{Pa(x) \ log \frac{Pa(x)}{Pd(x)}}

        #     :param label: column of labels
        #     :param sensitive_facet: column indicating sensitive group (not necessarily boolean)
        #     :return: Kullback and Leibler (KL) divergence metric for each group vs the rest
        # """
        unique_facets = sensitive_facet_index.unique()
        kl_results = {}

        for facet in unique_facets:
            xs_a = feature[sensitive_facet_index != facet]
            xs_d = feature[sensitive_facet_index == facet]

            (Pa, Pd) = pdfs_aligned_nonzero(
                xs_a, xs_d
            )  # assuming that this function is defined elsewhere

            if len(Pa) == 0 or len(Pd) == 0:
                raise ValueError(
                    "No instance of common facet found, dataset may be too small or improperly aligned"
                )

            kl = np.sum(Pa * np.log(Pa / Pd))
            kl_results[facet] = kl

        return {self.name: kl_results}


def pdfs_aligned_nonzero(
    xs_a: pd.Series, xs_d: pd.Series, num_points: int = 1000
) -> (np.ndarray, np.ndarray):
    """
    Compute PDFs of two data series, ensure they are aligned and non-zero.

    :param xs_a: Values from group A
    :param xs_d: Values from group D
    :param num_points: Number of points to evaluate PDFs at
    :return: (Pa, Pd) - PDFs of input series, aligned and non-zero
    """

    # Get kernel density estimates for both groups
    kde_a = gaussian_kde(xs_a)
    kde_d = gaussian_kde(xs_d)

    # Define a common support over which to evaluate the PDFs
    # You might want to adjust this depending on your specific use case
    common_support = np.linspace(
        min(xs_a.min(), xs_d.min()), max(xs_a.max(), xs_d.max()), num_points
    )

    # Evaluate PDFs
    Pa = kde_a.evaluate(common_support)
    Pd = kde_d.evaluate(common_support)

    # Ensure non-zero: add a very small constant if necessary
    epsilon = 1e-10  # You might want to adjust the magnitude of epsilon
    Pa = np.where(Pa <= epsilon, epsilon, Pa)
    Pd = np.where(Pd <= epsilon, epsilon, Pd)

    return Pa, Pd

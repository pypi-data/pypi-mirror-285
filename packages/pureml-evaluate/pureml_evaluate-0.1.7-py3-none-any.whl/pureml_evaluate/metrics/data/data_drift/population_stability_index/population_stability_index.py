from typing import Any

import numpy as np

from pureml_evaluate.metrics.metric_base import MetricBase


class PopulationStabilityIndex(MetricBase):
    name: Any = "population_stability_index"
    input_type: Any = "dataframe"
    output_type: Any = dict
    kwargs: dict = None

    def parse_data(self, data):
        return data

    def compute(self, reference, production=None, columns=None, bins=10, **kwargs):
        if production is None:
            mid = len(reference) // 2
            production = reference[mid:]
            reference = reference[:mid]

        # Exception: Empty Data
        if len(reference) == 0 or len(production) == 0:
            raise ValueError(
                "Neither the reference nor the production data should be empty."
            )

        # Exception: Mismatched Shapes
        if len(reference) != len(production):
            raise ValueError(
                "The reference and production data should have the same length for a meaningful PSI computation."
            )

        # Exception: Negative Values in Data
        if np.any(reference < 0) or np.any(production < 0):
            raise ValueError(
                "Both datasets should have non-negative values for a meaningful PSI computation."
            )

        # Calculate histogram for reference and production data
        hist_ref, bin_edges = np.histogram(reference, bins=bins, density=True)
        hist_prod, _ = np.histogram(production, bins=bin_edges, density=True)

        # Exception: All Zero Bins
        if np.sum(hist_ref) == 0 or np.sum(hist_prod) == 0:
            raise ValueError("Histograms should not have all zero bins.")

        # Convert histogram counts to proportions
        prop_ref = hist_ref / sum(hist_ref)
        prop_prod = hist_prod / sum(hist_prod)

        # Calculate PSI for each bin, adding a small value to avoid division by zero
        small_value = 1e-10
        psi_bins = (prop_ref - prop_prod) * np.log(
            (prop_ref + small_value) / (prop_prod + small_value)
        )

        # Handle division by zero and log of zero issues by replacing NaN and inf values with zero
        psi_bins = np.where(np.isnan(psi_bins) | np.isinf(psi_bins), 0, psi_bins)

        # Sum all PSI values for each bin to get the total PSI
        psi_total = np.sum(psi_bins)

        return {self.name: {"value": psi_total}}

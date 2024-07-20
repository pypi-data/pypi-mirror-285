from typing import Any

import numpy as np
import pandas as pd

from pureml_evaluate.metrics.metric_base import MetricBase


class IdentifierLabelCorrelation(MetricBase):
    name: Any = "identifier_label_correlation"
    input_type: Any = "dataframe"
    output_type: Any = pd.DataFrame
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, identifier_column, label_column, **kwargs):
        identifier_label_corr = []

        identifier_values = data[identifier_column]
        label_values = data[label_column]

        pps_score = self.calculate_pps(identifier_values, label_values)
        identifier_label_corr.append(
            {
                "Label": label_column,
                "Identifier": identifier_column,
                "PPS_Score": pps_score,
            }
        )

        result_df = pd.DataFrame(identifier_label_corr)

        return result_df

    def calculate_pps(self, identifier_values, label_values):
        unique_identifiers = identifier_values.unique()

        total_samples = len(label_values)
        pps_score = 0.0

        for identifier in unique_identifiers:
            label_subset = label_values[identifier_values == identifier]
            label_subset_count = len(label_subset)

            if label_subset_count > 0:
                label_subset_ratio = label_subset.sum() / label_subset_count
                label_ratio = label_values.sum() / total_samples

                pps_score += (
                    label_subset_count * (label_subset_ratio - label_ratio) ** 2
                )

        pps_score /= total_samples
        pps_score = np.sqrt(pps_score)

        return pps_score

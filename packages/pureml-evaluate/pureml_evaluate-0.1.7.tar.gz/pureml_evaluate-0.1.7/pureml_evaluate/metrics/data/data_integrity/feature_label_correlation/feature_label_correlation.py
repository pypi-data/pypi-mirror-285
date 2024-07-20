from typing import Any

import numpy as np
import pandas as pd

from pureml_evaluate.metrics.metric_base import MetricBase


class FeatureLabelCorrelation(MetricBase):
    name: Any = "feature_label_correlation"
    input_type: Any = "dataframe"
    output_type: Any = pd.DataFrame
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, label_column, **kwargs):
        feature_label_corr = []

        for column in data.columns:
            if column == label_column:
                continue

            if data[column].dtype == "object":
                pps_score = self.calculate_categorical_correlation(
                    data[column], data[label_column]
                )
            else:
                pps_score = self.calculate_numerical_correlation(
                    data[column], data[label_column]
                )

            feature_label_corr.append({"Column": column, "PPS_Score": pps_score})

        result_df = pd.DataFrame(feature_label_corr)

        return {self.name: result_df}

    def calculate_categorical_correlation(self, feature_column, label_column):
        feature_label_df = pd.DataFrame(
            {"Feature": feature_column, "Label": label_column}
        )
        contingency_table = pd.crosstab(
            feature_label_df["Feature"], feature_label_df["Label"]
        )
        chi2 = self.calculate_chi2(contingency_table)
        total_samples = len(feature_label_df)
        pps_score = chi2 / total_samples

        return pps_score

    def calculate_numerical_correlation(self, feature_column, label_column):
        feature_label_df = pd.DataFrame(
            {"Feature": feature_column, "Label": label_column}
        )
        feature_label_df = feature_label_df.dropna()
        feature_values = feature_label_df["Feature"]
        label_values = feature_label_df["Label"]

        numerator = np.cov(feature_values, label_values)[0, 1] ** 2
        denominator = np.var(feature_values) * np.var(label_values)
        pps_score = numerator / denominator if denominator != 0 else 0.0

        return pps_score

    def calculate_chi2(self, contingency_table):
        chi2 = contingency_table.apply(
            lambda r: np.sum((r - np.mean(r)) ** 2 / np.mean(r))
        )
        chi2 = chi2.sum()

        return chi2

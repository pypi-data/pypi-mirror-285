from typing import Any

import numpy as np
import pandas as pd

from pureml_evaluate.metrics.metric_base import MetricBase


class OutlierSampleDetection(MetricBase):
    name: Any = "outlier_sample_detection"
    input_type: Any = "dataframe"
    output_type: Any = pd.DataFrame
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, nearest_neighbors_percent=0.1, extent=3, **kwargs):
        distance_matrix = self.calculate_distance_matrix(data)
        outlier_indices = self.detect_outliers(
            distance_matrix, nearest_neighbors_percent, extent
        )

        outlier_samples = data.iloc[outlier_indices]

        return outlier_samples

    def calculate_distance_matrix(self, data):
        n = len(data)
        distance_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                distance = self.calculate_distance(data[i], data[j])
                distance_matrix[i, j] = distance
                distance_matrix[j, i] = distance

        return distance_matrix

    def calculate_distance(self, sample1, sample2):
        numeric_distance = np.abs(sample1 - sample2).sum()
        categorical_distance = (sample1 != sample2).sum()

        distance = numeric_distance + categorical_distance
        return distance

    def detect_outliers(self, distance_matrix, nearest_neighbors_percent, extent):
        num_neighbors = int(distance_matrix.shape[0] * nearest_neighbors_percent)
        outlier_indices = []

        for i in range(distance_matrix.shape[0]):
            row = distance_matrix[i, :]
            sorted_distances = np.sort(row)
            loop = np.mean(sorted_distances[:num_neighbors]) / np.mean(
                sorted_distances[num_neighbors:]
            )

            if loop > extent:
                outlier_indices.append(i)

        return outlier_indices

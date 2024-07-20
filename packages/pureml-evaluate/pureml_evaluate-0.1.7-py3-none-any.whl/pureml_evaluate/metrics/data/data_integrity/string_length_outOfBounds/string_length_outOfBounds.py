from typing import Any

from pureml_evaluate.metrics.metric_base import MetricBase


class StringLengthOutOfBounds(MetricBase):
    name: Any = "length_of_string_out_of_bounds"
    input_type: Any = "dataframe"
    output_type: Any = None
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, **kwargs):
        string_lengths = data.select_dtypes(exclude=["int", "float", "bool"]).applymap(
            len
        )

        string_lengths_out_of_bounds = {}
        for column in string_lengths.columns:
            column_lengths = string_lengths[column]
            mean_length = column_lengths.mean()
            std_length = column_lengths.std()

            # Define the thresholds for determining if a string length is out of bounds
            lower_threshold = mean_length - 2 * std_length
            upper_threshold = mean_length + 2 * std_length

            # Check if the string length is out of bounds for each value
            out_of_bounds_indices = (column_lengths < lower_threshold) | (
                column_lengths > upper_threshold
            )

            # Count the number of outliers
            num_outliers = out_of_bounds_indices.sum()

            # If there are outliers, add the column to the result
            if num_outliers > 0:
                min_length = column_lengths.min()
                max_length = column_lengths.max()
            else:
                min_length = None
                max_length = None

            string_lengths_out_of_bounds[column] = {
                "num_outliers": num_outliers,
                "normal_length_range": f"{min_length}-{max_length}",
                "outlier_length_range": (
                    f"{column_lengths[out_of_bounds_indices].min()}-{column_lengths[out_of_bounds_indices].max()}"
                    if num_outliers > 0
                    else None
                ),
            }

        return {self.name: string_lengths_out_of_bounds}

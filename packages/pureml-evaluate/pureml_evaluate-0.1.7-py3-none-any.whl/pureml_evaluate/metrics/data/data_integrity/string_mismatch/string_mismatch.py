import string
from typing import Any

import pandas as pd

from pureml_evaluate.metrics.metric_base import MetricBase


class StringMismatch(MetricBase):
    name: Any = "string_mismatch"
    input_type: Any = "dataframe"
    output_type: Any = pd.DataFrame
    kwargs: Any = {}


    def parse_data(self, data):
        return data

    def compute(self, data, **kwargs):
        string_mismatch_info = []

        string_columns = data.select_dtypes(exclude="int64").columns
        for column in string_columns:
            unique_values = data[column].unique()
            if len(unique_values) > 1:
                base_form_to_variants = self.get_base_form_to_variants_dict(
                    unique_values
                )
                for base_form, variants in base_form_to_variants.items():
                    mismatch_count = len(variants)
                    mismatch_percentage = (len(variants) / len(unique_values)) * 100
                    string_mismatch_info.append(
                        [
                            column,
                            base_form,
                            variants,
                            mismatch_count,
                            mismatch_percentage,
                        ]
                    )

        columns = ["Column", "Base String", "Actual Strings", "Count", "Percentage"]
        string_mismatch_df = pd.DataFrame(string_mismatch_info, columns=columns)

        return {self.name: string_mismatch_df}

    def get_base_form_to_variants_dict(self, uniques):
        base_form_to_variants = {}
        for value in uniques:
            base_form = self.get_base_string(value)
            if base_form in base_form_to_variants:
                base_form_to_variants[base_form].append(value)
            else:
                base_form_to_variants[base_form] = [value]
        return base_form_to_variants

    def get_base_string(self, string_value):
        # Convert to lowercase
        base_string = str(string_value).lower()
        # Remove punctuations
        base_string = base_string.translate(str.maketrans("", "", string.punctuation))
        return base_string

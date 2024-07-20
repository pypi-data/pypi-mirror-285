from typing import Any

import pandas as pd

from pureml_evaluate.metrics.metric_base import MetricBase


class SpecialCharacters(MetricBase):
    name: Any = "special_characters"
    input_type: Any = "dataframe"
    output_type: Any = pd.DataFrame
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, **kwargs):
        special_characters_info = []

        for column in data.columns:
            total_entries = len(data[column])
            special_character_entries = self.count_special_character_entries(
                data[column]
            )
            special_character_percentage = (
                special_character_entries / total_entries
            ) * 100

            special_characters_info.append(
                {
                    "Column": column,
                    "Special_Character_Count": special_character_entries,
                    "Total_Count": total_entries,
                    "Special_Character_Percentage": special_character_percentage,
                }
            )

        result_df = pd.DataFrame(special_characters_info)

        return {self.name: result_df}

    def count_special_character_entries(self, column):
        pattern = r"^[\W_]+$"  # Match only special characters
        return column.astype(str).str.match(pattern).sum()

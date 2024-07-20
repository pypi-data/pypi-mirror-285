from typing import Any

import numpy as np
import pandas as pd

from pureml_evaluate.metrics.metric_base import MetricBase


class DataDuplicatesCheck(MetricBase):
    name: Any = "data_duplicates"
    input_type: Any = "dataframe"
    output_type: Any = pd.DataFrame
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, data, **kwargs):
        duplicates = data[data.duplicated(keep=False)]
        duplicates_count = (
            duplicates.groupby(duplicates.columns.tolist())
            .size()
            .reset_index(name="Number of Duplicates")
        )
        duplicates_count["Entropy"] = duplicates_count.groupby(
            duplicates.columns.tolist()
        )["Number of Duplicates"].transform(
            lambda x: -np.sum((x / x.sum()) * np.log2(x / x.sum()))
        )
        duplicates_count["NumParams"] = duplicates_count[
            duplicates.columns.tolist()
        ].apply(lambda x: len(set(x)), axis=1)

        return {self.name: duplicates_count}

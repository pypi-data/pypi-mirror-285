from typing import Any

from scipy.stats import ks_2samp

from pureml_evaluate.metrics.metric_base import MetricBase


class KolmogorovSmirnov(MetricBase):
    name: Any = "kolmogorov_smirnov"
    input_type: Any = "dataframe"
    output_type: Any = dict
    kwargs: dict = None

    def parse_data(self, data):
        return data

    def compute(self, reference, production, columns, **kwargs):
        if production is None:
            split = len(reference) // 2
            data2 = production[split:]
            data1 = production[:split]
        else:
            data1 = reference
            data2 = production

        result = {}
        # len(columns) != 0 will throw an error as columns when not passed are set to None. len(columns) != 0 is used before
        if columns is not None:
            for column in columns:
                ks_stat, p_value = ks_2samp(data1[column], data2[column])
                result[column] = {"ks_stat": ks_stat, "p_value": p_value}

        # If no columns are specified, compute KS for each column in the dataframe
        else:
            for column in data1.columns:
                ks_stat, p_value = ks_2samp(data1[column], data2[column])
                result[column] = {"ks_stat": ks_stat, "p_value": p_value}

        return {self.name: result}

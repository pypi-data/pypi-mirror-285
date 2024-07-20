from typing import Any, Dict

from sklearn.metrics import homogeneity_completeness_v_measure

from pureml_evaluate.metrics.metric_base import MetricBase


class HomogeneityCompletenessVMeasure(MetricBase):
    name: Any = "homogeneity_completeness_v_measure"
    input_type: Any = "int"
    output_type: Any = None
    kwargs: Dict = None

    def parse_data(self, data):
        return data

    def compute(self, labels_true, labels_pred, beta=1.0, **kwargs):

        homogeneity, completeness, v_measure = homogeneity_completeness_v_measure(
            labels_true=labels_true, labels_pred=labels_pred, beta=beta
        )

        return {
            self.name: {
                "homogeneity": homogeneity,
                "completeness": completeness,
                "v_measure": v_measure,
            }
        }

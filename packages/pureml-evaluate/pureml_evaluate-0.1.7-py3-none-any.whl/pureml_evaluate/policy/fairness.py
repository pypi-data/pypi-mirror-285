from typing import List

from .policy_base import PolicyBase


class FairnessPolicy(PolicyBase):
    list_metrics: List[str] = None
    list_metrics_kwargs: List[dict] = None
    # list_thresholds: List[Union[float, int]] = None
    list_of_thresholds: dict = {}

    def compute(
        self,
        list_metrics,
        references,
        predictions,
        sensitive_features,
        prediction_scores,
        list_of_thresholds,
        **kwargs
    ):
        return super().compute(
            references=references,
            predictions=predictions,
            prediction_scores=prediction_scores,
            list_metrics=list_metrics,
            sensitive_features=sensitive_features,
            type="fairness",
            list_of_thresholds=list_of_thresholds,
            **kwargs
        )


# list_metrics_have = []
# list_metrics = []
# reference and production.

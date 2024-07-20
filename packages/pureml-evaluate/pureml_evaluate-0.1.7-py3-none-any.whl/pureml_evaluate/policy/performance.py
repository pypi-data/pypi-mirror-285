from typing import List

from .policy_base import PolicyBase


class Performance(PolicyBase):
    list_metrics: List[str] = None
    list_metrics_kwargs: List[dict] = None
    # list_thresholds: List[Union[float, int]] = None
    list_of_thresholds: dict = {}
    problem_type: str = None
    # problem_type = 'classification' or 'regression' or 'nlp'

    def compute(
        self,
        list_metrics,
        references,
        predictions,
        prediction_scores,
        list_of_thresholds,
        **kwargs
    ):
        return super().compute(
            references=references,
            predictions=predictions,
            prediction_scores=prediction_scores,
            list_metrics=list_metrics,
            type="performance",
            list_of_thresholds=list_of_thresholds,
            **kwargs
        )


# list_metrics_have = []
# list_metrics = []
# reference and production.

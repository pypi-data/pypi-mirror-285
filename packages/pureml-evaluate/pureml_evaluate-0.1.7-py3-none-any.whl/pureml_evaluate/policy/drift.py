from typing import List

from .policy_base import PolicyBase


class Drift(PolicyBase):
    list_metrics: List[str] = None
    list_metrics_kwargs: List[dict] = None
    # list_thresholds: List[Union[float, int]] = None
    list_of_thresholds: dict = {}

    def compute(
        self,
        list_metrics,
        references,
        productions,
        columns,
        list_of_thresholds,
        **kwargs
    ):
        return super().compute(
            references=references,
            productions=productions,
            columns=columns,
            list_metrics=list_metrics,
            type="drift",
            list_of_thresholds=list_of_thresholds,
            **kwargs
        )


# list_metrics_have = []
# list_metrics = []
# reference and production.

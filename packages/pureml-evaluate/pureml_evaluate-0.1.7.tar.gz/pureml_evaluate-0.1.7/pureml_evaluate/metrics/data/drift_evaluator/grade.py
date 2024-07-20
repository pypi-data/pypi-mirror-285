import typing
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, model_validator

from .multivariate import Multivariate
from .univariate import Univariate


class DriftTypes(str, Enum):
    feature_drift = "feature_drift"
    label_drift = "label_drift"


class VariateTypes(str, Enum):
    univariate = "univariate"
    multivariate = "multivariate"


class DatasetTypes(str, Enum):
    continuous = "continuous"
    discrete = "discrete"


class Grader(BaseModel):
    drift_types: DriftTypes
    variate_types: VariateTypes
    dataset_types: DatasetTypes

    kwargs: Optional[Dict[str, Any]] = None
    scores: Dict[str, Any] = {}
    task_grader: Optional[Any] = None
    columns: Optional[typing.List[str]] = None
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @model_validator(mode="before")
    @classmethod
    def _set_fields(cls, values: dict) -> dict:
        variate_type = values.get("variate_types")

        if variate_type == VariateTypes.univariate:
            task_grader = Univariate()
        elif variate_type == VariateTypes.multivariate:
            task_grader = Multivariate()
        else:
            task_grader = None

        values["task_grader"] = task_grader
        values["kwargs"] = {
            "drift_types": values.get("drift_types"),
            "dataset_types": values.get("dataset_types"),
        }

        return values

    def compute(self, reference, production, **kwargs):
        if self.task_grader is not None:
            self.task_grader.reference = reference
            self.task_grader.production = production
            self.task_grader.kwargs = (
                self.kwargs
            )  # This takes the kwargs from the root_validator instead of the local kwargs
            self.task_grader.columns = self.columns
            print(f"Columns in Grader File: {self.task_grader.columns}")
            self.scores = self.task_grader.compute()
        return self.scores


def grader(variate_types, **kwargs):
    grade = Grader(
        variate_types=variate_types,
        drift_types=kwargs.get("drift_types"),
        dataset_types=kwargs.get("dataset_types"),
    )
    return grade

import typing
from enum import Enum

# from .model.performance.nlp import NLP
from pydantic import BaseModel, ConfigDict, model_validator

from .model.fairness.fairness import Fairness
from .model.performance.classification import Classification
from .model.performance.regression import Regression


class TaskTypes(str, Enum):
    classification = "classification"
    regression = "regression"
    fairness = "fairness"


#    nlp = "nlp"


class Grader(BaseModel):
    # def __init__(self, task_type):
    task_type: TaskTypes

    kwargs: typing.Any = None
    scores: typing.Any = {}
    task_grader: typing.Any = None
    metrics: typing.Any = None
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @model_validator(mode="before")
    @classmethod
    def _set_fields(cls, values: dict) -> dict:
        # print(values)
        # print(values.keys())
        # print("metrics" in values.keys())
        # print(values["metrics"])

        task_type = values["task_type"]
        metrics_all = values["metrics"]

        metrics = None

        # print("here")

        if task_type is not None:

            if task_type == TaskTypes.classification:
                if metrics_all is not None:
                    if TaskTypes.classification in metrics_all:
                        metrics = metrics_all[TaskTypes.classification.value]
                task_grader = Classification(metrics=metrics)
                # print("classification")
            elif task_type == TaskTypes.regression:
                if metrics_all is not None:
                    if TaskTypes.regression in metrics_all:
                        metrics = metrics_all[TaskTypes.regression.value]
                task_grader = Regression(metrics=metrics)
            elif task_type == TaskTypes.fairness:
                if metrics_all is not None:
                    if TaskTypes.fairness in metrics_all:
                        metrics = metrics_all[TaskTypes.fairness.value]
                task_grader = Fairness(metrics=metrics)
                # print("fairness")
            #            elif task_type == TaskTypes.nlp:
            # if TaskTypes.nlp in metrics_all.keys():
            #     metrics_temp = metrics_all[TaskTypes.nlp]
            #                task_grader = NLP()
            else:
                task_grader = None

            values["task_grader"] = task_grader

        # print("here 2")

        return values

    def compute(
        self,
        references,
        predictions,
        prediction_scores=None,
        sensitive_features=None,
        **kwargs
    ):

        # print(self.task_grader)
        if self.task_grader is not None:
            # print('task grader is not none')
            self.task_grader.kwargs = kwargs
            self.task_grader.references = references
            self.task_grader.predictions = predictions
            self.task_grader.prediction_scores = prediction_scores
            self.task_grader.sensitive_features = sensitive_features

            # print("task grader", self.task_grader)

            self.scores = self.task_grader.compute()

        return self.scores


def grader(task_type, **kwargs):
    grade = Grader(task_type=task_type)

    return grade

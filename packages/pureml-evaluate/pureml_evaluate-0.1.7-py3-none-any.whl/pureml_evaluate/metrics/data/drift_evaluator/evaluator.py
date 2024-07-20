from collections import defaultdict
from typing import Any, List, Union

from pydantic import BaseModel, ConfigDict

from .grade import Grader


class Evaluator(BaseModel):
    reference: Any = None
    production: Any = None
    drift_evaluator: Union[List[str], str]
    variate_evaluator: Union[List[str], str]
    datasettype: Union[List[str], str]
    grader: List[Grader] = []
    columns: List[str] = []
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    def load_graders(self):
        # Ensure the evaluators are in list format
        drift_evaluators = (
            [self.drift_evaluator]
            if isinstance(self.drift_evaluator, str)
            else self.drift_evaluator
        )
        variate_evaluators = (
            [self.variate_evaluator]
            if isinstance(self.variate_evaluator, str)
            else self.variate_evaluator
        )
        dataset_types = (
            [self.datasettype]
            if isinstance(self.datasettype, str)
            else self.datasettype
        )

        # For each combination of evaluators, create a Grader
        for drift in drift_evaluators:
            for variate in variate_evaluators:
                for dataset in dataset_types:
                    self.grader.append(
                        Grader(
                            drift_types=drift,
                            variate_types=variate,
                            dataset_types=dataset,
                            columns=self.columns,
                        )
                    )

    def load(self):
        self.load_graders()

    def evaluate(self):
        values_all = defaultdict(dict)
        for g in self.grader:
            # print(f"G: {g}")
            grader_type = g.drift_types.value
            # print(grader_type)
            # print(f"Grader Type: {grader_type}")
            values = g.compute(
                reference=self.reference,
                production=self.production,
                kwargs=g.kwargs,
                columns=self.columns,
            )
            values_all[grader_type].update(values)
        values_all = dict(values_all)
        return values_all


def eval(
    reference,
    production,
    drift_evaluator,
    variate_evaluator,
    datasettype,
    columns: list[str],
):
    evaluator = Evaluator(
        reference=reference,
        production=production,
        drift_evaluator=drift_evaluator,
        variate_evaluator=variate_evaluator,
        datasettype=datasettype,
        columns=columns,
    )
    evaluator.load()
    return evaluator.evaluate()

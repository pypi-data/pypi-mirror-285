from pureml_evaluate.drift_metrics.tabular.chi_squared_statistic.chi_squared_statistic import (
    ChiSquaredStatistic,
)
from pureml_evaluate.drift_metrics.tabular.cramers_v.cramers_v import CramersV
from pureml_evaluate.drift_metrics.tabular.population_stability_index.population_stability_index import (
    PopulationStabilityIndex,
)


class Discrete:

    def __init__(self):
        self.kwargs = {}

        self.reference = None
        self.production = None

        self.metrics = [ChiSquaredStatistic(), CramersV(), PopulationStabilityIndex()]

        self.scores = {}
        self.columns = []

    def compute(self):
        for m in self.metrics:
            try:
                score = m.compute(
                    reference=self.reference,
                    production=self.production,
                    kwargs=self.kwargs,
                    columns=self.columns,
                )
                self.scores.update(score)
            except Exception as e:
                print("Unable to compute", m)
                print(f"Exception: {e}")

        return self.scores

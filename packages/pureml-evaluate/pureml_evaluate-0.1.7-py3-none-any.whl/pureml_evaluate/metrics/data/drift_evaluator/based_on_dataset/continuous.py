from pureml_evaluate.drift_metrics.tabular.hellinger_distance.hellinger_distance import (
    HellingerDistance,
)
from pureml_evaluate.drift_metrics.tabular.kolmogorov_smirnov.kolmogorov_smirnov_statistic import (
    KolmogorovSmirnov,
)
from pureml_evaluate.drift_metrics.tabular.l_infinity_distance.l_infinity_distance import (
    LInfinityDistance,
)
from pureml_evaluate.drift_metrics.tabular.wasserstein_distance.wasserstein_distance import (
    WassersteinDistance,
)


class Continuous:  # Numerical Dataset
    def __init__(self):

        self.kwargs = {}
        self.reference = None
        self.production = None

        self.metrics = [
            KolmogorovSmirnov(),
            WassersteinDistance(),
            HellingerDistance(),
            LInfinityDistance(),
        ]

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
                print("From Continuous File")
                print("Unable to compute", m)
                print(f"Exception: {e}")

        return self.scores

from .based_on_dataset.continuous import Continuous
from .based_on_dataset.discrete import Discrete


class FeatureLabelDrift:

    def __init__(self):
        self.reference = None
        self.production = None
        self.kwargs = {}

        self.metrics = []
        self.scores = {}
        self.columns = []

    def get_metrics(self):
        if self.kwargs["dataset_types"] == "continuous":
            self.metrics.append(Continuous())
        if self.kwargs["dataset_types"] == "discrete":
            self.metrics.append(Discrete())

    def compute(self):
        self.get_metrics()
        for m in self.metrics:
            try:
                t = m  # t = Continuous()
                t.reference = self.reference  # t.reference = reference
                t.production = self.production
                t.columns = self.columns
                score = t.compute()
                self.scores.update(score)
            except Exception as e:
                print("From Feature_Drift File")
                print("Unable to compute", m)
                print(f"Exception: {e}")
        # print(self.scores)
        return self.scores

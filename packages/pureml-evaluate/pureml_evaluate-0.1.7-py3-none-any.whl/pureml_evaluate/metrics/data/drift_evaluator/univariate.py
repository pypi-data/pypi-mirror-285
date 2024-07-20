from .feature_drift import FeatureLabelDrift
from .label_drift import LabelDrift


class Univariate:

    def __init__(self):
        self.reference = None
        self.production = None
        self.kwargs = {}

        self.metrics = []
        self.scores = {}
        self.columns = []

    def compute(self):
        self.compute_drift()
        for m in self.metrics:
            try:
                t = m  # t = FeatureLabelDrift()
                t.reference = self.reference  # t.reference = reference
                t.production = self.production  # t.production = production
                t.columns = self.columns  # t.columns = columns
                t.kwargs = self.kwargs  # t.kwargs = kwargs
                score = t.compute()
                self.scores.update(score)
            except Exception as e:
                print("From Univariate File")
                print("Unable to compute", m)
                print(f"Exception: {e}")
        return self.scores
        # Yet to complete this function

    def compute_drift(self):
        if self.kwargs["drift_types"] == "feature_drift":
            self.metrics.append(FeatureLabelDrift())
        if self.kwargs["drift_types"] == "label_drift":
            self.metrics.append(LabelDrift())

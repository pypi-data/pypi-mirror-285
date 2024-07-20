from pureml_evaluate.metrics.d2_absolute_error_score.d2_absolute_error_score import (
    D2AbsoluteErrorScore,
)
from pureml_evaluate.metrics.d2_pinball_score.d2_pinball_score import D2PinballScore
from pureml_evaluate.metrics.d2_tweedie_score.d2_tweedie_score import D2TweedieScore
from pureml_evaluate.metrics.explained_variance_score.explained_variance_score import (
    ExplainedVarianceScore,
)
from pureml_evaluate.metrics.max_error.max_error import MaxError
from pureml_evaluate.metrics.mean_absolute_error.mean_absolute_error import (
    MeanAbsoluteError,
)
from pureml_evaluate.metrics.mean_absolute_percentage_error.mean_absolute_percentage_error import (
    MeanAbsolutePercentageError,
)
from pureml_evaluate.metrics.mean_gamma_deviance.mean_gamma_deviance import (
    MeanGammaDeviance,
)
from pureml_evaluate.metrics.mean_poisson_deviance.mean_poisson_deviance import (
    MeanPoissonDeviance,
)
from pureml_evaluate.metrics.mean_squared_error.mean_squared_error import (
    MeanSquaredError,
)
from pureml_evaluate.metrics.mean_squared_log_error.mean_squared_log_error import (
    MeanSquaredLogError,
)
from pureml_evaluate.metrics.median_absolute_error.median_absolute_error import (
    MedianAbsoluteError,
)
from pureml_evaluate.metrics.r2_score.r2_score import R2Score


class Regression:
    def __init__(self, metrics=None):
        self.task_type = "regression"
        self.evaluation_type = "performance"

        self.kwargs = None
        self.evaluator = None

        self.metrics = metrics

        self.metrics_list = [
            MeanAbsoluteError(),
            MeanSquaredError(),
            R2Score(),
            MaxError(),
            MeanSquaredLogError(),
            MedianAbsoluteError(),
            MeanPoissonDeviance(),
            MeanGammaDeviance(),
            MeanAbsolutePercentageError(),
            D2AbsoluteErrorScore(),
            D2PinballScore(),
            D2TweedieScore(),
            ExplainedVarianceScore(),
        ]
        self.metrics_default = {m.name: m for m in self.metrics_list}

        if self.metrics is None:
            self.metrics = self.metrics_default
        else:
            self.metrics = self.parse_metrics()

        self.scores = {}

    def parse_metrics(self):
        metrics_temp = {}

        for metric in self.metrics:
            metric_key = metric["name"]
            if metric_key in self.metrics_default.keys():
                metrics_temp[metric_key] = self.metrics_default[metric_key]
            else:
                print("Metric ", metric_key, "not found")

    def compute(self):

        for metric_key, metric in self.metrics.items():
            # Adding  prediction scores to kwargs. It will be utilized my metrics needing it(roc_auc).
            try:
                self.kwargs["prediction_scores"] = self.prediction_scores

                score = metric.compute(
                    references=self.references,
                    predictions=self.predictions,
                    **self.kwargs
                )

                self.scores.update(score)

            except Exception as e:
                print("Unable to compute", metric_key)
                print(e)

        return self.scores

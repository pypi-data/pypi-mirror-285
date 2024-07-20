from pureml_evaluate.metrics.accuracy.accuracy import Accuracy
from pureml_evaluate.metrics.average_precision_score.average_precision_score import (
    AveragePrecisionScore,
)
from pureml_evaluate.metrics.balanced_accuracy_score.balanced_accuracy_score import (
    BalancedAccuracyScore,
)
from pureml_evaluate.metrics.brier_score_loss.brier_score_loss import BrierScoreLoss
from pureml_evaluate.metrics.f1_score.f1_score import F1
from pureml_evaluate.metrics.log_loss.log_loss import LogLoss
from pureml_evaluate.metrics.precision.precision import Precision
from pureml_evaluate.metrics.recall.recall import Recall
from pureml_evaluate.metrics.roc_auc.roc_auc import ROC_AUC
from pureml_evaluate.metrics.top_k_accuracy_score.top_k_accuracy_score import (
    TopKAccuracyScore,
)


class Classification:
    def __init__(self, metrics=None):
        self.task_type = "classification"
        self.evaluation_type = "performance"

        self.kwargs = {}

        self.references = None
        self.predictions = None
        self.prediction_scores = None

        self.label_type = "binary"
        self.metrics = metrics

        self.metrics_list = [
            Accuracy(),
            Precision(),
            Recall(),
            F1(),
            BalancedAccuracyScore(),
            TopKAccuracyScore(),
            LogLoss(),
            AveragePrecisionScore(),
            ROC_AUC(),
        ]

        if (
            self.label_type == "binary"
        ):  # To Get results for BrierScoreLoss. As it supports only for binary classification
            self.metrics_list.append(BrierScoreLoss())

        self.metrics_default = {m.name: m for m in self.metrics_list}

        if self.metrics is None:
            self.metrics = self.metrics_default
        else:
            self.metrics = self.parse_metrics()

        self.scores = {}

        # print("metrics classf 1")
        # print(self.metrics)

    def parse_metrics(self):
        metrics_temp = {}

        for metric in self.metrics:
            metric_key = metric["name"]
            if metric_key in self.metrics_default.keys():
                metrics_temp[metric_key] = self.metrics_default[metric_key]
            else:
                print("Metric ", metric_key, "not found")

        # print("metrics_temp", metrics_temp)

        return metrics_temp

    def compute(self):

        # print("metrics classf 2")
        # print(self.metrics)

        self.setup()

        # print(self.metrics)
        for metric_key, metric in self.metrics.items():
            # print(metric_key)
            # print(metric)
            # Adding  prediction scores to kwargs. It will be utilized my metrics needing it(roc_auc).

            try:

                self.kwargs["prediction_scores"] = self.prediction_scores
                score = metric.compute(
                    references=self.references,
                    predictions=self.predictions,
                    kwargs=self.kwargs,
                )
                # **self.kwargs is changed to kwargs=self.kwargs. As **self.kwargs when passed to compute function is having type None.

                self.scores.update(score)
            except Exception as e:
                print("Unable to compute", metric_key)
                print(f"Exception: {e}")

        return self.scores

    def setup(self):
        self.is_multiclass()
        self.setup_kwargs()

    def get_predictions(self):
        pass

    def is_multiclass(self):
        # print(self.predictions)
        # print(self.references)
        if self.predictions is not None:
            self.references = tuple(self.references)
            self.predictions = tuple(self.predictions)
            labels_all = set(self.references).union(self.predictions)
            if len(labels_all) > 2:
                self.label_type = "multilabel"

    def setup_kwargs(self):
        if "average" not in self.kwargs:
            if self.label_type == "multilabel":
                self.kwargs["average"] = "micro"

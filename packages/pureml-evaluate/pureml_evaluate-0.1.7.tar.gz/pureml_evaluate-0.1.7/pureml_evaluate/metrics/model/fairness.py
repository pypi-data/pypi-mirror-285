import typing
from typing import Any

import numpy as np
import pandas as pd
from fairlearn.metrics import (
    demographic_parity_difference,
    demographic_parity_ratio,
    equalized_odds_difference,
    equalized_odds_ratio,
    false_negative_rate,
    false_positive_rate,
    selection_rate,
    true_negative_rate,
    true_positive_rate,
)
from pydantic import BaseModel
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
)

from pureml_evaluate.utils.logger import get_logger

logger = get_logger(name="pureml_evaluate.metrics.fairness_for_policy.py")


class Fairness(BaseModel):
    task_type: Any = "fairness"
    evaluation_type: Any = "fairness"

    references: typing.Any = None
    predictions: typing.Any = None
    sensitive_features: typing.Any = None
    prediction_scores: typing.Any = None
    label_type: str = "binary"

    metrics_to_report: typing.List = [
        "balanced_accuracy",
        "balanced_acc_error",
        "selection_rate",
        "false_positive_rate",
        "false_positive_error",
        "false_negative_rate",
        "false_positive_error" "true_positive_rate",
        "true_negative_rate",
        "demographic_parity_difference",
        "demographic_parity_ratio",
        "equalized_odds_difference",
        "equalized_odds_ratio",
        "equalized_odds",
        "predictive_value_parity",
        "false_positive_parity",
        "true_positive_parity",
        "equal_opportunity",
        "disparate_impact",
    ]
    kwargs: dict = None

    fairness_metrics: dict = {}
    demography_metrics: dict = {}

    def __init__(self, **data):
        super().__init__(**data)
        self.fairness_metrics = {
            # "count": count,
            "balanced_accuracy": balanced_accuracy_score,
            "balanced_acc_error": self.balanced_accuracy_error,
            "selection_rate": selection_rate,
            "false_positive_rate": false_positive_rate,
            "false_positive_error": self.false_positive_error,
            "false_negative_rate": false_negative_rate,
            "false_negative_error": self.false_negative_error,
            "true_positive_rate": true_positive_rate,
            "true_negative_rate": true_negative_rate,
            "predictive_value_parity": self.predictive_value_parity,
            "false_positive_parity": self.false_positive_parity,
            "true_positive_parity": self.true_positive_parity,
        }

        self.demography_metrics = {
            "demographic_parity_difference": demographic_parity_difference,
            "demographic_parity_ratio": demographic_parity_ratio,
            "equalized_odds_difference": equalized_odds_difference,
            "equalized_odds_ratio": equalized_odds_ratio,
            "equal_opportunity": self.equal_opportunity,
            "disparate_impact": self.disparate_impact,
        }

    def setup_kwargs(self):
        try:
            if "average" not in self.kwargs:
                if self.label_type == "multilabel":
                    self.kwargs["average"] = "micro"
        except Exception as e:
            # print(e)
            logger.error(f"Error in setting up kwargs: {e}")

    def compute_error_metric(self, metric_value, sample_size):
        """Compute standard error of a given metric based on the assumption of
        normal distribution.

        Parameters:
        metric_value: Value of the metric
        sample_size: Number of data points associated with the metric

        Returns:
        The standard error of the metric
        """
        metric_value = metric_value / sample_size
        return (
            1.96 * np.sqrt(metric_value * (1.0 - metric_value)) / np.sqrt(sample_size)
        )

    def false_positive_error(self, y_true, y_pred):
        """Compute the standard error for the false positive rate estimate."""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        return self.compute_error_metric(fp, tn + fp)

    def false_negative_error(self, y_true, y_pred):
        """Compute the standard error for the false negative rate estimate."""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        return self.compute_error_metric(fn, fn + tp)

    def balanced_accuracy_error(self, y_true, y_pred, sensitive_features):
        """Compute the standard error for the balanced accuracy estimate."""
        fpr_error, fnr_error = self.false_positive_error(
            y_true, y_pred
        ), self.false_negative_error(y_true, y_pred)
        return np.sqrt(fnr_error**2 + fpr_error**2) / 2

    def equalized_odds(self, y_pred, y_true, sensitive_features):

        if sensitive_features is None:
            conf_mat = confusion_matrix(y_true, y_pred)
            fp = conf_mat[0, 1] / (conf_mat[0, 1] + conf_mat[0, 0])
            fn = conf_mat[1, 0] / (conf_mat[1, 0] + conf_mat[1, 1])
            return abs(fp - fn) < 0.05
        else:
            conf_matrices = {}
            for sens_group in np.unique(sensitive_features):
                mask = sensitive_features == sens_group
                y_pred_group = y_pred[mask]
                y_true_group = y_true[mask]
                conf_matrices[sens_group] = confusion_matrix(y_true_group, y_pred_group)

            # Calculate false positive and false negative rates for each group
            fp_rates = {}
            fn_rates = {}
            for group, conf_mat in conf_matrices.items():
                fp = conf_mat[0, 1] / (conf_mat[0, 1] + conf_mat[0, 0])
                fn = conf_mat[1, 0] / (conf_mat[1, 0] + conf_mat[1, 1])
                fp_rates[group] = fp
                fn_rates[group] = fn

            fp_rates = list(fp_rates.values())
            fn_rates = list(fn_rates.values())

            avg_fp_rate = np.mean(fp_rates)
            avg_fn_rate = np.mean(fn_rates)

            diff = np.abs(avg_fp_rate - avg_fn_rate)

            return diff

    def calculate_group_metric(self, metric_func, y_true, y_pred, sensitive_features):
        group_metrics = {}

        # Convert sensitive_features to a pandas DataFrame if it's a list or a numpy array
        if isinstance(sensitive_features, (list, np.ndarray)):
            if isinstance(sensitive_features, list) and all(
                isinstance(i, dict) for i in sensitive_features
            ):
                # If it's a list of dictionaries, directly create a DataFrame
                sensitive_features = pd.DataFrame(sensitive_features)
            elif (
                isinstance(sensitive_features, np.ndarray)
                and sensitive_features.dtype == object
                and isinstance(sensitive_features[0], dict)
            ):
                # If it's an ndarray of dictionaries, also create a DataFrame
                sensitive_features = pd.DataFrame(list(sensitive_features))
            elif (
                isinstance(sensitive_features, np.ndarray)
                and sensitive_features.ndim == 1
            ):
                # If it's a 1D ndarray, convert it to a DataFrame with a single column
                sensitive_features = pd.DataFrame(
                    sensitive_features, columns=["feature"]
                )
            elif (
                isinstance(sensitive_features, np.ndarray)
                and sensitive_features.ndim == 2
            ):
                # If it's a 2D ndarray, convert it to a DataFrame with multiple columns
                sensitive_features = pd.DataFrame(
                    sensitive_features,
                    columns=[
                        f"feature_{i}" for i in range(sensitive_features.shape[1])
                    ],
                )

        # Handle pandas DataFrame
        if isinstance(sensitive_features, pd.DataFrame):
            unique_combinations = sensitive_features.drop_duplicates()
            for _, combo in unique_combinations.iterrows():
                mask = (sensitive_features == combo).all(axis=1)
                group_metrics[tuple(combo)] = metric_func(y_true[mask], y_pred[mask])
        else:
            raise TypeError(
                "sensitive_features must be a list, a numpy array, or a pandas DataFrame."
            )

        return group_metrics

    def predictive_value_parity(self, y_true, y_pred, sensitive_features):
        """Calculate Predictive Value Parity."""
        precisions = self.calculate_group_metric(
            metric_func=precision_score,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        return precisions

    def false_positive_parity(self, y_true, y_pred, sensitive_features):
        """Calculate False Positive Parity."""
        fpr = lambda y_true, y_pred: false_positive_rate(y_true, y_pred)
        fpr_rates = self.calculate_group_metric(
            metric_func=fpr,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        return fpr_rates

    def true_positive_parity(self, y_true, y_pred, sensitive_features):
        if sensitive_features is None:
            return None  # Handle None case
        group_tpr_rates = self.calculate_group_metric(
            metric_func=recall_score,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        return group_tpr_rates

    def equal_opportunity(self, y_true, y_pred, sensitive_features):
        """Calculate Equal Opportunity for each group."""
        return self.true_positive_parity(y_true, y_pred, sensitive_features)

    def disparate_impact(self, y_pred, sensitive_features, y_true):
        """Calculate Disparate Impact for multiple groups.

        Parameters:
        - y_pred: Predicted values.
        - sensitive_features: Sensitive feature(s) as a numpy.ndarray, pandas.DataFrame, list of dicts, or None.
        - y_true: True values.
        """

        if isinstance(sensitive_features, pd.DataFrame):
            sensitive_features = sensitive_features.apply(
                lambda row: "_".join(row.values.astype(str)), axis=1
            )
        elif isinstance(sensitive_features, list) and all(
            isinstance(i, dict) for i in sensitive_features
        ):
            sensitive_features = pd.Series(
                [
                    "_".join(str(val) for val in item.values())
                    for item in sensitive_features
                ]
            )
        elif isinstance(sensitive_features, np.ndarray):
            sensitive_features = sensitive_features.astype(str)

        selection_rates = {}
        for sens_group in np.unique(sensitive_features):
            mask = sensitive_features == sens_group
            y_pred_group = y_pred[mask]
            selection_rates[sens_group] = np.mean(y_pred_group)

        # Find the group with the highest selection rate
        max_selection_rate = max(selection_rates.values(), default=0)

        # Calculate Disparate Impact for each group compared to the group with the highest rate
        di_results = {}
        for group, rate in selection_rates.items():
            if max_selection_rate > 0:  # Prevent division by zero
                di_results[group] = rate / max_selection_rate
            else:
                di_results[group] = "-1"  # or some other placeholder for no selection

        # Return Disparate Impact results for all groups
        # print(f"Line 296. di_results: {di_results}")
        return di_results

    def setup(self):
        self.setup_kwargs()

    def compute(self):

        self.setup()

        metrics = {}

        for metric_name, metric_func in self.fairness_metrics.items():
            try:
                logger.info(f"Computing {metric_name} metric")
                metrics[metric_name] = {
                    "value": metric_func(
                        y_true=self.references,
                        y_pred=self.predictions,
                        sensitive_features=self.sensitive_features,
                    )
                }
            except Exception:
                sensitive_features = pd.DataFrame(self.sensitive_features)
                metrics[metric_name] = {
                    "value": metric_func(
                        y_true=self.references, y_pred=self.predictions
                    )
                }
                # print("Unable to compute", metric_name)
                # print(e)

        for metric_name, metric_func in self.demography_metrics.items():
            try:
                # print(f"Line 294. sensitive_features: {self.sensitive_features}")
                # print(f"Line 295. type of sensitive_features: {type(self.sensitive_features)}")
                # print(f"Line 296. type of references: {type(self.references)}")
                # print(f"Line 297. type of predictions: {type(self.predictions)}")
                metrics[metric_name] = {
                    "value": metric_func(
                        y_true=self.references,
                        y_pred=self.predictions,
                        sensitive_features=self.sensitive_features,
                    )
                }
                # print(metrics)
                logger.info(f"Computing {metric_name} metric")
            except Exception:
                sensitive_features = pd.DataFrame(self.sensitive_features)
                metrics[metric_name] = {
                    "value": metric_func(
                        y_true=self.references,
                        y_pred=self.predictions,
                        sensitive_features=sensitive_features,
                    )
                }
                # print("Unable to compute", metric_name)
                # print(e)

        return metrics

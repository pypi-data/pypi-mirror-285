import typing

import numpy as np
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
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, precision_score

from pureml_evaluate.schema.metric import ColumnTemplate, MetricDictEnum, MetricTemplate
from pureml_evaluate.utils.utils import get_data_dim


class Fairness:
    def __init__(self, metrics=None):
        self.task_type = "fairness"
        self.evaluation_type = "fairness"

        self.references: typing.Any = None
        self.predictions: typing.Any = None
        self.sensitive_features: typing.Any = None
        self.prediction_scores: typing.Any = None
        self.label_type: str = "binary"

        self.metrics = metrics
        self.fairness_metrics = None
        self.demography_metrics = None

        self.fairness_metrics_default: dict = {
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
        }

        self.demography_metrics_default: dict = {
            "demographic_parity_difference": demographic_parity_difference,
            "demographic_parity_ratio": demographic_parity_ratio,
            "equalized_odds_difference": equalized_odds_difference,
            "equalized_odds_ratio": equalized_odds_ratio,
            "true_positive_parity": self.true_positive_parity,
            "false_positive_parity": self.false_positive_parity,
            "predictive_value_parity": self.predictive_value_parity,
            # "equalized_opportunity": self.equalized_odds_refined
        }
        self.kwargs: dict = None

        if self.metrics is None:
            self.fairness_metrics = self.fairness_metrics_default
            self.demography_metrics = self.demography_metrics_default
        else:
            self.fairness_metrics, self.demography_metrics = self.parse_metrics()

    def parse_metrics(self):
        metrics_temp_fairness = {}
        metrics_temp_demography = {}

        for metric in self.metrics:
            metric_key = metric["name"]
            if metric_key in self.fairness_metrics_default.keys():
                metrics_temp_fairness[metric_key] = self.fairness_metrics_default[
                    metric_key
                ]
            elif metric_key in self.demography_metrics_default.keys():
                metrics_temp_demography[metric_key] = self.demography_metrics_default[
                    metric_key
                ]
            else:
                print("Metric ", metric_key, "not found")

        return metrics_temp_fairness, metrics_temp_demography

    def setup_kwargs(self):
        if "average" not in self.kwargs:
            if self.label_type == "multilabel":
                self.kwargs["average"] = "micro"

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

    def balanced_accuracy_error(self, y_true, y_pred):
        """Compute the standard error for the balanced accuracy estimate."""
        fpr_error, fnr_error = self.false_positive_error(
            y_true, y_pred
        ), self.false_negative_error(y_true, y_pred)
        return np.sqrt(fnr_error**2 + fpr_error**2) / 2

    def true_positive_parity(self, y_pred, y_true, sensitive_features):
        """Calculate True Positive Parity."""
        if sensitive_features is None:
            conf_mat = confusion_matrix(y_true, y_pred)
            tpr = conf_mat[1, 1] / (conf_mat[1, 0] + conf_mat[1, 1])
            return tpr
        else:
            conf_matrices = {}
            for sens_group in np.unique(sensitive_features):
                mask = sensitive_features == sens_group
                y_pred_group = y_pred[mask]
                y_true_group = y_true[mask]
                conf_matrices[sens_group] = confusion_matrix(y_true_group, y_pred_group)

            # Calculate true positive rates for each group
            tpr_rates = {}
            for group, conf_mat in conf_matrices.items():
                tpr = conf_mat[1, 1] / (conf_mat[1, 0] + conf_mat[1, 1])
                tpr_rates[group] = tpr

            # Convert dict_values to lists
            tpr_rates = list(tpr_rates.values())

            return max(tpr_rates) - min(tpr_rates)

    def false_positive_parity(self, y_pred, y_true, sensitive_features):
        """Calculate False Positive Parity."""
        if sensitive_features is None:
            conf_mat = confusion_matrix(y_true, y_pred)
            fpr = conf_mat[0, 1] / (conf_mat[0, 1] + conf_mat[0, 0])
            return fpr
        else:
            conf_matrices = {}
            for sens_group in np.unique(sensitive_features):
                mask = sensitive_features == sens_group
                y_pred_group = y_pred[mask]
                y_true_group = y_true[mask]
                conf_matrices[sens_group] = confusion_matrix(y_true_group, y_pred_group)

            # Calculate false positive rates for each group
            fpr_rates = {}
            for group, conf_mat in conf_matrices.items():
                fpr = conf_mat[0, 1] / (conf_mat[0, 1] + conf_mat[0, 0])
                fpr_rates[group] = fpr

            # Convert dict_values to lists
            fpr_rates = list(fpr_rates.values())

            return max(fpr_rates) - min(fpr_rates)

    def predictive_value_parity(self, y_pred, y_true, sensitive_features):
        """Calculate Predictive Value Parity."""
        if sensitive_features is None:
            precision = precision_score(y_true, y_pred)
            return precision
        else:
            precisions = {}
            for sens_group in np.unique(sensitive_features):
                mask = sensitive_features == sens_group
                y_pred_group = y_pred[mask]
                y_true_group = y_true[mask]
                precisions[sens_group] = precision_score(y_true_group, y_pred_group)

            # Convert dict_values to lists
            precisions = list(precisions.values())
            return max(precisions) - min(precisions)

    def equalized_odds_refined(self, y_pred, y_true, sensitive_features):
        """Calculate Equalized Odds."""
        tpp = self.true_positive_parity(y_pred, y_true, sensitive_features)
        fpp = self.false_positive_parity(y_pred, y_true, sensitive_features)

        return {"tpp_diff": tpp, "fpp_diff": fpp}

    def setup(self):
        self.setup_kwargs()

    def compute(self):

        self.setup()

        # metrics = {}

        s_feat_dim, s_feat_df, column_names = get_data_dim(data=self.sensitive_features)

        # print(s_feat_dim, s_feat_df.shape, column_names)

        metric_dict_list_all = []

        if s_feat_dim > 1:
            for column_name in column_names:

                # s_feat = s_feat_df.get([column_name])
                s_feat = s_feat_df[column_name]

                metric_dict_list = self.compute_metrics_column(
                    s_feat=s_feat, column_name=column_name
                )

                # print("metric_dict_list")
                # print(metric_dict_list)

                metric_dict_list_all += metric_dict_list
        else:
            metric_dict_list = self.compute_metrics_column(
                s_feat=s_feat_df, column_name=column_names
            )

            metric_dict_list_all += metric_dict_list

        return metric_dict_list_all

    def compute_metrics_column(self, s_feat, column_name):
        metric_dict_list = []

        columns_sensitive = [
            ColumnTemplate(name=column_name, value=MetricDictEnum.all.value)
        ]

        if s_feat.nunique() == 1:
            columns_sensitive = [
                ColumnTemplate(name=column_name, value=s_feat.unique()[0])
            ]

        for metric_name, metric_func in self.fairness_metrics.items():
            # print(metric_name)
            try:
                values = metric_func(y_true=self.references, y_pred=self.predictions)

                # print(values)

                metric_dict = MetricTemplate(
                    name=metric_name,
                    category=self.evaluation_type,
                    value=values,
                    status=None,
                    columns_sensitive=columns_sensitive,
                )

                metric_dict_list.append(metric_dict)

            except Exception as e:
                print("Unable to compute", metric_name)
                print(e)

        for metric_name, metric_func in self.demography_metrics.items():
            try:
                # print(metric_name)

                values = metric_func(
                    y_true=self.references,
                    y_pred=self.predictions,
                    sensitive_features=s_feat.to_numpy(),
                )

                # print(values)

                metric_dict = MetricTemplate(
                    name=metric_name,
                    category=self.evaluation_type,
                    value=values,
                    status=None,
                    columns_sensitive=columns_sensitive,
                )

                metric_dict_list.append(metric_dict)

            except Exception as e:
                print(
                    "Unable to compute",
                    metric_name,
                    "for sensitive column",
                    column_name,
                )
                print(e)

        return metric_dict_list

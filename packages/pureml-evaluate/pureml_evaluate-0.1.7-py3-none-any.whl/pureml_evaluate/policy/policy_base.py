from collections import defaultdict
from typing import Any, List

from pydantic import BaseModel

from pureml_evaluate.metrics.model.fairness import Fairness
from pureml_evaluate.policy.metrics_import import metrics_to_class_name
from pureml_evaluate.utils.logger import get_logger

logger = get_logger(name="pureml_evaluate.policy.policy_base.py")


class PolicyBase(BaseModel):
    list_metrics: List[str] = []
    list_metrics_kwargs: List[dict] = None
    list_of_thresholds: dict = {}
    scores: dict = defaultdict(dict)  # Use defaultdict for nested dictionaries
    all_metrics_results: Any = []
    kwargs: Any = {}

    def compute(
        self,
        references=None,
        predictions=None,
        prediction_scores=None,
        sensitive_features=None,
        productions=None,
        list_metrics=None,
        type=None,
        list_of_thresholds=None,
        **kwargs,
    ):

        try:
            list_metrics_objects = [
                metrics_to_class_name[metric_name] for metric_name in list_metrics
            ]
        except Exception as e:
            # print(e)
            logger.error(f"Error in getting the metrics objects: {e}")

        if type == "performance" and references is not None and predictions is not None:
            for m in list_metrics_objects:
                try:
                    logger.info(f"Computing {m} from performance metrics")
                    result = m.compute(
                        references, predictions, prediction_scores, **kwargs
                    )
                    format_result = {
                        "category": "performance",
                        "risk": list(result.keys())[0],
                        "value": list(result.values())[0],
                    }
                    self.all_metrics_results.append(format_result)
                except Exception as e:
                    # print(e)
                    logger.error(
                        f"Error in computing {m} from performance metrics: {e}"
                    )

        if type == "drift" and references is not None and productions is not None:
            for m in list_metrics_objects:
                try:
                    logger.info(f"Computing {m} from drift metrics")
                    result = m.compute(references, productions, **kwargs)
                    format_result = {
                        "category": "drift",
                        "risk": list(result.keys())[0],
                        "value": list(result.values())[0],
                    }
                    self.all_metrics_results.append(format_result)
                except Exception as e:
                    # print(e)
                    logger.error(f"Error in computing {m} from drift metrics: {e}")

        if type == "fairness":
            fairness_evaluator = Fairness(
                references=references,
                predictions=predictions,
                sensitive_features=sensitive_features,
                prediction_scores=prediction_scores,
                **kwargs,
            )
            fairness_evaluator.fairness_metrics = {
                k: v
                for k, v in fairness_evaluator.fairness_metrics.items()
                if k in list_metrics
            }
            fairness_evaluator.demography_metrics = {
                k: v
                for k, v in fairness_evaluator.demography_metrics.items()
                if k in list_metrics
            }
            result = fairness_evaluator.compute()
            all_metric_names = list(result.keys())
            format_result = {"fairness": {}}
            for metric_name in all_metric_names:
                format_result["fairness"][metric_name] = result[metric_name]["value"]

            self.all_metrics_results.append(format_result)

        if kwargs.get("subset_name", "None") != "None":
            self.all_metrics_results = disparate_filter_metrics_result(
                self.all_metrics_results, keys_to_keep=kwargs.get("subset_name", "None")
            )

        for result in self.all_metrics_results:
            if "fairness" not in result.keys():
                category = result["category"]
                metric = result["risk"]
                self.scores[category][metric] = result["value"]
            else:
                self.scores = self.all_metrics_results[0]

        risk_analysis = evaluate_metrics_against_thresholds(
            scores=self.scores, thresholds=list_of_thresholds
        )

        return risk_analysis


def evaluate_metrics_against_thresholds(scores, thresholds):
    evaluation_results = []
    for category, metrics in scores.items():
        for metric_name, metric_info in metrics.items():
            if isinstance(metric_info, dict) and "value" in metric_info:
                value = metric_info["value"]
            else:
                value = metric_info

            metric_name = metric_name.lower()
            try:
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        evaluation_results.append(
                            {
                                "category": category,
                                "risk": f"{metric_name}",
                                "value": sub_value,
                            }
                        )
                else:
                    evaluation_result = {
                        "category": category,
                        "risk": metric_name,
                        "value": value,
                    }
                    evaluation_results.append(evaluation_result)

            except Exception:
                # print(e)
                evaluation_results.append(
                    {
                        "category": category,
                        "risk": metric_name,
                        "value": value,
                    }
                )
    try:
        return evaluation_results[0]
    except Exception:
        return evaluation_results


def disparate_filter_metrics_result(metrics_result, keys_to_keep):
    """
    Filters the metrics_result to keep only specified keys under 'disparate_impact' within 'fairness'.

    :param metrics_result: List of dictionaries containing the metrics.
    :param keys_to_keep: List of keys to keep in the 'disparate_impact' dictionary.
    :return: A filtered version of metrics_result.
    """
    filtering_occured = False

    filtered_metrics_result = []

    if isinstance(keys_to_keep, list):
        keys_to_keep = [str(key) for key in keys_to_keep]
    elif isinstance(keys_to_keep, str):
        keys_to_keep = keys_to_keep

    for item in metrics_result:
        for category, metrics in item.items():
            if category == "fairness" and "disparate_impact" in metrics:
                for metric_name, metric_values in metrics.items():
                    if metric_name == "disparate_impact":
                        filtered_metric_values = {
                            k: v for k, v in metric_values.items() if k in keys_to_keep
                        }
                        if filtered_metric_values:
                            new_item = {category: {metric_name: filtered_metric_values}}
                            filtered_metrics_result.append(new_item)
                            filtering_occured = True
    if not filtering_occured:
        return metrics_result

    return filtered_metrics_result

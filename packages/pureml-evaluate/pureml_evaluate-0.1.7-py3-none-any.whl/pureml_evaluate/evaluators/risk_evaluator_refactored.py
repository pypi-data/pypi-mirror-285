import json

import pkg_resources

path_to_desc = pkg_resources.resource_filename(__name__, "description.json")

with open(f"{path_to_desc}", "r") as description_file:
    description_file = json.load(description_file)


categories = ["performance", "fairness"]
fairness_metrics = [
    "true_positive_parity",
    "false_positive_parity",
    "predictive_value_parity",
    "equal_opportunity",
]


class RiskEvaluator:

    # To Initialize the value_all and values_subset_all and threshold
    def __init__(self, values_all=None, values_subset_all=None, path_to_config=None):
        self.values_all = values_all
        self.values_subset_all = values_subset_all
        self.path_to_config = path_to_config

    # To compute the Status Based on Threshold. Output is either high, low, medium or no risk

    def update_metric_info(
        self,
        category,
        metric_name,
        original_value,
        threshold_precent,
        description,
        matters,
    ):
        if metric_name in fairness_metrics:
            severity = get_severity_fairness(
                original_value=original_value, threshold_precent=threshold_precent
            )
            summary = f"{metric_name} has a value of {round(original_value,2)} with {severity} as Fairness  against the {threshold_precent} as threshold"
        else:
            severity = get_severity(
                original_value=original_value, threshold_precent=threshold_precent
            )
            summary = f"{metric_name} has a value of {round(original_value,2)} with {severity} as Severity Index against the {threshold_precent} as threshold"
        info_dict = {
            "severity": severity,
            "threshold": threshold_precent,
            "summary": summary,
            "description": description,
            "matters": matters,
        }
        return info_dict

    def compute_status(self):

        for i in range(len(categories)):
            category = categories[i]
            if categories[i] in self.values_all and self.values_subset_all != None:
                category_keys = self.values_all[categories[i]]
                keys_in_subset = list(self.values_subset_all.keys())

                with open(f"{self.path_to_config}", "r") as config_file:
                    config_file = json.load(config_file)

                for metric_name, metric_values in category_keys.items():
                    data_from_values_all = metric_values["value"]

                    threshold_precent = get_threshold_percentage(
                        config_file=config_file,
                        category=categories[i],
                        metric_name=metric_name,
                    )

                    description, matters = get_description_matters(
                        category=categories[i],
                        metric_name=metric_name,
                        description_file=description_file,
                    )

                    self.values_all[category][metric_name].update(
                        self.update_metric_info(
                            category,
                            metric_name,
                            data_from_values_all,
                            threshold_precent,
                            description,
                            matters,
                        )
                    )

                    for subset_key in keys_in_subset:
                        data_from_subset = self.values_subset_all[subset_key][
                            categories[i]
                        ][metric_name]["value"]

                        self.values_subset_all[subset_key][category][
                            metric_name
                        ].update(
                            self.update_metric_info(
                                category,
                                metric_name,
                                data_from_subset,
                                threshold_precent,
                                description,
                                matters,
                            )
                        )

            elif categories[i] in self.values_all:
                category_keys = self.values_all[categories[i]]

                with open(f"{self.path_to_config}", "r") as config_file:
                    config_file = json.load(config_file)

                for metric_name, metric_values in category_keys.items():
                    data_from_values_all = metric_values["value"]

                    threshold_precent = get_threshold_percentage(
                        config_file=config_file,
                        category=categories[i],
                        metric_name=metric_name,
                    )

                    description, matters = get_description_matters(
                        category=categories[i],
                        metric_name=metric_name,
                        description_file=description_file,
                    )
                    self.values_all[category][metric_name].update(
                        self.update_metric_info(
                            category,
                            metric_name,
                            data_from_values_all,
                            threshold_precent,
                            description,
                            matters,
                        )
                    )


def risk_calculate(threshold_precent, threshold):
    if threshold_precent <= threshold / 2:
        return "High"
    elif threshold_precent <= threshold:
        return "Moderate"
    elif threshold_precent <= threshold + 0.4:
        return "No Risk"
    else:
        return "Low"


def get_severity(original_value, threshold_precent):
    # return 'pass' if original_value >= threshold_precent and original_value <= threshold_precent*1.5 else 'fail'
    if (
        original_value >= threshold_precent
        and original_value <= threshold_precent * 1.5
    ):
        return "pass"
    # elif original_value <= threshold_precent/2:
    #    return  "high"
    # elif threshold_precent/2 < original_value < threshold_precent:
    #    return   "moderate"
    else:
        return "fail"
    # Say Threshold is 80 then 80 to 120 is pass and others as fail


def get_severity_fairness(
    original_value, threshold_precent
):  # For Fairness Metrics Defined Above.
    return "pass" if original_value <= threshold_precent else "high"


def get_threshold_percentage(config_file, category, metric_name):
    try:
        threshold_precent = config_file[category][metric_name]["threshold"]
    except KeyError as e:
        print(f"KeyError: {e} is not present in config.json")
        print(f"Add {metric_name} under fairness in config.json")
        print("Set the threshold to default = 0.7")
        threshold_precent = 0.7
    except Exception as e:
        print(f"Exception: {e} occured while reading config.json")
        print("Set the threshold to default = 0.7")
        threshold_precent = 0.7
    return threshold_precent


def get_description_matters(category, metric_name, description_file):
    if category in description_file and metric_name in description_file[category]:
        try:
            description = description_file[categories[i]][metric_name]["description"]
            matters = description_file[categories[i]][metric_name]["why it matters"]
        except Exception:
            description = " "
            matters = " "
    else:
        description = "No description available"
        matters = " "
    return description, matters

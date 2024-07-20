import json

import pkg_resources

path_to_desc = pkg_resources.resource_filename(__name__, "description.json")

with open(f"{path_to_desc}", "r") as description_file:
    description_file = json.load(description_file)


class RiskEvaluator:

    # To Initialize the value_all and values_subset_all and threshold
    def __init__(self, values_all=None, values_subset_all=None, path_to_config=None):
        self.values_all = values_all
        self.values_subset_all = values_subset_all
        self.path_to_config = path_to_config

    # To compute the Status Based on Threshold. Output is either high, low, medium or no risk

    def compute_status(self):
        if "fairness" in self.values_all and self.values_subset_all != None:
            fairness_keys = self.values_all["fairness"]
            keys_in_subset = list(self.values_subset_all.keys())

            with open(f"{self.path_to_config}", "r") as config_file:
                config_file = json.load(config_file)

            for metric_name, metric_values in fairness_keys.items():
                data_from_values_all = metric_values["value"]

                try:
                    threshold_precent = config_file["fairness"][metric_name][
                        "threshold"
                    ]
                except KeyError as e:
                    print(f"KeyError: {e} is not present in config.json")
                    print(f"Add {metric_name} under fairness in config.json")
                    print("Set the threshold to default = 0.7")
                    threshold_precent = 0.7
                except Exception as e:
                    print(f"Exception: {e} occured while reading config.json")
                    print("Set the threshold to default = 0.7")
                    threshold_precent = 0.7

                if (
                    "fairness" in description_file
                    and metric_name in description_file["fairness"]
                ):
                    try:
                        description = description_file["fairness"][metric_name][
                            "description"
                        ]
                        matters = description_file["fairness"][metric_name][
                            "why it matters"
                        ]
                    except Exception:
                        description = " "
                        matters = " "
                else:
                    description = "No description available"
                    matters = " "

                severity = get_severity(
                    original_value=data_from_values_all,
                    threshold_precent=threshold_precent,
                )
                self.values_all["fairness"][metric_name]["severity"] = severity
                self.values_all["fairness"][metric_name][
                    "threshold"
                ] = threshold_precent
                summary = f"{metric_name} has a value of {round(data_from_values_all,2)} with {severity} as Severity Index against the {threshold_precent} as threshold"
                self.values_all["fairness"][metric_name]["summary"] = summary
                self.values_all["fairness"][metric_name]["description"] = description
                self.values_all["fairness"][metric_name]["matters"] = matters

                for subset_key in keys_in_subset:
                    data_from_subset = self.values_subset_all[subset_key]["fairness"][
                        metric_name
                    ]["value"]

                    severity = get_severity(
                        original_value=data_from_subset,
                        threshold_precent=threshold_precent,
                    )
                    self.values_subset_all[subset_key]["fairness"][metric_name][
                        "severity"
                    ] = severity
                    self.values_all["fairness"][metric_name][
                        "threshold"
                    ] = threshold_precent
                    summary = f"{metric_name} has a value of {round(data_from_values_all,2)} with {severity} as Severity Index against the {threshold_precent} as threshold"
                    self.values_all["fairness"][metric_name]["summary"] = summary
                    self.values_all["fairness"][metric_name][
                        "description"
                    ] = description
                    self.values_all["fairness"][metric_name]["matters"] = matters

        elif "fairness" in self.values_all:
            fairness_keys = self.values_all["fairness"]

            with open(f"{self.path_to_config}", "r") as config_file:
                config_file = json.load(config_file)

            for metric_name, metric_values in fairness_keys.items():
                data_from_values_all = metric_values["value"]

                try:
                    threshold_precent = config_file["fairness"][metric_name][
                        "threshold"
                    ]
                except KeyError as e:
                    print(f"KeyError: {e} is not present in config.json")
                    print(f"Add {metric_name} under fairness in config.json")
                    print("Set the threshold to default = 0.7")
                    threshold_precent = 0.7
                except Exception as e:
                    print(f"Exception: {e} occured while reading config.json")
                    print("Set the threshold to default = 0.7")
                    threshold_precent = 0.7

                if (
                    "fairness" in description_file
                    and metric_name in description_file["fairness"]
                ):
                    try:
                        description = description_file["fairness"][metric_name][
                            "description"
                        ]
                        matters = description_file["fairness"][metric_name][
                            "why it matters"
                        ]
                    except Exception:
                        description = " "
                        matters = " "
                else:
                    description = "No description available"
                    matters = " "

                severity = get_severity(
                    original_value=data_from_values_all,
                    threshold_precent=threshold_precent,
                )
                self.values_all["fairness"][metric_name]["severity"] = severity
                self.values_all["fairness"][metric_name][
                    "threshold"
                ] = threshold_precent
                summary = f"{metric_name} has a value of {round(data_from_values_all,2)} with {severity} as Severity Index against the {threshold_precent} as threshold"
                self.values_all["fairness"][metric_name]["summary"] = summary
                self.values_all["fairness"][metric_name]["description"] = description
                self.values_all["fairness"][metric_name]["matters"] = matters

        compute_performance_analysis(
            self.values_all, self.values_subset_all, self.path_to_config
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
        return "high"
        # elif threshold_precent/2 < original_value < threshold_precent:
        return "moderate"
    else:
        return "fail"

    # Say Threshold is 80 then 80 to 120 is pass and others as fail


def compute_performance_analysis(values_all, values_subset_all, path_to_config):
    if "performance" in values_all and values_subset_all != None:
        performance_keys = values_all["performance"]
        keys_in_subset = list(values_subset_all.keys())

        for metric_name, metric_values in performance_keys.items():

            if metric_name == "confusion_matrix":
                continue

            with open(f"{path_to_config}", "r") as config_file:
                config_file = json.load(config_file)

            data_from_values_all = metric_values["value"]
            try:
                threshold_precent = config_file["performance"][metric_name]["threshold"]
            except KeyError as e:
                print(f"KeyError: {e} is not present in config.json")
                print(f"Add {metric_name} under performance in config.json")
                print("Set the threshold to default = 0.7")
                threshold_precent = 0.7
            except Exception as e:
                print(f"Exception: {e} occured while reading config.json")
                print("Set the threshold to default = 0.7")
                threshold_precent = 0.7

            if (
                "performance" in description_file
                and metric_name in description_file["performance"]
            ):
                try:
                    description = description_file["performance"][metric_name][
                        "description"
                    ]
                    matters = description_file["performance"][metric_name][
                        "why it matters"
                    ]
                except Exception:
                    description = " "
                    matters = " "
            else:
                description = "No description available"
                matters = " "

            severity = get_severity(
                original_value=data_from_values_all, threshold_precent=threshold_precent
            )
            values_all["performance"][metric_name]["severity"] = severity
            values_all["performance"][metric_name]["threshold"] = threshold_precent
            summary = f"{metric_name} has a value of {round(data_from_values_all,2)} with {severity} as Severity Index against the {threshold_precent} as threshold "
            values_all["performance"][metric_name]["summary"] = summary

            for subset_key in keys_in_subset:
                data_from_subset = values_subset_all[subset_key]["performance"][
                    metric_name
                ]["value"]

                severity = get_severity(
                    original_value=data_from_subset, threshold_precent=threshold_precent
                )
                values_subset_all[subset_key]["performance"][metric_name][
                    "severity"
                ] = severity
                values_all["performance"][metric_name]["threshold"] = threshold_precent
                summary = f"{metric_name} has a value of {round(data_from_values_all,2)} with {severity} as Severity Index against the {threshold_precent} as threshold "
                values_all["performance"][metric_name]["summary"] = summary
                values_all["performance"][metric_name]["description"] = description
                values_all["performance"][metric_name]["matters"] = matters

    elif "performance" in values_all:
        performance_keys = values_all["performance"]

        for metric_name, metric_values in performance_keys.items():

            if metric_name == "confusion_matrix":
                continue

            with open(f"{path_to_config}", "r") as config_file:
                config_file = json.load(config_file)

            data_from_values_all = metric_values["value"]
            try:
                threshold_precent = config_file["performance"][metric_name]["threshold"]
            except KeyError as e:
                print(f"KeyError: {e} is not present in config.json")
                print(f"Add {metric_name} under performance in config.json")
                print("Set the threshold to default = 0.7")
                threshold_precent = 0.7
            except Exception as e:
                print(f"Exception: {e} occured while reading config.json")
                print("Set the threshold to default = 0.7")
                threshold_precent = 0.7

            if (
                "performance" in description_file
                and metric_name in description_file["performance"]
            ):
                try:
                    description = description_file["performance"][metric_name][
                        "description"
                    ]
                    matters = description_file["performance"][metric_name][
                        "why it matters"
                    ]
                except Exception:
                    description = " "
                    matters = " "
            else:
                description = "No description available"
                matters = " "

            severity = get_severity(
                original_value=data_from_values_all, threshold_precent=threshold_precent
            )
            values_all["performance"][metric_name]["severity"] = severity
            values_all["performance"][metric_name]["threshold"] = threshold_precent
            summary = f"{metric_name} has a value of {round(data_from_values_all,2)} with {severity} as Severity Index against the {threshold_precent} as threshold "
            values_all["performance"][metric_name]["summary"] = summary
            values_all["performance"][metric_name]["description"] = description
            values_all["performance"][metric_name]["matters"] = matters

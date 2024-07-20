import json
import os
import sys
from collections import defaultdict
from importlib import import_module
from typing import Any, Union
import re
import numpy as np
import pandas as pd
import pureml
from pureml.components import dataset, model
from pureml.predictor.predictor import BasePredictor
from pureml.utils.logger import get_logger
from pydantic import BaseModel, ConfigDict
from rich import print
from pathlib import Path

from pureml_evaluate.policy.assignments import post_eval_json
from pureml_evaluate.policy.grade import Grader
from pureml_evaluate.policy.result_formation import format_response
from pureml_evaluate.policy.schema import framework_list
from pureml.cli.puremlconfig import PureMLConfigYML

logger = get_logger("pureml_evaluate.policy.policy_eval.py")

project_path = Path.cwd()
if Path.exists(project_path / "puremlconfig.yaml"):
    puremlconfig = PureMLConfigYML(project_path / "puremlconfig.yaml")
else:
    puremlconfig = None

class EvalHelper(BaseModel):  # To pass the requirements to eval in pureml_evaluate
    label_model: str
    label_dataset: str
    framework: dict = None
    predictor: BasePredictor = None
    predictor_path: str = "predict.py"
    dataset: Any = None
    sensitive_features: Union[None, Any] = None
    y_true: Any = None
    y_pred: Any = None
    y_pred_scores: Any = None
    framework_name: Any = None
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)
    metrics_list: Any = None
    framework_data: Any = None

    def load_dataset(self):
        self.dataset = dataset.fetch(self.label_dataset)
        if self.dataset:
            logger.info(f"Dataset Fetched Successfully: {self.label_dataset}")
            print(f"[bold green] Succesfully fetched the Dataset: {self.label_dataset}")
        else:
            print(f"[bold red] Dataset not fetched: {self.label_dataset}")
            raise Exception("Dataset fetching failed")

    def load_predictor(
        self
    ):  
        if puremlconfig is None:
            return 
        storage_configuration  = puremlconfig.data["repository"].split("://")[0]
        
        if storage_configuration != "file":
            self.predictor_path = str(pureml.predict.fetch(self.label_model))
            current_dir = os.getcwd()
            current_dir = str(current_dir)

            if self.predictor_path.startswith(current_dir):
                rel_path = self.predictor_path[len(current_dir) :].lstrip(os.sep)
                rel_path = str(rel_path)
                abs_path = os.path.join(current_dir, rel_path)

            if os.path.exists(abs_path):
                module_dir = os.path.dirname(
                    abs_path
                )  # Get the directory containing the module file

                module_name = os.path.splitext(os.path.basename(abs_path))[
                    0
                ]  # Extract module name without extension
                sys.path.insert(0, module_dir)
                module_import = import_module(module_name)

                predictor_class = getattr(module_import, "Predictor")

                self.predictor = predictor_class()
        else:
                self.predictor_path: str = "predict.py"
                module_path = self.predictor_path.replace(".py", "")
                module_import = import_module(module_path)

                predictor_class = getattr(module_import, "Predictor")

                self.predictor = predictor_class()
        logger.info(f"Predictor path: {self.predictor_path}")

        logger.info(f"Predict files fetched successfully: {self.predictor}")
        print(f"[bold green] Succesfully fetched the Predictor")

    def load_model(self):
        model_fetching = model.fetch(self.label_model)
        if model_fetching:
            self.predictor.label = self.label_model
            self.predictor.load_models()
            print(f"predictor models: {self.predictor.load_models()}")
            logger.info(f"Model Fetched Successfully: {self.label_model}")
            print(f"[bold green] Succesfully fetched the Model: {self.label_model}")
        else:
            print(f"[bold red] Model not fetched: {self.label_model}")
            raise Exception("Model fetching failed")

    def load_framework(self):
        self.framework = framework_list["custom_policy_to_run_all_metrics"]
        self.framework_data = list(self.framework.keys())
        print("[bold green] Succesfully fetched the Metrics ")
        logger.info(f"Metrics Fetched Successfully: {self.framework_data}")
        return list(self.framework.keys())

    def load_sensitive_features(self):
        if "sensitive_features" in self.dataset.keys():
            self.sensitive_features = self.dataset["sensitive_features"]
            return self.dataset["sensitive_features"]
        else:
            return None

    def load_y_true(self):
        self.y_true = self.dataset["y_test"]
        logger.info(f"Y_true Fetched Successfully: {self.dataset['y_test']}")
        return self.dataset["y_test"]

    def load_y_pred(self):
        self.y_pred = self.predictor.predict(self.dataset["x_test"])
        logger.info(
            f"Y_pred Fetched Successfully: {self.predictor.predict(self.dataset['x_test'])}"
        )
        return self.predictor.predict(self.dataset["x_test"])

    def load(self):
        self.load_dataset()
        self.load_predictor()
        self.load_model()
        self.load_framework()
        self.load_sensitive_features()
        self.load_y_true()
        self.load_y_pred()

    def get_y_pred(self):
        return self.predictor.predict(self.dataset["x_test"])

    def get_y_true(self):
        return self.dataset["y_test"]

    def get_sensitive_features(self):
        if "sensitive_features" in self.dataset.keys():
            return self.dataset["sensitive_features"]
        else:
            return None

    def evaluate(self):
        y_pred = self.get_y_pred()
        y_true = self.get_y_true()
        sensitive_features = self.get_sensitive_features()
        policies = self.framework_data
        grader = Grader(
            references=y_true,
            predictions=y_pred,
            sensitive_features=sensitive_features,
            framework=self.framework,
            metrics=policies,
        )

        return grader.compute()

    def evaluate_subsets(self):
        if self.sensitive_features is None:  # If No Sensitive Features are given
            return

        if self.sensitive_features is not None:
            subsets = self.give_subsets()

            values_subsets_all = {}

            for subset in subsets:
                defaultdict(dict)

                key = subset["key"]
                y_true = subset["y_true"]
                y_pred = subset["y_pred"]
                sensitive_features = subset["sensitive_features"]
                subset["y_pred_scores"]

                try:
                    key_tuple = tuple((k, v) for k, v in key.items())
                    keys = {k: v for k, v in key.items()}
                except:
                    key_tuple = key
                    keys = {"index": str(int(key))}

                key_tuple = str(key_tuple)
                if key_tuple not in values_subsets_all:
                    values_subsets_all[key_tuple] = {"columns": keys}

                policies = self.framework_data
                if "disparate_impact" in policies:
                    policies.remove("disparate_impact")
                    new_policies = ["disparate_impact"]
                    subset_name = get_unique_sensitive_for_disparate_impact(
                        sensitive_features
                    )
                    sensitive_features_1 = self.get_sensitive_features()
                    y_pred = self.get_y_pred()
                    y_true = self.get_y_true()
                    grader_disparate = Grader(
                        references=y_true,
                        predictions=y_pred,
                        sensitive_features=sensitive_features_1,
                        framework=self.framework,
                        metrics=new_policies,
                        subset_name=str(subset_name),
                    )
                    result_disparate = grader_disparate.compute()

                if policies:
                    y_true = subset["y_true"]
                    y_pred = subset["y_pred"]
                    subset["y_pred_scores"]

                    grader = Grader(
                        references=y_true,
                        predictions=y_pred,
                        sensitive_features=sensitive_features,
                        framework=self.framework,
                        metrics=policies,
                    )
                    result = grader.compute()
                try:
                    result = merge_results(result, result_disparate)
                    values_subsets_all[key_tuple].update(result)
                except Exception:
                    # print(e)
                    values_subsets_all[key_tuple].update(result)

            return values_subsets_all

    def give_subsets(self):
        subsets = []
        if isinstance(self.sensitive_features, np.ndarray):
            # Check if it is one-dimensional or two-dimensional
            if self.sensitive_features.ndim == 1:
                # Handle the one-dimensional case
                unique_values = np.unique(self.sensitive_features)
                for value in unique_values:
                    ind = np.where(self.sensitive_features == value)[0]
                    if ind.size > 0:
                        sub_dict = self.create_sub_dict(ind, value)
                        subsets.append(sub_dict)
            elif self.sensitive_features.ndim == 2:
                # Handle the two-dimensional case
                unique_combinations = np.unique(self.sensitive_features, axis=0)
                for combo in unique_combinations:
                    mask = np.all(self.sensitive_features == combo, axis=1)
                    ind = np.where(mask)[0]
                    if ind.size > 0:
                        sub_dict = self.create_sub_dict(ind, combo)
                        subsets.append(sub_dict)
            else:
                raise ValueError(
                    "sensitive_features array must be either one or two-dimensional."
                )
        # Check if sensitive_features is a pandas DataFrame
        elif isinstance(self.sensitive_features, pd.DataFrame):
            # Handle the DataFrame case
            unique_combinations = self.sensitive_features.drop_duplicates()
            for _, combo in unique_combinations.iterrows():
                mask = (self.sensitive_features == combo).all(axis=1)
                ind = self.sensitive_features.index[mask].tolist()
                if ind:
                    sub_dict = self.create_sub_dict(ind, combo.to_dict())
                    subsets.append(sub_dict)
        else:
            raise TypeError(
                "sensitive_features must be either a numpy array or a pandas DataFrame."
            )
        return subsets

    def create_sub_dict(self, ind, key):
        sub_dict = {
            "key": key,
            "y_true": self.y_true[ind],
            "y_pred": self.y_pred[ind],
            "sensitive_features": (
                self.sensitive_features[ind]
                if isinstance(self.sensitive_features, np.ndarray)
                else self.sensitive_features.loc[ind].to_dict("records")
            ),
        }
        if self.y_pred_scores is not None:
            sub_dict["y_pred_scores"] = self.y_pred_scores[ind]
        else:
            sub_dict["y_pred_scores"] = self.y_pred_scores
        return sub_dict


def eval(label_model: str, label_dataset: str, framework_name=None):
    evaluator = EvalHelper(
        label_model=label_model,
        label_dataset=label_dataset,
        framework_name=framework_name,
    )

    try:
        evaluator.load()
        complete = evaluator.evaluate()
        subsets = evaluator.evaluate_subsets()
        evaluation_result = {"complete": complete, "subsets": subsets}
        subsets_formatted = format_response(evaluation_result)

        result = {
            "model": f"{label_model}",
            "dataset": f"{label_dataset}",
            "data": {
                "sensitive_columns": list(
                    extract_sensitive_column_names(subsets_formatted)
                ),
                "complete": evaluation_result["complete"],
                "subsets": subsets_formatted,
            },
        }

        result = json.dumps(result)

        logger.info(f"JSON Result: {result}")
        #print(f"JSON Result: {result}")

        status = post_eval_json(data=result, label_model=label_model)
        if status:
            print(
                "[bold green] Evaluation Completed Successfully & Data sent to Backend"
            )
        else:
            print("[bold red] Evaluation Failed & Data not sent to Backend")
        return result
    except Exception as e:
        logger.error(f"Error in Evaluation: {e}")
        print(f"[bold red] Error while evaluating. {e}")


def extract_sensitive_column_names(data):
    sensitive_column_names = set()
    for i in range(len(data)):
        try:
            columns = data[i]["columns"]
            for key in columns.keys():
                if key == "index":
                    sensitive_column_names.add(columns["index"])
                else:
                    sensitive_column_names.add(key)
        except Exception:
            # print(e)
            pass
    return sensitive_column_names


def get_unique_sensitive_for_disparate_impact(
    sensitive_features,
):  # To get unique values for disparate impact
    if isinstance(sensitive_features, np.ndarray):
        return np.unique(sensitive_features)

    elif isinstance(sensitive_features, list) and all(
        isinstance(i, dict) for i in sensitive_features
    ):
        concatenated_values = [
            "_".join(str(value) for value in item.values())
            for item in sensitive_features
        ]
        return list(set(concatenated_values))

    else:
        raise ValueError(
            "sensitive_features must be a numpy.ndarray or a list of dictionaries."
        )


def merge_results(dict1, dict2):
    """Merge dict2 into dict1 at the level of specified keys."""
    if "fairness_scores" in dict2:
        scores = dict2["fairness_scores"]

    dict1["fairness_scores"]["disparate_impact"] = scores["disparate_impact"]

    return dict1

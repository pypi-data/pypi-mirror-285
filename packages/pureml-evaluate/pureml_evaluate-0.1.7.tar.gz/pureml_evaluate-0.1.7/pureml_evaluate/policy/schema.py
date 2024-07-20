from typing import Dict

# framework_list = {
#     'nyc144': {
#         'sensitive_columns': ['sex', 'race'],
#         'task_type': ['classification', 'fairness'],
#         'policies': {
#                 'classification':
#                 [
#                     {'name': 'accuracy', 'threshold': 0.6}
#                 ],
#                 'fairness':
#                 [
#                     {'name': 'demographic_parity_difference', 'threshold': 0.1}
#                 ]
#         }
#     }
# }


framework_list: Dict = {
    "nyc144": {
        "accuracy": 0.7,
        "precision": 0.8,
        "recall": 0.8,
        "f1": 0.7,
        "balanced_accuracy": 0.8,
        "balanced_acc_error": 0.7,
        "disparate_impact": 0.8,
        "demographic_parity_difference": 0.8,
    },
    "euai": {
        "accuracy": 0.7,
        "precision": 0.8,
        "balanced_accuracy": 0.8,
        "balanced_acc_error": 0.7,
        "disparate_impact": 0.8,
    },
    "pureml": {
        "equal_opportunity": 0.8,
        "predictive_value_parity": 0.8,
        "false_positive_parity": 0.8,
        "true_positive_parity": 0.8,
    },
    "eu_ai": {
        "accuracy": 0.6,
        "balancedaccuracyScore": 0.7,
        "averageprecisionscore": 0.8,
        "roc_auc": 0.5,
        "false_positive_rate": 0.6,
        "false_positive_error": 0.5,
        "demographic_parity_ratio": 0.8,
    },
    "custom_policy_to_run_all_metrics": {
        "accuracy": 0.8,
        "precision": 0.8,
        "recall": 0.8,
        "f1": 0.8,
        "balancedaccuracyScore": 0.8,
        "topkaccuracyscore": 0.8,
        "logloss": 0.8,
        "averageprecisionscore": 0.8,
        "roc_auc": 0.8,
        "brierscoreloss": 0.8,
        "kolmogorovsmirnov": 0.8,
        "wassersteindistance": 0.8,
        "hellingerdistance": 0.8,
        "linfinitydistance": 0.8,
        "chisquaredstatistic": 0.8,
        "cramersv": 0.8,
        "populationstabilityindex": 0.8,
        "balanced_accuracy": 0.8,
        "balanced_acc_error": 0.8,
        "selection_rate": 0.8,
        "false_positive_rate": 0.8,
        "false_positive_error": 0.8,
        "false_negative_rate": 0.8,
        "false_negative_error": 0.8,
        "true_positive_rate": 0.8,
        "true_negative_rate": 0.8,
        "predictive_value_parity": 0.8,
        "false_positive_parity": 0.8,
        "true_positive_parity": 0.8,
        "demographic_parity_difference": 0.8,
        "demographic_parity_ratio": 0.8,
        "equalized_odds_difference": 0.8,
        "equalized_odds_ratio": 0.8,
        "equal_opportunity": 0.8,
        "disparate_impact": 0.8,
    },
}

# new_framework_list = {
#     'nyc_144': {
#         'name': 'nyc_144',
#         'description': 'nyc_144',
#         'policies': [
#             {
#                 'name': 'accuracy should be greater than 0.6',
#                 'description': 'accuracy',
#                 'type': 'test',
#                 'threshold': 0.6,
#             },
#             {
#                 'name': 'parity',
#                 'description': 'proof',
#                 'type': 'document',
#                 'threshold': 0,
#             }
#         ]
#     }
# }

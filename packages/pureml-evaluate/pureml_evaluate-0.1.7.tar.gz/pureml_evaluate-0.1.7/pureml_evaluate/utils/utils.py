import numpy as np
import pandas as pd

from pureml_evaluate.schema.metric import ColumnTemplate


def generate_column_names(n, sensitive_data=True):
    if not sensitive_data:
        column_names = ["column_" + str(i) for i in range(1, n + 1)]
    else:
        column_names = ["sensitive_column_" + str(i) for i in range(1, n + 1)]

    return column_names


def get_data_dim(data, sensitive_data=True):
    dim = None
    data_df = None
    column_names = None

    if isinstance(data, list):

        data = np.array(data)
        dim = data.ndim
        column_names = generate_column_names(n=dim, sensitive_data=sensitive_data)
        data_df = pd.DataFrame(data, columns=column_names)
    elif isinstance(data, np.ndarray):

        dim = data.ndim
        column_names = generate_column_names(n=dim, sensitive_data=sensitive_data)
        data_df = pd.DataFrame(data, columns=column_names)
    elif isinstance(data, pd.DataFrame):

        dim = data.shape[1]
        data_df = data.copy()
        column_names = data.columns.to_list()

    else:
        print("Unsupported data type.")

    return dim, data_df, column_names


def give_subsets(s_feat_df, column_names, y_true, y_pred, y_pred_scores):

    subsets = []

    for column in column_names:
        s_feat_grp_col = s_feat_df.groupby(by=column)
        unique_values = list(s_feat_grp_col.groups.keys())

        print("Subset column: ", column)
        print("Unique values in the column: ", unique_values)

        for grp_val in unique_values:
            s_feat_grp = s_feat_grp_col.get_group(grp_val)
            ind = s_feat_grp.index.values

            print("Group: ", grp_val)
            print("Group count: ", len(ind))

            sub_dict = {
                "column": [ColumnTemplate(name=column, value=grp_val)],
                "y_true": y_true[ind],
                "y_pred": y_pred[ind],
                "sensitive_features": s_feat_grp,
            }

            if y_pred_scores is not None:
                sub_dict.update({"y_pred_scores": y_pred_scores[ind]})
            else:
                sub_dict.update({"y_pred_scores": y_pred_scores})

            subsets.append(sub_dict)

    return subsets


# def give_subsets(sensitive_features_array, dim, y_true, y_pred, y_pred_scores):
#     s_feat = sensitive_features_array[:, dim]

#     subsets = []
#     unique_values = np.unique(s_feat)

#     for value in unique_values:
#         ind = np.where(s_feat == value)

#         sub_dict = {
#             "subset_key": value,
#             "y_true": y_true[ind],
#             "y_pred": y_pred[ind],
#             "sensitive_features": sensitive_features_array[[ind]],
#         }

#         if y_pred_scores is not None:
#             sub_dict.update({"y_pred_scores": y_pred_scores[ind]})
#         else:
#             sub_dict.update({"y_pred_scores": y_pred_scores})

#         subsets.append(sub_dict)

#     return subsets

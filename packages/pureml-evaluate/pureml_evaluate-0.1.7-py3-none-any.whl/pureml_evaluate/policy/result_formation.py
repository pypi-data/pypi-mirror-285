def format_response(response):
    get_complete_data(response)
    result_subsets = format_subsets_data(response)
    return result_subsets


def get_complete_data(data):
    if "complete" in data:
        return data["complete"]


def format_subsets_data(data):
    formatted_subsets = []

    if "subsets" in data:
        for subset_key, subset_data in data["subsets"].items():
            single_subset = {}
            if "columns" not in single_subset:
                single_subset["columns"] = {}
            single_subset["columns"] = data["subsets"][subset_key]["columns"]
            for category, metrics in subset_data.items():

                single_subset[category] = metrics

            formatted_subsets.append(single_subset)

    return formatted_subsets

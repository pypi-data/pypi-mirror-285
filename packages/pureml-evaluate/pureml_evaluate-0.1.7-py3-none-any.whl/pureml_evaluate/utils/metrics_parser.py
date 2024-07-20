from pureml_evaluate.schema.metric import MetricTemplate


def format_metric_dict(metric_dict, grader):
    metric_dict_new = MetricTemplate(
        name=list(metric_dict.keys())[0],
        category=grader.evaluation_type,
        value=list(metric_dict.values())[0],
        status=None,
        columns_sensitive=None,
    )

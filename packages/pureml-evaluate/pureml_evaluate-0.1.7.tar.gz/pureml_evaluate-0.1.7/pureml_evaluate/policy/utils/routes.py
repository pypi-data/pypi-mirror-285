from urllib.parse import urljoin

from pureml.schema.backend import BackendSchema


def base_url():
    backend_schema = BackendSchema()
    return backend_schema.BASE_URL


def post_eval_json_url(encoded_model, encoded_model_version):
    url = f"eval-scores?model_name={encoded_model}&version={encoded_model_version}"
    return urljoin(base_url(), url)


def reports_url(org_id, model, model_version):
    url = f"reports?orgId={org_id}&model_name={model}&version={model_version}"
    return urljoin(base_url(), url)

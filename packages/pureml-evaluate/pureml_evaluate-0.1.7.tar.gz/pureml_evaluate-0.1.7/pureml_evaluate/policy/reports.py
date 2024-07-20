import requests
from pureml.cli.auth import get_auth_headers
from pureml.components import get_org_id
from pureml.schema.request import ContentTypeHeader
from rich import print

from pureml_evaluate.policy.utils.routes import reports_url


def get_reports(label_model, framework_name):
    model, model_version = label_model.split(":")
    url = reports_url(get_org_id(), model=model, model_version=model_version)
    headers = get_auth_headers(content_type=ContentTypeHeader.ALL)
    response = requests.get(url, headers=headers)
    for i in range(len(response.json()["data"])):
        if response.json()["data"][i]["framework"]["name"] == framework_name:
            result_url = response.json()["data"][i]["pdf_public_url"]
    print(f"Use this URL to view Report: {result_url}")
    if response.ok:
        print("Reports Fetched")
        return response.json()
    else:
        print("Reports Not Fetched")
        return None

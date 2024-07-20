from urllib.parse import urljoin

import requests
from pureml.cli.auth import get_auth_headers
from pureml.schema.backend import BackendSchema
from pureml.schema.request import ContentTypeHeader
from rich import print


def get_framework_details(framework_name):
    backend_schema = BackendSchema()
    url = f"frameworks/{framework_name}"
    url = urljoin(backend_schema.BASE_URL, url)
    headers = get_auth_headers(content_type=ContentTypeHeader.ALL)
    response = requests.get(url, headers=headers)
    if response.ok:
        print("[green]Succesfully fetched the framework details")
        try:
            framework_data = response.json()["data"][0]
            framework_data["uuid"]
            policies = framework_data["policies"]
            return {
                policy["metric"]: policy["threshold"]
                for policy in policies
                if policy["type"] == "test"
            }
        except Exception as e:
            print(f"Expection: {e}")
            print(f"Exception: {response.json()}")
    else:
        print("[red]Could not fetch the framework details")
        return None

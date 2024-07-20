import json
from urllib.parse import quote

import requests
from pureml.cli.auth import get_auth_headers
from pureml.components import get_org_id
from pureml.schema.request import ContentTypeHeader
from pureml.utils.logger import get_logger
from rich import print

from pureml_evaluate.policy.utils.routes import post_eval_json_url

logger = get_logger(name="pureml_evaluate.policy.assignments.py")


def post_eval_json(data, label_model):
    model, model_version = label_model.split(":")
    payload = {"eval_json": data}
    try:
        data_sending = json.dumps(payload)
        encoded_model = quote(model)
        encoded_model_version = quote(model_version)
        quote(get_org_id())
        url = post_eval_json_url(
            encoded_model=encoded_model, encoded_model_version=encoded_model_version
        )
        #print(f"url :{url}")
        logger.info(f"Payload for updating assignments: {data_sending}")
        logger.info(f"URL for sending to assignments to Backend: {url}")
        headers = get_auth_headers(content_type=ContentTypeHeader.ALL)
        #print(f"Headers: {headers}")
        response = requests.post(url, headers=headers, data=data_sending)
        #print(f"Assignment Status Code: {response.status_code}")
        logger.info(f"Status code for updating assignments: {response.status_code}")
        if not response.ok:
            error_message = response.json().get("message")
            logger.error(
                f"Could not update the assignments. Status Code: {response.status_code} & Error Message: {error_message}"
            )
            print("Could not update the assignments")
            return False
        else:
            logger.info("Updated the assignments")
            print("Updated the assignments")
            return True
    except Exception as e:
        logger.error(f"Exception while updating assignments: {e}")
        print(f"Exception: {e}")

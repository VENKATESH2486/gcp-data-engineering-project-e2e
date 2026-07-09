import base64
import json
import logging

import functions_framework
import google.auth
from google.auth.transport.requests import AuthorizedSession

logging.basicConfig(level=logging.INFO)

AUTH_SCOPE = "https://www.googleapis.com/auth/cloud-platform"

CREDENTIALS, _ = google.auth.default(scopes=[AUTH_SCOPE])

AIRFLOW_URL = (
    "https://fb9e7f83d40f48b2b5767a907e00d339-dot-us-central1.composer.googleusercontent.com"
)

DAG_ID = "customer_ingestion"


@functions_framework.http
def hello_pubsub(request):

    request_json = request.get_json(silent=True)

    if not request_json:
        return ("Missing request body", 400)

    message = request_json["message"]

    payload = json.loads(
        base64.b64decode(message["data"]).decode()
    )

    bucket = payload["bucket"]
    object_name = payload["name"]

    logging.info("Bucket : %s", bucket)
    logging.info("Object : %s", object_name)

    # Only process customer uploads
    if object_name != "raw/customer.csv":
        logging.info("Ignoring file")
        return "Ignored"

    session = AuthorizedSession(CREDENTIALS)

    endpoint = (
        f"{AIRFLOW_URL}/api/v2/dags/{DAG_ID}/dagRuns"
    )

    body = {
        "conf": {
            "bucket": bucket,
            "object": object_name,
        }
    }

    response = session.post(
        endpoint,
        json=body,
        timeout=90,
    )

    logging.info(response.status_code)
    logging.info(response.text)

    response.raise_for_status()

    return "Triggered"
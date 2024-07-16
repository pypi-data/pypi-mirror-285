import os

from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
print(GOOGLE_CLOUD_PROJECT)

client = secretmanager.SecretManagerServiceClient()


def create_secret(secret_id) -> None:
    try:
        client.create_secret(
            request={
                "parent": f"projects/{GOOGLE_CLOUD_PROJECT}",
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
    except Exception as e:
        print(e)


def add_secret_version(secret_id, payload) -> None:
    parent = client.secret_path(GOOGLE_CLOUD_PROJECT, secret_id)
    response = client.add_secret_version(
        request={"parent": parent, "payload": {"data": payload.encode("UTF-8")}}
    )
    print("Added secret version: {}".format(response.name))


def access_secret_version(secret_id, version_id="latest"):
    name = f"projects/{GOOGLE_CLOUD_PROJECT}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

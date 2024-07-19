import json
from google.cloud import secretmanager


class SecretManagerHelper:
    @staticmethod
    def get_credential(project_id, secret_name):
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(
            request={
                "name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            }
        )

        payload = response.payload.data.decode("UTF-8")
        return json.loads(payload)

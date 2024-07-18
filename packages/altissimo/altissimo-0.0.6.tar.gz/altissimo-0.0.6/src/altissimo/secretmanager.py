"""Altissimo SecretManager Class file."""
import os

from google.cloud import secretmanager_v1

GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")


class SecretManager:
    """Altissimo SecretManager Class."""

    def __init__(self, project=None, credentials=None):
        """Initialize the SecretManager class."""
        self.client = secretmanager_v1.SecretManagerServiceClient(
            credentials=credentials,
        )
        self.project = project or GOOGLE_CLOUD_PROJECT

    def get_name(self, secret, version="latest", project=None):
        """Return the full name of the secret."""
        project = project or self.project
        return f"projects/{project}/secrets/{secret}/versions/{version}"

    def get_secret(self, secret, version="latest", project=None):
        """Return the value of a secret."""
        name = self.get_name(secret, version, project)
        request = secretmanager_v1.AccessSecretVersionRequest(name=name)
        response = self.client.access_secret_version(request=request)
        return response.payload.data.decode("utf-8")

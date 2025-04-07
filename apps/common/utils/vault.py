"""
Vault utility module for handling API keys.

This module provides utilities to interact with HashiCorp Vault for secure secrets management.
"""

# Standard library imports
from typing import Any

# Third-party imports
import environ
import hvac
from django.conf import settings

# Initialize environment
env = environ.Env()


# Vault client class
class VaultClient:
    """HashiCorp Vault client for secret management.

    This class provides a wrapper around the hvac client to interact with HashiCorp Vault
    for secure storage and retrieval of API keys and other secrets.

    Attributes:
        client (hvac.Client): The hvac client instance for Vault API communication.
        mount_point (str): The Vault mount point where secrets are stored.
        initialized (bool): Flag indicating whether the client is properly initialized.
    """

    # Initialize the Vault client
    def __init__(self):
        """Initialize the Vault client.

        Reads configuration from Django settings and establishes a connection to the Vault server.
        """

        # Initialize the client
        self.client = None

        # Initialize the mount point
        self.mount_point = env.str("VAULT_MOUNT_POINT", "secret")

        # Initialize the initialized flag
        self.initialized = False

        # Initialize the client
        self._initialize_client()

    # Initialize the hvac client
    def _initialize_client(self) -> None:
        """Initialize the hvac client for Vault.

        Attempts to establish a connection to the Vault server using settings from Django.
        Sets the initialized flag if successful.
        """

        try:
            # Get the vault URL
            vault_url = env.str("VAULT_URL", "http://vault-service:8200")

            # Get the vault token
            vault_token = env.str("VAULT_TOKEN", "root")

            # Initialize the client
            self.client = hvac.Client(url=vault_url, token=vault_token)

            # Check if the client is authenticated
            if self.client.is_authenticated():
                # Set the initialized flag
                self.initialized = True

        except Exception:  # noqa: BLE001
            # Set the initialized flag
            self.initialized = False

    # Store a secret in Vault
    def store_secret(self, path: str, data: dict[str, Any]) -> bool:
        """Store a secret in Vault.

        Args:
            path (str): The path where the secret will be stored.
            data (Dict[str, Any]): The secret data to store.

        Returns:
            bool: True if the secret was stored successfully, False otherwise.
        """

        # Check if the client is initialized
        if not self.initialized:
            # Return False
            return False

        try:
            # Store the secret
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data,
                mount_point=self.mount_point,
            )

        except Exception:  # noqa: BLE001
            # Return False
            return False

        # Return True
        return True

    # Get a secret from Vault
    def get_secret(self, path: str) -> dict[str, Any] | None:
        """Retrieve a secret from Vault.

        Args:
            path (str): The path where the secret is stored.

        Returns:
            Optional[Dict[str, Any]]: The secret data if successful, None otherwise.
        """

        # Check if the client is initialized
        if not self.initialized:
            # Return None
            return None

        try:
            # Get the secret
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.mount_point,
            )

            # Return the secret
            return response["data"]["data"] if response else None

        except Exception:  # noqa: BLE001
            # Return None
            return None

    # Delete a secret from Vault
    def delete_secret(self, path: str) -> bool:
        """Delete a secret from Vault.

        Args:
            path (str): The path where the secret is stored.

        Returns:
            bool: True if the secret was deleted successfully, False otherwise.
        """

        # Check if the client is initialized
        if not self.initialized:
            # Return False
            return False

        try:
            # Delete the secret
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=path,
                mount_point=self.mount_point,
            )

        except Exception:  # noqa: BLE001
            # Return False
            return False

        # Return True
        return True


# Create a singleton instance of the VaultClient
vault_client = VaultClient()


# Store an API key in Vault
def store_api_key(entity_type: str, entity_id: str, api_key: str) -> bool:
    """Store an API key in Vault.

    Args:
        entity_type (str): The type of entity (e.g., 'llm', 'provider').
        entity_id (str): The ID of the entity.
        api_key (str): The API key to store.

    Returns:
        bool: True if the API key was stored successfully, False otherwise.
    """

    # Store the secret
    path = f"{entity_type}/{entity_id}"
    return vault_client.store_secret(path, {"api_key": api_key})


# Get an API key from Vault
def get_api_key(entity_type: str, entity_id: str) -> str | None:
    """Retrieve an API key from Vault.

    Args:
        entity_type (str): The type of entity (e.g., 'llm', 'provider').
        entity_id (str): The ID of the entity.

    Returns:
        Optional[str]: The API key if successful, None otherwise.
    """

    # Get the secret
    path = f"{entity_type}/{entity_id}"
    secret = vault_client.get_secret(path)

    # Return the API key
    return secret.get("api_key") if secret else None


# Delete an API key from Vault
def delete_api_key(entity_type: str, entity_id: str) -> bool:
    """Delete an API key from Vault.

    Args:
        entity_type (str): The type of entity (e.g., 'llm', 'provider').
        entity_id (str): The ID of the entity.

    Returns:
        bool: True if the API key was deleted successfully, False otherwise.
    """

    path = f"{entity_type}/{entity_id}"
    return vault_client.delete_secret(path)

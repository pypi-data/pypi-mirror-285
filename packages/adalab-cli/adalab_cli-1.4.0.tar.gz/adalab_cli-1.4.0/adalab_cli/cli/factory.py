import os

import typer
from adalib_auth.config import get_config
from adalib_auth.keycloak import get_client
from keycloak import KeycloakPostError
from loguru import logger
from rich import print as rich_print

from .login_commands import load_config, load_credentials


# Simulated authentication check function
def authenticate_with_stored_credentials() -> bool:
    """Attempt to authenticate the user with stored credentials."""
    # Load local configuration and credentials
    access_token, refresh_token = load_credentials()
    if access_token is None or refresh_token is None:
        print("Stored credentials not found.")
        return False
    logger.info("Stored credentials found.")
    local_config = load_config()
    if local_config.get("adalab_url") is None or local_config.get("adalab_secret") is None:
        print("AdaLab is not configured in the current environment.")
        return False
    logger.info("AdaLab is configured in the current environment.")

    # Append adalab URL to the API endpoint
    adalab_url = os.path.join(local_config.get("adalab_url"), "adaboard/api")

    # Store adalab secret in local variable
    adalab_secret = local_config.get("adalab_secret")
    os.environ["ADALAB_CLIENT_SECRET"] = adalab_secret

    # Check if the stored credentials are valid
    logger.info("Checking validity of stored credentials.")
    adalib_config = get_config(adaboard_api_url=adalab_url)
    client = get_client(
        adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
        adalib_config.KEYCLOAK_CLIENTS["jupyterhub_secret"],
    )
    if not client.introspect(token=access_token)["active"]:
        logger.warning("Stored access token no longer valid. Attempting to refresh token.")
        try:
            token = client.refresh_token(refresh_token=refresh_token)
            adalib_config.CREDENTIALS["access_token"] = token["access_token"]
            adalib_config.CREDENTIALS["refresh_token"] = token["refresh_token"]
            logger.info("Token refreshed successfully.")
            return True
        except KeycloakPostError as e:
            logger.warning(f"Error refreshing token: {e}")
            return False

    # Initialize adalib configuration with stored credentials
    logger.info("Stored credentials are valid.")
    adalib_config.CREDENTIALS["access_token"] = access_token
    adalib_config.CREDENTIALS["refresh_token"] = refresh_token

    return True


# Callback function to check authentication
def check_authentication():
    """Check if the user is authenticated.

    This function checks if the user is in a self-authenticating environment (AdaLab) or if the
    user is in-line authenticated.
    If the user is not authenticated, it raises a ValueError or a typer.Exit exception.

    :raises ValueError: If the user is not in a self-authenticating environment or if there is no
    existing authentication for an external environment.
    :raises typer.Exit: If the user is not authenticated and cannot be authenticated from the
    configuration file.
    """
    # First, check if user is in a self-authenticating environment (AdaLab)
    try:
        adalib_config = get_config()
        if adalib_config.ENVIRONMENT != "jupyterhub":
            raise ValueError("Not in a self-authenticating environment.")
        return
    except ValueError:
        logger.info("Not in AdaLab. Authentication check required.")

    # Second, check if user is in-line authenticated
    try:
        adalib_config = get_config()
        if adalib_config.ENVIRONMENT == "external" and adalib_config.CREDENTIALS["token"] is None:
            raise ValueError("Not existing authentication for external environment.")
        return
    except ValueError:
        logger.info("Not authenticated. Attempting to authenticate from configuration file.")
    if not authenticate_with_stored_credentials():
        logger.error("User not authenticated.")
        rich_print(
            "[bold red]No valid credentials found."
            "[/bold red] Run [bold]adalab login[/bold] to configure your environment."
        )

        raise typer.Exit(code=1)
    logger.info("User authenticated successfully.")

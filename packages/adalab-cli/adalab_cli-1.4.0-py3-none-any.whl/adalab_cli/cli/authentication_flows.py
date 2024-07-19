import os
from time import sleep

import requests
import typer
from adalib_auth.config import get_config
from keycloak import exceptions
from loguru import logger
from rich import print as rich_print

from .login_commands import CLIENT_ID, KeycloakAuth, save_credentials


def start_browser_auth(adalab_server_url: str = None, adalab_client_secret: str = None):
    """Starts the browser-based authentication flow.

    :param adalab_server_url: The URL of the Adalab server, defaults to None
    :type adalab_server_url: str, optional
    """
    auth = KeycloakAuth(
        adalab_server_url=adalab_server_url, adalab_client_secret=adalab_client_secret
    )
    auth.login()
    logger.success("Authentication successful. Credentials saved.")
    rich_print(
        "🎉 [bold green]Authentication successful[/bold green]. You can now enjoy the AdaLab CLI."
    )


def start_user_token_auth(
    token: str = None,
    adalab_server_url: str = None,
    adalab_client_secret: str = None,
    store_credentials: bool = True,
):
    """Starts the user token authentication flow.

    This function exchanges the user token for an access and refresh token. The token can be given
    directly in the prompt or as an environment variable.
    The access token and refresh token are saved to a file for future use.

    :param token: The user token, it will be retrieve from ADALAB_USER_TOKEN environment variable
        or prompted from the user.
    :type token: str, optional
    :param adalab_server_url: The URL of the ADALab server. If not provided, it will be retrieved
        from the adalab_server_url argument.
    :type adalab_server_url: str, optional
    """

    if token is None:
        token = os.getenv("ADALAB_USER_TOKEN") or typer.prompt(
            "What is your user token", hide_input=True
        )

    resp = requests.get(
        adalab_server_url + "/adaboard/api/adalib/token",
        headers={"Authorization": f"Token {token}"},
    )
    if resp.status_code != 200:
        raise AssertionError(f"Failed to authenticate with user token. {resp.text}")

    jh_token = resp.json()["access_token"]
    new_token = KeycloakAuth(
        adalab_server_url=adalab_server_url, adalab_client_secret=adalab_client_secret
    ).client.exchange_token(token=jh_token, audience=CLIENT_ID)
    if store_credentials:
        save_credentials(
            my_access_token=new_token["access_token"],
            my_refresh_token=new_token["refresh_token"],
        )
    logger.success("Authentication successful. Credentials saved.")
    rich_print(
        "🎉 [bold green]Authentication successful[/bold green]. You can now enjoy the AdaLab CLI."
    )


def start_device_code_auth(adalab_server_url: str = None, adalab_client_secret: str = None):
    """
    Starts the device code authentication flow.

    This function initiates the device code authentication flow using the AdaLab server URL.
    It retrieves the device code information from the Keycloak authentication client,
    prompts the user to visit the verification URI and enter the user code,
    and waits for the user authentication to complete.
    Once the authentication is successful, the access token and refresh token are saved.

    :param adalab_server_url: The AdaLab server URL, defaults to None
    :type adalab_server_url: str, optional
    """
    auth = KeycloakAuth(
        adalab_server_url=adalab_server_url, adalab_client_secret=adalab_client_secret
    )
    device_code_info = auth.client.device()
    device_code = device_code_info["device_code"]
    user_code = device_code_info["user_code"]
    verification_uri = device_code_info["verification_uri"]
    rich_print("Please visit %s and enter the code: %s", verification_uri, user_code)
    rich_print("This code expires in %s seconds", device_code_info["expires_in"])
    token = None
    while token is None:
        try:
            token = auth.client.token(
                grant_type="urn:ietf:params:oauth:grant-type:device_code",
                device_code=device_code,
            )
        except exceptions.KeycloakPostError as e:
            if "authorization_pending" in str(e):
                logger.info("Waiting for user authentication...")
                sleep(device_code_info["interval"])
            else:
                logger.error("Error during device polling: %s", str(e))
                exit(1)
    save_credentials(
        my_access_token=token["access_token"],
        my_refresh_token=token["refresh_token"],
    )
    logger.success("Authentication successful. Credentials saved.")
    rich_print(
        "🎉 [bold green]Authentication successful[/bold green]. You can now enjoy the AdaLab CLI."
    )


def in_line_authentication(
    adalab_server_url: str = None, adalab_secret: str = None, user_token: str = None
) -> None:
    """Auxiliary function for in-line authentication. This will not store credentials in the
    configuration file. Instead it will be used for one-time authentication. Only valid for the
    user token authentication flow.

    :param adalab_server_url: The AdaLab server URL, defaults to None
    :type adalab_server_url: str, optional
    :param adalab_secret: The AdaLab JupyterHub client secret, defaults to None
    :type adalab_secret: str, optional
    :param user_token: The user token retrieved from AdaLab, defaults to None
    :type user_token: str, optional
    """
    if adalab_server_url is None:
        adalab_server_url = os.getenv("ADALAB_URL") or None
    if adalab_secret is None:
        adalab_secret = os.getenv("ADALAB_CLIENT_SECRET") or None
    if user_token is None:
        user_token = os.getenv("ADALAB_USER_TOKEN") or None

    if None in (adalab_server_url, adalab_secret, user_token):
        raise AssertionError("Missing required variables for in-line authentication.")

    get_config(adaboard_api_url=adalab_server_url + "/adaboard/api", token=user_token)

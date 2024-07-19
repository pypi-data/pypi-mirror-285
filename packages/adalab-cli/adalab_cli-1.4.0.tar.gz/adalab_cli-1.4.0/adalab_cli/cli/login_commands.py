import configparser
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import typer
from keycloak import KeycloakOpenID, exceptions
from loguru import logger

login_app = typer.Typer()

PORT = 1997
REDIRECT_URI = f"http://localhost:{PORT}/callback"
CLIENT_ID = "jupyterhub"
REALM = "adalab"


# Determine user's home directory regardless of their OS
home_dir = os.path.expanduser("~")

config = configparser.ConfigParser()
config_path = os.path.join(home_dir, ".adalab", "config.ini")

cred = configparser.ConfigParser()
cred_path = os.path.join(home_dir, ".adalab", "auth.ini")


def extract_code_from_url(url: str):
    """Extract the authorization code from the callback URL."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("code", [None])[0]


def load_config():
    """Load AdaLab configuration the config file."""
    if os.path.exists(config_path):
        config.read(config_path)
        # Load access token and refresh token
        return config["DEFAULT"]
    return {"adalab_url": None, "adalab_secret": None}


def load_credentials():
    """Load the access token and refresh token from the credentials file."""
    if os.path.exists(cred_path):
        cred.read(cred_path)
        # Load access token and refresh token
        return cred["DEFAULT"].get("access_token"), cred["DEFAULT"].get("refresh_token")
    return None, None


def save_config(adalab_url: str, adalab_secret: str = None):
    """Save the AdaLab URL to the config file.

    :param adalab_url: The AdaLab URL.
    :type adalab_url: str
    """
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    config["DEFAULT"] = {
        "adalab_url": adalab_url,
        "adalab_secret": adalab_secret,
    }
    with open(config_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)


def save_credentials(my_access_token: str, my_refresh_token: str):
    """Save the access token and refresh token to the credentials file.

    :param my_access_token: Acess token
    :type my_access_token: str
    :param my_refresh_token: Refresh token
    :type my_refresh_token: str
    """
    os.makedirs(os.path.dirname(cred_path), exist_ok=True)
    cred["DEFAULT"] = {
        "access_token": my_access_token,
        "refresh_token": my_refresh_token,
    }
    with open(cred_path, "w", encoding="utf-8") as credfile:
        cred.write(credfile)


def is_access_token_valid(token: str, client: KeycloakOpenID) -> bool:
    """Check if the access token is valid.

    :param token: Access token to check
    :type token: str
    :param client: Keycloak client
    :type client: KeycloakOpenID
    :return: True if the token is valid, False otherwise.
    :rtype: bool
    """

    try:
        introspect_result = client.introspect(token)
    except exceptions.KeycloakAuthenticationError as e:
        logger.error("Error while authenticating: %s", str(e))
        return False
    if introspect_result["active"]:
        logger.info("Access token is valid")
        return True
    logger.info("Access token is expired.")
    return False


class KeycloakAuth:
    """Keycloak authentication class."""

    def __init__(self, adalab_server_url: str = None, adalab_client_secret: str = None):
        # Prioritize the URL in the class parameter
        stored_config = load_config()
        self.adalab_url = (
            adalab_server_url or stored_config.get("adalab_url") or os.getenv("ADALAB_URL", None)
        )
        self.adalab_client_secret = (
            adalab_client_secret
            or stored_config.get("adalab_secret")
            or os.getenv("ADALAB_CLIENT_SECRET", None)
        )

        if not self.adalab_url or not self.adalab_client_secret:
            raise ValueError(
                "AdaLab URL and client secret must be provided for external environment"
            )

        # Save the URL in the config file
        save_config(adalab_url=self.adalab_url, adalab_secret=adalab_client_secret)
        # Construct the Keycloak authorisation URL

        # Make the Keycloak client
        self.client = KeycloakOpenID(
            server_url=os.path.join(self.adalab_url, "keycloak/auth/"),
            realm_name=REALM,
            client_id=CLIENT_ID,
            client_secret_key=adalab_client_secret,
        )

        # Construct the full authorisation URL for the browser
        self.auth_url = self.client.auth_url(redirect_uri=REDIRECT_URI, scope="openid")
        self.shutdown_flag = False

    def run_server(self):
        """
        Run the local server to handle the callback
        """
        keycloak_auth_instance = self

        class CustomAuthHandler(AuthHandler):
            """CustomAuthHandler class.

            :param AuthHandler: The base class for HTTP request handlers.
            :type AuthHandler: class
            """

            def __init__(self, *args, **kwargs):
                self.keycloak_auth = keycloak_auth_instance
                super().__init__(*args, keycloak_auth=keycloak_auth_instance, **kwargs)

        with HTTPServer(("localhost", PORT), CustomAuthHandler) as httpd:
            httpd.timeout = 1
            while not self.shutdown_flag:
                httpd.handle_request()
            httpd.server_close()

    def login(self):
        """Login to Keycloak"""
        # saved_access_token, saved_refresh_token = load_credentials()
        auth_state = self.is_user_authenticated()
        if auth_state:
            return True
        logger.info("User not authenticated, starting login process")

        webbrowser.open(self.auth_url)
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()
        server_thread.join()

    def is_user_authenticated(self) -> bool:
        """Check if the user is authenticated.

        :return: True if the user is authenticated, False otherwise.
        :rtype: bool
        """
        # Check if the user is already authenticated
        saved_access_token, saved_refresh_token = load_credentials()
        if saved_access_token is None and saved_refresh_token is None:
            return False
        else:
            logger.info("Credentials found, checking validity")
            if is_access_token_valid(saved_access_token, self.client):
                return True
            if saved_refresh_token is None:
                return False
            logger.info("Access token is expired, attempting to refresh.")
            try:
                token = self.client.refresh_token(refresh_token=saved_refresh_token)
            except exceptions.KeycloakAuthenticationError as e:
                logger.warning("Error while refreshing token: %s", str(e))
                return False
            except exceptions.KeycloakPostError as e:
                logger.warning("Error while refreshing token: %s", str(e))
                return False
            logger.info("Token succesfully refreshed. Storing new credentials.")
            save_credentials(token["access_token"], token["refresh_token"])
            return True


class AuthHandler(BaseHTTPRequestHandler):
    """Handle the authentication callback.

    :param BaseHTTPRequestHandler: The base class for HTTP request handlers.
    :type BaseHTTPRequestHandler: class
    """

    def __init__(self, *args, keycloak_auth=None, **kwargs):
        self.keycloak_auth = keycloak_auth
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        """Handle a GET request."""
        if self.path.startswith("/callback"):
            code = extract_code_from_url(self.path)
            token = self.keycloak_auth.client.token(
                grant_type="authorization_code",
                code=code,
                redirect_uri=REDIRECT_URI,
            )
            if "access_token" in token:
                access_token = token["access_token"]
                refresh_token = token["refresh_token"]

                logger.info("Authentication successful. Saving credentials.")
                save_credentials(access_token, refresh_token)

                # Send a user-friendly HTML response
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                html_response = """
                <html>
                <head>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            text-align: center;
                            margin-top: 50px;
                        }
                        h1 {
                            color: #008000;
                        }
                    </style>
                </head>
                <body>
                    <h1>Authentication Successful</h1>
                    <p>Your authentication is complete. You can now close this window.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """
                self.wfile.write(html_response.encode("utf-8"))
                self.keycloak_auth.shutdown_flag = True

            return 0

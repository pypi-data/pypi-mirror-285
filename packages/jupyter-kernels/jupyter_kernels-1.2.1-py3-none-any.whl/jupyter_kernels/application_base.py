# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

import json
import os
import sys
import time
import threading
import typing as t
from getpass import getpass

import questionary

# We use `requests` instead of tornado to avoid trouble with the async event loop
import requests
from datalayer.application import DatalayerApp, base_aliases, base_flags
from rich import print_json
from traitlets import Bool, Unicode

from .cli.login_server import find_http_port, get_token
from ._version import __version__
from .utils import fetch


REQUEST_TIMEOUT = 5


jupyter_kernels_aliases = dict(base_aliases)
jupyter_kernels_aliases["kernels-url"] = "JupyterKernelsBaseApp.kernels_url"
jupyter_kernels_aliases["token"] = "JupyterKernelsBaseApp.token"

jupyter_kernels_flags = dict(base_flags)
jupyter_kernels_flags.update(
    {
        "no-browser": (
            {"JupyterKernelsBaseApp": {"no_browser": True}},
            "Will prompt for user and password on the CLI.",
        )
    }
)


class JupyterKernelsBaseApp(DatalayerApp):
    name = "jupyter_kernels"

    version = __version__

    aliases = jupyter_kernels_aliases

    flags = jupyter_kernels_flags

    username = None

    kernels_url = Unicode(
        "https://oss.datalayer.run", config=True, help="Datalayer RUN URL."
    )

    token = Unicode(None, allow_none=True, config=True, help="User access token.")

    no_browser = Bool(
        False, config=True, help="If true, prompt for login on the CLI only."
    )

    _is_initialized = False

    _requires_auth = True

    def initialize(self, argv=None):
        super().initialize(argv)

        self.token = os.environ.get("DATALAYER_TOKEN", self.token)
        self.kernels_url = os.environ.get("DATALAYER_KERNELS_URL", self.kernels_url)

        if self.token is None:
            self.username = None

        if not getattr(self, "_dispatching", False):
            super().initialize(argv)

        if JupyterKernelsBaseApp._is_initialized:
            return

        JupyterKernelsBaseApp._is_initialized = True

        # Log the user.
        if self._requires_auth:
            self._log_in()

        self.log.info(
            "Jupyter Kernels - Version %s - Connected as %s on %s",
            self.version,
            self.username,
            self.kernels_url,
        )


    def _fetch(self, request: str, **kwargs: t.Any) -> requests.Response:
        """Fetch a network resource as a context manager."""
        try:
            return fetch(request, token=self.token, **kwargs)
        except requests.exceptions.Timeout as e:
            raise e
        except requests.exceptions.HTTPError as e:
            raw = e.response.json()
            self.log.debug(raw)
            raise RuntimeError(
                f"Failed to request the URL {request if isinstance(request, str) else request.url!s}"
            ) from e


    def _log_in(self) -> None:
        """Log the application to the remote provider."""

        if self.token is not None:
            ans=None
            try:
                response = self._fetch(
                    f"{self.kernels_url}/api/iam/v1/login",
                    method="POST",
                    json={
                        "token": self.token
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                content = response.json()
                ans = content["user"]["handle_s"], content["token"]
            except BaseException as e:
                msg = f"Failed to authenticate with the Token on {self.kernels_url}"
                self.log.debug(msg, exc_info=e)
            if ans is None:
                self.log.critical(
                    "Failed to authenticate to %s",
                    self.kernels_url,
                )
                sys.exit(1)
            else:
                username, token = ans
                self.log.info(
                    "Authenticated as %s on %s",
                    username,
                    self.kernels_url,
                )
                self.username = username
                self.token = token
                try:
                    import keyring
                    keyring.set_password(
                        self.kernels_url, "access_token", self.token
                    )
                    self.log.debug("Store token with keyring %s", token)
                except ImportError as e:
                    self.log.debug("Unable to import keyring.", exc_info=e)
            

        if self.token is None:
            # Look for cached value.
            try:
                import keyring
                stored_token = keyring.get_password(self.kernels_url, "access_token")
                if stored_token:
                    content = {}
                    try:
                        response = fetch(
                            f"{self.kernels_url}/api/iam/v1/whoami",
                            headers={
                                "Accept": "application/json",
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {stored_token}",
                                "User-Agent": "Jupyter Kernels CLI",
                            },
                            timeout=REQUEST_TIMEOUT,
                        )
                        content = response.json()
                    except requests.exceptions.Timeout as error:
                        self.log.warning(
                            "Request to get the user profile timed out.", exc_info=error
                        )
                    except requests.exceptions.HTTPError as error:
                        if error.response.status_code == 401:
                            # Invalidate the stored token
                            self.log.debug(
                                f"Delete invalid cached token for {self.kernels_url}"
                            )
                            self._log_out()
                        else:
                            self.log.warning(
                                "Unable to get the user profile - Error %s %s",
                                error.response.status_code,
                                error.response.reason,
                            )
                    except json.JSONDecodeError as error:
                        self.log.warning(
                            "Unable to decode user profile.", exc_info=error
                        )
                    else:
                        username = content.get("profile", {}).get("handle_s")
                        self.log.debug("The cache token belongs to user %s", username)
                        self.username = username
                        self.token = stored_token
            except ImportError as e:
                self.log.debug("Unable to import keyring.", exc_info=e)

        # The previous step may have failed, so self.token may still be None.
        if self.token is None:
            # Ask the user to log in.
            ans = None
            if self.no_browser:
                # Ask credentials via CLI.
                credentials = self._ask_credentials()
                credentials.pop("credentials_type")
                try:
                    response = self._fetch(
                        f"{self.kernels_url}/api/iam/v1/login",
                        method="POST",
                        json=credentials,
                        timeout=REQUEST_TIMEOUT,
                    )
                    content = response.json()
                    ans = content["user"]["handle_s"], content["token"]
                except BaseException as e:
                    if "username" in credentials:
                        msg = f"Failed to authenticate as {credentials['username']} on {self.kernels_url}"
                    else:
                        msg = f"Failed to authenticate with the Token on {self.kernels_url}"
                    self.log.debug(msg, exc_info=e)
            else:
                # Ask credentials via Browser.
                port = find_http_port()
                self.__launch_browser(port)
                ans = get_token(self.kernels_url, port, self.log)

            if ans is None:
                self.log.critical(
                    "Failed to authenticate to %s",
                    self.kernels_url,
                )
                sys.exit(1)
            else:
                username, token = ans
                self.log.info(
                    "Authenticated as %s on %s",
                    username,
                    self.kernels_url,
                )
                self.username = username
                self.token = token
                try:
                    import keyring
                    keyring.set_password(
                        self.kernels_url, "access_token", self.token
                    )
                    self.log.debug("Store token with keyring %s", token)
                except ImportError as e:
                    self.log.debug("Unable to import keyring.", exc_info=e)


    def _ask_credentials(self) -> dict:
        questions = [
            {
                "type": "select",
                "name": "credentials_type",
                "message": "How do you want to log in?",
                "choices": [
                    {"name": "Username/Password", "value": "password"},
                    {"name": "Token", "value": "token"},
                ],
            },
            {
                "type": "text",
                "name": "handle",
                "message": "Username",
                "when": lambda x: x["credentials_type"] == "password",
                "validate": lambda x: True if len(x) > 0 else "Please enter a value",
            },
            {
                "type": "password",
                "name": "password",
                "message": "Password",
                "when": lambda x: x["credentials_type"] == "password",
                "validate": lambda x: True
                if len(x) >= 8
                else "Key must have at least 8 characters",
            },
            {
                "type": "password",
                "name": "token",
                "message": "Token",
                "when": lambda x: x["credentials_type"] == "token",
                "validate": lambda x: True
                if len(x) >= 8
                else "Token must have at least 8 characters",
            },
        ]

        return questionary.prompt(questions)


    def _log_out(self) -> None:
        """Log out from the remote provider"""
        self.token = None
        self.username = None

        try:
            import keyring

            keyring.delete_password(self.kernels_url, "access_token")
        except ImportError as e:
            self.log.debug("Unable to import keyring.", exc_info=e)


    def __launch_browser(self, port: int) -> None:
        """Launch the browser."""
        address = f"http://localhost:{port}/"
        # Deferred import for environments that do not have
        # the webbrowser module.
        import webbrowser

        try:
            browser = webbrowser.get()
        except webbrowser.Error as e:
            self.log.warning("No web browser found: %r.", e)
            browser = None

        if not browser:
            self.log.critical("Open %s to authenticate to the remote server.", address)
            return

        def target():
            assert browser is not None
            time.sleep(1)  # Allow for the server to start
            browser.open(address)

        threading.Thread(target=target).start()

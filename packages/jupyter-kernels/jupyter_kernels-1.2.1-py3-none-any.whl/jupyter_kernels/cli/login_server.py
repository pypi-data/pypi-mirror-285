# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

from __future__ import annotations

import contextlib
import json
import logging
import signal
import socket
import sys
import typing as t
import urllib
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import BaseRequestHandler

from .._version import __version__


HERE = Path(__file__).parent


DATALAYER_IAM_USER_KEY = "@datalayer/iam:user"

DATALAYER_IAM_TOKEN_KEY = "@datalayer/iam:token"


logger = logging.getLogger(__name__)


OAUTH_ERROR_TEMPLATE = """<!DOCTYPE html>
<html>
<body>
  <p>Failed to authenticate with {provider}.</p>
  <p>Error: {error}</p>
  <button id="return-btn">Return to Jupyter</button>
  <script type="module">
    const btn = document.getElementById("return-btn")
    btn.addEventListener("click", () => {{
      // Redirect to default page
      window.location.replace('{base_url}');           
    }})
  </script>
</body>
</html>"""

OAUTH_SUCCESS_TEMPLATE = """<!DOCTYPE html>
<html>
<body>
  <script type="module">
    // Store the user information
    window.localStorage.setItem(
      '{user_key}',
      JSON.stringify({{
        uid: '{uid}',
        handle: '{handle}',
        firstName: '{first_name}',
        lastName: '{last_name}',
        email: '{email}',
        displayName: '{display_name}'
      }})
    );
    // Store the token
    localStorage.setItem('{token_key}', '{token}');
    // Redirect to default page
    window.location.replace('{base_url}');
  </script>
</body>
</html>"""

DEFAULT_PAGE = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8"/>
    <title>🪐 ⚪ Datalayer Login</title>
    <script id="datalayer-config-data" type="application/json">
      {config}
    </script>
    <link rel="shortcut icon" href="data:image/x-icon;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAC7SURBVFiF7ZU9CgIxEIXfTHbPopfYc+pJ9AALtmJnZSOIoJWFoCTzLHazxh/Ebpt5EPIxM8XXTCKTxYyMCYwJFhOYCo4JFiMuu317PZwaqEBUIar4YMmskL73DytGjgu4gAt4PDJdzkkzMBloBhqBgcu69XW+1I+rNSQESNDuaMEhdP/Fj/7oW+ACLuACHk/3F5BAfuMLBjm8/ZnxNvNtHmY4b7Ztut0bqStoVSHfWj9Z6mr8LXABF3CBB3nvkDfEVN6PAAAAAElFTkSuQmCC" type="image/x-icon" />
    <script defer src="/login.js"></script>
  </head>
  <body>
  </body>
</html>"""


class LoginRequestHandler(SimpleHTTPRequestHandler):
    """Custom simple http request handler to serve static files
    from a directory and handle receiving the authentication token
    for CLI usage."""

    server_version = "LoginHTTP/" + __version__

    def _save_oauth_token(self, query: str):
        arguments = urllib.parse.parse_qs(query)
        error = arguments.get("error", [""])[0]
        if error:
            provider = arguments.get("provider", ["<unknown>"])[0]
            content = OAUTH_ERROR_TEMPLATE.format(
                error=error, provider=provider, base_url="/"
            ).encode("utf-8")
            self.send_error(HTTPStatus.UNAUTHORIZED)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(sys.getsizeof(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        user_raw = arguments.get("user", [""])[0]
        token = arguments.get("token", [""])[0]

        if not user_raw or not token:
            self.send_error(HTTPStatus.BAD_REQUEST, "user and token must be provided.")
        user = json.loads(urllib.parse.unquote(user_raw))
        content = OAUTH_SUCCESS_TEMPLATE.format(
            user_key=DATALAYER_IAM_USER_KEY,
            uid=user.get("uid"),
            handle=user["handle_s"],
            first_name=user["first_name_t"],
            last_name=user["last_name_t"],
            email=user["email_s"],
            display_name=" ".join((user["first_name_t"], user["last_name_t"])).strip(),
            token_key=DATALAYER_IAM_TOKEN_KEY,
            token=token,
            base_url="/",
        ).encode('UTF-8', 'replace')
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parts = urllib.parse.urlsplit(self.path)
        if parts[2].strip("/").endswith("oauth/callback"):
            self._save_oauth_token(parts[3])
        elif parts[2] in {"/", "/login"}:
            content = DEFAULT_PAGE.format(
                config=json.dumps(
                    {
                        "runUrl": self.server.kernels_url,
                        "iamRunUrl": self.server.kernels_url,
                        "whiteLabel": False
                    }
                )
            ).encode('UTF-8', 'replace')
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        response = post_data.decode("utf-8")
        content = json.loads(response)
        self.server.token = content["token"]
        self.server.user_handle = content["user_handle"]

        self.send_response(HTTPStatus.CREATED)
        self.send_header("Content-Length", "0")
        self.end_headers()

        signal.raise_signal(signal.SIGINT)

    def log_message(self, format, *args):
        message = format % args
        logger.debug(
            "%s - - [%s] %s\n"
            % (
                self.address_string(),
                self.log_date_time_string(),
                message.translate(self._control_char_table),
            )
        )


class DualStackServer(HTTPServer):
    def __init__(
        self,
        server_address: tuple[str | bytes | bytearray, int],
        RequestHandlerClass: t.Callable[[t.Any, t.Any, t.Self], BaseRequestHandler],
        kernels_url: str,
        bind_and_activate: bool = True,
    ) -> None:
        self.kernels_url = kernels_url
        self.user_handle = None
        self.token = None
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)

    def server_bind(self):
        # suppress exception when protocol is IPv4
        with contextlib.suppress(Exception):
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        return super().server_bind()

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(
            request, client_address, self, directory=str(HERE / "static")
        )


def get_token(
    kernels_url: str, port: int | None = None, logger: logging.Logger = logger
) -> tuple[str, str] | None:
    """Get the user handle and token."""

    server_address = ("", port or find_http_port())
    httpd = DualStackServer(server_address, LoginRequestHandler, kernels_url)
    logger.info("Waiting for user logging... Press Ctrl+C to abort.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logger.debug("Authentication finished")
    return None if httpd.token is None else (httpd.user_handle, httpd.token)


def find_http_port() -> int:
    """Find an available http port."""
    # Xref https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
    sock = socket.socket()
    sock.bind(("", 0))
    return sock.getsockname()[1]


if __name__ == "__main__":
    from sys import argv

    logging.basicConfig(level=logging.INFO)
    kernels_url = ("https://oss.datalayer.run",)
    if len(argv) == 2:
        ans = get_token(kernels_url, port=int(argv[1]))
    else:
        ans = get_token(kernels_url)

    if ans is not None:
        handle, token = ans
    else:
        handle = None
        token = None

    logger.info(f"Logged as {handle} with token: {token}")

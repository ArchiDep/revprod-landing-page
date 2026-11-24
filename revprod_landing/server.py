"""HTTP server serving the landing page."""

import itertools
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from .config import Config
from .pages import render_error, render_index

logger = logging.getLogger(__name__)

# The request line comes from the client, which could otherwise forge log lines
# with newlines or rewrite them with terminal escape sequences. Escapes control
# characters, and backslashes so that an escape cannot be faked, the same way as
# the base class does when it writes to standard error.
_LOG_ESCAPES = str.maketrans(
    {c: rf"\x{c:02x}" for c in itertools.chain(range(0x20), range(0x7F, 0xA0))}
    | {ord("\\"): r"\\"}
)


class LandingPageServer(ThreadingHTTPServer):
    """A server handling each request in its own thread."""

    # Do not wait for the requests in progress to finish when stopping.
    daemon_threads = True

    def __init__(self, config: Config) -> None:
        self.config = config
        super().__init__((config.host, config.port), LandingPageHandler)


class LandingPageHandler(BaseHTTPRequestHandler):
    """
    Serves the landing page at "/", a health check at "/health" and an error
    page for anything else.
    """

    server: LandingPageServer

    # Seconds to wait for a client to send its request. Without a limit, a
    # client that sends it very slowly, or never, keeps a thread busy forever,
    # and enough of them exhaust the server.
    timeout = 30

    def do_GET(self) -> None:
        self._respond(include_body=True)

    def do_HEAD(self) -> None:
        self._respond(include_body=False)

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        # A health check every few seconds would fill the logs.
        if self._is_health_check():
            return

        super().log_request(code, size)

    def log_message(self, format: str, *args: object) -> None:
        # The base class writes to standard error; use the logging module
        # instead, so that the log level applies.
        message = (format % args).translate(_LOG_ESCAPES)
        logger.info("%s - %s", self.address_string(), message)

    def _is_health_check(self) -> bool:
        return urlsplit(self.path).path == "/health"

    def _respond(self, include_body: bool) -> None:
        if self._is_health_check():
            self._send(HTTPStatus.OK, "text/plain; charset=utf-8", "OK", include_body)
            return

        config = self.server.config

        try:
            if urlsplit(self.path).path == "/":
                status = HTTPStatus.OK
                page = render_index(config)
            else:
                status = HTTPStatus.NOT_FOUND
                page = render_error(config, status)
        except Exception:
            logger.exception("Could not render the page for %s", self.path)
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            page = f"<h1>{status.value} {status.phrase}</h1>\n"

        self._send(status, "text/html; charset=utf-8", page, include_body)

    def _send(
        self, status: HTTPStatus, content_type: str, text: str, include_body: bool
    ) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        if include_body:
            self.wfile.write(body)

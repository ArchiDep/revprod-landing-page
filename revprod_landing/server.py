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
    """Serves the landing page at "/" and an error page for anything else."""

    server: LandingPageServer

    # Seconds to wait for a client to send its request. Without a limit, a
    # client that sends it very slowly, or never, keeps a thread busy forever,
    # and enough of them exhaust the server.
    timeout = 30

    def do_GET(self) -> None:
        self._respond(include_body=True)

    def do_HEAD(self) -> None:
        self._respond(include_body=False)

    def log_message(self, format: str, *args: object) -> None:
        # The base class writes to standard error; use the logging module
        # instead, so that the log level applies.
        message = (format % args).translate(_LOG_ESCAPES)
        logger.info("%s - %s", self.address_string(), message)

    def _respond(self, include_body: bool) -> None:
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

        body = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        if include_body:
            self.wfile.write(body)

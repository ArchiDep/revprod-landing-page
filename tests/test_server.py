import socket
import threading
from http.client import HTTPConnection

import pytest

from revprod_landing.config import Config
from revprod_landing.server import LandingPageHandler, LandingPageServer


@pytest.fixture
def server():
    # Port 0 lets the operating system pick a free port.
    config = Config(
        host="127.0.0.1",
        port=0,
        log_level="INFO",
        title="The Revolutionary Product",
        backend_base_url="http://revprod-backend.example.com",
    )
    server = LandingPageServer(config)
    # A short poll interval makes shutdown() return quickly.
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}
    )
    thread.start()

    yield server

    server.shutdown()
    server.server_close()
    thread.join()


def request(server, method, path):
    host, port = server.server_address[:2]
    connection = HTTPConnection(host, port, timeout=5)
    try:
        connection.request(method, path)
        response = connection.getresponse()
        return response.status, response.getheader("Content-Type"), response.read()
    finally:
        connection.close()


def test_landing_page(server):
    status, content_type, body = request(server, "GET", "/")

    assert (status, content_type) == (200, "text/html; charset=utf-8")
    assert b'data-backend-base-url="http://revprod-backend.example.com"' in body


def test_landing_page_with_a_query_string(server):
    status, _, body = request(server, "GET", "/?utm_source=newsletter")

    assert status == 200
    assert b'data-backend-base-url="http://revprod-backend.example.com"' in body


def test_head_has_no_body(server):
    assert request(server, "HEAD", "/") == (200, "text/html; charset=utf-8", b"")


@pytest.mark.parametrize("path", ["/share", "/comments", "/index.html"])
def test_other_paths_are_not_found(server, path):
    status, content_type, body = request(server, "GET", path)

    assert (status, content_type) == (404, "text/html; charset=utf-8")
    assert b'<h2 class="mt-3">Code 404</h2>' in body


def test_control_characters_are_escaped_in_the_logs(server, caplog):
    caplog.set_level("INFO", logger="revprod_landing.server")

    # http.client refuses to send control characters, so write the request
    # directly.
    with socket.create_connection(server.server_address[:2], timeout=5) as client:
        client.sendall(b"GET /\x1b[2J\\x41 HTTP/1.1\r\nHost: localhost\r\n\r\n")
        client.shutdown(socket.SHUT_WR)
        while client.recv(4096):
            pass

    assert [record.getMessage() for record in caplog.records] == [
        '127.0.0.1 - "GET /\\x1b[2J\\\\x41 HTTP/1.1" 404 -'
    ]


def test_a_client_that_sends_nothing_is_disconnected(server, monkeypatch):
    monkeypatch.setattr(LandingPageHandler, "timeout", 0.1)

    with socket.create_connection(server.server_address[:2], timeout=5) as client:
        # The server closes the connection without a response.
        assert client.recv(4096) == b""


def test_health_check(server):
    assert request(server, "GET", "/health") == (
        200,
        "text/plain; charset=utf-8",
        b"OK",
    )


def test_health_check_is_not_logged(server, caplog):
    caplog.set_level("INFO", logger="revprod_landing.server")

    request(server, "GET", "/health")

    assert caplog.records == []


def test_requests_are_logged(server, caplog):
    caplog.set_level("INFO", logger="revprod_landing.server")

    request(server, "GET", "/")

    assert [record.getMessage() for record in caplog.records] == [
        '127.0.0.1 - "GET / HTTP/1.1" 200 -'
    ]

"""
End-to-end test for check_json

Mock HTTP server to test fetching from URI
"""
import multiprocessing
import socket
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest  # type:ignore


def unused_port() -> int:
    """Get an unused port that we can ignore for testing failure"""
    sock = socket.socket()
    sock.bind(("", 0))
    return sock.getsockname()[1]


JSON = """
{
"name": "firstname lastname",
"description": "somedescription",
"email": "name@domain.tld",
"numberval": 5
}
"""
with tempfile.NamedTemporaryFile(delete=False) as tjson:
    JSON_FILE = tjson
    JSON_FILE.write(JSON.encode())
    pytest.JSON_FILEPATH = JSON_FILE.name

# SERVER_PORT = unused_port()
SERVER_PORT = 9996


class SimpleServer(BaseHTTPRequestHandler):
    # pylint: disable=invalid-name
    """
    Very simple HTTP server that only ever gives one answer
    for testing
    """
    content: str = JSON

    def do_GET(self):
        """Respond with static content"""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wfile.write(self.content.encode())

    def do_POST(self):
        """Pass to GET"""
        self.do_GET()

    def do_PUT(self):
        """Pass to GET"""
        self.do_GET()

    def do_DELETE(self):
        """Pass to GET"""
        self.do_GET()

    # pylint: enable=invalid-name


@pytest.fixture(scope="session")
def run_http_server():
    """Run static-response HTTP server with sample JSON"""
    httpd = HTTPServer(("localhost", SERVER_PORT), SimpleServer)
    # httpd.serve_forever()
    proc = multiprocessing.Process(target=httpd.serve_forever)
    proc.start()
    yield True
    proc.terminate()


@pytest.mark.endtoend
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            # OK (from file on disk)
            [
                "--filter",
                "label",
                ".numberval",
                "w@0",
                pytest.JSON_FILEPATH,
            ],
            {
                "returncode": 0,
                "output": "JSONFILE OK - label is 5 | label=5;@0",
            },
        ),
        (
            # OK (from URI)
            [
                "--filter",
                "label",
                ".numberval",
                "w@0",
                f"http://localhost:{SERVER_PORT}/file.json",
            ],
            {
                "returncode": 0,
                "output": "JSONFILE OK - label is 5 | label=5;@0",
            },
        ),
        (
            # WARN
            [
                "--filter",
                "label",
                ".numberval",
                "w@5:5",
                pytest.JSON_FILEPATH,
            ],
            {
                "returncode": 1,
                "output": (
                    "JSONFILE WARNING - label is 5 (outside range @5:5) | label=5;@5:5"
                ),
            },
        ),
        (
            # CRIT
            [
                "--filter",
                "label",
                ".numberval",
                "c@5:5",
                pytest.JSON_FILEPATH,
            ],
            {
                "returncode": 2,
                "output": (
                    "JSONFILE CRITICAL - label is 5 (outside range @5:5) | "
                    "label=5;;@5:5"
                ),
            },
        ),
        (
            # CRIT override WARN
            [
                "--filter",
                "label",
                ".numberval",
                "w@5:5,c@5:5",
                pytest.JSON_FILEPATH,
            ],
            {
                "returncode": 2,
                "output": (
                    "JSONFILE CRITICAL - label is 5 (outside range @5:5) | "
                    "label=5;@5:5;@5:5"
                ),
            },
        ),
        (
            # Unknown - make sure that filters yielding no result fail cleanly
            # up to v0.6.1, doing so raised `StopIteration` and bailed out
            [
                "--filter",
                "label",
                "select(.numberval < 0)",  # This will produce no results
                "w@0",
                pytest.JSON_FILEPATH,
            ],
            {
                "returncode": 3,
                "output": ("JSONFILE UNKNOWN - no check results"),
            },
        ),
    ],
)
# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
def test_end_to_end(run_http_server, test_input, expected, tmp_path):
    """Test"""
    command = ["python3", "-m", "check_json"] + test_input
    res = subprocess.run(command, capture_output=True, check=False, text=True)
    assert res.returncode == expected["returncode"]
    assert res.stdout.strip() == expected["output"]


# pylint: enable=redefined-outer-name
# pylint: enable=unused-argument

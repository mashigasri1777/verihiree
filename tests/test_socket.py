"""
Unit Tests for TCP Socket Client-Server Module (networking/)
Tests socket binding, JSON length header framing, ping, verification, and offline fallback.
"""

import threading
import time
import pytest
from networking.socket_server import SocketVerificationServer
from networking.socket_client import SocketVerificationClient

TEST_PORT = 9199


@pytest.fixture(scope="module")
def socket_server():
    """Spawns a dedicated TCP Socket server in a background thread for testing."""
    server = SocketVerificationServer(host="127.0.0.1", port=TEST_PORT)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.3)  # Wait for server to bind & listen

    yield server

    server.stop()
    time.sleep(0.2)


def test_socket_ping(socket_server):
    """Tests health check over TCP socket."""
    client = SocketVerificationClient(host="127.0.0.1", port=TEST_PORT, timeout=2.0)
    assert client.ping() is True


def test_socket_verify_single_certificate(socket_server):
    """Tests single certificate verification over TCP socket protocol."""
    client = SocketVerificationClient(host="127.0.0.1", port=TEST_PORT, timeout=2.0)
    cert = {
        "candidate_name": "Alice Johnson",
        "certificate_id": "CERT1001",
        "certificate_name": "Python Programming",
        "issuing_organization": "Demo Institute",
        "issue_date": "2024-05-15"
    }
    res = client.verify_certificate(cert)
    assert res["status"] == "VERIFIED"
    assert res["score"] == 100.0
    assert res["checks"]["name_match"] is True


def test_socket_batch_verify(socket_server):
    """Tests batch verification over TCP socket protocol."""
    client = SocketVerificationClient(host="127.0.0.1", port=TEST_PORT, timeout=2.0)
    certs = [
        {"certificate_id": "CERT1001", "candidate_name": "Alice Johnson", "certificate_name": "Python Programming", "issuing_organization": "Demo Institute"},
        {"certificate_id": "CERT1002", "candidate_name": "Bob Smith", "certificate_name": "Web Development", "issuing_organization": "Demo Institute"},
    ]
    results = client.batch_verify(certs)
    assert len(results) == 2
    assert results[0]["status"] == "VERIFIED"
    assert results[1]["status"] == "VERIFIED"


def test_socket_offline_fallback():
    """Tests client graceful handling when server is offline."""
    offline_client = SocketVerificationClient(host="127.0.0.1", port=9998, timeout=0.5)
    assert offline_client.ping() is False

    res = offline_client.verify_certificate({
        "certificate_id": "CERT1001",
        "certificate_name": "Python"
    })
    assert res["status"] == "UNABLE_TO_VERIFY"
    assert "offline" in res["details"].lower() or "connect" in res["details"].lower()

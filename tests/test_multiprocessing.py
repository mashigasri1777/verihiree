"""
Unit Tests for Multiprocessing Module (multiprocessing_module/parallel_verifier.py)
Tests concurrent batch certificate verification and process identification.
"""

import threading
import time
import pytest
from networking.socket_server import SocketVerificationServer
from multiprocessing_module.parallel_verifier import verify_certificates_in_parallel


@pytest.fixture(scope="module")
def shared_socket_server():
    """Runs socket server on default port for multiprocessing tests."""
    server = SocketVerificationServer(host="127.0.0.1", port=9099)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.3)

    yield server

    server.stop()
    time.sleep(0.2)


def test_parallel_verification_pool(shared_socket_server):
    """Tests parallel verification across multiple CPU workers."""
    test_certs = [
        {"certificate_id": "CERT1001", "candidate_name": "Alice Johnson", "certificate_name": "Python Programming", "issuing_organization": "Demo Institute"},
        {"certificate_id": "CERT1002", "candidate_name": "Bob Smith", "certificate_name": "Web Development", "issuing_organization": "Demo Institute"},
        {"certificate_id": "AWS-SAA-8842", "candidate_name": "Sarah Connor", "certificate_name": "AWS Certified Solutions Architect", "issuing_organization": "Amazon Web Services"},
        {"certificate_id": "CERT9999", "candidate_name": "Fake Candidate", "certificate_name": "Python Programming", "issuing_organization": "Demo Institute"},
    ]

    response = verify_certificates_in_parallel(test_certs, max_workers=4)

    assert "results" in response
    assert "summary" in response
    assert "diagnostics" in response

    results = response["results"]
    assert len(results) == 4

    # Verify worker metadata is attached
    for res in results:
        assert "multiprocessing_meta" in res
        assert res["multiprocessing_meta"]["worker_pid"] > 0
        assert res["multiprocessing_meta"]["execution_time_ms"] >= 0.0

    # Verify functional summary
    summary = response["summary"]
    assert summary["total_certificates"] == 4
    assert summary["verified_count"] == 3
    assert summary["failed_count"] == 1
    assert summary["average_score"] > 0.0


def test_empty_certificates_list():
    """Tests parallel verifier with empty input."""
    response = verify_certificates_in_parallel([])
    assert response["results"] == []
    assert response["summary"]["total_certificates"] == 0

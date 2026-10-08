"""
Unit Tests for Verification Engine & Comparison Engine
"""

import pytest
from backend.comparison_engine import compare_certificate_data, compare_names, compare_ids, compare_courses
from verification.mock_verifier import MockCertificateVerifier
from backend.verification_engine import default_verification_engine


def test_name_comparison():
    """Tests name matching logic."""
    score, match, _ = compare_names("Alice Johnson", "Alice Johnson")
    assert score == 1.0
    assert match is True

    # Reordered / formatted
    score, match, _ = compare_names("Johnson, Alice", "Alice Johnson")
    assert score == 1.0
    assert match is True

    # Clear mismatch
    score, match, _ = compare_names("John Doe", "Alice Johnson")
    assert score == 0.0
    assert match is False


def test_id_comparison():
    """Tests certificate ID matching logic."""
    score, match, _ = compare_ids("CERT1001", "CERT-1001")
    assert score == 1.0
    assert match is True

    score, match, _ = compare_ids("CERT1001", "CERT9999")
    assert score == 0.0
    assert match is False


def test_mock_verifier_valid_scenario():
    """Tests verification of valid official certificate."""
    verifier = MockCertificateVerifier()
    cert = {
        "candidate_name": "Alice Johnson",
        "certificate_id": "CERT1001",
        "certificate_name": "Python Programming",
        "issuing_organization": "Demo Institute",
        "issue_date": "2024-05-15"
    }
    res = verifier.verify(cert)
    assert res.status == "VERIFIED"
    assert res.score == 100.0
    assert res.checks["name_match"] is True
    assert res.checks["certificate_id_match"] is True


def test_mock_verifier_mismatch_scenario():
    """Tests verification when candidate name does not match official record."""
    verifier = MockCertificateVerifier()
    cert = {
        "candidate_name": "Imposter Bob",
        "certificate_id": "CERT1001",  # Official owner is Alice Johnson
        "certificate_name": "Python Programming",
        "issuing_organization": "Demo Institute",
        "issue_date": "2024-05-15"
    }
    res = verifier.verify(cert)
    assert res.score == 70.0
    assert res.status == "REVIEW REQUIRED"
    assert res.checks["name_match"] is False
    assert res.checks["certificate_id_match"] is True


def test_mock_verifier_revoked_scenario():
    """Tests verification of a revoked / fraudulent certificate."""
    verifier = MockCertificateVerifier()
    cert = {
        "candidate_name": "Fake Candidate",
        "certificate_id": "CERT9999",
        "certificate_name": "Python Programming",
        "issuing_organization": "Demo Institute",
        "issue_date": "2022-01-01"
    }
    res = verifier.verify(cert)
    assert res.status == "FAILED"
    assert res.score == 0.0


def test_verification_engine():
    """Tests central verification engine."""
    res = default_verification_engine.verify_single_certificate({
        "candidate_name": "Alice Johnson",
        "certificate_id": "CERT1001",
        "certificate_name": "Python Programming",
        "issuing_organization": "Demo Institute",
        "issue_date": "2024-05-15"
    })
    assert res["status"] == "VERIFIED"
    assert res["score"] == 100.0

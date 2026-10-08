"""
Unit Tests for Functional Programming Module (functional/functional_processing.py)
Tests pure functions, higher-order functions, map/filter/reduce, and transformation pipelines.
"""

import pytest
from functional.functional_processing import (
    normalize_string,
    normalize_certificate_name,
    normalize_certificate_dict,
    is_valid_certificate_structure,
    compose,
    create_field_extractor,
    create_score_filter,
    create_status_filter,
    filter_valid_certificates,
    filter_by_status,
    filter_by_score_threshold,
    extract_scores,
    calculate_total_score,
    calculate_average_score,
    summarize_verification_batch,
    functional_verification_pipeline,
)


def test_pure_string_normalization():
    """Tests deterministic pure string cleaning."""
    assert normalize_string("  John   Doe  ") == "john doe"
    assert normalize_string("PYTHON   PROGRAMMING") == "python programming"
    assert normalize_string(None) == ""


def test_pure_certificate_normalization():
    """Tests certificate name prefix stripping."""
    assert normalize_certificate_name("Certificate in Python Programming") == "python programming"
    assert normalize_certificate_name("Certificate of Completion: Machine Learning") == "machine learning"


def test_immutability():
    """Verifies that dictionary normalization creates a new object without mutating input."""
    original = {"name": "AWS Certified", "id": "CERT-1"}
    normalized = normalize_certificate_dict(original)
    
    assert "name_normalized" in normalized
    assert "name_normalized" not in original
    assert normalized["name_normalized"] == "aws certified"


def test_higher_order_functions():
    """Tests compose, closures, and predicate generators."""
    add_prefix = lambda s: f"pre_{s}"
    to_upper = lambda s: s.upper()
    composed = compose(to_upper, add_prefix)
    
    assert composed("test") == "PRE_TEST"

    # Closure extractor
    name_getter = create_field_extractor("name")
    assert name_getter({"name": "Alice"}) == "Alice"
    assert name_getter({}) is None

    # Predicate generators
    score_above_80 = create_score_filter(80.0)
    assert score_above_80({"score": 95.0}) is True
    assert score_above_80({"score": 75.0}) is False

    is_verified = create_status_filter("VERIFIED")
    assert is_verified({"status": "VERIFIED"}) is True
    assert is_verified({"status": "FAILED"}) is False


def test_map_filter_reduce_pipeline():
    """Tests standard functional transformations."""
    sample_results = [
        {"name": "Cert A", "score": 100.0, "status": "VERIFIED"},
        {"name": "Cert B", "score": 70.0, "status": "REVIEW REQUIRED"},
        {"name": "Cert C", "score": 40.0, "status": "SUSPICIOUS"},
        {"name": "Cert D", "score": 0.0, "status": "FAILED"},
    ]

    # map
    scores = extract_scores(sample_results)
    assert scores == [100.0, 70.0, 40.0, 0.0]

    # filter
    verified = filter_by_status(sample_results, "VERIFIED")
    assert len(verified) == 1
    assert verified[0]["name"] == "Cert A"

    high_scorers = filter_by_score_threshold(sample_results, 60.0)
    assert len(high_scorers) == 2

    # reduce
    total = calculate_total_score(scores)
    assert total == 210.0
    avg = calculate_average_score(scores)
    assert avg == 52.5


def test_summarize_verification_batch():
    """Tests full aggregate summary calculation via Functional Programming."""
    sample_results = [
        {"score": 100.0, "status": "VERIFIED"},
        {"score": 100.0, "status": "VERIFIED"},
    ]
    summary = summarize_verification_batch(sample_results)
    assert summary["total_certificates"] == 2
    assert summary["verified_count"] == 2
    assert summary["average_score"] == 100.0
    assert summary["overall_status"] == "VERIFIED"

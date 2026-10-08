"""
Unit Tests for SymPy Mathematics Scoring Engine (mathematics/authenticity_model.py)
Tests symbolic formulation, substitutions, evaluation, latex generation, and sensitivity analysis.
"""

import pytest
from mathematics.authenticity_model import (
    SymPyScoringEngine,
    calculate_certificate_score,
    get_symbolic_formula,
    get_latex_formula,
    get_weight_derivatives,
    classify_score
)


def test_sympy_symbols_and_formula():
    """Tests symbolic construction of the authenticity score formula."""
    engine = SymPyScoringEngine()
    formula_str = str(engine.score_expression)
    
    assert "name_match" in formula_str
    assert "certificate_id_match" in formula_str
    assert "course_match" in formula_str
    assert "organization_match" in formula_str
    assert "date_match" in formula_str


def test_perfect_score_substitution():
    """Tests 100% score calculation when all variables match."""
    res = calculate_certificate_score(
        name_match=1.0,
        certificate_id_match=1.0,
        course_match=1.0,
        organization_match=1.0,
        date_match=1.0
    )
    assert res["score"] == 100.0
    assert res["status"] == "VERIFIED"
    assert res["breakdown"]["name_contribution"] == 30.0
    assert res["breakdown"]["id_contribution"] == 30.0
    assert res["breakdown"]["course_contribution"] == 20.0
    assert res["breakdown"]["org_contribution"] == 10.0
    assert res["breakdown"]["date_contribution"] == 10.0


def test_mismatched_name_score():
    """Tests score when name is mismatched (30 points deducted -> 70%)."""
    res = calculate_certificate_score(
        name_match=0.0,
        certificate_id_match=1.0,
        course_match=1.0,
        organization_match=1.0,
        date_match=1.0
    )
    assert res["score"] == 70.0
    assert res["status"] == "REVIEW REQUIRED"
    assert res["breakdown"]["name_contribution"] == 0.0


def test_mismatched_id_score():
    """Tests score when certificate ID is mismatched (30 points deducted -> 70%)."""
    res = calculate_certificate_score(
        name_match=1.0,
        certificate_id_match=0.0,
        course_match=1.0,
        organization_match=1.0,
        date_match=1.0
    )
    assert res["score"] == 70.0
    assert res["status"] == "REVIEW REQUIRED"


def test_partial_match_score():
    """Tests partial fuzzy match coefficients."""
    res = calculate_certificate_score(
        name_match=0.5,
        certificate_id_match=1.0,
        course_match=0.5,
        organization_match=1.0,
        date_match=0.5
    )
    # 30*0.5 + 30*1 + 20*0.5 + 10*1 + 10*0.5 = 15 + 30 + 10 + 10 + 5 = 70
    assert res["score"] == 70.0


def test_latex_and_derivatives():
    """Tests LaTeX formula export and partial derivatives."""
    latex = get_latex_formula()
    assert len(latex) > 0
    
    derivs = get_weight_derivatives()
    assert derivs['d_Score/d_name_match'] == '30'
    assert derivs['d_Score/d_certificate_id_match'] == '30'
    assert derivs['d_Score/d_course_match'] == '20'
    assert derivs['d_Score/d_organization_match'] == '10'
    assert derivs['d_Score/d_date_match'] == '10'


def test_score_classification():
    """Tests classification thresholds."""
    status, _, _ = classify_score(95.0)
    assert status == "VERIFIED"

    status, _, _ = classify_score(80.0)
    assert status == "REVIEW REQUIRED"

    status, _, _ = classify_score(50.0)
    assert status == "SUSPICIOUS"

    status, _, _ = classify_score(20.0)
    assert status == "FAILED"

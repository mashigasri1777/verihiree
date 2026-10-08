"""
VERIRESUME - Functional Programming Module
==========================================
This module demonstrates core functional programming concepts in Python:
1. Pure Functions: Deterministic functions with no side effects.
2. Higher-Order Functions: Functions that accept or return other functions.
3. Lambdas & Closures: Inline anonymous function objects.
4. map(), filter(), reduce() transformations: Declarative collection pipelines.
5. Function Composition: Building complex pipelines by composing simple functions.
6. Immutability & Referential Transparency: Transforming data without mutating inputs.
"""

from functools import reduce
import re
from typing import Callable, List, Dict, Any, TypeVar, Optional

T = TypeVar('T')
U = TypeVar('U')


# ============================================================================
# 1. PURE FUNCTIONS (No side effects, deterministic return values)
# ============================================================================

def normalize_string(text: Optional[str]) -> str:
    """
    Pure Function: Normalizes a string by converting to lowercase, stripping
    leading/trailing whitespace, and collapsing multiple spaces to a single space.
    """
    if not text:
        return ""
    # Declarative text cleanup
    cleaned = re.sub(r'\s+', ' ', str(text).strip().lower())
    return cleaned


def normalize_certificate_name(name: Optional[str]) -> str:
    """
    Pure Function: Standardizes certificate titles (e.g. removing extraneous punctuation).
    """
    if not name:
        return ""
    norm = normalize_string(name)
    # Remove redundant prefixes like 'certificate in', 'certified', etc., for comparison
    norm = re.sub(r'^(certificate in|certified in|certificate of completion:?)\s*', '', norm)
    return norm.strip()


def normalize_certificate_dict(cert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure Function: Returns a new dictionary with normalized fields without mutating the original.
    Demonstrates Immutability.
    """
    return {
        **cert,
        "name_normalized": normalize_certificate_name(cert.get("name") or cert.get("course_name") or ""),
        "candidate_normalized": normalize_string(cert.get("candidate_name") or cert.get("candidate") or ""),
        "certificate_id_normalized": normalize_string(cert.get("certificate_id") or cert.get("id") or ""),
        "organization_normalized": normalize_string(cert.get("issuing_organization") or cert.get("organization") or ""),
        "issue_date_normalized": normalize_string(cert.get("issue_date") or cert.get("date") or ""),
    }


def is_valid_certificate_structure(cert: Dict[str, Any]) -> bool:
    """
    Pure Predicate Function: Checks if a certificate record has the minimum
    required fields to be valid for verification.
    """
    # A valid certificate must have at least a name or ID, and non-empty metadata
    has_name = bool(cert.get("name") or cert.get("course_name"))
    has_id = bool(cert.get("certificate_id") or cert.get("id"))
    has_org = bool(cert.get("organization") or cert.get("issuing_organization"))
    
    # Must have either a valid ID or (name and organization)
    return has_id or (has_name and has_org)


# ============================================================================
# 2. HIGHER-ORDER FUNCTIONS (Functions returning or operating on functions)
# ============================================================================

def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Higher-Order Function: Composes multiple functions from right to left.
    compose(f, g, h)(x) == f(g(h(x)))
    """
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def create_field_extractor(field_name: str) -> Callable[[Dict[str, Any]], Any]:
    """
    Higher-Order Function (Closure): Returns a function that extracts a specified key from a dict.
    Demonstrates Partial Application / Currying concept.
    """
    return lambda d: d.get(field_name)


def create_score_filter(min_score: float) -> Callable[[Dict[str, Any]], bool]:
    """
    Higher-Order Function: Returns a predicate function that filters items by minimum score threshold.
    """
    return lambda item: float(item.get("score", 0.0)) >= min_score


def create_status_filter(target_status: str) -> Callable[[Dict[str, Any]], bool]:
    """
    Higher-Order Function: Returns a predicate function filtering by verification status.
    """
    target = target_status.strip().upper()
    return lambda item: str(item.get("status", "")).strip().upper() == target


# ============================================================================
# 3. FUNCTIONAL TRANSFORMATIONS USING map(), filter(), reduce()
# ============================================================================

def filter_valid_certificates(certificates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    FP Idiom: filter() with predicate function to eliminate malformed records.
    """
    return list(filter(is_valid_certificate_structure, certificates))


def filter_by_status(certificates: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """
    FP Idiom: filter() using a higher-order status filter closure.
    """
    predicate = create_status_filter(status)
    return list(filter(predicate, certificates))


def filter_by_score_threshold(certificates: List[Dict[str, Any]], min_score: float) -> List[Dict[str, Any]]:
    """
    FP Idiom: filter() with higher-order score threshold closure.
    """
    predicate = create_score_filter(min_score)
    return list(filter(predicate, certificates))


def extract_scores(results: List[Dict[str, Any]]) -> List[float]:
    """
    FP Idiom: map() with lambda to extract float scores from verification result records.
    """
    score_extractor = lambda res: float(res.get("score", 0.0))
    return list(map(score_extractor, results))


def calculate_total_score(scores: List[float]) -> float:
    """
    FP Idiom: reduce() with lambda to compute sum of scores.
    """
    if not scores:
        return 0.0
    return float(reduce(lambda acc, val: acc + val, scores, 0.0))


def calculate_average_score(scores: List[float]) -> float:
    """
    Pure Function: Computes arithmetic mean using calculate_total_score.
    """
    if not scores:
        return 0.0
    total = calculate_total_score(scores)
    return round(total / len(scores), 2)


def summarize_verification_batch(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    FP Idiom: Uses map(), filter(), and reduce() to generate complete aggregate statistics.
    """
    if not results:
        return {
            "total_certificates": 0,
            "verified_count": 0,
            "review_count": 0,
            "suspicious_count": 0,
            "failed_count": 0,
            "average_score": 0.0,
            "overall_status": "NO_CERTIFICATES",
            "scores": []
        }

    # 1. Map to extract scores
    scores = extract_scores(results)

    # 2. Filter counts using higher-order predicate generators
    verified_items = list(filter(create_status_filter("VERIFIED"), results))
    review_items = list(filter(create_status_filter("REVIEW REQUIRED"), results))
    suspicious_items = list(filter(create_status_filter("SUSPICIOUS"), results))
    failed_items = list(filter(lambda x: str(x.get("status", "")).upper() in ("FAILED", "UNABLE_TO_VERIFY", "INVALID"), results))

    # 3. Reduce to compute overall average score
    avg_score = calculate_average_score(scores)

    # 4. Determine overall status from aggregate metrics
    if avg_score >= 90.0 and len(failed_items) == 0:
        overall_status = "VERIFIED"
    elif avg_score >= 70.0 and len(failed_items) == 0:
        overall_status = "REVIEW REQUIRED"
    elif len(verified_items) > 0 and len(failed_items) > 0:
        overall_status = "PARTIALLY VERIFIED"
    elif avg_score >= 40.0:
        overall_status = "SUSPICIOUS"
    else:
        overall_status = "FAILED"

    return {
        "total_certificates": len(results),
        "verified_count": len(verified_items),
        "review_count": len(review_items),
        "suspicious_count": len(suspicious_items),
        "failed_count": len(failed_items),
        "average_score": avg_score,
        "overall_status": overall_status,
        "scores": scores,
        "highest_score": reduce(lambda a, b: max(a, b), scores, 0.0) if scores else 0.0,
        "lowest_score": reduce(lambda a, b: min(a, b), scores, 100.0) if scores else 0.0,
    }


# ============================================================================
# 4. COMPLETE FUNCTIONAL PIPELINE
# ============================================================================

def functional_verification_pipeline(
    raw_certificates: List[Dict[str, Any]],
    verification_fn: Callable[[Dict[str, Any]], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Demonstrates a complete functional data processing pipeline:
    
    raw_certificates
        -> map(normalize_certificate_dict)
        -> filter(is_valid_certificate_structure)
        -> map(verification_fn)
        -> summarize_verification_batch (reduce/aggregate)
        -> final report dictionary
    """
    # Step 1: map raw certificates to normalized immutable dictionaries
    normalized_certs = list(map(normalize_certificate_dict, raw_certificates))

    # Step 2: filter out invalid / empty certificate entries
    valid_certs = list(filter(is_valid_certificate_structure, normalized_certs))

    # Step 3: map verification function over valid certificates
    verification_results = list(map(verification_fn, valid_certs))

    # Step 4: reduce / aggregate results into comprehensive summary
    batch_summary = summarize_verification_batch(verification_results)

    return {
        "processed_certificates": verification_results,
        "summary": batch_summary,
        "pipeline_metadata": {
            "total_input": len(raw_certificates),
            "valid_processed": len(valid_certs),
            "filtered_out": len(raw_certificates) - len(valid_certs),
            "functional_paradigm": "Pure Functions + map/filter/reduce Pipeline"
        }
    }

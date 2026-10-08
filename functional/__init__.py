"""
VERIRESUME Functional Programming Module
Implements pure functions, higher-order functions, and map/filter/reduce pipelines.
"""

from .functional_processing import (
    normalize_string,
    normalize_certificate_dict,
    filter_valid_certificates,
    filter_by_status,
    filter_by_score_threshold,
    extract_scores,
    calculate_total_score,
    calculate_average_score,
    summarize_verification_batch,
    compose,
    create_field_extractor,
    functional_verification_pipeline,
)

__all__ = [
    "normalize_string",
    "normalize_certificate_dict",
    "filter_valid_certificates",
    "filter_by_status",
    "filter_by_score_threshold",
    "extract_scores",
    "calculate_total_score",
    "calculate_average_score",
    "summarize_verification_batch",
    "compose",
    "create_field_extractor",
    "functional_verification_pipeline",
]

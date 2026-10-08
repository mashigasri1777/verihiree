"""
VERIRESUME Mathematics Module
Implements symbolic mathematical scoring using the SymPy library.
"""

from .authenticity_model import (
    SymPyScoringEngine,
    calculate_certificate_score,
    get_symbolic_formula,
    get_latex_formula,
    get_weight_derivatives,
    classify_score,
)

__all__ = [
    "SymPyScoringEngine",
    "calculate_certificate_score",
    "get_symbolic_formula",
    "get_latex_formula",
    "get_weight_derivatives",
    "classify_score",
]

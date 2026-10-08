"""
VERIRESUME - SymPy Authenticity Scoring Engine
=================================================
This module uses the SymPy symbolic mathematics library to model,
evaluate, simplify, and analyze certificate authenticity scores.

Key SymPy Features Demonstrated:
1. Symbolic variables creation using sympy.symbols()
2. Mathematical expression formulation and algebraic representation
3. Exact symbolic substitution using expr.subs()
4. Exact numerical evaluation using evalf() / float conversion
5. Symbolic partial differentiation (calculus) for sensitivity analysis
6. LaTeX and String representation generation for frontend/viva demonstration
"""

from typing import Dict, Any, Tuple
import sympy as sp


class SymPyScoringEngine:
    """
    Symbolic mathematical authenticity scoring engine powered by SymPy.
    """

    def __init__(self):
        # 1. Define Symbolic Variables
        # Each symbol represents a normalized match coefficient in range [0.0, 1.0]
        self.name_match = sp.Symbol('name_match', real=True, nonnegative=True)
        self.certificate_id_match = sp.Symbol('certificate_id_match', real=True, nonnegative=True)
        self.course_match = sp.Symbol('course_match', real=True, nonnegative=True)
        self.organization_match = sp.Symbol('organization_match', real=True, nonnegative=True)
        self.date_match = sp.Symbol('date_match', real=True, nonnegative=True)

        # 2. Define SymPy Symbolic Weights (sum = 100)
        self.w_name = sp.Integer(30)
        self.w_id = sp.Integer(30)
        self.w_course = sp.Integer(20)
        self.w_org = sp.Integer(10)
        self.w_date = sp.Integer(10)

        # 3. Construct the Symbolic Authenticity Equation
        self.score_expression = (
            self.w_name * self.name_match +
            self.w_id * self.certificate_id_match +
            self.w_course * self.course_match +
            self.w_org * self.organization_match +
            self.w_date * self.date_match
        )

        # 4. Symbolic Sensitivity Analysis (Partial Derivatives)
        self.derivatives = {
            'd_Score/d_name_match': sp.diff(self.score_expression, self.name_match),
            'd_Score/d_certificate_id_match': sp.diff(self.score_expression, self.certificate_id_match),
            'd_Score/d_course_match': sp.diff(self.score_expression, self.course_match),
            'd_Score/d_organization_match': sp.diff(self.score_expression, self.organization_match),
            'd_Score/d_date_match': sp.diff(self.score_expression, self.date_match),
        }

    def evaluate_score(
        self,
        name_match: float = 0.0,
        certificate_id_match: float = 0.0,
        course_match: float = 0.0,
        organization_match: float = 0.0,
        date_match: float = 0.0
    ) -> Dict[str, Any]:
        """
        Substitutes match indicators into the SymPy symbolic equation and computes
        the final authenticity score.
        """
        # Ensure values are clamped in [0.0, 1.0]
        vals = {
            self.name_match: max(0.0, min(1.0, float(name_match))),
            self.certificate_id_match: max(0.0, min(1.0, float(certificate_id_match))),
            self.course_match: max(0.0, min(1.0, float(course_match))),
            self.organization_match: max(0.0, min(1.0, float(organization_match))),
            self.date_match: max(0.0, min(1.0, float(date_match)))
        }

        # Substitute symbolic variables
        substituted_expr = self.score_expression.subs(vals)
        
        # Evaluate numerical result exactly using SymPy
        numerical_score = float(substituted_expr.evalf())
        rounded_score = round(numerical_score, 2)

        # Determine verification status
        status, status_color, description = classify_score(rounded_score)

        return {
            "score": rounded_score,
            "raw_score": numerical_score,
            "status": status,
            "status_color": status_color,
            "description": description,
            "symbolic_formula": str(self.score_expression),
            "latex_formula": sp.latex(self.score_expression),
            "substituted_formula": str(substituted_expr),
            "breakdown": {
                "name_contribution": float((self.w_name * vals[self.name_match]).evalf()),
                "id_contribution": float((self.w_id * vals[self.certificate_id_match]).evalf()),
                "course_contribution": float((self.w_course * vals[self.course_match]).evalf()),
                "org_contribution": float((self.w_org * vals[self.organization_match]).evalf()),
                "date_contribution": float((self.w_date * vals[self.date_match]).evalf()),
            }
        }

    def get_formula_representations(self) -> Dict[str, str]:
        """
        Returns string, LaTeX, and mathematical representations for display.
        """
        return {
            "symbolic": str(self.score_expression),
            "pretty": sp.pretty(self.score_expression, use_unicode=True),
            "latex": sp.latex(self.score_expression),
            "weights": {
                "name_match": int(self.w_name),
                "certificate_id_match": int(self.w_id),
                "course_match": int(self.w_course),
                "organization_match": int(self.w_org),
                "date_match": int(self.w_date)
            },
            "derivatives": {k: str(v) for k, v in self.derivatives.items()}
        }


def classify_score(score: float) -> Tuple[str, str, str]:
    """
    Classifies a calculated authenticity score into standard audit categories.

    Score Ranges:
    - 90 - 100: VERIFIED (Green)
    - 70 - 89:  REVIEW REQUIRED / SUSPICIOUS (Orange/Yellow)
    - 40 - 69:  SUSPICIOUS (Orange-Red)
    - 0 - 39:   FAILED (Red)
    """
    if score >= 90.0:
        return "VERIFIED", "#10B981", "Certificate data fully matches official registry record."
    elif score >= 70.0:
        return "REVIEW REQUIRED", "#F59E0B", "Minor discrepancies detected (e.g. date or slight spelling variance). Manual review suggested."
    elif score >= 40.0:
        return "SUSPICIOUS", "#EF4444", "Significant mismatch in critical fields (e.g. Candidate Name or Certificate ID mismatch)."
    else:
        return "FAILED", "#DC2626", "Failed verification or record not found in official registry."


# Global Singleton Instance for easy importing across modules
_engine = SymPyScoringEngine()


def calculate_certificate_score(
    name_match: float,
    certificate_id_match: float,
    course_match: float,
    organization_match: float,
    date_match: float
) -> Dict[str, Any]:
    """
    Convenience function that calculates the SymPy score.
    """
    return _engine.evaluate_score(
        name_match=name_match,
        certificate_id_match=certificate_id_match,
        course_match=course_match,
        organization_match=organization_match,
        date_match=date_match
    )


def get_symbolic_formula() -> str:
    """Returns string representation of SymPy formula."""
    return str(_engine.score_expression)


def get_latex_formula() -> str:
    """Returns LaTeX representation for frontend rendering."""
    return sp.latex(_engine.score_expression)


def get_weight_derivatives() -> Dict[str, str]:
    """Returns sensitivity gradient of the scoring equation."""
    return {k: str(v) for k, v in _engine.derivatives.items()}

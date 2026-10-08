"""
VERIRESUME - Mock Official Certificate Verifier
Provides an official verification registry simulation for offline testing and viva demonstration.
Clearly tags all outputs as DEMO / MOCK VERIFICATION SOURCE.
"""

from typing import Dict, Any, Optional
from .base_verifier import CertificateVerifier, VerificationResult
from backend.comparison_engine import compare_certificate_data, normalize_id
from mathematics.authenticity_model import calculate_certificate_score


# Official Registry Database (Simulated Authority Records)
MOCK_OFFICIAL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "CERT1001": {
        "certificate_id": "CERT1001",
        "candidate_name": "Alice Johnson",
        "certificate_name": "Python Programming",
        "issuing_organization": "Demo Institute",
        "issue_date": "2024-05-15",
        "status": "VALID",
        "accredited": True,
        "registry_source": "Demo Institute Official Credential Registry",
    },
    "CERT1002": {
        "certificate_id": "CERT1002",
        "candidate_name": "Bob Smith",
        "certificate_name": "Web Development",
        "issuing_organization": "Demo Institute",
        "issue_date": "2024-06-20",
        "status": "VALID",
        "accredited": True,
        "registry_source": "Demo Institute Official Credential Registry",
    },
    "AWS-SAA-8842": {
        "certificate_id": "AWS-SAA-8842",
        "candidate_name": "Sarah Connor",
        "certificate_name": "AWS Certified Solutions Architect - Associate",
        "issuing_organization": "Amazon Web Services",
        "issue_date": "2024-01-18",
        "status": "VALID",
        "accredited": True,
        "registry_source": "AWS Global Certification Registry",
    },
    "GCP-PDE-3011": {
        "certificate_id": "GCP-PDE-3011",
        "candidate_name": "David Miller",
        "certificate_name": "Google Professional Data Engineer",
        "issuing_organization": "Google Cloud",
        "issue_date": "2023-09-05",
        "status": "VALID",
        "accredited": True,
        "registry_source": "Google Cloud Certified Directory",
    },
    "MS-AZ-900": {
        "certificate_id": "MS-AZ-900",
        "candidate_name": "Emily Watson",
        "certificate_name": "Microsoft Certified: Azure Fundamentals",
        "issuing_organization": "Microsoft",
        "issue_date": "2024-02-14",
        "status": "VALID",
        "accredited": True,
        "registry_source": "Microsoft Learn Credential Registry",
    },
    "COURSERA-ML-441": {
        "certificate_id": "COURSERA-ML-441",
        "candidate_name": "John Doe",
        "certificate_name": "Machine Learning Specialization",
        "issuing_organization": "Coursera",
        "issue_date": "2023-11-10",
        "status": "VALID",
        "accredited": True,
        "registry_source": "Coursera Official Verification API",
    },
    "DEEP-AI-991": {
        "certificate_id": "DEEP-AI-991",
        "candidate_name": "Alice Johnson",
        "certificate_name": "Deep Learning Specialization",
        "issuing_organization": "DeepLearning.AI",
        "issue_date": "2024-03-22",
        "status": "VALID",
        "accredited": True,
        "registry_source": "DeepLearning.AI Verification Service",
    },
    "CS50-HARVARD-2023": {
        "certificate_id": "CS50-HARVARD-2023",
        "candidate_name": "Alice Johnson",
        "certificate_name": "CS50: Introduction to Computer Science",
        "issuing_organization": "Harvard University",
        "issue_date": "2023-12-15",
        "status": "VALID",
        "accredited": True,
        "registry_source": "edX / Harvard Online Verification",
    },
    "KAGGLE-DS-552": {
        "certificate_id": "KAGGLE-DS-552",
        "candidate_name": "Alice Johnson",
        "certificate_name": "Data Science Master Track",
        "issuing_organization": "Kaggle",
        "issue_date": "2024-04-10",
        "status": "VALID",
        "accredited": True,
        "registry_source": "Kaggle Certifications Registry",
    },
    "CERT9999": {
        "certificate_id": "CERT9999",
        "candidate_name": "Fake Candidate",
        "certificate_name": "Python Programming",
        "issuing_organization": "Demo Institute",
        "issue_date": "2022-01-01",
        "status": "REVOKED",
        "accredited": False,
        "registry_source": "Demo Institute Revocation Database",
    },
    "FRAUD-777": {
        "certificate_id": "FRAUD-777",
        "candidate_name": "Imposter John",
        "certificate_name": "Full Stack Web Development",
        "issuing_organization": "Demo Institute",
        "issue_date": "2021-01-01",
        "status": "FORGED_FLAGGED",
        "accredited": False,
        "registry_source": "Academic Integrity Blacklist",
    },
}


class MockCertificateVerifier(CertificateVerifier):
    """
    Simulated official registry verifier for local & offline verification.
    """

    def __init__(self, registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self.registry = registry or MOCK_OFFICIAL_REGISTRY

    def find_official_record(self, cert_id: str) -> Optional[Dict[str, Any]]:
        """Finds record by certificate ID using normalized comparison."""
        norm_target = normalize_id(cert_id)
        if not norm_target:
            return None

        for key, record in self.registry.items():
            if normalize_id(key) == norm_target:
                return record
            if normalize_id(record.get("certificate_id", "")) == norm_target:
                return record
        return None

    def verify(self, certificate: Dict[str, Any]) -> VerificationResult:
        cert_id = certificate.get("certificate_id") or certificate.get("id") or ""
        official_record = self.find_official_record(cert_id)

        source_label = "DEMO / MOCK OFFICIAL VERIFICATION REGISTRY"

        # Case 1: Record found in registry
        if official_record:
            # If the record in official registry is revoked or fraudulent
            if official_record.get("status") in ("REVOKED", "FORGED_FLAGGED", "INVALID"):
                return VerificationResult(
                    status="FAILED",
                    score=0.0,
                    checks={
                        "name_match": False,
                        "certificate_id_match": True,
                        "course_match": False,
                        "organization_match": False,
                        "date_match": False,
                    },
                    official_record=official_record,
                    source=source_label,
                    details=f"Official Record Found but Status is {official_record.get('status')}. Certificate has been revoked/flagged.",
                    breakdown={"name_contribution": 0, "id_contribution": 0, "course_contribution": 0, "org_contribution": 0, "date_contribution": 0}
                )

            # Compare certificate data
            comp_result = compare_certificate_data(certificate, official_record)
            coeffs = comp_result["coefficients"]

            # Calculate SymPy score
            scoring_res = calculate_certificate_score(
                name_match=coeffs["name_match"],
                certificate_id_match=coeffs["certificate_id_match"],
                course_match=coeffs["course_match"],
                organization_match=coeffs["organization_match"],
                date_match=coeffs["date_match"],
            )

            return VerificationResult(
                status=scoring_res["status"],
                score=scoring_res["score"],
                checks=comp_result["flags"],
                official_record=official_record,
                source=source_label,
                details=scoring_res["description"],
                breakdown=scoring_res["breakdown"]
            )

        # Case 2: Record NOT found in mock registry
        # Check if basic certificate metadata is present to compute partial or fallback score
        has_id = bool(cert_id)
        has_org = bool(certificate.get("issuing_organization") or certificate.get("organization"))
        has_name = bool(certificate.get("certificate_name") or certificate.get("name"))

        if has_id and has_org and has_name:
            return VerificationResult(
                status="UNABLE_TO_VERIFY",
                score=30.0,
                checks={
                    "name_match": False,
                    "certificate_id_match": False,
                    "course_match": True,
                    "organization_match": True,
                    "date_match": False,
                },
                official_record=None,
                source=source_label,
                details=f"Certificate ID '{cert_id}' not found in official verification registry. Issuer database unreachable or credentials unindexed.",
                breakdown={"name_contribution": 0, "id_contribution": 0, "course_contribution": 20, "org_contribution": 10, "date_contribution": 0}
            )

        return VerificationResult(
            status="UNABLE_TO_VERIFY",
            score=0.0,
            checks={
                "name_match": False,
                "certificate_id_match": False,
                "course_match": False,
                "organization_match": False,
                "date_match": False,
            },
            official_record=None,
            source=source_label,
            details="Insufficient certificate data extracted to query verification registries.",
            breakdown={"name_contribution": 0, "id_contribution": 0, "course_contribution": 0, "org_contribution": 0, "date_contribution": 0}
        )

"""
VERIRESUME - Comparison Engine
Compares candidate resume certificate claims against official/mock registry records.
Provides normalized field-level matching and detailed match flags.
"""

import re
from typing import Dict, Any, Tuple
from functional.functional_processing import normalize_string, normalize_certificate_name

# Standard organization synonyms for robust academic matching
ORGANIZATION_SYNONYMS = {
    "aws": "amazon web services",
    "amazon web services": "amazon web services",
    "gcp": "google cloud",
    "google": "google cloud",
    "google cloud platform": "google cloud",
    "google cloud": "google cloud",
    "ms": "microsoft",
    "microsoft": "microsoft",
    "microsoft azure": "microsoft",
    "azure": "microsoft",
    "coursera": "coursera",
    "demo institute": "demo institute",
    "example institute": "demo institute",
    "udemy": "udemy",
    "edx": "edx",
    "cisco": "cisco",
    "oracle": "oracle",
    "stanford": "stanford university",
    "harvard": "harvard university",
    "mit": "mit",
}


def normalize_id(cert_id: str) -> str:
    """Removes spaces, hyphens, and underscores for strict ID matching."""
    if not cert_id:
        return ""
    return re.sub(r'[\s\-_#:]+', '', str(cert_id).strip().upper())


def normalize_org(org: str) -> str:
    """Normalizes organization name and resolves common synonyms."""
    norm = normalize_string(org)
    return ORGANIZATION_SYNONYMS.get(norm, norm)


def compare_names(name1: str, name2: str) -> Tuple[float, bool, str]:
    """
    Compares candidate name from resume against official record.
    Handles 'First Last', 'Last, First', and middle initials.
    """
    n1 = normalize_string(name1)
    n2 = normalize_string(name2)

    if not n1 or not n2:
        return 0.0, False, "Candidate name missing or empty."

    if n1 == n2:
        return 1.0, True, "Exact candidate name match."

    # Split into token sets
    tokens1 = set(re.findall(r'\b\w+\b', n1))
    tokens2 = set(re.findall(r'\b\w+\b', n2))

    if tokens1 == tokens2:
        return 1.0, True, "Name tokens match (reordered or formatted differently)."

    # Check subset (e.g. middle name present in one but not other)
    intersection = tokens1.intersection(tokens2)
    if len(intersection) >= min(len(tokens1), len(tokens2)) and len(intersection) >= 2:
        return 0.9, True, f"High name similarity ({len(intersection)} shared name parts)."

    if len(intersection) >= 1 and (len(tokens1) == 1 or len(tokens2) == 1):
        return 0.5, False, "Partial name overlap."

    return 0.0, False, f"Name mismatch: '{name1}' vs official '{name2}'."


def compare_ids(id1: str, id2: str) -> Tuple[float, bool, str]:
    """Compares certificate identifiers."""
    norm1 = normalize_id(id1)
    norm2 = normalize_id(id2)

    if not norm1 or not norm2:
        return 0.0, False, "Certificate ID missing."

    if norm1 == norm2:
        return 1.0, True, "Exact certificate ID match."

    # Substring / Prefix match
    if norm1 in norm2 or norm2 in norm1:
        return 0.8, True, "Certificate ID matches partially/as prefix."

    return 0.0, False, f"Certificate ID mismatch: '{id1}' vs official '{id2}'."


def compare_courses(course1: str, course2: str) -> Tuple[float, bool, str]:
    """Compares course/certification titles."""
    c1 = normalize_certificate_name(course1)
    c2 = normalize_certificate_name(course2)

    if not c1 or not c2:
        return 0.0, False, "Course title missing."

    if c1 == c2:
        return 1.0, True, "Exact course/certification title match."

    tokens1 = set(re.findall(r'\b\w+\b', c1))
    tokens2 = set(re.findall(r'\b\w+\b', c2))

    common = tokens1.intersection(tokens2)
    total_unique = tokens1.union(tokens2)

    if not total_unique:
        return 0.0, False, "Empty course title."

    jaccard = len(common) / len(total_unique)
    if jaccard >= 0.6:
        return 1.0, True, f"Course title match ({int(jaccard*100)}% token similarity)."
    elif jaccard >= 0.3:
        return 0.7, True, f"Moderate course title similarity ({int(jaccard*100)}%)."

    return 0.0, False, f"Course mismatch: '{course1}' vs official '{course2}'."


def compare_organizations(org1: str, org2: str) -> Tuple[float, bool, str]:
    """Compares issuing organizations."""
    o1 = normalize_org(org1)
    o2 = normalize_org(org2)

    if not o1 or not o2:
        return 0.5, True, "Organization unspecified in one of the records."

    if o1 == o2:
        return 1.0, True, "Issuing organization match."

    # Check substring (e.g. 'Amazon' in 'Amazon Web Services')
    if o1 in o2 or o2 in o1:
        return 1.0, True, "Issuing organization synonym/abbreviation match."

    return 0.0, False, f"Organization mismatch: '{org1}' vs official '{org2}'."


def compare_dates(date1: str, date2: str) -> Tuple[float, bool, str]:
    """Compares issue dates."""
    d1 = normalize_string(date1)
    d2 = normalize_string(date2)

    if not d1:
        # Date wasn't mentioned on resume, award partial score
        return 0.8, True, "Date omitted on resume (non-critical)."

    if not d2:
        return 0.8, True, "Official registry has no issue date recorded."

    # Extract year (4 digits)
    y1 = re.search(r'\b(20\d{2}|19\d{2})\b', d1)
    y2 = re.search(r'\b(20\d{2}|19\d{2})\b', d2)

    if y1 and y2:
        if y1.group(1) == y2.group(1):
            return 1.0, True, f"Issue year matches ({y1.group(1)})."
        else:
            return 0.0, False, f"Issue year discrepancy: {y1.group(1)} vs official {y2.group(1)}."

    # Direct string match
    if d1 in d2 or d2 in d1:
        return 1.0, True, "Issue date matches."

    return 0.5, True, "Date format differs slightly."


def compare_certificate_data(
    claimed_cert: Dict[str, Any],
    official_record: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes full multi-field comparison between claimed certificate and official record.
    Returns normalized match flags, coefficients, and explanations.
    """
    name_score, name_match, name_msg = compare_names(
        claimed_cert.get("candidate_name") or claimed_cert.get("candidate") or "",
        official_record.get("candidate_name") or official_record.get("candidate") or ""
    )

    id_score, id_match, id_msg = compare_ids(
        claimed_cert.get("certificate_id") or claimed_cert.get("id") or "",
        official_record.get("certificate_id") or official_record.get("id") or ""
    )

    course_score, course_match, course_msg = compare_courses(
        claimed_cert.get("certificate_name") or claimed_cert.get("course_name") or claimed_cert.get("name") or "",
        official_record.get("certificate_name") or official_record.get("course_name") or official_record.get("name") or ""
    )

    org_score, org_match, org_msg = compare_organizations(
        claimed_cert.get("issuing_organization") or claimed_cert.get("organization") or "",
        official_record.get("issuing_organization") or official_record.get("organization") or ""
    )

    date_score, date_match, date_msg = compare_dates(
        claimed_cert.get("issue_date") or claimed_cert.get("date") or "",
        official_record.get("issue_date") or official_record.get("date") or ""
    )

    return {
        "coefficients": {
            "name_match": name_score,
            "certificate_id_match": id_score,
            "course_match": course_score,
            "organization_match": org_score,
            "date_match": date_score,
        },
        "flags": {
            "name_match": name_match,
            "certificate_id_match": id_match,
            "course_match": course_match,
            "organization_match": org_match,
            "date_match": date_match,
        },
        "explanations": {
            "name": name_msg,
            "certificate_id": id_msg,
            "course": course_msg,
            "organization": org_msg,
            "date": date_msg,
        }
    }

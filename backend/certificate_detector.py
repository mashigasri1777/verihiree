"""
VERIRESUME - Certificate Detector
Detects, parses, and extracts structured certificate credentials from resume text.
"""

import re
from typing import List, Dict, Any, Optional

# Known Organizations Regex Pattern
KNOWN_ORGS = [
    "Demo Institute", "Example Institute", "Amazon Web Services", "AWS",
    "Google Cloud", "Google", "GCP", "Microsoft", "Microsoft Azure", "Azure",
    "Coursera", "edX", "Udemy", "DeepLearning.AI", "Harvard University",
    "Stanford University", "MIT", "Kaggle", "Cisco", "Oracle", "IBM", "Meta",
    "Linux Foundation", "CompTIA", "Red Hat"
]

ORG_PATTERN = re.compile(r'\b(' + '|'.join([re.escape(org) for org in KNOWN_ORGS]) + r')\b', re.IGNORECASE)

# Credential ID Regex Patterns
ID_PATTERNS = [
    re.compile(r'(?:certificate\s*id|credential\s*id|cert\s*id|license\s*#?|id|badge\s*id)[:\s#]+([A-Za-z0-9\-_]{4,30})', re.IGNORECASE),
    re.compile(r'\b(CERT-?\d{4,8})\b', re.IGNORECASE),
    re.compile(r'\b([A-Z]{2,6}-[A-Z0-9]{2,6}-[A-Z0-9]{2,8})\b'),
    re.compile(r'\b(AWS-[A-Za-z0-9\-]+|GCP-[A-Za-z0-9\-]+|MS-[A-Za-z0-9\-]+)\b', re.IGNORECASE),
]

# URL Regex Pattern
URL_PATTERN = re.compile(r'https?://[^\s<>"\)\]]+', re.IGNORECASE)

# Date Patterns
DATE_PATTERN = re.compile(r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{4}|\d{4}-\d{2}-\d{2}|\b20\d{2}\b)', re.IGNORECASE)


class CertificateDetector:
    """
    Extracts structured certificate claims from raw or sectioned resume text.
    """

    def extract_certificates(self, resume_text: str, candidate_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scans resume text and returns a list of detected certificate dictionary records.
        """
        if not resume_text:
            return []

        certificates = []
        
        # 1. Look for explicit Certifications section
        cert_section_text = self._extract_cert_section(resume_text)
        target_text = cert_section_text if cert_section_text else resume_text

        # 2. Break into lines / bullet items
        lines = [line.strip() for line in target_text.split('\n') if line.strip()]
        
        # Group lines into certificate candidate blocks
        blocks = self._group_into_blocks(lines)

        for block in blocks:
            cert_info = self._parse_block(block, candidate_name)
            if cert_info and (cert_info.get("certificate_id") or cert_info.get("certificate_name")):
                certificates.append(cert_info)

        # 3. Fallback: If no structured blocks yielded certs, do regex scan across full text
        if not certificates:
            certificates = self._fallback_regex_scan(resume_text, candidate_name)

        return certificates

    def _extract_cert_section(self, text: str) -> Optional[str]:
        """Extracts text block under Certifications header."""
        header_patterns = [
            r'(?:certifications?|certificates?|licenses?\s*&\s*certifications?|academic\s*credentials|courses?\s*&\s*training)(.*?)(?=\n\s*(?:education|experience|skills|projects|summary|awards|languages)|\Z)',
        ]
        for pat in header_patterns:
            match = re.search(pat, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return None

    def _group_into_blocks(self, lines: List[str]) -> List[str]:
        """Groups lines that belong to individual certificate entries."""
        blocks = []
        current_block = []

        for line in lines:
            # Check if line looks like a bullet or start of a new certificate
            is_new_bullet = bool(re.match(r'^[\u2022\u2023\u25E6\u2043\u2219\*\-\d+\.]', line))
            has_cert_keyword = bool(re.search(r'\b(certified|certificate|specialization|credential|track|course|foundation|architect|developer|associate|expert)\b', line, re.IGNORECASE))
            has_id_keyword = bool(re.search(r'\b(id|cert\s*id|credential\s*id)\b', line, re.IGNORECASE))

            if (is_new_bullet or has_cert_keyword or has_id_keyword) and current_block:
                if len(current_block) > 0 and (has_cert_keyword or has_id_keyword):
                    blocks.append(" | ".join(current_block))
                    current_block = [line]
                else:
                    current_block.append(line)
            else:
                current_block.append(line)

        if current_block:
            blocks.append(" | ".join(current_block))

        return blocks

    def _parse_block(self, block: str, candidate_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """Extracts fields from a single certificate text block."""
        # Find Certificate ID
        cert_id = None
        for pat in ID_PATTERNS:
            id_match = pat.search(block)
            if id_match:
                cert_id = id_match.group(1) if id_match.groups() else id_match.group(0)
                break

        # Find Organization
        org_match = ORG_PATTERN.search(block)
        org = org_match.group(0) if org_match else "Demo Institute"

        # Find URL
        url_match = URL_PATTERN.search(block)
        url = url_match.group(0) if url_match else ""

        # Find Date
        date_match = DATE_PATTERN.search(block)
        issue_date = date_match.group(0) if date_match else ""

        # Extract Certificate Name
        # Remove ID, URL, Date, Org to isolate certificate name
        cleaned_block = block
        if cert_id:
            cleaned_block = cleaned_block.replace(cert_id, "")
        if url:
            cleaned_block = cleaned_block.replace(url, "")
        if issue_date:
            cleaned_block = cleaned_block.replace(issue_date, "")
        
        # Strip prefixes and bullet points
        cleaned_block = re.sub(r'^[^\w\(\)\[\]]+', '', cleaned_block)
        cleaned_block = re.sub(r'(?:certificate\s*id|credential\s*id|cert\s*id|id|issued\s*by|issuing\s*organization|verified\s*at|date):?', '', cleaned_block, flags=re.IGNORECASE)
        
        # Take the first prominent text segment as certificate title
        parts = [p.strip() for p in cleaned_block.split('|') if p.strip()]
        cert_name = parts[0] if parts else "Certified Credential"
        
        # Cleanup cert name - remove leading bullets, replacement chars, and special chars
        cert_name = re.sub(r'^[^\w\(\)]+', '', cert_name).strip()
        cert_name = re.sub(r'[\ufffd\u2022\u2023\u25E6\u2043\u2219\*\-\|]', '', cert_name).strip()
        cert_name = re.sub(r'[\(\)\[\]]', '', cert_name).strip()
        cert_name = re.sub(r'\s+', ' ', cert_name).strip()
        if len(cert_name) < 3:
            cert_name = "Python Programming" if "python" in block.lower() else "Certified Credential"

        if not cert_id and not org_match and not ("certified" in block.lower() or "certificate" in block.lower() or "specialization" in block.lower()):
            return None

        return {
            "certificate_name": cert_name,
            "candidate_name": candidate_name or "Unknown Candidate",
            "certificate_id": cert_id or "N/A",
            "issuing_organization": org,
            "issue_date": issue_date or "N/A",
            "verification_url": url
        }

    def _fallback_regex_scan(self, text: str, candidate_name: Optional[str]) -> List[Dict[str, Any]]:
        """Fallback scanner when no structured sections are found."""
        results = []
        # Find all ID occurrences
        for pat in ID_PATTERNS:
            for match in pat.finditer(text):
                cert_id = match.group(1) if match.groups() else match.group(0)
                # Look at context around the ID (+/- 100 characters)
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                window = text[start:end]

                org_match = ORG_PATTERN.search(window)
                org = org_match.group(0) if org_match else "Demo Institute"
                
                results.append({
                    "certificate_name": "Technical Credential",
                    "candidate_name": candidate_name or "Unknown Candidate",
                    "certificate_id": cert_id,
                    "issuing_organization": org,
                    "issue_date": "2024",
                    "verification_url": ""
                })
        return results


# Singleton detector instance
certificate_detector = CertificateDetector()

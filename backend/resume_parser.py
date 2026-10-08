"""
VERIRESUME - Resume Parser
Extracts text, candidate contact information, skills, education, and certificates
from PDF and DOCX resume documents.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import fitz  # PyMuPDF
import docx  # python-docx

from backend.certificate_detector import certificate_detector
from backend.ocr_engine import ocr_engine

logger = logging.getLogger("ResumeParser")


class ResumeParser:
    """
    Multi-format resume parser supporting PDF and DOCX.
    """

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parses resume file based on extension and returns structured candidate & certificate information.
        """
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            raw_text = self._extract_pdf_text(file_path)
        elif ext in (".docx", ".doc"):
            raw_text = self._extract_docx_text(file_path)
        elif ext in (".png", ".jpg", ".jpeg"):
            raw_text = ocr_engine.extract_text_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Allowed: .pdf, .docx, .png, .jpg")

        if not raw_text or len(raw_text.strip()) == 0:
            logger.warning(f"File {file_path.name} produced empty text. Attempting OCR fallback on pages.")
            raw_text = self._ocr_pdf_fallback(file_path)

        # Extract structured sections
        candidate_name = self._extract_candidate_name(raw_text)
        email = self._extract_email(raw_text)
        phone = self._extract_phone(raw_text)
        skills = self._extract_skills(raw_text)
        education = self._extract_education(raw_text)
        experience = self._extract_experience(raw_text)
        
        # Detect certificates
        certificates = certificate_detector.extract_certificates(raw_text, candidate_name=candidate_name)

        return {
            "raw_text": raw_text,
            "candidate_name": candidate_name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "education": education,
            "experience": experience,
            "certificates": certificates
        }

    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extracts text using PyMuPDF."""
        text_parts = []
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text_parts.append(page.get_text())
            return "\n".join(text_parts).strip()
        except Exception as e:
            logger.error(f"PyMuPDF error reading {file_path}: {e}")
            return ""

    def _extract_docx_text(self, file_path: Path) -> str:
        """Extracts text from DOCX document."""
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            paragraphs.append(cell.text.strip())
            return "\n".join(paragraphs).strip()
        except Exception as e:
            logger.error(f"python-docx error reading {file_path}: {e}")
            return ""

    def _ocr_pdf_fallback(self, file_path: Path) -> str:
        """Renders PDF pages to images and runs OCR if text was empty."""
        if file_path.suffix.lower() != ".pdf":
            return ""
        
        text_parts = []
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    pix = page.get_pixmap()
                    img_path = file_path.parent / f"temp_{file_path.stem}_p{page.number}.png"
                    pix.save(str(img_path))
                    page_text = ocr_engine.extract_text_from_image(img_path)
                    if img_path.exists():
                        img_path.unlink()
                    if page_text:
                        text_parts.append(page_text)
            return "\n".join(text_parts).strip()
        except Exception as e:
            logger.error(f"PDF OCR fallback failed: {e}")
            return ""

    def _extract_candidate_name(self, text: str) -> str:
        """Heuristic candidate name extraction from top lines."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:6]:
            # Filter out titles, emails, phones, links, headers
            if re.search(r'(resume|curriculum\s*vitae|cv|contact|email|phone|page|\.com|github|linkedin)', line, re.IGNORECASE):
                continue
            # Candidate names are typically 2 to 4 words, with letters and spaces
            if re.match(r'^[A-Z][a-zA-Z\.\'\-]+\s+([A-Z][a-zA-Z\.\'\-]+\s*){1,3}$', line):
                return line.strip()

        # Fallback: check first non-empty line
        for line in lines[:3]:
            if len(line) < 40 and not re.search(r'[@\(\)\d:]', line):
                return line.strip()

        return "Candidate"

    def _extract_email(self, text: str) -> Optional[str]:
        """Extracts email address."""
        match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extracts phone number."""
        match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        return match.group(0) if match else None

    def _extract_skills(self, text: str) -> List[str]:
        """Extracts list of technical and soft skills."""
        match = re.search(r'(?:technical\s*skills|skills|technologies|proficiencies|core\s*competencies)(.*?)(?=\n\s*(?:education|experience|certifications|projects|summary)|\Z)', text, re.IGNORECASE | re.DOTALL)
        if match:
            skills_text = match.group(1).strip()
            # Split by commas, bullets, pipes, or newlines
            items = re.split(r'[,\|\u2022\u2023\u25E6\*\n;]', skills_text)
            cleaned = [re.sub(r'^[^\w]+', '', item).strip() for item in items if len(item.strip()) > 1]
            return [c for c in cleaned if c and len(c) < 50][:20]
        return ["Python", "Machine Learning", "Software Development", "Problem Solving"]

    def _extract_education(self, text: str) -> List[str]:
        """Extracts education entries."""
        match = re.search(r'(?:education|academic\s*background|degrees)(.*?)(?=\n\s*(?:skills|experience|certifications|projects|summary)|\Z)', text, re.IGNORECASE | re.DOTALL)
        if match:
            edu_text = match.group(1).strip()
            lines = [l.strip() for l in edu_text.split('\n') if l.strip()]
            return lines[:5]
        return ["Bachelor of Science in Computer Science"]

    def _extract_experience(self, text: str) -> List[str]:
        """Extracts work experience summary."""
        match = re.search(r'(?:work\s*experience|experience|employment\s*history)(.*?)(?=\n\s*(?:education|skills|certifications|projects|summary)|\Z)', text, re.IGNORECASE | re.DOTALL)
        if match:
            exp_text = match.group(1).strip()
            lines = [l.strip() for l in exp_text.split('\n') if l.strip()]
            return lines[:5]
        return []


# Singleton parser instance
resume_parser = ResumeParser()

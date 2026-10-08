"""
VERIRESUME - OCR Engine
Performs optical character recognition on scanned certificates and image documents.
Handles environments without Tesseract gracefully without throwing uncaught exceptions.
"""

import logging
from typing import Optional
from pathlib import Path
from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

logger = logging.getLogger("OCREngine")


class OCREngine:
    """
    OCR extraction engine with automatic fallback handling.
    """

    def __init__(self):
        self.is_ready = False
        if PYTESSERACT_AVAILABLE:
            try:
                # Verify pytesseract works
                _ = pytesseract.get_tesseract_version()
                self.is_ready = True
                logger.info("Tesseract OCR is available and initialized.")
            except Exception as e:
                logger.warning(f"Tesseract binary not found on system path ({e}). Falling back to native text extraction.")
                self.is_ready = False
        else:
            logger.info("pytesseract library not available.")

    def extract_text_from_image(self, image_path: Path) -> str:
        """Extracts text from an image file."""
        if not self.is_ready:
            return ""

        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return ""

    def extract_text_from_pil(self, pil_image: Image.Image) -> str:
        """Extracts text from a PIL Image object."""
        if not self.is_ready:
            return ""

        try:
            text = pytesseract.image_to_string(pil_image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed on PIL image: {e}")
            return ""


# Singleton OCR Engine instance
ocr_engine = OCREngine()

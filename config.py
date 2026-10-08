"""
VeriHire AI – Configuration Module
==================================
Manages system settings, brand constants, file paths, upload thresholds,
and verification server parameters.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"
SAMPLE_DIR = BASE_DIR / "sample_data"

# Ensure essential directories exist
for directory in (DATA_DIR, UPLOADS_DIR, REPORTS_DIR, LOGS_DIR, SAMPLE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# Application Branding
APP_NAME = "VeriHire AI"
APP_SYSTEM_TITLE = "Resume & Certificate Verification System"
APP_TAGLINE = "Verify Talent. Hire With Confidence."
APP_SUBTITLE = "AI-powered resume screening and certificate verification for smarter, safer recruitment."

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'verihire.db'}")

# Socket Communication Configuration
SOCKET_HOST = os.getenv("SOCKET_HOST", "127.0.0.1")
SOCKET_PORT = int(os.getenv("SOCKET_PORT", "9099"))
SOCKET_TIMEOUT = float(os.getenv("SOCKET_TIMEOUT", "5.0"))
SOCKET_BUFFER_SIZE = int(os.getenv("SOCKET_BUFFER_SIZE", "65536"))

# Web Server Configuration
WEB_HOST = os.getenv("WEB_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))

# Demo Mode
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

# Upload Limits
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "15"))
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"}

# Multiprocessing Configuration
DEFAULT_WORKER_PROCESSES = int(os.getenv("VERIFIER_PROCESSES", "4"))

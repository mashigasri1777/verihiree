"""
VeriHire AI – Web Application Server Runner
Starts Uvicorn serving the recruiter web platform on http://127.0.0.1:8000.
"""

import sys
from pathlib import Path
import uvicorn

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config

if __name__ == "__main__":
    print("=" * 70)
    print(" Starting VeriHire AI – Resume & Certificate Verification System")
    print(f" Web Application URL: http://{config.WEB_HOST}:{config.WEB_PORT}")
    print(" Tagline: 'Verify Talent. Hire With Confidence.'")
    print("=" * 70)
    uvicorn.run("main:app", host=config.WEB_HOST, port=config.WEB_PORT, reload=False)

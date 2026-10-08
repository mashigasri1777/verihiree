"""
VERIRESUME - FastAPI Web Server Runner
Starts Uvicorn serving the web dashboard on http://127.0.0.1:8000.
"""

import sys
from pathlib import Path
import uvicorn

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config

if __name__ == "__main__":
    print("=" * 60)
    print(" Starting VERIRESUME FastAPI Web Dashboard")
    print(f" Access URL: http://{config.WEB_HOST}:{config.WEB_PORT}")
    print("=" * 60)
    uvicorn.run("main:app", host=config.WEB_HOST, port=config.WEB_PORT, reload=True)

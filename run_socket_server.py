"""
VERIRESUME - Socket Server Runner
Starts the TCP Socket Verification Server on 127.0.0.1:9099.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from networking.socket_server import run_server

if __name__ == "__main__":
    print("=" * 60)
    print(" Starting VERIRESUME TCP Socket Verification Server")
    print(" Host: 127.0.0.1 | Port: 9099 | Protocol: TCP/JSON Length Header")
    print("=" * 60)
    run_server()

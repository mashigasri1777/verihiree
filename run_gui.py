"""
VERIRESUME - Tkinter Desktop Admin GUI Runner
Launches the Desktop Administration Application.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gui.tkinter_app import run_gui

if __name__ == "__main__":
    print("=" * 60)
    print(" Launching VERIRESUME Tkinter Desktop Admin Panel")
    print("=" * 60)
    run_gui()

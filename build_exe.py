#!/usr/bin/env python3
"""Build script to create keris.exe executable using pybin."""

import subprocess
import sys
import os

# Path to pybin.exe
PYBIN_PATH = r"D:/Bin/!custombins/pybin.exe"

def build_executable():
    """Build the keris.exe executable."""
    # Check if pybin.exe exists
    if not os.path.exists(PYBIN_PATH):
        print(f"\n✗ pybin.exe not found at: {PYBIN_PATH}", file=sys.stderr)
        sys.exit(1)
    
    # pybin command (assuming similar interface to PyInstaller)
    cmd = [
        PYBIN_PATH,
        "--name=keris",
        "--onefile",  # Create a single executable file
        "--console",  # Console application (for REPL)
        "--clean",    # Clean cache before building
        "main.py"
    ]
    
    print("Building keris.exe...")
    print(f"Using: {PYBIN_PATH}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✓ Build successful!")
        print(f"Executable created at: {os.path.join('dist', 'keris.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    build_executable()

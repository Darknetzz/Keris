#!/usr/bin/env python3
"""Build script to create keris executable using PyInstaller."""

import subprocess
import sys
import os

def build_executable():
    """Build the keris executable."""
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=keris",
        "--onefile",  # Create a single executable file
        "--console",  # Console application (for REPL)
        "--clean",    # Clean PyInstaller cache before building
        "main.py"
    ]
    
    print("Building keris...")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✓ Build successful!")
        print(f"Executable created at: {os.path.join('dist', 'keris')}")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("\n✗ PyInstaller not found. Install it with:", file=sys.stderr)
        print("  pip install pyinstaller", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    build_executable()

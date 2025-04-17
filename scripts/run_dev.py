#!/usr/bin/env python
"""
Development server script with auto-reload enabled.
This script is meant to be used during development to automatically reload the server
when code changes are detected.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.main import run_server

if __name__ == "__main__":
    # Enable auto-reload and set reload directories
    run_server(
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 
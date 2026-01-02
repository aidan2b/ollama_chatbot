#!/usr/bin/env python3
"""Entry point script for the chatbot application."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from chatbot.app import main
from chatbot.utils.logging import setup_logging

if __name__ == "__main__":
    setup_logging()
    main()

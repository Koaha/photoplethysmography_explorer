#!/usr/bin/env python3
"""
Simple test runner for the PPG analysis tool.

This script runs all tests from the root directory.
"""

import sys
from pathlib import Path

# Add the tests directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "tests"))

if __name__ == "__main__":
    from run_tests import main
    sys.exit(main())

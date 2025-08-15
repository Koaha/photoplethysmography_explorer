#!/usr/bin/env python3
"""
Local development helper script for linting and formatting.

This script helps developers run the same checks locally that the CI/CD pipeline runs.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Run all linting and formatting checks."""
    print("🚀 Running local development checks...\n")
    
    # Check if we're in the right directory
    if not Path("src").exists() or not Path("tests").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Run checks
    checks = [
        ("flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503,W291,W293,E501,F401,F841,E722,W605,E731,F403,F405,E402,C901", "Flake8 linting"),
        ("black --check src/ tests/", "Black formatting check"),
        ("isort --check-only src/ tests/", "Import sorting check"),
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All checks passed! Your code is ready for commit.")
        sys.exit(0)
    else:
        print("⚠️  Some checks failed. Please fix the issues before committing.")
        sys.exit(1)


if __name__ == "__main__":
    main()

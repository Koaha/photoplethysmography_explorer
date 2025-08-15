#!/usr/bin/env python3
"""
Script to automatically fix import ordering issues across all Python files.

This script uses isort to fix import ordering and black to fix formatting.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description, check_only=False):
    """Run a command and handle errors."""
    print(f"🔍 {description}...")
    try:
        if check_only:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ {description} passed")
            return True
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ {description} completed")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Fix import ordering and formatting issues."""
    print("🚀 Fixing import ordering and formatting issues...\n")
    
    # Check if we're in the right directory
    if not Path("src").exists() or not Path("tests").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # First, check current status
    print("📋 Checking current status...")
    checks = [
        ("isort --check-only src/ tests/", "Import sorting check"),
        ("black --check src/ tests/", "Black formatting check"),
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description, check_only=True):
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All checks passed! No fixes needed.")
        return
    
    # Fix the issues
    print("🔧 Fixing issues...")
    fixes = [
        ("isort src/ tests/", "Fixing import sorting"),
        ("black src/ tests/", "Fixing code formatting"),
    ]
    
    for command, description in fixes:
        if not run_command(command, description):
            print(f"❌ Failed to {description.lower()}")
            sys.exit(1)
        print()
    
    # Verify fixes
    print("🔍 Verifying fixes...")
    for command, description in checks:
        if not run_command(command, description, check_only=True):
            print(f"❌ {description} still failing after fixes")
            sys.exit(1)
        print()
    
    print("🎉 All issues have been fixed successfully!")


if __name__ == "__main__":
    main()

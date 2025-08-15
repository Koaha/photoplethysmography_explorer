#!/usr/bin/env python3
"""
Installation script for PPG Analysis Tool dependencies.
This script installs the required packages for the refactored code.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error output: {e.stderr}")
        return False


def main():
    """Main installation function."""
    print("🚀 PPG Analysis Tool - Dependency Installation")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  No virtual environment detected. Consider creating one:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print()
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("❌ Failed to upgrade pip. Please check your Python installation.")
        return False
    
    # Install core dependencies
    dependencies = [
        "dash>=2.0.0",
        "plotly>=5.0.0", 
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0"
    ]
    
    print("\n📦 Installing core dependencies...")
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"❌ Failed to install {dep}")
            return False
    
    # Install Pydantic dependencies
    print("\n🔧 Installing configuration dependencies...")
    pydantic_deps = [
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0"
    ]
    
    for dep in pydantic_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"❌ Failed to install {dep}")
            return False
    
    # Install development dependencies (optional)
    print("\n🛠️  Installing development dependencies (optional)...")
    dev_deps = [
        "pytest>=6.0.0",
        "pytest-cov>=3.0.0",
        "black>=22.0.0",
        "isort>=5.0.0",
        "flake8>=4.0.0"
    ]
    
    for dep in dev_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️  Failed to install {dep} (optional, continuing...)")
    
    print("\n🎉 Installation completed!")
    print("\n📋 Next steps:")
    print("1. Create a .env file from env.example:")
    print("   cp env.example .env")
    print("2. Edit .env with your preferred settings")
    print("3. Run the application:")
    print("   python main.py")
    print("\n🧪 To run tests:")
    print("   python -m pytest tests/")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

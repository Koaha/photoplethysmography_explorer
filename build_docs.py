#!/usr/bin/env python3
"""
Documentation build script for PPG Analysis Tool
Works on both Windows and Unix-like systems
"""

import os
import sys
import subprocess
from pathlib import Path

def build_docs():
    """Build the documentation using Sphinx"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    docs_dir = project_root / "docs"
    
    if not docs_dir.exists():
        print("❌ Error: docs/ directory not found!")
        return False
    
    # Change to docs directory
    os.chdir(docs_dir)
    
    try:
        # Try to import sphinx
        import sphinx
        print(f"✅ Using Sphinx version: {sphinx.__version__}")
        
        # Build the documentation
        print("🔨 Building documentation...")
        
        # Use sphinx-build command if available
        try:
            result = subprocess.run([
                sys.executable, "-m", "sphinx.cmd.build",
                "-b", "html",
                ".",
                "_build/html"
            ], capture_output=True, text=True, check=True)
            
            print("✅ Documentation built successfully!")
            print(f"📁 Output location: {docs_dir / '_build' / 'html' / 'index.html'}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error building documentation: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False
            
    except ImportError:
        print("❌ Error: Sphinx not found!")
        print("Please install it with: pip install -r requirements-dev.txt")
        return False

def main():
    """Main function"""
    print("🚀 PPG Analysis Tool - Documentation Builder")
    print("=" * 50)
    
    success = build_docs()
    
    if success:
        print("\n🎉 Documentation build completed successfully!")
        print("You can now open docs/_build/html/index.html in your browser")
    else:
        print("\n💥 Documentation build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple test script to verify the configuration system works.
Run this to test if the refactored code can be imported and configured.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config_import():
    """Test if configuration can be imported."""
    try:
        print("🔄 Testing configuration import...")
        from config.settings import settings, DEFAULT_FS, DEFAULT_HR_MIN
        print("✅ Configuration imported successfully")
        print(f"   App name: {settings.app_name}")
        print(f"   Default FS: {settings.default_fs}")
        print(f"   Default HR min: {settings.default_hr_min}")
        print(f"   Legacy constants: DEFAULT_FS={DEFAULT_FS}, DEFAULT_HR_MIN={DEFAULT_HR_MIN}")
        return True
    except Exception as e:
        print(f"❌ Configuration import failed: {e}")
        return False

def test_exceptions_import():
    """Test if exceptions can be imported."""
    try:
        print("\n🔄 Testing exceptions import...")
        from utils.exceptions import PPGError, FileNotFoundError, ValidationError
        print("✅ Exceptions imported successfully")
        return True
    except Exception as e:
        print(f"❌ Exceptions import failed: {e}")
        return False

def test_validation_import():
    """Test if validation can be imported."""
    try:
        print("\n🔄 Testing validation import...")
        from utils.validation import validate_sampling_frequency, validate_heart_rate_range
        print("✅ Validation imported successfully")
        return True
    except Exception as e:
        print(f"❌ Validation import failed: {e}")
        return False

def test_file_utils_import():
    """Test if file utilities can be imported."""
    try:
        print("\n🔄 Testing file utilities import...")
        from utils.file_utils import get_auto_file_path, get_default_sample_data_path
        print("✅ File utilities imported successfully")
        return True
    except Exception as e:
        print(f"❌ File utilities import failed: {e}")
        return False

def test_app_import():
    """Test if app can be imported."""
    try:
        print("\n🔄 Testing app import...")
        from app import create_app
        print("✅ App imported successfully")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 PPG Analysis Tool - Configuration Test")
    print("=" * 50)
    
    tests = [
        test_config_import,
        test_exceptions_import,
        test_validation_import,
        test_file_utils_import,
        test_app_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactored code is working correctly.")
        print("\n🚀 You can now run the application with:")
        print("   python main.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\n💡 Try running the installation script:")
        print("   python install_dependencies.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

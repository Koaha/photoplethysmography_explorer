#!/usr/bin/env python3
"""
Test script to verify that the colorlog import fix works.
This script tests the logging configuration without requiring colorlog to be installed.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_logging_import():
    """Test that logging_config can be imported without colorlog."""
    try:
        print("Testing logging_config import...")
        from config.logging_config import setup_logging, get_logger, COLORLOG_AVAILABLE
        print(f"✅ Successfully imported logging_config")
        print(f"   COLORLOG_AVAILABLE: {COLORLOG_AVAILABLE}")
        
        # Test getting a logger
        logger = get_logger("test")
        print(f"✅ Successfully created logger: {logger.name}")
        
        # Test logging setup (without colors to avoid colorlog dependency)
        print("Testing logging setup...")
        setup_logging(enable_colors=False)
        print("✅ Successfully set up logging without colors")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ppg_analysis_import():
    """Test that ppg_analysis can be imported."""
    try:
        print("\nTesting ppg_analysis import...")
        from utils.ppg_analysis import find_ppg_peaks
        print("✅ Successfully imported ppg_analysis")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_callbacks_import():
    """Test that callbacks can be imported."""
    try:
        print("\nTesting callbacks import...")
        from callbacks.data_callbacks import load_data
        print("✅ Successfully imported data_callbacks")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing colorlog import fix...")
    print("=" * 50)
    
    success = True
    
    # Test logging import
    if not test_logging_import():
        success = False
    
    # Test ppg_analysis import
    if not test_ppg_analysis_import():
        success = False
    
    # Test callbacks import
    if not test_callbacks_import():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The colorlog fix is working.")
    else:
        print("💥 Some tests failed. There are still import issues.")
    
    sys.exit(0 if success else 1)

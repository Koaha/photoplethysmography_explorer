#!/usr/bin/env python3
"""
Test runner for the PPG analysis tool.

This script runs all unit tests and provides a summary of results.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_all_tests():
    """Run all tests and return the test suite."""
    # Discover all test files
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()

    # Load tests from each test file
    test_suite = unittest.TestSuite()

    # Configuration tests
    try:
        from tests.test_config import TestConfigSettings

        test_suite.addTests(loader.loadTestsFromTestCase(TestConfigSettings))
        print("✓ Loaded configuration tests")
    except ImportError as e:
        print(f"✗ Failed to load configuration tests: {e}")

    # Utility tests
    try:
        from tests.test_utils import TestSignalProcessing, TestFileUtils

        test_suite.addTests(loader.loadTestsFromTestCase(TestSignalProcessing))
        test_suite.addTests(loader.loadTestsFromTestCase(TestFileUtils))
        print("✓ Loaded utility tests")
    except ImportError as e:
        print(f"✗ Failed to load utility tests: {e}")

    # PPG analysis tests
    try:
        from tests.test_ppg_analysis import TestPPGAnalysis

        test_suite.addTests(loader.loadTestsFromTestCase(TestPPGAnalysis))
        print("✓ Loaded PPG analysis tests")
    except ImportError as e:
        print(f"✗ Failed to load PPG analysis tests: {e}")

    # Callback tests
    try:
        from tests.test_callbacks import TestPlotCallbacks, TestDataCallbacks, TestWindowCallbacks

        test_suite.addTests(loader.loadTestsFromTestCase(TestPlotCallbacks))
        test_suite.addTests(loader.loadTestsFromTestCase(TestDataCallbacks))
        test_suite.addTests(loader.loadTestsFromTestCase(TestWindowCallbacks))
        print("✓ Loaded callback tests")
    except ImportError as e:
        print(f"✗ Failed to load callback tests: {e}")

    # Integration tests
    try:
        from tests.test_integration import TestApplicationIntegration, TestDataValidation

        test_suite.addTests(loader.loadTestsFromTestCase(TestApplicationIntegration))
        test_suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
        print("✓ Loaded integration tests")
    except ImportError as e:
        print(f"✗ Failed to load integration tests: {e}")

    return test_suite


def main():
    """Main test runner function."""
    print("PPG Analysis Tool - Test Suite")
    print("=" * 40)

    # Run tests
    test_suite = run_all_tests()

    if test_suite.countTestCases() == 0:
        print("\nNo tests found!")
        return 1

    print(f"\nRunning {test_suite.countTestCases()} tests...")
    print("-" * 40)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback.split('Exception:')[-1].strip()}")

    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

"""
Unit tests for utility functions.
"""

import unittest
import numpy as np
import tempfile
import os
from pathlib import Path

from src.utils.signal_processing import (
    safe_float,
    safe_int,
    design_base_filter,
    apply_chain,
    estimate_rates_psd,
    quick_snr,
    auto_decimation,
    cross_correlation_lag,
)
from src.utils.file_utils import (
    count_rows_quick,
    get_columns_only,
    parse_uploaded_csv_to_temp,
    read_window,
    get_auto_file_path,
)


class TestSignalProcessing(unittest.TestCase):
    """Test signal processing utility functions."""

    def test_safe_float(self):
        """Test safe float conversion."""
        self.assertEqual(safe_float("3.14", 0.0), 3.14)
        self.assertEqual(safe_float("invalid", 2.5), 2.5)
        self.assertEqual(safe_float(None, 1.0), 1.0)
        self.assertEqual(safe_float(42, 0.0), 42.0)

    def test_safe_int(self):
        """Test safe integer conversion."""
        self.assertEqual(safe_int("42", 0), 42)
        self.assertEqual(safe_int("invalid", 10), 10)
        self.assertEqual(safe_int(None, 5), 5)
        self.assertEqual(safe_int(3.14, 0), 3)

    def test_design_base_filter(self):
        """Test filter design."""
        # Test lowpass filter
        sos = design_base_filter(100.0, "butter", "lowpass", 0.5, 5.0, 2, 1.0, 40.0)
        self.assertEqual(sos.shape[0], 2)  # 2nd order filter

        # Test bandpass filter
        sos = design_base_filter(100.0, "butter", "bandpass", 0.5, 5.0, 2, 1.0, 40.0)
        self.assertEqual(sos.shape[0], 2)

    def test_apply_chain(self):
        """Test signal processing chain."""
        # Create test signal
        t = np.linspace(0, 1, 1000)
        x = np.sin(2 * np.pi * 10 * t) + 0.1 * np.random.randn(1000)

        # Test basic filtering
        y = apply_chain(x, 1000, detrend_mean=True)
        self.assertEqual(len(y), len(x))
        self.assertLess(np.std(y), np.std(x))  # Detrending should reduce variance

        # Test with filter
        sos = design_base_filter(1000.0, "butter", "lowpass", 0.5, 20.0, 2, 1.0, 40.0)
        y = apply_chain(x, 1000, base_sos=sos)
        self.assertEqual(len(y), len(x))

    def test_estimate_rates_psd(self):
        """Test rate estimation from PSD."""
        # Create test signal with known frequency
        t = np.linspace(0, 10, 10000)
        fs = 1000
        # Signal with 1 Hz component (60 bpm)
        x = np.sin(2 * np.pi * 1 * t) + 0.1 * np.random.randn(10000)

        rate = estimate_rates_psd(x, fs, (0.5, 2.0))
        self.assertIsNotNone(rate)
        self.assertGreater(rate, 50)  # Should be around 60 bpm
        self.assertLess(rate, 70)

    def test_quick_snr(self):
        """Test SNR estimation."""
        # High SNR signal
        x_high = np.sin(2 * np.pi * 10 * np.linspace(0, 1, 1000)) + 0.01 * np.random.randn(1000)
        snr_high = quick_snr(x_high)
        self.assertIsNotNone(snr_high)
        self.assertGreater(snr_high, 1.0)

        # Low SNR signal
        x_low = 0.01 * np.sin(2 * np.pi * 10 * np.linspace(0, 1, 1000)) + 0.1 * np.random.randn(
            1000
        )
        snr_low = quick_snr(x_low)
        self.assertIsNotNone(snr_low)
        self.assertLess(snr_low, 1.0)

    def test_auto_decimation(self):
        """Test auto-decimation."""
        n = 100000
        decim = auto_decimation(n, 1, traces=8, cap=10000)
        self.assertGreater(decim, 1)
        self.assertLessEqual(n // decim, 10000)

    def test_cross_correlation_lag(self):
        """Test cross-correlation."""
        # Create test signals
        t = np.linspace(0, 1, 1000)
        x = np.sin(2 * np.pi * 10 * t)
        y = np.roll(x, 50)  # Shifted by 50 samples

        lags, corr, best_lag = cross_correlation_lag(x, y, 1000, max_lag_sec=0.1)
        self.assertIsNotNone(lags)
        self.assertIsNotNone(corr)
        self.assertIsNotNone(best_lag)
        self.assertAlmostEqual(best_lag, 0.05, places=2)  # 50 samples / 1000 Hz = 0.05s


class TestFileUtils(unittest.TestCase):
    """Test file utility functions."""

    def setUp(self):
        """Set up test data."""
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        self.temp_file.write("time,red,ir\n")
        for i in range(1000):
            self.temp_file.write(f"{i/100:.3f},{1000+np.sin(i/10)*100},{800+np.cos(i/10)*80}\n")
        self.temp_file.close()
        self.temp_path = self.temp_file.name

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)

    def test_count_rows_quick(self):
        """Test quick row counting."""
        count = count_rows_quick(self.temp_path)
        self.assertEqual(count, 1001)  # Header + 1000 data rows

    def test_get_columns_only(self):
        """Test column extraction."""
        cols = get_columns_only(self.temp_path)
        self.assertIn("time", cols)
        self.assertIn("red", cols)
        self.assertIn("ir", cols)
        self.assertEqual(len(cols), 3)

    def test_read_window(self):
        """Test window reading."""
        df = read_window(self.temp_path, ["red", "ir"], 100, 200)
        self.assertEqual(len(df), 101)  # 100 to 200 inclusive
        self.assertIn("red", df.columns)
        self.assertIn("ir", df.columns)

    def test_parse_uploaded_csv_to_temp(self):
        """Test CSV parsing from upload."""
        csv_content = "time,red,ir\n0.0,1000,800\n0.01,1001,801\n"
        temp_path = parse_uploaded_csv_to_temp(csv_content, "test.csv")

        try:
            self.assertTrue(os.path.exists(temp_path))
            df = read_window(temp_path, ["red", "ir"], 0, 2)
            self.assertEqual(len(df), 3)  # Header + 2 data rows
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_auto_file_path(self):
        """Test auto file path detection."""
        # Test with existing file
        path = get_auto_file_path("PPG.csv")
        self.assertIsInstance(path, str)

        # Test with non-existing file
        path = get_auto_file_path("nonexistent.csv")
        self.assertIsInstance(path, str)


if __name__ == "__main__":
    unittest.main()

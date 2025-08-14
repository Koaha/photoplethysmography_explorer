"""
Unit tests for configuration settings.
"""

import unittest
from src.config.settings import (
    DEFAULT_FS, DEFAULT_DECIM_USER, MAX_DISPLAY_POINTS,
    DEFAULT_SPEC_WIN_SEC, DEFAULT_SPEC_OVERLAP,
    DEFAULT_HR_MIN, DEFAULT_HR_MAX, DEFAULT_PEAK_PROM_FACTOR,
    APP_TITLE, APP_SUBTITLE, GRID_COLUMNS, GRID_GAP, MAX_WIDTH
)


class TestConfigSettings(unittest.TestCase):
    """Test configuration constants and settings."""
    
    def test_default_fs(self):
        """Test default sampling frequency."""
        self.assertEqual(DEFAULT_FS, 100.0)
        self.assertIsInstance(DEFAULT_FS, float)
    
    def test_default_decim_user(self):
        """Test default decimation factor."""
        self.assertEqual(DEFAULT_DECIM_USER, 1)
        self.assertIsInstance(DEFAULT_DECIM_USER, int)
    
    def test_max_display_points(self):
        """Test maximum display points."""
        self.assertEqual(MAX_DISPLAY_POINTS, 300_000)
        self.assertIsInstance(MAX_DISPLAY_POINTS, int)
    
    def test_default_spec_win_sec(self):
        """Test default spectrogram window size."""
        self.assertEqual(DEFAULT_SPEC_WIN_SEC, 2.0)
        self.assertIsInstance(DEFAULT_SPEC_WIN_SEC, float)
    
    def test_default_spec_overlap(self):
        """Test default spectrogram overlap."""
        self.assertEqual(DEFAULT_SPEC_OVERLAP, 0.5)
        self.assertIsInstance(DEFAULT_SPEC_OVERLAP, float)
    
    def test_default_hr_min(self):
        """Test default HR minimum."""
        self.assertEqual(DEFAULT_HR_MIN, 40)
        self.assertIsInstance(DEFAULT_HR_MIN, int)
    
    def test_default_hr_max(self):
        """Test default HR maximum."""
        self.assertEqual(DEFAULT_HR_MAX, 180)
        self.assertIsInstance(DEFAULT_HR_MAX, int)
    
    def test_default_peak_prom_factor(self):
        """Test default peak prominence factor."""
        self.assertEqual(DEFAULT_PEAK_PROM_FACTOR, 0.5)
        self.assertIsInstance(DEFAULT_PEAK_PROM_FACTOR, float)
    
    def test_app_title(self):
        """Test application title."""
        self.assertIn("PPG Filter Lab", APP_TITLE)
        self.assertIsInstance(APP_TITLE, str)
    
    def test_app_subtitle(self):
        """Test application subtitle."""
        self.assertIn("Load CSV", APP_SUBTITLE)
        self.assertIsInstance(APP_SUBTITLE, str)
    
    def test_layout_settings(self):
        """Test layout configuration."""
        self.assertIsInstance(GRID_COLUMNS, str)
        self.assertIsInstance(GRID_GAP, str)
        self.assertIsInstance(MAX_WIDTH, str)


if __name__ == "__main__":
    unittest.main()

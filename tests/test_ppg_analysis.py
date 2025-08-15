"""
Unit tests for PPG analysis functions.
"""

import unittest
import numpy as np
from src.utils.ppg_analysis import (
    robust_absorbance,
    beats_from_peaks,
    beat_ac_dc,
    r_series_spo2,
    avg_beat,
    ms_coherence,
    estimate_spo2,
    compute_hr_trend,
    sdppg,
)


class TestPPGAnalysis(unittest.TestCase):
    """Test PPG analysis functions."""

    def test_robust_absorbance(self):
        """Test robust absorbance calculation."""
        # Test with positive values
        x = np.array([100, 200, 300, 400, 500])
        a = robust_absorbance(x)
        self.assertEqual(len(a), len(x))
        self.assertTrue(np.all(np.isfinite(a)))

        # Test with zeros (should handle gracefully)
        x_zero = np.array([0, 100, 200])
        a_zero = robust_absorbance(x_zero)
        self.assertEqual(len(a_zero), len(x_zero))
        self.assertTrue(np.all(np.isfinite(a_zero)))

    def test_beats_from_peaks(self):
        """Test beat segmentation from peaks."""
        # Create test signal with known peaks
        fs = 100
        t_peaks = np.array([0.5, 1.5, 2.5, 3.5])  # 1 second intervals

        beats = beats_from_peaks(np.random.randn(400), fs, t_peaks)
        self.assertEqual(len(beats), len(t_peaks))

        # Each beat should have (start, peak, end) indices
        for beat in beats:
            self.assertEqual(len(beat), 3)
            start, peak, end = beat
            self.assertLessEqual(start, peak)
            self.assertLessEqual(peak, end)

    def test_beat_ac_dc(self):
        """Test beat AC/DC analysis."""
        # Create test data
        fs = 100
        signal_raw = 1000 + 100 * np.sin(2 * np.pi * 1 * np.linspace(0, 4, 400))
        signal_ac = 100 * np.sin(2 * np.pi * 1 * np.linspace(0, 4, 400))
        beats = [(50, 100, 150), (250, 300, 350)]

        t_mid, ac, dc = beat_ac_dc(signal_raw, signal_ac, beats, fs)
        self.assertEqual(len(t_mid), len(beats))
        self.assertEqual(len(ac), len(beats))
        self.assertEqual(len(dc), len(beats))

        # AC should be positive (peak-to-trough)
        self.assertTrue(np.all(ac > 0))
        # DC should be around 1000
        self.assertTrue(np.all(dc > 900))

    def test_r_series_spo2(self):
        """Test R-ratio and SpO2 calculation."""
        # Create test data
        fs = 100
        red_raw = 1000 + 100 * np.sin(2 * np.pi * 1 * np.linspace(0, 2, 200))
        ir_raw = 800 + 80 * np.cos(2 * np.pi * 1 * np.linspace(0, 2, 200))
        red_ac = 100 * np.sin(2 * np.pi * 1 * np.linspace(0, 2, 200))
        ir_ac = 80 * np.cos(2 * np.pi * 1 * np.linspace(0, 2, 200))
        t_peaks = np.array([0.5, 1.5])

        tB, R, spo2 = r_series_spo2(red_raw, ir_raw, red_ac, ir_ac, t_peaks, fs)

        if len(tB) > 0:
            self.assertEqual(len(tB), len(R))
            self.assertEqual(len(R), len(spo2))
            # R should be positive
            self.assertTrue(np.all(R > 0))
            # SpO2 should be reasonable (80-100%)
            self.assertTrue(np.all((spo2 >= 80) & (spo2 <= 100)))

    def test_avg_beat(self):
        """Test ensemble-averaged beat calculation."""
        # Create test signal with peaks
        fs = 100
        signal = np.sin(2 * np.pi * 1 * np.linspace(0, 4, 400))
        t_peaks = np.array([0.5, 1.5, 2.5, 3.5])

        t_rel, mean, std = avg_beat(signal, t_peaks, fs, width_s=1.0, out_len=100)

        if len(t_rel) > 0:
            self.assertEqual(len(t_rel), 100)
            self.assertEqual(len(mean), 100)
            self.assertEqual(len(std), 100)
            # Time should be centered around 0
            self.assertAlmostEqual(t_rel[0], -0.5, places=1)
            self.assertAlmostEqual(t_rel[-1], 0.5, places=1)

    def test_ms_coherence(self):
        """Test magnitude-squared coherence."""
        # Create test signals
        fs = 100
        t = np.linspace(0, 10, 1000)
        # Correlated signals
        x = np.sin(2 * np.pi * 2 * t) + 0.1 * np.random.randn(1000)
        y = np.sin(2 * np.pi * 2 * t + np.pi / 4) + 0.1 * np.random.randn(1000)

        f, C = ms_coherence(x, y, fs)
        self.assertEqual(len(f), len(C))
        # Coherence should be between 0 and 1
        self.assertTrue(np.all((C >= 0) & (C <= 1)))

    def test_estimate_spo2(self):
        """Test SpO2 estimation."""
        # Create test data
        red_raw = np.full(1000, 1000)
        ir_raw = np.full(1000, 800)
        red_ac = 100 * np.sin(2 * np.pi * 1 * np.linspace(0, 10, 1000))
        ir_ac = 80 * np.cos(2 * np.pi * 1 * np.linspace(0, 10, 1000))

        spo2, R, PI = estimate_spo2(red_raw, ir_raw, red_ac, ir_ac)

        if spo2 is not None:
            self.assertIsInstance(spo2, float)
            self.assertIsInstance(R, float)
            self.assertIsInstance(PI, float)
            # SpO2 should be reasonable
            self.assertGreaterEqual(spo2, 80)
            self.assertLessEqual(spo2, 100)
            # R should be positive
            self.assertGreater(R, 0)
            # PI should be positive
            self.assertGreater(PI, 0)

    def test_compute_hr_trend(self):
        """Test heart rate trend computation."""
        # Create test signal with known frequency
        fs = 100
        t = np.linspace(0, 10, 1000)
        # Signal with 1.2 Hz component (72 bpm)
        signal = np.sin(2 * np.pi * 1.2 * t) + 0.1 * np.random.randn(1000)

        t_peaks, ibis, (hr_t, hr_bpm) = compute_hr_trend(signal, fs, hr_min=40, hr_max=180)

        if len(hr_t) > 0:
            self.assertEqual(len(hr_t), len(hr_bpm))
            # HR should be around 72 bpm
            self.assertTrue(np.all((hr_bpm >= 60) & (hr_bpm <= 90)))
            # IBI should be reasonable (0.5-2 seconds)
            if len(ibis) > 0:
                self.assertTrue(np.all((ibis >= 0.5) & (ibis <= 2.0)))

    def test_sdppg(self):
        """Test second derivative PPG."""
        # Create test signal
        t = np.linspace(0, 1, 1000)
        x = np.sin(2 * np.pi * 10 * t)

        sd = sdppg(x)
        self.assertEqual(len(sd), len(x))
        # Second derivative should have more zero crossings
        zero_crossings_orig = np.sum(np.diff(np.sign(x)) != 0)
        zero_crossings_sd = np.sum(np.diff(np.sign(sd)) != 0)
        self.assertGreaterEqual(zero_crossings_sd, zero_crossings_orig)


if __name__ == "__main__":
    unittest.main()

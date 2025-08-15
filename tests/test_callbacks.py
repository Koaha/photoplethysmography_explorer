"""
Unit tests for callback functions.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import dash
import numpy as np
import pandas as pd
from dash import Input, Output

from src.callbacks.data_callbacks import load_data
from src.callbacks.plot_callbacks import (
    _create_blank_figure,
    _generate_dual_source_plots,
    _generate_file_info,
    _generate_frequency_plots,
    _generate_insights,
    _generate_time_domain_plots,
)
from src.callbacks.window_callbacks import handle_slider_change, reflect_window, window_controls


class TestPlotCallbacks(unittest.TestCase):
    """Test plot generation callback functions."""

    def setUp(self):
        """Set up test data."""
        self.template = "plotly"
        self.theme = "light"
        self.fs = 100
        self.n = 1000
        self.t = np.linspace(0, 10, self.n)
        self.red = 1000 + 100 * np.sin(2 * np.pi * 1.2 * self.t)
        self.ir = 800 + 80 * np.cos(2 * np.pi * 1.2 * self.t)
        self.red_ac = 100 * np.sin(2 * np.pi * 1.2 * self.t)
        self.ir_ac = 80 * np.cos(2 * np.pi * 1.2 * self.t)

    def test_create_blank_figure(self):
        """Test blank figure creation."""
        fig = _create_blank_figure(300, self.template, self.theme)
        self.assertEqual(fig.layout.height, 300)
        self.assertEqual(fig.layout.template, self.template)

    def test_generate_time_domain_plots(self):
        """Test time domain plot generation."""
        # Test with time_domain tab
        fig_raw, fig_ac = _generate_time_domain_plots(
            "time_domain",
            self.t,
            self.red,
            self.ir,
            self.red_ac,
            self.ir_ac,
            "RED",
            "IR",
            "butter",
            "bandpass",
            2,
            self.n,
            self.template,
            self.theme,
        )

        self.assertIsNotNone(fig_raw)
        self.assertIsNotNone(fig_ac)
        self.assertEqual(fig_raw.layout.height, 420)
        self.assertEqual(fig_ac.layout.height, 420)

        # Test with different tab
        fig_raw, fig_ac = _generate_time_domain_plots(
            "frequency",
            self.t,
            self.red,
            self.ir,
            self.red_ac,
            self.ir_ac,
            "RED",
            "IR",
            "butter",
            "bandpass",
            2,
            self.n,
            self.template,
            self.theme,
        )

        self.assertEqual(fig_raw.layout.height, 420)
        self.assertEqual(fig_ac.layout.height, 420)

    def test_generate_frequency_plots(self):
        """Test frequency domain plot generation."""
        # Test with frequency tab
        fig_psd, fig_spec = _generate_frequency_plots(
            "frequency",
            self.red_ac,
            self.ir_ac,
            self.fs,
            2.0,
            0.5,
            ["on"],
            self.template,
            self.theme,
        )

        self.assertIsNotNone(fig_psd)
        self.assertIsNotNone(fig_spec)
        self.assertEqual(fig_psd.layout.height, 360)
        self.assertEqual(fig_spec.layout.height, 380)

        # Test with different tab
        fig_psd, fig_spec = _generate_frequency_plots(
            "time_domain",
            self.red_ac,
            self.ir_ac,
            self.fs,
            2.0,
            0.5,
            ["on"],
            self.template,
            self.theme,
        )

        self.assertEqual(fig_psd.layout.height, 360)
        self.assertEqual(fig_spec.layout.height, 380)

    def test_generate_dynamics_plots(self):
        """Test dynamics plot generation."""
        # Test with dynamics tab
        fig_hr, fig_hist, fig_poi, fig_xc = _generate_dynamics_plots(
            "dynamics",
            "hr",
            self.red_ac,
            self.ir_ac,
            self.fs,
            "ir",
            40,
            180,
            0.5,
            ["hr"],
            self.template,
            self.theme,
        )

        self.assertIsNotNone(fig_hr)
        self.assertIsNotNone(fig_hist)
        self.assertIsNotNone(fig_poi)
        self.assertIsNotNone(fig_xc)

        # Test with different tab
        fig_hr, fig_hist, fig_poi, fig_xc = _generate_dynamics_plots(
            "time_domain",
            "hr",
            self.red_ac,
            self.ir_ac,
            self.fs,
            "ir",
            40,
            180,
            0.5,
            ["hr"],
            self.template,
            self.theme,
        )

        self.assertEqual(fig_hr.layout.height, 320)
        self.assertEqual(fig_hist.layout.height, 280)

    def test_generate_dual_source_plots(self):
        """Test dual source plot generation."""
        # Test with dual_source tab
        fig_rtrend, fig_coh, fig_liss, fig_avgbeat, fig_sdppg = _generate_dual_source_plots(
            "dual_source",
            "rtrend",
            self.red,
            self.ir,
            self.red_ac,
            self.ir_ac,
            self.fs,
            self.t,
            self.template,
            self.theme,
        )

        self.assertIsNotNone(fig_rtrend)
        self.assertIsNotNone(fig_coh)
        self.assertIsNotNone(fig_liss)
        self.assertIsNotNone(fig_avgbeat)
        self.assertIsNotNone(fig_sdppg)

        # Test with different tab
        fig_rtrend, fig_coh, fig_liss, fig_avgbeat, fig_sdppg = _generate_dual_source_plots(
            "time_domain",
            "rtrend",
            self.red,
            self.ir,
            self.red_ac,
            self.ir_ac,
            self.fs,
            self.t,
            self.template,
            self.theme,
        )

        self.assertEqual(fig_rtrend.layout.height, 320)
        self.assertEqual(fig_coh.layout.height, 300)

    def test_generate_insights(self):
        """Test insight generation."""
        chips = _generate_insights(self.red, self.ir, self.red_ac, self.ir_ac, None, self.template)

        self.assertIsInstance(chips, list)
        self.assertGreater(len(chips), 0)

        # Test with filter error
        chips_error = _generate_insights(
            self.red, self.ir, self.red_ac, self.ir_ac, "Test error", self.template
        )
        self.assertGreater(len(chips_error), len(chips))

    def test_generate_file_info(self):
        """Test file info generation."""
        info = _generate_file_info(
            "/path/to/test.csv",
            10000,
            100,
            200,
            100,
            self.fs,
            "butter",
            "bandpass",
            2,
            0.5,
            5.0,
            False,
            1,
            "ir",
            40,
            180,
            0.5,
            2.0,
            0.5,
        )

        self.assertIsInstance(info, list)
        self.assertGreater(len(info), 0)


class TestDataCallbacks(unittest.TestCase):
    """Test data loading callbacks."""

    def setUp(self):
        """Set up test data."""
        self.app = dash.Dash(__name__)

    def test_load_data(self):
        """Test data loading callback."""
        # This would require more complex mocking of Dash components
        # For now, just test that the function exists and is callable
        self.assertTrue(callable(load_data))


class TestWindowCallbacks(unittest.TestCase):
    """Test window management callbacks."""

    def setUp(self):
        """Set up test data."""
        self.app = dash.Dash(__name__)

    def test_window_controls(self):
        """Test window controls callback."""
        # This would require more complex mocking of Dash components
        # For now, just test that the function exists and is callable
        self.assertTrue(callable(window_controls))

    def test_reflect_window(self):
        """Test window reflection callback."""
        # This would require more complex mocking of Dash components
        # For now, just test that the function exists and is callable
        self.assertTrue(callable(reflect_window))

    def test_handle_slider_change(self):
        """Test slider change handler callback."""
        # This would require more complex mocking of Dash components
        # For now, just test that the function exists and is callable
        self.assertTrue(callable(handle_slider_change))


if __name__ == "__main__":
    unittest.main()

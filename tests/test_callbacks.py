"""
Unit tests for callback functions.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
from dash import Dash, Input, Output

from src.callbacks.data_callbacks import register_data_callbacks
from src.callbacks.plot_callbacks import InsightGenerator, PlotManager
from src.callbacks.window_callbacks import register_window_callbacks


class TestPlotCallbacks(unittest.TestCase):
    """Test plot generation callback functions."""

    def setUp(self):
        """Set up test data."""
        self.template = "plotly"
        self.theme = "light"
        self.fs = 100
        self.n = int(1000)  # Ensure n is explicitly an integer
        self.t = np.linspace(0, 10, self.n)
        self.red = 1000 + 100 * np.sin(2 * np.pi * 1.2 * self.t)
        self.ir = 800 + 80 * np.cos(2 * np.pi * 1.2 * self.t)
        self.red_ac = 100 * np.sin(2 * np.pi * 1.2 * self.t)
        self.ir_ac = 80 * np.cos(2 * np.pi * 1.2 * self.t)

        # Create instances of the classes
        self.plot_manager = PlotManager(self.template, self.theme)
        self.insight_generator = InsightGenerator()

        # Verify types
        self.assertIsInstance(self.n, int)
        self.assertEqual(self.n, 1000)

    def test_create_blank_figure(self):
        """Test blank figure creation."""
        fig = self.plot_manager.create_blank_figure(300)
        self.assertEqual(fig.layout.height, 300)
        # Check that the template is set (the actual template object, not the string name)
        self.assertIsNotNone(fig.layout.template)

    def test_generate_time_domain_plots(self):
        """Test time domain plot generation."""
        # Ensure n is an integer
        n_value = int(self.n)

        # Test with time_domain tab
        fig_raw, fig_ac = self.plot_manager.create_time_domain_plots(
            self.t,  # t
            self.red,  # red
            self.ir,  # ir
            self.red,  # waveform (using red as waveform for testing)
            self.red_ac,  # red_ac
            self.ir_ac,  # ir_ac
            self.red_ac,  # waveform_ac (using red_ac as waveform_ac for testing)
            "RED",  # red_col
            "IR",  # ir_col
            "WAVEFORM",  # waveform_col
            "butter",  # family
            "bandpass",  # resp
            2,  # order
            n_value,  # n
        )

        self.assertIsNotNone(fig_raw)
        self.assertIsNotNone(fig_ac)
        self.assertEqual(fig_raw.layout.height, 600)  # Updated height
        self.assertEqual(fig_ac.layout.height, 600)  # Updated height

        # Test with different tab
        fig_raw, fig_ac = self.plot_manager.create_time_domain_plots(
            self.t,  # t
            self.red,  # red
            self.ir,  # ir
            self.red,  # waveform (using red as waveform for testing)
            self.red_ac,  # red_ac
            self.ir_ac,  # ir_ac
            self.red_ac,  # waveform_ac (using red_ac as waveform_ac for testing)
            "RED",  # red_col
            "IR",  # ir_col
            "WAVEFORM",  # waveform_col
            "butter",  # family
            "bandpass",  # resp
            2,  # order
            n_value,  # n
        )

        self.assertEqual(fig_raw.layout.height, 600)  # Updated height
        self.assertEqual(fig_ac.layout.height, 600)  # Updated height

    def test_generate_frequency_plots(self):
        """Test frequency domain plot generation."""
        # Test with frequency tab
        fig_psd, fig_spec = self.plot_manager.create_frequency_plots(
            self.red_ac,
            self.ir_ac,
            self.fs,
            2.0,
            0.5,
            ["on"],
        )

        self.assertIsNotNone(fig_psd)
        self.assertIsNotNone(fig_spec)
        self.assertEqual(fig_psd.layout.height, 360)
        self.assertEqual(fig_spec.layout.height, 380)

        # Test with different tab
        fig_psd, fig_spec = self.plot_manager.create_frequency_plots(
            self.red_ac,
            self.ir_ac,
            self.fs,
            2.0,
            0.5,
            ["on"],
        )

        self.assertEqual(fig_psd.layout.height, 360)
        self.assertEqual(fig_spec.layout.height, 380)

    def test_generate_dynamics_plots(self):
        """Test dynamics plot generation."""
        # Test with dynamics tab
        fig_hr, fig_hist, fig_poi, fig_xc = self.plot_manager.create_dynamics_plots(
            self.red_ac,
            self.ir_ac,
            self.fs,
            "ir",
            40,
            180,
            0.5,
            ["hr"],
        )

        self.assertIsNotNone(fig_hr)
        self.assertIsNotNone(fig_hist)
        self.assertIsNotNone(fig_poi)
        self.assertIsNotNone(fig_xc)

        # Test with different tab
        fig_hr, fig_hist, fig_poi, fig_xc = self.plot_manager.create_dynamics_plots(
            self.red_ac,
            self.ir_ac,
            self.fs,
            "ir",
            40,
            180,
            0.5,
            ["hr"],
        )

        self.assertEqual(fig_hr.layout.height, 320)
        self.assertEqual(fig_hist.layout.height, 280)

    def test_generate_dual_source_plots(self):
        """Test dual source plot generation."""
        # Test with dual_source tab
        fig_rtrend, fig_coh, fig_liss, fig_avgbeat, fig_sdppg = (
            self.plot_manager.create_dual_source_plots(
                self.red,
                self.ir,
                self.red_ac,
                self.ir_ac,
                self.fs,
                self.t,
            )
        )

        self.assertIsNotNone(fig_rtrend)
        self.assertIsNotNone(fig_coh)
        self.assertIsNotNone(fig_liss)
        self.assertIsNotNone(fig_avgbeat)
        self.assertIsNotNone(fig_sdppg)

        # Test with different tab
        fig_rtrend, fig_coh, fig_liss, fig_avgbeat, fig_sdppg = (
            self.plot_manager.create_dual_source_plots(
                self.red,
                self.ir,
                self.red_ac,
                self.ir_ac,
                self.fs,
                self.t,
            )
        )

        self.assertEqual(fig_rtrend.layout.height, 320)
        self.assertEqual(fig_coh.layout.height, 300)

    def test_generate_insights(self):
        """Test insight generation."""
        chips = self.insight_generator.generate_insights(
            self.red, self.ir, self.red_ac, self.ir_ac, None, self.template
        )

        self.assertIsInstance(chips, list)
        self.assertGreater(len(chips), 0)

        # Test with filter error
        chips_error = self.insight_generator.generate_insights(
            self.red, self.ir, self.red_ac, self.ir_ac, "Test error", self.template
        )
        self.assertGreater(len(chips_error), len(chips))

    def test_generate_file_info(self):
        """Test file info generation."""
        info = self.insight_generator.generate_file_info(
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
        self.app = Dash(__name__)

    def test_register_data_callbacks(self):
        """Test data callbacks registration."""
        # Test that the registration function exists and is callable
        self.assertTrue(callable(register_data_callbacks))


class TestWindowCallbacks(unittest.TestCase):
    """Test window management callbacks."""

    def setUp(self):
        """Set up test data."""
        self.app = Dash(__name__)

    def test_register_window_callbacks(self):
        """Test window callbacks registration."""
        # Test that the registration function exists and is callable
        self.assertTrue(callable(register_window_callbacks))


if __name__ == "__main__":
    unittest.main()

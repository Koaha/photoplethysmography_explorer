"""
Tests for the refactored plot callbacks.
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch

# Import the refactored classes
from src.callbacks.plot_callbacks import PlotManager, DataProcessor, InsightGenerator


class TestPlotManager(unittest.TestCase):
    """Test the PlotManager class."""
    
    def setUp(self):
        """Set up test data."""
        self.plot_mgr = PlotManager("plotly", "light")
        self.t = np.linspace(0, 10, 1000)
        self.red = 1000 + 100 * np.sin(2 * np.pi * 1.2 * self.t)
        self.ir = 800 + 80 * np.cos(2 * np.pi * 1.2 * self.t)
        self.red_ac = 100 * np.sin(2 * np.pi * 1.2 * self.t)
        self.ir_ac = 80 * np.cos(2 * np.pi * 1.2 * self.t)
    
    def test_init(self):
        """Test PlotManager initialization."""
        self.assertEqual(self.plot_mgr.template, "plotly")
        self.assertEqual(self.plot_mgr.theme, "light")
        self.assertIsInstance(self.plot_mgr.colors, dict)
    
    def test_create_blank_figure(self):
        """Test blank figure creation."""
        fig = self.plot_mgr.create_blank_figure(300)
        self.assertEqual(fig.layout.height, 300)
        self.assertEqual(fig.layout.template, "plotly")
    
    def test_create_time_domain_plots(self):
        """Test time domain plot creation."""
        fig_raw, fig_ac = self.plot_mgr.create_time_domain_plots(
            self.t, self.red, self.ir, self.red_ac, self.ir_ac,
            "RED", "IR", "butter", "bandpass", 2, len(self.t)
        )
        
        self.assertIsNotNone(fig_raw)
        self.assertIsNotNone(fig_ac)
        self.assertEqual(fig_raw.layout.height, 420)
        self.assertEqual(fig_ac.layout.height, 420)
    
    def test_create_frequency_plots(self):
        """Test frequency plot creation."""
        fig_psd, fig_spec = self.plot_mgr.create_frequency_plots(
            self.red_ac, self.ir_ac, 100, 2.0, 0.5, ["on"]
        )
        
        self.assertIsNotNone(fig_psd)
        self.assertIsNotNone(fig_spec)
        self.assertEqual(fig_psd.layout.height, 360)
        self.assertEqual(fig_spec.layout.height, 380)
    
    def test_create_dynamics_plots(self):
        """Test dynamics plot creation."""
        fig_hr, fig_hist, fig_poi, fig_xc = self.plot_mgr.create_dynamics_plots(
            self.red_ac, self.ir_ac, 100, "ir", 40, 180, 0.5, ["hr"]
        )
        
        self.assertIsNotNone(fig_hr)
        self.assertIsNotNone(fig_hist)
        self.assertIsNotNone(fig_poi)
        self.assertIsNotNone(fig_xc)
    
    def test_create_dual_source_plots(self):
        """Test dual source plot creation."""
        fig_rtrend, fig_coh, fig_liss, fig_avgbeat, fig_sdppg = self.plot_mgr.create_dual_source_plots(
            self.red, self.ir, self.red_ac, self.ir_ac, 100, self.t
        )
        
        self.assertIsNotNone(fig_rtrend)
        self.assertIsNotNone(fig_coh)
        self.assertIsNotNone(fig_liss)
        self.assertIsNotNone(fig_avgbeat)
        self.assertIsNotNone(fig_sdppg)


class TestDataProcessor(unittest.TestCase):
    """Test the DataProcessor class."""
    
    def test_process_data_valid(self):
        """Test data processing with valid data."""
        # Mock data
        path = "/test/path.csv"
        window = {"start": 0, "end": 100}
        red_col = "red"
        ir_col = "ir"
        
        # Mock the read_window function
        with patch('src.callbacks.plot_callbacks.read_window') as mock_read:
            mock_df = Mock()
            mock_df.dropna.return_value = mock_df
            mock_df.empty = False
            mock_df.__getitem__.return_value.astype.return_value.to_numpy.return_value = np.random.randn(100)
            mock_read.return_value = mock_df
            
            # Mock the filter functions
            with patch('src.callbacks.plot_callbacks.design_base_filter') as mock_filter:
                with patch('src.callbacks.plot_callbacks.apply_chain') as mock_apply:
                    mock_filter.return_value = np.array([[1, 0, 1]])
                    mock_apply.return_value = np.random.randn(100)
                    
                    result = DataProcessor.process_data(
                        path, window, red_col, ir_col, 100, 1, "butter", "bandpass",
                        2, 1.0, 40.0, False, 50.0, 30.0, []
                    )
                    
                    self.assertIsNotNone(result[0])  # t
                    self.assertIsNotNone(result[1])  # red
                    self.assertIsNotNone(result[2])  # ir
                    self.assertIsNotNone(result[3])  # red_ac
                    self.assertIsNotNone(result[4])  # ir_ac
                    self.assertIsNone(result[5])     # filt_err
    
    def test_process_data_invalid(self):
        """Test data processing with invalid data."""
        result = DataProcessor.process_data(
            None, None, None, None, 100, 1, "butter", "bandpass",
            2, 1.0, 40.0, False, 50.0, 30.0, []
        )
        
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        self.assertIsNone(result[2])
        self.assertIsNone(result[3])
        self.assertIsNone(result[4])
        self.assertIsNone(result[5])


class TestInsightGenerator(unittest.TestCase):
    """Test the InsightGenerator class."""
    
    def test_generate_insights(self):
        """Test insight generation."""
        red = np.random.randn(1000)
        ir = np.random.randn(1000)
        red_ac = np.random.randn(1000)
        ir_ac = np.random.randn(1000)
        
        # Mock the analysis functions
        with patch('src.callbacks.plot_callbacks.estimate_spo2') as mock_spo2:
            with patch('src.callbacks.plot_callbacks.estimate_rates_psd') as mock_hr:
                with patch('src.callbacks.plot_callbacks.quick_snr') as mock_snr:
                    mock_spo2.return_value = (95.0, 0.5, 2.0)
                    mock_hr.return_value = 72.0
                    mock_snr.return_value = 15.0
                    
                    chips = InsightGenerator.generate_insights(
                        red, ir, red_ac, ir_ac, None, "plotly"
                    )
                    
                    self.assertIsInstance(chips, list)
                    self.assertGreater(len(chips), 0)
                    self.assertTrue(any("SpO₂" in str(chip) for chip in chips))
                    self.assertTrue(any("HR_psd" in str(chip) for chip in chips))
    
    def test_generate_insights_with_error(self):
        """Test insight generation with filter error."""
        red = np.random.randn(1000)
        ir = np.random.randn(1000)
        red_ac = np.random.randn(1000)
        ir_ac = np.random.randn(1000)
        
        with patch('src.callbacks.plot_callbacks.estimate_spo2') as mock_spo2:
            with patch('src.callbacks.plot_callbacks.estimate_rates_psd') as mock_hr:
                with patch('src.callbacks.plot_callbacks.quick_snr') as mock_snr:
                    mock_spo2.return_value = (95.0, 0.5, 2.0)
                    mock_hr.return_value = 72.0
                    mock_snr.return_value = 15.0
                    
                    chips = InsightGenerator.generate_insights(
                        red, ir, red_ac, ir_ac, "Test error", "plotly"
                    )
                    
                    self.assertIsInstance(chips, list)
                    self.assertGreater(len(chips), 0)
                    self.assertTrue(any("Filter error" in str(chip) for chip in chips))
    
    def test_generate_file_info(self):
        """Test file info generation."""
        info = InsightGenerator.generate_file_info(
            "/test/path.csv", 10000, 100, 200, 100, 100, "butter", "bandpass", 2,
            0.5, 5.0, False, 1, "ir", 40, 180, 0.5, 2.0, 0.5
        )
        
        self.assertIsInstance(info, list)
        self.assertGreater(len(info), 0)
        self.assertTrue(any("File:" in str(item) for item in info))
        self.assertTrue(any("Window" in str(item) for item in info))


if __name__ == "__main__":
    unittest.main()

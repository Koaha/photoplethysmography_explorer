"""
Pytest configuration and fixtures for the PPG analysis tool tests.
"""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path

# Add the src directory to the Python path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_ppg_data():
    """Generate sample PPG data for testing."""
    fs = 100
    t = np.linspace(0, 10, 1000)

    # Generate realistic PPG-like signals
    # Heart rate around 72 bpm (1.2 Hz)
    red_base = 1000 + 100 * np.sin(2 * np.pi * 1.2 * t)
    ir_base = 800 + 80 * np.cos(2 * np.pi * 1.2 * t)

    # Add some noise
    red_noise = red_base + 20 * np.random.randn(1000)
    ir_noise = ir_base + 15 * np.random.randn(1000)

    return {
        "time": t,
        "red": red_noise,
        "ir": ir_noise,
        "fs": fs,
        "red_ac": 100 * np.sin(2 * np.pi * 1.2 * t),
        "ir_ac": 80 * np.cos(2 * np.pi * 1.2 * t),
    }


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    temp_file.write("time,red,ir\n")

    # Add some test data
    for i in range(100):
        t = i / 100.0
        red_val = 1000 + 100 * np.sin(2 * np.pi * 1.2 * t)
        ir_val = 800 + 80 * np.cos(2 * np.pi * 1.2 * t)
        temp_file.write(f"{t:.3f},{red_val:.1f},{ir_val:.1f}\n")

    temp_file.close()
    temp_path = temp_file.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_dash_app():
    """Create a mock Dash app for testing callbacks."""
    from unittest.mock import Mock

    app = Mock()
    app.callback_map = {}

    return app

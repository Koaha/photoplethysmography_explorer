"""
Tests for the refactored code to ensure it works correctly.
"""

from pathlib import Path

import pytest

from src.config.settings import settings
from src.utils.exceptions import FileNotFoundError, PPGError, ValidationError
from src.utils.file_utils import get_auto_file_path, get_default_sample_data_path
from src.utils.validation import (
    validate_file_path,
    validate_heart_rate_range,
    validate_sampling_frequency,
    validate_window_parameters,
)


class TestConfiguration:
    """Test configuration management."""

    def test_settings_loaded(self):
        """Test that settings are properly loaded."""
        assert hasattr(settings, "app_name")
        assert hasattr(settings, "default_fs")
        assert hasattr(settings, "default_hr_min")
        assert hasattr(settings, "default_hr_max")

    def test_legacy_constants_available(self):
        """Test that legacy constants are still available for backward compatibility."""
        from src.config.settings import DEFAULT_FS, DEFAULT_HR_MAX, DEFAULT_HR_MIN

        assert DEFAULT_FS == settings.default_fs
        assert DEFAULT_HR_MIN == settings.default_hr_min
        assert DEFAULT_HR_MAX == settings.default_hr_max


class TestExceptions:
    """Test custom exception classes."""

    def test_ppg_error_base(self):
        """Test base PPG error class."""
        error = PPGError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details == {}

    def test_file_error_with_path(self):
        """Test file error with file path."""
        error = FileNotFoundError("File not found", file_path="/path/to/file.csv")
        assert error.file_path == "/path/to/file.csv"

    def test_error_with_details(self):
        """Test error with additional details."""
        details = {"operation": "file_read", "timestamp": "2024-01-01"}
        error = PPGError("Operation failed", details=details)
        assert error.details == details


class TestValidation:
    """Test validation functions."""

    def test_validate_sampling_frequency_valid(self):
        """Test valid sampling frequency."""
        validate_sampling_frequency(100.0)
        validate_sampling_frequency(1000.0)

    def test_validate_sampling_frequency_invalid(self):
        """Test invalid sampling frequency."""
        with pytest.raises(ValidationError):
            validate_sampling_frequency(-100.0)

        with pytest.raises(ValidationError):
            validate_sampling_frequency(0.0)

    def test_validate_heart_rate_range_valid(self):
        """Test valid heart rate range."""
        validate_heart_rate_range(40, 180)
        validate_heart_rate_range(60, 120)

    def test_validate_heart_rate_range_invalid(self):
        """Test invalid heart rate range."""
        with pytest.raises(ValidationError):
            validate_heart_rate_range(10, 180)  # Too low minimum

        with pytest.raises(ValidationError):
            validate_heart_rate_range(40, 400)  # Too high maximum

        with pytest.raises(ValidationError):
            validate_heart_rate_range(180, 40)  # Min > Max

    def test_validate_window_parameters_valid(self):
        """Test valid window parameters."""
        validate_window_parameters(0, 100, 1000)
        validate_window_parameters(100, 200, 1000)

    def test_validate_window_parameters_invalid(self):
        """Test invalid window parameters."""
        with pytest.raises(ValidationError):
            validate_window_parameters(-1, 100, 1000)  # Negative start

        with pytest.raises(ValidationError):
            validate_window_parameters(100, 50, 1000)  # End < Start

        with pytest.raises(ValidationError):
            validate_window_parameters(100, 1100, 1000)  # End > Total rows


class TestFileUtils:
    """Test file utility functions."""

    def test_get_auto_file_path_none(self):
        """Test auto file path when no file exists."""
        # This should not raise an exception even when no file is found
        result = get_auto_file_path("nonexistent_file.csv")
        assert result is None

    def test_get_default_sample_data_path(self):
        """Test getting default sample data path."""
        result = get_default_sample_data_path()
        # Should return None if sample data doesn't exist
        # This test just ensures the function doesn't crash
        assert result is None or isinstance(result, str)


class TestIntegration:
    """Test integration between refactored components."""

    def test_settings_import_works(self):
        """Test that settings can be imported and used."""
        from src.config.settings import APP_TITLE, settings

        assert isinstance(settings.app_name, str)
        assert isinstance(APP_TITLE, str)

    def test_exceptions_import_works(self):
        """Test that exceptions can be imported and used."""
        from src.utils.exceptions import (
            DataError,
            FileError,
            PPGError,
            ProcessingError,
            ValidationError,
        )

        # Just test that imports work
        assert PPGError
        assert FileError
        assert DataError
        assert ValidationError
        assert ProcessingError

    def test_validation_import_works(self):
        """Test that validation functions can be imported and used."""
        from src.utils.validation import validate_csv_file, validate_dataframe, validate_file_path

        # Just test that imports work
        assert validate_file_path
        assert validate_csv_file
        assert validate_dataframe


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

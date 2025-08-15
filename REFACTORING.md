# PPG Analysis Tool - Refactoring Documentation

## Overview

This document describes the comprehensive refactoring performed on the PPG Analysis Tool to improve code quality, maintainability, and follow best practices.

## Key Improvements Made

### 1. Configuration Management

**Before**: Hardcoded constants scattered throughout the code
**After**: Centralized configuration using Pydantic with environment variable support

- **New**: `src/config/settings.py` - Centralized configuration with validation
- **Features**:
  - Environment variable support (`.env` files)
  - Input validation with Pydantic
  - Type-safe configuration
  - Backward compatibility with legacy constants

### 2. Error Handling

**Before**: Basic exception handling with generic error messages
**After**: Comprehensive error handling with custom exception hierarchy

- **New**: `src/utils/exceptions.py` - Custom exception classes
- **Features**:
  - Hierarchical exception structure
  - Detailed error information
  - Specific error types for different scenarios
  - Better debugging and user experience

### 3. Input Validation

**Before**: Limited input validation
**After**: Comprehensive validation system

- **New**: `src/utils/validation.py` - Validation utilities
- **Features**:
  - File path validation
  - Data type validation
  - Parameter range validation
  - CSV file format validation
  - Signal processing parameter validation

### 4. Type Hints

**Before**: No type hints
**After**: Comprehensive type annotations throughout

- **Benefits**:
  - Better IDE support
  - Improved code documentation
  - Static type checking with mypy
  - Reduced runtime errors

### 5. Logging

**Before**: No structured logging
**After**: Comprehensive logging system

- **New**: `src/config/logging_config.py` - Logging configuration
- **Features**:
  - Configurable log levels
  - File and console output
  - Log rotation
  - Debug logging for development
  - Production-ready logging

### 6. Code Organization

**Before**: Some functions were too long and complex
**After**: Better separation of concerns and smaller, focused functions

- **Improvements**:
  - Smaller, more focused functions
  - Better separation of concerns
  - Improved readability
  - Easier testing and maintenance

## New File Structure

```
src/
├── config/
│   ├── __init__.py
│   ├── settings.py          # NEW: Centralized configuration
│   └── logging_config.py    # NEW: Logging configuration
├── utils/
│   ├── __init__.py
│   ├── exceptions.py        # NEW: Custom exceptions
│   ├── validation.py        # NEW: Input validation
│   ├── file_utils.py        # REFACTORED: Better error handling
│   ├── ppg_analysis.py      # REFACTORED: Better validation
│   └── signal_processing.py
├── app.py                   # REFACTORED: Better error handling
└── ...
```

## Configuration

### Environment Variables

The application now supports configuration via environment variables:

```bash
# App settings
APP_NAME="PPG Filter Lab"
APP_VERSION="1.0.0"
DEBUG=false

# File handling
MAX_FILE_SIZE_MB=100
TEMP_FILE_PREFIX="ppg_"

# Signal processing
DEFAULT_FS=100.0
DEFAULT_HR_MIN=40
DEFAULT_HR_MAX=180
```

### Configuration File

Create a `.env` file in the project root:

```env
DEBUG=true
MAX_FILE_SIZE_MB=50
DEFAULT_FS=200.0
```

## Error Handling

### Custom Exceptions

The application now uses a hierarchy of custom exceptions:

```python
from src.utils.exceptions import (
    PPGError,              # Base exception
    FileError,             # File-related errors
    DataError,             # Data processing errors
    ValidationError,       # Validation errors
    ProcessingError,       # Signal processing errors
    ConfigurationError     # Configuration errors
)
```

### Example Usage

```python
from src.utils.exceptions import FileNotFoundError
from src.utils.validation import validate_file_path

try:
    file_path = validate_file_path("nonexistent.csv")
except FileNotFoundError as e:
    logger.error(f"File not found: {e.file_path}")
    # Handle error appropriately
```

## Validation

### Input Validation

All inputs are now validated before processing:

```python
from src.utils.validation import (
    validate_file_path,
    validate_csv_file,
    validate_sampling_frequency,
    validate_heart_rate_range
)

# Validate file
file_path = validate_file_path("data.csv")
validate_csv_file(file_path)

# Validate parameters
validate_sampling_frequency(100.0)
validate_heart_rate_range(40, 180)
```

## Logging

### Logging Configuration

The application automatically configures logging:

```python
from src.config.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Processing started")
logger.debug(f"Parameters: {params}")
logger.error(f"Processing failed: {error}")
```

### Log Levels

- **DEBUG**: Detailed information for development
- **INFO**: General information about application flow
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors that may cause application failure

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_validation.py

# Run with verbose output
pytest -v
```

### Test Structure

Tests are organized to match the source code structure:

```
tests/
├── test_config.py          # Configuration tests
├── test_validation.py      # Validation tests
├── test_exceptions.py      # Exception tests
├── test_file_utils.py      # File utility tests
├── test_ppg_analysis.py    # PPG analysis tests
└── ...
```

## Code Quality

### Static Analysis

The project now includes several code quality tools:

```bash
# Code formatting
black src/
isort src/

# Linting
flake8 src/

# Type checking
mypy src/

# Security scanning
bandit src/
safety check
```

### Pre-commit Hooks

Consider setting up pre-commit hooks to automatically run these tools:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## Migration Guide

### For Existing Code

1. **Update imports**: Use new exception and validation modules
2. **Add type hints**: Gradually add type annotations
3. **Use configuration**: Replace hardcoded values with settings
4. **Add logging**: Use the new logging system
5. **Update error handling**: Use custom exceptions

### Example Migration

**Before**:
```python
def process_file(file_path):
    if not os.path.exists(file_path):
        return None, "File not found"
    # ... processing code
```

**After**:
```python
from src.utils.exceptions import FileNotFoundError
from src.utils.validation import validate_file_path
from src.config.logging_config import get_logger

logger = get_logger(__name__)

def process_file(file_path: str) -> Tuple[Any, str]:
    try:
        validated_path = validate_file_path(file_path)
        logger.info(f"Processing file: {validated_path}")
        # ... processing code
        return result, "Success"
    except FileNotFoundError as e:
        logger.error(f"File not found: {e.file_path}")
        return None, str(e)
```

## Benefits

### For Developers

- **Better IDE support** with type hints
- **Easier debugging** with comprehensive logging
- **Reduced errors** with input validation
- **Clearer code** with better organization
- **Easier testing** with smaller, focused functions

### For Users

- **Better error messages** with specific error types
- **More reliable** with comprehensive validation
- **Easier troubleshooting** with detailed logging
- **Better performance** with optimized code structure

### For Maintenance

- **Easier to modify** with clear separation of concerns
- **Easier to test** with focused functions
- **Better documentation** with type hints and docstrings
- **Consistent patterns** throughout the codebase

## Future Improvements

1. **API Documentation**: Add OpenAPI/Swagger documentation
2. **Performance Monitoring**: Add metrics and performance tracking
3. **Caching**: Implement caching for expensive operations
4. **Async Support**: Add async/await support for better performance
5. **Plugin System**: Create a plugin architecture for extensibility

## Conclusion

This refactoring significantly improves the codebase quality, maintainability, and developer experience. The new structure follows Python best practices and provides a solid foundation for future development.

For questions or issues with the refactored code, please refer to the test suite or create an issue in the project repository.

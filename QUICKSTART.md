# 🚀 PPG Analysis Tool - Quick Start Guide

## Overview

This guide will help you get the refactored PPG Analysis Tool running quickly. The refactored code includes significant improvements in code quality, error handling, and maintainability.

## 🏃‍♂️ Quick Start (3 Steps)

### Step 1: Install Dependencies

**Option A: Automatic Installation (Recommended)**
```bash
python install_dependencies.py
```

**Option B: Manual Installation**
```bash
pip install pydantic pydantic-settings dash plotly numpy pandas scipy
```

### Step 2: Test the Configuration

Verify that everything is working:
```bash
python test_config.py
```

You should see:
```
🧪 PPG Analysis Tool - Configuration Test
==================================================
✅ Configuration imported successfully
✅ Exceptions imported successfully
✅ Validation imported successfully
✅ File utilities imported successfully
✅ App imported successfully

📊 Test Results: 5/5 tests passed
🎉 All tests passed! The refactored code is working correctly.
```

### Step 3: Run the Application

```bash
python main.py
```

The application should start and be available at `http://localhost:8050`

## 🔧 Configuration

### Environment Variables

Create a `.env` file from the example:
```bash
cp env.example .env
```

Edit `.env` with your preferred settings:
```env
DEBUG=true
MAX_FILE_SIZE_MB=50
DEFAULT_FS=200.0
```

### Key Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `MAX_FILE_SIZE_MB` | Maximum file size limit | `100` |
| `DEFAULT_FS` | Default sampling frequency | `100.0` |
| `DEFAULT_HR_MIN` | Minimum heart rate | `40` |
| `DEFAULT_HR_MAX` | Maximum heart rate | `180` |

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/
```

### Run Specific Tests
```bash
python -m pytest tests/test_refactored_code.py -v
```

### Run Configuration Test
```bash
python test_config.py
```

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```
ModuleNotFoundError: No module named 'pydantic_settings'
```
**Solution**: Install the missing dependency:
```bash
pip install pydantic-settings
```

**2. Configuration Errors**
```
pydantic.errors.PydanticImportError: BaseSettings has been moved
```
**Solution**: The code now handles this automatically. Make sure you have the latest version.

**3. File Permission Errors**
```
PermissionError: [Errno 13] Permission denied
```
**Solution**: Check file permissions or run with appropriate privileges.

### Getting Help

1. **Check the logs**: Look for error messages in the console output
2. **Verify dependencies**: Run `python test_config.py` to check imports
3. **Check configuration**: Ensure your `.env` file is properly formatted
4. **Review documentation**: See `REFACTORING.md` for detailed information

## 📁 Project Structure

```
Photoplethymogram/
├── src/                          # Source code
│   ├── config/                   # Configuration
│   │   ├── settings.py          # Main settings
│   │   └── logging_config.py    # Logging setup
│   ├── utils/                    # Utilities
│   │   ├── exceptions.py        # Custom exceptions
│   │   ├── validation.py        # Input validation
│   │   ├── file_utils.py        # File handling
│   │   └── ppg_analysis.py      # PPG analysis
│   └── app.py                   # Main application
├── tests/                        # Test files
├── install_dependencies.py       # Dependency installer
├── test_config.py               # Configuration tester
├── env.example                  # Environment template
└── REFACTORING.md               # Detailed refactoring docs
```

## 🚀 What's New in the Refactored Code

### ✨ **Major Improvements**

1. **Configuration Management**
   - Environment variable support
   - Type-safe configuration with Pydantic
   - Validation and error checking

2. **Error Handling**
   - Custom exception hierarchy
   - Detailed error messages
   - Better debugging support

3. **Input Validation**
   - Comprehensive parameter validation
   - File format checking
   - Data integrity verification

4. **Type Hints**
   - Complete type annotations
   - Better IDE support
   - Static type checking ready

5. **Logging**
   - Structured logging system
   - Configurable log levels
   - File and console output

6. **Code Quality**
   - Better organization
   - Smaller, focused functions
   - Consistent patterns

## 🔄 Migration from Old Code

If you're updating from the previous version:

1. **Update imports**: The new structure uses different import paths
2. **Use configuration**: Replace hardcoded values with `settings.variable_name`
3. **Add error handling**: Use the new exception classes
4. **Add validation**: Use validation functions before processing data

### Example Migration

**Before:**
```python
def process_file(file_path):
    if not os.path.exists(file_path):
        return None, "File not found"
    # ... processing code
```

**After:**
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

## 📚 Next Steps

1. **Explore the code**: Check out the new structure in `src/`
2. **Read documentation**: See `REFACTORING.md` for detailed information
3. **Run tests**: Verify everything works with `python test_config.py`
4. **Customize**: Modify `.env` file for your environment
5. **Contribute**: The new structure makes it easier to add features

## 🆘 Need Help?

- **Check logs**: Look for error messages in console output
- **Run tests**: Use `python test_config.py` to diagnose issues
- **Review docs**: See `REFACTORING.md` for comprehensive information
- **Check dependencies**: Ensure all required packages are installed

---

**Happy coding! 🎉**

The refactored code provides a solid foundation for future development while maintaining all the original functionality.

# PPG Analysis Tool - Modular Version

A refactored, modular version of the PPG (Photoplethysmogram) analysis tool built with Dash, designed for both local development and cloud deployment.

## 🏗️ **New Modular Structure**

```
photoplethymogram/
├── src/                          # Source code package
│   ├── __init__.py              # Package initialization
│   ├── app.py                   # Main Dash application
│   ├── callbacks/               # Callback functions
│   │   ├── __init__.py
│   │   ├── data_callbacks.py    # Data loading & file handling
│   │   ├── window_callbacks.py  # Window & slider management
│   │   └── plot_callbacks.py    # Chart generation
│   ├── components/              # UI components
│   │   ├── __init__.py
│   │   ├── layout.py            # App layout
│   │   └── styles.py            # CSS & styling
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── signal_processing.py # Filtering & analysis
│   │   ├── ppg_analysis.py      # PPG-specific calculations
│   │   └── file_utils.py        # File handling utilities
│   └── config/                  # Configuration
│       ├── __init__.py
│       └── settings.py          # Constants & defaults
├── tests/                       # Test suite
├── main.py                      # Development entry point
├── main-prod.py                 # Production entry point
├── Dockerfile.prod              # Production Docker configuration
├── requirements.txt             # Development dependencies
├── requirements-prod.txt        # Production dependencies
├── render.yaml                  # Render.com deployment config
├── cloudbuild.yaml             # Google Cloud Build config
├── deploy.sh                   # Deployment automation script
└── README.md                    # This file
```

## 🚀 **Key Improvements**

### **1. Modular Architecture**
- **Separation of Concerns**: Each module has a specific responsibility
- **Maintainability**: Easier to locate and modify specific functionality
- **Testability**: Individual modules can be tested in isolation
- **Reusability**: Utility functions can be imported elsewhere

### **2. Organized Callbacks**
- **`data_callbacks.py`**: File loading, dynamic column detection, auto-file handling
- **`window_callbacks.py`**: Window management, slider controls, UI synchronization
- **`plot_callbacks.py`**: Chart generation, data processing, insights (refactored for maintainability)

### **3. Utility Modules**
- **`signal_processing.py`**: Filter design, signal analysis, cross-correlation
- **`ppg_analysis.py`**: Heart rate detection, SpO2 estimation, beat analysis
- **`file_utils.py`**: CSV handling, row counting, upload processing

### **4. Configuration Management**
- **`settings.py`**: Centralized constants and defaults
- **Easy customization**: Modify settings in one place

### **5. Code Quality Improvements**
- **Refactored Plot Callbacks**: Large `update_plots` function broken down into focused classes:
  - **`PlotManager`**: Handles all plot generation with clean separation of concerns
  - **`DataProcessor`**: Manages data processing and validation
  - **`InsightGenerator`**: Generates insights and file information
- **Dynamic Column Selection**: Smart detection of RED/IR columns based on naming patterns
- **Maintainable Code**: Each class has a single responsibility, making the code easier to understand and modify

## 🛠️ **Installation & Usage**

### **1. Install Dependencies**
```bash
# For basic usage
pip install -r requirements.txt

# For development and testing
pip install -r requirements-dev.txt

# For production deployment
pip install -r requirements-prod.txt
```

### **2. Run the Application**

#### **Development Mode**
```bash
python main.py
```

#### **Production Mode**
```bash
python main-prod.py
```

### **3. Access the Web Interface**
- **Development**: Open `http://localhost:8050`
- **Production**: Open `http://localhost:8080` (or your configured port)

## 🚀 **Deployment Options**

This tool is designed for easy deployment to various cloud platforms with Docker support.

### **🐳 Docker Deployment**

#### **Quick Start with Docker**
```bash
# Build the production image
docker build -f Dockerfile.prod -t ppg-tool:latest .

# Run locally
docker run -d --name ppg-tool -p 8080:8080 ppg-tool:latest

# Access at http://localhost:8080
```

#### **Docker Compose (Development)**
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f ppg-tool

# Stop the application
docker-compose down
```

### **☁️ Render.com Deployment**

#### **Option 1: Using Render Dashboard**
1. Connect your GitHub repository to Render.com
2. Create a new Web Service
3. Configure with:
   - **Build Command**: `pip install -r requirements-prod.txt`
   - **Start Command**: `python main-prod.py`
   - **Environment Variables**:
     - `PYTHON_VERSION`: `3.11.0`
     - `PORT`: `8080`
     - `DEBUG`: `false`

#### **Option 2: Using Render Blueprint**
```bash
# Install Render CLI
curl -sSL https://render.com/download-cli/install.sh | bash

# Deploy using the blueprint
render blueprint apply
```

#### **Option 3: Using Deployment Script**
```bash
chmod +x deploy.sh
./deploy.sh render
```

### **☁️ Google Cloud Platform Deployment**

#### **Prerequisites**
```bash
# Install Google Cloud SDK
# macOS
brew install google-cloud-sdk

# Ubuntu/Debian
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install google-cloud-sdk

# Authenticate and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### **Deploy to Cloud Run**
```bash
# Using Cloud Build (Recommended)
gcloud builds submit --config cloudbuild.yaml .

# Using deployment script
chmod +x deploy.sh
./deploy.sh gcp

# Manual deployment
docker build -f Dockerfile.prod -t gcr.io/YOUR_PROJECT_ID/ppg-tool .
docker push gcr.io/YOUR_PROJECT_ID/ppg-tool

gcloud run deploy ppg-tool \
  --image gcr.io/YOUR_PROJECT_ID/ppg-tool \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

### **🔧 Environment Variables**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Port to run the application on | `8080` | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `PYTHONPATH` | Python path for imports | `/app/src` | No |

### **📊 Health Checks**

The application includes a health check endpoint at `/health` used by:
- Docker health checks
- Load balancers
- Cloud platforms for monitoring

### **🔒 Security Features**

- **Non-root user**: Application runs as non-root user `app`
- **Minimal base image**: Uses Python slim image to reduce attack surface
- **Security headers**: Nginx configuration includes security headers
- **Port binding**: Only binds to necessary ports

### **📈 Scaling Configuration**

#### **Render.com**
- **Auto-scaling**: 1-3 instances
- **Target concurrency**: 100 requests per instance
- **Memory utilization**: Scales at 80% memory usage

#### **Google Cloud Platform**
- **Cloud Run**: Automatically scales to zero when not in use
- **Max instances**: Limited to 10 instances
- **Memory**: 512MB per instance
- **CPU**: 1 vCPU per instance

## 🔧 **Development**

### **Adding New Features**
1. **New Analysis**: Add functions to `src/utils/ppg_analysis.py`
2. **New Plots**: Extend `src/callbacks/plot_callbacks.py`
3. **New Controls**: Modify `src/components/layout.py`
4. **New Callbacks**: Create new files in `src/callbacks/`

### **Modifying Existing Features**
- **Signal Processing**: Edit `src/utils/signal_processing.py`

### **Code Quality & Testing**
- **Run Tests**: `python -m pytest tests/ -v`
- **Code Coverage**: `python -m pytest tests/ --cov=src --cov-report=html`
- **Linting**: `flake8 src/ tests/`
- **Formatting**: `black src/ tests/` and `isort src/ tests/`
- **Security**: `bandit -r src/` and `safety check`

### **Using Makefile Commands**
```bash
make help           # Show available commands
make install-dev    # Install development dependencies
make test           # Run all tests
make test-coverage  # Run tests with coverage
make lint           # Run all linting checks
make format         # Format code automatically
make quality        # Run full quality check suite
make build          # Build package distribution
make clean          # Clean build artifacts
make run            # Run the application locally
```

## 📚 **Documentation**

### **Building Documentation**
```bash
cd docs
make html
```

The documentation will be built in `docs/_build/html/` and includes:
- **Installation Guide**: Setup and configuration instructions
- **User Guide**: Comprehensive usage instructions and examples
- **API Reference**: Detailed documentation of all functions and classes
- **Development Guide**: Setup and contribution guidelines

## 🚀 **CI/CD Pipeline**

This project includes a comprehensive GitHub Actions workflow (`.github/workflows/ci-cd.yml`) that provides:

### **Automated Testing**
- **Multi-Python Testing**: Tests against Python 3.8, 3.9, 3.10, and 3.11
- **Code Coverage**: Automated coverage reporting with Codecov integration
- **Linting**: Automated code quality checks (flake8, black, isort)

### **Security Scanning**
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency vulnerability checking

### **Quality Assurance**
- **Type Checking**: MyPy integration for static type analysis
- **Documentation**: Automated documentation building
- **Package Building**: Automated package distribution creation

### **Deployment**
- **PyPI Publishing**: Automatic package publishing on releases
- **Artifact Management**: Build artifacts and reports storage

### **Workflow Triggers**
- **Push**: Runs on pushes to `main` and `develop` branches
- **Pull Request**: Runs on all PRs to ensure code quality
- **Release**: Automatically publishes to PyPI on new releases

## 📦 **Package Management**

### **Modern Python Packaging**
- **`pyproject.toml`**: Modern Python packaging configuration
- **`setup.py`**: Traditional setup configuration for compatibility
- **Development Tools**: Comprehensive tool configuration for code quality

### **Dependencies**
- **Production**: Core dependencies in `requirements.txt`
- **Development**: Development tools in `requirements-dev.txt`
- **Production**: Optimized dependencies in `requirements-prod.txt`
- **UI Layout**: Modify `src/components/layout.py`
- **Styling**: Update `src/components/styles.py`
- **Defaults**: Change `src/config/settings.py`

### **Testing**
The project includes a comprehensive test suite located in the `tests/` directory:

```
tests/
├── __init__.py                      # Test package initialization
├── test_config.py                   # Configuration settings tests
├── test_utils.py                    # Utility function tests
├── test_ppg_analysis.py             # PPG analysis algorithm tests
├── test_callbacks.py                # Callback function tests
├── test_refactored_callbacks.py     # Refactored callback tests
├── test_integration.py              # Integration tests
├── conftest.py                      # Pytest configuration
└── run_tests.py                     # Test runner script
```

#### **Running Tests**
```bash
# Run all tests
python tests/run_tests.py

# Run specific test modules
python -m unittest tests.test_config
python -m unittest tests.test_utils
python -m unittest tests.test_ppg_analysis

# Run with coverage (if coverage.py is installed)
coverage run tests/run_tests.py
coverage report
```

#### **Test Categories**
- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test the complete data processing pipeline
- **Validation Tests**: Test error handling and edge cases
- **Performance Tests**: Test signal processing algorithms with realistic data

#### **Writing New Tests**
1. Create test functions that inherit from `unittest.TestCase`
2. Use descriptive test method names starting with `test_`
3. Test both normal operation and edge cases
4. Include setup and teardown methods for test data
5. Use realistic PPG-like test signals for algorithm testing

## 📊 **Features**

### **Data Loading**
- CSV file upload (drag & drop)
- Local file path loading
- **Smart column detection**: Automatically identifies RED/IR columns using multiple strategies:
  - Pattern matching (red, ir, infrared, red_adc, ir_signal, etc.)
  - Numeric column selection (excludes time/timestamp columns)
  - Fallback to first available columns
- Row windowing for large datasets

### **Signal Processing**
- Multiple filter types (Butterworth, Chebyshev, Elliptic, Bessel)
- Bandpass, bandstop, lowpass, highpass responses
- Line noise notch filtering (50/60 Hz)
- Detrending and signal inversion

### **Analysis**
- Heart rate detection and trend analysis
- SpO2 estimation from dual-wavelength data
- Beat-by-beat R-ratio analysis
- Cross-correlation between signals
- Ensemble-averaged beat shapes
- Second derivative analysis (SDPPG)

### **Visualization**
- Time-domain plots (raw and filtered)
- Frequency domain (PSD, spectrograms)
- Heart rate dynamics (trends, histograms, Poincaré plots)
- Dual-source analytics (coherence, Lissajous, average beats)

## 🐛 **Bug Fixes**

### **Circular Dependency Issue**
The original version had a circular dependency between callbacks that caused "Maximum call stack size exceeded" errors. This has been fixed by:

1. **Consolidating slider updates** into the `window_controls` callback
2. **Removing separate slider callbacks** that caused loops
3. **Using `allow_duplicate=True`** to prevent conflicts
4. **Proper callback organization** to prevent infinite recursion

## 🔄 **Migration from Original**

If you're migrating from the original `ppg_tool.py`:

1. **Backup your original file**
2. **Install the new requirements**: `pip install -r requirements.txt`
3. **Run the new version**: `python main.py`
4. **Test functionality** to ensure everything works as expected

## 🚀 **Deployment Best Practices**

### **Environment Configuration**
- Use `main-prod.py` for production deployments
- Set `DEBUG=false` in production
- Configure appropriate port binding (`0.0.0.0` for Docker)
- Disable hot reload and debug UI in production

### **Docker Optimization**
- Use multi-stage builds to reduce image size
- Leverage layer caching for faster builds
- Include only production dependencies
- Run as non-root user for security

### **Cloud Platform Considerations**
- **Render.com**: Great for simple deployments with automatic scaling
- **Google Cloud**: More control over infrastructure and scaling
- **Health Checks**: Essential for load balancer integration
- **Environment Variables**: Use for configuration management

### **Monitoring and Logging**
- Implement proper logging for production debugging
- Use platform-specific monitoring tools
- Set up alerts for application health
- Monitor resource usage and scaling metrics

## 📝 **Contributing**

When contributing to this project:

1. **Follow the modular structure**
2. **Add docstrings** to new functions
3. **Update relevant modules** when adding features
4. **Test your changes** before submitting
5. **Follow deployment guidelines** when adding deployment-related changes

## 📄 **License**

This project is open source. Feel free to use, modify, and distribute according to your needs.

---

**Note**: This modular version maintains all the functionality of the original while providing a much cleaner, maintainable codebase structure and comprehensive deployment options for various cloud platforms.

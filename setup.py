"""
Setup configuration for PPG Analysis Tool.

This package provides a comprehensive tool for analyzing photoplethysmogram (PPG) signals
with advanced signal processing, visualization, and analysis capabilities.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read version from __init__.py
def get_version():
    """Extract version from package __init__.py file."""
    init_file = this_directory / "src" / "__init__.py"
    with open(init_file, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'')
    return "0.1.0"

setup(
    name="ppg-analysis-tool",
    version=get_version(),
    author="PPG Analysis Team",
    author_email="team@ppg-analysis.com",
    description="A comprehensive tool for PPG signal analysis and visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ppg-analysis-tool",
    project_urls={
        "Bug Reports": "https://github.com/your-username/ppg-analysis-tool/issues",
        "Source": "https://github.com/your-username/ppg-analysis-tool",
        "Documentation": "https://ppg-analysis-tool.readthedocs.io/",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "dash>=2.0.0",
        "plotly>=5.0.0",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.6.0",
            "flake8>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "coverage>=6.0.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "bandit>=1.7.0",
            "safety>=2.0.0",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.6.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ppg-tool=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    zip_safe=False,
    keywords=[
        "ppg", "photoplethysmogram", "signal-processing", "biomedical",
        "heart-rate", "spo2", "oxygen-saturation", "dash", "plotly",
        "medical-devices", "healthcare", "analysis", "visualization"
    ],
)

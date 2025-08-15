# PPG Analysis Tool Documentation

This directory contains the complete documentation for the PPG Analysis Tool.

## 📁 Documentation Structure

- **`index.rst`** - Main documentation index and overview
- **`installation.rst`** - Installation guide and setup instructions
- **`user_guide.rst`** - Comprehensive user guide and tutorials
- **`api_reference.rst`** - Technical API documentation
- **`development.rst`** - Developer setup and workflow guide
- **`contributing.rst`** - Contribution guidelines and community standards
- **`conf.py`** - Sphinx configuration file
- **`Makefile`** - Unix/Linux/macOS build commands

## 🚀 Building Documentation

### Prerequisites
- Python 3.8+
- Sphinx and sphinx-rtd-theme installed
- All dependencies from `requirements-dev.txt`

### Build Commands

**Cross-platform (recommended):**
```bash
python build_docs.py
```

**Windows:**
```bash
build_docs.bat
```

**Unix/Linux/macOS:**
```bash
make docs
```

**Direct Sphinx:**
```bash
cd docs
sphinx-build -b html . _build/html
```

## 📖 Viewing Documentation

After building, open `_build/html/index.html` in your web browser to view the complete documentation.

## 🔧 Configuration

The documentation is configured in `conf.py` with:
- Sphinx extensions for auto-documentation
- Read the Docs theme
- Intersphinx links to external documentation
- Custom settings for the project

## 📝 Adding New Documentation

1. Create new `.rst` files in this directory
2. Update `index.rst` to include your new documents
3. Add cross-references between related documents
4. Rebuild documentation to see your changes

## 🐛 Troubleshooting

**Common Issues:**
- **Import errors**: Ensure all dependencies are installed
- **Build failures**: Check for syntax errors in RST files
- **Missing modules**: Verify autodoc can find your source code
- **Theme issues**: Ensure sphinx-rtd-theme is installed

**Getting Help:**
- Check the main project README
- Review Sphinx documentation
- Check for syntax errors in RST files
- Verify all dependencies are installed

## 📚 Documentation Standards

- Use Google-style docstrings in Python code
- Follow RST syntax guidelines
- Include practical examples
- Cross-reference related documents
- Keep content up-to-date with code changes

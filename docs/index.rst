PPG Analysis Tool Documentation
===============================

Welcome to the PPG Analysis Tool documentation! This tool provides comprehensive analysis capabilities for photoplethysmogram (PPG) signals with advanced signal processing, visualization, and insights.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   user_guide
   api_reference
   development
   contributing

Features
--------

* **Advanced Signal Processing**: Multiple filter families (Butterworth, Chebyshev, Elliptic, Bessel) with configurable parameters
* **Comprehensive Visualization**: Time-domain, frequency-domain, and dynamics plots with interactive features
* **Smart Column Detection**: Automatic identification of RED/IR channels from various naming conventions
* **Real-time Analysis**: Live signal processing with adjustable parameters and immediate feedback
* **Export Capabilities**: CSV download and data export for further analysis
* **Modular Architecture**: Clean, maintainable code structure with comprehensive testing

Quick Start
-----------

1. **Install the tool**:
   .. code-block:: bash
      
      pip install -r requirements.txt

2. **Run the application**:
   .. code-block:: bash
      
      python main.py

3. **Load your PPG data** and start analyzing!

Installation
------------

See :doc:`installation` for detailed installation instructions.

User Guide
----------

See :doc:`user_guide` for comprehensive usage instructions and examples.

API Reference
-------------

See :doc:`api_reference` for detailed API documentation.

Development
-----------

See :doc:`development` for development setup and contribution guidelines.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

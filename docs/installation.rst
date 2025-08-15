Installation Guide
=================

This guide will help you install the PPG Analysis Tool on your system.

Prerequisites
------------

* Python 3.8 or higher
* pip (Python package installer)
* Git (for cloning the repository)

Installation Methods
-------------------

Method 1: Install from Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Clone the repository**:
   .. code-block:: bash
      
      git clone https://github.com/yourusername/Photoplethymogram.git
      cd Photoplethymogram

2. **Create a virtual environment** (recommended):
   .. code-block:: bash
      
      python -m venv venv
      
      # On Windows:
      venv\Scripts\activate
      
      # On macOS/Linux:
      source venv/bin/activate

3. **Install dependencies**:
   .. code-block:: bash
      
      pip install -r requirements.txt

4. **Install the package in development mode**:
   .. code-block:: bash
      
      pip install -e .

Method 2: Install Dependencies Only
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you just want to run the tool without installing it as a package:

.. code-block:: bash
   
   pip install -r requirements.txt

Method 3: Install Production Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For production deployment:

.. code-block:: bash
   
   pip install -r requirements-prod.txt

Verification
-----------

To verify the installation, run:

.. code-block:: bash
   
   python -c "import src; print('Installation successful!')"

Or run the main application:

.. code-block:: bash
   
   python main.py

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

* **Import errors**: Make sure you're in the correct directory and have activated your virtual environment
* **Missing dependencies**: Run `pip install -r requirements.txt` again
* **Permission errors**: On Unix-like systems, you might need to use `sudo` or install with `--user` flag

Getting Help
-----------

If you encounter issues during installation:

1. Check the `README.md` file for additional information
2. Review the `requirements.txt` file for dependency versions
3. Ensure your Python version meets the minimum requirements
4. Check that all system dependencies are installed

Next Steps
----------

After successful installation, proceed to the :doc:`user_guide` to learn how to use the tool.

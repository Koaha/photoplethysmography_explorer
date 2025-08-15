API Reference
=============

This document provides detailed API documentation for the PPG Analysis Tool.

Core Modules
------------

Signal Processing
~~~~~~~~~~~~~~~~

.. automodule:: src.utils.signal_processing
   :members:
   :undoc-members:
   :show-inheritance:

PPG Analysis
~~~~~~~~~~~

.. automodule:: src.utils.ppg_analysis
   :members:
   :undoc-members:
   :show-inheritance:

File Utilities
~~~~~~~~~~~~~

.. automodule:: src.utils.file_utils
   :members:
   :undoc-members:
   :show-inheritance:

Validation
~~~~~~~~~~

.. automodule:: src.utils.validation
   :members:
   :undoc-members:
   :show-inheritance:

Application Components
---------------------

Main Application
~~~~~~~~~~~~~~~

.. automodule:: src.app
   :members:
   :undoc-members:
   :show-inheritance:

Layout Components
~~~~~~~~~~~~~~~~

.. automodule:: src.components.layout
   :members:
   :undoc-members:
   :show-inheritance:

Callback Functions
-----------------

Data Callbacks
~~~~~~~~~~~~~

.. automodule:: src.callbacks.data_callbacks
   :members:
   :undoc-members:
   :show-inheritance:

Plot Callbacks
~~~~~~~~~~~~~

.. automodule:: src.callbacks.plot_callbacks
   :members:
   :undoc-members:
   :show-inheritance:

Window Callbacks
~~~~~~~~~~~~~~~

.. automodule:: src.callbacks.window_callbacks
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
-------------

Settings
~~~~~~~~

.. automodule:: src.config.settings
   :members:
   :undoc-members:
   :show-inheritance:

Logging Configuration
~~~~~~~~~~~~~~~~~~~~

.. automodule:: src.config.logging_config
   :members:
   :undoc-members:
   :show-inheritance:

Key Functions Reference
----------------------

Signal Processing Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. function:: apply_filter(signal, filter_type, cutoff_freq, filter_order, sample_rate)

   Apply digital filter to signal data.
   
   :param signal: Input signal array
   :param filter_type: Type of filter ('butterworth', 'chebyshev', 'elliptic', 'bessel')
   :param cutoff_freq: Cutoff frequency in Hz
   :param filter_order: Filter order (integer)
   :param sample_rate: Sampling rate in Hz
   :return: Filtered signal array
   :raises ValueError: If filter parameters are invalid

.. function:: compute_fft(signal, sample_rate)

   Compute Fast Fourier Transform of signal.
   
   :param signal: Input signal array
   :param sample_rate: Sampling rate in Hz
   :return: Tuple of (frequencies, magnitudes)

.. function:: detect_peaks(signal, threshold=None, distance=None)

   Detect peaks in signal data.
   
   :param signal: Input signal array
   :param threshold: Minimum peak height
   :param distance: Minimum distance between peaks
   :return: Array of peak indices

PPG Analysis Functions
~~~~~~~~~~~~~~~~~~~~~~

.. function:: calculate_heart_rate(peak_times, time_window)

   Calculate heart rate from peak detection.
   
   :param peak_times: Array of peak time indices
   :param time_window: Time window for calculation in seconds
   :return: Heart rate in beats per minute

.. function:: compute_signal_quality(signal, noise_threshold=0.1)

   Assess signal quality metrics.
   
   :param signal: Input signal array
   :param noise_threshold: Threshold for noise detection
   :return: Dictionary of quality metrics

File Processing Functions
~~~~~~~~~~~~~~~~~~~~~~~~

.. function:: load_ppg_data(file_path, file_type='auto')

   Load PPG data from various file formats.
   
   :param file_path: Path to data file
   :param file_type: File type ('csv', 'excel', 'text', or 'auto')
   :return: Dictionary containing data and metadata

.. function:: detect_columns(data_frame)

   Automatically detect time and signal columns.
   
   :param data_frame: Pandas DataFrame
   :return: Dictionary with detected column names

Configuration Functions
~~~~~~~~~~~~~~~~~~~~~~

.. function:: get_settings()

   Get application settings.
   
   :return: Settings object with configuration parameters

.. function:: setup_logging(log_level='INFO')

   Configure logging system.
   
   :param log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
   :return: Configured logger instance

Data Structures
--------------

Signal Data
~~~~~~~~~~~

.. class:: PPGSignal

   Container for PPG signal data.
   
   .. attribute:: time
      Time array in seconds
   
   .. attribute:: red_channel
      RED channel signal data
   
   .. attribute:: ir_channel
      IR channel signal data
   
   .. attribute:: sample_rate
      Sampling rate in Hz

Filter Configuration
~~~~~~~~~~~~~~~~~~~

.. class:: FilterConfig

   Configuration for digital filters.
   
   .. attribute:: filter_type
      Type of filter ('butterworth', 'chebyshev', 'elliptic', 'bessel')
   
   .. attribute:: cutoff_frequency
      Cutoff frequency in Hz
   
   .. attribute:: filter_order
      Filter order (integer)
   
   .. attribute:: filter_design
      Filter design method ('iir' or 'fir')

Analysis Results
~~~~~~~~~~~~~~~

.. class:: AnalysisResult

   Container for analysis results.
   
   .. attribute:: filtered_signal
      Filtered signal data
   
   .. attribute:: frequency_spectrum
      Frequency domain analysis
   
   .. attribute:: quality_metrics
      Signal quality assessment
   
   .. attribute:: heart_rate
      Calculated heart rate

Error Handling
--------------

Custom Exceptions
~~~~~~~~~~~~~~~~

.. exception:: PPGDataError

   Raised when there are issues with PPG data format or content.

.. exception:: FilterConfigurationError

   Raised when filter parameters are invalid or incompatible.

.. exception:: FileProcessingError

   Raised when there are issues reading or processing files.

Usage Examples
--------------

Basic Signal Processing
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.utils.signal_processing import apply_filter
   from src.utils.file_utils import load_ppg_data
   
   # Load data
   data = load_ppg_data('sample_data.csv')
   
   # Apply filter
   filtered_signal = apply_filter(
       data['red_channel'],
       filter_type='butterworth',
       cutoff_freq=10.0,
       filter_order=4,
       sample_rate=data['sample_rate']
   )

Advanced Analysis
~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.utils.ppg_analysis import calculate_heart_rate, compute_signal_quality
   from src.utils.signal_processing import detect_peaks
   
   # Detect peaks
   peaks = detect_peaks(filtered_signal, threshold=0.5, distance=100)
   
   # Calculate heart rate
   hr = calculate_heart_rate(peaks, time_window=60)
   
   # Assess quality
   quality = compute_signal_quality(filtered_signal)

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.config.settings import get_settings
   from src.config.logging_config import setup_logging
   
   # Get settings
   settings = get_settings()
   
   # Setup logging
   logger = setup_logging(settings.log_level)

For more detailed examples, see the :doc:`user_guide` and check the source code in the `src/` directory.

User Guide
==========

This guide will walk you through using the PPG Analysis Tool to analyze photoplethysmogram signals.

Getting Started
--------------

1. **Launch the Application**:
   .. code-block:: bash
      
      python main.py

2. **Open your web browser** and navigate to the URL shown in the terminal (usually `http://127.0.0.1:8050`)

3. **Load your PPG data** using the file upload component

Data Loading
------------

Supported Formats
~~~~~~~~~~~~~~~~

* **CSV files**: Comma-separated values with time series data
* **Excel files**: .xlsx and .xls formats
* **Text files**: Tab or space-separated data

Data Requirements
~~~~~~~~~~~~~~~~

Your data should contain:
* A time column (automatically detected)
* Signal columns (RED/IR channels for PPG data)
* Consistent sampling rate

Column Detection
~~~~~~~~~~~~~~~

The tool automatically detects:
* **Time column**: Based on common naming patterns
* **RED channel**: Usually contains "RED", "red", or similar
* **IR channel**: Usually contains "IR", "ir", or similar

Signal Processing
----------------

Filtering Options
~~~~~~~~~~~~~~~~

The tool provides multiple filter families:

* **Butterworth**: Smooth frequency response, no ripples
* **Chebyshev**: Sharp cutoff with controlled ripples
* **Elliptic**: Sharpest cutoff but with ripples in both passband and stopband
* **Bessel**: Linear phase response, good for preserving signal shape

Filter Parameters
~~~~~~~~~~~~~~~~

* **Cutoff frequency**: Frequency at which the filter starts attenuating
* **Filter order**: Higher orders provide sharper cutoff but more computational cost
* **Filter type**: Low-pass, high-pass, band-pass, or band-stop

Visualization Features
---------------------

Time Domain Analysis
~~~~~~~~~~~~~~~~~~~

* **Raw signal display**: View your original data
* **Filtered signal**: Compare processed vs. raw signals
* **Zoom and pan**: Interactive exploration of your data
* **Multiple channel overlay**: Compare different signals

Frequency Domain Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Power spectral density**: Identify dominant frequencies
* **FFT analysis**: Fast Fourier Transform for frequency components
* **Filter response**: Visualize how your filters affect the signal

Dynamics Analysis
~~~~~~~~~~~~~~~~

* **Signal statistics**: Mean, variance, peak-to-peak amplitude
* **Quality metrics**: Signal-to-noise ratio estimates
* **Trend analysis**: Long-term signal variations

Export and Analysis
------------------

Data Export
~~~~~~~~~~~

* **CSV download**: Save processed data for external analysis
* **Plot export**: Save visualizations as PNG or PDF
* **Parameter export**: Save filter settings and analysis parameters

Advanced Features
----------------

Real-time Processing
~~~~~~~~~~~~~~~~~~~

* **Live parameter adjustment**: Change filter settings and see immediate results
* **Interactive plots**: Click and drag to explore data
* **Parameter optimization**: Automated parameter suggestions

Batch Processing
~~~~~~~~~~~~~~~

* **Multiple file processing**: Analyze multiple datasets simultaneously
* **Parameter presets**: Save and reuse filter configurations
* **Automated reporting**: Generate analysis summaries

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

* **Data not loading**: Check file format and column names
* **Poor filtering results**: Adjust filter parameters or try different filter types
* **Slow performance**: Reduce data size or use simpler filters
* **Visualization issues**: Check browser compatibility and refresh the page

Performance Tips
~~~~~~~~~~~~~~~

* **Use appropriate data sizes**: Very large datasets may slow down processing
* **Choose filter orders wisely**: Higher orders provide better results but slower processing
* **Close other applications**: Free up system resources for better performance

Getting Help
-----------

* **Check the logs**: Look for error messages in the terminal
* **Review sample data**: Use the provided sample data to test functionality
* **Check documentation**: Refer to the :doc:`api_reference` for technical details

Next Steps
----------

* Explore the :doc:`api_reference` for advanced usage
* Check the :doc:`development` guide if you want to contribute
* Review the :doc:`contributing` guidelines for the project

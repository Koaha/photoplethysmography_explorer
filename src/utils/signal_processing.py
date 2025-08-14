"""
Signal processing utilities for PPG analysis.

This module provides core signal processing functions including:
- Safe type conversion with fallback values
- IIR filter design for various filter families
- Signal processing chains (detrend, filter, notch, invert)
- Rate estimation from power spectral density
- Signal-to-noise ratio estimation
- Automatic decimation for display optimization
- Cross-correlation analysis
"""

import numpy as np
from scipy.signal import iirfilter, sosfiltfilt, iirnotch, tf2sos, welch, spectrogram, find_peaks
from scipy.signal import coherence


def safe_float(x, fallback):
    """
    Safely convert input to float with fallback value.
    
    This function attempts to convert the input to a float, returning
    the fallback value if conversion fails. Useful for handling
    user inputs that may be invalid or None.
    
    Args:
        x: Input value to convert to float
        fallback (float): Value to return if conversion fails
        
    Returns:
        float: Converted value or fallback
    """
    try:
        return float(x)
    except Exception:
        return fallback


def safe_int(x, fallback):
    """
    Safely convert input to integer with fallback value.
    
    This function attempts to convert the input to an integer, returning
    the fallback value if conversion fails. Useful for handling
    user inputs that may be invalid or None.
    
    Args:
        x: Input value to convert to integer
        fallback (int): Value to return if conversion fails
        
    Returns:
        int: Converted value or fallback
    """
    try:
        return int(x)
    except Exception:
        return fallback


def design_base_filter(fs, family, resp_type, low_hz, high_hz, order, rp, rs):
    """
    Design IIR filter with specified parameters.
    
    This function creates digital filters using various IIR filter families
    (Butterworth, Chebyshev, Elliptic) with configurable response types
    (lowpass, highpass, bandpass, bandstop).
    
    Args:
        fs (float): Sampling frequency in Hz
        family (str): Filter family ('butter', 'cheby1', 'cheby2', 'ellip', 'bessel')
        resp_type (str): Filter response type ('lowpass', 'highpass', 'bandpass', 'bandstop')
        low_hz (float): Lower cutoff frequency in Hz
        high_hz (float): Upper cutoff frequency in Hz
        order (int): Filter order
        rp (float): Passband ripple in dB (for Chebyshev and Elliptic)
        rs (float): Stopband attenuation in dB (for Chebyshev and Elliptic)
        
    Returns:
        numpy.ndarray: Second-order sections (SOS) filter coefficients
        
    Note:
        - Frequencies are automatically constrained to prevent aliasing
        - For bandpass/bandstop, frequencies are automatically sorted
        - Filter parameters (rp, rs) are only used for relevant filter families
    """
    fs = float(fs)
    nyq = fs / 2.0  # Nyquist frequency
    
    # Validate and constrain cutoff frequencies
    low_hz = max(1e-6, float(low_hz))
    high_hz = max(1e-6, float(high_hz))
    
    # Set up frequency specifications based on response type
    if resp_type in ("lowpass", "highpass"):
        Wn = high_hz if resp_type == "lowpass" else low_hz
        Wn = min(Wn, nyq * 0.999)  # Prevent aliasing
    else:
        # For bandpass/bandstop, sort frequencies and constrain
        lo, hi = sorted([low_hz, high_hz])
        hi = min(hi, nyq * 0.999)  # Prevent aliasing
        lo = max(1e-6, min(lo, hi - 1e-6))  # Ensure valid band
        Wn = [lo, hi]
    
    # Set up filter design parameters
    kwargs = dict(ftype=family, fs=fs, output="sos")
    if family == "cheby1":
        kwargs["rp"] = rp
    elif family == "cheby2":
        kwargs["rs"] = rs
    elif family == "ellip":
        kwargs["rp"] = rp
        kwargs["rs"] = rs
    
    return iirfilter(order, Wn, btype=resp_type, **kwargs)


def apply_chain(x, fs, base_sos=None, notch_enable=False, notch_hz=50.0, notch_q=30.0,
                detrend_mean=False, invert=False):
    """
    Apply signal processing chain: detrend → filter → notch → invert.
    
    This function applies a sequence of signal processing operations in order:
    1. Detrending (remove mean if enabled)
    2. Base filtering (if SOS coefficients provided)
    3. Notch filtering (if enabled)
    4. Signal inversion (if enabled)
    
    Args:
        x (array-like): Input signal
        fs (float): Sampling frequency in Hz
        base_sos (numpy.ndarray, optional): Base filter SOS coefficients
        notch_enable (bool): Whether to enable notch filter
        notch_hz (float): Notch filter center frequency in Hz
        notch_q (float): Notch filter quality factor
        detrend_mean (bool): Whether to remove signal mean
        invert (bool): Whether to invert the signal
        
    Returns:
        numpy.ndarray: Processed signal
        
    Note:
        - All operations are applied in sequence
        - Notch filter is only applied if notch_enable is True
        - Base filter is only applied if base_sos is provided
    """
    y = np.asarray(x, dtype=float)
    
    # Step 1: Detrend (remove mean if requested)
    if detrend_mean:
        y = y - np.mean(y)
    
    # Step 2: Apply base filter if provided
    if base_sos is not None:
        y = sosfiltfilt(base_sos, y)
    
    # Step 3: Apply notch filter if enabled
    if notch_enable and notch_hz > 0:
        b, a = iirnotch(w0=notch_hz, Q=notch_q, fs=fs)
        sos_notch = tf2sos(b, a)
        y = sosfiltfilt(sos_notch, y)
    
    # Step 4: Invert signal if requested
    if invert:
        y = -y
    
    return y


def estimate_rates_psd(sig, fs, band_tuple):
    """
    Estimate rate from PSD peak in specified frequency band.
    
    This function calculates the power spectral density of a signal and
    finds the frequency with maximum power within a specified band.
    Useful for estimating heart rate, respiratory rate, etc.
    
    Args:
        sig (array-like): Input signal
        fs (float): Sampling frequency in Hz
        band_tuple (tuple): (low_freq, high_freq) frequency band in Hz
        
    Returns:
        float or None: Estimated rate in units per minute, or None if estimation fails
        
    Note:
        - Uses Welch's method for PSD estimation
        - Automatically adjusts window size based on signal length
        - Returns rate in units per minute (60 * frequency)
    """
    # Calculate power spectral density using Welch's method
    f, Pxx = welch(sig, fs=fs, nperseg=min(len(sig), 2048))
    lo, hi = band_tuple
    
    # Find frequencies within the specified band
    mask = (f >= lo) & (f <= hi)
    
    if not np.any(mask):
        return None
    
    # Extract power values within the band
    f_band = f[mask]
    P_band = Pxx[mask]
    
    # Check for valid power values
    if len(P_band) == 0 or np.all(np.isnan(P_band)):
        return None
    
    # Find frequency with maximum power
    f_peak = f_band[np.nanargmax(P_band)]
    return 60.0 * f_peak  # Convert to per minute


def quick_snr(sig):
    """
    Quick signal-to-noise ratio estimation.
    
    This function provides a simple estimate of SNR based on the
    peak-to-peak amplitude of the signal. This is a rough approximation
    suitable for quick quality assessment.
    
    Args:
        sig (array-like): Input signal
        
    Returns:
        float or None: Estimated SNR, or None if signal is too short
        
    Note:
        - Uses peak-to-peak amplitude as a simple SNR proxy
        - Returns None for signals with less than 2 samples
        - This is a simplified SNR estimate, not a rigorous calculation
    """
    if len(sig) < 2:
        return None
    
    # Calculate peak-to-peak amplitude as SNR proxy
    ptp = float(np.ptp(sig))
    std = float(np.std(sig))
    
    if std == 0:
        return None
    
    return ptp / (6*std)


def auto_decimation(n, decim_user, traces, cap):
    """Auto-decimate signal for display."""
    target_per = max(1, cap // max(traces, 1))
    d = max(1, int(decim_user))
    
    if n // d > target_per:
        d = int(np.ceil(n / target_per))
    
    return max(1, d)


def cross_correlation_lag(x, y, fs, max_lag_sec=1.0):
    """Compute cross-correlation between two signals."""
    n = min(len(x), len(y))
    if n == 0:
        return None, None, None
    
    max_lag = int(max_lag_sec * fs)
    lags = np.arange(-max_lag, max_lag+1)
    
    # normalize
    x0 = (x - np.mean(x)) / (np.std(x) + 1e-12)
    y0 = (y - np.mean(y)) / (np.std(y) + 1e-12)
    
    corr = np.array([
        np.correlate(x0[max(0,lag):n+min(0,lag)],
                     y0[max(0,-lag):n-min(0,lag)])[0] / (n - abs(lag))
        for lag in lags
    ])
    
    best_idx = int(np.argmax(corr))
    best_lag_s = lags[best_idx] / fs
    
    return lags/fs, corr, best_lag_s

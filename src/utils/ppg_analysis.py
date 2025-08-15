"""
PPG-specific analysis utilities.
"""

import numpy as np
from scipy.signal import find_peaks, welch, spectrogram, coherence


def robust_absorbance(x):
    """Beer–Lambert-ish: A = -log(I / I0); use median as I0, guard zeros."""
    x = np.asarray(x, float)
    I0 = np.median(x) if np.median(x) > 0 else np.maximum(np.mean(x), 1.0)
    return -np.log(np.clip(x / I0, 1e-9, None))


def beats_from_peaks(sig_ac, fs, t_peaks, guard=0.15):
    """Return list of (idx_start, idx_peak, idx_end) for each beat, using midpoints between peaks.
    guard trims edges by a fraction of local IBI."""
    if len(t_peaks) < 2:
        return []

    p = (t_peaks * fs).astype(int)
    ibis = np.diff(p)
    mids = p[:-1] + ibis // 2
    starts = np.r_[max(0, p[0] - int(guard * ibis[0])), mids]
    ends = np.r_[mids, p[-1] + int(guard * ibis[-1])]

    beats = []
    n = len(sig_ac)

    for s, pk, e in zip(starts, p, ends):
        s = int(np.clip(s, 0, n - 2))
        e = int(np.clip(e, s + 1, n - 1))
        beats.append((s, pk, e))

    return beats


def beat_ac_dc(signal_raw, signal_ac, beats, fs, dc_win_s=0.4):
    """Per-beat AC amplitude (peak-to-trough) and local DC (median in ±dc_win_s)."""
    ac, dc, t_mid = [], [], []
    n = len(signal_raw)
    half = int(dc_win_s * fs / 2)

    for s, pk, e in beats:
        seg = signal_ac[s : e + 1]
        if len(seg) < 3:
            continue

        # peak-to-trough in that beat
        a = float(np.max(seg) - np.min(seg))

        # DC as median around peak
        lo = max(0, pk - half)
        hi = min(n, pk + half)
        d = float(np.median(signal_raw[lo:hi])) if hi > lo else float(np.median(signal_raw))

        ac.append(a)
        dc.append(d)
        t_mid.append((s + e) / (2 * fs))

    return np.array(t_mid), np.array(ac), np.array(dc)


def r_series_spo2(red_raw, ir_raw, red_ac, ir_ac, t_peaks, fs):
    """Compute beat-by-beat R ratio and SpO2."""
    beats = beats_from_peaks(ir_ac, fs, t_peaks)  # use IR peaks to segment beats
    if not beats:
        return np.array([]), np.array([]), np.array([])

    t_mid, ac_r, dc_r = beat_ac_dc(red_raw, red_ac, beats, fs)
    _, ac_i, dc_i = beat_ac_dc(ir_raw, ir_ac, beats, fs)

    ok = (ac_r > 0) & (ac_i > 0) & (dc_r > 0) & (dc_i > 0)
    if not np.any(ok):
        return t_mid, np.array([]), np.array([])

    R = ((ac_r / dc_r) / (ac_i / dc_i))[ok]
    tB = t_mid[ok]
    spo2 = -45.06 * R**2 + 30.354 * R + 94.845

    return tB, R, spo2


def avg_beat(signal, t_peaks, fs, width_s=1.2, out_len=200):
    """Ensemble average a window around each peak; return (t_rel, mean, std)."""
    if len(t_peaks) < 2:
        return np.array([]), np.array([]), np.array([])

    half = int(width_s * fs / 2)
    p = (t_peaks * fs).astype(int)
    segs = []

    for pk in p:
        s = max(0, pk - half)
        e = min(len(signal), pk + half)
        seg = signal[s:e]

        if len(seg) < 10:
            continue

        # resample to common length
        xi = np.linspace(0, 1, len(seg))
        x = np.linspace(0, 1, out_len)
        segs.append(np.interp(x, xi, seg))

    if not segs:
        return np.array([]), np.array([]), np.array([])

    M = np.vstack(segs)
    return np.linspace(-width_s / 2, width_s / 2, out_len), M.mean(0), M.std(0)


def ms_coherence(red_ac, ir_ac, fs):
    """Compute magnitude-squared coherence between RED and IR signals."""
    f, C = coherence(red_ac, ir_ac, fs=fs, nperseg=min(len(red_ac), 2048))
    return f, C


def estimate_spo2(red_raw, ir_raw, red_ac, ir_ac):
    """Estimate SpO2, R ratio, and Perfusion Index from windowed data."""
    dc_red, dc_ir = float(np.mean(red_raw)), float(np.mean(ir_raw))
    ac_red_amp, ac_ir_amp = float(np.ptp(red_ac) / 2.0), float(np.ptp(ir_ac) / 2.0)

    if min(dc_red, dc_ir, ac_red_amp, ac_ir_amp) <= 0:
        return None, None, None

    R = (ac_red_amp / dc_red) / (ac_ir_amp / dc_ir)
    spo2 = -45.06 * R**2 + 30.354 * R + 94.845
    PI = 100.0 * (ac_ir_amp / dc_ir)  # perfusion index (%) via IR

    return spo2, R, PI


def compute_hr_trend(ac_signal, fs, hr_min=40, hr_max=180, prom_factor=0.5):
    """Beat detection on AC signal; returns peak times (s), ibi array (s), HR rolling over windows (s, bpm)."""
    if len(ac_signal) < fs:  # too short
        return np.array([]), np.array([]), (np.array([]), np.array([]))

    min_dist = int(max(1, fs * 60.0 / hr_max))
    prom = float(prom_factor) * float(np.std(ac_signal))
    peaks, _ = find_peaks(ac_signal, distance=min_dist, prominence=max(1e-12, prom))

    if len(peaks) < 2:
        return np.array([]), np.array([]), (np.array([]), np.array([]))

    t_peaks = peaks / fs
    ibis = np.diff(t_peaks)  # seconds

    # HR over time: midpoint between consecutive peaks
    hr_t = (t_peaks[:-1] + t_peaks[1:]) / 2.0
    hr_bpm = 60.0 / np.clip(ibis, 1e-6, None)

    # mask outside HR band
    hr_mask = (hr_bpm >= hr_min) & (hr_bpm <= hr_max)

    return t_peaks, ibis, (hr_t[hr_mask], hr_bpm[hr_mask])


def sdppg(x):
    """Compute second derivative (SDPPG) of signal."""
    return np.gradient(np.gradient(x))

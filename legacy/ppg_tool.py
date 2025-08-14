# app_ppg_windowed_insights.py
import base64, io, os, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import iirfilter, sosfiltfilt, iirnotch, tf2sos, welch, spectrogram, find_peaks
from scipy.signal import coherence

import dash
from dash import dcc, html, Input, Output, State, callback_context, no_update
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --------------------
# Defaults / Limits
# --------------------
DEFAULT_FS = 100.0
DEFAULT_FILE_ON_DISK = "PPG.csv"   # optional auto-load if present
DEFAULT_WINDOW_START = 0
DEFAULT_WINDOW_END = 9_999         # ≈ 10k rows by default
MAX_DISPLAY_POINTS = 300_000       # higher cap to allow bigger visuals
DEFAULT_DECIM_USER = 1

# HR/peaks defaults
DEFAULT_HR_MIN = 40
DEFAULT_HR_MAX = 180
DEFAULT_PEAK_PROM_FACTOR = 0.5     # peaks prominence = factor * std(AC)

# Spectrogram defaults
DEFAULT_SPEC_WIN_SEC = 2.0
DEFAULT_SPEC_OVERLAP = 0.5

# --------------------
# Helpers
# --------------------
def safe_float(x, fallback):
    try: return float(x)
    except Exception: return fallback

def safe_int(x, fallback):
    try: return int(x)
    except Exception: return fallback

def robust_absorbance(x):
    # Beer–Lambert-ish: A = -log(I / I0); use median as I0, guard zeros
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
    starts = np.r_[max(0, p[0] - int(guard*ibis[0])), mids]
    ends   = np.r_[mids, p[-1] + int(guard*ibis[-1])]
    beats = []
    n = len(sig_ac)
    for s, pk, e in zip(starts, p, ends):
        s = int(np.clip(s, 0, n-2))
        e = int(np.clip(e, s+1, n-1))
        beats.append((s, pk, e))
    return beats

def beat_ac_dc(signal_raw, signal_ac, beats, fs, dc_win_s=0.4):
    """Per-beat AC amplitude (peak-to-trough) and local DC (median in ±dc_win_s)."""
    ac, dc, t_mid = [], [], []
    n = len(signal_raw); half = int(dc_win_s*fs/2)
    for s, pk, e in beats:
        seg = signal_ac[s:e+1]
        if len(seg) < 3:
            continue
        # peak-to-trough in that beat
        a = float(np.max(seg) - np.min(seg))
        # DC as median around peak
        lo = max(0, pk - half); hi = min(n, pk + half)
        d = float(np.median(signal_raw[lo:hi])) if hi > lo else float(np.median(signal_raw))
        ac.append(a); dc.append(d); t_mid.append( (s+e)/(2*fs) )
    return np.array(t_mid), np.array(ac), np.array(dc)

def r_series_spo2(red_raw, ir_raw, red_ac, ir_ac, t_peaks, fs):
    beats = beats_from_peaks(ir_ac, fs, t_peaks)  # use IR peaks to segment beats
    if not beats: 
        return np.array([]), np.array([]), np.array([])
    t_mid, ac_r, dc_r = beat_ac_dc(red_raw, red_ac, beats, fs)
    _,     ac_i, dc_i = beat_ac_dc(ir_raw,  ir_ac,  beats, fs)
    ok = (ac_r>0) & (ac_i>0) & (dc_r>0) & (dc_i>0)
    if not np.any(ok):
        return t_mid, np.array([]), np.array([])
    R = ( (ac_r/dc_r) / (ac_i/dc_i) )[ok]
    tB = t_mid[ok]
    spo2 = -45.06*R**2 + 30.354*R + 94.845
    return tB, R, spo2

def avg_beat(signal, t_peaks, fs, width_s=1.2, out_len=200):
    """Ensemble average a window around each peak; return (t_rel, mean, std)."""
    if len(t_peaks) < 2: 
        return np.array([]), np.array([]), np.array([])
    half = int(width_s*fs/2)
    p = (t_peaks*fs).astype(int)
    segs = []
    for pk in p:
        s = max(0, pk-half); e = min(len(signal), pk+half)
        seg = signal[s:e]
        if len(seg) < 10: 
            continue
        # resample to common length
        xi = np.linspace(0, 1, len(seg))
        x  = np.linspace(0, 1, out_len)
        segs.append(np.interp(x, xi, seg))
    if not segs: 
        return np.array([]), np.array([]), np.array([])
    M = np.vstack(segs)
    return np.linspace(-width_s/2, width_s/2, out_len), M.mean(0), M.std(0)

def ms_coherence(red_ac, ir_ac, fs):
    f, C = coherence(red_ac, ir_ac, fs=fs, nperseg=min(len(red_ac), 2048))
    return f, C


def count_rows_quick(path):
    with open(path, "rb") as f:
        total_lines = sum(1 for _ in f)
    return max(0, total_lines - 1)

def get_columns_only(path):
    return list(pd.read_csv(path, nrows=0).columns)

def parse_uploaded_csv_to_temp(contents, filename):
    if not contents: return None
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    suffix = ".csv" if not filename else f".{filename.split('.')[-1]}"
    fd, tmp_path = tempfile.mkstemp(prefix="ppg_", suffix=suffix)
    os.close(fd)
    with open(tmp_path, "wb") as f:
        f.write(decoded)
    return tmp_path

def read_window(path, cols, start_row, end_row):
    start_row = max(0, int(start_row))
    end_row = max(start_row, int(end_row))
    nrows = end_row - start_row + 1
    skip = range(1, 1 + start_row) if start_row > 0 else None
    return pd.read_csv(path, usecols=cols, skiprows=skip, nrows=nrows)

def design_base_filter(fs, family, resp_type, low_hz, high_hz, order, rp, rs):
    fs = float(fs); nyq = fs / 2.0
    low_hz = max(1e-6, float(low_hz))
    high_hz = max(1e-6, float(high_hz))
    if resp_type in ("lowpass", "highpass"):
        Wn = high_hz if resp_type == "lowpass" else low_hz
        Wn = min(Wn, nyq * 0.999)
    else:
        lo, hi = sorted([low_hz, high_hz])
        hi = min(hi, nyq * 0.999)
        lo = max(1e-6, min(lo, hi - 1e-6))
        Wn = [lo, hi]
    kwargs = dict(ftype=family, fs=fs, output="sos")
    if family == "cheby1": kwargs["rp"] = rp
    elif family == "cheby2": kwargs["rs"] = rs
    elif family == "ellip": kwargs["rp"] = rp; kwargs["rs"] = rs
    return iirfilter(order, Wn, btype=resp_type, **kwargs)

def apply_chain(x, fs, base_sos=None, notch_enable=False, notch_hz=50.0, notch_q=30.0,
                detrend_mean=False, invert=False):
    y = np.asarray(x, dtype=float)
    if detrend_mean: y = y - np.mean(y)
    if base_sos is not None: y = sosfiltfilt(base_sos, y)
    if notch_enable and notch_hz > 0:
        b, a = iirnotch(w0=notch_hz, Q=notch_q, fs=fs)
        sos_notch = tf2sos(b, a)
        y = sosfiltfilt(sos_notch, y)
    if invert: y = -y
    return y

def estimate_spo2(red_raw, ir_raw, red_ac, ir_ac):
    dc_red, dc_ir = float(np.mean(red_raw)), float(np.mean(ir_raw))
    ac_red_amp, ac_ir_amp = float(np.ptp(red_ac)/2.0), float(np.ptp(ir_ac)/2.0)
    if min(dc_red, dc_ir, ac_red_amp, ac_ir_amp) <= 0: return None, None, None
    R = (ac_red_amp/dc_red) / (ac_ir_amp/dc_ir)
    spo2 = -45.06 * R**2 + 30.354 * R + 94.845
    PI = 100.0 * (ac_ir_amp / dc_ir)  # perfusion index (%) via IR
    return spo2, R, PI

def estimate_rates_psd(sig, fs, band_tuple):
    f, Pxx = welch(sig, fs=fs, nperseg=min(len(sig), 2048))
    lo, hi = band_tuple
    mask = (f >= lo) & (f <= hi)
    if not np.any(mask): return None
    f_band = f[mask]; P_band = Pxx[mask]
    if len(P_band) == 0 or np.all(np.isnan(P_band)): return None
    f_peak = f_band[np.nanargmax(P_band)]
    return 60.0 * f_peak  # per minute

def quick_snr(sig):
    if len(sig) < 2: return None
    ptp = float(np.ptp(sig)); std = float(np.std(sig))
    if std == 0: return None
    return ptp / (6*std)

def auto_decimation(n, decim_user, traces, cap=MAX_DISPLAY_POINTS):
    target_per = max(1, cap // max(traces, 1))
    d = max(1, int(decim_user))
    if n // d > target_per:
        d = int(np.ceil(n / target_per))
    return max(1, d)

def compute_hr_trend(ac_signal, fs, hr_min=DEFAULT_HR_MIN, hr_max=DEFAULT_HR_MAX, prom_factor=DEFAULT_PEAK_PROM_FACTOR):
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

def cross_correlation_lag(x, y, fs, max_lag_sec=1.0):
    n = min(len(x), len(y))
    if n == 0: return None, None, None
    max_lag = int(max_lag_sec * fs)
    lags = np.arange(-max_lag, max_lag+1)
    # normalize
    x0 = (x - np.mean(x)) / (np.std(x) + 1e-12)
    y0 = (y - np.mean(y)) / (np.std(y) + 1e-12)
    corr = np.array([np.correlate(x0[max(0,lag):n+min(0,lag)],
                                  y0[max(0,-lag):n-min(0,lag)])[0] / (n - abs(lag))
                     for lag in lags])
    best_idx = int(np.argmax(corr))
    best_lag_s = lags[best_idx] / fs
    return lags/fs, corr, best_lag_s

# Auto file if present
auto_file = str(Path(DEFAULT_FILE_ON_DISK).resolve()) if Path(DEFAULT_FILE_ON_DISK).exists() else None

# --------------------
# Dash App + Style (plots wider/taller)
# --------------------
app = dash.Dash(__name__)
app.title = "PPG Filter Lab — Window Mode (Wide)"

app.index_string = """
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>PPG Filter Lab — Window Mode (Wide)</title>
    {%favicon%}
    {%css%}
    <style>
        body { font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
               background:#0f172a; color:#e2e8f0; margin:0; }
        .wrap { max-width: 1760px; margin: 24px auto; padding: 0 16px; }
        .header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
        .title { font-size: 24px; font-weight: 700; }
        .subtle { color:#94a3b8; }
        /* Make the plots column wider */
        .grid { display:grid; grid-template-columns: 340px 2.1fr 0.9fr; gap: 18px; }
        .card { background:#111827; border:1px solid #1f2937; border-radius:14px; padding:14px;
                box-shadow: 0 6px 18px rgba(0,0,0,.35); }
        .section-title { font-size:13px; text-transform:uppercase; color:#93c5fd; letter-spacing:.12em; margin: 6px 0 10px; }
        .row { display:flex; gap:10px; align-items:center; flex-wrap: wrap; }
        label { font-size: 12px; color:#a5b4fc; }
        .hint { font-size: 12px; color:#94a3b8; }
        input, select { background:#0b1220; color:#e2e8f0; border:1px solid #23324a; border-radius:8px; padding:8px 10px; }
        .btn { background:#2563eb; border:none; color:#fff; padding:8px 12px; border-radius:10px; cursor:pointer; }
        .btn.secondary { background:#334155; }
        .pill { background:#0b1220; border:1px solid #23324a; border-radius:999px; padding:4px 8px; font-size:12px; }
        .upload { border: 1px dashed #334155; padding: 12px; border-radius: 12px; text-align:center; color:#94a3b8; }
        .upload:hover { background:#0b1220; }
    </style>
</head>
<body>
    <div class="wrap">
        {%app_entry%}
    </div>
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
"""

app.layout = html.Div([
    # Stores
    dcc.Store(id="store_file_path"),
    dcc.Store(id="store_total_rows"),
    dcc.Store(id="store_window"),  # {"start": int, "end": int}
    dcc.Store(id="store_theme", data="dark"),
    dcc.Store(id="store_prev_total_rows"),

    html.Div(className="header", children=[
        html.Div(className="title", children="PPG Filter Lab — Window Mode (Wide + Insights)"),
        html.Div(className="subtle", children="Load CSV • Select row window • Bigger plots • Extra insight visuals")
    ]),

    html.Div(className="grid", children=[
        # ---------------- Left: Data & Filter ----------------
        html.Div(className="card", children=[
            html.Div(className="section-title", children="Data"),
            html.Div(className="row", children=[
                html.Div(children=[
                    html.Label("Load from local path"),
                    dcc.Input(id="file_path", type="text", placeholder="e.g., PPG.csv",
                              value=auto_file or "", style={"width":"220px"}),
                ]),
                html.Button("Load", id="btn_load_path", className="btn", n_clicks=0),
            ]),
            html.Div(style={"height":"8px"}),
            dcc.Upload(
                id='upload_csv',
                children=html.Div(["⬆️ ", html.Span("Drag & drop or click to upload CSV")]),
                multiple=False,
                className="upload"
            ),
            html.Div(id="file_status", className="hint", style={"marginTop":"6px"}),

            html.Div(style={"height":"10px"}),
            html.Label("Column mapping"),
            html.Div(className="row", children=[
                html.Div(children=["RED",
                    dcc.Dropdown(id="red_col", options=[], value=None, style={"width":"280px"})]),
            ]),
            html.Div(className="row", style={"marginTop":"6px"}, children=[
                html.Div(children=["IR",
                    dcc.Dropdown(id="ir_col", options=[], value=None, style={"width":"280px"})]),
            ]),

            html.Div(style={"height":"10px"}),
            html.Label("Sampling frequency (Hz)"),
            dcc.Input(id="fs", type="number", value=DEFAULT_FS, step=0.5, min=1, style={"width":"120px"}),

            html.Div(style={"height":"10px"}),
            html.Label("Theme"),
            dcc.Dropdown(id="theme",
                options=[{"label":"Dark","value":"dark"},{"label":"Light","value":"light"}],
                value="dark", clearable=False, style={"width":"160px"}),

            html.Div(style={"height":"16px"}),
            html.Div(className="section-title", children="Window (rows)"),
            html.Div(className="row", children=[
                html.Div(children=[html.Div("start_row"), dcc.Input(id="start_row", type="number", value=DEFAULT_WINDOW_START, min=0, step=100)]),
                html.Div(children=[html.Div("end_row"),   dcc.Input(id="end_row", type="number", value=DEFAULT_WINDOW_END,   min=0, step=100)]),
                html.Button("Apply", id="btn_apply_window", className="btn", n_clicks=0),
            ]),
            html.Div(className="row", style={"marginTop":"6px"}, children=[
                html.Button("−10k", id="nudge_m10k", className="btn secondary", n_clicks=0),
                html.Button("−1k",  id="nudge_m1k",  className="btn secondary", n_clicks=0),
                html.Button("+1k",  id="nudge_p1k",  className="btn secondary", n_clicks=0),
                html.Button("+10k", id="nudge_p10k", className="btn secondary", n_clicks=0),
                html.Div(id="window_badge", className="pill", children="Rows: 0–0"),
            ]),
            html.Div(style={"height":"8px"}),
            # dcc.RangeSlider(id="row_slider", min=0, max=10000, step=1, value=[0, 10000]),
            dcc.RangeSlider(id="row_slider", min=0, max=10000, step=1, value=[0, 10000], allowCross=False, pushable=100, updatemode="mouseup"),


            html.Div(style={"height":"16px"}),
            html.Div(className="section-title", children="Filter"),
            html.Div(className="row", children=[
                dcc.Dropdown(
                    id="family", value="butter",
                    options=[{"label":"Butterworth","value":"butter"},
                             {"label":"Chebyshev I","value":"cheby1"},
                             {"label":"Chebyshev II","value":"cheby2"},
                             {"label":"Elliptic","value":"ellip"},
                             {"label":"Bessel","value":"bessel"}],
                    clearable=False, style={"width":"160px"}
                ),
                dcc.Dropdown(
                    id="resp", value="bandpass",
                    options=[{"label":"Bandpass","value":"bandpass"},
                             {"label":"Bandstop (Notch)","value":"bandstop"},
                             {"label":"Lowpass","value":"lowpass"},
                             {"label":"Highpass","value":"highpass"}],
                    clearable=False, style={"width":"170px"}
                )
            ]),
            html.Div(className="row"),  # (Note: keep syntax valid if you edit)
        ]),

        # ---------------- Middle: Charts (wider/taller) ----------------
        html.Div(children=[
            dcc.Tabs(id="main_charts_tabs", value="time_domain", children=[
                dcc.Tab(label="Time-domain", value="time_domain", children=[
                    html.Div(className="card", children=[
                        html.Div(className="section-title", children="Time-domain (bigger)"),
                        dcc.Loading(dcc.Graph(id="fig_raw", style={"height":"420px"}), type="default"),
                        dcc.Loading(dcc.Graph(id="fig_ac",  style={"height":"420px"}), type="default"),
                    ]),
                ]),
                dcc.Tab(label="Frequency", value="frequency", children=[
                    html.Div(className="card", children=[
                        html.Div(className="section-title", children="Frequency"),
                        dcc.Loading(dcc.Graph(id="fig_psd", style={"height":"360px"}), type="default"),
                        html.Div(className="row", children=[
                            html.Div(children=[html.Div("Spectrogram win (s)"),
                                dcc.Input(id="spec_win_sec", type="number", value=DEFAULT_SPEC_WIN_SEC, min=0.5, step=0.5, style={"width":"100px"})]),
                            html.Div(children=[html.Div("Overlap (0–0.95)"),
                                dcc.Input(id="spec_overlap", type="number", value=DEFAULT_SPEC_OVERLAP, min=0.0, max=0.95, step=0.05, style={"width":"100px"})]),
                            html.Div(children=[html.Div("Show spectrogram"),
                                dcc.Checklist(id="show_spec", options=[{"label":"Enable","value":"on"}], value=["on"])]),
                        ], style={"margin":"6px 0"}),
                        dcc.Loading(dcc.Graph(id="fig_spec", style={"height":"380px"}), type="default"),
                    ]),
                ]),
                dcc.Tab(label="Dual-source analytics", value="dual_source", children=[
                    html.Div(className="card", children=[
                        html.Div(className="section-title", children="Dual-source analytics"),
                        dcc.Tabs(id="dual_source_tabs", value="rtrend", children=[
                            dcc.Tab(label="R-trend & SpO₂", value="rtrend", children=[
                                dcc.Loading(dcc.Graph(id="fig_rtrend", style={"height":"320px"}), type="default")
                            ]),
                            dcc.Tab(label="Coherence", value="coh", children=[
                                dcc.Loading(dcc.Graph(id="fig_coh", style={"height":"300px"}), type="default")
                            ]),
                            dcc.Tab(label="Lissajous", value="liss", children=[
                                dcc.Loading(dcc.Graph(id="fig_liss", style={"height":"300px"}), type="default")
                            ]),
                            dcc.Tab(label="Average Beat", value="avgbeat", children=[
                                dcc.Loading(dcc.Graph(id="fig_avgbeat", style={"height":"300px"}), type="default")
                            ]),
                            dcc.Tab(label="SDPPG", value="sdppg", children=[
                                dcc.Loading(dcc.Graph(id="fig_sdppg", style={"height":"300px"}), type="default")
                            ]),
                        ]),
                    ]),
                ]),
                dcc.Tab(label="Dynamics (HR/IBI)", value="dynamics", children=[
                    html.Div(className="card", children=[
                        html.Div(className="section-title", children="Dynamics (HR/IBI)"),
                        html.Div(className="row", children=[
                            html.Div(children=[html.Div("HR source"), dcc.Dropdown(id="hr_source",
                                options=[{"label":"IR (default)","value":"ir"}, {"label":"RED","value":"red"}],
                                value="ir", clearable=False, style={"width":"140px"})]),
                            html.Div(children=[html.Div("HR min/max (bpm)"),
                                dcc.Input(id="hr_min", type="number", value=DEFAULT_HR_MIN, min=20, step=5, style={"width":"80px"}),
                                dcc.Input(id="hr_max", type="number", value=DEFAULT_HR_MAX, min=60, step=5, style={"width":"80px"})]),
                            html.Div(children=[html.Div("Peak prom ×std"),
                                dcc.Input(id="peak_prom", type="number", value=DEFAULT_PEAK_PROM_FACTOR, min=0.1, step=0.1, style={"width":"80px"})]),
                            html.Div(children=[html.Div("Show advanced"),
                                dcc.Checklist(id="show_adv", options=[
                                    {"label":"HR trend","value":"hr"},
                                    {"label":"IBI hist","value":"hist"},
                                    {"label":"Poincaré","value":"poi"},
                                    {"label":"Cross-corr","value":"xcorr"}],
                                    value=["hr","hist","poi","xcorr"])]),
                        ]),
                        dcc.Tabs(id="dynamics_tabs", value="hr", children=[
                            dcc.Tab(label="HR Trend", value="hr", children=[
                                dcc.Loading(dcc.Graph(id="fig_hr_trend", style={"height":"320px"}), type="default")
                            ]),
                            dcc.Tab(label="IBI Histogram", value="hist", children=[
                                dcc.Loading(dcc.Graph(id="fig_ibi_hist", style={"height":"280px"}), type="default")
                            ]),
                            dcc.Tab(label="Poincaré", value="poi", children=[
                                dcc.Loading(dcc.Graph(id="fig_poincare", style={"height":"280px"}), type="default")
                            ]),
                            dcc.Tab(label="Cross-correlation", value="xcorr", children=[
                                dcc.Loading(dcc.Graph(id="fig_xcorr", style={"height":"280px"}), type="default")
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),

        # ---------------- Right: Insights & Export ----------------
        html.Div(children=[
            html.Div(className="card", children=[
                html.Div(className="section-title", children="Filter Controls (cont'd)"),
                html.Div(className="row", children=[
                    html.Div(children=[html.Div("Low (Hz)"),  dcc.Input(id="low_hz", type="number", value=0.5, step=0.1, min=0)]),
                    html.Div(children=[html.Div("High (Hz)"), dcc.Input(id="high_hz", type="number", value=5.0, step=0.1, min=0.1)]),
                ]),
                html.Div(style={"height":"6px"}),
                html.Div(children=[html.Div("Order"),
                    dcc.Slider(id="order", min=1, max=10, step=1, value=2, marks={i: str(i) for i in range(1,11)})]),
                html.Div(style={"height":"10px"}),
                html.Label("Ripple (Cheby/Ellip)"),
                html.Div(className="row", children=[
                    html.Div(children=[html.Div("rp (dB)"), dcc.Input(id="rp", type="number", value=1.0, step=0.1, min=0.01, style={"width":"90px"})]),
                    html.Div(children=[html.Div("rs (dB)"), dcc.Input(id="rs", type="number", value=40.0, step=1, min=10, style={"width":"90px"})]),
                ]),
                html.Div(style={"height":"10px"}),
                html.Label("Line-noise notch"),
                html.Div(className="row", children=[
                    dcc.Checklist(id="notch_enable", options=[{"label":"Enable","value":"on"}], value=[]),
                    dcc.Dropdown(id="notch_hz", value=50.0,
                        options=[{"label":"50 Hz","value":50.0},{"label":"60 Hz","value":60.0}],
                        clearable=False, style={"width":"110px"}),
                    html.Div(children=[html.Div("Q"), dcc.Input(id="notch_q", type="number", value=30.0, step=1, min=5, style={"width":"90px"})]),
                ]),
                html.Div(style={"height":"10px"}),
                html.Label("Display decimation (auto-ups if needed)"),
                dcc.Input(id="decim", type="number", value=DEFAULT_DECIM_USER, min=1, step=1, style={"width":"120px"}),
                html.Div(style={"height":"10px"}),
                dcc.Checklist(
                    id="flags",
                    options=[{"label":"Detrend (remove mean)","value":"detrend"},
                             {"label":"Invert filtered AC (pulse up)","value":"invert"}],
                    value=["invert"]
                ),
            ]),
            html.Div(style={"height":"12px"}),
            html.Div(className="card", children=[
                html.Div(className="section-title", children="Insights"),
                html.Div(id="insights", className="row", style={"flexWrap":"wrap", "gap":"10px"}),
                html.Div(id="notes", className="hint", style={"marginTop":"10px"})
            ]),
            html.Div(style={"height":"12px"}),
            html.Div(className="card", children=[
                html.Div(className="section-title", children="File / Window / Export"),
                html.Div(id="file_info", className="row", style={"flexWrap":"wrap", "gap":"10px"}),
                html.Div(style={"height":"8px"}),
                html.Button("Download current window (CSV)", id="btn_dl_csv", className="btn", n_clicks=0),
                dcc.Download(id="dl_csv")
            ]),
        ])
    ])
])

# --------------------
# Callbacks
# --------------------
@app.callback(
    Output("store_file_path", "data"),
    Output("store_total_rows", "data"),
    Output("file_status", "children"),
    Output("red_col", "options"),
    Output("ir_col", "options"),
    Output("red_col", "value"),
    Output("ir_col", "value"),
    Output("store_window", "data"),
    Input("btn_load_path", "n_clicks"),
    Input("upload_csv", "contents"),
    State("upload_csv", "filename"),
    State("file_path", "value"),
    prevent_initial_call=False
)
def load_data(n_clicks_path, upload_contents, upload_filename, file_path):
    trig = callback_context.triggered[0]["prop_id"] if callback_context.triggered else ""
    path = None
    status = "No data loaded."

    if "upload_csv.contents" in trig and upload_contents:
        path = parse_uploaded_csv_to_temp(upload_contents, upload_filename or "uploaded.csv")
        status = f"Uploaded: {Path(path).name} → temp"
    elif "btn_load_path.n_clicks" in trig and (file_path or "").strip():
        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return no_update, no_update, f"File not found: {file_path}", [], [], None, None, no_update
        path = str(p); status = f"Loaded from path: {p}"
    else:
        if auto_file:
            path = auto_file
            status = f"Auto-loaded: {Path(path).name}"
        else:
            return None, None, status, [], [], None, None, None

    cols = get_columns_only(path)
    opts = [{"label": c, "value": c} for c in cols]
    red_guess = next((c for c in cols if "red" in c.lower()), cols[0] if cols else None)
    ir_guess  = next((c for c in cols if "ir"  in c.lower()), cols[0] if cols else None)

    total = count_rows_quick(path)
    end_default = min(DEFAULT_WINDOW_END, max(0, total - 1))
    window = {"start": DEFAULT_WINDOW_START, "end": end_default}

    status += f" • total rows ≈ {total:,} • default window {window['start']:,}–{window['end']:,}"
    return path, total, status, opts, opts, red_guess, ir_guess, window

# --- One-way window state <-> controls/slider (prevents loops) ---
@app.callback(
    Output("store_window", "data", allow_duplicate=True),
    Output("row_slider", "value", allow_duplicate=True),
    Output("row_slider", "min", allow_duplicate=True),
    Output("row_slider", "max", allow_duplicate=True),
    Input("btn_apply_window", "n_clicks"),
    Input("nudge_m10k", "n_clicks"),
    Input("nudge_m1k", "n_clicks"),
    Input("nudge_p1k", "n_clicks"),
    Input("nudge_p10k", "n_clicks"),
    State("store_window", "data"),
    State("start_row", "value"),
    State("end_row", "value"),
    State("store_total_rows", "data"),
    prevent_initial_call=True
)
def window_controls(n_apply, nm10, nm1, np1, np10, window, start_in, end_in, total_rows):
    ctx = callback_context
    trig = ctx.triggered[0]["prop_id"] if ctx.triggered else ""
    total = int(total_rows or 0)
    if not window: window = {"start": 0, "end": 9999}
    start, end = int(window["start"]), int(window["end"])

    if trig == "btn_apply_window.n_clicks":
        start = int(start_in or 0); end = int(end_in or start)
    elif trig == "nudge_m10k.n_clicks":
        start -= 10_000; end -= 10_000
    elif trig == "nudge_m1k.n_clicks":
        start -= 1_000; end -= 1_000
    elif trig == "nudge_p1k.n_clicks":
        start += 1_000; end += 1_000
    elif trig == "nudge_p10k.n_clicks":
        start += 10_000; end += 10_000
    else:
        return no_update, no_update, no_update, no_update

    if total > 0:
        start = max(0, min(start, total - 1))
        end   = max(start, min(end, total - 1))
    
    # Update slider bounds and value in the same callback
    slider_min = 0
    slider_max = max(1, total - 1) if total > 0 else 10000
    slider_value = [start, end]
    
    return {"start": start, "end": end}, slider_value, slider_min, slider_max


@app.callback(
    Output("window_badge", "children"),
    Output("start_row", "value"),
    Output("end_row", "value"),
    Output("store_prev_total_rows", "data"),
    Input("store_window", "data"),
    State("store_total_rows", "data"),
    State("store_prev_total_rows", "data"),
    prevent_initial_call=False
)
def reflect_window(window, total_rows, prev_total):
    total = int(total_rows or 0)
    if not window:
        return "Rows: 0–0", 0, 0, total

    start = int(window.get("start", 0))
    end   = int(window.get("end", start))
    if total > 0:
        start = max(0, min(start, total - 1))
        end   = max(start, min(end, total - 1))
    badge = f"Rows: {start:,}–{end:,}"

    return badge, start, end, total


# Handle slider changes from user interaction
@app.callback(
    Output("store_window", "data", allow_duplicate=True),
    Input("row_slider", "value"),
    State("store_window", "data"),
    prevent_initial_call=True
)
def handle_slider_change(slider_value, current_window):
    if not slider_value or len(slider_value) != 2:
        return no_update
    
    start, end = int(slider_value[0]), int(slider_value[1])
    
    # Only update if the slider value actually changed the window
    if (current_window and 
        current_window.get("start") == start and 
        current_window.get("end") == end):
        return no_update
    
    return {"start": start, "end": end}


# --- Charts + Insights + Export ---
@app.callback(
    Output("fig_raw", "figure"),
    Output("fig_ac", "figure"),
    Output("fig_psd", "figure"),
    Output("fig_spec", "figure"),
    Output("fig_hr_trend", "figure"),
    Output("fig_ibi_hist", "figure"),
    Output("fig_poincare", "figure"),
    Output("fig_xcorr", "figure"),
    Output("insights", "children"),
    Output("file_info", "children"),
    Output("dl_csv", "data"),
    Output("fig_rtrend", "figure"),
    Output("fig_coh", "figure"),
    Output("fig_liss", "figure"),
    Output("fig_avgbeat", "figure"),
    Output("fig_sdppg", "figure"),
    Input("store_file_path", "data"),
    Input("store_total_rows", "data"),
    Input("store_window", "data"),
    Input("red_col", "value"),
    Input("ir_col", "value"),
    Input("fs", "value"),
    Input("decim", "value"),
    Input("family", "value"),
    Input("resp", "value"),
    Input("low_hz", "value"),
    Input("high_hz", "value"),
    Input("order", "value"),
    Input("rp", "value"),
    Input("rs", "value"),
    Input("notch_enable", "value"),
    Input("notch_hz", "value"),
    Input("notch_q", "value"),
    Input("flags", "value"),
    Input("theme", "value"),
    Input("spec_win_sec", "value"),
    Input("spec_overlap", "value"),
    Input("show_spec", "value"),
    Input("hr_source", "value"),
    Input("hr_min", "value"),
    Input("hr_max", "value"),
    Input("peak_prom", "value"),
    Input("show_adv", "value"),
    Input("btn_dl_csv", "n_clicks"),
    Input("dual_source_tabs", "value"),
    Input("dynamics_tabs", "value"),
    Input("main_charts_tabs", "value"),
    prevent_initial_call=False
)
def update_plots(path, total_rows, window, red_col, ir_col, fs, decim_user,
                 family, resp, low_hz, high_hz, order, rp, rs,
                 notch_enable, notch_hz, notch_q, flags, theme,
                 spec_win_sec, spec_overlap, show_spec,
                 hr_source, hr_min, hr_max, peak_prom, show_adv, n_dl,
                 dual_source_tab, dynamics_tab, main_tab):

    template = "plotly_dark" if theme == "dark" else "plotly"
    
    # Set default tab values if None
    dual_source_tab = dual_source_tab or "rtrend"
    dynamics_tab = dynamics_tab or "hr"
    main_tab = main_tab or "time_domain"
    
    def blank(h=300):
        f = go.Figure(); f.update_layout(template=template, height=h,
                                         paper_bgcolor="#111827" if theme=="dark" else None,
                                         plot_bgcolor="#0b1220" if theme=="dark" else None)
        return f

    # Precheck
    if not path or not window or red_col is None or ir_col is None:
        # Build blanks with correct heights (so layout stays steady)
        fig_blank_420 = blank(420)
        fig_blank_380 = blank(380)
        fig_blank_360 = blank(360)
        fig_blank_320 = blank(320)
        fig_blank_300 = blank(300)
        fig_blank_280 = blank(280)

        # Example for 'precheck' branch:
        msg = [html.Span("Load a CSV and pick columns/window.", className="pill")]
        return (
            fig_blank_420, fig_blank_420, fig_blank_360, fig_blank_380,   # 1–4
            fig_blank_320, fig_blank_280, fig_blank_280, fig_blank_280,   # 5–8
            msg, [], None,                                                # 9–11
            fig_blank_320, fig_blank_300, fig_blank_300,                  # 12–14
            fig_blank_300, fig_blank_300                                  # 15–16
        )


    fs = safe_float(fs, DEFAULT_FS)
    decim_user = max(1, safe_int(decim_user, DEFAULT_DECIM_USER))
    start, end = int(window["start"]), int(window["end"])
    total = int(total_rows or 0)

    # Read window
    try:
        df = read_window(path, [red_col, ir_col], start, end).dropna()
    except Exception as e:
        msg = [html.Span(f"Read error: {e}", className="pill")]
        fig_blank_420 = blank(420)
        fig_blank_380 = blank(380)
        fig_blank_360 = blank(360)
        fig_blank_320 = blank(320)
        fig_blank_300 = blank(300)
        fig_blank_280 = blank(280)

        return (
            fig_blank_420, fig_blank_420, fig_blank_360, fig_blank_380,   # 1–4
            fig_blank_320, fig_blank_280, fig_blank_280, fig_blank_280,   # 5–8
            msg, [], None,                                                # 9–11
            fig_blank_320, fig_blank_300, fig_blank_300,                  # 12–14
            fig_blank_300, fig_blank_300                                  # 15–16
        )

    if df.empty:
        msg = [html.Span("Empty window.", className="pill")]
        fig_blank_420 = blank(420)
        fig_blank_380 = blank(380)
        fig_blank_360 = blank(360)
        fig_blank_320 = blank(320)
        fig_blank_300 = blank(300)
        fig_blank_280 = blank(280)

        return (
            fig_blank_420, fig_blank_420, fig_blank_360, fig_blank_380,   # 1–4
            fig_blank_320, fig_blank_280, fig_blank_280, fig_blank_280,   # 5–8
            msg, [], None,                                                # 9–11
            fig_blank_320, fig_blank_300, fig_blank_300,                  # 12–14
            fig_blank_300, fig_blank_300                                  # 15–16
        )

    red = df[red_col].astype(float).to_numpy()
    ir  = df[ir_col].astype(float).to_numpy()
    n = len(df)
    t = np.arange(n) / fs

    # Filter design & apply
    order = max(1, safe_int(order, 2))
    rp = safe_float(rp, 1.0); rs = safe_float(rs, 40.0)
    low_hz = safe_float(low_hz, 0.5); high_hz = safe_float(high_hz, 5.0)
    invert = "invert" in (flags or []); detrend = "detrend" in (flags or [])
    notch_on = ("on" in (notch_enable or []))
    notch_hz = safe_float(notch_hz, 50.0); notch_q = safe_float(notch_q, 30.0)

    try:
        base_sos = design_base_filter(fs, family, resp, low_hz, high_hz, order, rp, rs)
        red_ac = apply_chain(red, fs, base_sos, notch_on, notch_hz, notch_q, detrend, invert)
        ir_ac  = apply_chain(ir,  fs, base_sos, notch_on, notch_hz, notch_q, detrend, invert)
        filt_err = None
    except Exception as e:
        red_ac = np.zeros_like(red); ir_ac = np.zeros_like(ir)
        filt_err = str(e)

    # Insights (single-window)
    spo2, R, PI = estimate_spo2(red, ir, red_ac, ir_ac)
    hr_psd = estimate_rates_psd(ir_ac, fs, (0.6, 3.5))   # 36–210 bpm
    rr_psd = estimate_rates_psd(ir_ac, fs, (0.1, 0.5))   # 6–30 rpm
    snr_red = quick_snr(red_ac); snr_ir = quick_snr(ir_ac)
    dc_red, dc_ir = float(np.mean(red)), float(np.mean(ir))

    # Auto-decimate for display
    decim_eff = auto_decimation(n, decim_user, traces=8, cap=MAX_DISPLAY_POINTS)
    td = t[::decim_eff]
    red_d,  ir_d  = red[::decim_eff],  ir[::decim_eff]
    red_ad, ir_ad = red_ac[::decim_eff], ir_ac[::decim_eff]

    # Time-domain plots (bigger) - only compute if time_domain tab is selected
    if main_tab == "time_domain":
        fig_raw = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                                subplot_titles=(f"Raw {red_col}", f"Raw {ir_col}"))
        fig_raw.add_trace(go.Scatter(x=td, y=red_d, name=f"Raw {red_col}", mode="lines"), 1, 1)
        fig_raw.add_trace(go.Scatter(x=td, y=ir_d,  name=f"Raw {ir_col}",  mode="lines"), 2, 1)
        fig_raw.update_xaxes(title_text="Time (s)", row=2, col=1, rangeslider={"visible": True})
        fig_raw.update_yaxes(title_text="ADC", row=1, col=1); fig_raw.update_yaxes(title_text="ADC", row=2, col=1)
        fig_raw.update_layout(template=template, title=f"Raw ({n:,} rows, decim×{decim_eff})",
                              hovermode="x unified", height=420,
                              paper_bgcolor="#111827" if theme=="dark" else None,
                              plot_bgcolor="#0b1220" if theme=="dark" else None)

        fig_ac = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                               subplot_titles=(f"Filtered {red_col} ({family},{resp})",
                                               f"Filtered {ir_col} ({family},{resp})"))
        fig_ac.add_trace(go.Scatter(x=td, y=red_ad, name=f"AC {red_col}", mode="lines"), 1, 1)
        fig_ac.add_trace(go.Scatter(x=td, y=ir_ad,  name=f"AC {ir_col}",  mode="lines"), 2, 1)
        fig_ac.update_xaxes(title_text="Time (s)", row=2, col=1, rangeslider={"visible": True})
        fig_ac.update_yaxes(title_text="Amplitude", row=1, col=1); fig_ac.update_yaxes(title_text="Amplitude", row=2, col=1)
        fig_ac.update_layout(template=template, title=f"Filtered (order {order}, decim×{decim_eff})",
                             hovermode="x unified", height=420,
                             paper_bgcolor="#111827" if theme=="dark" else None,
                             plot_bgcolor="#0b1220" if theme=="dark" else None)
    else:
        # Return blank figures for time-domain charts when not selected
        fig_raw = blank(420)
        fig_ac = blank(420)

    # PSD and Spectrogram - only compute if frequency tab is selected
    if main_tab == "frequency":
        # PSD
        f_r, P_r = welch(red_ac, fs=fs, nperseg=min(len(red_ac), 4096))
        f_i, P_i = welch(ir_ac,  fs=fs, nperseg=min(len(ir_ac),  4096))
        fig_psd = go.Figure()
        fig_psd.add_trace(go.Scatter(x=f_r, y=10*np.log10(P_r+1e-20), mode="lines", name=f"PSD {red_col}"))
        fig_psd.add_trace(go.Scatter(x=f_i, y=10*np.log10(P_i+1e-20), mode="lines", name=f"PSD {ir_col}"))
        fig_psd.update_xaxes(title_text="Frequency (Hz)")
        fig_psd.update_yaxes(title_text="Power (dB)")
        fig_psd.update_layout(template=template, height=360,
                              paper_bgcolor="#111827" if theme=="dark" else None,
                              plot_bgcolor="#0b1220" if theme=="dark" else None)

        # Spectrogram (optional)
        show_spec_on = ("on" in (show_spec or []))
        if show_spec_on and len(ir_ac) > fs:
            nper = max(16, int(safe_float(spec_win_sec, DEFAULT_SPEC_WIN_SEC) * fs))
            nover = int(np.clip(safe_float(spec_overlap, DEFAULT_SPEC_OVERLAP), 0.0, 0.95) * nper)
            f_s, t_s, Sxx = spectrogram(ir_ac, fs=fs, nperseg=nper, noverlap=nover, scaling="spectrum", mode="psd")
            fig_spec = go.Figure(data=go.Heatmap(
                x=t_s, y=f_s, z=10*np.log10(Sxx+1e-18), colorbar=dict(title="dB")))
            fig_spec.update_xaxes(title_text="Time (s)")
            fig_spec.update_yaxes(title_text="Frequency (Hz)")
            fig_spec.update_layout(template=template, height=380,
                                   paper_bgcolor="#111827" if theme=="dark" else None,
                                   plot_bgcolor="#0b1220" if theme=="dark" else None)
        else:
            fig_spec = blank(380)
    else:
        fig_psd = blank(360)
        fig_spec = blank(380)

    # Dynamics (HR trend, IBI hist, Poincaré, Cross-corr)
    src_ac = ir_ac if (hr_source or "ir") == "ir" else red_ac
    hr_min = safe_int(hr_min, DEFAULT_HR_MIN)
    hr_max = safe_int(hr_max, DEFAULT_HR_MAX)
    peak_prom = safe_float(peak_prom, DEFAULT_PEAK_PROM_FACTOR)

    t_peaks, ibis, (hr_t, hr_bpm) = compute_hr_trend(src_ac, fs, hr_min, hr_max, peak_prom)

    # --- New analyses using both wavelengths ---

    # Beat-by-beat R & SpO2 (robust AC/DC per beat)
    tB, Rbeats, spo2_beats = r_series_spo2(red, ir, red_ac, ir_ac, t_peaks, fs)

    # Coherence spectrum
    fC, Cxy = ms_coherence(red_ac, ir_ac, fs)
    coh_hr = None
    if hr_psd:
        # coherence at HR (Hz)
        hr_hz = hr_psd/60.0
        idx = np.argmin(np.abs(fC - hr_hz))
        coh_hr = float(Cxy[idx])

    # Lissajous (RED_ac vs IR_ac), z-scored & decimated
    dd = max(1, int(len(ir_ac)//10000))  # keep dots reasonable
    zr = (red_ac - red_ac.mean())/(red_ac.std()+1e-12)
    zi = (ir_ac  - ir_ac.mean()) /(ir_ac.std()+1e-12)
    zr_d, zi_d = zr[::dd], zi[::dd]

    # Average beat overlay (AC, normalized)
    t_rel, mean_red, std_red = avg_beat(red_ac, t_peaks, fs, width_s=1.2, out_len=200)
    _,     mean_ir,  std_ir  = avg_beat(ir_ac,  t_peaks, fs, width_s=1.2, out_len=200)

    # SDPPG (second derivative) for IR (default) + RED overlay
    def sdppg(x): 
        return np.gradient(np.gradient(x))
    sd_red = sdppg(red_ac); sd_ir = sdppg(ir_ac)

    
        # Dynamics charts - only compute if dynamics tab is selected
    if main_tab == "dynamics":
        if dynamics_tab == "hr" and "hr" in (show_adv or []) and len(hr_t) > 0:
            # HR trend
            fig_hr = go.Figure()
            fig_hr.add_trace(go.Scatter(x=hr_t, y=hr_bpm, mode="lines+markers", name="HR"))
            fig_hr.update_xaxes(title_text="Time (s)")
            fig_hr.update_yaxes(title_text="HR (bpm)")
            fig_hr.update_layout(template=template, height=320,
                                 paper_bgcolor="#111827" if theme=="dark" else None,
                                 plot_bgcolor="#0b1220" if theme=="dark" else None)
        else:
            fig_hr = blank(320)

        if dynamics_tab == "hist" and "hist" in (show_adv or []) and len(ibis) > 1:
            # IBI histogram
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(x=1000.0*ibis, nbinsx=30, name="IBI"))
            fig_hist.update_xaxes(title_text="IBI (ms)")
            fig_hist.update_yaxes(title_text="Count")
            fig_hist.update_layout(template=template, height=280,
                                   paper_bgcolor="#111827" if theme=="dark" else None,
                                   plot_bgcolor="#0b1220" if theme=="dark" else None)
        else:
            fig_hist = blank(280)

        if dynamics_tab == "poi" and "poi" in (show_adv or []) and len(ibis) > 2:
            # Poincaré (IBI_{n} vs IBI_{n+1})
            fig_poi = go.Figure()
            fig_poi.add_trace(go.Scatter(x=1000.0*ibis[:-1], y=1000.0*ibis[1:], mode="markers", name="IBI pairs"))
            fig_poi.update_xaxes(title_text="IBI_n (ms)")
            fig_poi.update_yaxes(title_text="IBI_{n+1} (ms)")
            fig_poi.update_layout(template=template, height=280,
                                  paper_bgcolor="#111827" if theme=="dark" else None,
                                  plot_bgcolor="#0b1220" if theme=="dark" else None)
        else:
            fig_poi = blank(280)

        if dynamics_tab == "xcorr" and "xcorr" in (show_adv or []) and n > 10:
            # Cross-correlation (red_ac vs ir_ac)
            lags_s, corr, best_lag = cross_correlation_lag(red_ac, ir_ac, fs, max_lag_sec=1.0)
            if lags_s is not None:
                fig_xc = go.Figure()
                fig_xc.add_trace(go.Scatter(x=lags_s, y=corr, mode="lines", name="xcorr"))
                fig_xc.add_vline(x=best_lag, line_dash="dash")
                fig_xc.update_xaxes(title_text="Lag (s) [positive = RED leads IR]")
                fig_xc.update_yaxes(title_text="Correlation")
                fig_xc.update_layout(template=template, height=280,
                                     paper_bgcolor="#111827" if theme=="dark" else None,
                                     plot_bgcolor="#0b1220" if theme=="dark" else None)
            else:
                fig_xc = blank(280)
        else:
            fig_xc = blank(280)
    else:
        # Return blank figures for all dynamics charts when not selected
        fig_hr = blank(320)
        fig_hist = blank(280)
        fig_poi = blank(280)
        fig_xc = blank(280)

    # Dual-source analytics charts - only compute if dual_source tab is selected
    if main_tab == "dual_source":
        if dual_source_tab == "rtrend":
            # R trend (per-beat) with SpO2
            fig_rtrend = go.Figure()
            if len(tB) > 0:
                if len(spo2_beats) > 0:
                    fig_rtrend.add_trace(go.Scatter(x=tB[:len(spo2_beats)], y=spo2_beats, mode="lines+markers", name="SpO₂ (beat)"))
                fig_rtrend.add_trace(go.Scatter(x=tB[:len(Rbeats)], y=Rbeats, yaxis="y2", mode="lines", name="R"))
            fig_rtrend.update_layout(
                template=template, height=320, hovermode="x unified",
                yaxis=dict(title="SpO₂ (%)"),
                yaxis2=dict(title="R", overlaying="y", side="right", showgrid=False),
                paper_bgcolor="#111827" if theme=="dark" else None,
                plot_bgcolor ="#0b1220" if theme=="dark" else None,
                title="Beat-by-beat SpO₂ & R"
            )
        else:
            fig_rtrend = blank(320)

        if dual_source_tab == "coh":
            # Coherence
            fig_coh = go.Figure()
            fig_coh.add_trace(go.Scatter(x=fC, y=Cxy, mode="lines", name="Coherence"))
            if hr_psd:
                fig_coh.add_vline(x=hr_psd/60.0, line_dash="dash")
            fig_coh.update_xaxes(title_text="Frequency (Hz)")
            fig_coh.update_yaxes(title_text="Cxy (0–1)", range=[0,1])
            fig_coh.update_layout(template=template, height=300,
                paper_bgcolor="#111827" if theme=="dark" else None,
                plot_bgcolor ="#0b1220" if theme=="dark" else None,
                title="RED–IR Magnitude-Squared Coherence"
            )
        else:
            fig_coh = blank(300)

        if dual_source_tab == "liss":
            # Lissajous
            fig_liss = go.Figure()
            fig_liss.add_trace(go.Scatter(x=zr_d, y=zi_d, mode="markers", name="AC points", opacity=0.4))
            fig_liss.update_xaxes(title_text="RED AC (z-score)")
            fig_liss.update_yaxes(title_text="IR AC (z-score)")
            fig_liss.update_layout(template=template, height=300,
                paper_bgcolor="#111827" if theme=="dark" else None,
                plot_bgcolor ="#0b1220" if theme=="dark" else None,
                title="Lissajous: RED vs IR (AC)"
            )
        else:
            fig_liss = blank(300)

        if dual_source_tab == "avgbeat":
            # Average beat overlay (normalized)
            fig_avgbeat = go.Figure()
            if len(t_rel)>0:
                # normalize to unit peak for shape comparison
                mr = mean_red / (np.max(np.abs(mean_red))+1e-12)
                mi = mean_ir  / (np.max(np.abs(mean_ir))+1e-12)
                fig_avgbeat.add_trace(go.Scatter(x=t_rel, y=mr, mode="lines", name="RED avg"))
                fig_avgbeat.add_trace(go.Scatter(x=t_rel, y=mi, mode="lines", name="IR avg"))
            fig_avgbeat.update_xaxes(title_text="Time relative to peak (s)")
            fig_avgbeat.update_yaxes(title_text="Normalized amplitude")
            fig_avgbeat.update_layout(template=template, height=300,
                paper_bgcolor="#111827" if theme=="dark" else None,
                plot_bgcolor ="#0b1220" if theme=="dark" else None,
                title="Ensemble-averaged beat shape"
            )
        else:
            fig_avgbeat = blank(300)

        if dual_source_tab == "sdppg":
            # SDPPG
            fig_sdppg = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                    subplot_titles=("SDPPG RED", "SDPPG IR"))
            fig_sdppg.add_trace(go.Scatter(x=td, y=sd_red[::decim_eff], mode="lines", name="SDPPG RED"), 1, 1)
            fig_sdppg.add_trace(go.Scatter(x=td, y=sd_ir[::decim_eff],  mode="lines", name="SDPPG IR"),  2, 1)
            fig_sdppg.update_xaxes(title_text="Time (s)", row=2, col=1)
            fig_sdppg.update_yaxes(title_text="2nd deriv.", row=1, col=1)
            fig_sdppg.update_yaxes(title_text="2nd deriv.", row=2, col=1)
            fig_sdppg.update_layout(template=template, height=300,
                paper_bgcolor="#111827" if theme=="dark" else None,
                plot_bgcolor ="#0b1220" if theme=="dark" else None)
        else:
            fig_sdppg = blank(300)
    else:
        # Return blank figures for all dual-source charts when not selected
        fig_rtrend = blank(320)
        fig_coh = blank(300)
        fig_liss = blank(300)
        fig_avgbeat = blank(300)
        fig_sdppg = blank(300)

    
    # Insight chips
    chips = []
    if filt_err: chips.append(html.Span(f"Filter error: {filt_err}", className="pill"))
    chips.extend([
        html.Span(f"SpO₂={f'{spo2:.2f}%' if spo2 is not None else 'n/a'}", className="pill"),
        html.Span(f"R={f'{R:.4f}' if R is not None else 'n/a'}", className="pill"),
        html.Span(f"PI={f'{PI:.2f}%' if PI is not None else 'n/a'}", className="pill"),
        html.Span(f"HR_psd={f'{hr_psd:.1f} bpm' if hr_psd else 'n/a'}", className="pill"),
        html.Span(f"RR_psd={f'{rr_psd:.1f} rpm' if rr_psd else 'n/a'}", className="pill"),
        html.Span(f"DC_red={dc_red:.1f}", className="pill"),
        html.Span(f"DC_ir={dc_ir:.1f}", className="pill"),
        html.Span(f"SNR~ red={f'{snr_red:.2f}' if snr_red else 'n/a'}", className="pill"),
        html.Span(f"SNR~ ir={f'{snr_ir:.2f}' if snr_ir else 'n/a'}", className="pill"),
        html.Span(f"peaks={len(t_peaks)}", className="pill"),
    ])

    # File/window info
    duration = n / fs
    info = [
        html.Span(f"File: {Path(path).name}", className="pill"),
        html.Span(f"Total rows ≈ {total:,}", className="pill"),
        html.Span(f"Window {start:,}–{end:,} (n={n:,})", className="pill"),
        html.Span(f"Duration ≈ {duration:.2f}s @ fs={fs:g} Hz", className="pill"),
        html.Span(f"Family={family} • Resp={resp} • Order={order}", className="pill"),
        html.Span(f"Cutoffs {low_hz:g}–{high_hz:g} Hz • Notch={'on' if notch_on else 'off'}", className="pill"),
        html.Span(f"Decimation ×{decim_eff}", className="pill"),
        html.Span(f"HR src={hr_source or 'ir'}; HR band {hr_min}-{hr_max} bpm; prom×std={peak_prom:g}", className="pill"),
        html.Span(f"Spectrogram win={safe_float(spec_win_sec, DEFAULT_SPEC_WIN_SEC):g}s ovlp={safe_float(spec_overlap, DEFAULT_SPEC_OVERLAP):g}", className="pill"),
    ]

    # CSV download of current window
    trigger = callback_context.triggered[0]["prop_id"] if callback_context.triggered else ""
    dl = None
    if trigger == "btn_dl_csv.n_clicks":
        dl = dcc.send_data_frame(df.to_csv, f"ppg_window_{start}_{end}.csv", index=False)

    # return (fig_raw, fig_ac, fig_psd, fig_spec, fig_hr, fig_hist, fig_poi, fig_xc,
    #         fig_rtrend, fig_coh, fig_liss, fig_avgbeat, fig_sdppg,
    #         chips, info, dl)
    return (
        fig_raw, fig_ac, fig_psd, fig_spec,          # 1–4
        fig_hr,  fig_hist, fig_poi, fig_xc,          # 5–8
        chips,   info,     dl,                       # 9–11
        fig_rtrend, fig_coh, fig_liss,               # 12–14
        fig_avgbeat, fig_sdppg                       # 15–16
    )


# --------------------
# Main
# --------------------
if __name__ == "__main__":
    app.run_server(debug=True)

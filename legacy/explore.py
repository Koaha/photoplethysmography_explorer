# app_ppg_dash.py
import numpy as np
import pandas as pd
from scipy.signal import iirfilter, sosfiltfilt
from pathlib import Path
import os
import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --------------------
# Config
# --------------------
CSV_FILE = "PPG.csv"
COL_RED = "RED_ADC"
COL_IR = "IR_ADC"
FS_DEFAULT = 100.0        # Hz
N_ROWS = 10_000           # hard cap as requested

# --------------------
# Load data (first N rows)
# --------------------
if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"CSV not found: {CSV_FILE}")

df = pd.read_csv(CSV_FILE, nrows=N_ROWS)
missing = [c for c in (COL_RED, COL_IR) if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in CSV: {missing}")

df = df[[COL_RED, COL_IR]].dropna().reset_index(drop=True)
red = df[COL_RED].to_numpy(dtype=float)
ir  = df[COL_IR].to_numpy(dtype=float)

# --------------------
# Helpers
# --------------------
def design_and_apply_filter(x, fs, family, resp_type, low_hz, high_hz, order, rp, rs):
    """
    Build IIR filter as SOS and apply filtfilt. Handles LP/HP/BP/BS.
    family: 'butter', 'cheby1', 'cheby2', 'ellip', 'bessel'
    resp_type: 'lowpass' | 'highpass' | 'bandpass' | 'bandstop'
    """
    nyq = fs / 2.0
    # sanitize & map cutoffs
    if resp_type in ("lowpass", "highpass"):
        Wn = float(high_hz if resp_type == "lowpass" else low_hz)
        Wn = max(1e-6, min(Wn, nyq * 0.999))  # keep strictly < Nyquist
    else:
        lo = max(1e-6, min(low_hz, high_hz))
        hi = max(lo + 1e-6, high_hz)
        hi = min(hi, nyq * 0.999)
        Wn = [lo, hi]

    kwargs = dict(ftype=family, fs=fs, output="sos")
    # ripple params only apply to certain families
    if family == "cheby1":
        kwargs["rp"] = rp
    elif family == "cheby2":
        kwargs["rs"] = rs
    elif family == "ellip":
        kwargs["rp"] = rp
        kwargs["rs"] = rs

    sos = iirfilter(order, Wn, btype=resp_type, **kwargs)
    y = sosfiltfilt(sos, x)
    return y

def estimate_spo2(red_raw, ir_raw, red_filt, ir_filt):
    """
    Same simple rule-of-thumb as your script:
    R = (AC_red/DC_red) / (AC_ir/DC_ir), then quadratic.
    AC amplitude via peak-to-peak/2, DC via mean(raw).
    """
    dc_red = float(np.mean(red_raw))
    dc_ir  = float(np.mean(ir_raw))
    ac_red_amp = float(np.ptp(red_filt) / 2.0)
    ac_ir_amp  = float(np.ptp(ir_filt)  / 2.0)

    if min(dc_red, dc_ir, ac_red_amp, ac_ir_amp) <= 0:
        return None, None
    R = (ac_red_amp / dc_red) / (ac_ir_amp / dc_ir)
    spo2 = -45.06 * R**2 + 30.354 * R + 94.845
    return spo2, R

# --------------------
# App UI
# --------------------
app = dash.Dash(__name__)
app.title = "PPG Filter Explorer (10k rows cap)"

app.layout = html.Div(className="container", children=[
    html.H2("PPG Filter Explorer (first 10,000 rows)"),
    html.Div(style={"display": "flex", "gap": "24px", "flexWrap": "wrap"}, children=[

        html.Div(style={"minWidth": "260px"}, children=[
            html.Label("Sampling frequency (Hz)"),
            dcc.Input(id="fs", type="number", value=FS_DEFAULT, step=0.5, min=1, debounce=True, style={"width": "100%"}),

            html.Br(), html.Br(),
            html.Label("Filter family"),
            dcc.Dropdown(
                id="family",
                value="butter",
                options=[
                    {"label": "Butterworth", "value": "butter"},
                    {"label": "Chebyshev I", "value": "cheby1"},
                    {"label": "Chebyshev II", "value": "cheby2"},
                    {"label": "Elliptic", "value": "ellip"},
                    {"label": "Bessel", "value": "bessel"},
                ],
                clearable=False
            ),

            html.Br(),
            html.Label("Response type"),
            dcc.Dropdown(
                id="resp",
                value="bandpass",
                options=[
                    {"label": "Bandpass", "value": "bandpass"},
                    {"label": "Bandstop (Notch)", "value": "bandstop"},
                    {"label": "Lowpass", "value": "lowpass"},
                    {"label": "Highpass", "value": "highpass"},
                ],
                clearable=False
            ),

            html.Br(),
            html.Label("Cutoff frequencies (Hz)"),
            html.Div("For LP: use High only. For HP: use Low only."),
            html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px"}, children=[
                html.Div(children=[
                    html.Div("Low"),
                    dcc.Input(id="low_hz", type="number", value=0.5, step=0.1, min=0.0, debounce=True, style={"width": "100%"})
                ]),
                html.Div(children=[
                    html.Div("High"),
                    dcc.Input(id="high_hz", type="number", value=5.0, step=0.1, min=0.1, debounce=True, style={"width": "100%"})
                ]),
            ]),

            html.Br(),
            html.Label("Order"),
            dcc.Slider(id="order", min=1, max=8, step=1, value=2,
                       marks={i: str(i) for i in range(1, 9)}),

            html.Br(),
            html.Label("Ripple params (only for Chebyshev/Elliptic)"),
            html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px"}, children=[
                html.Div(children=[
                    html.Div("rp (dB, passband)"),
                    dcc.Input(id="rp", type="number", value=1.0, step=0.1, min=0.01, debounce=True, style={"width": "100%"})
                ]),
                html.Div(children=[
                    html.Div("rs (dB, stopband)"),
                    dcc.Input(id="rs", type="number", value=40.0, step=1, min=10, debounce=True, style={"width": "100%"})
                ]),
            ]),

            html.Br(),
            dcc.Checklist(
                id="invert",
                options=[{"label": "Invert filtered AC (pulse up)", "value": "invert"}],
                value=["invert"]
            ),
        ]),

        html.Div(style={"flex": "1", "minWidth": "360px"}, children=[
            html.Div(id="metrics", style={"padding": "8px 12px", "border": "1px solid #ddd", "borderRadius": "8px", "marginBottom": "10px"}),
            dcc.Graph(id="fig_raw", style={"height": "360px"}),
            dcc.Graph(id="fig_ac", style={"height": "360px"}),
        ]),
    ]),

    html.Div(style={"marginTop": "6px", "color": "#666"}, children=f"Loaded {len(df)} rows from {CSV_FILE}")
])

# --------------------
# Callbacks
# --------------------
@app.callback(
    Output("fig_raw", "figure"),
    Output("fig_ac", "figure"),
    Output("metrics", "children"),
    Input("fs", "value"),
    Input("family", "value"),
    Input("resp", "value"),
    Input("low_hz", "value"),
    Input("high_hz", "value"),
    Input("order", "value"),
    Input("rp", "value"),
    Input("rs", "value"),
    Input("invert", "value"),
)
def update_plots(fs, family, resp, low_hz, high_hz, order, rp, rs, invert_flags):
    fs = float(fs or FS_DEFAULT)
    low_hz = float(low_hz or 0.5)
    high_hz = float(high_hz or 5.0)
    order = int(order or 2)
    rp = float(rp or 1.0)
    rs = float(rs or 40.0)
    invert = "invert" in (invert_flags or [])

    t = np.arange(len(df)) / fs

    # RAW figure
    fig_raw = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                            subplot_titles=("Raw RED PPG", "Raw IR PPG"))
    fig_raw.add_trace(go.Scatter(x=t, y=red, name="Raw RED", mode="lines"), 1, 1)
    fig_raw.add_trace(go.Scatter(x=t, y=ir,  name="Raw IR",  mode="lines"), 2, 1)
    fig_raw.update_xaxes(title_text="Time (s)", row=2, col=1, rangeslider={"visible": True})
    fig_raw.update_yaxes(title_text="ADC", row=1, col=1)
    fig_raw.update_yaxes(title_text="ADC", row=2, col=1)
    fig_raw.update_layout(title=f"PPG Raw Waveforms (first {len(df)} rows)", hovermode="x unified", height=360)

    # FILTERED figure
    # Be resilient to invalid combos
    try:
        red_ac = design_and_apply_filter(red, fs, family, resp, low_hz, high_hz, order, rp, rs)
        ir_ac  = design_and_apply_filter(ir,  fs, family, resp, low_hz, high_hz, order, rp, rs)
        if invert:
            red_ac = -red_ac
            ir_ac  = -ir_ac

        fig_ac = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                               subplot_titles=(f"Filtered RED ({family}, {resp})",
                                               f"Filtered IR ({family}, {resp})"))
        fig_ac.add_trace(go.Scatter(x=t, y=red_ac, name="AC RED", mode="lines"), 1, 1)
        fig_ac.add_trace(go.Scatter(x=t, y=ir_ac,  name="AC IR",  mode="lines"), 2, 1)
        fig_ac.update_xaxes(title_text="Time (s)", row=2, col=1, rangeslider={"visible": True})
        fig_ac.update_yaxes(title_text="Amplitude", row=1, col=1)
        fig_ac.update_yaxes(title_text="Amplitude", row=2, col=1)
        fig_ac.update_layout(title=f"PPG Filtered Waveforms (order {order})", hovermode="x unified", height=360)

        # SpO2 estimate
        spo2, R = estimate_spo2(red, ir, red_ac, ir_ac)
        met = (f"Estimated SpO₂: {spo2:.2f}% (R={R:.4f})"
               if (spo2 is not None) else "Estimated SpO₂: n/a (insufficient AC/DC)")
    except Exception as e:
        fig_ac = go.Figure()
        fig_ac.update_layout(title=f"Filter error: {e}")
        met = f"Filter error: {e}"

    # Metrics panel
    metrics = html.Div([
        html.Div(f"Filter: {family} • {resp} • order={order} • fs={fs:g} Hz"),
        html.Div(f"Low={low_hz:g} Hz, High={high_hz:g} Hz • rp={rp:g} dB, rs={rs:g} dB • invert={invert}"),
        html.Strong(met),
    ])

    return fig_raw, fig_ac, metrics

# --------------------
# Main
# --------------------
if __name__ == "__main__":
    app.run_server(debug=True)

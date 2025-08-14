"""
Configuration settings and constants for the PPG analysis tool.
"""

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

# App settings
APP_TITLE = "PPG Filter Lab — Window Mode (Wide + Insights)"
APP_SUBTITLE = "Load CSV • Select row window • Bigger plots • Extra insight visuals"

# Layout settings
GRID_COLUMNS = "340px 2.1fr 0.9fr"
GRID_GAP = "18px"
MAX_WIDTH = "1760px"

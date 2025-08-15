"""
Data loading and management callbacks for PPG analysis.

This module contains callbacks responsible for handling data loading operations,
including file path loading, CSV uploads, and automatic file detection.
It also implements smart column detection for RED/IR channel identification
and manages data window settings.
"""

import dash
from dash import Input, Output, State, callback_context, no_update
from pathlib import Path
from ..utils.file_utils import (
    count_rows_quick,
    get_columns_only,
    parse_uploaded_csv_to_temp,
    get_auto_file_path,
)
from ..config.settings import DEFAULT_WINDOW_START, DEFAULT_WINDOW_END


def register_data_callbacks(app):
    """
    Register data-related callbacks with the Dash app.

    This function sets up the main data loading callback that handles:
    - File path loading from user input
    - CSV file uploads
    - Automatic file detection
    - Smart column identification for RED/IR channels
    - Data window initialization

    Args:
        app (dash.Dash): The main Dash application object
    """

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
        prevent_initial_call=False,
    )
    def load_data(n_clicks_path, upload_contents, upload_filename, file_path):
        """
        Load data from file path or uploaded content with smart column detection.

        This callback handles three data loading scenarios:
        1. CSV file upload via drag-and-drop
        2. File path loading from user input
        3. Automatic file detection in the current directory

        It implements intelligent column detection to automatically identify
        RED and IR channels based on naming patterns and data characteristics.

        Args:
            n_clicks_path (int): Number of clicks on the load path button
            upload_contents (str): Base64 encoded content of uploaded CSV
            upload_filename (str): Name of the uploaded file
            file_path (str): User-provided file path

        Returns:
            tuple: (path, total_rows, status, red_options, ir_options,
                   red_value, ir_value, window) - Data loading results
        """
        # Determine which trigger activated the callback
        trig = callback_context.triggered[0]["prop_id"] if callback_context.triggered else ""
        path = None
        status = "No data loaded."

        # Handle CSV file upload
        if "upload_csv.contents" in trig and upload_contents:
            path = parse_uploaded_csv_to_temp(upload_contents, upload_filename or "uploaded.csv")
            status = f"Uploaded: {Path(path).name} → temp"

        # Handle file path loading
        elif "btn_load_path.n_clicks" in trig and (file_path or "").strip():
            p = Path(file_path).expanduser().resolve()
            if not p.exists():
                return (
                    no_update,
                    no_update,
                    f"File not found: {file_path}",
                    [],
                    [],
                    None,
                    None,
                    no_update,
                )
            path = str(p)
            status = f"Loaded from path: {p}"

        # Handle automatic file detection
        else:
            auto_file = get_auto_file_path("PPG.csv")
            if auto_file:
                path = auto_file
                status = f"Auto-loaded: {Path(path).name}"
            else:
                return None, None, status, [], [], None, None, None

        # Get available columns and create dropdown options
        cols = get_columns_only(path)
        opts = [{"label": c, "value": c} for c in cols]

        # Smart column detection - look for common PPG column patterns
        red_guess = None
        ir_guess = None

        # Try to find RED/IR columns by common naming patterns
        for col in cols:
            col_lower = col.lower()
            if not red_guess and any(
                pattern in col_lower
                for pattern in ["red", "r_", "r-", "r ", "red_adc", "red_signal"]
            ):
                red_guess = col
            elif not ir_guess and any(
                pattern in col_lower
                for pattern in ["ir", "infrared", "i_", "i-", "i ", "ir_adc", "ir_signal"]
            ):
                ir_guess = col

        # If no specific patterns found, try to use first two numeric columns
        if not red_guess or not ir_guess:
            numeric_cols = [col for col in cols if col != "time" and col != "timestamp"]
            if len(numeric_cols) >= 2:
                if not red_guess:
                    red_guess = numeric_cols[0]
                if not ir_guess:
                    ir_guess = numeric_cols[1] if numeric_cols[1] != red_guess else numeric_cols[0]

        # Fallback to first available columns if all else fails
        if not red_guess and cols:
            red_guess = cols[0]
        if not ir_guess and len(cols) > 1:
            ir_guess = cols[1] if cols[1] != red_guess else cols[0]

        # Set up default data window
        total = count_rows_quick(path)
        end_default = min(DEFAULT_WINDOW_END, max(0, total - 1))
        window = {"start": DEFAULT_WINDOW_START, "end": end_default}

        # Update status with file information
        status += (
            f" • total rows ≈ {total:,} • default window {window['start']:,}–{window['end']:,}"
        )

        return path, total, status, opts, opts, red_guess, ir_guess, window

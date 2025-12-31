"""
--------------------------------------------------------------------
File: ldo_design_color_spectrum_analysis.py

Purpose:
    Visual "traffic-light" summary of analog design optimization results
    across multiple design points (e.g., Hooke-Jeeves runs).

What it does:
    - Reads a CSV with per-design-point metrics (Gain, Phase Margin, UGF, Slew Rate)
    - Converts values to floats robustly (handles scientific notation strings)
    - Classifies each metric into a color spectrum (red/orange/yellow/green)
    - Adds an additional transistor-region "pass/fail" color
    - Plots a compact Plotly strip chart (one row per metric)
    - Exports the figure as a high-resolution PDF

Inputs:
    - CSV file(s) containing at minimum:
        Design Point, Gain (dB), Phase Margin (deg), slewrate (V/us), UGF (Hz),
        M1, M3, M5, M6, M7

Outputs:
    - Interactive Plotly figure (display)
    - PDF export: parameter_analysis_Hooke-Jeeves_Design1.pdf

Author:
    Akhil Ambati

Notes:
    - Thresholds in get_color_spectrum() reflect your design targets.
    - Consider moving thresholds to a config section for easier reuse.
--------------------------------------------------------------------
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# --------------------------------------------------------------------
# Column mapping
#   Keeps a single source-of-truth for expected column names.
#   Useful if CSV headers change slightly in future.
# --------------------------------------------------------------------
column_mapping = {
    'Design Point': 'Design Point',
    'Gain (dB)': 'Gain (dB)',
    'Phase Margin (deg)': 'Phase Margin (deg)',
    'slewrate (V/us)': 'slewrate (V/us)',
    'UGF (Hz)': 'UGF (Hz)',
    'M1': 'M1',
    'M3': 'M3',
    'M5': 'M5',
    'M6': 'M6',
    'M7': 'M7'
}


# --------------------------------------------------------------------
# Optional utility: weights for selecting "worst" condition.
#   (Currently not used in final logic, but kept for future aggregation.)
# --------------------------------------------------------------------
color_weights = {
    'red': 1,
    'orange': 2,
    'yellow': 3,
    'green': 4
}


# --------------------------------------------------------------------
# Robust conversion helper
#   Handles strings, scientific notation, and comma decimal separators.
# --------------------------------------------------------------------
def convert_to_float(value):
    """
    Convert arbitrary CSV cell values to float.

    - Replaces comma decimal separators (e.g., '1,23E-3') with dot.
    - Returns NaN if parsing fails.

    Parameters:
        value: value from dataframe cell

    Returns:
        float or np.nan
    """
    if isinstance(value, str) and 'E' in value:
        value = value.replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return np.nan


# --------------------------------------------------------------------
# Color classification logic
#   Converts each metric into a qualitative status color.
#   Thresholds encode your spec/targets for quick scanning.
# --------------------------------------------------------------------
def get_color_spectrum(param_name, param_value):
    """
    Map a metric value to a color bucket.

    Parameters:
        param_name (str): metric name
        param_value (float): metric value

    Returns:
        str: one of {red, orange, yellow, green, gray}
    """
    # Missing values get gray (unknown / not measured)
    if param_value is None or pd.isna(param_value):
        return 'gray'

    # Gain thresholds (example: >=68 dB is strong)
    if param_name == 'Gain (dB)':
        if param_value < 50:
            return 'red'
        elif 50 <= param_value < 60:
            return 'orange'
        elif 60 <= param_value < 68:
            return 'yellow'
        elif param_value >= 68:
            return 'green'
        return 'gray'

    # Phase margin thresholds (example: 60–100 deg preferred)
    elif param_name == 'Phase Margin (deg)':
        if param_value < 45 or param_value > 100:
            return 'red'
        elif 45 <= param_value < 50:
            return 'orange'
        elif 50 <= param_value < 60:
            return 'yellow'
        elif 60 <= param_value <= 100:
            return 'green'
        return 'gray'

    # Slew rate thresholds (your script uses 6e6..11e6)
    # NOTE: If your CSV is truly in V/us, these values might actually be in V/s.
    #       Keep as-is (portfolio code), but consider unit clarification later.
    elif param_name == 'slewrate (V/us)':
        if param_value < 6e6 or param_value > 11e6:
            return 'red'
        elif 6e6 <= param_value < 8e6:
            return 'orange'
        elif 8e6 <= param_value < 10e6:
            return 'yellow'
        elif 10e6 <= param_value <= 11e6:
            return 'green'
        return 'gray'

    # UGF thresholds (example: >20 MHz preferred)
    elif param_name == 'UGF (Hz)':
        if param_value < 15e6:
            return 'red'
        elif 15e6 <= param_value < 17e6:
            return 'orange'
        elif 17e6 <= param_value < 20e6:
            return 'yellow'
        elif param_value > 20e6:
            return 'green'
        return 'gray'

    # Transistor "region" flags: expects values == 2 for "OK"
    elif param_name.startswith('M'):
        return 'green' if param_value == 2 else 'red'

    # Fallback for unhandled parameters
    return 'gray'


# --------------------------------------------------------------------
# CSV reader + normalization
#   Attempts to handle "weird" CSV formatting cases:
#   - single-column loads
#   - headers embedded in first row
#   - underscores in headers
# --------------------------------------------------------------------
def read_and_process_file(file_name):
    """
    Read CSV data and generate per-metric color classification columns.

    Parameters:
        file_name (str): CSV file path

    Returns:
        pd.DataFrame: processed dataframe (numeric values + Color_* columns)
    """
    # Standard read
    df = pd.read_csv(file_name, delimiter=',')

    # If CSV got parsed into one column, attempt alternate parsing
    if len(df.columns) == 1:
        df = pd.read_csv(file_name, delimiter=',', header=None)
        df.columns = df.iloc[0]
        df = df[1:]

    # Normalize column names (remove whitespace, replace underscores)
    df.columns = df.columns.str.strip().str.replace('_', ' ')

    # If first column contains comma-separated headers, split manually
    if ',' in df.columns[0]:
        df.columns = df.columns[0].split(',')

    # Ensure required columns exist
    for col in column_mapping.values():
        if col not in df.columns:
            raise ValueError(f"Missing expected column: {col}")

    # Convert required columns to numeric
    for param in column_mapping.values():
        df[param] = df[param].apply(lambda x: convert_to_float(str(x)))

    # Create Color_<param> columns for plotting
    for param in column_mapping.values():
        if param in df.columns:
            df[f'Color_{param}'] = df.apply(
                lambda x: get_color_spectrum(param, x[param]),
                axis=1
            )

    return df


# --------------------------------------------------------------------
# Plot builder
#   Creates a compact strip chart (one y-offset per metric).
# --------------------------------------------------------------------
def build_parameter_strip_plot(data_frames):
    """
    Build a Plotly strip chart where each metric is drawn as a colored row.

    Parameters:
        data_frames (dict[str, pd.DataFrame]): mapping file->dataframe

    Returns:
        plotly.graph_objects.Figure
    """
    # Single-panel subplot (kept expandable if you add more files/rows later)
    fig = make_subplots(
        rows=1,
        cols=1,
        subplot_titles=['Hooke-Jeeves Algorithm (time 63.87 min)'],
        shared_xaxes=True,
        vertical_spacing=0.1
    )

    valid_colors = {'red', 'orange', 'yellow', 'green', 'gray'}

    for _, df in data_frames.items():
        # Build color column list for tracked metrics
        color_columns = [
            f'Color_{col}'
            for col in column_mapping.values()
            if f'Color_{col}' in df.columns
        ]

        # Ensure all color columns contain valid values
        for col in color_columns:
            df[col] = df[col].fillna('gray')
            df[col] = df[col].apply(lambda x: x if x in valid_colors else 'gray')

        # Compute transistor-region overall color:
        # green only if all region flags match expected "2"
        transistor_values = df[['M1', 'M3', 'M5', 'M6', 'M7']]
        df['Transistor_Color'] = [
            'green' if (
                np.isclose(row['M1'], 2) and
                np.isclose(row['M3'], 2) and
                np.isclose(row['M5'], 2) and
                np.isclose(row['M6'], 2) and
                np.isclose(row['M7'], 2)
            ) else 'red'
            for _, row in transistor_values.iterrows()
        ]

        # Define the plot rows (top to bottom) and their y offsets
        params = [
            'Gain (dB)',
            'Phase Margin (deg)',
            'slewrate (V/us)',
            'UGF (Hz)',
            'Transistor regions'
        ]
        offsets = [0.4, 0.3, 0.2, 0.1, 0.0]

        # Add one scatter trace per metric
        for i, param in enumerate(params):
            color_column = 'Transistor_Color' if param == 'Transistor regions' else f'Color_{param}'

            fig.add_trace(
                go.Scatter(
                    x=df[column_mapping['Design Point']],
                    y=[offsets[i]] * len(df),
                    mode='markers',
                    marker=dict(size=10, color=df[color_column], symbol='square'),
                    showlegend=False,
                    name=param
                ),
                row=1,
                col=1
            )

            # Add a metric label annotation to the right of the last point
            fig.add_annotation(
                x=df[column_mapping['Design Point']].iloc[-1] + 40,
                y=offsets[i],
                text=param,
                showarrow=False,
                row=1,
                col=1
            )

    # Layout: clean compact strip chart
    fig.update_layout(
        height=300,
        width=1000,
        title_text="",
        showlegend=False,
        yaxis=dict(tickvals=[], ticktext=[]),
        margin=dict(l=10, r=10, t=40, b=10)
    )

    fig.update_xaxes(title_text="Design Points")
    fig.update_yaxes(showticklabels=False)

    return fig


# --------------------------------------------------------------------
# Script entry point
# --------------------------------------------------------------------
if __name__ == "__main__":
    # Map CSV -> title (expandable to multiple algorithms/runs later)
    file_name_title_map = {
        'conjugate_cond.csv': 'Hooke-Jeeves Algorithm',
    }

    # Read and process files
    data_frames = {
        file_name: read_and_process_file(file_name)
        for file_name in file_name_title_map.keys()
    }

    # Build plot
    fig = build_parameter_strip_plot(data_frames)

    # Display interactive plot
    fig.show()

    # Export plot to PDF (requires kaleido installed for Plotly image export)
    fig.write_image("parameter_analysis_Hooke-Jeeves_Design1.pdf", scale=2)

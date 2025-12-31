"""
--------------------------------------------------------------------
File: analog_optimization_color_spectrum_dashboard.py

Purpose:
    Visual comparison of analog design optimization algorithms
    using qualitative color-spectrum grading of key performance metrics.

What it does:
    - Reads optimization result CSVs from multiple algorithms
    - Evaluates gain, phase margin, slew rate, UGF, and device regions
    - Maps numeric values to red–green qualitative grades
    - Displays a compact dashboard for rapid design screening
    - Enables comparison across algorithms and design points

Inputs:
    CSV files containing optimization results per algorithm

Outputs:
    High-resolution SVG dashboard plot

Author:
    Akhil Ambati

Notes:
    - Thresholds reflect design targets and can be tuned per project
    - Intended for methodology demonstration, not PDK disclosure
--------------------------------------------------------------------
"""




import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Define the correct column names mapping
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

# Assign weights to each color
color_weights = {
    'red': 1,
    'orange': 2,
    'yellow': 3,
    'green': 4
}

def convert_to_float(value):
    # Function to handle conversion to float
    if isinstance(value, str) and 'E' in value:
        value = value.replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return np.nan

# Define the color map function based on parameter values
def get_color_spectrum(param_name, param_value):
    if param_value is None or pd.isna(param_value):
        return 'gray'  # Return a default color for missing values

    if param_name == 'Gain (dB)':
        if param_value < 50:
            return 'red'
        elif 50 <= param_value < 60:
            return 'orange'
        elif 60 <= param_value < 70:
            return 'yellow'
        elif param_value > 70:
            return 'green'
    elif param_name == 'Phase Margin (deg)':
        if param_value < 45:
            return 'red'
        elif 45 <= param_value < 50:
            return 'orange'
        elif 50 <= param_value < 60:
            return 'yellow'
        elif param_value >= 60:
            return 'green'
    elif param_name == 'slewrate (V/us)':
        if param_value < 6e6 or param_value > 11e6:
            return 'red'
        elif 6e6 <= param_value < 8e6:
            return 'orange'
        elif 8e6 <= param_value < 10e6:
            return 'yellow'
        elif param_value <= 11e6:
            return 'green'
    elif param_name == 'UGF (Hz)':
        if param_value < 15e6 :
            return 'red'
        elif 15e6 <= param_value < 17e6:
            return 'orange'
        elif 17e6 <= param_value < 20e6:
            return 'yellow'
        elif param_value >= 20e6:
            return 'green'
    elif param_name.startswith('M'):  # Handle transistor values
        if param_value != 2:
            return 'red'
        else:
            return 'green'
    else:
        return 'gray'  # Default color for any unspecified parameter

def read_and_process_file(file_name):
    # Read CSV data with the correct delimiter
    df = pd.read_csv(file_name, delimiter=',')
    # Additional processing steps
    if len(df.columns) == 1:
        df = pd.read_csv(file_name, delimiter=',', header=None)
        df.columns = df.iloc[0]
        df = df[1:]

    df.columns = df.columns.str.strip().str.replace('_', ' ')

    # Split the first column manually if it contains all column names
    if ',' in df.columns[0]:
        df.columns = df.columns[0].split(',')

    for col in column_mapping.values():
        if col not in df.columns:
            raise ValueError(f"Missing expected column: {col}")

    for param in column_mapping.values():
        df[param] = df[param].apply(lambda x: convert_to_float(str(x)))

    # Apply the function to create new color columns for the spectrum
    for param in column_mapping.values():
        if param in df.columns:
            df[f'Color_{param}'] = df.apply(lambda x: get_color_spectrum(param, x[param]), axis=1)

    return df

# List of CSV files to read and corresponding plot titles
file_name_title_map = {
    'bfgs_local.csv': 'BFGS Algorithm',
    'conjugate.csv': 'Conjugate Gradient Algorithm',
    'Brent_Powell.csv': 'Brent-Powell Algorithm',
    'Hooke_Jeeves.csv': 'Hooke-Jeeves Algorithm'
}

# Read and process each file
data_frames = {file_name: read_and_process_file(file_name) for file_name in file_name_title_map.keys()}

# Setup the subplot frame
fig = make_subplots(
    rows=4,
    cols=1,
    subplot_titles=[
        'BFGS Algorithm (time  4.28 min)',
        'Conjugate Gradient Algorithm ( time 4.21 min)',
        'Brent-Powell Algorithm (time 16.46 min)',
        'Hooke-Jeeves Algorithm (time 6.18 min)'
    ],
    shared_xaxes=True,
    vertical_spacing=0.1
)

# Combine the color columns into a single color column based on the worst condition for each DataFrame
for idx, (file_name, df) in enumerate(data_frames.items()):
    color_columns = [f'Color_{col}' for col in column_mapping.values() if f'Color_{col}' in df.columns]
    combined_df = df[['Design Point'] + color_columns].copy()

    # Fill NaN values with 'gray'
    for col in color_columns:
        combined_df[col] = combined_df[col].fillna('gray')


    # Determine the colors for the transistor values based on the condition
    transistor_values = df[['M1', 'M3', 'M5', 'M6', 'M7']]
    df['Transistor_Color'] = ['green' if (
        np.isclose(row['M1'], 2) and
        np.isclose(row['M3'], 2) and
        np.isclose(row['M5'], 2) and
        np.isclose(row['M6'], 2) and
        np.isclose(row['M7'], 2)) else 'red' for idx, row in transistor_values.iterrows()]

    # Create individual plots for each parameter in reverse order      
    params = ['Gain (dB)', 'Phase Margin (deg)', 'slewrate (V/us)', 'UGF (Hz)', 'Transistor regions']
    offsets = [0.4, 0.3, 0.2, 0.1, 0]

    for i, param in enumerate(params):
        color_column = 'Transistor_Color' if param == 'Transistor regions' else f'Color_{param}'
        fig.add_trace(go.Scatter(
            x=df[column_mapping['Design Point']],
            y=[offsets[i]] * len(df),
            mode='markers',
            marker=dict(size=10, color=df[color_column], symbol='square'),
            showlegend=False,
            name=param
        ), row=idx + 1, col=1)

        # Add annotations for the parameter names at the end of each line
        fig.add_annotation(
            x=df[column_mapping['Design Point']].iloc[-1] + 20,  # Position it after the last point
            y=offsets[i],
            text=param,
            showarrow=False,
            row=idx + 1,
            col=1
        )
# Update layout
fig.update_layout(
    height=700,  # Adjust height as needed
    width=1000,
    title_text="Design1",
    showlegend=False,  # Set showlegend to False to hide legends
    yaxis=dict(
        tickvals=[],
        ticktext=[]  # Empty ticktext to hide y-axis labels
    ),
    margin=dict(l=10, r=10, t=100, b=10)  # Adjust the top margin for the annotation box
)

# Add a boxed annotation for the input values
input_values_text = "Design 1 Input Values: Gain > 70 dB, SR = 10e6 V/S, Cl = 10e-12 F, GB = 20e6 Hz, Phi > 60 deg"
fig.add_annotation(
    text=input_values_text,
    xref="paper", yref="paper",
    x=0.65, y=1.12,
    showarrow=False,
    bordercolor="black",
    borderwidth=1,
    borderpad=4,
    bgcolor="white",
    xanchor="right",
    yanchor="top",
    align="left"
)

# Update x-axis titles
fig.update_xaxes(title_text="Design Points")

# Hide y-axis values
fig.update_yaxes(showticklabels=False)

# Show the figure
fig.show()

# Save the figure as a high-resolution image
fig.write_image("parameter_analysis_across_algorithms_Design1.svg", scale=2)

"""
--------------------------------------------------------------------
File: ldo_transient_ripple_analysis.py

Purpose:
    Time-domain analysis of LDO output voltage ripple
    during load current transients.

What it does:
    - Reads transient simulation CSV data
    - Plots load current (ILOAD) and output voltage (VOUT) vs time
    - Quantifies overshoot and undershoot relative to average VOUT
    - Highlights critical ripple regions for visual inspection
    - Generates publication-quality SVG plots

Inputs:
    CSV files with columns:
        Time, Load Current, Output Voltage

Outputs:
    High-resolution SVG plots for each load case

Author:
    Akhil Ambati

Notes:
    - Intended for post-processing Spectre/Custom Compiler simulations
    - CSV data assumed to be sanitized and non-confidential
--------------------------------------------------------------------
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


# ------------------------------------------------------------------
# CSV reader and preprocessing
# ------------------------------------------------------------------
def read_and_process_ripple_file(file_name):
    """
    Read and sanitize voltage ripple CSV file.

    Parameters:
        file_name (str): CSV file path

    Returns:
        DataFrame: Time, Current, Voltage columns (numeric)
    """
    df = pd.read_csv(file_name)

    # Explicit column naming for robustness
    df.columns = ['Time', 'Current', 'Voltage']

    # Ensure numeric conversion (protects against formatting issues)
    df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
    df['Current'] = pd.to_numeric(df['Current'], errors='coerce')
    df['Voltage'] = pd.to_numeric(df['Voltage'], errors='coerce')

    return df[['Time', 'Current', 'Voltage']]


# ------------------------------------------------------------------
# Annotation helper: overshoot / undershoot
# ------------------------------------------------------------------
def add_annotations(ax, df, average_voltage):
    """
    Add overshoot and undershoot arrows relative to average VOUT.

    Parameters:
        ax (Axes): Matplotlib axis for voltage plot
        df (DataFrame): Transient data
        average_voltage (float): Nominal output voltage
    """
    max_voltage = df['Voltage'].max()
    min_voltage = df['Voltage'].min()

    overshoot = max_voltage - average_voltage
    undershoot = average_voltage - min_voltage

    # Overshoot arrow
    ax.annotate(
        '',
        xy=(df['Time'][df['Voltage'].idxmax()], max_voltage),
        xytext=(df['Time'][df['Voltage'].idxmax()], average_voltage),
        arrowprops=dict(arrowstyle='<->', color='black')
    )
    ax.text(
        df['Time'][df['Voltage'].idxmax()],
        (max_voltage + average_voltage) / 2,
        f'Overshoot = {overshoot:.2f} V',
        fontsize=10,
        ha='left'
    )

    # Undershoot arrow
    ax.annotate(
        '',
        xy=(df['Time'][df['Voltage'].idxmin()], min_voltage),
        xytext=(df['Time'][df['Voltage'].idxmin()], average_voltage),
        arrowprops=dict(arrowstyle='<->', color='black')
    )
    ax.text(
        df['Time'][df['Voltage'].idxmin()],
        (min_voltage + average_voltage) / 2,
        f'Undershoot = {undershoot:.2f} V',
        fontsize=10,
        ha='left'
    )


# ------------------------------------------------------------------
# Main plotting routine
# ------------------------------------------------------------------
def plot_individual_ripple(
    df,
    current_label,
    voltage_label,
    avg_voltage,
    ylim,
    output_file
):
    """
    Plot load current and output voltage transient with dual y-axes.

    Parameters:
        df (DataFrame): Transient data
        current_label (str): ILOAD label
        voltage_label (str): VOUT label
        avg_voltage (float): Nominal output voltage
        ylim (list): Y-axis limits for current plot
        output_file (str): Output SVG filename
    """
    fig, ax1 = plt.subplots(figsize=(8, 6))

    # ---- Current axis (left) ----
    ax1.set_xlabel('Time (µs)')
    ax1.set_ylabel('Current (mA)', color='red')
    ax1.plot(
        df['Time'],
        df['Current'],
        linestyle='--',
        color='red',
        label=current_label
    )
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.set_ylim(ylim)

    # ---- Voltage axis (right) ----
    ax2 = ax1.twinx()
    ax2.set_ylabel('Voltage (V)', color='blue')
    ax2.plot(
        df['Time'],
        df['Voltage'],
        color='blue',
        label=voltage_label
    )
    ax2.tick_params(axis='y', labelcolor='blue')

    # Add overshoot / undershoot annotations
    add_annotations(ax2, df, avg_voltage)

    # Highlight critical ripple region (specific case)
    if voltage_label == 'VOUT = 2.496 V':
        highlight_start_time = 0.000039
        highlight_end_time = 0.000042

        ax2.add_patch(
            Rectangle(
                (highlight_start_time, avg_voltage),
                highlight_end_time - highlight_start_time,
                df['Voltage'].max() - avg_voltage,
                color='red',
                alpha=0.3
            )
        )

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc='upper right'
    )

    ax1.set_title(f'{voltage_label} vs {current_label}')

    # Save high-quality vector graphic
    plt.tight_layout()
    plt.savefig(output_file, format='svg', dpi=300)
    plt.show()


# ------------------------------------------------------------------
# Script entry point
# ------------------------------------------------------------------
if __name__ == "__main__":
    df1 = read_and_process_ripple_file('voltageripple1.8.csv')
    df2 = read_and_process_ripple_file('voltageripple2.5.csv')
    df3 = read_and_process_ripple_file('voltageripple3.3.csv')

    plot_individual_ripple(
        df1, 'ILOAD 20 mA', 'VOUT = 1.8 V',
        1.8, [0, 0.025], 'high_res_ripple_output_case1.svg'
    )

    plot_individual_ripple(
        df2, 'ILOAD 100 mA', 'VOUT = 2.496 V',
        2.496, [0, 0.25], 'high_res_ripple_output_case2.svg'
    )

    plot_individual_ripple(
        df3, 'ILOAD 100 mA', 'VOUT = 3.3 V',
        3.3, [0, 0.15], 'high_res_ripple_output_case3.svg'
    )

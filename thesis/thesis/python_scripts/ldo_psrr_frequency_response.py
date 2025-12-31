import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def read_and_process_psrr_file(file_name):
    """Read and process the PSRR CSV file."""
    df = pd.read_csv(file_name)
    # Extract the column names for PSRR based on the unique parts of their names
    freq_col = [col for col in df.columns if 'freq' in col][0]
    psrr_col = [col for col in df.columns if 'PSRR' in col][0]
    df.rename(columns={freq_col: 'Frequency', psrr_col: 'PSRR'}, inplace=True)
    df['Frequency'] = pd.to_numeric(df['Frequency'], errors='coerce')
    df['PSRR'] = pd.to_numeric(df['PSRR'], errors='coerce')
    return df[['Frequency', 'PSRR']]

def plot_individual_psrr_data(df, title, xlabel, ylabel, filename, color, label):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.plot(df['Frequency'], df['PSRR'], label=label, color=color, linewidth=2)
    
    # Find the index of the closest frequency to 1000 Hz
    idx = (np.abs(df['Frequency'] - 1000)).idxmin()
    value_at_1khz = df.loc[idx, 'PSRR']
    ax.annotate(f'PSRR @ 1kHz = {value_at_1khz:.2f} dB', 
                xy=(df.loc[idx, 'Frequency'], value_at_1khz), 
                xytext=(df.loc[idx, 'Frequency'], value_at_1khz + 10), 
                arrowprops=dict(facecolor=color, shrink=0.05),
                fontsize=12, color=color, horizontalalignment='center')
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xscale('log')
    ax.grid(True, which='both', linestyle='--')
    ax.legend()

    plt.tight_layout()
    plt.savefig(filename, format='svg', dpi=300)  # Save the figure as a high-resolution PDF
    plt.show()  # Display the plot in the viewer

def plot_psrr_data(file1, file2, file3):
    """Plot PSRR data from three CSV files with specific annotations and styles."""
    df1 = read_and_process_psrr_file(file1)
    df2 = read_and_process_psrr_file(file2)
    df3 = read_and_process_psrr_file(file3)

    plot_individual_psrr_data(df1, 
                              'File 1: PSRR vs. Frequency', 
                              'Frequency (Hz)', 
                              'PSRR (dB)', 
                              '1.8V_20mA_130nm_psrr.svg', 
                              color='blue', 
                              label='PSRR @Iload 20mA')

    plot_individual_psrr_data(df2, 
                              'File 2: PSRR vs. Frequency', 
                              'Frequency (Hz)', 
                              'PSRR (dB)', 
                              '2.5V_200mA_130nm_psrr.svg', 
                              color='red', 
                              label='PSRR @Iload 200mA')

    plot_individual_psrr_data(df3, 
                              'File 3: PSRR vs. Frequency', 
                              'Frequency (Hz)', 
                              'PSRR (dB)', 
                              '3.3V_100mA_130nm_psrr.svg', 
                              color='green', 
                              label='PSRR @Iload 100mA')

# Example usage
plot_psrr_data('psrr1.8.csv', 'psrr2.5.csv', 'psrr3.3.csv')

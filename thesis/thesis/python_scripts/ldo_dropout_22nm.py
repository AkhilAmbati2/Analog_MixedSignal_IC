import pandas as pd
import matplotlib.pyplot as plt

def read_and_process_file(file_name):
    """Read and process the CSV file, renaming columns for easier access."""
    df = pd.read_csv(file_name)
    # Rename columns to more manageable names
    df.columns = ['VDD', 'Vin', 'Vout']
    # Convert 'Vin' and 'Vout' to numeric, ensuring no parsing errors
    df['Vin'] = pd.to_numeric(df['Vin'], errors='coerce')
    df['Vout'] = pd.to_numeric(df['Vout'], errors='coerce')
    return df

def plot_individual_data(df, title, xlabel, ylabel, filename, annotations, patch_coords, patch_size, patch_color):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.plot(df['VDD'], df['Vin'], label='Vin', color='blue', linewidth=2)
    ax.plot(df['VDD'], df['Vout'], label=annotations['Vout_label'], color='red', linewidth=2)
    ax.add_patch(plt.Rectangle(patch_coords, patch_size[0], patch_size[1], color=patch_color, alpha=0.3))
    ax.annotate(annotations['Vout_text'], xy=annotations['Vout_xy'], xytext=annotations['Vout_text_xy'], arrowprops=dict(arrowstyle='->'))
    ax.annotate(annotations['VDO_text'], xy=annotations['VDO_xy'], xytext=annotations['VDO_text_xy'], arrowprops=dict(arrowstyle='->'))
    ax.annotate(annotations['Region_text'], xy=annotations['Region_xy'], xytext=annotations['Region_text_xy'], arrowprops=dict(arrowstyle='->'))
    ax.annotate('Dropout Region', xy=(patch_coords[0] + patch_size[0]/2, patch_coords[1] + patch_size[1]/2), 
                xycoords='data', fontsize=12, bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='lightgreen'), ha='center')

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()

    plt.tight_layout()
    plt.savefig(filename, format='svg', dpi=300)  # Save the figure as a high-resolution PDF
    plt.show()  # Display the plot in the viewer

def plot_data(file1, file2, file3):
    """Plot VDD vs Vout from three CSV files with specific annotations and styles."""
    df1 = read_and_process_file(file1)
    df2 = read_and_process_file(file2)
    df3 = read_and_process_file(file3)

    annotations1 = {
        'Vout_label': 'Vout@Iload 100mA',
        'Vout_text': 'Vout = 1V', 
        'Vout_xy': (1.35, 0.98), 
        'Vout_text_xy': (1.45, 1.1), 
        'VDO_text': 'VDO = 358mV', 
        'VDO_xy': (1.35, 1), 
        'VDO_text_xy': (0.7, 1.1), 
        'Region_text': 'LINEAR REGION', 
        'Region_xy': (2, 1.35), 
        'Region_text_xy': (1, 1.35)
    }
    patch_coords1 = (0.55, 0.25)
    patch_size1 = (0.8, 0.8)

    plot_individual_data(df1, 
                         'Case 1: VOUT vs. VIN @ Iload 100mA', 
                         'VDD (V)', 
                         'Voltage (V)', 
                         'high_res_output_1.svg', 
                         annotations1, 
                         patch_coords1, 
                         patch_size1, 
                         'red')

    annotations2 = {
        'Vout_label': 'Vout@Iload 20mA',
        'Vout_text': 'Vout = 1.2V', 
        'Vout_xy': (1.45, 1.2), 
        'Vout_text_xy': (1.55, 1.25), 
        'VDO_text': 'VDO = 196mV', 
        'VDO_xy': (1.32, 1.1), 
        'VDO_text_xy': (0.8, 1.3), 
        'Region_text': 'LINEAR REGION', 
        'Region_xy': (2.0, 1.5), 
        'Region_text_xy': (1, 1.5)
    }
    patch_coords2 = (0.3, 0.25)
    patch_size2 = (1.1, 1)

    plot_individual_data(df2, 
                         'Case 2: VOUT vs. VIN @ Iload 20mA', 
                         'VDD (V)', 
                         'Voltage (V)', 
                         'high_res_output_2.svg', 
                         annotations2, 
                         patch_coords2, 
                         patch_size2, 
                         'green')

    annotations3 = {
        'Vout_label': 'Vout@Iload 50mA',
        'Vout_text': 'Vout = 1.5V', 
        'Vout_xy': (1.65, 1.5), 
        'Vout_text_xy': (1.8, 1.6), 
        'VDO_text': 'VDO = 170mV', 
        'VDO_xy': (1.66, 1.495), 
        'VDO_text_xy': (1.13, 1.6), 
        'Region_text': 'LINEAR REGION', 
        'Region_xy': (2, 1.8), 
        'Region_text_xy': (1.4, 1.8)
    }
    patch_coords3 = (0.6, 0.6)
    patch_size3 = (1.1, 0.9)

    plot_individual_data(df3, 
                         'Case 3: VOUT vs. VIN @ Iload 50mA', 
                         'VDD (V)', 
                         'Voltage (V)', 
                         'high_res_output_3.svg', 
                         annotations3, 
                         patch_coords3, 
                         patch_size3, 
                         'yellow')


# Read the data
df1 = read_and_process_file('dropoutvoltage_1V.csv')
df2 = read_and_process_file('dropoutvoltage_1.2V.csv')
df3 = read_and_process_file('dropoutvoltage_1.5V.csv')

# Generate individual plots
plot_data('dropoutvoltage_1V.csv', 'dropoutvoltage_1.2V.csv', 'dropoutvoltage_1.5V.csv')

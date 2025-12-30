"""
Script: ldo_csv_postprocess.py

Purpose:
Post-process LDO design evaluation data exported from circuit simulations.
The script cleans column names, extracts key metrics (e.g., phase margin),
and generates a cleaned CSV suitable for plotting and analysis.

Inputs:
- CSV file containing LDO design metrics (exported from simulation)

Outputs:
- Cleaned CSV file with standardized column names
- Phase margin data preserved for analysis

Notes:
- Technology-agnostic (no PDK or model data included)
- Intended for post-processing and visualization workflows
"""



import pandas as pd

# Function to clean the CSV
def clean_csv(file_path, output_path):
    # Read the CSV data
    df = pd.read_csv(file_path, delimiter=',')
    
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Define the correct column names mapping
    column_mapping = {
        'Design_Point': 'Design Point',
        'PSRR_LDO_@1KHz (dB)': 'PSRR LDO @1KHz',
        'Phase Margin_LDO (deg)': 'Phase Margin LDO',
        'Vout_DO': 'Vout DO',
        'LDO_DO (V)': 'LDO DO',
        'Vout_undershoot (V/A)': 'Vout undershoot',
        'Vout_Overshoot (V/A)': 'Vout Overshoot'
    }


    # Rename columns
    df.rename(columns=column_mapping, inplace=True)

    # Extract Phase Margin values and corresponding design point numbers before dropping columns
    phase_margin_data = df[['Design Point', 'Phase Margin LDO']].copy()

    # Drop unnecessary columns
    df.drop(columns=['Design_Point .1', 'Design_Point .2', 'Phase Margin LDO'], inplace=True, errors='ignore')

    # Save the cleaned DataFrame to a new CSV file
    df.to_csv(output_path, index=False)
    
    return df, phase_margin_data

# Specify the input and output file paths
input_file = 'ldo_design_data.csv'
output_file = 'ldo_design_data_cleaned.csv'

# Clean the CSV file
cleaned_df, phase_margin_data = clean_csv(input_file, output_file)

# Add phase_margin_data back into cleaned_df
cleaned_df_with_phase_margin = cleaned_df.copy()
cleaned_df_with_phase_margin['Phase Margin LDO'] = phase_margin_data['Phase Margin LDO']

# Save the final DataFrame with phase margin data to the cleaned output file
cleaned_df_with_phase_margin.to_csv(output_file, index=False)

# Display the final DataFrame
print("Final DataFrame with Phase Margin Data:")
print(cleaned_df_with_phase_margin.head())

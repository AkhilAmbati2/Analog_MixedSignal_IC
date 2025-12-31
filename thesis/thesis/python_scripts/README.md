# Simulation Analysis & Plotting Scripts

This directory contains Python scripts used to post-process analog/mixed-signal
circuit simulation data exported from Cadence (CSV format).

The scripts focus on **LDO and OTA performance analysis**, covering:
- Stability and frequency-domain metrics
- Load-transient and ripple behavior
- Power-supply rejection (PSRR)
- Multi-objective optimization result screening

All scripts are written for **methodology demonstration and visualization**.
No PDK files, proprietary models, or confidential parameters are included.

---

## Script Overview

### `ldo_dropout_22nm.py`
Analyzes LDO dropout behavior by plotting VOUT and VIN versus VDD.
Highlights the dropout region and annotates key operating points.

**Key metrics:** Dropout voltage, linear regulation region

---

### `ldo_transient_ripple_evaluation.py`
Evaluates time-domain LDO load-transient performance.
Plots ILOAD steps and VOUT response, extracting overshoot and undershoot.

**Key metrics:** Transient ripple, overshoot, undershoot

---

### `ldo_psrr_frequency_response.py`
Performs frequency-domain PSRR analysis using AC simulation data.
Plots PSRR versus frequency and annotates PSRR at 1 kHz.

**Key metrics:** PSRR, frequency response

---

### `analog_optimization_color_spectrum_dashboard.py`
Visual dashboard for comparing optimization algorithms (BFGS, CG,
Brent–Powell, Hooke–Jeeves) using qualitative color-spectrum grading.

**Key metrics:** Gain, phase margin, slew rate, UGF, device operating regions

---

### `ldo_design_color_spectrum_analysis.py`
Single-design optimization screening using color-spectrum visualization.
Useful for rapid identification of spec-compliant and violating design points.

---

### `ldo_csv_postprocess.py`
Utility script for reading, cleaning, and aggregating CSV simulation outputs.
Used as a preprocessing step for higher-level analysis scripts.

---

## Requirements
- Python ≥ 3.9
- numpy
- pandas
- matplotlib
- plotly (for dashboard visualizations)

---

## Notes
- CSV files are assumed to be sanitized and non-confidential
- Scripts are modular and reusable across technology nodes
- Intended for academic and industrial design-flow demonstration

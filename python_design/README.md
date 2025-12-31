# Python-Based Design Automation

This folder contains Python scripts used for analog and mixed-signal
circuit sizing, analysis, and visualization.

## Included Methods
- Square-law MOS sizing
- gm/ID-based design methodology
- Parametric sweeps and plotting

## Applications
- Transistor sizing for analog blocks
- Design trade-off exploration
- Support for schematic

## Tools & Libraries
- Python
- NumPy
- SciPy
- Pandas
- Matplotlib

Note:
- Scripts focus on **design methodology**, not foundry-specific implementation
- Technology parameters are either:
  - explicitly stated (e.g., square-law models for 130 nm), or
  - provided via sanitized lookup tables (gm/ID methodology)
- No proprietary PDK files or confidential data are included

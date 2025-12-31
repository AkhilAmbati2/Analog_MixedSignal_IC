# Square-Law Design Models

This folder contains **first-order square-law-based design scripts** used for
rapid, pre-Cadence exploration of analog circuits.

## Purpose
- Provide intuition and trend analysis before schematic simulation
- Enable fast parameter tuning (bias currents, compensation, W/L ratios)
- Establish a reasonable starting point for detailed gm/ID or SPICE-based design

## Contents

### `ldo_squarelaw_pre_cadence_model_130nm.py`
First-order behavioral model of an LDO implemented in **130 nm technology**.
Includes:
- Square-law sizing of the LDO error amplifier (controller OTA)
- First-order pass-device sizing from dropout and load current
- Simplified output resistance model (gds ≈ λ·Id)
- Symbolic loop transfer-function derivation and stability analysis

## Notes
- Square-law assumptions are most valid for older nodes and longer channel lengths
- Results are intended for **trend analysis**, not final sign-off

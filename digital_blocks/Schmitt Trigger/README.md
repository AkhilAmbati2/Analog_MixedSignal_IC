# Schmitt Trigger — CMOS Inverter with Hysteresis

This block implements a **CMOS Schmitt Trigger** designed and verified at the
**transistor level** using **Cadence Virtuoso**.

The Schmitt Trigger converts **slow, noisy, or analog input signals** into a
clean digital output by introducing **intentional hysteresis** between the
rising and falling switching thresholds.

---

## Purpose
- Noise-immune signal conditioning  
- Conversion of slow or noisy analog inputs to digital levels  
- Input buffering for clocks, resets, and sensor interfaces  
- Prevention of output chatter near threshold  

---

## Architecture
- CMOS inverter with **positive feedback**
- Asymmetric pull-up and pull-down strength
- Static operation (no dynamic storage)
- Single-ended input, rail-to-rail output

The feedback path shifts the effective switching threshold depending on the
current output state, creating two distinct trip points:
- Rising threshold (**VTH+**)
- Falling threshold (**VTH−**)

---

## Functional Operation
Unlike a standard inverter, the Schmitt Trigger exhibits
**memory-dependent switching behavior**:

- When **Vin increases**, the output switches at **VTH+**
- When **Vin decreases**, the output switches at **VTH−**

This separation prevents multiple output transitions when the input is noisy or
slow-moving.

---

## DC Transfer & Hysteresis Characterization

DC analysis was performed by sweeping **Vin from 0 → VDD** and observing the
output transition points.

All threshold measurements are referenced to the **50% output level**
(≈ **400 mV**).

### Extracted Thresholds (Typical Corner)
- **Rising threshold (VTH+)**: ≈ 460–490 mV  
- **Falling threshold (VTH−)**: ≈ 250–310 mV  

\[
V_{HYS} = V_{TH+} - V_{TH-}
\]

- **Measured hysteresis width:** ≈ **160–220 mV**

This confirms correct Schmitt Trigger behavior and strong noise margin.

---

## Transient Verification (Slow Ramp Input)

Transient simulations were performed using a **slow triangular / ramp input**
to emulate realistic sensor-like signals.

### Observations
- Output switches only once per threshold crossing  
- No multiple transitions during slow input slopes  
- Clean rail-to-rail output behavior  

This validates that hysteresis is effective **in the time domain**, not only in
DC.

---

## Noise Immunity Verification

Additional transient simulations were run with **noise superimposed on the input
signal**, biased near the switching region.

### Result
- Output remains stable within the hysteresis window  
- No false triggering or oscillation observed  

This demonstrates the primary advantage of the Schmitt Trigger over a standard
CMOS inverter.

---

## Process Corner Analysis

DC hysteresis extraction was repeated across **process corners**.

### Corners Simulated
- TT (Typical-Typical)  
- SS (Slow-Slow)  
- FF (Fast-Fast)  

### Observations
- Switching thresholds shift moderately with process
- Hysteresis window is preserved across all corners
- No functional failures observed

This confirms **robust operation under PVT variation**.

---

## Representative Electrical Metrics

| Parameter | Typical Value |
|---------|---------------|
| Supply Voltage | 0.8 V |
| Output Swing | Rail-to-rail |
| VTH+ | ~470 mV |
| VTH− | ~280 mV |
| Hysteresis Width | ~190 mV |
| Noise Immunity | High |

(Exact values depend on sizing and corner conditions.)

---

## Verification Summary
- DC transfer and hysteresis extraction  
- Transient verification with slow input ramps  
- Noise immunity validation  
- Process-corner robustness confirmed  
- Consistent switching behavior observed  

---

## Notes
- All plots are **sanitized** and free of proprietary PDK information  
- No foundry models, layouts, or netlists are included  
- Documentation focuses on **design intent and verification methodology**

---

## Files in This Folder
- `Schmitt_trigger.sch` — Transistor-level schematic  
- `Schmitt_trigger_TB.sch` — Testbench  
- `results/` — DC, transient, and corner plots  


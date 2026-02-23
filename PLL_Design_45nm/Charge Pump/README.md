# Charge Pump (CP)

![Technology](https://img.shields.io/badge/Technology-45nm%20CMOS-blue)
![Type](https://img.shields.io/badge/Architecture-Charge%20Pump-orange)
![Design](https://img.shields.io/badge/Design-Phase%20Locked%20Loop-brightgreen)

## Overview
This folder contains the design and characterization of a **current-steering Charge Pump (CP)** implemented in **45 nm CMOS**.

The charge pump interfaces the **PFD** and the **loop filter**. It converts `UP_IN` / `DOWN_IN` logic pulses into well-defined current packets **Icp** that charge/discharge the loop filter capacitor, generating the VCO control voltage **Vctrl**.

---

## Circuit Description
The design is organized into five sub-blocks (for matching and predictable biasing):

1. **Main Bias Mirror**
   - Generates internal bias currents from the reference current (**IBIAS**).

2. **Cascode Bias Generation**
   - Generates cascode bias voltages (**VBiasP**, **VBiasN**) for improved output compliance.

3. **Intermediate UP/DOWN Mirrors**
   - Buffers and isolates the bias network from the output stage.

4. **Output Mirrors (P & N)**
   - **P-mirror sources** current during `UP_IN`
   - **N-mirror sinks** current during `DOWN_IN`

5. **Switching Devices**
   - Gate the sourcing/sinking paths with `UP_IN` and `DOWN_IN`.

---

## Key Specifications (Measured)

| Parameter | Value | Notes |
|---|---:|---|
| Technology | 45 nm CMOS | |
| Supply Voltage | 1.0 V | |
| Nominal Pump Current (Icp) | ~20.5 µA | measured with pulse test (see below) |
| UP/DOWN Current Mismatch | ~0.73% | at Vctrl ≈ 0.5 V |
| Recommended Compliance Region | 0.2–0.8 V | stable/high-impedance region |
| Topology | Gate-switched cascode mirrors | improved compliance |

> Note: Pump current varies with Vctrl due to finite output resistance and compliance limits near the rails.

---

## Simulation Setup (How currents were measured)
To avoid ambiguity in sign conventions, UP and DOWN currents were measured using the **loop filter capacitor current**:
- **I(C1/PLUS)** was clipped over the *flat region* of a 2 ns pulse (excluding switching spikes).
- The scalar output reports **average current during the ON window**.

Pulse settings:
- Pulse width: **2 ns**
- Non-overlapping UP-only and DOWN-only tests

---

## Results

### 1) Schematic
![Charge Pump Schematic](./images/charge_pump_schematic.png)

### 2) UP-only pulse test (average current extraction)
![UP-only waveform and scalar current](./images/up_only_waveform.png)

### 3) DOWN-only pulse test (average current extraction)
![DOWN-only waveform and scalar current](./images/down_only_waveform.png)

### 4) Compliance / Current vs Vctrl (VIC sweep)
UP current vs Vctrl:
![IUP vs Vctrl](./images/iup_vs_vctrl.png)

DOWN current vs Vctrl:
![IDOWN vs Vctrl](./images/idown_vs_vctrl.png)


---

## Pin Description
| Pin Name | Type | Description |
|---|---|---|
| UP_IN | Input | Control signal (source current) |
| DOWN_IN | Input | Control signal (sink current) |
| IOUT | Output | Pump output to loop filter |
| IBIAS | Input | Reference bias current |

---

## Notes
- Schematics/layout are **sanitized**
- No PDK files, proprietary models, or restricted data are included
- Figures are for **educational/portfolio** purposes

---

## References
1. M. Mestice, G. Ciarpi, D. Rossi, and S. Saponara, “An Integrated Charge Pump for Phase-Locked Loop Applications in Harsh Environments,” *Electronics*, vol. 13, no. 4, p. 744, Feb. 2024. DOI: 10.3390/electronics13040744

---
*Part of the 1 GHz PLL Design Project.*

# D-Flip Flop (DFF) Design in 45nm CMOS

![Technology](https://img.shields.io/badge/Technology-45nm%20CMOS-blue)
![Type](https://img.shields.io/badge/Architecture-D--Flip%20Flop-orange)
![Design](https://img.shields.io/badge/Design-Phase%20Locked%20Loop-brightgreen)

## Overview
This folder contains the schematic design and characterization results of a **D-Flip Flop (DFF)** designed in **45nm CMOS technology**. The flip-flop is a critical building block for the Phase Frequency Detector (PFD) and Frequency Divider in the Phase-Locked Loop (PLL) system.

The design features an **Active High Reset**, optimized for high-speed switching suitable for GHz-range applications.

## Key Specifications

| Parameter | Value | Condition |
| :--- | :--- | :--- |
| **Technology** | 45 nm CMOS | |
| **Supply Voltage ($V_{DD}$)** | 1.0 V | |
| **Clock-to-Q Delay** | **60 ps** | Unloaded (Intrinsic) |
| **Setup Time ($T_{setup}$)** | **~50 ps** | Data stable before Clock |
| **Reset Logic** | Active High | Logic '1' clears output |


## Design & Simulation Strategy

### 1. Schematic Design
The topology utilizes a transmission-gate-based master-slave configuration (or standard CMOS NAND-based topology) to ensure robust logic levels and minimized leakage.
* **File:** `schematic.png`
* **Sizing:** Transistors are sized to balance rise/fall times ($W_p \approx 2 \times W_n$) while keeping area minimal.

### 2. Propagation Delay ($T_{C-Q}$)
Measured the delay from the rising edge of the Clock (50%) to the valid transition of the Output Q (50%).
* **Result:** The intrinsic delay was measured at **60 ps** without load.
* *Note:* Initial simulations with a 10fF load showed ~490ps delay, confirming the need for output buffering when driving long interconnects.

### 3. Setup Time Characterization
A **Parametric Sweep** analysis was performed to determine the setup time.
* **Method:** The Data (`D`) arriving time was swept closer to the Clock (`CLK`) rising edge in **20 ps steps**.
* **Criterion:** The setup time is defined as the time margin where the Clock-to-Q delay increases by >10% or the output fails to switch.
* **Result:** Valid data capture was observed down to **50 ps** before the clock edge.
* **File:** `transient_setup.png`

### 4. Hold Time Characterization
Verified the minimum time Data must remain stable after the Clock edge.
* **Method:** Data transition was swept starting from the Clock edge outwards.
* **File:** `transient_hold.png`

## Files Included
* **`schematic.png`**: Transistor-level schematic of the DFF.
* **`transient.png`**: Waveforms showing the setup time parametric sweep (Pass/Fail boundary).

---
*Part of the 1GHz PLL Design Project.*

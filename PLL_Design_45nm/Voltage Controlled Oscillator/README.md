# Voltage Controlled Oscillator (VCO) Design

![Technology](https://img.shields.io/badge/Technology-45nm%20CMOS-blue)
![Type](https://img.shields.io/badge/Architecture-Voltage%20Controlled%20Oscillator-orange)
![Design](https://img.shields.io/badge/Design-Phase%20Locked%20Loop-brightgreen)   

## 📌 Overview
This directory contains the design and simulation of the **Current-Starved Voltage Controlled Oscillator (CS-VCO)**. The VCO is the heart of the PLL, generating the high-frequency clock signal (1.0 GHz). Its frequency is controlled by the analog voltage ($V_{CTRL}$) coming from the Loop Filter.

For this project, a **7-Stage Current-Starved Ring Oscillator** topology was chosen for its wide tuning range and linear voltage-to-frequency gain ($K_{VCO}$).

---

## ⚙️ Design Specifications
The VCO is designed to oscillate at a center frequency of 1.0 GHz with sufficient tuning margin to cover Process, Voltage, and Temperature (PVT) variations.

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Center Frequency** | **1.0 GHz** | Achieved at $V_{CTRL} \approx 488 \text{ mV}$. |
| **Supply Voltage** | 1.0 V | Standard core voltage for 45nm CMOS. |
| **Number of Stages** | **7** | Odd number of inverters required for oscillation. |
| **Tuning Range** | 0.8 GHz - 1.4 GHz | Covers the target frequency comfortably. |
| **Linearity** | High | Current-starved topology ensures roughly linear $f_{out}$ vs $V_{ctrl}$. |

---

## 📸 Schematic
The design consists of a bias circuit (current mirrors), the ring oscillator core, and an output buffer.

* **Bias Stage:** Converts $V_{CTRL}$ into a current ($I_{bias}$) that limits the charging/discharging speed of the inverters.
* **Ring Core:** 7 cascaded inverter stages. The delay of each stage is controlled by the starvation transistors (Top PMOS / Bottom NMOS).
* **Output Buffer:** A standard inverter at the end squares the output wave and isolates the oscillator loop from the capacitive load of the Divider.

![VCO Schematic](schematic.png)
*Figure 1: Schematic of the 7-Stage Current-Starved VCO with Output Buffer.*

---

## 📊 Simulation Results
The transient simulation verifies the oscillation stability and frequency at the lock voltage.

* **Simulation Condition:** $V_{CTRL}$ fixed at **488 mV** (The PLL lock voltage).
* **Output (Green):** Stable rail-to-rail oscillation at **1.00 GHz**.
* **Control Voltage (Pink):** Constant DC input showing the operating point.

![VCO Transient Response](transient.png)
*Figure 2: Transient response showing steady-state 1 GHz oscillation.*

---

## 📝 Key Features
* **Current-Starved Topology:** Allows precise frequency control by limiting the current available to charge the parasitic capacitances of the internal nodes.
* **Positive Gain:** As $V_{CTRL}$ increases $\rightarrow$ Current increases $\rightarrow$ Delay decreases $\rightarrow$ **Frequency Increases**.
* **Area Efficient:** Implemented using only standard logic transistors without large inductors or capacitors.

 ## Notes
- All schematics and layouts are **sanitized**
- No foundry PDK files, device models, or proprietary data are included
- Images are provided for **educational and portfolio purposes only**
- The focus is on **design methodology**, not process-specific optimization

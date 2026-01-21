# Frequency Divider Design (Divide-by-10)

![Technology](https://img.shields.io/badge/Technology-45nm%20CMOS-blue)
![Type](https://img.shields.io/badge/Architecture-Frequency%20Divider-orange)
![Design](https://img.shields.io/badge/Design-Phase%20Locked%20Loop-brightgreen)

## 📌 Overview
This directory contains the design and simulation of the **High-Speed Frequency Divider**. The role of this block is to divide the 1.0 GHz VCO output down to 100 MHz to match the Reference Clock frequency for the Phase Frequency Detector (PFD).

Because the input frequency (1 GHz) is relatively high for standard digital logic in 45nm, a **two-stage hybrid architecture** was implemented.

---

## ⚙️ Design Architecture
The divider achieves a total division ratio of **N = 10** using two cascaded stages:

### **Stage 1: High-Speed TSPC Divide-by-2**
* **Logic Style:** True Single-Phase Clock (Dynamic Logic).
* **Function:** Divides 1 GHz $\rightarrow$ 500 MHz.
* **Why TSPC?** Standard static CMOS Flip-Flops are slow and power-hungry at 1 GHz. TSPC is faster and uses fewer transistors (reduced load on VCO).
* **Critical Fix:** An input **Inverter Buffer** was added to "square up" the sinusoidal VCO output. Without this, the dynamic logic failed to hold charge due to slow edge rates.

### **Stage 2: Modulo-5 Asynchronous Counter**
* **Logic Style:** Static CMOS Logic (Standard Cell D-Flip Flops).
* **Function:** Divides 500 MHz $\rightarrow$ 100 MHz.
* **Topology:** 3-bit Ripple Counter with asynchronous Reset.
* **Reset Logic:** An AND gate monitors outputs $Q_0$ and $Q_2$. When the count reaches **5 (101)**, it triggers a global reset to 0.

---

## 📸 Schematic
The schematic shows the input buffering, the TSPC stage, and the 3-stage ripple counter chain.

* **Left:** Input Inverter & TSPC DFF (Self-looped $\bar{Q} \rightarrow D$).
* **Middle:** 3 Standard DFFs forming the ripple counter. Note the clocking scheme: $Q_{bar}$ of the previous stage drives $CLK$ of next stage.
* **Right:** AND Gate Feedback for Modulo-5 Reset.

![Frequency Divider Schematic](schematic.png)
*Figure 1: Schematic of the Divide-by-10 circuit (TSPC Stage + Modulo-5 Counter).*

---

## 📊 Simulation Results
The transient response confirms the correct division at every stage.

* **Top Trace (Purple):** Final Output (`F_DIV`). Frequency = **100 MHz**. (Divide-by-10)
* **Middle Trace (Orange):** Output of TSPC Stage (`F1`). Frequency = **500 MHz**. (Divide-by-2)
* **Bottom Trace (Yellow):** Internal Counter Bit (`F2`).

![Transient Response](transient.png)
*Figure 2: Transient simulation showing the stepwise frequency division from 1 GHz (implicit input) to 500 MHz to 100 MHz.*

---

## 🛠 Design Challenges & Solutions
| Challenge | Symptom | Solution |
| :--- | :--- | :--- |
| **Input Slewing** | TSPC acted as a buffer (1GHz out) instead of dividing. | Added strong **Inverter Buffer** to sharpen VCO edges. |
| **Logic Threshold** | TSPC PMOS too weak to pull up node. | Increased PMOS width to **240nm** (2:1 ratio). |
| **Startup Failure** | Output remained at 0V (Dead zone). | Added **Initial Condition (0V)** to internal TSPC node to kickstart oscillation. |
| **Counter Error** | Divided by 3 instead of 5. | Corrected wiring: Connected AND gate input to **FF3** ($Q_2$) instead of FF2 ($Q_1$). |

## Notes
- All schematics and layouts are **sanitized**
- No foundry PDK files, device models, or proprietary data are included
- Images are provided for **educational and portfolio purposes only**
- The focus is on **design methodology**, not process-specific optimization

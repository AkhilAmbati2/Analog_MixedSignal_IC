# Single-Stage Operational Transconductance Amplifier (OTA)

![Technology](https://img.shields.io/badge/Technology-CMOS-blue)
![Type](https://img.shields.io/badge/Architecture-Single%20Stage%20OTA-orange)
![Design](https://img.shields.io/badge/Design-Fully%20Custom-green)

## Overview
This repository presents a **fully custom single-stage Operational Transconductance Amplifier (OTA)** designed at the **transistor level** with a strong emphasis on **matching, symmetry, and layout robustness**.

The OTA is intended for use in **low-power analog signal paths**, such as biasing circuits, LDOs, comparators, and as a gain stage in mixed-signal systems.

The design follows **best-practice analog layout methodologies**, including **common-centroid matching**, **guard rings**, and **strict symmetry** to minimize mismatch, gradient effects, and substrate noise.

---

## Architecture Description
The OTA is based on a **single-stage topology** consisting of:
- Differential NMOS input pair
- PMOS active load
- Tail current source with enable control
- Single-ended output

The amplifier converts a **differential input voltage** into a **single-ended output current/voltage**, providing high intrinsic gain with minimal complexity.

---

## Schematic


::contentReference[oaicite:0]{index=0}


**Key Features**
- Differential input pair with matched devices
- Biasing via current mirror
- Enable-controlled tail current source
- Clean single-ended output node

---

## Physical Layout


::contentReference[oaicite:1]{index=1}


**Layout Techniques Applied**
- **Common-centroid matching** for critical transistor pairs
- **Perfect left-right symmetry** for the differential signal path
- **Guard rings** around sensitive analog devices
- Dedicated **VDD/VSS routing** to reduce IR drop and noise coupling
- Compact placement to minimize parasitics

---

## Matching & Reliability Considerations
- All matched devices share identical orientation and environment
- Dummy devices used where required to improve edge symmetry
- Guard rings mitigate latch-up and substrate coupling
- Symmetric routing minimizes systematic offset

---

## Design Intent
This OTA was designed to:
- Demonstrate **analog layout discipline**
- Serve as a **reusable analog IP block**
- Provide a clean baseline for gain, offset, and noise analysis
- Be suitable for integration into larger analog/mixed-signal systems

---

## Notes
- All schematics and layouts are **sanitized**
- No foundry PDK files, device models, or proprietary data are included
- Images are provided for **educational and portfolio purposes only**
- The focus is on **design methodology**, not process-specific optimization

---

*Designed using industry-standard full-custom analog IC design practices.*

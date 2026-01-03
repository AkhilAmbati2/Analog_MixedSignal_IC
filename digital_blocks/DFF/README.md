# D Flip-Flop (DFF) — 14 nm CMOS

This block implements a **positive-edge-triggered D Flip-Flop (DFF)** designed
and verified in a **14 nm CMOS technology** using Cadence Virtuoso.

The DFF is realized using **inverter-based storage nodes** and
**clock-controlled transmission logic**, and was characterized not only
functionally, but also for **setup and hold timing constraints**.

---

## Purpose
- Edge-triggered data storage
- Clock-domain synchronization
- Fundamental sequential element for registers, counters, and control logic

---

## Architecture
- Master–slave latch topology
- Static inverter-based storage
- Clocked transmission gates
- Optional reset/set logic (if present)

The master latch samples input **D** when the clock is low, and the slave latch
updates the output **Q** on the **rising edge of the clock**, ensuring
non-transparent operation.

---

## Functional Operation
The DFF updates its output **Q** only on the rising edge of the clock.
Between clock edges, changes at **D** do not propagate to **Q**, confirming
correct edge-triggered behavior and absence of transparency.

**Reference plot:**
- `dff_functional_timing.png`

---

## Timing Characterization

Timing behavior was analyzed by **shifting the data (D) arrival time relative
to the clock edge** and observing the resulting output behavior.
All timing measurements are referenced to the **50% (400 mV) crossing points**
of the signals.

### 1. Functional / Safe Operation
- **D delay:** `td = 17 ns`
- D transitions well before the clock rising edge
- Large positive setup margin

This condition represents normal, safe operation.

---

### 2. Setup-Time Boundary Condition
- **D delay:** `td ≈ 20.26 ns`
- D transitions approximately at the clock edge
- Measured setup margin ≈ 0 ps (slightly negative)

This condition demonstrates the **setup-time limit**, where data arrives too
late to be reliably captured.

**Reference plot:**
- `dff_setup_time.png`

---

### 3. Hold-Time Stress Condition
- **D delay:** `td = 20.35 ns`
- D transitions shortly *after* the clock edge
- Measured hold margin ≈ 50–100 ps

This condition stresses the **hold-time requirement**, illustrating sensitivity
to data changes immediately after sampling.

**Reference plot:**
- `dff_hold_time.png`

---

## Measured Timing Metrics (Representative)
- Clock-to-Q delay: ~90–100 ps
- Setup-time boundary: ~0 ps margin
- Hold-time stress demonstrated at ~100 ps after clock edge

(Exact values depend on stimulus and loading conditions.)

---

## Verification Summary
- Transient functional verification
- Setup-time boundary identification
- Hold-time stress analysis
- Consistent behavior across multiple clock cycles
- DRC/LVS performed in Cadence (not included here)

---

## Notes
- All figures are **sanitized** and free of proprietary PDK information
- No schematics, layouts, netlists, or foundry data are included
- This documentation focuses on **design intent and timing methodology**

---

# CMOS Inverter (14 nm)

This block implements a CMOS inverter designed and verified in a 14 nm CMOS technology using Cadence Virtuoso.

## Purpose
- Fundamental digital logic element
- Reference cell for delay, power, and noise-margin analysis
- Baseline block for mixed-signal circuits

## Architecture
- Complementary NMOS–PMOS pull-down/pull-up structure
- Ratioed sizing for symmetric switching threshold

## Analog Perspective
When biased around the switching point, the inverter operates as a high-gain
single-stage amplifier with a gain of approximately:
Av ≈ (gm_n + gm_p) · (r_on || r_op)

## Verification Performed
- DC transfer characteristic (VTC)
- Transient response (rise/fall delay)
- DRC/LVS (Cadence)

## Notes
Figures are sanitized; no proprietary PDK data is included.

"""
--------------------------------------------------------------------
File: ldo_squarelaw_pre_cadence_model_130nm.py

LDO (130nm) — Square-law pre-Cadence behavioral sizing + loop analysis

What this script is:
    A fast, first-order estimator to explore LDO loop behavior BEFORE Cadence.
    It combines:
      (1) Square-law sizing for the LDO error amplifier (OTA/controller)
      (2) A simplified output resistance model via channel-length modulation:
              gds ≈ λ · Id   and   ro ≈ 1/(λ · Id)
      (3) First-order MOS capacitance estimates in saturation:
              Cgg ≈ (2/3) · Cox · W · L   (overlap/fringing not included)
      (4) Symbolic loop transfer-function derivation for vfb/vs
          and frequency-domain evaluation (Bode + pole-zero plot)

What this script is NOT:
    - Not a replacement for Spectre/Cadence sign-off
    - Not a gm/ID lookup-table flow (no device characterization tables here)

Intended use:
    - Rapid parameter tweaking (Ibias, Cc, Rc, pass-device sizing, feedback ratio)
    - Quick sanity check of loop-gain trends and phase-margin sensitivity
    - Provide a reasonable starting point before schematic simulation

Notes:
    Square-law is most defensible for older nodes (e.g., 130nm) and/or longer L.
    Treat results as trend guidance (pre-Cadence), not final numbers.

Author:
    Akhil Ambati
--------------------------------------------------------------------
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from control.matlab import TransferFunction, bode, pzmap, margin


# ======================================================================
# User inputs / design targets
#   Includes:
#     - Error amplifier (controller) targets: SR, GBW, controller load cap (Cl)
#     - LDO system targets: Iload, Cout, dropout, Vout, reference
# ======================================================================

Vdd = float(input("input value of Vdd = "))               # [V]
Vss = float(input("input value of Vss = "))               # [V]
SR = float(input("input value of SR = "))                 # [V/s]
Cl = float(input("input value of Cl = "))                 # [F]  (controller output load cap for estimation)
GB = float(input("input value of GB = "))                 # [Hz] (controller unity-gain bandwidth target)
phi = float(input("input value of Phi = "))               # [deg] (optional—informational)

# ======================================================================
# LDO system specifications
#   These define the plant (pass device + Cout/ESR/load) and feedback ratio.
# ======================================================================

Iload_LDO = float(input("input value of Iload = "))        # [A]
C_out_LDO = float(input("input value of Cout = "))         # [F]
LDO_DO = float(input("input value of LDO_DO = "))          # [V] dropout
Vout_LDO = float(input("input value of Vout_LDO = "))      # [V]
V_Ref = 1.2                                                # [V] reference (set for your 130nm system)


# ======================================================================
# Physical constants and process parameters (130nm placeholders)
# ======================================================================

T = 300
Kb = 1.3806226e-23

# Thresholds (placeholder)
Vtn = 0.79               # [V]
Vtp = 0.775              # [V] magnitude (use positive magnitude)
Vtn_max = 1.5

# Process transconductance parameters (placeholder)
k_n = 130e-6             # [A/V^2]
k_p = 35e-6              # [A/V^2]

# Oxide & permittivity (placeholder)
t_ox = 1.2e-9
e0 = 8.854214871e-12
e_SiO2 = 3.9
e_ox = e0 * e_SiO2

# Headroom / saturation approximations (placeholder)
Vdsatp = 0.3
Vdsatn = 0.2

# Optional bounds (placeholder)
Vout_max = 4.5
Vout_min = 0.4
Vin_cm_max = 4.8
Vin_cm_min = 1.2

omega1 = (2 * np.pi) * GB
C_ox = e_ox / t_ox
mu_n = k_n / C_ox
mu_p = k_p / C_ox


# ----------------------------------------------------------------------
# Square-law ONLY: MOS gate capacitance estimate in saturation
# ----------------------------------------------------------------------
def cgg_saturation_approx(W: float, L: float, Cox: float) -> float:
    """
    First-order MOS gate capacitance in saturation:
        Cgg ≈ (2/3) * Cox * W * L
    """
    return (2.0 / 3.0) * Cox * W * L


# ----------------------------------------------------------------------
# Square-law ONLY: channel-length modulation model
#   gds ≈ λ * Id  and ro ≈ 1/(λ*Id)
# ----------------------------------------------------------------------
lambda_n = 0.05  # 1/V  (NMOS) placeholder: tune using one DC operating point if available
lambda_p = 0.06  # 1/V  (PMOS) placeholder: tune using one DC operating point if available


# ======================================================================
# Error amplifier (controller OTA) first-order sizing
#   The OTA is the LDO controller. We size it from SR and GBW targets.
# ======================================================================

# (1) Initial compensation cap guess (classic Miller-comp intuition)
Cc = 0.3 * Cl

# (2) gm required from GBW target (first-order)
gm1 = omega1 * Cc
gm2 = gm1

# (3) Slew-rate sets tail current (classic Miller OTA approximation)
I5 = Cc * SR
Ibias = I5
I8 = I5

I1 = I5 / 2
I2 = I1
I3 = I1
I4 = I2

# (4) Square-law sizing: input pair M1/M2
#     S = W/L
S1 = (gm1 ** 2) / (2 * k_n * I1)
S2 = S1

# (5) Square-law sizing: PMOS active load M3/M4
Vdsat3 = Vdd - Vin_cm_max - Vtp + Vtn
S3 = I5 / (k_p * (Vdsat3 ** 2))
S4 = S3
gm4 = np.sqrt(2 * k_p * S4 * I4)
gm3 = gm4

# (6) Square-law sizing: tail device M5/M8
# NOTE: Keep your original intent; ensure Vdsat5 remains physically valid (>0).
Vdsat5 = Vin_cm_min - Vss - np.sqrt(2 * I5 * 10e-6 / k_n * S1) - Vtn_max
S5 = 2 * I5 / (k_n * (Vdsat5 ** 2))
S8 = S5

# (7) Controller second stage sizing (M6/M7) — preserves your original design intent
gm6 = 10 * gm1
S6 = (gm6 / gm4) * S4
I6 = gm6 ** 2 / (2 * k_p * S6)
I7 = I6

S7 = (I7 / I5) * S5
gm7 = np.sqrt(2 * k_p * S7 * I7)

# (8) Output resistances using channel-length modulation only (no gm/ID tables)
gds2 = lambda_n * I2
gds4 = lambda_p * I4
gds6 = lambda_p * I6
gds7 = lambda_n * I7

# (9) Compensation resistor
Rc = 2 / gm6

# (10) Static power estimate (controller only)
P = Vdd * (I6 + I5)

# (11) Controller stage gains / resistances
Av1 = gm1 / (gds2 + gds4)
Av2 = (2 * gm6) / (gds6 + gds7)
R1 = 1 / (gds2 + gds4)
R2 = 1 / (gds6 + gds7)

# (12) Choose a single L for first-order sizing (longer L improves square-law plausibility)
L = 1e-6  # [m]

W1 = L * S1
W2 = L * S2
W3 = L * S3
W4 = L * S4
W5 = L * S5
W6 = L * S6
W7 = L * S7
W8 = L * S8

# (13) First-order node capacitances from Cgg instead of hard-coded constants
Cgg1 = cgg_saturation_approx(W1, L, C_ox)
Cgg3 = cgg_saturation_approx(W3, L, C_ox)
Cgg6 = cgg_saturation_approx(W6, L, C_ox)
Cgg7 = cgg_saturation_approx(W7, L, C_ox)

# Node capacitances (first-order)
C1 = 2 * Cgg1 + Cgg3 + Cc
C2 = Cgg6 + Cgg7 + Cl

# ======================================================================
# LDO pass-device and feedback network
# ======================================================================

# (14) LDO pass-device sizing (square-law first-order)
# Used to estimate required W/L from dropout and load current.
S_pass = 2 * Iload_LDO / (k_p * (LDO_DO ** 2))
W_pass = L * S_pass

# (15) Feedback network (simple divider)
Rf2 = 100e3
Rf1 = (Vout_LDO / V_Ref - 1) * Rf2

# (16) Controller DC gain estimate (linear -> dB)
Av_lin = Av1 * Av2
Av_cal = 20 * np.log10(abs(Av_lin))

# (17) Poles/zeros (kept as first-order, consistent with your structure)
P1 = -gm1 / (2 * np.pi * (10 ** (Av_cal / 20.0)) * Cc)  # Av_cal is dB; convert back to linear magnitude
P2 = -gm6 / (2 * np.pi * Cl)
P3 = -gm3 / (2 * 0.667 * W3 * L * C_ox)

P1_MHz = P1 / 1e6
P2_MHz = P2 / 1e6
P3_MHz = P3 / 1e6


# ======================================================================
# Summary prints
# ======================================================================
print("\nNOTE: M1–M8 refer to the LDO error amplifier devices; W_pass is the LDO pass transistor.\n")

print("(a) Component values:")
print(f"Cc = {Cc*1e12:.3f} pF")
print(f"Rc = {Rc/1e3:.3f} kOhm")
print(f"Ibias = {Ibias/1e-6:.3f} uA")
print(f"f_u = {omega1:.3f} rad/s\n")

print("(b) MOSFET sizing:")
print("--------------------------------------------------")
print("#\t W [um]\t\t L [um]\t\t S [um/um]")
print("--------------------------------------------------")
L_um = L * 1e6
W_values_um = [W1, W2, W3, W4, W5, W6, W7, W8, W_pass]
S_values = [S1, S2, S3, S4, S5, S6, S7, S8, S_pass]
for i, (W_m, S) in enumerate(zip(W_values_um, S_values), start=1):
    print(f"M{i}\t {W_m*1e6:.3f}\t\t {L_um:.3f}\t\t {S:.3f}")
print("--------------------------------------------------\n")

print("(c) Drain currents:")
I_values = [I1, I2, I3, I4, I5, I6, I7, I8]
for i, I in enumerate(I_values, start=1):
    print(f"I{i}\t {I/1e-6:.3f} uA")
print()

print(f"(d) Static power (controller): P = {P/1e-6:.3f} uW\n")
print(f"(e) Controller open-loop gain (approx): Av = {Av_cal:.3f} dB\n")
print("(f) Approx poles:")
print(f"P1 = {P1_MHz:.3f} MHz")
print(f"P2 = {P2_MHz:.3f} MHz")
print(f"P3 = {P3_MHz:.3f} MHz\n")


# ======================================================================
# LDO loop transfer function + frequency response
#   - Builds symbolic equations and solves for vfb/vs
#   - Converts to numeric TF and plots Bode / pole-zero map
# ======================================================================

s, v1, v2, vout, vfb, vs = sp.symbols("s v1 v2 vout vfb vs")
R1_sym, R2_sym, rop_sym, Resr_sym, Rf1_sym, Rf2_sym = sp.symbols("R1 R2 rop Resr Rf1 Rf2")
gm1_sym, gm2_sym, gmp_sym = sp.symbols("gm1 gm2 gmp")
C1_sym, C2_sym, Cgd_sym, Cout_sym, Cc_sym, Rc_sym = sp.symbols("C1 C2 Cgd Cout Cc Rc")

# Error amplifier + compensation
eq1 = sp.Eq(-gm1_sym * vs + v1 / R1_sym + v1 * s * C1_sym + (v1 - v2) * s * Cc_sym / (1 + s * Cc_sym * Rc_sym), 0)
eq2 = sp.Eq(gm2_sym * v1 + v2 / R2_sym + (v2 - v1) * s * Cc_sym / (1 + s * Cc_sym * Rc_sym) + v2 * s * C2_sym + (v2 - vout) * s * Cgd_sym, 0)

# Pass device + output network
eq3 = sp.Eq(gmp_sym * v2 + vout / rop_sym + vout * s * Cout_sym / (1 + s * Cout_sym * Resr_sym), 0)

# Feedback divider
eq4 = sp.Eq(vfb - (vout * Rf2_sym) / (Rf1_sym + Rf2_sym), 0)

solution = sp.solve([eq1, eq2, eq3, eq4], (v1, v2, vout, vfb), dict=True)[0]
vfb_vs = sp.simplify(solution[vfb] / vs)

n, d = sp.fraction(vfb_vs)

# Substitute numeric parameters into symbolic TF
params = {
    gm1_sym: gm1,
    gm2_sym: gm2,
    gmp_sym: gm6,          # using gm6 as an effective pass-transconductance placeholder (consistent with your script)
    R1_sym: R1,
    R2_sym: R2,
    rop_sym: R2,           # placeholder; for better realism, model pass-device ro separately
    Resr_sym: 0.18,        # example ESR [ohm]
    Rf1_sym: Rf1,
    Rf2_sym: Rf2,
    C1_sym: C1,
    C2_sym: C2,
    Cgd_sym: 550e-15,      # placeholder Cgd
    Cout_sym: C_out_LDO,
    Cc_sym: Cc,
    Rc_sym: Rc,
    vs: 1,
}

n_sub = sp.simplify(n.subs(params))
d_sub = sp.simplify(d.subs(params))

# Convert to polynomial coefficients
n_poly = sp.Poly(n_sub, s)
d_poly = sp.Poly(d_sub, s)

n_num = [float(coeff) for coeff in n_poly.all_coeffs()]
d_num = [float(coeff) for coeff in d_poly.all_coeffs()]

H = TransferFunction(n_num, d_num)

# Bode plot
mag, phase, omega = bode(H, np.logspace(0, 15, 1000), Plot=False)

fig, (mag_ax, phase_ax) = plt.subplots(2, 1)
mag_ax.semilogx(omega, 20 * np.log10(mag))
phase_ax.semilogx(omega, phase * (180 / np.pi))

mag_ax.set_ylabel("Magnitude (dB)")
phase_ax.set_ylabel("Phase (deg)")
phase_ax.set_xlabel("Frequency (rad/s)")
mag_ax.grid(True, which="both", axis="both", linestyle="--", linewidth=0.5)
phase_ax.grid(True, which="both", axis="both", linestyle="--", linewidth=0.5)

plt.show()

# Pole-Zero plot
plt.figure()
pzmap(H, Plot=True)
plt.title("Pole Zero Map")
plt.show()

# Margins
gain_margin, phase_margin, gain_cross_freq, phase_cross_freq = margin(H)
print(f"Phase Margin: {phase_margin:.2f} degrees at frequency {phase_cross_freq:.3e} rad/s")

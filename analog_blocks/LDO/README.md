# Low Dropout Regulator (LDO) Design - 45nm CMOS Technology

Complete analog design and layout of a Low Dropout Regulator implemented in 45nm CMOS technology, providing 1.0V regulated output from 1.2V supply with 50mA load capability.

## 📋 Overview

This LDO regulator demonstrates professional analog IC design methodology from specification to verified layout:

- ✅ Two-stage operational amplifier (error amplifier)
- ✅ PMOS pass transistor (4 fingers, m=25)
- ✅ Precision resistive feedback divider with matching
- ✅ Metal stacking up to M6 for robust power routing
- ✅ Complete layout with DRC/LVS verification

## ⚡ Quick Specifications

| Parameter | Value |
|-----------|-------|
| **Input Voltage** | 1.2V |
| **Output Voltage** | 1.0V ± 2% |
| **Load Current** | 50mA (max) |
| **Dropout Voltage** | 200mV |
| **Quiescent Current** | ~1.5mA |
| **Technology** | 45nm CMOS |
| **Efficiency** | ~81% @ full load |

## 🏗️ Architecture
```
VDD (1.2V) ────┬─────────────────────┬───→ VOUT (1.0V, 50mA)
               │                     │
         ┌─────┴─────┐          ┌────┴────┐
         │ Two-Stage │          │  PMOS   │
         │  Op-Amp   │◄──VFB    │  Pass   │
         │  (Error)  │          │   FET   │
         └─────┬─────┘          └────┬────┘
               │                     │
          Vref=0.333V              VOUT
                                     │
                                ┌────┴────┐
                                │R1 1.3kΩ │
                                ├────┬────┤ VFB=0.333V
                                │R2 650Ω │
                                └────┴────┘
                                     │
                                    VSS
```

**Regulation Principle:**
- Feedback: VFB = VOUT × R2/(R1+R2) = 1.0V × 0.333 = 0.333V
- Error amplifier compares VFB to Vref (0.333V)
- Output controls pass transistor gate to maintain VOUT = 1.0V

## 🔧 Key Design Features

### 1. Two-Stage Error Amplifier
- Miller-compensated architecture
- DC gain > 60dB
- Unity-gain bandwidth > 1MHz
- Phase margin > 60° for stability
- Designed for 1.2V low-voltage operation

### 2. Pass Transistor (PMOS)
```
Configuration:
  - Device: 45nm Standard-VT PMOS
  - Fingers: 4
  - Multiplier: m=25
  - Total devices: 100 (4×25)
  - Supports 50mA with 200mV dropout


### 3. Feedback Resistor Divider
```
R1: 1.3kΩ (2 segments of 650Ω each)
  - Width: 1.5µm
  - Length per segment: 1.5µm
  - Sheet resistivity: 650Ω/□
  
R2: 650Ω (1 segment)
  - Width: 1.5µm
  - Length: 1.5µm
  - Sheet resistivity: 650Ω/□

Matching features:
  - Dummy resistor guards (top/bottom)
  - Same width and orientation
  - Symmetric metal routing
  - Common-centroid principles
```

### 4. Metal Stack (M1 to M6)
- **M6**: VDD power rail (1µm wide, top metal)
- **M5**: VOUT power distribution (1µm wide)
- **M4**: VSS ground plane (1µm wide)
- **M3**: Intermediate signal routing
- **M2**: Feedback traces (VFB, Vref)
- **M1**: Device-level connections

## 📐 Layout Highlights

- ✅ Multi-finger pass transistor for uniform current distribution
- ✅ Dummy resistor guards for edge protection
- ✅ Guard rings for latch-up prevention
- ✅ Wide power rails to minimize IR drop
- ✅ Via arrays (4×4) for high-current paths
- ✅ Symmetric routing for matched devices
- ✅ Metal density fills for CMP compliance



## 📊 Performance Summary

╔════════════════════════╦═══════════╦═════════════╗
║ Parameter              ║ Value     ║ Spec        ║
╠════════════════════════╬═══════════╬═════════════╣
║ Input Voltage          ║ 1.2V      ║ Fixed       ║
║ Output Voltage         ║ 1.0V      ║ 1.0V ± 2%   ║
║ Load Current           ║ 50mA      ║ 50mA max    ║
║ Dropout Voltage        ║ 200mV     ║ < 250mV     ║
║ ║ Feedback Ratio       ║ 0.333     ║ -         ║
╚════════════════════════╩═══════════╩═════════════╝


## 📚 Documentation

For detailed information, see:
- **[Design Calculations](docs/design_calculations.md)** - Hand calculations and derivations
- **[Specifications](docs/specifications.md)** - Complete electrical specs
- **[Layout Guidelines](docs/layout_guidelines.md)** - Layout methodology
- **[Metal Stack Guide](docs/metal_stack_guide.md)** - M1-M6 routing strategy

## 🎓 Design Methodology

1. **Specification** - Define requirements (VDD, VOUT, IL)
2. **Architecture** - Select topology (error amp + pass FET)
3. **Sizing** - Calculate device dimensions
4. **Schematic** - Capture complete circuit
5. **Simulation** - Verify performance
6. **Layout** - Physical implementation
7. **Verification** - DRC, LVS checks
8. **Post-layout** - Extract and re-simulate


## 👤 Author

**Akhil Ambati**
- GitHub: [@AkhilAmbati2](https://github.com/AkhilAmbati2)

## 📝 License

## Notes
- All schematics and layouts are **sanitized**
- No foundry PDK files, device models, or proprietary data are included
- Images are provided for **educational and portfolio purposes only**
- The focus is on **design methodology**, not process-specific optimization


**Status:** ✅ Design Complete | ✅ Layout Complete | ✅ Verified

**Last Updated:** February 2026

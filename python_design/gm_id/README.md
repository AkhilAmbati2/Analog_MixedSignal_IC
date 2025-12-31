### gm/ID-Based Differential Pair Sizing

**Script:** `gmid_nmos_diffpair_sizing.py`

This script implements a full gm/ID-based sizing flow for an NMOS
Input differential pair using multi-dimensional technology lookup tables.

Key features:
- 4-D device data parsing (L, VGS, VDS, parameter)
- gm/ID and gm/gds surface interpolation
- Constraint-driven channel-length selection
- Width calculation from current density (JDS)
- Parasitic-aware iterative sizing loop
- Supports gain, GBW, and load-cap constraints

This code represents the core gm/ID design methodology used throughout
the analog blocks in this repository.

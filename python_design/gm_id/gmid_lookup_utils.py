"""
--------------------------------------------------------------------
File: gmid_lookup_utils.py

Purpose:
    Unified gm/ID lookup + interpolation utilities for analog sizing.

What this module provides:
    - Robust loading of device characterization tables (whitespace-separated .dat)
    - Derived metrics: gm/ID, gds/ID
    - 1-D interpolation of any column versus gm/ID (or other ratio columns)
    - Convenience wrappers for common lookups:
        - gds/ID vs gm/ID
        - Cgg vs gm/ID
        - generic: value vs gm/ID

Assumptions:
    Input file format is whitespace-separated numeric columns. Typical columns:
        vgs id gm gds region vdsat cgg
    Some datasets may omit cgg; the loader supports both.

Notes for GitHub:
    - This file contains no PDK content.
    - It only processes already-exported characterization data.
    - Keep your .dat files out of the public repo (or sanitize them).

Author:
    Akhil Ambati
--------------------------------------------------------------------
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Union

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d


Number = Union[int, float, np.floating]


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class DeviceTableSchema:
    """
    Schema definition for device characterization tables.

    Use this if your column order differs across datasets.
    """
    columns: Sequence[str]


# Default schema variants you can use
SCHEMA_WITH_CGG = DeviceTableSchema(
    columns=("vgs", "id", "gm", "gds", "region", "vdsat", "cgg")
)

SCHEMA_NO_CGG = DeviceTableSchema(
    columns=("vgs", "id", "gm", "gds", "region", "vdsat")
)


# ---------------------------------------------------------------------
# Core loading and derived-metric computation
# ---------------------------------------------------------------------
def load_device_table(
    filepath: str,
    schema: Optional[DeviceTableSchema] = None,
) -> pd.DataFrame:
    """
    Load a whitespace-separated device table into a clean numeric DataFrame.

    Parameters
    ----------
    filepath:
        Path to the device data file (e.g., 'nmos_22nm.dat').
    schema:
        Column schema. If None, the function will infer based on column count
        (6 -> no cgg, 7 -> includes cgg).

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe with numeric columns only and NaNs removed.

    Raises
    ------
    ValueError
        If the number of columns in the file doesn't match expected schema.
    """
    df = pd.read_csv(filepath, delim_whitespace=True, header=None)

    if schema is None:
        if df.shape[1] == 7:
            schema = SCHEMA_WITH_CGG
        elif df.shape[1] == 6:
            schema = SCHEMA_NO_CGG
        else:
            raise ValueError(
                f"Cannot infer schema for '{filepath}'. "
                f"Expected 6 or 7 columns, got {df.shape[1]}."
            )

    if df.shape[1] != len(schema.columns):
        raise ValueError(
            f"Schema mismatch for '{filepath}'. "
            f"Schema expects {len(schema.columns)} cols, file has {df.shape[1]}."
        )

    df.columns = list(schema.columns)

    # Convert everything to numeric; non-numeric becomes NaN then dropped.
    df = df.apply(pd.to_numeric, errors="coerce")
    df.dropna(inplace=True)

    return df


def add_derived_gmid_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add gm/ID and gds/ID columns to a device dataframe.

    Notes
    -----
    - Uses 'gm', 'gds', 'id' columns.
    - Avoids division by zero (rows with id==0 will be removed).

    Returns
    -------
    pd.DataFrame
        A copy of the dataframe with 'gm_id' and 'gds_id' columns appended.
    """
    if not {"gm", "gds", "id"}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'gm', 'gds', and 'id' columns.")

    df2 = df.copy()
    df2 = df2[df2["id"] != 0].copy()

    df2["gm_id"] = df2["gm"] / df2["id"]
    df2["gds_id"] = df2["gds"] / df2["id"]

    return df2


# ---------------------------------------------------------------------
# Generic interpolation utilities
# ---------------------------------------------------------------------
def interpolate_column_vs_ratio(
    df: pd.DataFrame,
    ratio_col: str,
    value_col: str,
    ratio_targets: Sequence[Number],
    *,
    kind: str = "linear",
    extrapolate: bool = True,
) -> List[float]:
    """
    Interpolate 'value_col' as a function of 'ratio_col' for target ratio values.

    Parameters
    ----------
    df:
        Device table dataframe (already numeric + cleaned).
    ratio_col:
        Column used as x-axis (e.g., 'gm_id').
    value_col:
        Column to interpolate (e.g., 'gds_id', 'cgg', 'vdsat', etc.).
    ratio_targets:
        List of ratio values at which to evaluate the interpolated function.
    kind:
        Interpolation kind for scipy.interpolate.interp1d.
    extrapolate:
        If True, allows extrapolation outside the data range.

    Returns
    -------
    List[float]
        Interpolated values for each target ratio.
    """
    if ratio_col not in df.columns:
        raise ValueError(f"Missing ratio_col '{ratio_col}' in dataframe.")
    if value_col not in df.columns:
        raise ValueError(f"Missing value_col '{value_col}' in dataframe.")

    df_sorted = df.sort_values(ratio_col)

    x = df_sorted[ratio_col].to_numpy(dtype=float)
    y = df_sorted[value_col].to_numpy(dtype=float)

    if extrapolate:
        fill_value = "extrapolate"
        bounds_error = False
    else:
        fill_value = np.nan
        bounds_error = False

    f = interp1d(x, y, kind=kind, fill_value=fill_value, bounds_error=bounds_error)
    return [float(f(float(r))) for r in ratio_targets]


# ---------------------------------------------------------------------
# Convenience wrappers (match your existing workflow)
# ---------------------------------------------------------------------
def interpolate_gds_id_vs_gm_id(
    filepath: str,
    gm_id_targets: Sequence[Number],
    *,
    schema: Optional[DeviceTableSchema] = None,
    kind: str = "linear",
) -> List[float]:
    """
    Convenience: gds/ID interpolated as a function of gm/ID.

    Equivalent to your previous interpolate_gds_id() behavior.
    """
    df = load_device_table(filepath, schema=schema)
    df = add_derived_gmid_metrics(df)
    return interpolate_column_vs_ratio(df, "gm_id", "gds_id", gm_id_targets, kind=kind)


def interpolate_cgg_vs_gm_id(
    filepath: str,
    gm_id_targets: Sequence[Number],
    *,
    schema: Optional[DeviceTableSchema] = None,
    kind: str = "linear",
) -> List[float]:
    """
    Convenience: Cgg interpolated as a function of gm/ID.

    Requires the dataset to include a 'cgg' column. If your tables use
    a different capacitance naming, adapt the schema or rename column.
    """
    df = load_device_table(filepath, schema=schema)
    df = add_derived_gmid_metrics(df)

    if "cgg" not in df.columns:
        raise ValueError(
            f"'{filepath}' does not include 'cgg'. "
            f"Use a schema with cgg or switch to another capacitance column."
        )

    return interpolate_column_vs_ratio(df, "gm_id", "cgg", gm_id_targets, kind=kind)


def load_table_with_gmid(filepath: str, *, schema: Optional[DeviceTableSchema] = None) -> pd.DataFrame:
    """
    Helper for debugging/plots: load a table and immediately add gm/ID metrics.
    """
    return add_derived_gmid_metrics(load_device_table(filepath, schema=schema))


# ---------------------------------------------------------------------
# Example usage (kept as comments so it doesn't run on import)
# ---------------------------------------------------------------------
# if __name__ == "__main__":
#     gm_id = [12.0]  # example gm/ID target
#     nmos_file = "nmos1_22nm.dat"
#     pmos_file = "pmos3_22nm.dat"
#
#     gds_id_n = interpolate_gds_id_vs_gm_id(nmos_file, gm_id)
#     cgg_n = interpolate_cgg_vs_gm_id(nmos_file, gm_id)
#     print("NMOS gds/ID:", gds_id_n, "Cgg:", cgg_n)
#
#     gds_id_p = interpolate_gds_id_vs_gm_id(pmos_file, gm_id)
#     print("PMOS gds/ID:", gds_id_p)

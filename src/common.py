"""Shared constants, data loading and numerical helpers for QXU6028 (group G15).

Physics conventions (see QXU6028_Virtual_Lab_Practical_Methods_Guide_2026-27.pdf):

* energies in eV throughout the integrations
* linear (graphene-like) density of states g(E) = c |E| with c in cm^-2 eV^-2
* N_A converts the per-atom DoS to an areal density in cm^-2
* the Fermi window is split at E_F on purpose: n integrates upward from E_F,
  p integrates downward from E_F.  The same split is used for every model.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Physical constants fixed by the data generator (Methods Guide, page 3)
# --------------------------------------------------------------------------
KB = 8.617333e-5          # eV K^-1
NA = 3.816e15             # cm^-2  (areal atom density)
QE = 1.602176634e-19      # C
E_MAX = 2.5               # eV, numerical integration cutoff
E_MIN = -2.5              # eV, lower cutoff for the L2 model integrals

# Numerical settings
N_E_L1 = 20001            # L1 integration points
N_E_L2 = 4000             # L2 integration points (matches the generator)
N_EF_GRID = 400           # L2 candidate Fermi-level grid points
EF_GRID_MIN_KT = -8.0     # candidate E_F from -8 k_BT
EF_GRID_MAX_KT = 9.0      # ... to +9 k_BT
GAP_GRID_KT = np.arange(0.50, 8.00 + 1e-9, 0.25)   # E_g/k_BT candidates

# Model-selection rule (Methods Guide, page 8)
GAP_RESIDUAL_RATIO = 0.85  # hard gap only if r_gap < 0.85 r_cone
GAP_MIN_KT = 1.0           # ... and E_g >= 1 k_BT

# Reproducibility seeds
BOOTSTRAP_SEED = 20261124
NOISE_SEED = 20261124
N_BOOTSTRAP = 200
N_NOISE = 500

# Announced Session-3 specification (fraction of the reference conductivity)
TAU = 0.03


def fermi(E, EF, T):
    """Finite-temperature Fermi-Dirac occupation with a clipped exponent.

    Clipping to [-60, 60] avoids overflow without changing any value that is
    representable in double precision.
    """
    x = np.clip((E - EF) / (KB * T), -60.0, 60.0)
    return 1.0 / (np.exp(x) + 1.0)


def dos(E, model, c, Eg):
    """Linear DoS; optional symmetric hard gap of width Eg centred on E=0."""
    if model == "cone":
        return c * np.abs(E)
    D = Eg / 2.0
    return np.where(np.abs(E) > D, c * (np.abs(E) - D), 0.0)


def carrier_np(EF, T, model, c, Eg, E=None):
    """Electron-like (n) and hole-like (p) Fermi-window populations in cm^-2."""
    if E is None:
        E = np.linspace(E_MIN, E_MAX, N_E_L2)
    f = fermi(E, EF, T)
    g = dos(E, model, c, Eg)
    n = NA * np.trapezoid(np.where(E >= EF, g * f, 0.0), E)
    p = NA * np.trapezoid(np.where(E <= EF, g * (1.0 - f), 0.0), E)
    return n, p


def hall_and_sheet(n, p):
    """Two-channel Hall coefficient and sheet resistance (Methods Guide, p.6).

        R_H = (p - n) / (e (p + n)^2)      R_s = 1 / (e mu (p + n))

    With e = mu = 1 the constants cancel because each channel is normalised by
    its own maximum, so only the ratio matters.  The signs of R_H are kept: a
    positive R_H means hole-dominated transport (E_F below the Dirac point).
    """
    R_H = (p - n) / np.square(p + n)
    R_s = 1.0 / (p + n)
    return R_H, R_s


def gradient_matrix(npix=10):
    """First-difference operator for a npix x npix map (180 x 100 for 10x10)."""
    rows = []
    N = npix * npix
    for i in range(npix):
        for j in range(npix):
            k = i * npix + j
            if j < npix - 1:                 # horizontal neighbour
                r = np.zeros(N)
                r[k] = -1.0
                r[k + 1] = 1.0
                rows.append(r)
            if i < npix - 1:                 # vertical neighbour
                r = np.zeros(N)
                r[k] = -1.0
                r[k + npix] = 1.0
                rows.append(r)
    return np.asarray(rows)


def load_dataset(data_dir):
    """Load one group dataset without modifying any supplied file."""
    data_dir = Path(data_dir)
    ds = {
        "dir": data_dir,
        "l1_params": json.loads((data_dir / "L1_params.json").read_text(encoding="utf-8")),
        "l1_data": pd.read_csv(data_dir / "L1_data.csv"),
        "l2_data": pd.read_csv(data_dir / "L2_data.csv"),
        "l2_meta": json.loads((data_dir / "L2_meta.json").read_text(encoding="utf-8")),
        "l3_meta": json.loads((data_dir / "L3_meta.json").read_text(encoding="utf-8")),
        "A": np.load(data_dir / "L3_A.npy"),
        "d": np.loadtxt(data_dir / "L3_d.csv", delimiter=","),
    }
    # Shape / consistency checks from the Methods Guide, page 2 and page 10
    assert ds["A"].shape == (128, 100), ds["A"].shape
    assert ds["d"].shape == (3, 128), ds["d"].shape
    assert np.max(np.abs(ds["A"].sum(axis=1))) < 1e-11, "rows of A must sum to ~0"
    return ds


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path

"""L1 - forward carrier counting and the mobility correction.

Research question: the datasheet used the textbook band-edge carrier count.
By how much is the true sensor sensitivity mis-stated at the operating point?

Physics
-------
Both counts use the same linear DoS and the same finite-temperature Fermi
function.  Only the lower integration limit changes:

    n_band(E_F)  = N_A * int_0^{E_max}   c E f(E, E_F) dE
    n_Fermi(E_F) = N_A * int_{E_F}^{E_max} c E f(E, E_F) dE

so that n_band >= n_Fermi for E_F >= 0 and the two agree exactly at neutrality.
At fixed sheet resistivity rho the extracted mobility is mu = 1/(e n rho),
therefore mu_F = (n_band/n_F) * mu_band = C * mu_band: the correction factor
propagates unchanged into the mobility.
"""

from __future__ import annotations

import numpy as np

from . import common as C


def n_band(EF, T, c, n_points=C.N_E_L1):
    E = np.linspace(0.0, C.E_MAX, n_points)
    return C.NA * np.trapezoid(c * E * C.fermi(E, EF, T), E)


def n_fermi(EF, T, c, n_points=C.N_E_L1):
    E = np.linspace(EF, C.E_MAX, n_points)
    return C.NA * np.trapezoid(c * E * C.fermi(E, EF, T), E)


def n_fermi_closed(EF, T, c):
    """Closed form of the Fermi-referenced integral for the linear DoS.

    int_{E_F}^{inf} c E f dE  ->  c kT (E_F ln2 + (pi^2/12) kT)
    (Sommerfeld-type expansion for a linear band; exact to O((kT/E_F)^2)).
    """
    kT = C.KB * T
    return C.NA * c * kT * (EF * np.log(2.0) + (np.pi ** 2 / 12.0) * kT)


def _crossing(EFs, ratio, level):
    """Linear interpolation of the E_F where ratio (monotone) reaches level."""
    d = ratio - level
    for i in range(len(d) - 1):
        if d[i] == 0.0:
            return float(EFs[i])
        if d[i] * d[i + 1] < 0.0:
            return float(EFs[i] - d[i] * (EFs[i + 1] - EFs[i]) / (d[i + 1] - d[i]))
    return float("nan")


def run(ds):
    p = ds["l1_params"]
    c, T, rho, EF_op = p["c"], p["T"], p["rho_ohm_sq"], p["EF_op_eV"]
    df = ds["l1_data"]

    EFs = df["EF_eV"].to_numpy(float)
    n_band_supplied = df["n_band_cm2"].to_numpy(float)

    # Recompute the band-edge column as an independent check on the generator
    n_band_recomputed = np.array([n_band(e, T, c) for e in EFs])
    max_rel_dev = float(np.max(np.abs(n_band_recomputed / n_band_supplied - 1.0)))

    # C(E_F) uses the SUPPLIED band-edge column (Methods Guide, page 4)
    n_F_sweep = np.array([n_fermi(e, T, c) for e in EFs])
    ratio = n_band_supplied / n_F_sweep

    # Reference gates required by the Methods Guide, page 5
    gates = [(0.0, 1.00), (0.073, 2.00), (0.10, 2.60), (0.20, 5.10)]
    gate_rows = []
    for ef, target in gates:
        r = n_band(ef, T, c) / n_fermi(ef, T, c)
        gate_rows.append({"EF_eV": ef, "ratio": float(r), "target": target,
                          "rel_dev_from_target": float(abs(r / target - 1.0))})

    # Closed form vs numerical check (Methods Guide asks to compare if both used)
    closed_rel = float(np.max(np.abs(n_fermi_closed(EFs, T, c) / n_F_sweep - 1.0)))

    # Exact operating point: never the nearest CSV row
    nb_op = n_band(EF_op, T, c)
    nf_op = n_fermi(EF_op, T, c)
    C_op = nb_op / nf_op
    mu_corr = 1.0 / (C.QE * nf_op * rho)
    mu_band = 1.0 / (C.QE * nb_op * rho)

    # Dense sweep for the C=2 and C=4 crossings and for the figure
    EF_dense = np.linspace(0.0, EFs.max(), 2001)
    ratio_dense = np.array([n_band(e, T, c) / n_fermi(e, T, c) for e in EF_dense])
    EF_C2 = _crossing(EF_dense, ratio_dense, 2.0)
    EF_C4 = _crossing(EF_dense, ratio_dense, 4.0)

    result = {
        "correction_factor": float(C_op),
        "n_fermi_op_cm2": float(nf_op),
        "mobility_corrected_cm2_Vs": float(mu_corr),
    }

    diagnostics = {
        "EF_op_eV": float(EF_op),
        "n_band_op_cm2": float(nb_op),
        "mobility_band_edge_cm2_Vs": float(mu_band),
        "rho_ohm_sq": float(rho),
        "T_K": float(T),
        "dos_slope_c": float(c),
        "gates": gate_rows,
        "max_rel_dev_recomputed_vs_supplied_n_band": max_rel_dev,
        "closed_form_max_rel_dev_vs_numerical": closed_rel,
        "EF_at_C_equals_2_eV": EF_C2,
        "EF_at_C_equals_4_eV": EF_C4,
        "ratio_at_operating_point": float(C_op),
        "mobility_ratio_corrected_over_band_edge": float(mu_corr / mu_band),
        "sweep": {"EF_eV": EFs.tolist(), "C": ratio.tolist()},
        "dense": {"EF_eV": EF_dense.tolist(), "C": ratio_dense.tolist()},
        "eps_sweep": {
            "EF_eV": EFs.tolist(),
            "n_band": n_band_supplied.tolist(),
            "n_F": n_F_sweep.tolist(),
        },
    }

    # Gate assertions: fail loudly rather than report a wrong method
    assert abs(gate_rows[0]["ratio"] - 1.0) < 1e-3, "E_F = 0 must give ratio 1.00"
    assert abs(gate_rows[2]["ratio"] - 2.60) < 0.05, "ratio at 0.10 eV must be ~2.60"
    assert C_op > 1.0, "correction factor below 1 at positive doping: integration limits wrong"
    assert closed_rel < 1e-6, "closed form and numerical Fermi counts disagree"

    return result, diagnostics

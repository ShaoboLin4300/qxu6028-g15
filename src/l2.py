"""L2 - zero-dimensional inverse problem: DoS class, gap and E_F trajectory.

Method (Methods Guide, pages 6-9)
--------------------------------
1. group the three repeats by measurement_index, mean = central estimate,
   standard deviation = uncertainty source for the bootstrap
2. normalise R_H and R_xx SEPARATELY by their own maxima (never together)
3. build the model library: ideal cone plus a symmetric hard-gap "V" model
   with E_g/k_BT = 0.50 ... 8.00 in steps of 0.25, evaluated on 400 candidate
   Fermi levels from -8 k_BT to +9 k_BT
4. assign a Fermi level to each measured pair by the nearest point on each
   normalised model curve (nearest-point fitting, not same-index comparison)
5. select the hard gap only when r_gap < 0.85 r_cone AND E_g >= 1 k_BT
6. 200 bootstrap replicates (one of the three repeats drawn at random per
   index) give the gap interval, the E_F band and the model-selection fraction
"""

from __future__ import annotations

import numpy as np

from . import common as C


def build_library(T, c):
    """Pre-computed normalised model curves, reusable during bootstrapping."""
    kT = C.KB * T
    EF_grid = np.linspace(C.EF_GRID_MIN_KT * kT, C.EF_GRID_MAX_KT * kT, C.N_EF_GRID)
    E = np.linspace(C.E_MIN, C.E_MAX, C.N_E_L2)

    # f(E_j, EF_i) and the split masks depend on EF only, so build them once
    F = C.fermi(E[None, :], EF_grid[:, None], T)
    upper = (E[None, :] >= EF_grid[:, None])      # E >= E_F  -> electron-like
    lower = ~upper                                 # E <= E_F  -> hole-like

    models = [{"model": "cone", "Eg_kT": 0.0, "Eg_eV": 0.0}]
    for g in C.GAP_GRID_KT:
        models.append({"model": "hard_gap", "Eg_kT": float(g), "Eg_eV": float(g * kT)})

    for m in models:
        g = C.dos(E, m["model"], c, m["Eg_eV"])
        n = C.NA * np.trapezoid(np.where(upper, g[None, :] * F, 0.0), E, axis=1)
        p = C.NA * np.trapezoid(np.where(lower, g[None, :] * (1.0 - F), 0.0), E, axis=1)
        RH, Rs = C.hall_and_sheet(n, p)
        m["RH_norm"] = RH / np.max(np.abs(RH))
        m["Rs_norm"] = Rs / np.max(np.abs(Rs))
        m["xy"] = np.column_stack([m["RH_norm"], m["Rs_norm"]])

    return {"EF_grid": EF_grid, "kT": kT, "models": models}


def _fit(data_xy, models):
    """Nearest-point residual (rms) and assigned E_F index for every model."""
    out = []
    for m in models:
        d2 = ((data_xy[:, None, :] - m["xy"][None, :, :]) ** 2).sum(axis=2)
        j = np.argmin(d2, axis=1)
        rms = float(np.sqrt(np.mean(d2[np.arange(len(j)), j])))
        out.append({"rms": rms, "j": j})
    return out


def _select(fits, models):
    """15% improvement rule: hard gap only if materially better and >= 1 kT."""
    r_cone = fits[0]["rms"]
    gap_fits = [(f["rms"], k) for k, f in enumerate(fits) if k > 0]
    r_gap, k_gap = min(gap_fits, key=lambda t: t[0])
    if r_gap < C.GAP_RESIDUAL_RATIO * r_cone and models[k_gap]["Eg_kT"] >= C.GAP_MIN_KT:
        return {"model": "hard_gap", "Eg_kT": models[k_gap]["Eg_kT"], "k": k_gap,
                "rms": r_gap, "fit": fits[k_gap], "r_cone": r_cone, "r_gap": r_gap}
    return {"model": "cone", "Eg_kT": 0.0, "k": 0,
            "rms": r_cone, "fit": fits[0], "r_cone": r_cone, "r_gap": r_gap}


def _prep(ds):
    df = ds["l2_data"]
    idx = np.sort(df["measurement_index"].unique())
    RH = np.empty((len(idx), 3))
    RS = np.empty((len(idx), 3))
    for a, i in enumerate(idx):
        sel = df[df["measurement_index"] == i]
        RH[a, :] = sel["R_H_raw"].to_numpy(float)
        RS[a, :] = sel["R_xx_raw"].to_numpy(float)
    return idx, RH, RS


def _normalise(rh, rs):
    """Independent normalisation; the sign of R_H is preserved."""
    return np.column_stack([rh / np.max(np.abs(rh)), rs / np.max(rs)])


def run(ds):
    p = ds["l1_params"]
    T, c = ds["l2_meta"]["T_K"], p["c"]
    idx, RH, RS = _prep(ds)

    rh_mean = RH.mean(axis=1)
    rs_mean = RS.mean(axis=1)
    rh_std = RH.std(axis=1, ddof=1)
    rs_std = RS.std(axis=1, ddof=1)

    lib = build_library(T, c)
    EF_grid, models = lib["EF_grid"], lib["models"]

    data_xy = _normalise(rh_mean, rs_mean)
    fits = _fit(data_xy, models)
    sel = _select(fits, models)

    EF_traj = EF_grid[sel["fit"]["j"]]

    # ---- bootstrap ------------------------------------------------------
    rng = np.random.default_rng(C.BOOTSTRAP_SEED)
    boot_Eg, boot_EF, boot_model = [], [], []
    for _ in range(C.N_BOOTSTRAP):
        pick = rng.integers(0, RH.shape[1], size=RH.shape[0])
        rows = np.arange(RH.shape[0])
        rh_b = RH[rows, pick]
        rs_b = RS[rows, pick]
        f_b = _fit(_normalise(rh_b, rs_b), models)
        s_b = _select(f_b, models)
        boot_Eg.append(s_b["Eg_kT"])
        boot_model.append(s_b["model"])
        boot_EF.append(EF_grid[s_b["fit"]["j"]])

    boot_Eg = np.asarray(boot_Eg)
    boot_EF = np.asarray(boot_EF)
    frac_gap = float(np.mean([m == "hard_gap" for m in boot_model]))

    eg_lo, eg_hi = np.percentile(boot_Eg, [16, 84])
    ef_lo, ef_hi = np.percentile(boot_EF, [16, 84], axis=0)

    # Sign-change index pair, used by the report to show that neutrality was
    # located before normalisation
    sign_change = np.where(np.diff(np.sign(rh_mean)) != 0)[0]

    # Physical consistency check between the two channels: a positive R_H means
    # hole-dominated transport, so the assigned E_F must cross zero at the same
    # index as the measured R_H (Methods Guide, page 6 and page 7)
    traj_sign_change = np.where(np.diff(np.sign(EF_traj)) != 0)[0]
    gate_ok = (len(sign_change) > 0 and len(traj_sign_change) > 0
               and abs(traj_sign_change[0] - sign_change[0]) <= 1)

    result = {
        "model": sel["model"],
        "Eg_kT": float(sel["Eg_kT"]),
        "Eg_uncertainty_kT": [float(eg_lo), float(eg_hi)],
        "EF_trajectory_eV": [float(v) for v in EF_traj],
    }

    diagnostics = {
        "n_indices": int(len(idx)),
        "residual_cone": float(sel["r_cone"]),
        "residual_best_hard_gap": float(sel["r_gap"]),
        "residual_ratio_gap_over_cone": float(sel["r_gap"] / sel["r_cone"]),
        "selection_threshold_ratio": C.GAP_RESIDUAL_RATIO,
        "gap_selection_fraction": frac_gap,
        "bootstrap_repeats": C.N_BOOTSTRAP,
        "bootstrap_seed": C.BOOTSTRAP_SEED,
        "Eg_kT_median_bootstrap": float(np.median(boot_Eg)),
        "EF_trajectory_uncertainty_16_84_eV": {"lower": ef_lo.tolist(), "upper": ef_hi.tolist()},
        "EF_trajectory_range_eV": [float(EF_traj.min()), float(EF_traj.max())],
        "RH_sign_change_between_indices": sign_change.tolist(),
        "RH_mean": rh_mean.tolist(),
        "RS_mean": rs_mean.tolist(),
        "RH_std": rh_std.tolist(),
        "RS_std": rs_std.tolist(),
        "measurement_index": idx.tolist(),
        "rh_norm": data_xy[:, 0].tolist(),
        "rs_norm": data_xy[:, 1].tolist(),
        "EF_grid_eV": EF_grid.tolist(),
        "selected_curve": {
            "RH_norm": models[sel["k"]]["xy"][:, 0].tolist(),
            "Rs_norm": models[sel["k"]]["xy"][:, 1].tolist(),
        },
    }

    # Length requirement from the Methods Guide, page 8
    assert len(result["EF_trajectory_eV"]) == len(idx)
    assert gate_ok, ("the assigned E_F must cross zero where R_H changes sign: "
                     f"trajectory {list(traj_sign_change)} vs data {list(sign_change)}")
    diagnostics["zero_crossing_gate"] = {
        "RH_sign_change_index_position": [int(v) for v in sign_change],
        "EF_zero_crossing_index_position": [int(v) for v in traj_sign_change],
        "consistent": bool(gate_ok),
    }
    return result, diagnostics

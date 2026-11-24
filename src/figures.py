"""Figure generation for the QXU6028 report (matplotlib, Agg backend).

A single style block keeps every panel consistent: same font sizes, hairline
axes, grid only on the value axis, no top or right spine, and one palette.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from . import common as C

# ---------------------------------------------------------------- style
BLUE = "#2f5d8a"
RED = "#b03a2e"
GREY = "#8a8a8a"
ORANGE = "#c87f0a"
GREEN = "#2e7d5b"
PALETTE = [BLUE, RED, GREEN, ORANGE]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8.5,
    "axes.titlesize": 9.0,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#2b2b2b",
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": "#dcdcdc",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "figure.dpi": 220,
    "savefig.dpi": 220,
    "savefig.facecolor": "white",
    "legend.frameon": False,
})


def _save(fig, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    return path


def _clean(ax, grid_axis="both"):
    ax.grid(True, axis=grid_axis)
    ax.set_axisbelow(True)
    return ax


# ---------------------------------------------------------------- L1
def l1_sweep(d, path):
    fig, ax = plt.subplots(1, 2, figsize=(10.4, 3.7), constrained_layout=True)

    EF = np.asarray(d["dense"]["EF_eV"])
    Cd = np.asarray(d["dense"]["C"])
    ax[0].plot(EF, Cd, color=BLUE, lw=2.0, label=r"$C=n_{\rm band}/n_F$")
    ax[0].plot(np.asarray(d["sweep"]["EF_eV"]), np.asarray(d["sweep"]["C"]), "o",
               ms=4.2, mfc="white", mec=RED, mew=1.0, label="supplied sweep rows")
    for lev, ls in ((2.0, (0, (1, 2))), (4.0, (0, (4, 2)))):
        ax[0].axhline(lev, color="#555555", ls=ls, lw=0.9)
    ax[0].axvline(d["EF_op_eV"], color=ORANGE, lw=1.1, ls="-.")
    ax[0].plot(d["EF_at_C_equals_2_eV"], 2.0, "s", ms=5, color=BLUE)
    ax[0].plot(d["EF_at_C_equals_4_eV"], 4.0, "s", ms=5, color=BLUE)
    ax[0].annotate(f"$C$=2 at {d['EF_at_C_equals_2_eV']*1e3:.1f} meV",
                   (d["EF_at_C_equals_2_eV"], 2.0), xytext=(0.112, 1.42),
                   fontsize=7.5, arrowprops=dict(arrowstyle="-", lw=0.6, color=GREY))
    ax[0].annotate(f"$C$=4 at {d['EF_at_C_equals_4_eV']*1e3:.1f} meV",
                   (d["EF_at_C_equals_4_eV"], 4.0), xytext=(0.168, 3.42),
                   fontsize=7.5, arrowprops=dict(arrowstyle="-", lw=0.6, color=GREY))
    ax[0].annotate(f"operating point\n$E_F$={d['EF_op_eV']*1e3:.1f} meV, "
                   f"$C$={d['ratio_at_operating_point']:.3f}",
                   (d["EF_op_eV"], d["ratio_at_operating_point"]),
                   xytext=(0.126, 6.0), fontsize=7.5, color=ORANGE,
                   arrowprops=dict(arrowstyle="->", lw=0.8, color=ORANGE))
    ax[0].set_ylim(0.85, 7.6)
    ax[0].set_xlabel(r"$E_F$ (eV)")
    ax[0].set_ylabel(r"correction factor $C$")
    ax[0].set_title("(a) counting-convention correction")
    ax[0].legend(loc="upper left", handlelength=1.6)
    _clean(ax[0])

    eps = d.get("eps_sweep", {})
    if eps:
        ax[1].semilogy(eps["EF_eV"], eps["n_band"], "o-", ms=3, lw=1.3,
                       color=RED, label=r"$n_{\rm band}$, lower limit $E=0$")
        ax[1].semilogy(eps["EF_eV"], eps["n_F"], "s-", ms=3, lw=1.3,
                       color=BLUE, label=r"$n_F$, lower limit $E=E_F$")
        ax[1].axvline(d["EF_op_eV"], color=ORANGE, lw=1.1, ls="-.")
        ax[1].set_xlabel(r"$E_F$ (eV)")
        ax[1].set_ylabel(r"carrier density (cm$^{-2}$)")
        ax[1].set_title("(b) the two finite-temperature counts")
        ax[1].legend(loc="lower right", handlelength=1.6)
        _clean(ax[1], "both")

    fig.suptitle("L1 forward carrier counting, group G15", fontsize=10.5)
    return _save(fig, path)


# ---------------------------------------------------------------- L2
def l2_raw(d, path):
    idx = np.asarray(d["measurement_index"])
    RH = np.asarray(d["RH_repeats"])
    RS = np.asarray(d["RS_repeats"])
    fig, ax = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True,
                           constrained_layout=True)
    for a, M, lab in zip(ax, (RH, RS), (r"$R_H$  (V A$^{-1}$ T$^{-1}$)",
                                        r"$R_{xx}$  ($\Omega$/\u25a1)")):
        for r in range(M.shape[1]):
            a.plot(idx, M[:, r], "o-", ms=2.8, lw=0.9, alpha=0.85,
                   color=PALETTE[r], label=f"repeat {r+1}")
        a.set_ylabel(lab)
        _clean(a)
    ax[0].legend(loc="upper right", ncol=3, columnspacing=1.0,
                 handlelength=0.9, borderaxespad=0.2)
    for k in d.get("RH_sign_change_between_indices", []):
        for a in ax:
            a.axvspan(idx[k] - 0.4, idx[k + 1] + 0.4, color=RED, alpha=0.09, lw=0)
        ax[0].annotate("$R_H$ changes sign between these two indices\n"
                       "(neutrality is bracketed before normalisation)",
                       xy=(0.30, 0.96), xycoords="axes fraction", va="top",
                       fontsize=7.2, color=RED)
    ax[1].set_xlabel("measurement index (original acquisition order)")
    ax[0].set_title("L2 raw data: three repeats of the signed Hall and sheet channels")
    return _save(fig, path)


def l2_model_fit(d, path):
    fig, ax = plt.subplots(figsize=(5.0, 3.9))
    rh = np.asarray(d["rh_norm"])
    rs = np.asarray(d["rs_norm"])
    cv = np.asarray(d["selected_curve"]["RH_norm"])
    cs = np.asarray(d["selected_curve"]["Rs_norm"])
    ax.plot(cv, cs, color="#9a9a9a", lw=1.5, zorder=1,
            label=f"selected model (cone, $E_g$={d['Eg_kT']:.2f} $k_BT$)")
    sc = ax.scatter(rh, rs, c=np.arange(len(rh)), cmap="viridis", s=24,
                    zorder=3, edgecolor="white", linewidth=0.4)
    cb = fig.colorbar(sc, ax=ax, pad=0.02, fraction=0.05)
    cb.set_label("measurement index", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    ax.axhline(0, color="#cccccc", lw=0.7)
    ax.axvline(0, color="#cccccc", lw=0.7)
    ax.set_xlabel(r"$\tilde R_H = R_H/\max|R_H|$")
    ax.set_ylabel(r"$\tilde R_s = R_s/\max R_s$")
    ax.set_title("L2 nearest-point fit in separately normalised space")
    ax.legend(loc="lower left", handlelength=1.4)
    _clean(ax)
    return _save(fig, path)


def l2_channels(d, path):
    EFg = np.asarray(d["EF_grid_eV"]) * 1e3
    cv = np.asarray(d["selected_curve"]["RH_norm"])
    cs = np.asarray(d["selected_curve"]["Rs_norm"])
    ef = np.asarray(d["EF_assigned_per_index_eV"]) * 1e3
    rh = np.asarray(d["rh_norm"])
    rs = np.asarray(d["rs_norm"])

    fig, ax = plt.subplots(1, 3, figsize=(11.0, 3.3), constrained_layout=True)

    ax[0].plot(EFg, cv, color="#9a9a9a", lw=1.4, label="cone model")
    ax[0].plot(ef, rh, "o", ms=3.6, color=BLUE, label="measured (mean of 3)")
    ax[0].axhline(0, color="#cccccc", lw=0.7)
    ax[0].axvline(0, color="#cccccc", lw=0.7)
    ax[0].set_xlabel(r"assigned $E_F$ (meV)")
    ax[0].set_ylabel(r"$\tilde R_H$")
    ax[0].set_title(r"(a) signed $\tilde R_H(E_F)$")
    ax[0].legend(loc="lower right", handlelength=1.2)
    _clean(ax[0])

    ax[1].plot(EFg, cs, color="#9a9a9a", lw=1.4, label="cone model")
    ax[1].plot(ef, rs, "o", ms=3.6, color=RED, label="measured (mean of 3)")
    ax[1].set_xlabel(r"assigned $E_F$ (meV)")
    ax[1].set_ylabel(r"$\tilde R_s$")
    ax[1].set_title(r"(b) $\tilde R_s(E_F)$, peaked at neutrality")
    ax[1].legend(loc="upper right", handlelength=1.2)
    _clean(ax[1])

    res = np.asarray(d["residual_per_index"])
    ax[2].bar(np.asarray(d["measurement_index"]), res, color=BLUE, width=0.82,
              linewidth=0)
    rms = float(np.sqrt(np.mean(res ** 2)))
    ax[2].axhline(rms, color=RED, ls=(0, (4, 2)), lw=1.0)
    ax[2].annotate(f"rms = {rms:.5f}", (0.52, 0.95), xycoords="axes fraction",
                   fontsize=7.5, color=RED, va="top")
    ax[2].set_xlabel("measurement index")
    ax[2].set_ylabel("distance to model curve")
    ax[2].set_title("(c) residual per measurement")
    _clean(ax[2], "y")

    fig.suptitle("L2 channel overlays and residuals against the selected model",
                 fontsize=10)
    return _save(fig, path)


def l2_trajectory(d, path):
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    idx = np.asarray(d["measurement_index"])
    ef = np.asarray(d["EF_trajectory_eV"])
    lo = np.asarray(d["EF_trajectory_uncertainty_16_84_eV"]["lower"])
    hi = np.asarray(d["EF_trajectory_uncertainty_16_84_eV"]["upper"])
    ax.fill_between(idx, lo * 1e3, hi * 1e3, color=BLUE, alpha=0.16, lw=0,
                    label="bootstrap 16-84 %")
    ax.plot(idx, ef * 1e3, "o-", ms=3.0, lw=1.3, color=BLUE,
            label="assigned $E_F$ (central fit)")
    ax.axhline(0, color="#bbbbbb", lw=0.8, ls=(0, (3, 2)))
    for k in d.get("RH_sign_change_between_indices", []):
        ax.axvline(idx[k] + 0.5, color=RED, lw=0.9, ls=(0, (1, 2)))
        ax.annotate("$R_H$ zero crossing", (idx[k] + 0.5, ef.min() * 1e3),
                    rotation=90, fontsize=6.8, color=RED,
                    textcoords="offset points", xytext=(2, 4), va="bottom")
    ax.set_xlabel("measurement index (original acquisition order)")
    ax.set_ylabel(r"assigned $E_F$ (meV)")
    ax.set_title(f"L2 Fermi-level trajectory, {d['n_indices']} indices")
    ax.legend(loc="lower right", handlelength=1.4)
    _clean(ax)
    return _save(fig, path)


def l2_bootstrap(d, path):
    eg = np.asarray(d["bootstrap_Eg_kT"])
    hw = np.asarray(d["EF_band_halfwidth_eV"]) * 1e3
    idx = np.asarray(d["measurement_index"])
    models = np.asarray(d["bootstrap_models"])

    fig, ax = plt.subplots(1, 3, figsize=(11.0, 3.2), constrained_layout=True)

    eg_grid = np.concatenate([[0.0], np.asarray(d["residual_by_gap_kT"])])
    rms_g = np.concatenate([[d["residual_cone"]], np.asarray(d["residual_by_gap"])])
    ax[0].plot(eg_grid, rms_g, "o-", ms=3.0, lw=1.2, color=BLUE)
    ax[0].axhline(d["residual_cone"], color="#666666", lw=0.9, ls=(0, (4, 2)))
    ax[0].axhline(C.GAP_RESIDUAL_RATIO * d["residual_cone"], color=RED, lw=1.0,
                  ls=(0, (1, 2)))
    ax[0].plot(0.0, d["residual_cone"], "o", ms=6.5, color=RED, zorder=5,
               label="selected model (cone)")
    ax[0].annotate("acceptance threshold $0.85\\,r_{\\rm cone}$",
                   (6.0, C.GAP_RESIDUAL_RATIO * d["residual_cone"]),
                   textcoords="offset points", xytext=(0, 7), ha="center",
                   fontsize=7, color=RED)
    ax[0].legend(loc="center right", handlelength=1.0)
    ax[0].set_xlabel(r"$E_g/k_BT$")
    ax[0].set_ylabel(r"rms residual")
    ax[0].set_title("(a) residual against gap size")
    ax[0].set_ylim(0, max(rms_g) * 1.15)
    _clean(ax[0])

    ax[1].plot(idx, hw, "o-", ms=3.0, lw=1.1, color=GREEN)
    ax[1].axhline(np.median(hw), color=RED, lw=0.9, ls=(0, (4, 2)))
    ax[1].annotate(f"median {np.median(hw):.2f} meV", (0.5, 0.92),
                   xycoords="axes fraction", fontsize=7.5, color=RED, ha="center")
    ax[1].set_xlabel("measurement index")
    ax[1].set_ylabel(r"16-84 % half-width (meV)")
    ax[1].set_title(r"(b) per-index $E_F$ band width")
    _clean(ax[1])

    counts = [int((models == 0).sum()), int((models == 1).sum())]
    bars = ax[2].bar(["cone", "hard gap"], counts, color=[BLUE, ORANGE], width=0.55,
                     linewidth=0)
    for b, c in zip(bars, counts):
        ax[2].annotate(f"{c/len(models)*100:.0f} %",
                       (b.get_x() + b.get_width() / 2, c), ha="center",
                       va="bottom", fontsize=8)
    ax[2].set_ylabel("replicates")
    ax[2].set_title("(c) model-selection fraction")
    ax[2].set_ylim(0, max(counts) * 1.25 + 1e-9)
    _clean(ax[2], "y")

    fig.suptitle(f"L2 bootstrap stability ({len(models)} replicates, seed {d['bootstrap_seed']})",
                 fontsize=10)
    return _save(fig, path)


# ---------------------------------------------------------------- L3
def l3_map(d, path):
    m = np.asarray(d["map_2d"])
    ml = np.asarray(d["map_localised"]).reshape(m.shape)
    fig, ax = plt.subplots(1, 2, figsize=(10.2, 4.2), constrained_layout=True)
    ext = [-3.0, 3.0, -3.0, 3.0]

    im = ax[0].imshow(m, origin="lower", extent=ext, cmap="RdBu_r",
                      vmin=-np.max(np.abs(m)), vmax=np.max(np.abs(m)),
                      interpolation="nearest")
    cb = fig.colorbar(im, ax=ax[0], pad=0.02, fraction=0.046)
    cb.set_label(r"$\hat m$ (rel. conductivity)", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    for key, mark in (("argmax_pixel", "^"), ("argmin_pixel", "v")):
        p = d[key]
        ax[0].plot(p["x"], p["y"], mark, color="k", ms=7)
        ax[0].annotate(f"{p['value']*100:+.2f}%", (p["x"], p["y"]),
                       textcoords="offset points", xytext=(-34, 3), fontsize=7)
    ax[0].set_title(f"(a) zero-mean reconstruction, max$|m|$={d['max_abs_map']*100:.2f}%")

    vmax = np.max(np.abs(ml))
    im2 = ax[1].imshow(ml, origin="lower", extent=ext, cmap="RdBu_r",
                       vmin=-vmax, vmax=vmax, interpolation="nearest")
    for f in d["features"]:
        if f["space"].startswith("tilt-removed"):
            ax[1].plot(f["x_probe_pitch"], f["y_probe_pitch"], "o", ms=10,
                       mfc="none", mec="k", mew=1.2)
            ax[1].annotate(f"{f['amplitude']*100:+.2f}%",
                           (f["x_probe_pitch"], f["y_probe_pitch"]),
                           textcoords="offset points", xytext=(7, 6), fontsize=7.5)
    ax[1].set_title(f"(b) plane removed: $|m_{{\\rm loc}}|$={d['localised_max_abs']*100:.2f}% "
                    f"(scale $\\pm${vmax*100:.2f}%)")

    for a in ax:
        a.set_xlabel("x (probe pitches)")
        a.set_ylabel("y (probe pitches)")
        a.grid(False)
        a.set_xticks([-3, -1.5, 0, 1.5, 3])
        a.set_yticks([-3, -1.5, 0, 1.5, 3])
    fig.suptitle("L3 uniformity map, G15 "
                 f"(gradient {np.hypot(*d['tilt_coefficients_per_pitch'].values())*100:.2f}%/pitch, "
                 f"$\\delta_{{95}}$={d['delta95']:.1e}, {d['decision']})", fontsize=9.5)
    return _save(fig, path)


def l3_method(d, path):
    fig, ax = plt.subplots(2, 2, figsize=(9.6, 6.2), constrained_layout=True)

    sens = d["eta_sensitivity"]
    mult = [s["eta_over_eta0"] for s in sens]
    r = [s["residual_norm"] for s in sens]
    noise = d["noise_norm"] / np.sqrt(3)
    ax[0, 0].loglog(mult, r, "o-", color=BLUE, ms=4, lw=1.2)
    ax[0, 0].axhline(noise, color=RED, ls=(0, (4, 2)), lw=1.0)
    ax[0, 0].annotate("noise level\nof the 3-repeat mean", (mult[0], noise),
                      textcoords="offset points", xytext=(4, 6), fontsize=7,
                      color=RED)
    ax[0, 0].axvline(1.0, color="#999999", lw=0.7, ls=(0, (1, 2)))
    ax[0, 0].set_xlabel(r"$\eta/\eta_0$")
    ax[0, 0].set_ylabel(r"$\|A\hat m-\bar d\|$")
    ax[0, 0].set_title("(a) misfit against regularisation")
    _clean(ax[0, 0], "both")

    sv = np.asarray(d["singular_values"])
    k = np.arange(1, len(sv) + 1)
    ax[0, 1].semilogy(k, sv, color=BLUE, lw=1.2)
    ax[0, 1].axvline(d["rank_A"], color=RED, lw=0.9, ls=(0, (4, 2)))
    ax[0, 1].annotate(f"rank {d['rank_A']} of {len(sv)}", (d["rank_A"], sv.min()),
                      textcoords="offset points", xytext=(-64, 8), fontsize=7.2,
                      color=RED)
    ax[0, 1].set_xlabel("index")
    ax[0, 1].set_ylabel(r"singular value of $A$")
    ax[0, 1].set_title("(b) spectrum of the forward matrix")
    _clean(ax[0, 1], "y")

    sig = np.asarray(d["sigma_per_channel"]) * 1e6
    ax[1, 0].plot(np.arange(len(sig)), sig, ".", ms=3.2, color=GREEN)
    ax[1, 0].axhline(np.median(sig), color=RED, lw=0.9, ls=(0, (4, 2)))
    ax[1, 0].annotate(f"median {np.median(sig):.3f}", (0.5, 0.92),
                      xycoords="axes fraction", ha="center", fontsize=7.2, color=RED)
    ax[1, 0].set_xlabel("detector channel")
    ax[1, 0].set_ylabel(r"repeat $\sigma_j$ ($\times10^{-6}$)")
    ax[1, 0].set_title("(c) channel-wise repeat noise")
    _clean(ax[1, 0])

    nm = np.asarray(d["noise_maxima"])
    ax[1, 1].hist(nm, bins=38, color=BLUE, alpha=0.85, linewidth=0)
    ax[1, 1].axvline(d["delta95"], color=RED, ls=(0, (4, 2)), lw=1.1)
    ax[1, 1].annotate(rf"$\delta_{{95}}$={d['delta95']:.1e}", (d["delta95"], 0),
                      textcoords="offset points", xytext=(5, 26), fontsize=7.5,
                      color=RED)
    ax[1, 1].set_xlabel(r"$\max|m_{\rm noise}|$")
    ax[1, 1].set_ylabel("count")
    ax[1, 1].set_title("(d) 500 noise-only reconstructions")
    _clean(ax[1, 1], "y")

    fig.suptitle("L3 regularisation, conditioning and detection limit", fontsize=10.5)
    return _save(fig, path)


def l3_resolution(d, path):
    maps = [np.asarray(mm).reshape(10, 10) for mm in d["psf_maps"]]
    tests = d["resolution_tests"]
    fig, ax = plt.subplots(2, 2, figsize=(8.4, 6.2), constrained_layout=True)
    ext = [-3, 3, -3, 3]

    for col, (mp, t) in enumerate(zip(maps, tests)):
        im = ax[0, col].imshow(mp, origin="lower", extent=ext, cmap="RdBu_r",
                               vmin=-np.max(np.abs(mp)), vmax=np.max(np.abs(mp)),
                               interpolation="nearest")
        ax[0, col].plot(t["x"], t["y"], "+", color="k", ms=9, mew=1.2)
        ax[0, col].set_title(f"({'ab'[col]}) point spread at "
                             f"({t['x']:+.1f}, {t['y']:+.1f}) pitch")
        ax[0, col].set_xlabel("x (probe pitches)")
        ax[0, col].set_ylabel("y (probe pitches)")
        ax[0, col].grid(False)
        cb = fig.colorbar(im, ax=ax[0, col], pad=0.02, fraction=0.046)
        cb.ax.tick_params(labelsize=6.5)

        ci, cj = divmod(t["pixel"], 10)
        row = mp[ci, :]
        xs = (np.arange(10) - cj) * 0.6
        ax[1, col].plot(xs, row / np.max(row), "o-", ms=3.4, lw=1.2, color=BLUE)
        ax[1, col].axhline(0.5, color=RED, ls=(0, (4, 2)), lw=1.0)
        ax[1, col].axvspan(-t["fwhm_probe_pitch"] / 2, t["fwhm_probe_pitch"] / 2,
                           color=RED, alpha=0.07, lw=0)
        ax[1, col].set_xlabel("position relative to the injected pixel (pitch)")
        ax[1, col].set_ylabel("normalised response")
        ax[1, col].set_title(f"({'cd'[col]}) cross-section, "
                             f"FWHM {t['fwhm_probe_pitch']:.2f} pitch")
        _clean(ax[1, col])

    fig.suptitle("L3 resolution: injected point response at the centre and off-centre",
                 fontsize=10.5)
    return _save(fig, path)


def l3_forward(d, path):
    dm = np.asarray(d["d_measured"]) * 1e3          # mOhm/sq
    dp = np.asarray(d["d_predicted"]) * 1e3
    rv = np.asarray(d["residual_vector"]) * 1e6     # micro-Ohm/sq
    k = 3 * np.asarray(d["sigma_per_channel"]) * 1e6
    n = np.arange(len(dm))

    fig, ax = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=True,
                           constrained_layout=True)
    ax[0].plot(n, dm, "-", color="#8a8a8a", lw=2.2, alpha=0.9,
               label=r"measured $\bar d$")
    ax[0].plot(n, dp, "--", color=BLUE, lw=1.2, label=r"reconstructed $A\hat m$")
    ax[0].set_ylabel("reading (mΩ/□)")
    ax[0].legend(loc="upper left", ncol=2, handlelength=1.8)
    ax[0].set_title("(a) forward check: measured and reconstructed readings")
    _clean(ax[0])

    ax[1].plot(n, rv, "o", ms=2.6, color=BLUE, label="residual")
    ax[1].fill_between(n, -k, k, color=RED, alpha=0.25, lw=0,
                       label=r"$\pm3\sigma_j$")
    ax[1].axhline(0, color="#999999", lw=0.7)
    ax[1].set_xlabel("detector channel")
    ax[1].set_ylabel("residual (µΩ/□)")
    ax[1].legend(loc="upper left", ncol=2, handlelength=1.4)
    ax[1].set_title("(b) residual against the repeat noise band")
    _clean(ax[1])

    fig.suptitle("L3 consistency of the reconstruction with the measured scan",
                 fontsize=10.5)
    return _save(fig, path)

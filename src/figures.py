"""Figure generation for the QXU6028 report (matplotlib, Agg backend)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from . import common as C


def _save(fig, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def l1_sweep(d, path):
    fig, ax = plt.subplots(1, 2, figsize=(10.4, 3.9), constrained_layout=True)

    EF = np.asarray(d["dense"]["EF_eV"])
    Cd = np.asarray(d["dense"]["C"])
    ax[0].plot(EF, Cd, color="#1f4e79", lw=2, label=r"$C=n_{\rm band}/n_F$")
    ax[0].plot(np.asarray(d["sweep"]["EF_eV"]), np.asarray(d["sweep"]["C"]), "o",
               ms=4, color="#c00000", label="supplied sweep rows")
    for lev, ls in ((2.0, ":"), (4.0, "--")):
        ax[0].axhline(lev, color="0.4", ls=ls, lw=1)
    ax[0].axvline(d["EF_op_eV"], color="#e69138", lw=1.2, ls="-.")
    ax[0].plot(d["EF_at_C_equals_2_eV"], 2.0, "s", color="0.2", ms=5)
    ax[0].plot(d["EF_at_C_equals_4_eV"], 4.0, "s", color="0.2", ms=5)
    ax[0].annotate(f"C=2 at {d['EF_at_C_equals_2_eV']*1e3:.1f} meV",
                   (d["EF_at_C_equals_2_eV"], 2.0), xycoords="data",
                   xytext=(0.112, 1.42), textcoords="data", fontsize=8,
                   arrowprops=dict(arrowstyle="-", lw=0.7, color="0.4"))
    ax[0].annotate(f"C=4 at {d['EF_at_C_equals_4_eV']*1e3:.1f} meV",
                   (d["EF_at_C_equals_4_eV"], 4.0), xycoords="data",
                   xytext=(0.168, 3.42), textcoords="data", fontsize=8,
                   arrowprops=dict(arrowstyle="-", lw=0.7, color="0.4"))
    ax[0].annotate(
        f"operating point\n$E_F$={d['EF_op_eV']*1e3:.1f} meV, $C$={d['ratio_at_operating_point']:.3f}",
        (d["EF_op_eV"], d["ratio_at_operating_point"]), xycoords="data",
        xytext=(0.128, 6.05), textcoords="data", fontsize=8, color="#b45f06",
        arrowprops=dict(arrowstyle="->", lw=0.9, color="#b45f06"))
    ax[0].set_ylim(0.85, 7.6)
    ax[0].set_xlabel(r"$E_F$ (eV)")
    ax[0].set_ylabel(r"correction factor $C$")
    ax[0].set_title("(a) counting-convention correction", fontsize=10)
    ax[0].legend(fontsize=8, loc="upper left")
    ax[0].grid(alpha=0.25)

    eps = d.get("eps_sweep", {})
    if eps:
        ax[1].semilogy(eps["EF_eV"], eps["n_band"], "o-", ms=3, lw=1.4,
                       color="#c00000", label=r"$n_{\rm band}$ (E=0 lower limit)")
        ax[1].semilogy(eps["EF_eV"], eps["n_F"], "s-", ms=3, lw=1.4,
                       color="#1f4e79", label=r"$n_F$ (E=E$_F$ lower limit)")
        ax[1].axvline(d["EF_op_eV"], color="#e69138", lw=1.2, ls="-.")
        ax[1].set_xlabel(r"$E_F$ (eV)")
        ax[1].set_ylabel(r"carrier density (cm$^{-2}$)")
        ax[1].set_title("(b) the two finite-temperature counts", fontsize=10)
        ax[1].legend(fontsize=8)
        ax[1].grid(alpha=0.25, which="both")

    fig.suptitle("L1 forward carrier counting, group G15", fontsize=11)
    return _save(fig, path)


def l2_raw(d, path):
    """The three raw repeats of both channels, in acquisition order."""
    idx = np.asarray(d["measurement_index"])
    RH = np.asarray(d["RH_repeats"])
    RS = np.asarray(d["RS_repeats"])
    fig, ax = plt.subplots(2, 1, figsize=(7.4, 5.4), sharex=True,
                           constrained_layout=True)
    for a, (M, lab, unit) in zip(ax, [(RH, r"$R_H$", r"$R$"),
                                      (RS, r"$R_{xx}$", r"$\Omega/\square$")]):
        for r in range(M.shape[1]):
            a.plot(idx, M[:, r], "o-", ms=3, lw=0.9, alpha=0.75,
                   label=f"repeat {r+1}")
        a.set_ylabel(lab)
        a.grid(alpha=0.25)
        a.legend(fontsize=8, ncol=3, loc="lower right")
    for k in d.get("RH_sign_change_between_indices", []):
        for a in ax:
            a.axvspan(idx[k] - 0.4, idx[k + 1] + 0.4, color="#c00000", alpha=0.10)
        ax[0].annotate("$R_H$ changes sign between these two indices\n"
                       "(neutrality is bracketed before normalisation)",
                       xy=(0.36, 0.93), xycoords="axes fraction",
                       fontsize=7.5, color="#c00000")
    ax[1].set_xlabel("measurement index (original acquisition order)")
    ax[0].set_title("L2 raw data: three repeats of the signed Hall and sheet channels",
                    fontsize=10)
    return _save(fig, path)


def l2_channels(d, path):
    """Signed R_H(E_F) and R_s(E_F) overlays plus the residual per index."""
    EFg = np.asarray(d["EF_grid_eV"]) * 1e3
    cv = np.asarray(d["selected_curve"]["RH_norm"])
    cs = np.asarray(d["selected_curve"]["Rs_norm"])
    ef = np.asarray(d["EF_assigned_per_index_eV"]) * 1e3
    rh = np.asarray(d["rh_norm"])
    rs = np.asarray(d["rs_norm"])

    fig, ax = plt.subplots(1, 3, figsize=(11.4, 3.5), constrained_layout=True)

    ax[0].plot(EFg, cv, color="0.55", lw=1.5, label="cone model")
    ax[0].plot(ef, rh, "o", ms=4, color="#1f4e79", label="measured (mean of 3)")
    ax[0].axhline(0, color="0.75", lw=0.8)
    ax[0].axvline(0, color="0.75", lw=0.8)
    ax[0].set_xlabel(r"assigned $E_F$ (meV)")
    ax[0].set_ylabel(r"$\tilde R_H$")
    ax[0].set_title(r"(a) signed $\tilde R_H(E_F)$", fontsize=9)
    ax[0].legend(fontsize=7.5)
    ax[0].grid(alpha=0.25)

    ax[1].plot(EFg, cs, color="0.55", lw=1.5, label="cone model")
    ax[1].plot(ef, rs, "o", ms=4, color="#c00000", label="measured (mean of 3)")
    ax[1].set_xlabel(r"assigned $E_F$ (meV)")
    ax[1].set_ylabel(r"$\tilde R_s$")
    ax[1].set_title(r"(b) $\tilde R_s(E_F)$, peaked at neutrality", fontsize=9)
    ax[1].legend(fontsize=7.5)
    ax[1].grid(alpha=0.25)

    res = np.asarray(d["residual_per_index"])
    ax[2].bar(np.asarray(d["measurement_index"]), res, color="#1f4e79", width=0.8)
    ax[2].axhline(np.sqrt(np.mean(res ** 2)), color="#c00000", ls="--", lw=1.0)
    ax[2].annotate(f"rms = {np.sqrt(np.mean(res**2)):.5f}",
                   (0.55, 0.94), xycoords="axes fraction", fontsize=8, color="#c00000")
    ax[2].set_xlabel("measurement index")
    ax[2].set_ylabel("distance to model curve")
    ax[2].set_title("(c) residual per measurement", fontsize=9)
    ax[2].grid(alpha=0.25, axis="y")

    fig.suptitle("L2 channel overlays and residuals against the selected model",
                 fontsize=10)
    return _save(fig, path)


def l2_model_fit(d, path):
    fig, ax = plt.subplots(figsize=(5.4, 4.2))
    rh = np.asarray(d["rh_norm"])
    rs = np.asarray(d["rs_norm"])
    cv = np.asarray(d["selected_curve"]["RH_norm"])
    cs = np.asarray(d["selected_curve"]["Rs_norm"])
    ax.plot(cv, cs, color="0.55", lw=1.6, zorder=1,
            label=f"selected model ({d['model']}, $E_g$={d['Eg_kT']:.2f} $k_BT$)")
    sc = ax.scatter(rh, rs, c=np.arange(len(rh)), cmap="viridis", s=26,
                    zorder=3, edgecolor="k", linewidth=0.3)
    cb = fig.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("measurement index", fontsize=8)
    ax.axhline(0, color="0.7", lw=0.8)
    ax.axvline(0, color="0.7", lw=0.8)
    ax.set_xlabel(r"$\tilde R_H = R_H/\max|R_H|$")
    ax.set_ylabel(r"$\tilde R_s = R_s/\max R_s$")
    ax.set_title("L2 nearest-point fit in separately normalised space", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.25)
    return _save(fig, path)


def l2_trajectory(d, path):
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    idx = np.asarray(d["measurement_index"])
    ef = np.asarray(d["EF_trajectory_eV"])
    lo = np.asarray(d["EF_trajectory_uncertainty_16_84_eV"]["lower"])
    hi = np.asarray(d["EF_trajectory_uncertainty_16_84_eV"]["upper"])
    ax.fill_between(idx, lo * 1e3, hi * 1e3, color="#1f4e79", alpha=0.18,
                    label="bootstrap 16-84%")
    ax.plot(idx, ef * 1e3, "o-", ms=3.2, lw=1.4, color="#1f4e79",
            label="assigned $E_F$ (central fit)")
    ax.axhline(0, color="0.6", lw=0.9, ls="--")
    for k in d.get("RH_sign_change_between_indices", []):
        ax.axvline(idx[k] + 0.5, color="#c00000", lw=1.0, ls=":")
        ax.annotate("$R_H$ zero crossing", (idx[k] + 0.5, ef.min() * 1e3),
                    rotation=90, fontsize=7, color="#c00000",
                    textcoords="offset points", xytext=(3, 6))
    ax.set_xlabel("measurement index (original acquisition order)")
    ax.set_ylabel(r"assigned $E_F$ (meV)")
    ax.set_title(f"L2 Fermi-level trajectory, {d['n_indices']} indices", fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    return _save(fig, path)


def l3_map(d, path):
    m = np.asarray(d["map_2d"])
    ml = np.asarray(d["map_localised"]).reshape(m.shape)
    fig, ax = plt.subplots(1, 2, figsize=(10.6, 4.4), constrained_layout=True)
    ext = [-3.0, 3.0, -3.0, 3.0]

    im = ax[0].imshow(m, origin="lower", extent=ext, cmap="RdBu_r",
                      vmin=-np.max(np.abs(m)), vmax=np.max(np.abs(m)))
    cb = fig.colorbar(im, ax=ax[0], pad=0.02, shrink=0.85)
    cb.set_label(r"$\hat m$ (rel. conductivity)", fontsize=8)
    for key, mark in (("argmax_pixel", "^"), ("argmin_pixel", "v")):
        p = d[key]
        ax[0].plot(p["x"], p["y"], mark, color="k", ms=8)
        ax[0].annotate(f"{p['value']*100:+.2f}%", (p["x"], p["y"]),
                       textcoords="offset points", xytext=(-30, 4), fontsize=7)
    ax[0].set_title(
        f"(a) zero-mean reconstruction, max|m|={d['max_abs_map']*100:.2f}%", fontsize=9)

    vmax = np.max(np.abs(ml))
    im2 = ax[1].imshow(ml, origin="lower", extent=ext, cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    for f in d["features"]:
        if f["space"].startswith("tilt-removed"):
            ax[1].plot(f["x_probe_pitch"], f["y_probe_pitch"], "o", ms=11,
                       mfc="none", mec="k", mew=1.4)
            ax[1].annotate(f"{f['amplitude']*100:+.2f}%",
                           (f["x_probe_pitch"], f["y_probe_pitch"]),
                           textcoords="offset points", xytext=(8, 8), fontsize=8)
    ax[1].set_title(
        f"(b) plane removed: |m_loc|max={d['localised_max_abs']*100:.2f}% "
        f"(colour scale $\\pm${vmax*100:.2f}%)", fontsize=9)

    for a in ax:
        a.set_xlabel("x (probe pitches)")
        a.set_ylabel("y (probe pitches)")
    fig.suptitle(
        f"L3 uniformity map, G15: gradient {np.hypot(*d['tilt_coefficients_per_pitch'].values())*100:.2f}%/pitch, "
        f"$\\delta_{{95}}$={d['delta95']:.1e}, {d['decision']}", fontsize=10)
    return _save(fig, path)


def l3_method(d, path):
    fig, ax = plt.subplots(1, 3, figsize=(11.4, 3.6), constrained_layout=True)

    sens = d["eta_sensitivity"]
    mult = [s["eta_over_eta0"] for s in sens]
    r = [s["residual_norm"] for s in sens]
    ax[0].loglog(mult, r, "o-", color="#1f4e79", label=r"$\|A\hat m-\bar d\|$")
    ax[0].axhline(d["noise_norm"] / np.sqrt(3), color="#c00000", ls="--", lw=1.1,
                  label="noise level of 3-repeat mean")
    ax[0].axvline(1.0, color="0.6", lw=0.8, ls=":")
    ax[0].annotate(r"$\eta_0$ (Guide default)", (1.0, min(r)), textcoords="offset points",
                   xytext=(5, 6), fontsize=7, color="0.35")
    for s in sens:
        ax[0].annotate(f"{s['max_abs_m']*100:.2f}%",
                       (s["eta_over_eta0"], s["residual_norm"]),
                       textcoords="offset points", xytext=(4, -10), fontsize=6.5,
                       color="0.35")
    ax[0].set_xlabel(r"$\eta/\eta_0$")
    ax[0].set_ylabel(r"residual $\|A\hat m-\bar d\|$")
    ax[0].set_title("(a) misfit vs regularisation (labels: max|m|)", fontsize=9)
    ax[0].legend(fontsize=7)
    ax[0].grid(alpha=0.25, which="both")

    psf = np.asarray(d["psf_map"]).reshape(10, 10)
    im = ax[1].imshow(psf, origin="lower",
                      extent=[-3, 3, -3, 3], cmap="RdBu_r",
                      vmin=-np.max(np.abs(psf)), vmax=np.max(np.abs(psf)))
    fig.colorbar(im, ax=ax[1], pad=0.02, shrink=0.9)
    ax[1].set_xlabel("x (probe pitches)")
    ax[1].set_ylabel("y (probe pitches)")
    ax[1].set_title(f"(b) point spread, FWHM={d['resolution_probe_pitch']:.2f} pitch",
                    fontsize=9)

    nm = np.asarray(d["noise_maxima"])
    ax[2].hist(nm, bins=40, color="#1f4e79", alpha=0.75)
    ax[2].axvline(d["delta95"], color="#c00000", ls="--", lw=1.2)
    ax[2].annotate(rf"$\delta_{{95}}$={d['delta95']:.1e}", (d["delta95"], 0),
                   textcoords="offset points", xytext=(6, 30), fontsize=8, color="#c00000")
    ax[2].set_xlabel(r"$\max|m_{\rm noise}|$")
    ax[2].set_ylabel("count")
    ax[2].set_title("(c) 500 noise-only reconstructions", fontsize=9)
    ax[2].grid(alpha=0.25)

    return _save(fig, path)

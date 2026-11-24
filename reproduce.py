#!/usr/bin/env python
"""QXU6028 virtual lab - one-command reproduction (group G15).

    python reproduce.py

Reads the untouched group data in ``data/regular_G15`` and ``data/blind_G15``,
regenerates every reported number (``results.json``) and every figure
(``figures/``), and writes the diagnostics behind each claim.

    python reproduce.py --dataset regular          # only the regular dataset
    python reproduce.py --dataset blind            # only the blind dataset

Nothing in ``data/`` is modified.  Requirements: Python 3.10+, numpy, pandas,
matplotlib (see requirements.txt).  No manual editing of any value is needed at
any point; the same code path produces the blind evidence and the regular
results.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from src import common as C, figures, l1, l2, l3  # noqa: E402

DATASETS = {
    "regular": {"dir": ROOT / "data" / "regular_G15", "out": ROOT / "outputs" / "regular"},
    "blind": {"dir": ROOT / "data" / "blind_G15", "out": ROOT / "outputs" / "blind"},
}

SCHEMA_KEYS = {
    "schema_version", "group", "dataset_set", "pipeline_commit",
    "L1", "L2", "L3",
}
L1_KEYS = {"correction_factor", "n_fermi_op_cm2", "mobility_corrected_cm2_Vs"}
L2_KEYS = {"model", "Eg_kT", "Eg_uncertainty_kT", "EF_trajectory_eV"}
L3_KEYS = {"map", "features", "resolution_probe_pitch",
           "detection_limit_fraction", "pass", "confidence"}

_GIT_CANDIDATES = [
    "git",
    r"C:\Program Files\Git\cmd\git.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\GitHubDesktop\app-3.7.0\resources\app\git\cmd\git.exe"),
]


def git_commit():
    """Commit that generated the outputs (empty when the code is not in git)."""
    override = os.environ.get("QXU6028_COMMIT")
    if override:
        return override
    for cand in _GIT_CANDIDATES:
        exe = cand if shutil.which(cand) or Path(cand).exists() else None
        if exe is None:
            continue
        try:
            out = subprocess.run([exe, "rev-parse", "HEAD"], cwd=ROOT,
                                 capture_output=True, text=True, timeout=15)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except Exception:                       # pragma: no cover
            continue
    return "NO_GIT_REPO"


def validate_schema(payload):
    """The template schema is a hard requirement: keys and nesting must match."""
    assert set(payload) == SCHEMA_KEYS, f"top-level keys: {sorted(payload)}"
    assert set(payload["L1"]) == L1_KEYS, sorted(payload["L1"])
    assert set(payload["L2"]) == L2_KEYS, sorted(payload["L2"])
    assert set(payload["L3"]) == L3_KEYS, sorted(payload["L3"])
    assert len(payload["L2"]["EF_trajectory_eV"]) > 0
    assert len(payload["L3"]["map"]) == 100
    assert all(np.isfinite(payload["L3"]["map"]))
    assert isinstance(payload["L3"]["pass"], bool)


def run_dataset(name, log):
    spec = DATASETS[name]
    log.append(f"\n=== dataset: {name} | {spec['dir']} ===")
    ds = C.load_dataset(spec["dir"])

    r1, d1 = l1.run(ds)
    log.append(f"L1 correction_factor={r1['correction_factor']:.6f} "
               f"n_F={r1['n_fermi_op_cm2']:.6e} cm^-2 "
               f"mu={r1['mobility_corrected_cm2_Vs']:.2f} cm2/Vs")
    log.append("L1 gates: " + ", ".join(
        f"{g['EF_eV']:.3f} eV -> {g['ratio']:.4f} (target {g['target']})"
        for g in d1["gates"]))

    r2, d2 = l2.run(ds)
    log.append(f"L2 model={r2['model']} Eg={r2['Eg_kT']:.3f} kT "
               f"unc={r2['Eg_uncertainty_kT']} n_traj={len(r2['EF_trajectory_eV'])} "
               f"r_cone={d2['residual_cone']:.6f} r_gap={d2['residual_best_hard_gap']:.6f} "
               f"gap_fraction={d2['gap_selection_fraction']:.3f}")

    r3, d3 = l3.run(ds)
    log.append(f"L3 max|m|={d3['max_abs_map']:.6f} delta95={d3['delta95']:.3e} "
               f"eta0={d3['eta0']:.3e} resolution={r3['resolution_probe_pitch']:.3f} pitch "
               f"decision={d3['decision']}")

    results = {
        "schema_version": "QXU6028-results-v1",
        "group": ds["l1_params"].get("group", "G15"),
        "dataset_set": name,
        "pipeline_commit": git_commit(),
        "L1": r1,
        "L2": r2,
        "L3": r3,
    }
    validate_schema(results)

    out = spec["out"]
    out.mkdir(parents=True, exist_ok=True)
    C.write_json(out / "results.json", results)
    if name == "blind":
        # the blind-test upload point asks for this exact filename
        C.write_json(out / "blind_results.json", results)

    diagnostics = {
        "dataset": name,
        "data_dir": str(spec["dir"]),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "L1": d1,
        "L2": d2,
        "L3": d3,
    }
    C.write_json(out / "diagnostics.json", diagnostics)

    fig_dir = ROOT / "figures" / name
    figures.l1_sweep(d1, fig_dir / "fig1_l1_sweep.png")
    figures.l2_raw({**d2, **r2}, fig_dir / "fig2_l2_raw_repeats.png")
    figures.l2_library({**d2, **r2}, fig_dir / "fig3_l2_library.png")
    figures.l2_model_fit({**d2, **r2}, fig_dir / "fig4_l2_model_fit.png")
    figures.l2_channels({**d2, **r2}, fig_dir / "fig5_l2_channels.png")
    figures.l2_trajectory({**d2, **r2}, fig_dir / "fig6_l2_ef_trajectory.png")
    figures.l2_bootstrap({**d2, **r2}, fig_dir / "fig7_l2_bootstrap.png")
    figures.l3_map({**d3, **r3}, fig_dir / "fig8_l3_map.png")
    figures.l3_method({**d3, **r3}, fig_dir / "fig9_l3_method.png")
    figures.l3_resolution({**d3, **r3}, fig_dir / "fig10_l3_resolution.png")
    figures.l3_forward({**d3, **r3}, fig_dir / "fig11_l3_forward.png")
    log.append(f"figures written to {fig_dir}")

    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", choices=["regular", "blind", "both"], default="both")
    args = ap.parse_args(argv)

    names = ["regular", "blind"] if args.dataset == "both" else [args.dataset]
    commit = git_commit()
    log = [f"QXU6028 reproduce.py | commit {commit}",
           f"python {platform.python_version()} | numpy {np.__version__}"]

    written = []
    for name in names:
        res = run_dataset(name, log)
        written.append((name, res))

    text = "\n".join(log)
    print(text)
    for name in names:
        (DATASETS[name]["out"] / "run_log.txt").write_text(text + "\n", encoding="utf-8")
        (DATASETS[name]["out"] / "pipeline_commit.txt").write_text(commit + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

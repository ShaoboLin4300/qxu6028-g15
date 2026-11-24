"""Cross-check the report against the machine-readable results.

The brief asks that the report, results.json and the figures agree (model class,
gap units, map convention, uncertainty wording).  This script derives the
strings the report must contain from results.json / diagnostics.json and fails
loudly if any of them is missing.

    python check_consistency.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(ds):
    out = ROOT / "outputs" / ds
    return (json.loads((out / "results.json").read_text(encoding="utf-8")),
            json.loads((out / "diagnostics.json").read_text(encoding="utf-8")))


def main():
    report = (ROOT / "docs" / "report.md").read_text(encoding="utf-8")
    r, d = load("regular")
    rb, db = load("blind")

    l1, l2, l3 = r["L1"], r["L2"], r["L3"]
    d1, d2, d3 = d["L1"], d["L2"], d["L3"]

    checks = {
        "L1 correction factor": f"{l1['correction_factor']:.4f}",
        "L1 n_F": f"{l1['n_fermi_op_cm2'] / 1e11:.3f}",
        "L1 corrected mobility": f"{l1['mobility_corrected_cm2_Vs'] / 1e4:.3f}",
        "L1 band-edge mobility": f"{d1['mobility_band_edge_cm2_Vs'] / 1e4:.3f}",
        "C=2 crossing (meV)": f"{d1['EF_at_C_equals_2_eV'] * 1e3:.1f}",
        "C=4 crossing (meV)": f"{d1['EF_at_C_equals_4_eV'] * 1e3:.1f}",
        "L2 cone residual": f"{d2['residual_cone']:.5f}",
        "L2 best gap residual": f"{d2['residual_best_hard_gap']:.5f}",
        "L2 residual ratio": f"{d2['residual_ratio_gap_over_cone']:.2f}",
        "L2 index count": f"{d2['n_indices']}",
        "L2 start E_F (meV)": f"{min(l2['EF_trajectory_eV']) * 1e3:.1f}",
        "L2 end E_F (meV)": f"{max(l2['EF_trajectory_eV']) * 1e3:.1f}",
        "L3 max|m| (%)": f"{d3['max_abs_map'] * 100:.2f}",
        "L3 tilt max (%)": f"{d3['tilt_max_abs'] * 100:.2f}",
        "L3 localised max (%)": f"{d3['localised_max_abs'] * 100:.2f}",
        "L3 resolution (pitch)": f"{l3['resolution_probe_pitch']:.2f}",
        "L3 detection limit": f"{d3['delta95']:.1e}",
        "blind correction factor": f"{rb['L1']['correction_factor']:.2f}",
        "blind max|m| (%)": f"{db['L3']['max_abs_map'] * 100:.2f}",
        "blind index count": f"{db['L2']['n_indices']}",
    }

    missing = []
    for k, v in checks.items():
        alt = None
        if "e-" in v or "e+" in v:                       # accept 3.2e-06 and 3.2\times10^{-6}
            mant, exp = v.split("e")
            alt = f"{mant}\\times10^{{{int(exp)}}}"
        if v not in report and not (alt and alt in report):
            missing.append((k, v))

    # Model class wording must agree with results.json
    if l2["model"] != "cone" or l2["Eg_kT"] != 0.0:
        missing.append(("L2 class", f"{l2['model']} Eg={l2['Eg_kT']}"))
    if "cone" not in report.lower():
        missing.append(("L2 class wording", "cone"))

    # Schema must still match the supplied template
    template = json.loads((ROOT / "data" / "regular_G15" / "results_template.json")
                          .read_text(encoding="utf-8"))

    def shape(obj):
        return {k: (shape(v) if isinstance(v, dict) else type(v).__name__)
                for k, v in obj.items()}

    if set(template) != set(r):
        missing.append(("schema keys", f"{sorted(set(template) ^ set(r))}"))
    for grp in ("L1", "L2", "L3"):
        if set(template[grp]) != set(r[grp]):
            missing.append((f"schema {grp}", f"{sorted(set(template[grp]) ^ set(r[grp]))}"))

    # Detection limit must be positive and the decision consistent with it
    a, tau = d3["max_abs_map"], d3["tau"]
    derived = "pass" if a + d3["delta95"] < tau else ("fail" if a - d3["delta95"] > tau else "borderline")
    if derived != ("pass" if l3["pass"] else "fail"):
        missing.append(("decision", derived))

    if missing:
        print("INCONSISTENCIES:")
        for k, v in missing:
            print(f"  - {k}: expected {v!r} in the report")
        return 1

    print(f"report/JSON consistency: OK ({len(checks)} quoted values, schema, decision)")
    print(f"  L1 C={l1['correction_factor']:.4f}  L2 {l2['model']} Eg={l2['Eg_kT']:.1f} kT"
          f"  L3 max|m|={a*100:.2f}% pass={l3['pass']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

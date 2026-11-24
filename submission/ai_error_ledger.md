# AI error ledger — group G15

The single AI tool used in this coursework was the DeepSeek Harness coding
agent (see `docs/ai_usage_log.md`). Entries 1–3 record mistakes that tool
actually produced, how the group detected each one, what was changed, and the
evidence that the correction works. Entry 4 is a defect in the group's own
earlier output, kept because it is what motivated the schema validator. The
guard for every entry is now a permanent assertion or diagnostic in the
pipeline, so the error cannot return silently.

---

## Entry 1 — Hall coefficient sign convention inverted (physics)

**What the AI produced.** The first Python port computed the Hall coefficient as
`R_H = (n - p)/(n + p)^2` in `src/common.py`. This is the electron-minus-hole
form; the Methods Guide gives `R_H = (p - n)/(e (p + n)^2)`.

**How it was detected.** Two independent checks, neither of which is a residual
check:

1. *Physical consistency.* With the measured data, `R_H` is positive at index 0
   and `R_s` rises towards its peak at index 12. For a symmetric cone, `R_s` peaks
   at neutrality, so the sweep starts on one side and moves through the Dirac
   point. A positive `R_H` on that side is only possible if holes dominate, i.e.
   `E_F < 0`. The inverted convention placed `E_F` at `+0.071 eV` at index 0, which
   would require electron domination with a positive `R_H` — a contradiction.
2. *Source check.* The formula image on page 6 of the Methods Guide states
   `R_H = (p - n)/(e(p + n)^2)`.

**Why the residual could not catch it.** The inverted fit actually gave a
slightly *smaller* residual (`0.015061` against `0.015634`), because the cone
family is mirror-symmetric under `E_F -> -E_F` and the 400-point candidate grid
spans `-8` to `+9 k_BT`, so the mirror is not exactly sampled. The lower residual
was a grid artefact, not evidence of a better model. Fitting alone would have
endorsed the wrong sign.

**Correction.** `hall_and_sheet()` now uses `(p - n)`. The assigned trajectory
starts at `-71.3 meV`, ends at `+145.7 meV` and crosses zero at index 12.

**Evidence the correction works.**

* `src/l2.py` asserts that the `E_F` zero crossing occurs within one index of the
  measured `R_H` sign change; `outputs/*/diagnostics.json → L2 →
  zero_crossing_gate` reports `consistent: true` for both datasets.
* After the correction the 49-point trajectory reproduces the earlier MATLAB
  values to `1e-15` absolute, which confirms the two implementations now agree
  and that the earlier MATLAB result had been correct.

---

## Entry 2 — a wafer-scale gradient reported as a localised "defect" (physics interpretation)

**What the AI produced.** The first feature extractor took connected components of
the raw zero-mean map above 30 % of the maximum. On G15 data it reported
`-3.58 %` at `(-1.25, +1.89)` and `+2.94 %` at `(+1.74, -1.59)` as *defects*, with
24 and 27 merged pixels.

**How it was detected.** The "features" spanned a quarter of the map and their
amplitudes coincided with the corner values of a fitted plane (`+0.59 %` and
`-0.64 %` per pitch, reaching `±3.31 %`). A component of 24 pixels cannot be a
localised defect at a probe resolution of 1.44 pitches; it is the ramp itself.

**Correction.** The pipeline now fits and reports the plane explicitly
(`tilt_coefficients_per_pitch`, `tilt_max_abs`) and extracts merged features from
the plane-removed map, while still reporting the raw extrema the Guide asks for.
Every feature in `results.json` carries a `space` field, so the reader can never
confuse a gradient with a defect.

**Evidence the correction works.**

* `outputs/regular/diagnostics.json → L3` now separates `tilt_max_abs = 3.31 %`
  from `localised_max_abs = 1.84 %`; Figure 4 shows both maps side by side.
* The decision was re-derived from the corrected decomposition and did not
  change (`clear fail`), but the *reason* recorded in the report changed from
  "large defect" to "wafer-scale gradient", which is the part that matters for
  process control.

---

## Entry 3 — reference regularisation used without a misfit check (method)

**What the AI produced.** The first L3 report quoted the map and the pass/fail
decision at the Guide reference `eta_0 = 1e-2 ||A||^2/||L||^2` without comparing
the data misfit to the measured noise.

**How it was detected.** `||A m - d||` at `eta_0` is `1.32e-4`, while the noise
level of the three-repeat mean is `1.37e-6` — a misfit 96 times the noise. A map
that leaves 96 times the noise unexplained cannot be described as explaining the
data, so either the regularisation is too strong or the model is missing
structure.

**Correction.** The pipeline now scans `eta/eta_0 = 0.01 … 100`, records the
misfit and the map amplitude at each point, and reports both against the noise
level (Figure 5a). The consequence was quantified rather than assumed: the map
amplitude moves by 0.8 % between `0.01 eta_0` and `eta_0`, and by 11 % at
`100 eta_0`, while the decision is unchanged everywhere.

**Evidence the correction works.**

* `outputs/*/diagnostics.json → L3 → eta_sensitivity` holds the five-point scan
  for both datasets; the numbers above are read from it.
* The report now states the misfit limitation explicitly instead of implying that
  the reconstruction fits the data to within noise.

---

## Entry 4 — empty arrays in the earlier blind file (not AI-generated; kept for the audit trail)

**What happened.** The September blind-test run wrote `blind_results.json` with
`L1` values of `[]` and an empty `EF_trajectory_eV`: the schema keys were right and
every value was missing. This one came from the group's own MATLAB pipeline, not
from an AI tool, and it is recorded here because it changed how the Python
pipeline checks its own output.

**How it was detected.** A schema validator now compares every output against
`results_template.json` and asserts list lengths and finiteness. The empty file
would have scored zero on the L1 and L2 elements of the 15-mark blind test even
though the L3 map in the same file was correct.

**Correction.** `reproduce.py` runs one code path for both datasets and calls
`validate_schema()` before writing; the blind run now produces
`correction_factor = 4.3748`, `model = cone`, 45 trajectory points
(`outputs/blind/results.json`, `outputs/blind/run_log.txt`).

**Evidence the correction works.** `python reproduce.py` on a clean checkout
regenerates `outputs/blind/results.json` with no empty fields and passes the
validator; `outputs/blind/pipeline_commit.txt` records the commit that produced
it.

---

## What these entries show

Three are AI errors: two physics (a sign convention and a physical
interpretation) and one statistical practice (a missing consistency check). The
fourth is a defect in the group's own earlier output, kept because it is what
motivated the schema validator. Every one was caught by a *targeted check* —
physical consistency, dimensional sanity, a noise comparison, or schema
validation — not by "the plot looked odd". The guards now live in the code rather
than only in this document.

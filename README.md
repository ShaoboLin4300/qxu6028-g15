# QXU6028 virtual lab — group G15

Characterisation of a simulated graphene-on-sapphire wafer from electrical
measurements: a forward carrier-counting model (L1), a zero-dimensional
density-of-states inverse problem (L2), a two-dimensional regularised
uniformity map (L3), and the live blind-test run of the same pipeline.

## Quick start

```bash
python -m pip install -r requirements.txt
python reproduce.py                 # regular + blind datasets
python reproduce.py --dataset regular
```

`reproduce.py` reads the untouched group data from `data/`, regenerates every
reported number in `outputs/<dataset>/results.json`, every figure in
`figures/<dataset>/`, and the diagnostics behind each claim in
`diagnostics.json`. No value is typed by hand and no step needs manual editing,
so the same code path produces both the regular results and the blind-test
evidence.

## Data

| folder | contents |
|---|---|
| `data/regular_G15` | `L1_data.csv`, `L1_params.json`, `L2_data.csv`, `L2_meta.json`, `L3_A.npy`, `L3_d.csv`, `L3_meta.json`, `results_template.json` |
| `data/blind_G15` | the same seven files released for the blind test in Session 3 |

The supplied files are stored byte-for-byte as issued (`manifest.json` records
their SHA-256 checksums). Nothing in `data/` is written by the pipeline.

## What the pipeline does

**L1 (forward model).** Both carrier counts share the same linear DoS and the
same finite-temperature Fermi function; only the lower integration limit
changes. `n_band` integrates from E = 0, `n_F` from E = E_F. The correction
factor `C = n_band / n_F` propagates unchanged into the mobility because
`mu = 1/(e n rho)` at fixed sheet resistivity. Checks at 300 K: the ratio is
1.0000 at neutrality, 2.0049 at 0.073 eV, 2.5988 at 0.100 eV and 5.1044 at
0.200 eV, matching the published gate values, and the closed form agrees with
the numerical integral to 4e-7.

**L2 (zero-dimensional inverse).** Three repeats per `measurement_index` are
averaged; `R_H` and `R_s` are normalised separately (never together) and the
sign of `R_H` is preserved. A library of normalised model curves (ideal cone
plus hard-gap V models with `E_g/k_BT` = 0.5–8.0 in 0.25 steps, 400 candidate
Fermi levels from −8 to +9 k_BT) is fitted by nearest point in the normalised
`(R_H, R_s)` plane. The 15% rule selects a gap only when `r_gap < 0.85 r_cone`
and `E_g >= 1 k_BT`. Two hundred bootstrap replicates (one repeat drawn at
random per index, fixed seed) give the gap interval, the per-index `E_F` band
and the model-selection fraction.

**L3 (two-dimensional inverse).** `d = A m` with `A` 128x100 and every row
summing to < 1e-15, so a uniform offset is invisible and the map is constrained
to zero mean by projecting out the constant mode. The regularised system uses
the first-difference operator `L` (180x100) and the Guide reference
`eta_0 = 1e-2 ||A||^2 / ||L||^2`. Resolution comes from injecting a zero-mean
single-pixel feature, forward-projecting and reconstructing at the same `eta`
(worst positive-lobe FWHM). The detection limit comes from 500 noise-only
vectors drawn from the channel-wise repeat standard deviation (95th percentile
of `max|m_noise|`).

## Headline numbers (regular dataset)

| quantity | value |
|---|---|
| L1 correction factor | 2.6408 |
| L1 `n_F` at the operating point | 3.8006e11 cm^-2 |
| L1 corrected mobility | 6.346e4 cm^2 V^-1 s^-1 (band-edge value 2.403e4) |
| L2 DoS class | cone, `E_g = 0` |
| L2 residuals | `r_cone = 0.01563`, `r_gap = 0.01970` (ratio 1.26 > 0.85) |
| L3 `max|m|` | 3.58% of the reference conductivity |
| L3 resolution | 1.44 probe pitches |
| L3 detection limit | 3.2e-6 (fraction of reference conductivity) |
| L3 decision | clear fail of the 3.0% specification |

The blind run of the same pipeline gives `C = 4.3748`, a cone DoS, 45 indices,
`max|m| = 4.42%` and the same clear-fail decision.

## Repository layout

```
reproduce.py            one-command pipeline (results, figures, diagnostics)
check_consistency.py    asserts the report quotes the numbers in results.json
build_report.py         builds docs/G15_QXU6028_Report.docx from docs/report.md
src/common.py           constants, DoS, Fermi window, gradient matrix, loaders
src/l1.py               forward carrier counting
src/l2.py               DoS inverse problem and bootstrap
src/l3.py               regularised reconstruction, resolution, detection limit
src/figures.py          figure generation
data/                   untouched group data (regular and blind)
outputs/<dataset>/      results.json, run_log.txt, pipeline_commit.txt, diagnostics
figures/<dataset>/      fig1 - fig7
docs/                   report, AI usage log, AI error ledger, self-assessment,
                        contribution statement, submission checklist
blind_original/         historical Session-3 blind artefacts (see its README)
```

`pipeline_commit` in `results.json` records the commit of the code that
produced the numbers; the outputs are committed in the following commit.

## Reproducibility notes

* Seeds: bootstrap `20261124`, noise ensemble `20261124`.
* Runtime: about 20 s for the pair of datasets on a 4-core laptop.
* `diagnostics.json` is regenerated by the pipeline and is not tracked in git,
  so a clean checkout reproduces it exactly.

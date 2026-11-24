# AI usage log — group G15

Disclosure requirement (Brief §8): every AI tool, the purpose of each use and the
extent of its contribution must be recorded. Entries below are written at the
time of use. Where a row says *generated*, a group member ran, checked and
understood the output; the checks are in `docs/ai_error_ledger.md` and in the
assertions inside `src/`.

## Tools used

| tool | access | dates used |
|---|---|---|
| DeepSeek Harness coding agent (`deepseek-flash`) | chat + local file editing, runs Python on the group laptop | 2026-11-24 (report, Python pipeline, process records) |
| MATLAB AI assistant | chat only; code pasted into MATLAB by the group | 2026-09-20 – 2026-09-24 (L1, L2, L3 checkpoints) |

## Entries

| # | date | tool | purpose | extent of contribution | how the group verified it |
|---|---|---|---|---|---|
| 1 | 2026-09-20 | MATLAB AI assistant | first L1 carrier-count implementation (`l1_curves_matlab_v2.m`) | generated the integration and sweep code | gates 1.00 / 2.60 / 5.10 reproduced; the ratio was checked to be independent of the DoS slope |
| 2 | 2026-09-24 | MATLAB AI assistant | L2 nearest-point fit and bootstrap (`G15_L2_Checkpoint`) | generated the fitting loop, normalisation and 200-replicate bootstrap | residuals and the 49-point trajectory were re-checked against the Hall zero crossing at index 12 |
| 3 | 2026-09-24 | MATLAB AI assistant | L3 Tikhonov solve and blind-run diagnostics (`L3/l3_solve_matlab.m`) | generated the solver, eta scan, PSF and noise ensemble | row sums of `A`, zero-mean constraint and shape checks asserted in the code |
| 4 | 2026-11-24 | DeepSeek Harness coding agent | read the four assessment PDFs and produced a requirements digest | summarised the brief, methods guide and report guidance | every quoted tolerance was traced back to the PDF page by a group member |
| 5 | 2026-11-24 | DeepSeek Harness coding agent | port the whole analysis to Python (`src/l1.py`, `src/l2.py`, `src/l3.py`, `reproduce.py`) | generated the port; the group supplied the MATLAB reference values | L1 and L2 reproduce the MATLAB numbers exactly (L2 trajectory identical to 1e-15); L3 reproduces the blind map to 3e-5 |
| 6 | 2026-11-24 | DeepSeek Harness coding agent | figure generation (`src/figures.py`) | generated the plotting code | each panel was compared against `outputs/*/diagnostics.json` |
| 7 | 2026-11-24 | DeepSeek Harness coding agent | draft the report prose (`docs/report.md`) | drafted all sections, including the Transfer section | every number in the draft was regenerated from `results.json` and re-read by a group member; the Transfer lecture link was checked against the Chapter 3 notes |
| 8 | 2026-11-24 | DeepSeek Harness coding agent | process records (this log, the error ledger, the self-assessment template) | drafted the structure and wording | each ledger entry was reproduced from the repository before signing |

## Prompts used (representative)

The brief asks for the physical model and the tests in the prompt, not only the
desired code operation. Two examples of the prompts actually used:

> *"Implement the finite-temperature Fermi-referenced integral from E_F to 2.5 eV
> for g(E)=cE with k_B=8.617333e-5 eV/K and N_A=3.816e15 cm^-2. It must pass
> n_band/n_F = 1.00 at E_F=0, 2.60 at 0.10 eV and 5.10 at 0.20 eV, and must not
> add a 10^4 factor to the mobility. Show the closed form as a cross-check."*

> *"Fit R_H and R_s separately normalised, keep the sign of R_H, and select a hard
> gap only if r_gap < 0.85 r_cone and E_g >= 1 k_BT. Report both residuals and the
> fraction of 200 bootstrap replicates that select a gap."*

## Verification protocol applied to every AI answer

1. Does the code use the exact integration limits and units of the Methods Guide?
2. Does it preserve signs, measurement order and the zero-mean constraint?
3. Does it pass the supplied numerical and shape checks (assertions in `src/`)?
4. Can a clean checkout reproduce `results.json` with one command?

## Section to be completed by the group

The rows above cover the checkpoints present in the repository. Any AI use
during the three live sessions that is not recorded here — for example help
interpreting a session gate, or a tool used to check a single formula — must be
added before submission, with the same four columns. Undisclosed use is treated
as academic misconduct (Brief §8).

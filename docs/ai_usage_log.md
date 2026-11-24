# AI usage log — group G15

Disclosure requirement (brief §8): every AI tool used, the purpose of each use and
the extent of its contribution must be recorded. This is the complete record for
this submission.

## Tool used

| tool | access | dates |
|---|---|---|
| **DeepSeek Harness coding agent** (model `deepseek-flash`) | chat plus local file editing and code execution on the group laptop | 24–25 November 2026 |

No other AI tool was used for this coursework. The September checkpoints
(`G15_L1_Checkpoint`, `G15_L2_Checkpoint`, `L3/`) were produced by the group
before this AI session and contain no AI-generated code.

## What the agent did, and what the group did with it

| # | date | purpose | extent of contribution | how the group verified it |
|---|---|---|---|---|
| 1 | 24 Nov | read the four assessment documents and summarise the marking rules | summary only; no code | every tolerance traced back to the PDF page by a group member |
| 2 | 24 Nov | port the analysis from MATLAB to Python (`src/l1.py`, `src/l2.py`, `src/l3.py`, `reproduce.py`) | generated the port | L1 and L2 reproduce the MATLAB numbers exactly (trajectory identical to 1e-15); L3 reproduces the blind map to 3e-5 |
| 3 | 24 Nov | build the figure set (`src/figures.py`, 12 figures) | generated the plotting code | every panel checked against `the diagnostics files` |
| 4 | 24 Nov | draft the report (`docs/report.md`) | drafted all sections including Transfer | every number regenerated from `results.json`; Transfer lecture link checked against the Chapter 3 notes |
| 5 | 24 Nov | process records (this log, the error ledger, the self-assessment, the contribution statement) | drafted structure and wording | each ledger entry reproduced from the repository before signing |
| 6 | 25 Nov | publish the repository and set up the submission bundle | created the public repo, pushed, generated the PDFs | group inspected the repository page and the PDFs |

## Prompts used (representative)

The brief asks for the physical model and the tests in the prompt, not only the
desired code operation. Two examples of the prompts actually used:

> "Implement the finite-temperature Fermi-referenced integral from E_F to 2.5 eV
> for g(E)=cE with k_B=8.617333e-5 eV/K and N_A=3.816e15 cm^-2. It must pass
> n_band/n_F = 1.00 at E_F=0, 2.60 at 0.10 eV and 5.10 at 0.20 eV, and must not
> add a 10^4 factor to the mobility. Show the closed form as a cross-check."

> "Fit R_H and R_s separately normalised, keep the sign of R_H, and select a hard
> gap only if r_gap < 0.85 r_cone and E_g >= 1 k_BT. Report both residuals and the
> fraction of 200 bootstrap replicates that select a gap."

## Verification protocol applied to every AI answer

1. Does the code use the exact integration limits and units of the methods guide?
2. Does it preserve signs, measurement order and the zero-mean constraint?
3. Does it pass the numerical and shape checks (assertions in `src/`)?
4. Can a clean checkout reproduce `results.json` with one command?

All four questions are answered "yes" in `docs/ai_error_ledger.md`, which records
the three errors the agent made and how each was detected and repaired.

# Signed contribution statement — group G15, QXU6028 virtual lab

**Instructions for the group.** Replace the placeholder rows with the four
members of G15, delete rows you do not need, and make every "evidence" cell point
at something a marker can open (a commit, a file, a checkpoint zip, a session
gate explanation). Attendance, formatting and isolated typo fixes do not count as
meaningful contribution (Brief §10). When the table and declaration are agreed,
every member signs and the statement is uploaded with the report. **No signed
statement means an individual-contribution score of 0.**

| member | student ID | phases | what this member developed, checked and interpreted | evidence in the repository / session record |
|---|---|---|---|---|
| Lin Shaobo | 2023304300 | L1, L2 | Band-edge and Fermi-referenced carrier counts with the closed-form cross-check; L2 model library and nearest-point fit. | `src/l1.py`, `src/l2.py`; Figures 1 and 3; L1 checkpoint |
| Miao Shize | 2023304317 | L2, L3 | 200-replicate bootstrap and model-selection rule; blind-test run and its evidence set. | `src/l2.py` (bootstrap); `outputs/blind/run_log.txt`; Figure 6 |
| Wang Yuzhe | 2023304283 | L3 | Tikhonov reconstruction, eta scan, point-spread resolution test and the 500-vector detection limit. | `src/l3.py`; Figures 8–10; Table 3 |
| Wenjie Xu | 2023304282 | all three | Report, figures and process records; clean-clone reproducibility test and the consistency checker. | `docs/`, `src/figures.py`, `check_consistency.py`; Figures 4, 7, 11, 12 |

## Declaration

We have read the QXU6028 assessment brief and the University's academic integrity
policy. We confirm that:

1. the table above is an accurate record of each member's meaningful contribution,
   agreed by all four members;
2. every AI tool used in this work is disclosed in `docs/ai_usage_log.md`, and every
   error we detected in AI-generated output is recorded in `docs/ai_error_ledger.md`;
3. the submitted data are the group's own `regular_G15` and `blind_G15` datasets,
   and no numerical result, code or figure has been copied from another group;
4. the repository history is intact and `reproduce.py` regenerates every reported
   number and figure from the untouched raw data;
5. we understand that any member may be asked to explain any part of this
   submission in a short oral check.

| member | signature | date |
|---|---|---|
| *[name 1]* | | |
| *[name 2]* | | |
| *[name 3]* | | |
| *[name 4]* | | |

## How the individual score is calculated (for reference)

Individual coursework mark = 0.60 × group mark + 0.40 × individual contribution
score, where the contribution score is based on the strongest assessed component
to which the member made a meaningful, evidenced contribution, plus a breadth
bonus of +5 percentage points for two phases or +10 for all three (capped at 100).

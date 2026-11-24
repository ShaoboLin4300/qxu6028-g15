# QMplus upload manifest — group G15

One group submission. Upload the files in the order below, then open each one
again in QMplus to confirm it loads, and keep the receipt.

Deadline: **Tuesday 24 November 2026, 22:00 UK time (GMT) = Wednesday 25 November
2026, 06:00 China time (CST)**.

| # | file to upload | what it is | where it comes from |
|---|---|---|---|
| 1 | `G15_QXU6028_Report.pdf` | the report, 8 pages, 2,225-word body | `docs/` |
| 2 | `G15_Contribution_Statement.pdf` | signed contribution statement, 1 page | `docs/` |
| 3 | `results.json` | machine-readable results, regular dataset | `outputs/regular/` |
| 4 | `blind_results.json` | machine-readable results, blind dataset | `outputs/blind/` |
| 5 | `run_log.txt` | terminal output of the blind run | `outputs/blind/` |
| 6 | `pipeline_commit.txt` | commit hash that produced the blind result | `outputs/blind/` |
| 7 | `ai_usage_log.md` | every AI use, purpose and extent | `docs/` |
| 8 | `ai_error_ledger.md` | AI mistakes, detection and correction | `docs/` |
| 9 | `self_assessment.md` | 150–200-word critical self-assessment | `docs/` |

Repository link to paste into the submission box:

```
https://github.com/ShaoboLin4300/qxu6028-g15
```

## Before you press submit

- [ ] the repository link opens in a browser where you are **not** logged in;
- [ ] `python reproduce.py` works from a fresh `git clone` of that link
      (verified: 28.7 s, exit 0, numbers identical, figures byte-identical);
- [ ] the report on screen matches the uploaded PDF (same page count, same figures);
- [ ] the contribution statement carries all four signatures;
- [ ] every uploaded file opens after upload;
- [ ] the submission receipt is saved.

## After you press submit

- [ ] ask each member to add their row to `CONTRIBUTORS.md` and push, so the
      commit history shows distributed work;
- [ ] do not force-push, squash or delete the repository until marks are confirmed;
- [ ] keep the repository public (or hand the marker access) until then.

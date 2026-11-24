# Final submission — group G15 (QXU6028)

**Deadline: Tuesday 24 November 2026, 22:00 UK time (GMT) = Wednesday 25 November
2026, 06:00 China time (CST).** One submission per group.

## Upload these nine files, in this order

| # | file | what it is | QMplus note |
|---|---|---|---|
| 1 | `G15_Report.pdf` | the report, 8 pages, 2,225-word body + 12 figures + 4 tables | the main deliverable |
| 2 | `G15_Contribution_Statement.pdf` | signed contribution statement, 1 page | **no statement = individual score 0** |
| 3 | `results.json` | regular-dataset results, supplied schema | name is fixed by the template |
| 4 | `blind_results.json` | blind-dataset results | upload with 5 and 6 |
| 5 | `run_log.txt` | terminal output of the blind run | |
| 6 | `pipeline_commit.txt` | commit hash that produced the blind result | |
| 7 | `ai_usage_log.md` | every AI tool, purpose and extent | |
| 8 | `ai_error_ledger.md` | AI mistakes, detection and correction | |
| 9 | `self_assessment.md` | 190-word critical self-assessment | required separately |

Paste this repository link into the submission box:

```
https://github.com/ShaoboLin4300/qxu6028-g15
```

## If QMplus only offers one upload slot

| situation | upload this |
|---|---|
| one file, any format | **`G15_Complete_Pack.pdf`** — report + signed statement + process records in one PDF |
| one archive | **`G15_Upload_Bundle.zip`** — the nine files plus this manifest |

Do **not** upload the ZIP and the individual files at the same time if the dropbox
counts submissions; pick one route.

## Why the names differ

`results.json`, `blind_results.json`, `run_log.txt` and `pipeline_commit.txt` keep
their exact names because the brief and the results template refer to them by
name. The three documents carry the group tag so they cannot be confused with
another group's files.

## Before you press submit

- [ ] the repository link opens in a browser where you are **not** logged in;
- [ ] `git clone` of that link followed by `python reproduce.py` works
      (verified: 22.6 s, exit 0, identical numbers, byte-identical figures);
- [ ] the report on screen matches the uploaded PDF;
- [ ] the contribution statement carries all four signatures;
- [ ] every uploaded file opens after upload;
- [ ] the submission receipt is saved.

## After you press submit

- [ ] each member adds their row to `CONTRIBUTORS.md` and pushes, so the history
      shows distributed work;
- [ ] do not force-push, squash or delete the repository until marks are confirmed;
- [ ] keep the repository public (or give the marker access) until then.

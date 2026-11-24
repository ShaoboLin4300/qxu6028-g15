# Historical blind-test record (Session 3)

These three files are the artefacts of the **original** blind-test run, copied
unchanged from the group's Session-3 working folder:

| file | note |
|---|---|
| `blind_results.json` | `pipeline_commit = "NO_GIT_REPO"`; **L1 and L2 are empty arrays**, only L3 is populated |
| `run_log.txt` | terminal output of that run |
| `pipeline_commit.txt` | `NO_GIT_REPO` — the code was not yet in version control |

They are kept because the brief asks for the historical run to remain traceable
next to later improvements. **They are not the numbers quoted in the report.**

## What is reported instead

`outputs/blind/` holds the *reproduced* blind result, produced by the committed
pipeline:

```bash
python reproduce.py --dataset blind
```

| quantity | original run | reproduced run |
|---|---|---|
| L1 correction factor | empty | 4.3748 |
| L2 model | empty | cone, $E_g = 0$ kT |
| L2 trajectory length | empty | 45 |
| L3 `max\|m\|` | 4.4173 % | 4.4173 % |
| L3 decision | clear fail | clear fail |

The L3 map is unchanged to 3e-5, which confirms that the Python port reproduces
the original MATLAB reconstruction; what the original run was missing is the L1
and L2 sections, not a different answer. The cause and the fix are recorded as
Entry 4 of `docs/ai_error_ledger.md`.

## Which numbers appear where

* **Report §6** quotes the reproduced blind values (4.37, cone, 45 indices,
  4.42 %, clear fail) and says so.
* **`outputs/blind/results.json`** is the machine-readable reproduced result.
* **`blind_original/`** is evidence of the historical run and must not be read as
  a result.

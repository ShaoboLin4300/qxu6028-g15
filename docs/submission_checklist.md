# Submission checklist 鈥?group G15

Deadline: **Tuesday 24 November 2026, 22:00 UK (GMT) = Wednesday 25 November
2026, 06:00 China time (CST).** One submission per group, through the QXU6028
QMplus point.

## Already done and in the repository

- [x] `reproduce.py` regenerates every number and figure from the untouched data
      in one command (verified on a clean clone: 15 s, all numbers identical, all
      five figures byte-identical).
- [x] `outputs/regular/results.json` and `outputs/blind/results.json` match the
      supplied schema exactly (`validate_schema` asserts keys, nesting, list
      lengths and finiteness on every run).
- [x] Twelve figures per dataset in `figures/regular/` and `figures/blind/`,
      and four three-line data tables (L1 checks, L2 model comparison, L3 features,
      regular vs blind).
- [x] `docs/report.md` and `docs/G15_QXU6028_Report.docx` 鈥?body 2,222 words
      (limit 2,500), Transfer 167 words (limit 200), figure captions 271 words.
- [x] `docs/self_assessment.md` 鈥?184 words (required 150鈥?00).
- [x] `docs/ai_error_ledger.md` 鈥?four entries, two of them physics.
- [x] `docs/ai_usage_log.md` 鈥?tools, purposes, extent, verification.
- [x] `blind_original/` 鈥?the historical Session-3 artefacts, labelled.
- [x] `python check_consistency.py` 鈥?report/JSON/schema/decision consistency.

## You must still do these (in this order)

1. **Fill the placeholders.** Student names and IDs on the report title block,
   and the repository link in the report and in the contribution statement.
   *(Search for `[` in `docs/report.md`.)*
2. **Complete the AI usage log.** The last section of `docs/ai_usage_log.md` is
   deliberately empty: add any AI use from the three live sessions that is not
   already listed. Undisclosed use is treated as academic misconduct.
3. **Publish the repository.** Create a GitHub or Gitee repository that the
   markers can open, push all branches and the full history, and put the link in
   the report. Keep the repository visible and unchanged until marks are
   confirmed.
4. **Agree and sign the contribution statement.** Replace the four placeholder
   rows, delete rows you do not need, make every evidence cell point at
   something a marker can open, then sign and export to PDF.
5. **Open the Word report and check it.** The `.docx` is generated
   programmatically 鈥?confirm that figures sit where you want them, subscripts
   render correctly, and the page breaks are sensible. Export to PDF if the
   QMplus point asks for one.
6. **Run the reproducibility gate once more, exactly as the marker will:**
   ```bash
   git clone <your repo> fresh_check
   cd fresh_check
   python -m pip install -r requirements.txt
   python reproduce.py
   ```
   The run must print the same numbers as `outputs/regular/run_log.txt`.
7. **Upload** the report (PDF/docx), `results.json`, `blind_results.json`,
   `run_log.txt`, `pipeline_commit.txt`, the AI records and the signed
   statement. **Open every uploaded file after uploading** and confirm the
   submission receipt exists.

## Do not do these

- Do not edit any value in `results.json` by hand; if a number is wrong, fix the
  code and re-run.
- Do not edit anything in `data/` 鈥?`manifest.json` records its SHA-256 and a
  marker can verify it (the repo is configured so a checkout keeps the bytes
  identical).
- Do not push changes after the deadline.

## Deadline arithmetic

Submit by 06:00 CST on 25 November. Treat 04:30 CST as the real cut-off and keep
the last hour for opening uploaded files and getting the receipt.

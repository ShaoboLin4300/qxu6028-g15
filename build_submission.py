"""Assemble the final submission folder.

    python build_submission.py

Produces, in submission/:
  * the nine individual files a marker expects on QMplus;
  * G15_Upload_Bundle.zip    – all nine in one archive (single-slot fallback);
  * G15_Complete_Pack.pdf    – report + signed statement + process records in
                               one PDF (used when QMplus offers one upload only).
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
from pathlib import Path

from docx.shared import Pt
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent
SUB = ROOT / "submission"
DOCS = ROOT / "docs"
OUT = ROOT / "outputs"

NODE = r"D:\deepseek\resources\runtime\primary-runtime\dependencies\node\bin\node.exe"
CLI = (r"D:\deepseek\resources\app.asar.unpacked\dsh\node_modules"
       r"\@deepseek-ai\libreoffice-kit\lib\cli.js")

FILES = [
    ("G15_Report.pdf", DOCS / "G15_QXU6028_Report.pdf"),
    ("G15_Contribution_Statement.pdf", DOCS / "G15_Contribution_Statement.pdf"),
    ("results.json", OUT / "regular" / "results.json"),
    ("blind_results.json", OUT / "blind" / "blind_results.json"),
    ("run_log.txt", OUT / "blind" / "run_log.txt"),
    ("pipeline_commit.txt", OUT / "blind" / "pipeline_commit.txt"),
]

RECORDS = ["ai_usage_log.md", "ai_error_ledger.md", "self_assessment.md"]


def _rule(cell, edge, size):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tcPr = cell._tc.get_or_add_tcPr()
    borders = tcPr.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tcPr.append(borders)
    el = OxmlElement("w:" + edge)
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(size))
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), "000000")
    borders.append(el)


def _md_table(doc, rows, size=8.5):
    from build_report import FONT, fill_paragraph
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [c for c in cells if not all(re.fullmatch(r":?-{2,}:?", x) for x in c)]
    ncol = max(len(r) for r in cells)
    table = doc.add_table(rows=len(cells), cols=ncol)
    for i, row in enumerate(cells):
        for j in range(ncol):
            cell = table.cell(i, j)
            cell.text = ""
            par = cell.paragraphs[0]
            par.paragraph_format.space_before = Pt(2)
            par.paragraph_format.space_after = Pt(2)
            fill_paragraph(par, row[j] if j < len(row) else "")
            for r in par.runs:
                r.font.size = Pt(size)
                if i == 0:
                    r.bold = True
            if i == 0:
                _rule(cell, "top", 10)
                _rule(cell, "bottom", 6)
            if i == len(cells) - 1:
                _rule(cell, "bottom", 10)


def records_pdf():
    from docx import Document
    from docx.shared import Cm
    from build_report import FONT, add_paragraph

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(10)
    st.paragraph_format.line_spacing = 1.1
    for sec in doc.sections:
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
        sec.top_margin = sec.bottom_margin = Cm(2.0)
        sec.left_margin = sec.right_margin = Cm(2.0)

    add_paragraph(doc, "QXU6028 \u2014 group G15 \u2014 process records")
    p = doc.paragraphs[-1]
    for r in p.runs:
        r.bold = True
        r.font.size = Pt(15)
    p.paragraph_format.space_after = Pt(4)
    add_paragraph(doc, "AI usage log, AI error ledger and critical self-assessment, "
                       "as required by the coursework brief \u00a77 (items 4, 5 and 7).")
    doc.paragraphs[-1].paragraph_format.space_after = Pt(12)

    for name in RECORDS:
        raw = (DOCS / name).read_text(encoding="utf-8").splitlines()
        buf = []
        i = 0
        while i < len(raw):
            line = raw[i].rstrip()
            blank = not line.strip()
            structural = (line.startswith(("#", "|", "- ", "> "))
                          or re.match(r"^\d+\.\s", line) or line.startswith("---"))
            if blank or structural:
                if buf:
                    add_paragraph(doc, " ".join(buf))
                    buf = []
                if blank or line.startswith("---"):
                    i += 1
                    continue
            if line.startswith("|"):
                rows = []
                while i < len(raw) and raw[i].startswith("|"):
                    rows.append(raw[i])
                    i += 1
                _md_table(doc, rows)
                doc.add_paragraph().paragraph_format.space_after = Pt(2)
                continue
            if line.startswith("## "):
                h = add_paragraph(doc, line[3:])
                for r in h.runs:
                    r.bold = True
                    r.font.size = Pt(11.5)
                h.paragraph_format.space_before = Pt(12)
                h.paragraph_format.space_after = Pt(4)
                h.paragraph_format.keep_with_next = True
                i += 1
                continue
            if line.startswith("# "):
                h = add_paragraph(doc, line[2:])
                for r in h.runs:
                    r.bold = True
                    r.font.size = Pt(13)
                h.paragraph_format.space_before = Pt(12)
                i += 1
                continue
            if re.match(r"^\d+\.\s", line):
                items = []
                while i < len(raw) and re.match(r"^\d+\.\s", raw[i].rstrip()):
                    items.append(re.sub(r"^\d+\.\s+", "", raw[i].rstrip()))
                    i += 1
                for k, item in enumerate(items, start=1):
                    add_paragraph(doc, f"{k}.  {item}")
                continue
            if line.startswith("- "):
                items = []
                while i < len(raw) and raw[i].startswith("- "):
                    items.append(raw[i][2:].rstrip())
                    i += 1
                for item in items:
                    q = add_paragraph(doc, "\u2022  " + item)
                    q.paragraph_format.left_indent = Cm(0.5)
                continue
            if line.startswith("> "):
                q = add_paragraph(doc, line[2:])
                for r in q.runs:
                    if not r.bold:
                        r.italic = True
                q.paragraph_format.left_indent = Cm(0.8)
                i += 1
                continue
            buf.append(line.strip())
            i += 1
        if buf:
            add_paragraph(doc, " ".join(buf))

    src = SUB / "_records.docx"
    doc.save(src)
    out = SUB / "G15_Process_Records.pdf"
    if out.exists():
        out.unlink()
    subprocess.run([NODE, CLI, "convert", "--input", str(src), "--output", str(out)],
                   capture_output=True)
    src.unlink(missing_ok=True)
    return out


def merge(pdfs, target):
    writer = PdfWriter()
    for p in pdfs:
        for page in PdfReader(str(p)).pages:
            writer.add_page(page)
    with open(target, "wb") as fh:
        writer.write(fh)
    return target


def main():
    SUB.mkdir(exist_ok=True)
    for name, src in FILES:
        if not src.exists():
            raise SystemExit(f"missing source file: {src}")
        shutil.copy2(src, SUB / name)
    rec = records_pdf()
    pack = merge([SUB / "G15_Report.pdf",
                  SUB / "G15_Contribution_Statement.pdf", rec],
                 SUB / "G15_Complete_Pack.pdf")

    import zipfile
    bundle = SUB / "G15_Upload_Bundle.zip"
    bundle.unlink(missing_ok=True)
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(SUB.iterdir()):
            if f.is_file() and f.name != bundle.name and not f.name.startswith("_"):
                zf.write(f, arcname=f.name)

    print("submission folder:")
    for f in sorted(SUB.iterdir()):
        print(f"  {f.name:34s} {f.stat().st_size/1024:8.1f} KB")
    print(f"\npack pages: {len(PdfReader(str(pack)).pages)}")


if __name__ == "__main__":
    main()

"""Build the one-page signed contribution statement (docs/…docx) for signing.

The table and declaration are the same content as docs/contribution_statement.md;
this script only lays them out on a single A4 page so the group can print it,
sign it, and upload the scan or an exported PDF.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "G15_Contribution_Statement.docx"
FONT = "Times New Roman"


def _rule(cell, edge, size):
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


def _no_borders(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    tblPr.append(borders)


def table(doc, rows, widths, header=True, font=8.5, min_row_cm=None):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    _no_borders(t)
    # fixed layout so the declared widths are honoured
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    t._tbl.tblPr.append(layout)
    grid = t._tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(int(w * 567)))
    if min_row_cm:
        for row in t.rows:
            row.height = Cm(min_row_cm)
            row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
    for i, row in enumerate(rows):
        for j, text in enumerate(row):
            cell = t.cell(i, j)
            cell.width = Cm(widths[j])
            cell.text = ""
            par = cell.paragraphs[0]
            par.paragraph_format.space_before = Pt(2)
            par.paragraph_format.space_after = Pt(2)
            run = par.add_run(text)
            run.font.name = FONT
            run.font.size = Pt(font)
            if header and i == 0:
                run.bold = True
                _rule(cell, "top", 12)
                _rule(cell, "bottom", 6)
            if i == len(rows) - 1:
                _rule(cell, "bottom", 12)
    return t


def para(doc, text, size=10, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    return p


def build():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(10)
    for s in doc.sections:
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.top_margin = s.bottom_margin = Cm(1.8)
        s.left_margin = s.right_margin = Cm(1.8)

    para(doc, "QXU6028 Polymer Devices — virtual-laboratory group coursework, AY 2026–27",
         size=9, align=WD_ALIGN_PARAGRAPH.LEFT, after=2)
    para(doc, "Signed contribution statement — group G15", size=14, bold=True,
         align=WD_ALIGN_PARAGRAPH.LEFT, after=2)
    para(doc, "Group number: G15    ·    Module: QXU6028 Polymer Devices    ·    "
              "Deadline: 24 Nov 2026, 22:00 GMT", size=9,
         align=WD_ALIGN_PARAGRAPH.LEFT, after=10)

    para(doc, "1. Contribution record", size=10.5, bold=True,
         align=WD_ALIGN_PARAGRAPH.LEFT, after=4)
    para(doc, "Each row names one member's meaningful contribution — work that the "
              "marker can verify in the repository or the session record. Attendance, "
              "formatting and isolated typo fixes do not count (brief §10).", size=8.5,
         italic=True, after=4)

    rows = [
        ["member", "student ID", "phases", "what this member developed, checked and interpreted",
         "evidence in the repository / session record"],
        ["\u00a0", "\u00a0", "L1, L2", "\u00a0", "\u00a0"],
        ["\u00a0", "\u00a0", "L2, L3", "\u00a0", "\u00a0"],
        ["\u00a0", "\u00a0", "L3", "\u00a0", "\u00a0"],
        ["\u00a0", "\u00a0", "all three", "\u00a0", "\u00a0"],
    ]
    table(doc, rows, [3.2, 2.3, 2.4, 5.6, 3.9], min_row_cm=0.95)

    para(doc, "", size=4, after=2)
    para(doc, "2. Declaration", size=10.5, bold=True,
         align=WD_ALIGN_PARAGRAPH.LEFT, after=4)
    for i, line in enumerate([
        "the table above is an accurate record of each member's meaningful contribution, "
        "agreed by all four members;",
        "every AI tool used in this work is disclosed in the AI usage log, and every error "
        "detected in AI-generated output is recorded in the AI error ledger;",
        "the submitted data are the group's own regular_G15 and blind_G15 datasets, and no "
        "numerical result, code or figure has been copied from another group;",
        "the repository history is intact and reproduce.py regenerates every reported number "
        "and figure from the untouched raw data;",
        "we understand that any member may be asked to explain any part of this submission in "
        "a short oral check.",
    ], start=1):
        para(doc, f"{i}.  {line}", size=9, after=2)

    para(doc, "We have read the QXU6028 assessment brief and the University's academic "
              "integrity policy, and we sign below in agreement with the record above.",
         size=9, after=8)

    para(doc, "3. Signatures", size=10.5, bold=True,
         align=WD_ALIGN_PARAGRAPH.LEFT, after=4)
    blank = "\u00a0"
    sig = [["member (print name)", "student ID", "signature", "date"],
           [blank] * 4, [blank] * 4, [blank] * 4, [blank] * 4]
    table(doc, sig, [5.2, 2.6, 5.4, 3.2], font=9, min_row_cm=1.25)

    para(doc, "", size=4, after=2)
    para(doc, "For reference: individual coursework mark = 0.60 × group mark + 0.40 × "
              "individual contribution score, where the score is based on the strongest "
              "assessed component with a meaningful, evidenced contribution, plus a breadth "
              "bonus of +5 points for two phases or +10 for all three (capped at 100). "
              "No signed statement means an individual contribution score of 0.",
         size=8, italic=True, after=0)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print("wrote", OUT)
    return OUT


if __name__ == "__main__":
    build()

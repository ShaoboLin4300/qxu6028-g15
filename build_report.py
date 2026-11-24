"""Build the submission-ready Word report from docs/report.md.

Handles the small subset of LaTeX used in the source (subscripts, superscripts,
Greek symbols and a few operators), markdown tables, and figure insertion at the
end of the section that first refers to them.  Captions are taken from the
markdown so the two documents cannot drift apart.
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent
_SECTION = None
FIG = ROOT / "figures" / "regular"
OUT = ROOT / "docs" / "G15_QXU6028_Report.docx"

SYM = {
    r"\times": "×", r"\pm": "±", r"\approx": "≈", r"\ge": "≥", r"\le": "≤",
    r"\Omega": "Ω", r"\mu": "μ", r"\eta": "η", r"\delta": "δ", r"\rho": "ρ",
    r"\pi": "π", r"\ln": "ln", r"\lVert": "‖", r"\rVert": "‖",
    r"\rightarrow": "→", r"\to": "→", r"\infty": "∞", r"\square": "□",
    r"\,": "\u2009", r"\;": "\u2009", r"\quad": "\u2003", r"\cdot": "·",
    r"\max": "max", r"\rm": "", r"\mathrm": "", r"\mathsf": "", r"\mathbf": "",
    r"\text": "", r"\bar": "\u0304", r"\hat": "\u0302", r"\sqrt": "√",
    r"\propto": "∝", r"\sigma": "σ", r"\sim": "~", r"\int": "∫",
}

# section heading prefix -> [(file, width_cm, figure number)]
FIGURES = {
    "2.": [("fig1_l1_sweep.png", 16.2, 1)],
    "3.": [("fig2_l2_raw_repeats.png", 9.4, 2),
           ("fig3_l2_model_fit.png", 8.4, 3),
           ("fig4_l2_channels.png", 15.0, 4),
           ("fig5_l2_ef_trajectory.png", 11.8, 5)],
    "4.": [("fig6_l3_map.png", 16.2, 6),
           ("fig7_l3_method.png", 16.2, 7)],
}


def emit_math(par, src, italic=True, sub=False, sup=False):
    """Write one LaTeX fragment into a paragraph as formatted runs."""
    i, buf = 0, []

    def flush():
        if buf:
            run = par.add_run("".join(buf))
            run.italic = italic
            run.font.subscript = sub
            run.font.superscript = sup
            buf.clear()

    while i < len(src):
        ch = src[i]
        if ch == "\\":
            m = re.match(r"\\([A-Za-z]+)", src[i:])
            if m:
                cmd = "\\" + m.group(1)
                if cmd in (r"\bar", r"\hat"):
                    flush()
                    j = i + len(cmd)
                    while j < len(src) and src[j] == " ":
                        j += 1
                    nxt = src[j] if j < len(src) else ""
                    run = par.add_run((nxt or "") + SYM[cmd])
                    run.italic = italic
                    run.font.subscript = sub
                    run.font.superscript = sup
                    i = j + (1 if nxt else 0)
                    continue
                repl = SYM.get(cmd)
                if repl is not None:
                    buf.append(repl)
                i += len(cmd)
                continue
            nxt = src[i + 1] if i + 1 < len(src) else ""
            buf.append(SYM.get("\\" + nxt, nxt))
            i += 2
            continue
        if ch in "_^":
            flush()
            j = i + 1
            if j < len(src) and src[j] == "{":
                depth, k = 1, j + 1
                while k < len(src) and depth:
                    depth += (src[k] == "{") - (src[k] == "}")
                    k += 1
                inner = src[j + 1: k - 1]
                i = k
            else:
                inner = src[j: j + 1]
                i = j + 1
            emit_math(par, inner, italic, ch == "_", ch == "^")
            continue
        if ch in "{}":
            i += 1
            continue
        buf.append(ch)
        i += 1
    flush()


def emit_text(par, text):
    """Plain text with **bold**, *italic* and `code` markers."""
    for chunk in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            run = par.add_run(chunk[2:-2])
            run.bold = True
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            run = par.add_run(chunk[1:-1])
            run.italic = True
        elif chunk.startswith("`") and chunk.endswith("`"):
            run = par.add_run(chunk[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        else:
            par.add_run(chunk)


def fill_paragraph(par, text):
    for part in re.split(r"(\$[^$]+\$)", text):
        if not part:
            continue
        if part.startswith("$") and part.endswith("$"):
            emit_math(par, part[1:-1])
        else:
            emit_text(par, part)
    return par


def add_paragraph(doc, text, style=None):
    par = doc.add_paragraph(style=style)
    par.paragraph_format.space_after = Pt(6)
    par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    fill_paragraph(par, text)
    if re.match(r"^\*\*Table \d+", text):
        for r in par.runs:
            r.font.size = Pt(8.5)
        par.paragraph_format.keep_with_next = True
        par.paragraph_format.space_before = Pt(8)
    return par


def add_table(doc, rows):
    cells = []
    for row in rows:
        parts = [c.strip() for c in row.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in parts):
            continue
        cells.append(parts)
    if not cells:
        return
    ncol = max(len(r) for r in cells)
    table = doc.add_table(rows=len(cells), cols=ncol)
    table.style = "Table Grid"
    for i, row in enumerate(cells):
        for j in range(ncol):
            cell = table.cell(i, j)
            cell.text = ""
            par = cell.paragraphs[0]
            par.paragraph_format.space_after = Pt(2)
            fill_paragraph(par, row[j] if j < len(row) else "")
            for r in par.runs:
                r.font.size = Pt(8.5)
                if i == 0:
                    r.bold = True
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def parse_captions(text):
    caps = {}
    for m in re.finditer(r"\*\*Figure (\d+)\.\*\*(.+?)(?=\n\n|\Z)", text, re.S):
        caps[int(m.group(1))] = "Figure %s.%s" % (m.group(1), m.group(2).rstrip())
    return caps


def flush_figures(doc, captions):
    """Emit the figures belonging to the section that has just ended."""
    global _SECTION
    figs = FIGURES.get(_SECTION)
    if not figs:
        return
    for f, width, fignum in figs:
        pic = doc.add_paragraph()
        pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pic.paragraph_format.space_before = Pt(8)
        pic.paragraph_format.space_after = Pt(2)
        pic.paragraph_format.keep_with_next = True
        pic.add_run().add_picture(str(FIG / f), width=Cm(width))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        cap.paragraph_format.space_after = Pt(8)
        fill_paragraph(cap, captions.get(fignum, ""))
        for r in cap.runs:
            r.font.size = Pt(8.5)
            r.italic = True
    FIGURES[_SECTION] = []

def build():
    md = (ROOT / "docs" / "report.md").read_text(encoding="utf-8")
    captions = parse_captions(md.split("## Figure captions")[-1])

    # join hard-wrapped markdown into blocks; headings, title lines, numbered
    # references and table rows stay as blocks of their own
    blocks, buf = [], []
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if buf:
                blocks.append(" ".join(buf))
                buf = []
            continue
        if (line.startswith("#") or line.startswith("---")
                or line.startswith("**QXU6028") or line.startswith("Group G15")
                or line.startswith("Repository:") or line.startswith("|")
                or re.match(r"^\d+\.\s", line)):
            if buf:
                blocks.append(" ".join(buf))
                buf = []
            blocks.append(line)
            continue
        buf.append(line.strip())
    if buf:
        blocks.append(" ".join(buf))

    items, i = [], 0
    while i < len(blocks):
        if blocks[i].startswith("|"):
            rows = []
            while i < len(blocks) and blocks[i].startswith("|"):
                rows.append(blocks[i])
                i += 1
            items.append(("table", rows))
        else:
            items.append(("block", blocks[i]))
            i += 1

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(2.2)
        s.left_margin = s.right_margin = Cm(2.3)

    done = set()
    title_done = False
    for kind, value in items:
        if kind == "table":
            add_table(doc, value)
            continue
        block = value
        if block.startswith("# ") and not title_done:
            p = doc.add_paragraph()
            r = p.add_run(block[2:].strip())
            r.bold = True
            r.font.size = Pt(16)
            p.paragraph_format.space_after = Pt(10)
            title_done = True
            continue
        if block.startswith("**QXU6028") or block.startswith("Group G15"):
            p = doc.add_paragraph()
            r = p.add_run(re.sub(r"[*]", "", block))
            r.font.size = Pt(10)
            p.paragraph_format.space_after = Pt(2)
            continue
        if block.startswith("Repository:"):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(10)
            r = p.add_run(re.sub(r"[*`]", "", block))
            r.font.size = Pt(9)
            continue
        if block.startswith("---"):
            continue
        if block.startswith("## "):
            heading = block[3:].strip()
            if heading.startswith("Figure captions"):
                flush_figures(doc, captions)
                break
            # figures sit at the END of the section that refers to them
            flush_figures(doc, captions)
            h = doc.add_paragraph()
            hr = h.add_run(heading)
            hr.bold = True
            hr.font.size = Pt(12)
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            global _SECTION
            _SECTION = next((k for k in FIGURES if heading.startswith(k)), None)
            continue
        if re.match(r"^\d+\.\s", block):
            add_paragraph(doc, re.sub(r"^\d+\.\s+", "", block), style="List Number")
            continue
        add_paragraph(doc, block)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print("wrote", OUT, "| captions:", sorted(captions))
    return OUT


if __name__ == "__main__":
    build()

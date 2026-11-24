"""Build the submission-ready Word report from docs/report.md.

Handles the small subset of LaTeX used in the source: subscripts, superscripts,
Greek symbols and a handful of operators.  Figures are inserted at the end of
the section that first refers to them, with numbered captions.
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
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

FIGURES = [
    ("2.", [("fig1_l1_sweep.png", 16.2)],
     "Figure 1. L1 carrier counting. (a) Correction factor C = n_band/n_F across the supplied sweep, with the C = 2 and C = 4 crossings, the exact operating point and the supplied rows. (b) The two finite-temperature counts on a logarithmic scale: they coincide at neutrality and separate as E_F rises."),
    ("3.", [("fig2_l2_model_fit.png", 9.6), ("fig3_l2_ef_trajectory.png", 14.4)],
     "Figure 2. L2 nearest-point fit in the separately normalised (R_H, R_s) plane. Points are the measured means coloured by acquisition index; the grey curve is the selected cone model. Figure 3. L2 Fermi-level trajectory against measurement index with the bootstrap 16–84 % band; the dotted line marks the R_H sign change at index 12, where the assigned E_F crosses zero."),
    ("4.", [("fig4_l3_map.png", 16.2), ("fig5_l3_method.png", 16.2)],
     "Figure 4. L3 zero-mean reconstruction. (a) The full map with the positive and negative extrema marked; the wafer-scale gradient dominates. (b) The same map after removing the fitted plane, showing the localised features. Figure 5. L3 method evidence. (a) Data misfit against regularisation, with matched maps and the noise level of the three-repeat mean. (b) Reconstructed point-spread function, FWHM 1.44 probe pitches. (c) Distribution of max|m_noise| over 500 noise-only reconstructions."),
]


def emit_math(par, src, italic=True, sub=False, sup=False):
    """Write one LaTeX fragment into a paragraph as formatted runs."""
    i, buf = 0, []

    def flush(bold_flag=None):
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
            run = par.add_run(chunk)
            # inline math inside the chunk
        run = None


def add_paragraph(doc, text, style=None):
    par = doc.add_paragraph(style=style)
    par.paragraph_format.space_after = Pt(6)
    par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for part in re.split(r"(\$[^$]+\$)", text):
        if not part:
            continue
        if part.startswith("$") and part.endswith("$"):
            emit_math(par, part[1:-1])
        else:
            emit_text(par, part)
    return par


def build():
    md = (ROOT / "docs" / "report.md").read_text(encoding="utf-8")
    lines = md.splitlines()

    # Markdown hard-wraps: join lines into blocks separated by blank lines.
    blocks, buf = [], []
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            if buf:
                blocks.append(" ".join(buf))
                buf = []
            continue
        if (line.startswith("#") or line.startswith("---")
                or line.startswith("**QXU6028") or line.startswith("Group G15")
                or line.startswith("Repository:")
                or re.match(r"^\d+\.\s", line)):
            if buf:
                blocks.append(" ".join(buf))
                buf = []
            blocks.append(line)
            continue
        buf.append(line.strip())
    if buf:
        blocks.append(" ".join(buf))

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(2.2)
        s.left_margin = s.right_margin = Cm(2.3)

    figures_done = set()
    title_done = False
    for block in blocks:
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
                break
            h = doc.add_paragraph()
            hr = h.add_run(heading)
            hr.bold = True
            hr.font.size = Pt(12)
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            for num, files, caption in FIGURES:
                if heading.startswith(num) and num not in figures_done:
                    figures_done.add(num)
                    for f, width in files:
                        pic = doc.add_paragraph()
                        pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        pic.paragraph_format.space_before = Pt(6)
                        pic.paragraph_format.space_after = Pt(2)
                        pic.add_run().add_picture(str(FIG / f), width=Cm(width))
                    cap = doc.add_paragraph()
                    cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    cr = cap.add_run(caption)
                    cr.font.size = Pt(8.5)
                    cr.italic = True
                    cap.paragraph_format.space_after = Pt(10)
            continue
        if re.match(r"^\d+\.\s", block):
            add_paragraph(doc, re.sub(r"^\d+\.\s+", "", block), style="List Number")
            continue
        add_paragraph(doc, block)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print("wrote", OUT)
    return OUT


if __name__ == "__main__":
    build()

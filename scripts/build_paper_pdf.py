# -*- coding: utf-8 -*-
"""Render the food-value-learning paper (.md) to PDF with reportlab + Sarabun.

Supports the Markdown subset used by the paper: # / ## / ### headings,
paragraphs with **bold** / `code` / *italic*, Markdown tables, bullet and
numbered lists, ![alt](path) images, fenced code blocks, and --- rules.
No Word/LibreOffice dependency (see project memory).

Usage: python scripts/build_paper_pdf.py [source.md] [out.pdf]
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, Image, ListFlowable, ListItem, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets" / "fonts"
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "reports" / "food_value_learning_paper_2026-06-19.th.md"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else SOURCE.with_suffix(".pdf")

MARGIN = 1.6 * cm
CONTENT_W = A4[0] - 2 * MARGIN
ACCENT = colors.HexColor("#1F4E79")
INK = colors.HexColor("#15212B")
MUTED = colors.HexColor("#5B6B7A")
RULE = colors.HexColor("#C3D0DD")
HEAD_FILL = colors.HexColor("#1F4E79")
ROW_FILL = colors.HexColor("#EEF3F9")
CODE_FILL = colors.HexColor("#F2F4F7")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Sarabun", str(FONT_DIR / "Sarabun-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Sarabun-Bold", str(FONT_DIR / "Sarabun-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Sarabun-Italic", str(FONT_DIR / "Sarabun-Italic.ttf")))


def styles() -> dict[str, ParagraphStyle]:
    return {
        "title": ParagraphStyle("title", fontName="Sarabun-Bold", fontSize=17, leading=22,
                                 textColor=ACCENT, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontName="Sarabun-Italic", fontSize=11, leading=15,
                                    textColor=MUTED, spaceAfter=8),
        "meta": ParagraphStyle("meta", fontName="Sarabun", fontSize=9.5, leading=14, textColor=MUTED),
        "h1": ParagraphStyle("h1", fontName="Sarabun-Bold", fontSize=14, leading=19,
                             textColor=ACCENT, spaceBefore=14, spaceAfter=5),
        "h2": ParagraphStyle("h2", fontName="Sarabun-Bold", fontSize=11.5, leading=16,
                             textColor=INK, spaceBefore=9, spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Sarabun", fontSize=10.5, leading=15.5,
                               textColor=INK, spaceAfter=6, alignment=4),
        "cap": ParagraphStyle("cap", fontName="Sarabun-Italic", fontSize=9, leading=13,
                              textColor=MUTED, spaceBefore=2, spaceAfter=10, alignment=1),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=8.3, leading=11.5,
                               textColor=INK, backColor=CODE_FILL, borderPadding=6,
                               spaceBefore=4, spaceAfter=8),
        "cell": ParagraphStyle("cell", fontName="Sarabun", fontSize=9, leading=12.5, textColor=INK),
        "cellh": ParagraphStyle("cellh", fontName="Sarabun-Bold", fontSize=9, leading=12.5,
                                textColor=colors.white),
        "li": ParagraphStyle("li", fontName="Sarabun", fontSize=10.5, leading=15, textColor=INK),
    }


_TOKEN = re.compile(r"(\*\*.+?\*\*|`.+?`|\*.+?\*)")


def inline(text: str) -> str:
    out, cur = [], 0
    for m in _TOKEN.finditer(text):
        out.append(html.escape(text[cur:m.start()]))
        tok = m.group(0)
        if tok.startswith("**"):
            out.append(f'<font name="Sarabun-Bold">{html.escape(tok[2:-2])}</font>')
        elif tok.startswith("`"):
            out.append(f'<font name="Courier" size="9">{html.escape(tok[1:-1])}</font>')
        else:
            out.append(f'<font name="Sarabun-Italic">{html.escape(tok[1:-1])}</font>')
        cur = m.end()
    out.append(html.escape(text[cur:]))
    return "".join(out)


def make_table(rows: list[list[str]], st: dict) -> Table:
    header = [Paragraph(inline(c), st["cellh"]) for c in rows[0]]
    body = [[Paragraph(inline(c), st["cell"]) for c in r] for r in rows[1:]]
    data = [header] + body
    ncol = len(rows[0])
    tbl = Table(data, colWidths=[CONTENT_W / ncol] * ncol, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_FILL),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ROW_FILL))
    tbl.setStyle(TableStyle(style))
    return tbl


def image_flowable(path: Path) -> Image:
    iw, ih = ImageReader(str(path)).getSize()
    w = min(CONTENT_W, 15.5 * cm)
    return Image(str(path), width=w, height=w * ih / iw)


def build() -> None:
    register_fonts()
    st = styles()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story: list = []
    i, n = 0, len(lines)
    first_h1 = True

    def add_para(buf: list[str]):
        if buf:
            story.append(Paragraph(inline(" ".join(buf)), st["body"]))
            buf.clear()

    para_buf: list[str] = []
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # fenced code block
        if stripped.startswith("```"):
            add_para(para_buf)
            i += 1
            code: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            esc = "<br/>".join(html.escape(c).replace(" ", "&nbsp;") for c in code)
            story.append(Paragraph(esc, st["code"]))
            continue

        # image
        m = re.match(r"!\[.*?\]\((.+?)\)", stripped)
        if m:
            add_para(para_buf)
            img = (SOURCE.parent / m.group(1)).resolve()
            if img.exists():
                story.append(image_flowable(img))
            i += 1
            continue

        # table block
        if stripped.startswith("|") and i + 1 < n and set(lines[i + 1].strip()) <= set("|-: "):
            add_para(para_buf)
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if set("".join(cells)) <= set("-: "):
                    i += 1; continue
                rows.append(cells); i += 1
            if rows:
                story.append(make_table(rows, st))
                story.append(Spacer(1, 6))
            continue

        # list block
        if re.match(r"^(\-|\d+\.)\s+", stripped):
            add_para(para_buf)
            items, numbered = [], bool(re.match(r"^\d+\.", stripped))
            while i < n and re.match(r"^(\-|\d+\.)\s+", lines[i].strip()):
                txt = re.sub(r"^(\-|\d+\.)\s+", "", lines[i].strip())
                items.append(ListItem(Paragraph(inline(txt), st["li"]), leftIndent=12))
                i += 1
            story.append(ListFlowable(items, bulletType="1" if numbered else "bullet",
                                      bulletColor=ACCENT, leftIndent=14, spaceAfter=6))
            continue

        # headings
        if stripped.startswith("### "):
            add_para(para_buf); story.append(Paragraph(inline(stripped[4:]), st["h2"])); i += 1; continue
        if stripped.startswith("## "):
            add_para(para_buf); story.append(Paragraph(inline(stripped[3:]), st["h1"])); i += 1; continue
        if stripped.startswith("# "):
            add_para(para_buf); story.append(Paragraph(inline(stripped[2:]), st["title"]))
            i += 1; continue

        # horizontal rule
        if stripped == "---":
            add_para(para_buf)
            story.append(Spacer(1, 2))
            story.append(HRFlowable(width="100%", thickness=0.6, color=RULE, spaceBefore=2, spaceAfter=6))
            i += 1; continue

        # blank line -> flush paragraph
        if not stripped:
            add_para(para_buf); i += 1; continue

        # caption (รูปที่ / **รูปที่)
        if stripped.startswith("**รูปที่") or stripped.lower().startswith("**fig"):
            add_para(para_buf)
            story.append(Paragraph(inline(stripped), st["cap"])); i += 1; continue

        # subtitle (bold-only line near top) / meta lines
        if first_h1 and stripped.startswith("**") and stripped.endswith("**"):
            story.append(Paragraph(inline(stripped), st["subtitle"])); i += 1; continue
        if first_h1 and ("：" in stripped or ": " in stripped) and not stripped.startswith("|"):
            story.append(Paragraph(inline(stripped), st["meta"])); i += 1; continue

        # normal paragraph text
        if stripped.startswith("## ") is False:
            para_buf.append(stripped)
            # once we hit real body, stop treating as frontmatter
            if stripped.startswith("##"):
                first_h1 = False
        i += 1

    add_para(para_buf)

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                            title="Food-value learning paper", author="Chisanupong")

    def furniture(canvas, d):
        canvas.saveState()
        canvas.setFont("Sarabun", 8)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(A4[0] - MARGIN, 1.0 * cm, f"{d.page}")
        canvas.drawString(MARGIN, 1.0 * cm, "Artificial Evolution · TURC2026")
        canvas.restoreState()

    doc.build(story, onFirstPage=furniture, onLaterPages=furniture)
    print(f"wrote {OUT}  ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()

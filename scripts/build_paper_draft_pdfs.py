from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
DRAFT_DIR = ROOT / "reports" / "paper_draft_2026-05-11"
FONT_REGULAR = "Tahoma"
FONT_BOLD = "Tahoma-Bold"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, r"C:\Windows\Fonts\tahoma.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, r"C:\Windows\Fonts\tahomabd.ttf"))


def make_styles() -> StyleSheet1:
    sheet = StyleSheet1()
    sheet.add(
        ParagraphStyle(
            name="Title",
            fontName=FONT_BOLD,
            fontSize=20,
            leading=26,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#16324f"),
            spaceAfter=10,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="H1",
            fontName=FONT_BOLD,
            fontSize=14,
            leading=18,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#1f4e79"),
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="H2",
            fontName=FONT_BOLD,
            fontSize=11,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#2f5d7c"),
            spaceBefore=6,
            spaceAfter=4,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Body",
            fontName=FONT_REGULAR,
            fontSize=9.5,
            leading=13,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#1f2933"),
            spaceAfter=4,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Bullet",
            fontName=FONT_REGULAR,
            fontSize=9.5,
            leading=13,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#1f2933"),
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=3,
        )
    )
    return sheet


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(colors.HexColor("#52606d"))
    canvas.drawString(18 * mm, 10 * mm, "Artificial Evolution Paper Draft")
    canvas.drawRightString(doc.pagesize[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def markdown_to_story(path: Path, title_override: str | None = None) -> list:
    sheet = make_styles()
    story: list = [Spacer(1, 12 * mm)]
    lines = path.read_text(encoding="utf-8").splitlines()
    title_added = False

    for raw in lines:
        line = raw.rstrip()
        if not line:
            story.append(Spacer(1, 2 * mm))
            continue
        if line.startswith("# "):
            text = title_override or line[2:].strip()
            if not title_added:
                story.append(p(text, sheet["Title"]))
                title_added = True
            else:
                story.append(p(text, sheet["H1"]))
            continue
        if line.startswith("## "):
            story.append(p(line[3:].strip(), sheet["H1"]))
            continue
        if line.startswith("### "):
            story.append(p(line[4:].strip(), sheet["H2"]))
            continue
        if line.startswith("- "):
            story.append(p(f"• {line[2:].strip()}", sheet["Bullet"]))
            continue
        if raw[:3].isdigit() and raw[1:3] == ". ":
            story.append(p(line, sheet["Bullet"]))
            continue
        story.append(p(line, sheet["Body"]))
    return story


def build_pdf(source: Path, destination: Path, title_override: str | None = None) -> None:
    doc = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=title_override or source.stem,
        author="OpenAI Codex",
    )
    doc.build(markdown_to_story(source, title_override=title_override), onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    register_fonts()
    outputs = [
        (DRAFT_DIR / "paper_summary_en.md", DRAFT_DIR / "paper_summary_en.pdf", "Artificial Evolution Paper Summary Draft"),
        (DRAFT_DIR / "paper_summary_th.md", DRAFT_DIR / "paper_summary_th.pdf", "ร่างสรุปสำหรับเขียน Paper"),
        (DRAFT_DIR / "evidence_index.md", DRAFT_DIR / "evidence_index.pdf", "Evidence Index"),
    ]
    for source, destination, title in outputs:
        build_pdf(source, destination, title_override=title)
        print(destination)


if __name__ == "__main__":
    main()

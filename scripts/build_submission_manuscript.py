# -*- coding: utf-8 -*-
"""Build a journal-review manuscript PDF with vector figure pages.

The source of scientific prose remains manuscript_v0.en.md. This formatter
creates a Letter-size, single-column, double-spaced PDF for author review. Each
publication figure is merged from its PDF master, preserving vector content.
"""
from __future__ import annotations

import html
import io
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = ROOT / "reports/publication_value_of_information_2026-09-13"
SOURCE = PUBLICATION / "manuscript_v0.en.md"
OUTPUT_DIR = PUBLICATION / "submission"
TEXT_PDF = OUTPUT_DIR / ".manuscript_text.tmp.pdf"
OUTPUT = OUTPUT_DIR / "manuscript_initial_submission_draft.pdf"

FIGURES = (
    PUBLICATION / "confirmatory/figures/figure_2_information_rescue.pdf",
    PUBLICATION / "confirmatory/figures/figure_e6_energy_gradient.pdf",
    PUBLICATION / "confirmatory/figures/figure_1_hidden_toxicity.pdf",
    PUBLICATION / "confirmatory/figures/figure_t2rb_replication.pdf",
    PUBLICATION / "confirmatory/figures/figure_3_selection_and_denominator.pdf",
)

FIGURE_INSERT_BEFORE = {
    "### 3.2 Primary survival contrast: B2 did not outperform the sham": 1,
    "### 3.3 Energy 10 coincided with a policy-regime change and senescence ceiling": 2,
    "### 3.6 High-drain replication (T2-RB): deficit under constant-payoff controls": 3,
    "### 3.7 Prediction and deviation audit": 4,
    "## 4. Discussion": 5,
}

FONT_REGULAR = "TimesNewRoman"
FONT_BOLD = "TimesNewRoman-Bold"
FONT_ITALIC = "TimesNewRoman-Italic"
FONT_BOLD_ITALIC = "TimesNewRoman-BoldItalic"
MARGIN = 1.0 * inch
CONTENT_WIDTH = LETTER[0] - 2 * MARGIN
TOKEN = re.compile(r"(\*\*.+?\*\*|`.+?`|\*.+?\*|<sub>[^<]+</sub>)")
AUTHOR_NAME = "Chisanupong Injun"
AUTHOR_AFFILIATION = "Deebuk Phangnga Wittayayon School"
AUTHOR_POSTAL_ADDRESS = "Phang Nga 82000, Thailand"
AUTHOR_EMAIL = "chisanupong.injun@gmail.com"
AUTHOR_ORCID = "https://orcid.org/0009-0000-2979-1916"


def register_fonts() -> None:
    fonts = Path(r"C:\Windows\Fonts")
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(fonts / "times.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, str(fonts / "timesbd.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_ITALIC, str(fonts / "timesi.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_BOLD_ITALIC, str(fonts / "timesbi.ttf")))
    pdfmetrics.registerFontFamily(
        FONT_REGULAR,
        normal=FONT_REGULAR,
        bold=FONT_BOLD,
        italic=FONT_ITALIC,
        boldItalic=FONT_BOLD_ITALIC,
    )


def inline(text: str) -> str:
    output: list[str] = []
    cursor = 0
    for match in TOKEN.finditer(text):
        output.append(html.escape(text[cursor : match.start()]))
        token = match.group(0)
        if token.startswith("**"):
            output.append(f"<b>{html.escape(token[2:-2])}</b>")
        elif token.startswith("`"):
            output.append(f'<font name="Courier" size="10.5">{html.escape(token[1:-1])}</font>')
        elif token.startswith("<sub>"):
            output.append(f"<sub>{html.escape(token[5:-6])}</sub>")
        else:
            output.append(f"<i>{html.escape(token[1:-1])}</i>")
        cursor = match.end()
    output.append(html.escape(text[cursor:]))
    return "".join(output)


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "SubmissionTitle",
            parent=base["Title"],
            fontName=FONT_BOLD,
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor="#000000",
            spaceAfter=18,
        ),
        "meta": ParagraphStyle(
            "SubmissionMeta",
            parent=base["Normal"],
            fontName=FONT_REGULAR,
            fontSize=12,
            leading=24,
            alignment=TA_CENTER,
            textColor="#000000",
            spaceAfter=2,
        ),
        "h1": ParagraphStyle(
            "SubmissionH1",
            parent=base["Heading1"],
            fontName=FONT_BOLD,
            fontSize=13,
            leading=24,
            textColor="#000000",
            spaceBefore=18,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "SubmissionH2",
            parent=base["Heading2"],
            fontName=FONT_BOLD,
            fontSize=12,
            leading=24,
            textColor="#000000",
            spaceBefore=12,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "SubmissionBody",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=12,
            leading=24,
            alignment=TA_LEFT,
            textColor="#000000",
            spaceAfter=8,
            allowWidows=0,
            allowOrphans=0,
        ),
        "keywords": ParagraphStyle(
            "SubmissionKeywords",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=12,
            leading=24,
            textColor="#000000",
            spaceBefore=4,
            spaceAfter=10,
        ),
        "list": ParagraphStyle(
            "SubmissionList",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=12,
            leading=24,
            textColor="#000000",
            leftIndent=0,
            spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "SubmissionCaption",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=10.5,
            leading=14,
            textColor="#000000",
            alignment=TA_LEFT,
        ),
        "table": ParagraphStyle(
            "SubmissionTable",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=10.5,
            textColor="#000000",
            alignment=TA_LEFT,
        ),
        "figure_marker": ParagraphStyle(
            "VectorFigurePageMarker",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=1,
            leading=1,
            textColor=colors.white,
        ),
    }


def parse_source() -> tuple[str, list[str], list[str]]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("manuscript source must start with one H1 title")
    title = lines[0][2:].strip()
    try:
        figure_index = lines.index("## Figure captions")
    except ValueError as exc:
        raise ValueError("missing Figure captions section") from exc
    body = lines[1:figure_index]
    captions = [line.strip() for line in lines[figure_index + 1 :] if line.strip()]
    if len(captions) != len(FIGURES):
        raise ValueError(f"expected {len(FIGURES)} figure captions, found {len(captions)}")
    return title, body, captions


def page_furniture(pdf_canvas: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    pdf_canvas.saveState()
    pdf_canvas.setFont(FONT_REGULAR, 9)
    pdf_canvas.drawCentredString(LETTER[0] / 2, 0.55 * inch, str(doc.page))
    pdf_canvas.restoreState()


def build_text_pdf(title: str, lines: list[str], styles: dict[str, ParagraphStyle]) -> None:
    story: list[object] = [Spacer(1, 0.3 * inch), Paragraph(inline(title), styles["title"])]
    for value in (
        "Article",
        AUTHOR_NAME,
        AUTHOR_AFFILIATION,
        AUTHOR_POSTAL_ADDRESS,
        f"Corresponding author: {AUTHOR_NAME}; {AUTHOR_EMAIL}",
        f"ORCID: {AUTHOR_ORCID}",
    ):
        story.append(Paragraph(inline(value), styles["meta"]))
    story.append(Spacer(1, 0.18 * inch))

    paragraph: list[str] = []
    index = 0

    def flush() -> None:
        if paragraph:
            text = " ".join(paragraph)
            if text.startswith("**Keywords:"):
                style = styles["keywords"]
            elif text.startswith("**Table 1."):
                style = ParagraphStyle(
                    "Table1Caption",
                    parent=styles["body"],
                    keepWithNext=True,
                )
            else:
                style = styles["body"]
            story.append(Paragraph(inline(text), style))
            paragraph.clear()

    while index < len(lines):
        stripped = lines[index].strip()
        # Working-draft front matter is matched by prefix: an exact-string match
        # silently stopped filtering once the Target journal note was reworded.
        if stripped.startswith((
            "**Manuscript type:**",
            "**Target journal:**",
            "**Author:**",
            "**Affiliation:**",
            "**Postal address:**",
            "**Corresponding author:**",
            "**ORCID:**",
            "**Status:**",
        )):
            index += 1
            continue
        if not stripped:
            flush()
            index += 1
            continue
        figure_number = FIGURE_INSERT_BEFORE.get(stripped)
        if figure_number is not None:
            flush()
            story.extend([
                PageBreak(),
                Paragraph(f"VECTOR_FIGURE_PAGE_{figure_number}", styles["figure_marker"]),
                PageBreak(),
            ])
        if stripped.startswith("#### "):
            flush()
            story.append(Paragraph(inline(stripped[5:]), styles["h2"]))
            index += 1
            continue
        if stripped.startswith("### "):
            flush()
            story.append(Paragraph(inline(stripped[4:]), styles["h2"]))
            index += 1
            continue
        if stripped.startswith("## "):
            flush()
            story.append(Paragraph(inline(stripped[3:]), styles["h1"]))
            index += 1
            continue
        if re.match(r"^(?:-|\d+\.)\s+", stripped):
            flush()
            numbered = bool(re.match(r"^\d+\.", stripped))
            items = []
            while index < len(lines) and re.match(r"^(?:-|\d+\.)\s+", lines[index].strip()):
                item = re.sub(r"^(?:-|\d+\.)\s+", "", lines[index].strip())
                items.append(ListItem(Paragraph(inline(item), styles["list"]), leftIndent=18))
                index += 1
            list_options = {
                "bulletType": "1" if numbered else "bullet",
                "leftIndent": 22,
                "bulletFontName": FONT_REGULAR,
                "bulletFontSize": 12,
                "spaceAfter": 8,
            }
            if numbered:
                list_options["start"] = "1"
            else:
                list_options["bulletChar"] = "•"
            story.append(ListFlowable(items, **list_options))
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            flush()
            rows: list[list[str]] = []
            while index < len(lines):
                table_line = lines[index].strip()
                if not (table_line.startswith("|") and table_line.endswith("|")):
                    break
                cells = [cell.strip() for cell in table_line.strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    rows.append(cells)
                index += 1
            if not rows:
                raise ValueError("empty Markdown table")
            if any(len(row) != len(rows[0]) for row in rows):
                raise ValueError("Markdown table rows have inconsistent column counts")
            is_e6_table = rows[0] == [
                "Energy", "B1 mean", "B2 mean", "B3 mean",
                "Primary B2-B3 [95% CI]", "Secondary B2-B1 [95% CI]",
            ]
            if is_e6_table:
                proportions = (0.08, 0.11, 0.11, 0.11, 0.295, 0.295)
                col_widths = [CONTENT_WIDTH * value for value in proportions]
            else:
                width = CONTENT_WIDTH / len(rows[0])
                col_widths = [width] * len(rows[0])
            is_t2_table = rows[0][0] == "Arm" and len(rows[0]) == 11
            if is_t2_table:
                proportions = (0.075, 0.10, 0.09, 0.10, 0.09, 0.10, 0.09, 0.10, 0.09, 0.08, 0.085)
                col_widths = [CONTENT_WIDTH * value for value in proportions]
            cell_style = styles["table"]
            if is_t2_table:
                cell_style = ParagraphStyle(
                    "T2Table",
                    parent=styles["table"],
                    fontSize=8,
                    leading=9.5,
                )
            rendered = [
                [Paragraph(inline(cell), cell_style) for cell in row]
                for row in rows
            ]
            table = Table(
                rendered,
                colWidths=col_widths,
                repeatRows=1,
                splitByRow=0 if is_e6_table else 1,
            )
            table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#777777")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(table)
            story.append(Spacer(1, 8))
            continue
        paragraph.append(stripped)
        index += 1
    flush()
    document = SimpleDocTemplate(
        str(TEXT_PDF),
        pagesize=LETTER,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.85 * inch,
        bottomMargin=0.8 * inch,
        title=title,
        author=AUTHOR_NAME,
        subject="Initial submission manuscript for Artificial Life",
    )
    document.build(story, onFirstPage=page_furniture, onLaterPages=page_furniture)


def figure_overlay(
    caption: str,
    styles: dict[str, ParagraphStyle],
    page_number: int,
    caption_top: float,
) -> PdfReader:
    buffer = io.BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=LETTER)
    caption_flowable = Paragraph(inline(caption), styles["caption"])
    _, height = caption_flowable.wrap(CONTENT_WIDTH, 2.0 * inch)
    caption_flowable.drawOn(pdf_canvas, MARGIN, caption_top - height)
    pdf_canvas.setFont(FONT_REGULAR, 9)
    pdf_canvas.drawCentredString(LETTER[0] / 2, 0.55 * inch, str(page_number))
    pdf_canvas.save()
    buffer.seek(0)
    return PdfReader(buffer)


def place_vector_figures(
    text_pdf: Path, output: Path, captions: list[str], styles: dict[str, ParagraphStyle]
) -> None:
    text_reader = PdfReader(str(text_pdf))
    writer = PdfWriter()
    marker_pages: dict[int, int] = {}
    for page_index, page in enumerate(text_reader.pages):
        text = page.extract_text() or ""
        match = re.search(r"VECTOR_FIGURE_PAGE_(\d+)", text)
        if match:
            figure_number = int(match.group(1))
            if figure_number in marker_pages:
                raise ValueError(f"duplicate vector figure marker: {figure_number}")
            marker_pages[figure_number] = page_index
    expected = set(range(1, len(FIGURES) + 1))
    if set(marker_pages) != expected:
        raise ValueError(
            f"vector figure markers mismatch: expected {sorted(expected)}, found {sorted(marker_pages)}"
        )

    figures_by_page = {page_index: figure_number for figure_number, page_index in marker_pages.items()}
    for page_index, text_page in enumerate(text_reader.pages):
        figure_number = figures_by_page.get(page_index)
        if figure_number is None:
            writer.add_page(text_page)
            continue
        figure_path = FIGURES[figure_number - 1]
        caption = captions[figure_number - 1]
        figure_reader = PdfReader(str(figure_path))
        if len(figure_reader.pages) != 1:
            raise ValueError(f"figure master must have one page: {figure_path}")
        source_page = figure_reader.pages[0]
        source_width = float(source_page.mediabox.width)
        source_height = float(source_page.mediabox.height)
        available_height = 5.6 * inch
        scale = min(CONTENT_WIDTH / source_width, available_height / source_height)
        width = source_width * scale
        height = source_height * scale
        x = (LETTER[0] - width) / 2
        y = LETTER[1] - 1.0 * inch - height
        # Replace the marker page instead of merging onto it so the internal
        # marker never survives in searchable or copied manuscript text.
        target_page = writer.add_blank_page(width=LETTER[0], height=LETTER[1])
        overlay = figure_overlay(caption, styles, page_index + 1, y - 14).pages[0]
        target_page.merge_page(overlay, over=True)
        target_page.merge_transformed_page(
            source_page,
            Transformation().scale(scale).translate(x, y),
            over=True,
        )
    with output.open("wb") as handle:
        writer.write(handle)


def main() -> int:
    register_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for figure in FIGURES:
        if not figure.is_file():
            raise FileNotFoundError(figure)
    title, lines, captions = parse_source()
    style_map = make_styles()
    build_text_pdf(title, lines, style_map)
    place_vector_figures(TEXT_PDF, OUTPUT, captions, style_map)
    TEXT_PDF.unlink()
    reader = PdfReader(str(OUTPUT))
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes, {len(reader.pages)} pages, 5 vector figure pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

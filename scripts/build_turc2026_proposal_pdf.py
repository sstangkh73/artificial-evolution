from __future__ import annotations

import html
import re
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
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
SOURCE = ROOT / "reports" / "proposal" / "TURC2026_Concept_Proposal_Chisanuong_Injun.md"
OUT = ROOT / "reports" / "proposal" / "TURC2026_Concept_Proposal_Chisanuong_Injun.pdf"
FONT_DIR = ROOT / "assets" / "fonts"

CONTENT_WIDTH = A4[0] - (1.45 * cm * 2)
ACCENT = colors.HexColor("#1F4E79")
INK = colors.HexColor("#111827")
MUTED = colors.HexColor("#64748B")
RULE = colors.HexColor("#CBD5E1")
FILL = colors.HexColor("#F4F7FB")
FILL_2 = colors.HexColor("#EAF1F8")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Sarabun", str(FONT_DIR / "Sarabun-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Sarabun-Bold", str(FONT_DIR / "Sarabun-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Sarabun-Italic", str(FONT_DIR / "Sarabun-Italic.ttf")))


def inline_markup(text: str) -> str:
    pattern = re.compile(r"(\*\*.+?\*\*|`.+?`)")
    chunks: list[str] = []
    cursor = 0
    for match in pattern.finditer(text):
        chunks.append(html.escape(text[cursor : match.start()]))
        token = match.group(0)
        value = html.escape(token[2:-2] if token.startswith("**") else token[1:-1])
        chunks.append(f'<font name="Sarabun-Bold">{value}</font>')
        cursor = match.end()
    chunks.append(html.escape(text[cursor:]))
    return "".join(chunks)


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(inline_markup(text), style)


def para_lines(lines: list[str], style: ParagraphStyle) -> Paragraph:
    return Paragraph("<br/>".join(inline_markup(line) for line in lines), style)


def rich_para(markup: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(markup, style)


def spacer(height: float = 4) -> Spacer:
    return Spacer(1, height)


def register_styles() -> dict[str, ParagraphStyle]:
    return {
        "kicker": ParagraphStyle(
            "kicker",
            fontName="Sarabun-Bold",
            fontSize=12.5,
            leading=15,
            alignment=TA_CENTER,
            textColor=MUTED,
            spaceAfter=3,
            wordWrap="CJK",
        ),
        "title": ParagraphStyle(
            "title",
            fontName="Sarabun-Bold",
            fontSize=18.4,
            leading=22.8,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4,
            wordWrap="CJK",
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Sarabun",
            fontSize=12.6,
            leading=15.8,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334155"),
            spaceAfter=2,
            wordWrap="CJK",
        ),
        "meta": ParagraphStyle(
            "meta",
            fontName="Sarabun",
            fontSize=13.2,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334155"),
            spaceAfter=2,
            wordWrap="CJK",
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName="Sarabun-Bold",
            fontSize=17.0,
            leading=21,
            textColor=ACCENT,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
            wordWrap="CJK",
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Sarabun-Bold",
            fontSize=15.5,
            leading=19,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=6,
            spaceAfter=2.5,
            keepWithNext=True,
            wordWrap="CJK",
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Sarabun",
            fontSize=15.6,
            leading=20.1,
            alignment=TA_LEFT,
            textColor=INK,
            spaceAfter=5.2,
            wordWrap="CJK",
        ),
        "body_tight": ParagraphStyle(
            "body_tight",
            fontName="Sarabun",
            fontSize=15.0,
            leading=18.8,
            alignment=TA_LEFT,
            textColor=INK,
            spaceAfter=2.5,
            wordWrap="CJK",
        ),
        "callout": ParagraphStyle(
            "callout",
            fontName="Sarabun",
            fontSize=14.2,
            leading=18.2,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#0F172A"),
            wordWrap="CJK",
        ),
        "table": ParagraphStyle(
            "table",
            fontName="Sarabun",
            fontSize=11.0,
            leading=13.6,
            alignment=TA_LEFT,
            textColor=INK,
            wordWrap="CJK",
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontName="Sarabun-Bold",
            fontSize=11.1,
            leading=13.2,
            alignment=TA_CENTER,
            textColor=colors.white,
            wordWrap="CJK",
        ),
        "var_label": ParagraphStyle(
            "var_label",
            fontName="Sarabun-Bold",
            fontSize=12.0,
            leading=13.0,
            alignment=TA_CENTER,
            textColor=colors.white,
            wordWrap="CJK",
        ),
        "var_table": ParagraphStyle(
            "var_table",
            fontName="Sarabun",
            fontSize=11.8,
            leading=13.6,
            alignment=TA_LEFT,
            textColor=INK,
            wordWrap="CJK",
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="Sarabun-Italic",
            fontSize=12.2,
            leading=15.0,
            alignment=TA_LEFT,
            textColor=MUTED,
            spaceAfter=3,
            wordWrap="CJK",
        ),
        "diagram": ParagraphStyle(
            "diagram",
            fontName="Sarabun-Bold",
            fontSize=11.8,
            leading=13.8,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
            wordWrap="CJK",
        ),
        "diagram_sub": ParagraphStyle(
            "diagram_sub",
            fontName="Sarabun",
            fontSize=10.6,
            leading=12.8,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334155"),
            wordWrap="CJK",
        ),
        "arrow": ParagraphStyle(
            "arrow",
            fontName="Sarabun-Bold",
            fontSize=9.5,
            leading=6.8,
            alignment=TA_CENTER,
            textColor=ACCENT,
            wordWrap="CJK",
        ),
    }


def add_page_furniture(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.35)
    canvas.line(1.45 * cm, height - 0.82 * cm, width - 1.45 * cm, height - 0.82 * cm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Sarabun", 9.5)
    canvas.drawString(1.45 * cm, height - 0.62 * cm, "TURC2026 Concept Proposal")
    canvas.drawRightString(width - 1.45 * cm, height - 0.62 * cm, "Artificial Life / World Discovery")
    canvas.setStrokeColor(RULE)
    canvas.line(1.45 * cm, 0.88 * cm, width - 1.45 * cm, 0.88 * cm)
    canvas.setFont("Sarabun", 10.5)
    canvas.drawCentredString(width / 2, 0.55 * cm, f"หน้า {doc.page}")
    canvas.restoreState()


def clean_name(line: str) -> str:
    match = re.match(r"ชื่อ\s+(.+?)\s+นามสกุล\s+(.+)", line)
    if not match:
        return line
    return f"{match.group(1).strip()} {match.group(2).strip()}"


def frontmatter(markdown: str) -> dict[str, str]:
    bold_lines = re.findall(r"^\*\*(.+?)\*\*$", markdown, flags=re.MULTILINE)
    category = re.search(r"^ประเภทโครงงาน:\s*(.+)$", markdown, flags=re.MULTILINE)
    keywords = re.search(r"^คำสำคัญ:\s*(.+)$", markdown, flags=re.MULTILINE)
    member_block = markdown.split("## 2) สมาชิก", 1)[1].split("---", 1)[0]
    member_lines = [line.strip() for line in member_block.splitlines() if line.strip()]
    student_idx = member_lines.index("หัวหน้าทีม")
    advisor_idx = member_lines.index("อาจารย์ที่ปรึกษา")
    return {
        "thai_title": bold_lines[0],
        "english_title": bold_lines[1],
        "category": category.group(1).strip() if category else "",
        "keywords": keywords.group(1).strip() if keywords else "",
        "student_name": clean_name(member_lines[student_idx + 1]),
        "student_level": member_lines[student_idx + 2],
        "advisor_name": clean_name(member_lines[advisor_idx + 1]),
        "advisor_school": member_lines[advisor_idx + 2],
        "advisor_affiliation": member_lines[advisor_idx + 3],
    }


def member_table(info: dict[str, str], styles: dict[str, ParagraphStyle]) -> Table:
    rows = [
        [
            para("หัวหน้าทีม", styles["h2"]),
            para_lines([info["student_name"], info["student_level"]], styles["body_tight"]),
        ],
        [
            para("อาจารย์ที่ปรึกษา", styles["h2"]),
            para_lines(
                [info["advisor_name"], info["advisor_school"], info["advisor_affiliation"]],
                styles["body_tight"],
            ),
        ],
    ]
    table = Table(rows, colWidths=[4.2 * cm, CONTENT_WIDTH - 4.2 * cm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (0, 0), (-1, 0), 0.35, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def callout_box(text: str, styles: dict[str, ParagraphStyle]) -> Table:
    table = Table([[para(text, styles["callout"])]], colWidths=[CONTENT_WIDTH])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF6FF")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#BFD7EE")),
                ("LINEBEFORE", (0, 0), (0, -1), 2.2, ACCENT),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def list_block(items: list[str], numbered: bool, styles: dict[str, ParagraphStyle]) -> ListFlowable:
    flowables = [ListItem(para(item, styles["body_tight"]), leftIndent=0) for item in items]
    return ListFlowable(
        flowables,
        bulletType="1" if numbered else "bullet",
        start="1" if numbered else "bulletchar",
        bulletFontName="Sarabun",
        bulletFontSize=14.4,
        leftIndent=22,
        bulletIndent=0,
        bulletOffsetY=0.5,
        spaceBefore=0,
        spaceAfter=6,
    )


def markdown_table(lines: list[str], styles: dict[str, ParagraphStyle]) -> Table:
    parsed: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        parsed.append(cells)

    data = []
    for row_idx, row in enumerate(parsed):
        style = styles["table_header"] if row_idx == 0 else styles["table"]
        data.append([para(cell, style) for cell in row])

    table = Table(data, colWidths=[2.45 * cm, 6.35 * cm, CONTENT_WIDTH - 8.8 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFBFC")]),
                ("BOX", (0, 0), (-1, -1), 0.55, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5.5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5.5),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ]
        )
    )
    return table


def variable_table(rows_in: list[tuple[str, list[str]]], styles: dict[str, ParagraphStyle]) -> Table:
    headers = [para(label, styles["var_label"]) for label, _items in rows_in]
    details = [
        rich_para("<br/>".join(f"• {inline_markup(item)}" for item in items), styles["var_table"])
        for _label, items in rows_in
    ]
    width = CONTENT_WIDTH / max(1, len(rows_in))
    table = Table([headers, details], colWidths=[width] * len(rows_in), hAlign="LEFT", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.55, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                ("VALIGN", (0, 1), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def concept_diagram(styles: dict[str, ParagraphStyle]) -> Table:
    steps = [
        ("โลกจำลองที่ไม่ให้ความหมายสำเร็จรูป", ""),
        ("กฎพื้นฐานของโลก", "พลังงาน พืช เมล็ด แสง น้ำ อุณหภูมิ ดิน อาหาร"),
        ("เอเจนต์ปฏิสัมพันธ์กับโลก", "เดิน กิน จำตำแหน่ง หยิบ/ปล่อยเมล็ด"),
        ("ตัวชี้วัดความรู้จากประสบการณ์", "return lift, seed causal chain, patch productivity"),
        ("การทดสอบด้วย control", "current-position, nearby, visible, random, low-food signal, world-size stress"),
        ("ข้อสรุปแบบไม่เกินหลักฐาน", "emergent ecological interaction / ยังไม่ใช่ intentional farming หรือ full technology"),
    ]
    rows = []
    box_rows = []
    for idx, (title, detail) in enumerate(steps):
        body = rich_para(
            inline_markup(title)
            if not detail
            else f'{inline_markup(title)}<br/><font name="Sarabun">{html.escape(detail)}</font>',
            styles["diagram"],
        )
        rows.append([body])
        box_rows.append(len(rows) - 1)
        if idx < len(steps) - 1:
            rows.append([para("↓", styles["arrow"])])

    table = Table(rows, colWidths=[CONTENT_WIDTH - 1.0 * cm], hAlign="CENTER")
    commands = [
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
    ]
    for offset, row_idx in enumerate(box_rows):
        commands.extend(
            [
                ("BACKGROUND", (0, row_idx), (0, row_idx), FILL_2 if offset % 2 == 0 else FILL),
                ("BOX", (0, row_idx), (0, row_idx), 0.55, colors.HexColor("#9CB7D2")),
                ("TOPPADDING", (0, row_idx), (0, row_idx), 2.5),
                ("BOTTOMPADDING", (0, row_idx), (0, row_idx), 3.2),
            ]
        )
    table.setStyle(TableStyle(commands))
    return table


def collect_list(lines: list[str], start: int, numbered: bool) -> tuple[list[str], int]:
    items: list[str] = []
    pattern = re.compile(r"^\d+\.\s+(.+)$") if numbered else re.compile(r"^-\s+(.+)$")
    idx = start
    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            lookahead = idx + 1
            while lookahead < len(lines) and not lines[lookahead].strip():
                lookahead += 1
            if lookahead < len(lines) and pattern.match(lines[lookahead].strip()):
                idx = lookahead
                continue
            break
        match = pattern.match(line)
        if not match:
            break
        items.append(match.group(1).strip())
        idx += 1
    return items, idx


def collect_variable_rows(lines: list[str], start: int) -> tuple[list[tuple[str, list[str]]], int]:
    labels = {"ตัวแปรต้น:", "ตัวแปรตาม:", "ตัวแปรควบคุม:"}
    rows: list[tuple[str, list[str]]] = []
    idx = start
    while idx < len(lines) and lines[idx].strip() in labels:
        label = lines[idx].strip().rstrip(":")
        idx += 1
        while idx < len(lines) and not lines[idx].strip():
            idx += 1
        items, idx = collect_list(lines, idx, numbered=False)
        rows.append((label, items))
        while idx < len(lines) and not lines[idx].strip():
            idx += 1
    return rows, idx


def flush_paragraph(buffer: list[str], story: list, styles: dict[str, ParagraphStyle]) -> None:
    if not buffer:
        return
    text = " ".join(part.strip() for part in buffer if part.strip())
    buffer.clear()
    if not text:
        return
    if text.startswith("**") and text.endswith("**"):
        story.append(callout_box(text[2:-2], styles))
        story.append(spacer(4))
    else:
        story.append(para(text, styles["body"]))


def add_markdown_body(body: str, story: list, styles: dict[str, ParagraphStyle]) -> None:
    lines = body.splitlines()
    idx = 0
    paragraph_buffer: list[str] = []
    while idx < len(lines):
        raw_line = lines[idx]
        line = raw_line.strip()
        if not line:
            flush_paragraph(paragraph_buffer, story, styles)
            idx += 1
            continue
        if line == "---":
            flush_paragraph(paragraph_buffer, story, styles)
            idx += 1
            continue
        if line.startswith("|"):
            flush_paragraph(paragraph_buffer, story, styles)
            table_lines: list[str] = []
            while idx < len(lines) and lines[idx].strip().startswith("|"):
                table_lines.append(lines[idx].strip())
                idx += 1
            story.append(para("ตารางสรุปหลักฐานเบื้องต้นจากการทดลองในโครงการ", styles["caption"]))
            story.append(markdown_table(table_lines, styles))
            story.append(spacer(5))
            continue
        if line.startswith("```"):
            flush_paragraph(paragraph_buffer, story, styles)
            idx += 1
            code_lines: list[str] = []
            while idx < len(lines) and not lines[idx].strip().startswith("```"):
                code_lines.append(lines[idx])
                idx += 1
            idx += 1
            story.append(KeepTogether([concept_diagram(styles), spacer(4)]))
            continue
        if re.match(r"^\d+\.\s+", line):
            flush_paragraph(paragraph_buffer, story, styles)
            items, idx = collect_list(lines, idx, numbered=True)
            story.append(list_block(items, True, styles))
            continue
        if line.startswith("- "):
            flush_paragraph(paragraph_buffer, story, styles)
            items, idx = collect_list(lines, idx, numbered=False)
            story.append(list_block(items, False, styles))
            continue
        if line in {"ตัวแปรต้น:", "ตัวแปรตาม:", "ตัวแปรควบคุม:"}:
            flush_paragraph(paragraph_buffer, story, styles)
            rows, idx = collect_variable_rows(lines, idx)
            story.append(PageBreak())
            story.append(para("ตัวแปรในการวิจัย", styles["h2"]))
            story.append(variable_table(rows, styles))
            story.append(spacer(8))
            continue
        if line.endswith(":") and len(line) <= 70:
            flush_paragraph(paragraph_buffer, story, styles)
            story.append(para(line, styles["h2"]))
            idx += 1
            continue
        paragraph_buffer.append(line)
        idx += 1
    flush_paragraph(paragraph_buffer, story, styles)


def section_bodies(markdown: str) -> list[tuple[str, str]]:
    chunks = re.split(r"^##\s+", markdown, flags=re.MULTILINE)
    sections: list[tuple[str, str]] = []
    for chunk in chunks[1:]:
        title, _, body = chunk.partition("\n")
        sections.append((title.strip(), body.strip()))
    return sections


def build() -> None:
    register_fonts()
    styles = register_styles()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    markdown = SOURCE.read_text(encoding="utf-8")
    info = frontmatter(markdown)

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=1.45 * cm,
        rightMargin=1.45 * cm,
        topMargin=1.05 * cm,
        bottomMargin=1.05 * cm,
        title="TURC2026 Concept Proposal",
        author=info["student_name"],
        subject="Experience-Based Knowledge Emergence in Artificial Agents",
    )

    story: list = []
    story.append(para("Concept Proposal | Triam Udom Research Challenge 2026", styles["kicker"]))
    story.append(spacer(2))
    story.append(para("1) ชื่อโครงงาน", styles["h1"]))
    story.append(
        para_lines(
            [
                "การศึกษาการเกิดความรู้จากประสบการณ์",
                "ของเอเจนต์ปัญญาประดิษฐ์ในโลกจำลอง",
                "ที่ไม่ให้ความรู้ล่วงหน้า",
            ],
            styles["title"],
        )
    )
    story.append(para(info["english_title"], styles["subtitle"]))
    story.append(para(f'ประเภทโครงงาน: {info["category"]}', styles["meta"]))
    story.append(para(f'คำสำคัญ: {info["keywords"]}', styles["meta"]))
    story.append(spacer(6))

    story.append(para("2) สมาชิก", styles["h1"]))
    story.append(member_table(info, styles))
    story.append(spacer(5))

    for title, body in section_bodies(markdown):
        if title.startswith(("1)", "2)")):
            continue
        if title.startswith(("4)", "6)")):
            story.append(PageBreak())
        story.append(para(title, styles["h1"]))
        add_markdown_body(body, story, styles)

    doc.build(story, onFirstPage=add_page_furniture, onLaterPages=add_page_furniture)
    reader = PdfReader(str(OUT))
    pages = len(reader.pages)
    if pages > 5:
        raise SystemExit(f"PDF exceeds TURC proposal requirement: {pages} pages")
    print(f"Wrote {OUT} ({pages} pages)")


if __name__ == "__main__":
    build()

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
DRAFT_DIR = ROOT / "reports" / "paper_draft_2026-05-11"
FONT_REGULAR = "Tahoma"
FONT_BOLD = "Tahoma-Bold"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, r"C:\Windows\Fonts\tahoma.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, r"C:\Windows\Fonts\tahomabd.ttf"))


def styles() -> StyleSheet1:
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
            name="Body",
            fontName=FONT_REGULAR,
            fontSize=9.6,
            leading=13.8,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#1f2933"),
            spaceAfter=5,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Bullet",
            fontName=FONT_REGULAR,
            fontSize=9.6,
            leading=13.8,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#1f2933"),
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=4,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Caption",
            fontName=FONT_REGULAR,
            fontSize=8.8,
            leading=11.2,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#52606d"),
            spaceAfter=8,
        )
    )
    return sheet


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(colors.HexColor("#52606d"))
    canvas.drawString(18 * mm, 10 * mm, "Artificial Evolution Full Manuscript Draft")
    canvas.drawRightString(doc.pagesize[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def add_markdown_story(story: list, path: Path, sheet: StyleSheet1) -> None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line:
            story.append(Spacer(1, 2 * mm))
            continue
        if line.startswith("# "):
            story.append(p(line[2:].strip(), sheet["Title"]))
            continue
        if line.startswith("## "):
            story.append(p(line[3:].strip(), sheet["H1"]))
            continue
        if line.startswith("- "):
            story.append(p(f"• {line[2:].strip()}", sheet["Bullet"]))
            continue
        if raw[:3].isdigit() and raw[1:3] == ". ":
            story.append(p(line, sheet["Bullet"]))
            continue
        story.append(p(line, sheet["Body"]))


def add_figure(story: list, image_path: Path, caption: str, width_mm: float = 165) -> None:
    width = width_mm * mm
    img = Image(str(image_path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = width
    img.drawHeight = width * ratio
    story.append(Spacer(1, 2 * mm))
    story.append(img)
    story.append(Spacer(1, 1 * mm))
    story.append(p(caption, STYLES["Caption"]))
    story.append(Spacer(1, 2 * mm))


register_fonts()
STYLES = styles()


def main() -> None:
    output = DRAFT_DIR / "manuscript_full_th_with_figures.pdf"
    story: list = [Spacer(1, 10 * mm)]
    add_markdown_story(story, DRAFT_DIR / "manuscript_full_th.md", STYLES)

    story.append(PageBreak())
    story.append(p("ภาคผนวกภาพและกราฟจากผลการทดลองปัจจุบัน", STYLES["H1"]))
    story.append(
        p(
            "ภาพต่อไปนี้สร้างจาก publication packages และ robustness packages ล่าสุดของโปรเจกต์ เพื่อแสดงทั้งแนวโน้มประชากร ความน่าจะเป็นการรอด การเกิดเทคโนโลยี และผลเชิงสถิติในระดับเงื่อนไขการทดลอง",
            STYLES["Body"],
        )
    )

    main_fig_dir = ROOT / "data" / "publication_packages" / "experiment_047_publication_batch" / "figures"
    robust_fig_dir = ROOT / "data" / "publication_packages" / "experiment_048_robustness_sweep" / "figures"

    add_figure(
        story,
        main_fig_dir / "figure_2_population_trajectories.png",
        "Figure 1. Population trajectories across the main publication batch. เส้นประชากรแสดงว่ากลุ่ม sexed conditions มีระดับประชากรสูงกว่า baseline อย่างชัดเจน แต่ยังมีการลดลงในหลาย replicate จนสูญพันธุ์ในที่สุด",
    )
    add_figure(
        story,
        main_fig_dir / "figure_3_survival_curves.png",
        "Figure 2. Survival curves across the main publication batch. ภาพนี้เน้นความต่างระหว่าง baseline conditions ที่ล่มทั้งหมด กับ sexed conditions ที่เริ่มมีส่วนหนึ่งของ replicate ผ่านไปได้ไกลกว่าเดิม",
    )
    add_figure(
        story,
        main_fig_dir / "figure_8_condition_statistics.png",
        "Figure 3. Condition-level statistics for the main publication batch. สถิติสรุปชี้ว่า `sexed_gen3_body_8` ให้ gen3 success สูงที่สุดในชุดหลัก แต่ก็ยังไม่ถึงระดับ robust outcome",
    )
    add_figure(
        story,
        robust_fig_dir / "figure_5_technology_emergence.png",
        "Figure 4. Technology emergence under robustness conditions. เมื่อโลกถูกทำให้โหดขึ้น first-technology tick ถูกผลักให้ช้าลงอย่างมีนัยสำคัญ และบาง replicate ไม่เกิด technology ภายในช่วงรัน",
    )
    add_figure(
        story,
        robust_fig_dir / "figure_6_failure_reasons.png",
        "Figure 5. Reproduction failure reasons across robustness conditions. ปัจจัยบล็อกการส่งต่อข้ามรุ่นยังคงเกี่ยวข้องกับพลังงาน การอยู่ใกล้รัง และข้อจำกัดด้าน household resources",
    )
    add_figure(
        story,
        robust_fig_dir / "figure_8_condition_statistics.png",
        "Figure 6. Condition-level statistics for the robustness sweep. ผลนี้ยืนยันว่าการกดอาหารลงทำให้ gen3 success ลดลง และการกด frontier cost ช่วยชะลอ technology emergence ได้ แต่ยังไม่ทำให้เกิด delayed innovation ในระดับที่แข็งพอ",
    )

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Artificial Evolution Full Manuscript Draft",
        author="OpenAI Codex",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    main()

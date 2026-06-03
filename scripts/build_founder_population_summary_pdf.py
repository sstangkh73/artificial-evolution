from __future__ import annotations

import json
from pathlib import Path

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "reports" / "founder_population_stage_2026-05-11"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

FONT_REGULAR = "Tahoma"
FONT_BOLD = "Tahoma-Bold"
OUTPUT_PDF = REPORT_DIR / "founder_population_stage_summary_2026-05-11.pdf"


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
            leading=25,
            textColor=colors.HexColor("#16324f"),
            alignment=TA_CENTER,
            spaceAfter=7,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Subtitle",
            fontName=FONT_REGULAR,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#52606d"),
            alignment=TA_CENTER,
            spaceAfter=14,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Section",
            fontName=FONT_BOLD,
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1e4a72"),
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Body",
            fontName=FONT_REGULAR,
            fontSize=9.3,
            leading=13,
            textColor=colors.HexColor("#1f2933"),
            alignment=TA_LEFT,
            spaceAfter=4,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Small",
            fontName=FONT_REGULAR,
            fontSize=8.3,
            leading=10.5,
            textColor=colors.HexColor("#52606d"),
            alignment=TA_LEFT,
            spaceAfter=3,
        )
    )
    return sheet


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(colors.HexColor("#52606d"))
    canvas.drawString(18 * mm, 10 * mm, "Artificial Evolution Founder Population Stage Summary")
    canvas.drawRightString(doc.pagesize[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_table(rows: list[list[str]], widths: list[float]) -> Table:
    table = Table(rows, colWidths=widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT_REGULAR),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f7fafc"), colors.HexColor("#edf2f7")]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9fb3c8")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_bar_chart(
    title: str,
    x_values: list[str],
    series: list[tuple[str, list[float], colors.Color]],
    y_max: float,
    y_step: float,
    width: int = 470,
    height: int = 210,
) -> Drawing:
    drawing = Drawing(width, height)
    drawing.add(String(width / 2, height - 12, title, fontName=FONT_BOLD, fontSize=11, textAnchor="middle", fillColor=colors.HexColor("#16324f")))

    chart = VerticalBarChart()
    chart.x = 40
    chart.y = 35
    chart.height = 130
    chart.width = width - 80
    chart.data = [values for _, values, _ in series]
    chart.strokeColor = colors.HexColor("#8aa1b1")
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = y_max
    chart.valueAxis.valueStep = y_step
    chart.valueAxis.labels.fontName = FONT_REGULAR
    chart.valueAxis.labels.fontSize = 7
    chart.categoryAxis.labels.boxAnchor = "ne"
    chart.categoryAxis.labels.dx = 0
    chart.categoryAxis.labels.dy = -2
    chart.categoryAxis.labels.angle = 0
    chart.categoryAxis.labels.fontName = FONT_REGULAR
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.categoryNames = x_values
    chart.groupSpacing = 6
    chart.barSpacing = 2

    for index, (_, _, color) in enumerate(series):
        chart.bars[index].fillColor = color
        chart.bars[index].strokeColor = color

    drawing.add(chart)

    legend_y = 15
    legend_x = 46
    for label, _, color in series:
        drawing.add(String(legend_x + 12, legend_y, label, fontName=FONT_REGULAR, fontSize=7.5, fillColor=colors.HexColor("#334e68")))
        drawing.add(Rect(legend_x, legend_y - 5, 8, 8, fillColor=color, strokeColor=color))
        legend_x += 110

    return drawing


def load_context() -> dict:
    return {
        "optimal": read_json(DATA_DIR / "founder_population_optimal_search.json"),
        "micro": read_json(DATA_DIR / "founder_population_scaling_micro_body14.json"),
        "baseline": read_json(DATA_DIR / "founder_population_scaling_body14.json"),
    }


def append_title(story: list, sheet: StyleSheet1) -> None:
    story.append(Spacer(1, 14 * mm))
    story.append(para("Founder Population Scaling Summary", sheet["Title"]))
    story.append(para("สรุปผลการทดลองขนาดประชากรเริ่มต้นในโลก sexed + inheritance ณ วันที่ 2026-05-11", sheet["Title"]))
    story.append(
        para(
            "This report summarizes how initial founder population size changes multi-generation persistence under the current world rules.",
            sheet["Subtitle"],
        )
    )
    story.append(
        para(
            "เอกสารนี้สรุปว่าจำนวน founder เริ่มต้นส่งผลต่อการพาสายตระกูลไปข้ามรุ่นอย่างไร ภายใต้กติกาโลกชุดปัจจุบัน",
            sheet["Subtitle"],
        )
    )


def append_overview(story: list, sheet: StyleSheet1, ctx: dict) -> None:
    ranked = ctx["optimal"]["ranked_populations"]
    top = ctx["optimal"]["summary_by_population"][str(ranked[0])]
    second = ctx["optimal"]["summary_by_population"][str(ranked[1])]
    third = ctx["optimal"]["summary_by_population"][str(ranked[2])]
    story.append(para("Key Findings", sheet["Section"]))
    bullets = [
        f"The current sweet spot is 250 founders. It has mean max generation {top['mean_max_generation']} and reaches generation 7 or more in {top['generation_7_or_more_runs']}/{top['runs']} runs.",
        f"300 founders is close behind. It produces more children overall, but its mean max generation ({second['mean_max_generation']}) is still lower than 250.",
        f"200 founders clearly improves over 50-100, but remains less robust than 250-300.",
        f"Tiny populations fail almost immediately. Population 2 never exceeded generation 1 in the test set, and population 4 never exceeded generation 1 either.",
        "Increasing founders helps, but it does not fix the root problem by itself. The world is still unstable and can still collapse even in high-founder runs.",
    ]
    for bullet in bullets:
        story.append(para(f"- {bullet}", sheet["Body"]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        para(
            f"Top three populations in this stage: 250, 300, and 200 founders. Their best observed runs reached generations {top['best_run']['max_generation_observed']}, {second['best_run']['max_generation_observed']}, and {third['best_run']['max_generation_observed']} respectively.",
            sheet["Body"],
        )
    )


def append_summary_table(story: list, sheet: StyleSheet1, ctx: dict) -> None:
    story.append(para("Population Ranking", sheet["Section"]))
    ranked = ctx["optimal"]["ranked_populations"]
    rows = [["Rank", "Founders", "Runs", "Mean max gen", "Mean final tick", "Gen>=5", "Not extinct"]]
    for rank, population in enumerate(ranked, start=1):
        item = ctx["optimal"]["summary_by_population"][str(population)]
        rows.append(
            [
                str(rank),
                str(population),
                str(item["runs"]),
                str(item["mean_max_generation"]),
                str(item["mean_final_tick"]),
                f"{item['generation_5_or_more_runs']}/{item['runs']}",
                f"{item['runs'] - item['extinctions']}/{item['runs']}",
            ]
        )
    story.append(build_table(rows, [14 * mm, 22 * mm, 16 * mm, 28 * mm, 28 * mm, 21 * mm, 23 * mm]))


def append_charts(story: list, sheet: StyleSheet1, ctx: dict) -> None:
    story.append(para("Charts", sheet["Section"]))
    ranked = ctx["optimal"]["ranked_populations"]
    x_values = [str(p) for p in ranked]
    summaries = ctx["optimal"]["summary_by_population"]
    mean_max_gen = [summaries[str(p)]["mean_max_generation"] for p in ranked]
    mean_final_tick = [summaries[str(p)]["mean_final_tick"] for p in ranked]
    non_extinct = [summaries[str(p)]["runs"] - summaries[str(p)]["extinctions"] for p in ranked]
    gen7 = [summaries[str(p)]["generation_7_or_more_runs"] for p in ranked]

    story.append(
        build_bar_chart(
            "Mean Maximum Generation by Founder Population",
            x_values,
            [("Mean max generation", mean_max_gen, colors.HexColor("#2f7ed8"))],
            y_max=11,
            y_step=1,
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
        build_bar_chart(
            "Persistence Signals by Founder Population",
            x_values,
            [
                ("Mean final tick", mean_final_tick, colors.HexColor("#5cb85c")),
                ("Non-extinct runs", non_extinct, colors.HexColor("#f0ad4e")),
                ("Gen>=7 runs", gen7, colors.HexColor("#d9534f")),
            ],
            y_max=1000,
            y_step=100,
        )
    )
    story.append(para("Note: the second chart mixes scales. Mean final tick uses the same axis as run counts, so treat it as a directional comparison rather than a precise visual magnitude comparison.", sheet["Small"]))


def append_case_studies(story: list, sheet: StyleSheet1, ctx: dict) -> None:
    story.append(PageBreak())
    story.append(para("Representative Cases", sheet["Section"]))
    optimal = ctx["optimal"]["summary_by_population"]
    cases = [
        ("Population 2", ctx["micro"]["summary_by_population"]["2"]),
        ("Population 50", ctx["baseline"]["summary_by_population"]["50"]),
        ("Population 200", optimal["200"]),
        ("Population 250", optimal["250"]),
        ("Population 300", optimal["300"]),
    ]
    rows = [["Case", "Mean max gen", "Mean tick", "Best run", "Interpretation"]]
    for label, item in cases:
        best = item["best_run"]
        if label == "Population 2":
            interpretation = "Cannot establish a durable reproduction chain."
        elif label == "Population 50":
            interpretation = "Can reach gen2-gen4, but still thins out quickly."
        elif label == "Population 200":
            interpretation = "Crosses the bottleneck more often, but is still unstable."
        elif label == "Population 250":
            interpretation = "Current best balance between depth and repeatability."
        else:
            interpretation = "High-output regime, but noisier than 250."
        rows.append(
            [
                label,
                str(item["mean_max_generation"]),
                str(item["mean_final_tick"]),
                f"seed {best['seed']} -> gen {best['max_generation_observed']}",
                interpretation,
            ]
        )
    story.append(build_table(rows, [28 * mm, 24 * mm, 22 * mm, 34 * mm, 70 * mm]))


def append_conclusion(story: list, sheet: StyleSheet1, ctx: dict) -> None:
    story.append(para("Interpretation", sheet["Section"]))
    lines = [
        "The current world shows a clear founder-mass threshold. Tiny populations collapse before a lineage can stabilize, mid-sized populations can establish short chains, and high populations can sometimes sustain long thin chains.",
        "The best observed operating region is around 250 founders. That region produces the strongest combination of deep generations, longer runtime, and repeatable non-extinction within the test horizon.",
        "The system is still not solved. Even the best region does not guarantee long-run stability, and some high-founder runs still collapse early.",
        "This means founder count is a strong amplifier, not the full fix. The deeper root cause remains in post-generation-1 replacement dynamics, especially whether the system can keep enough adults, enough mating continuity, and enough energy to keep replacement above one.",
    ]
    for line in lines:
        story.append(para(line, sheet["Body"]))

    story.append(para("Source Data", sheet["Section"]))
    paths = [
        str(DATA_DIR / "founder_population_scaling_micro_body14.json"),
        str(DATA_DIR / "founder_population_scaling_body14.json"),
        str(DATA_DIR / "founder_population_optimal_search.json"),
    ]
    for path in paths:
        story.append(para(f"- {path}", sheet["Small"]))


def build_report() -> Path:
    register_fonts()
    sheet = make_styles()
    ctx = load_context()

    story: list = []
    append_title(story, sheet)
    append_overview(story, sheet, ctx)
    append_summary_table(story, sheet, ctx)
    story.append(Spacer(1, 4 * mm))
    append_charts(story, sheet, ctx)
    append_case_studies(story, sheet, ctx)
    append_conclusion(story, sheet, ctx)

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return OUTPUT_PDF


if __name__ == "__main__":
    output = build_report()
    print(output)

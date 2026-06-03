from __future__ import annotations

from pathlib import Path
import json

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
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

FONT_REGULAR = "Tahoma"
FONT_BOLD = "Tahoma-Bold"

OUTPUTS = {
    "bilingual": REPORTS_DIR / "artificial_evolution_status_bilingual_2026-05-10.pdf",
    "th": REPORTS_DIR / "artificial_evolution_status_th_2026-05-10.pdf",
    "en": REPORTS_DIR / "artificial_evolution_status_en_2026-05-10.pdf",
}


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, r"C:\Windows\Fonts\tahoma.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, r"C:\Windows\Fonts\tahomabd.ttf"))


def make_styles() -> StyleSheet1:
    sheet = StyleSheet1()
    sheet.add(
        ParagraphStyle(
            name="Title",
            fontName=FONT_BOLD,
            fontSize=21,
            leading=27,
            textColor=colors.HexColor("#16324f"),
            alignment=TA_CENTER,
            spaceAfter=8,
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
            spaceAfter=16,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Section",
            fontName=FONT_BOLD,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e4a72"),
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Subsection",
            fontName=FONT_BOLD,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#244f74"),
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=4,
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
            fontSize=8.4,
            leading=11,
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


def add_bullets(story: list, sheet: StyleSheet1, lines: list[str]) -> None:
    for line in lines:
        story.append(para(f"- {line}", sheet["Body"]))


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(colors.HexColor("#52606d"))
    canvas.drawString(18 * mm, 10 * mm, "Artificial Evolution Status Report")
    canvas.drawRightString(doc.pagesize[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_table(rows: list[list[str]]) -> Table:
    table = Table(rows, colWidths=[16 * mm, 49 * mm, 25 * mm, 22 * mm, 20 * mm, 22 * mm, 26 * mm])
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


def load_context() -> dict:
    sexed_test = read_json(DATA_DIR / "sexed_generation_test.json")
    sexed_search = read_json(DATA_DIR / "sexed_world_body_search.json")
    first_technology = read_json(DATA_DIR / "first_technology_emergence_study.json")
    return {
        "exp40": {
            "final_tick": 201,
            "peak_population": 76,
            "total_births": 26,
            "matured_children": 18,
            "population_extinct": True,
            "target_generation_reached": False,
        },
        "exp41": sexed_search,
        "exp45": sexed_test,
        "exp39": first_technology,
        "first_tool": {
            "successful_runs": 2,
            "mean_first_tool_tick": 1.5,
            "min_first_tool_tick": 1,
            "max_first_tool_tick": 2,
            "tool_name": "knife",
        },
        "paper_bundle_path": str(
            ROOT / "data" / "research_runs" / "experiment_033_paper_capture" / "manifest.json"
        ),
        "protocol_path": str(ROOT / "docs" / "PAPER_DATA_PROTOCOL.md"),
    }


def append_title(story: list, sheet: StyleSheet1, variant: str) -> None:
    story.append(Spacer(1, 14 * mm))
    if variant == "th":
        story.append(para("รายงานสรุปสถานะ Artificial Evolution", sheet["Title"]))
        story.append(
            para(
                "สรุปปัญหาปัจจุบัน รากสาเหตุที่ตรวจพบ และผลการทดลองล่าสุดทั้งหมด ณ วันที่ 2026-05-10",
                sheet["Subtitle"],
            )
        )
    elif variant == "en":
        story.append(para("Artificial Evolution Status Report", sheet["Title"]))
        story.append(
            para(
                "Current problem summary, root-cause findings, and latest experiment outcomes as of 2026-05-10",
                sheet["Subtitle"],
            )
        )
    else:
        story.append(para("Artificial Evolution Status Report", sheet["Title"]))
        story.append(para("รายงานสรุปสถานะ Artificial Evolution", sheet["Title"]))
        story.append(
            para(
                "Bilingual working report covering the current problems and the latest experiment outcomes as of 2026-05-10.",
                sheet["Subtitle"],
            )
        )
        story.append(
            para(
                "เอกสารสองภาษาฉบับทำงาน สรุปปัญหาปัจจุบันและผลการทดลองล่าสุดทั้งหมด ณ วันที่ 2026-05-10",
                sheet["Subtitle"],
            )
        )


def append_timeline(story: list, sheet: StyleSheet1, ctx: dict, variant: str) -> None:
    exp41_best = ctx["exp41"]["best_record"]
    exp45_summary = ctx["exp45"]["summary"]
    exp39 = ctx["exp39"]
    first_tool = ctx["first_tool"]
    if variant == "th":
        story.append(para("ไทม์ไลน์การทดลองสำคัญ", sheet["Section"]))
        rows = [
            ["Exp", "จุดประสงค์", "ผลลัพธ์", "Tick", "Births", "Matured", "หมายเหตุ"],
            ["36", "first-tool full test", "เร็วเกินไป", "1-2", "-", "-", "tool แรกเกิดแทบทันที"],
            ["39", "emergent technology", "พบเร็ว", str(exp39["min_first_technology_tick"]), "9", "6", "proto_composite_type_a ที่ tick 8"],
            ["40", "sexed world ครั้งแรก", "ตายหมด", str(ctx["exp40"]["final_tick"]), "26", "18", "ไม่ถึง gen3"],
            ["41", "search ร่างกายทั้งโลก", "ยังไม่รอด", str(exp41_best["final_tick"]), str(exp41_best["total_births"]), str(exp41_best["matured_children"]), "best body ยัง extinct"],
            ["42-44", "diagnostics", "เจอสาเหตุ", "-", "-", "-", "gen1 ตันที่ low_energy และ nest access"],
            ["45", "fix household continuity", "สำเร็จ", str(exp45_summary["final_tick"]), str(exp45_summary["total_births"]), str(exp45_summary["matured_children"]), "ไปถึง gen3 โดยโลกยากเท่าเดิม"],
        ]
    elif variant == "en":
        story.append(para("Experiment Timeline", sheet["Section"]))
        rows = [
            ["Exp", "Purpose", "Result", "Tick", "Births", "Matured", "Key note"],
            ["36", "first-tool full test", "too fast", "1-2", "-", "-", "first tool appeared almost immediately"],
            ["39", "emergent technology", "emerged early", str(exp39["min_first_technology_tick"]), "9", "6", "proto_composite_type_a at tick 8"],
            ["40", "first sexed world", "extinct", str(ctx["exp40"]["final_tick"]), "26", "18", "failed before gen3"],
            ["41", "full body search", "no survivor", str(exp41_best["final_tick"]), str(exp41_best["total_births"]), str(exp41_best["matured_children"]), "best body still extinct"],
            ["42-44", "diagnostics", "root cause found", "-", "-", "-", "gen1 blocked by low energy and nest access"],
            ["45", "household continuity fix", "success", str(exp45_summary["final_tick"]), str(exp45_summary["total_births"]), str(exp45_summary["matured_children"]), "reached gen3 with same hard world"],
        ]
    else:
        story.append(para("Experiment Timeline / ไทม์ไลน์การทดลองสำคัญ", sheet["Section"]))
        rows = [
            ["Exp", "Purpose / จุดประสงค์", "Result", "Tick", "Births", "Matured", "Key note"],
            ["36", "first-tool test", "too fast", "1-2", "-", "-", "named tool emerged almost instantly"],
            ["39", "emergent technology", "early", str(exp39["min_first_technology_tick"]), "9", "6", "proto_composite_type_a at tick 8"],
            ["40", "first sexed-world test", "extinct", str(ctx["exp40"]["final_tick"]), "26", "18", "failed before gen3"],
            ["41", "full sexed body search", "no survivor", str(exp41_best["final_tick"]), str(exp41_best["total_births"]), str(exp41_best["matured_children"]), "best pre-fix body still extinct"],
            ["42-44", "reproduction diagnostics", "root cause found", "-", "-", "-", "gen1 blocked by energy and household access"],
            ["45", "family household continuity fix", "success", str(exp45_summary["final_tick"]), str(exp45_summary["total_births"]), str(exp45_summary["matured_children"]), "gen3 reached without lowering world difficulty"],
        ]
    story.append(build_table(rows))


def append_thai_section(story: list, sheet: StyleSheet1, ctx: dict) -> None:
    exp41_best = ctx["exp41"]["best_record"]
    exp45_summary = ctx["exp45"]["summary"]
    exp39_record = ctx["exp39"]["records"][0]
    story.append(para("ส่วนภาษาไทย", sheet["Section"]))
    story.append(para("1. ปัญหาปัจจุบัน", sheet["Subsection"]))
    add_bullets(
        story,
        sheet,
        [
            "เป้าหมายวิจัยตอนนี้เปลี่ยนจาก crafting แบบเกม ไปสู่ emergent technology ที่ไม่ตั้งชื่อของล่วงหน้าโดยนักพัฒนา",
            "ผลทดลองฝั่ง named crafting เดิมบอกชัดว่าโลกยังไม่กดดันพอ เพราะ tool แรกเกิดเร็วมากที่ tick 1-2",
            "เมื่อเปลี่ยนเป็น emergent technology ปัญหาใหม่คือเทคโนโลยีก็ยังโผล่เร็วเกินไป โดย `proto_composite_type_a` เกิดตั้งแต่ tick 8",
            "ด้านการสืบพันธุ์แบบแยกเพศ คอขวดหลักก่อน fix คือ generation 1 ไม่ส่งต่อไป generation 2 ได้ แม้จะโตเป็น adult แล้ว",
        ],
    )

    story.append(para("2. ผลการทดลองสำคัญ", sheet["Subsection"]))
    add_bullets(
        story,
        sheet,
        [
            f"Experiment 36 first-tool: สำเร็จทุก seed แต่เร็วเกินไปมาก ค่าเฉลี่ย tool แรก = tick {ctx['first_tool']['mean_first_tool_tick']}",
            f"Experiment 39 emergent technology: {exp39_record['first_technology_name']} เกิดที่ tick {exp39_record['first_technology_tick']} พร้อม peak population {exp39_record['peak_population']}",
            f"Experiment 40 sexed generation test: final_tick={ctx['exp40']['final_tick']}, births={ctx['exp40']['total_births']}, matured_children={ctx['exp40']['matured_children']}, extinct=True",
            f"Experiment 41 body search: สแกน 250 candidate x 3 seeds, best body คือ idx={exp41_best['body_index']} แต่ยัง extinct ที่ tick {exp41_best['final_tick']}",
            f"Experiment 45 หลังแก้ household continuity: final_tick={exp45_summary['final_tick']}, extinct={exp45_summary['population_extinct']}, gen3={exp45_summary['target_generation_reached']}, gen3_tick={exp45_summary['target_generation_tick']}",
        ],
    )

    story.append(para("3. สาเหตุที่ตรวจพบจริง", sheet["Subsection"]))
    add_bullets(
        story,
        sheet,
        [
            "ไม่ใช่ bug ว่าลืมใส่เพศให้ gen1",
            "ไม่ใช่ bug ว่า gen0 ไม่ส่ง parent metadata ให้ลูก",
            "telemetry จาก experiment 42-44 ชี้ว่า gen1 females จำนวนมากมีคู่และบางตัวอยู่ใกล้ nest แต่ติด `nest_food=0` และ `low_energy` พร้อมกัน",
            "สรุปคือปัญหาอยู่ที่ family household continuity มากกว่าความยากโลกอย่างเดียว",
        ],
    )

    story.append(para("4. สิ่งที่แก้แล้ว", sheet["Subsection"]))
    add_bullets(
        story,
        sheet,
        [
            "เพิ่มการ resolve บ้านของครอบครัวจาก parent, other_parent และ shared home",
            "ทำให้ลูกโตแล้วสามารถใช้งาน household storage ของครอบครัวได้สมเหตุสมผลขึ้น",
            "ไม่ลด threshold, ไม่เพิ่มอาหาร, และไม่ทำให้โลกง่ายลง",
        ],
    )

    story.append(para("5. สิ่งที่ยังเปิดอยู่", sheet["Subsection"]))
    add_bullets(
        story,
        sheet,
        [
            "ต้อง rerun sexed-world body search หลัง fix เพราะผล search เดิมเป็น pre-fix",
            "ต้องทำ batch หลาย seed เพื่อยืนยันว่า exp45 ไม่ใช่ผลเฉพาะ seed เดียว",
            "ต้องทำให้ emergent technology ช้าลงและเกิดจากแรงกดดันจริง ไม่ใช่เกิดเร็วในช่วงตั้งต้น",
            f"ชั้นข้อมูลสำหรับงานวิจัยพร้อมแล้วตาม protocol ที่ {ctx['protocol_path']}",
        ],
    )


def append_english_section(story: list, sheet: StyleSheet1, ctx: dict) -> None:
    exp41_best = ctx["exp41"]["best_record"]
    exp45_summary = ctx["exp45"]["summary"]
    exp39_record = ctx["exp39"]["records"][0]
    story.append(para("English Section", sheet["Section"]))
    story.append(para("1. Current Problem Set", sheet["Subsection"]))
    add_bullets(
        story,
        sheet,
        [
            "The project has moved away from explicit named crafting and toward emergent technology defined by behavioral impact and spread.",
            "The old named-tool setup was too easy: the first tool appeared at tick 1-2, which made the research question too weak.",
            "The new emergent-technology setup is conceptually better, but technology still appears too early: `proto_composite_type_a` emerged at tick 8 in the smoke test.",
            "Under sexed reproduction, the main failure mode before the fix was a broken generation-1 to generation-2 reproduction chain.",
        ],
    )

    story.append(para("2. Major Experiment Outcomes", sheet["Subsection"]))
    add_bullets(
        story,
        sheet,
        [
            f"Experiment 36 first-tool study: all runs succeeded, but too quickly, with mean first-tool tick {ctx['first_tool']['mean_first_tool_tick']}.",
            f"Experiment 39 emergent technology study: {exp39_record['first_technology_name']} emerged at tick {exp39_record['first_technology_tick']} with peak population {exp39_record['peak_population']}.",
            f"Experiment 40 first sexed-generation test: final_tick={ctx['exp40']['final_tick']}, births={ctx['exp40']['total_births']}, matured_children={ctx['exp40']['matured_children']}, extinct=True.",
            f"Experiment 41 full sexed-world body search: 250 candidates across 3 seeds each; best body was idx={exp41_best['body_index']} but still went extinct at tick {exp41_best['final_tick']}.",
            f"Experiment 45 after the family-household fix: final_tick={exp45_summary['final_tick']}, extinct={exp45_summary['population_extinct']}, gen3={exp45_summary['target_generation_reached']}, gen3_tick={exp45_summary['target_generation_tick']}.",
        ],
    )

    story.append(para("3. Root Cause Found", sheet["Subsection"]))
    add_bullets(
        story,
        sheet,
        [
            "Generation-1 agents did have valid sex assignments and inherited parent metadata.",
            "Diagnostics in experiments 42-44 showed repeated `repro_fail` cases where adult generation-1 females had mates but hit `nest_food=0` and `low_energy` together.",
            "This pointed to a household continuity problem: children matured without reliably resolving usable family household storage.",
            "The fix therefore targeted family household ownership and storage continuity rather than making the world easier.",
        ],
    )

    story.append(para("4. What Is Solved vs Still Open", sheet["Subsection"]))
    add_bullets(
        story,
        sheet,
        [
            "Solved: generation-3 adulthood can now be reached in the same hard world with the same body family.",
            "Solved: research-grade telemetry, readable logs, and dashboard outputs exist for serious analysis.",
            "Open: the full sexed-world search must be rerun after the fix because the old ranking is now stale.",
            "Open: emergent technology still appears too early, so the world pressure and experimentation loop need to be hardened.",
            f"Open: publication-grade inference still needs multi-seed batches, even though the data protocol is already defined in {ctx['protocol_path']}.",
        ],
    )


def append_key_files(story: list, sheet: StyleSheet1, ctx: dict, variant: str) -> None:
    title = {
        "th": "ไฟล์อ้างอิงหลัก",
        "en": "Key Reference Files",
        "bilingual": "Key Files / ไฟล์อ้างอิงหลัก",
    }[variant]
    story.append(para(title, sheet["Section"]))
    for line in [
        str(ROOT / "data" / "first_technology_emergence_study.md"),
        str(ROOT / "data" / "sexed_world_body_search.md"),
        str(ROOT / "data" / "sexed_generation_test.md"),
        str(ROOT / "data" / "experiments" / "experiment_040.md"),
        str(ROOT / "data" / "experiments" / "experiment_041.md"),
        str(ROOT / "data" / "experiments" / "experiment_044.md"),
        str(ROOT / "data" / "experiments" / "experiment_045.md"),
        str(ROOT / "data" / "dashboards" / "sexed_generation_mode" / "experiment_045_sexed_seed_7" / "index.html"),
        ctx["paper_bundle_path"],
        ctx["protocol_path"],
    ]:
        story.append(para(f"- {line}", sheet["Small"]))


def build_story(variant: str, ctx: dict) -> list:
    sheet = make_styles()
    story: list = []
    append_title(story, sheet, variant)
    append_timeline(story, sheet, ctx, variant)
    if variant == "th":
        append_thai_section(story, sheet, ctx)
    elif variant == "en":
        append_english_section(story, sheet, ctx)
    else:
        append_thai_section(story, sheet, ctx)
        story.append(PageBreak())
        append_english_section(story, sheet, ctx)
    append_key_files(story, sheet, ctx, variant)
    return story


def build_pdf(path: Path, variant: str, ctx: dict) -> None:
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Artificial Evolution Status Report",
        author="OpenAI Codex",
    )
    doc.build(build_story(variant, ctx), onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    register_fonts()
    ctx = load_context()
    for variant, path in OUTPUTS.items():
        build_pdf(path, variant, ctx)
        print(path)


if __name__ == "__main__":
    main()

"""Build the official Research Summary PDF (EN + TH) for advisor outreach.

Source content: reports/research_summary_2026-06-30.en.md
Style: A4, Sarabun (Thai-capable), teal headings, page numbers -- matches the
previous advisor-materials PDF so EN and TH read as a consistent pair.

Run:
    python scripts/build_research_summary_pdf.py
Outputs:
    output/pdf/Research_Summary_EN_2026-06-30.pdf
    output/pdf/Research_Summary_TH_2026-06-30.pdf
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "pdf"
FIG_DIR = ROOT / "reports" / "figures"
FONT_DIR = ROOT / "assets" / "fonts"


def register_fonts() -> dict[str, str]:
    regular = FONT_DIR / "Sarabun-Regular.ttf"
    bold = FONT_DIR / "Sarabun-Bold.ttf"
    italic = FONT_DIR / "Sarabun-Italic.ttf"
    if regular.exists() and bold.exists() and italic.exists():
        pdfmetrics.registerFont(TTFont("Sarabun", regular))
        pdfmetrics.registerFont(TTFont("Sarabun-Bold", bold))
        pdfmetrics.registerFont(TTFont("Sarabun-Italic", italic))
        return {"regular": "Sarabun", "bold": "Sarabun-Bold", "italic": "Sarabun-Italic"}
    return {"regular": "Helvetica", "bold": "Helvetica-Bold", "italic": "Helvetica-Oblique"}


FONTS = register_fonts()

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#25636B")
GREY = colors.HexColor("#4B5563")
LINK = colors.HexColor("#1F5F99")


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title", parent=base["Title"], fontName=FONTS["bold"], fontSize=19,
            leading=23, alignment=TA_CENTER, textColor=NAVY, spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"], fontName=FONTS["regular"], fontSize=10.5,
            leading=14, alignment=TA_CENTER, textColor=GREY, spaceAfter=3,
        ),
        "meta": ParagraphStyle(
            "Meta", parent=base["Normal"], fontName=FONTS["italic"], fontSize=9,
            leading=12, alignment=TA_CENTER, textColor=GREY, spaceAfter=2,
        ),
        "link": ParagraphStyle(
            "Link", parent=base["BodyText"], fontName=FONTS["regular"], fontSize=9,
            leading=12, alignment=TA_CENTER, textColor=LINK, spaceAfter=2,
        ),
        "h1": ParagraphStyle(
            "Heading1", parent=base["Heading1"], fontName=FONTS["bold"], fontSize=13.5,
            leading=17, textColor=NAVY, spaceBefore=11, spaceAfter=5,
        ),
        "h2": ParagraphStyle(
            "Heading2", parent=base["Heading2"], fontName=FONTS["bold"], fontSize=11,
            leading=14, textColor=TEAL, spaceBefore=7, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName=FONTS["regular"], fontSize=10,
            leading=13.4, alignment=TA_JUSTIFY, spaceAfter=4,
        ),
        "lead": ParagraphStyle(
            "Lead", parent=base["BodyText"], fontName=FONTS["regular"], fontSize=10,
            leading=13.6, alignment=TA_LEFT, textColor=NAVY, spaceAfter=5,
            borderColor=colors.HexColor("#CBD5E1"), borderWidth=0, leftIndent=0,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName=FONTS["regular"], fontSize=8.4,
            leading=10.8, textColor=colors.black, spaceAfter=2,
        ),
        "caption": ParagraphStyle(
            "Caption", parent=base["BodyText"], fontName=FONTS["italic"], fontSize=8,
            leading=10.4, textColor=GREY, alignment=TA_CENTER, spaceBefore=2, spaceAfter=8,
        ),
    }


S = styles()


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def bullets(items: list[str], style: str = "body") -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(it, S[style]), leftIndent=10) for it in items],
        bulletType="bullet", leftIndent=14,
        bulletFontName=FONTS["regular"], bulletFontSize=8,
    )


def numbered(items: list[str], style: str = "body") -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(it, S[style]), leftIndent=12) for it in items],
        bulletType="1", leftIndent=16,
        bulletFontName=FONTS["regular"], bulletFontSize=9.5,
    )


def table(rows: list[list[str]], widths: list[float] | None = None) -> Table:
    tbl = Table([[p(c, "small") for c in row] for row in rows], colWidths=widths, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F0F2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
        ("FONTNAME", (0, 0), (-1, 0), FONTS["bold"]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F9FA")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return tbl


def figure(name: str, caption: str, width_cm: float = 12.6, max_height_cm: float = 9.0) -> list:
    path = FIG_DIR / name
    if not path.exists():
        return [p(f"[figure missing: {name}]", "small")]
    img = Image(str(path))
    w = width_cm * cm
    h = img.imageHeight * (w / img.imageWidth)
    if h > max_height_cm * cm:
        h = max_height_cm * cm
        w = img.imageWidth * (h / img.imageHeight)
    img.drawWidth, img.drawHeight = w, h
    img.hAlign = "CENTER"
    return [KeepTogether([img, p(caption, "caption")])]


def rule() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#CBD5E1"),
                      spaceBefore=4, spaceAfter=6)


def header_block(c: dict) -> list:
    return [
        p(c["title"], "title"),
        p(c["subtitle"], "subtitle"),
        p(c["meta"], "meta"),
        p("Email: chisanupong.injun@gmail.com&nbsp;&nbsp;|&nbsp;&nbsp;GitHub: github.com/sstangkh73/artificial-evolution", "link"),
        Spacer(1, 0.1 * cm),
        rule(),
    ]


# --------------------------------------------------------------------------- #
#  ENGLISH CONTENT
# --------------------------------------------------------------------------- #
def story_en() -> list:
    S["body"].alignment = TA_JUSTIFY  # English justifies cleanly (natural word spaces)
    s: list = []
    s += header_block({
        "title": "Research Summary",
        "subtitle": "Artificial Life Simulation for Emergent Adaptive Behavior",
        "meta": "Chisanupong Injun &middot; Grade 10 (M.4), Dibuk Phang-nga Wittayayon School, Phang-nga, Thailand &middot; Updated 30 June 2026",
    })

    s += [p("Research question", "h1")]
    s += [p("<b>Can adaptive, knowledge-like behavior <i>emerge</i> from an agent's interaction with a simulated ecology, "
            "when the agent is <u>not</u> given predefined semantic labels, explicit instructions about resource use, "
            "or a hand-authored task-reward function?</b>")]
    s += [p("<b>Honest one-line status:</b> the project has solid, controlled evidence for <b>experience-based learning</b> "
            "and <b>ecological interaction</b>, and an <b>honestly unsolved</b> problem in <b>long-run population "
            "sustainability</b>. It does not yet claim intentional farming, social transmission, or open-ended evolution.")]

    s += [p("Part 1 &mdash; What the project has established (strengths, with reason + data)", "h1")]
    s += [p("Each item gives the <b>claim</b>, <b>why it is credible</b> (the control or method), and the <b>data</b>, plus "
            "its scope limit. The project rule: a pattern is not promoted to &lsquo;knowledge&rsquo; until controls rule out "
            "simpler explanations (food hotspots, hunger pressure, deterministic movement, shared corridors).")]

    s += [p("1. A working ecology substrate exists &mdash; not just an idea.", "h2")]
    s += [p("A full seed &rarr; plant &rarr; fruit &rarr; consumed cycle runs and is logged in a tuned 100x100 world. "
            "<b>Data:</b> Phase 1 passed 5/5 seeds; per run ~139.0 germinated seeds, 33.6 mature plants, 68.6 fruiting "
            "events, 47.8 plant-food consumptions. <b>Scope:</b> establishes the substrate only &mdash; no cognition claim.")]

    s += [p("2. Reward-place learning is measurable and large.", "h2")]
    s += [p("A strict <i>leave-then-return</i> metric is compared against a random-position baseline, so &lsquo;returning to "
            "food&rsquo; cannot be explained by chance position. <b>Data:</b> Phase 2 passed 3/3 seeds; mean owner return "
            "lift <b>41.7x</b> (per-seed 52.7x / 38.7x / 33.7x). <b>Scope:</b> place memory, not semantic understanding.")]

    s += [p("3. Experience-based food-value learning &mdash; the strongest result, hardened with controls + statistics.", "h2")]
    s += [p("The baseline architecture is <i>value-blind</i> at eating time (it eats whatever fits the mouth). When "
            "experience-based value memory is enabled, agents learn each food's energy value and stop eating the low-value "
            "one. The result survives three independent controls:")]
    s += [bullets([
        "<b>Per-agent causality (A1):</b> of 12 agents, 10 learned to skip the low-value seed &mdash; and <b>0/12 skipped "
        "it without first tasting the better food</b>. Behavior change is bound to direct individual experience.",
        "<b>Mechanism control (A5):</b> same seed, same config, only the memory switch differs. Memory <b>on</b> &rarr; "
        "10/12 skip (108 seed meals, 2,163 skips); memory <b>off</b> &rarr; <b>0/12 skip</b> (382 seed meals, 0 skips); "
        "plant meals identical 52 = 52. The behavior disappears when the mechanism is removed.",
        "<b>Quantitative threshold (A2):</b> agents learn seed = 50 &lt;&lt; plant = 250, and skip seed because it falls "
        "below a learned threshold (125), not because of a &lsquo;bad&rsquo; label.",
    ])]
    s += [Spacer(1, 0.1 * cm)]
    s += [table([
        ["Window", "Value-blind (no learning)", "Value-learning enabled"],
        ["0-1k ticks", "591", "236"],
        ["1-2k ticks", "613", "105"],
        ["2-3k ticks", "370", "15"],
        ["3-4k ticks", "336", "5"],
        ["4-5k ticks", "392", "5"],
        ["5-6k ticks", "334", "5"],
    ], [4.2 * cm, 6.0 * cm, 6.0 * cm])]
    s += [p("Low-value seed meals per 1,000 ticks. Learning is population-wide (10/10 who tasted both foods learned; "
            "mean time-to-learn 14.1 ticks, range 2-59), not one lucky agent. <b>Scope:</b> individual learning only "
            "&mdash; not social transmission.", "small")]
    s += [Spacer(1, 0.15 * cm)]
    s += figure("fig4_learning_curve.png",
                "Figure 1. Food-value learning curve: with value-learning, low-value food consumption collapses toward "
                "zero while the value-blind baseline stays high.")
    s += figure("fig_taste_vs_skip_2x2.png",
                "Figure 2. Per-agent causality: every agent that skips the low-value seed has first tasted the better "
                "food. The cell &lsquo;skips without tasting better food&rsquo; is empty (0/12).")

    s += [p("4. Agent actions can enter delayed ecological chains (proto-farming substrate).", "h2")]
    s += [p("Agent-moved seeds were tracked through the full seed &rarr; plant &rarr; fruit &rarr; consumed chain against "
            "a control. <b>Data:</b> Phase 3 passed 3/3 seeds; ~162.3 moved seeds/run, 16.3 completed moved-seed chains, "
            "moved/control lift <b>1.40x</b>. <b>Scope:</b> a proto-farming substrate &mdash; explicitly not intentional "
            "or understood farming.")]

    s += [p("5. An evolutionary (neuroevolution) controller works as a proof of concept.", "h2")]
    s += [p("A neural controller (1,281-parameter genome) is evolved by a genetic algorithm with tournament selection and "
            "elitism, evaluated across held-out seeds. <b>Data:</b> over 12 generations (population 30), best fitness rose "
            "to 30.0. <b>Scope:</b> proof that the neuroevolution loop functions; not yet a large-scale evolved-behavior "
            "result.")]
    s += figure("neuroevolution_learning_curve.png",
                "Figure 3. Neuroevolution proof of concept: best/mean fitness improve over generations.")

    s += [p("6. Method discipline is itself a result.", "h2")]
    s += [p("67/67 automated tests pass; movement RNG is now bound to the experiment seed (fixed 26 June), making "
            "multi-seed replication valid; new instrumentation is opt-in and byte-identical by default. The project treats "
            "<b>negative results as evidence</b> and writes an explicit &lsquo;can claim / cannot claim&rsquo; box for "
            "every result.")]

    s += [PageBreak()]
    s += [p("Part 2 &mdash; Where the project is honestly stuck (the open problem)", "h1")]
    s += [p("<b>The blocker: a mortal population still goes extinct over the long run.</b> What makes this interesting is "
            "that the root cause has been <i>progressively localized with evidence</i>, not hand-waved:")]
    s += [numbered([
        "First suspected <b>fecundity</b> (too few births) &rarr; ruled out: female fecundity reached near-replacement.",
        "Then <b>demographic dynamics</b> &rarr; delayed density dependence produced boom-crash oscillation, but tuning it "
        "did not save the population.",
        "Then <b>foraging access</b> &rarr; measured directly: agents sense food only within ~4 cells while realistic food "
        "is sparser, so at realistic density <b>0% of agents sense food</b> and intake collapses (drain:intake ~453:1).",
        "<b>Option GA (28 June) solved foraging access</b> &mdash; a seed-rain plant economy woke the plant lifecycle "
        "(0 &rarr; ~6,800 fruits) and a decoupled &lsquo;smell&rsquo; sensing radius raised the sensing fraction "
        "0.04 &rarr; 0.77 (meal rate x6.5) on plant-only food, with no artificial crutch. Dispersed agents reached an "
        "<b>energy surplus of 200-550</b>. Access is no longer the bottleneck &mdash; proven by measured surplus.",
        "<b>The bottleneck relocated to a deeper layer: spatial-demographic.</b> New telemetry shows the honest failure "
        "mode: after a crash, global food looks fine (food-per-capita 5.2 &rarr; 19.83) but <b>local food-per-capita "
        "around the cluster is 0.0</b> &mdash; agents starve locally while food sits elsewhere.",
    ])]
    s += [p("The current tension: <b>clustering</b> (needed to find mates) &rarr; local food depletion &rarr; local "
            "starvation; <b>dispersal</b> (needed to eat) &rarr; mates too far apart &rarr; Allee effect, births fade; "
            "plus <b>synchronized lifespan death</b> producing a death wave (death-window CV 0.93). Representative "
            "baseline: extinct at tick 549, peak population 148, 114 births, deaths = 123 lifespan / 37 starvation / "
            "4 durability.")]
    s += figure("fig1_energy_budget.png",
                "Figure 4. The earlier energy bottleneck (drain vs intake) that the foraging-access fix removed; the "
                "residual blocker is now demographic, not energetic.")
    s += [p("<b>This is reported as an honest negative.</b> Each &lsquo;failure&rsquo; sharpened the question and ruled "
            "out an alternative, which is exactly how the real bottleneck was found. Resolving the clustering-vs-dispersal "
            "tension and de-synchronizing death on a world with a real carrying capacity is the next experiment, not a "
            "solved result.")]

    s += [p("Part 3 &mdash; What the project does NOT claim (to be explicit)", "h1")]
    s += [bullets([
        "Intentional farming or semantic understanding of seeds.",
        "Social transmission of food knowledge (only individual learning is shown).",
        "Stable open-ended evolution across generations (population not yet sustained).",
        "Some positive results were isolated in tuned or energy-surplus regimes to separate one mechanism at a time; "
        "that is stated wherever it applies.",
    ])]

    s += [p("Part 4 &mdash; Where I would value an advisor's guidance", "h1")]
    s += [numbered([
        "<b>Population dynamics / theoretical ecology:</b> is the clustering-vs-dispersal tension best framed as a "
        "metapopulation / Allee problem, and what minimal mechanism would let a mortal population converge around a real "
        "carrying capacity?",
        "<b>Experiment design &amp; statistics:</b> sharpening the multi-seed confirmatory protocol (effect sizes, "
        "confidence intervals, non-parametric tests) so the food-value-learning result is publication-grade.",
        "<b>Framing &amp; scope:</b> which single result is strongest to lead with for YSC / ISEF and the Junior Young "
        "Rising Stars award, and how to scope the claims so they stay defensible.",
    ])]
    s += [p("I have a CV, this summary, and a fully open, reproducible codebase with a complete report archive. I would be "
            "grateful for even brief feedback, and would welcome the chance to discuss the project further.")]

    s += [p("Methods note", "h1")]
    s += [p("Python agent-based artificial-life simulation. The world has a grid environment, food spawning, a plant "
            "lifecycle, seeds, energy drain, a metabolism model (food composition &rarr; embodied energy, not symbolic "
            "reward), day-night and seasonal effects, agent memory, reproduction gates, lineage tracking, and "
            "experimental telemetry. Controls include random-position and current-position baselines, memory ablations, "
            "state decoupling, mechanism on/off controls, and multi-seed replication. Reproduction is gated by energy "
            "<i>and</i> body durability (durability 10 &rarr; 0 births; durability 26 &rarr; 50 births under the same "
            "energy regime), which is why energy surplus alone did not immediately yield births.")]

    s += [p("Source index (key reports in the repository)", "h1")]
    s += [table([
        ["Topic", "File"],
        ["Phase 1-3 results", "reports/phase3/phase1_to_phase3_research_success_report_2026-06-13.th.md"],
        ["Food-value learning", "reports/food_value_learning_paper_2026-06-19.th.md"],
        ["Per-agent food learning", "reports/agent_food_value_individual_tracking_2026-06-23.th.md"],
        ["Statistical hardening (Tier A)", "reports/tier_a_completion_summary_2026-06-30.th.md"],
        ["Energy economy", "reports/energy_economy_diagnosis_2026-06-19.th.md"],
        ["Foraging-access fix (Option GA)", "reports/option_ga_foraging_access_results_2026-06-28.th.md"],
        ["Spatial-demographic blocker (Option KHO)", "reports/option_kho_demographic_telemetry_baseline_report_2026-06-28.th.md"],
        ["Full competition report", "reports/competition_full_report_artificial_evolution_2026-06-29.th.md"],
    ], [5.0 * cm, 11.2 * cm])]
    return s


# --------------------------------------------------------------------------- #
#  THAI CONTENT
# --------------------------------------------------------------------------- #
def story_th() -> list:
    S["body"].alignment = TA_LEFT  # Thai has no inter-word spaces; justify creates ugly rivers
    s: list = []
    s += header_block({
        "title": "บทสรุปงานวิจัย",
        "subtitle": "การจำลองชีวิตเทียมเพื่อศึกษาพฤติกรรมปรับตัวที่เกิดขึ้นเอง",
        "meta": "ชิษณุพงศ์ อินทร์จันทร์ &middot; มัธยมศึกษาปีที่ 4 โรงเรียนดีบุกพังงาวิทยายน จังหวัดพังงา &middot; ปรับปรุง 30 มิถุนายน 2569",
    })

    s += [p("คำถามวิจัย", "h1")]
    s += [p("<b>พฤติกรรมปรับตัวที่คล้ายการมี &lsquo;ความรู้&rsquo; สามารถ <i>เกิดขึ้นเอง (emerge)</i> จากการที่ agent "
            "มีปฏิสัมพันธ์กับระบบนิเวศจำลองได้หรือไม่ เมื่อ agent <u>ไม่ได้รับ</u> ป้ายความหมายที่กำหนดไว้ล่วงหน้า "
            "ไม่ได้รับคำสั่งตรง ๆ ว่าให้ใช้ทรัพยากรอย่างไร และไม่มีฟังก์ชันรางวัล (reward) ที่ออกแบบด้วยมือ</b>")]
    s += [p("<b>สถานะโดยสรุปอย่างซื่อสัตย์ (หนึ่งบรรทัด):</b> โครงงานมีหลักฐานที่หนักแน่นและมี control รองรับสำหรับ "
            "<b>การเรียนรู้จากประสบการณ์</b> และ <b>การมีปฏิสัมพันธ์กับระบบนิเวศ</b> และมีปัญหาที่ "
            "<b>ยังแก้ไม่สำเร็จอย่างตรงไปตรงมา</b> คือ <b>ความยั่งยืนของประชากรในระยะยาว</b> "
            "โครงงานยังไม่อ้างว่ามีการทำเกษตรอย่างมีเจตนา การถ่ายทอดความรู้ทางสังคม หรือวิวัฒนาการแบบเปิด")]

    s += [p("ส่วนที่ 1 &mdash; สิ่งที่โครงงานพิสูจน์ได้แล้ว (จุดเด่น พร้อมเหตุผล + ข้อมูล)", "h1")]
    s += [p("แต่ละข้อระบุ <b>ข้ออ้าง (claim)</b>, <b>เหตุผลที่เชื่อถือได้</b> (control หรือวิธีวัด), และ <b>ข้อมูล</b> "
            "พร้อมขอบเขตที่อ้างได้ หลักของโครงงานคือ: จะไม่ยกระดับ &lsquo;รูปแบบพฤติกรรม&rsquo; เป็น &lsquo;ความรู้&rsquo; "
            "จนกว่า control จะตัดคำอธิบายที่ง่ายกว่าออกได้ (จุดอาหารหนาแน่น, แรงกดดันจากความหิว, การเดินแบบกำหนดตายตัว, "
            "เส้นทางหาอาหารร่วมกัน)")]

    s += [p("1. มีระบบนิเวศ (ecology) ที่ทำงานได้จริง &mdash; ไม่ใช่แค่แนวคิด", "h2")]
    s += [p("วงจร เมล็ด &rarr; พืช &rarr; ผล &rarr; ถูกกิน ทำงานครบและถูกบันทึก log ในโลกขนาด 100x100 ที่ปรับค่าแล้ว "
            "<b>ข้อมูล:</b> Phase 1 ผ่าน 5/5 ซีด; ต่อรันเฉลี่ย ~139.0 เมล็ดงอก, 33.6 ต้นโตเต็มวัย, 68.6 ครั้งที่ออกผล, "
            "47.8 ครั้งที่กินอาหารจากพืช <b>ขอบเขต:</b> ยืนยันแค่ &lsquo;พื้นฐานระบบนิเวศ&rsquo; ยังไม่อ้างเรื่องการรู้คิด")]

    s += [p("2. การเรียนรู้ตำแหน่งรางวัล (reward-place learning) วัดได้และมีขนาดผลใหญ่", "h2")]
    s += [p("ใช้ตัวชี้วัดแบบเข้ม &lsquo;ออกไปแล้วกลับมา (leave-then-return)&rsquo; เทียบกับ baseline ตำแหน่งสุ่ม "
            "การ &lsquo;กลับไปหาอาหาร&rsquo; จึงอธิบายด้วยความบังเอิญของตำแหน่งไม่ได้ <b>ข้อมูล:</b> Phase 2 ผ่าน 3/3 ซีด; "
            "อัตราการกลับของเจ้าของตำแหน่งเฉลี่ย <b>41.7 เท่า</b> (รายซีด 52.7x / 38.7x / 33.7x) "
            "<b>ขอบเขต:</b> เป็นความจำตำแหน่ง ไม่ใช่ความเข้าใจเชิงความหมาย")]

    s += [p("3. การเรียนรู้คุณค่าอาหารจากประสบการณ์ &mdash; ผลที่แข็งที่สุด เสริมด้วย control + สถิติ", "h2")]
    s += [p("สถาปัตยกรรม baseline นั้น <i>มองไม่เห็นคุณค่า (value-blind)</i> ตอนกิน (กินทุกอย่างที่เข้าปากได้) "
            "เมื่อเปิดความจำคุณค่าจากประสบการณ์ agent เรียนรู้ค่าพลังงานของอาหารแต่ละชนิดและเลิกกินอาหารค่าต่ำ "
            "ผลนี้ผ่าน control อิสระ 3 ชั้น:")]
    s += [bullets([
        "<b>เหตุภาพรายตัว (A1):</b> จาก 12 ตัว มี 10 ตัวเรียนรู้ที่จะเมินเมล็ดค่าต่ำ &mdash; และ "
        "<b>0/12 ตัวที่เมินโดยไม่เคยชิมอาหารที่ดีกว่าก่อน</b> การเปลี่ยนพฤติกรรมผูกกับประสบการณ์ตรงรายตัว",
        "<b>control ของกลไก (A5):</b> ซีดเดียวกัน คอนฟิกเดียวกัน ต่างแค่สวิตช์ความจำ &mdash; เปิดความจำ &rarr; "
        "เมิน 10/12 (กิน seed 108 มื้อ, เมิน 2,163 ครั้ง); ปิดความจำ &rarr; <b>เมิน 0/12</b> (กิน seed 382 มื้อ, "
        "เมิน 0 ครั้ง); กิน plant เท่ากัน 52 = 52 พฤติกรรมหายไปเมื่อถอดกลไกออก",
        "<b>เกณฑ์เชิงปริมาณ (A2):</b> agent เรียนว่า seed = 50 &lt;&lt; plant = 250 และเมิน seed เพราะค่าต่ำกว่าเกณฑ์ที่เรียนมา "
        "(125) ไม่ใช่เพราะป้ายบอกว่า &lsquo;ไม่ดี&rsquo;",
    ])]
    s += [Spacer(1, 0.1 * cm)]
    s += [table([
        ["ช่วงเวลา", "value-blind (ไม่เรียนรู้)", "เปิดการเรียนรู้คุณค่า"],
        ["0-1k ticks", "591", "236"],
        ["1-2k ticks", "613", "105"],
        ["2-3k ticks", "370", "15"],
        ["3-4k ticks", "336", "5"],
        ["4-5k ticks", "392", "5"],
        ["5-6k ticks", "334", "5"],
    ], [4.2 * cm, 6.0 * cm, 6.0 * cm])]
    s += [p("จำนวนมื้ออาหารค่าต่ำต่อ 1,000 ticks การเรียนรู้เกิดทั้งประชากร (10/10 ตัวที่ได้ชิมครบทั้งสองอย่างเรียนได้; "
            "เวลาเรียนเฉลี่ย 14.1 ticks ช่วง 2-59) ไม่ใช่ตัวเดียวฟลุค <b>ขอบเขต:</b> เป็นการเรียนรู้รายตัวเท่านั้น "
            "&mdash; ยังไม่ใช่การถ่ายทอดทางสังคม", "small")]
    s += [Spacer(1, 0.15 * cm)]
    s += figure("fig4_learning_curve.png",
                "ภาพที่ 1 เส้นโค้งการเรียนรู้คุณค่าอาหาร: เมื่อเปิดการเรียนรู้ การกินอาหารค่าต่ำลดเข้าใกล้ศูนย์ "
                "ขณะที่ baseline แบบ value-blind ยังสูงคงเดิม")
    s += figure("fig_taste_vs_skip_2x2.png",
                "ภาพที่ 2 เหตุภาพรายตัว: ทุกตัวที่เมินเมล็ดค่าต่ำ ล้วนเคยชิมอาหารที่ดีกว่ามาก่อน "
                "ช่อง &lsquo;เมินโดยไม่เคยชิมอาหารที่ดีกว่า&rsquo; ว่างเปล่า (0/12)")

    s += [p("4. การกระทำของ agent เข้าสู่ห่วงโซ่ระบบนิเวศแบบหน่วงเวลาได้ (พื้นฐานก่อนการทำเกษตร)", "h2")]
    s += [p("เมล็ดที่ agent เคลื่อนย้ายถูกติดตามตลอดห่วงโซ่ เมล็ด &rarr; พืช &rarr; ผล &rarr; ถูกกิน เทียบกับ control "
            "<b>ข้อมูล:</b> Phase 3 ผ่าน 3/3 ซีด; ~162.3 เมล็ดที่ถูกย้ายต่อรัน, 16.3 ห่วงโซ่ที่สำเร็จ, "
            "อัตราเทียบ control <b>1.40 เท่า</b> <b>ขอบเขต:</b> เป็นพื้นฐานก่อนการทำเกษตร (proto-farming) "
            "ไม่ใช่การทำเกษตรอย่างมีเจตนาหรือเข้าใจ")]

    s += [p("5. ตัวควบคุมแบบวิวัฒนาการ (neuroevolution) ทำงานได้ในระดับพิสูจน์แนวคิด", "h2")]
    s += [p("ตัวควบคุมแบบโครงข่ายประสาท (genome 1,281 พารามิเตอร์) ถูกวิวัฒน์ด้วย genetic algorithm ที่มี tournament "
            "selection และ elitism ประเมินผลข้ามซีดที่กันไว้ <b>ข้อมูล:</b> ตลอด 12 รุ่น (ประชากร 30) fitness ดีสุดขึ้นถึง "
            "30.0 <b>ขอบเขต:</b> พิสูจน์ว่าวงจร neuroevolution ทำงานได้ ยังไม่ใช่ผลพฤติกรรมวิวัฒน์ขนาดใหญ่")]
    s += figure("neuroevolution_learning_curve.png",
                "ภาพที่ 3 การพิสูจน์แนวคิด neuroevolution: fitness ดีสุด/เฉลี่ย ดีขึ้นตามรุ่น")

    s += [p("6. วินัยเชิงระเบียบวิธีก็เป็นผลงานในตัวเอง", "h2")]
    s += [p("ผ่านการทดสอบอัตโนมัติ 67/67; ตอนนี้ RNG ของการเคลื่อนที่ผูกกับซีดการทดลองแล้ว (แก้ 26 มิ.ย.) "
            "ทำให้การทำซ้ำหลายซีดสมเหตุสมผล; เครื่องมือวัดใหม่เป็นแบบ opt-in และไม่กระทบพฤติกรรมเดิม (byte-identical) "
            "โดย default โครงงานถือว่า <b>ผลลบเป็นหลักฐาน</b> และเขียนกรอบ &lsquo;อ้างได้ / ห้ามอ้าง&rsquo; กำกับทุกผล")]

    s += [PageBreak()]
    s += [p("ส่วนที่ 2 &mdash; จุดที่โครงงานยังติด (ปัญหาที่ยังเปิดอยู่)", "h1")]
    s += [p("<b>ตัวบล็อก: ประชากรที่มีอายุขัยยังสูญพันธุ์ในระยะยาว</b> สิ่งที่น่าสนใจคือรากของปัญหาถูก "
            "<i>ระบุให้แคบลงเรื่อย ๆ ด้วยหลักฐาน</i> ไม่ใช่การเดา:")]
    s += [numbered([
        "ตอนแรกสงสัย <b>อัตราการเกิด (fecundity)</b> ต่ำ &rarr; ตัดทิ้ง: fecundity เพศเมียแตะระดับใกล้ทดแทน",
        "ต่อมา <b>พลวัตประชากร</b> &rarr; density dependence แบบหน่วงทำให้เกิดการแกว่ง boom-crash แต่การจูนก็ไม่ช่วยให้รอด",
        "ต่อมา <b>การเข้าถึงอาหาร (foraging access)</b> &rarr; วัดตรง: agent รับรู้อาหารแค่รัศมี ~4 ช่อง ขณะที่อาหารจริงเบาบางกว่า "
        "ที่ความหนาแน่นสมจริงจึงมี <b>agent 0% ที่รับรู้อาหารได้</b> และการกินทรุด (drain:intake ~453:1)",
        "<b>Option ก (28 มิ.ย.) แก้ foraging access สำเร็จ</b> &mdash; เศรษฐกิจพืชแบบ seed rain ปลุก plant lifecycle "
        "(0 &rarr; ~6,800 ผล) และรัศมีการรับรู้แบบ &lsquo;กลิ่น&rsquo; ที่แยกจากสายตา ยกสัดส่วนการรับรู้ 0.04 &rarr; 0.77 "
        "(meal rate x6.5) บนอาหารพืชล้วน โดยไม่มี crutch เทียม agent ที่กระจายตัวถึง <b>energy surplus 200-550</b> "
        "&mdash; access ไม่ใช่คอขวดอีกต่อไป (พิสูจน์ด้วย surplus ที่วัดได้)",
        "<b>คอขวดเลื่อนไปชั้นที่ลึกกว่า: spatial-demographic</b> telemetry ใหม่เผยโหมดความล้มเหลวอย่างตรงไปตรงมา: "
        "หลัง crash อาหารโลกดูเหมือนพอ (food-per-capita 5.2 &rarr; 19.83) แต่ <b>อาหารต่อหัวรอบ cluster เป็น 0.0</b> "
        "&mdash; agent อดตายเฉพาะที่ ขณะที่อาหารกองอยู่ที่อื่น",
    ])]
    s += [p("ความขัดแย้งปัจจุบัน: <b>การกระจุก</b> (เพื่อหาคู่) &rarr; อาหารเฉพาะที่พร่อง &rarr; อดตายเฉพาะที่; "
            "<b>การกระจาย</b> (เพื่อหากิน) &rarr; คู่อยู่ไกลกัน &rarr; Allee effect การเกิดจางลง; บวกกับ "
            "<b>การตายแบบอายุขัยพร้อมกัน</b> ที่ทำให้เกิดคลื่นการตาย (death-window CV 0.93) ตัวอย่าง baseline: "
            "สูญพันธุ์ที่ tick 549, ประชากรสูงสุด 148, เกิด 114, ตาย = 123 อายุขัย / 37 อดอยาก / 4 ความทนทานหมด")]
    s += figure("fig1_energy_budget.png",
                "ภาพที่ 4 คอขวดพลังงานเดิม (drain เทียบ intake) ที่การแก้ foraging access ลบออกไปแล้ว "
                "ตัวบล็อกที่เหลือตอนนี้เป็นเชิงประชากร ไม่ใช่เชิงพลังงาน")
    s += [p("<b>รายงานนี้เป็น honest negative</b> ทุก &lsquo;ความล้มเหลว&rsquo; ทำให้คำถามคมขึ้นและตัดทางเลือกอื่นออก "
            "ซึ่งเป็นวิธีที่ทำให้พบคอขวดจริง การคลายความขัดแย้งระหว่างการกระจุกกับการกระจาย และการทำให้การตายไม่พร้อมกัน "
            "บนโลกที่มี carrying capacity จริง คือการทดลองขั้นถัดไป ไม่ใช่ผลที่แก้เสร็จแล้ว")]

    s += [p("ส่วนที่ 3 &mdash; สิ่งที่โครงงาน &lsquo;ไม่อ้าง&rsquo; (เพื่อความชัดเจน)", "h1")]
    s += [bullets([
        "การทำเกษตรอย่างมีเจตนา หรือความเข้าใจเชิงความหมายของเมล็ด",
        "การถ่ายทอดความรู้เรื่องอาหารทางสังคม (แสดงได้แค่การเรียนรู้รายตัว)",
        "วิวัฒนาการแบบเปิดที่เสถียรข้ามรุ่น (ประชากรยังอยู่รอดไม่ได้)",
        "ผลบวกบางส่วนถูกแยกในสภาวะที่ปรับค่าหรือมีพลังงานเหลือเฟือ เพื่อแยกทีละกลไก ซึ่งระบุกำกับไว้ทุกที่ที่เกี่ยวข้อง",
    ])]

    s += [p("ส่วนที่ 4 &mdash; จุดที่อยากได้คำแนะนำจากอาจารย์ที่ปรึกษา", "h1")]
    s += [numbered([
        "<b>พลวัตประชากร / นิเวศวิทยาเชิงทฤษฎี:</b> ความขัดแย้งการกระจุก-กระจาย ควรวางกรอบเป็นปัญหา metapopulation / Allee "
        "หรือไม่ และกลไกที่น้อยที่สุดแบบใดจะทำให้ประชากรที่มีอายุขัยลู่เข้าหา carrying capacity จริงได้",
        "<b>การออกแบบการทดลองและสถิติ:</b> ทำให้โปรโตคอลยืนยันหลายซีดคมขึ้น (effect size, ช่วงความเชื่อมั่น, "
        "การทดสอบแบบ non-parametric) เพื่อยกผลการเรียนรู้คุณค่าอาหารให้ถึงระดับตีพิมพ์",
        "<b>การวางกรอบและขอบเขต:</b> ผลใดเด่นที่สุดที่ควรชูนำสำหรับ YSC / ISEF และรางวัล Junior Young Rising Stars "
        "และจะวางขอบเขตข้ออ้างอย่างไรให้ยังป้องกันได้",
    ])]
    s += [p("ผมมี CV, บทสรุปนี้, และ codebase ที่เปิดเผยและทำซ้ำได้ทั้งหมดพร้อมคลังรายงานครบถ้วน "
            "หากอาจารย์กรุณาให้คำแนะนำแม้เพียงสั้น ๆ ผมจะขอบพระคุณอย่างยิ่ง และยินดีอย่างยิ่งที่จะได้พูดคุยเรื่องโครงงานเพิ่มเติม")]

    s += [p("หมายเหตุระเบียบวิธี", "h1")]
    s += [p("เป็นการจำลองชีวิตเทียมแบบ agent-based ด้วย Python โลกประกอบด้วยกริด, การเกิดอาหาร, วงจรชีวิตพืช, เมล็ด, "
            "การสูญเสียพลังงาน, แบบจำลองเมแทบอลิซึม (องค์ประกอบอาหาร &rarr; พลังงานในร่าง ไม่ใช่รางวัลเชิงสัญลักษณ์), "
            "ผลกลางวัน-กลางคืนและฤดูกาล, ความจำของ agent, เงื่อนไขการสืบพันธุ์, การติดตามสายพันธุ์ และ telemetry การทดลอง "
            "control ที่ใช้ได้แก่ baseline ตำแหน่งสุ่มและตำแหน่งปัจจุบัน, การตัดความจำ (ablation), การแยก state, "
            "การเปิด/ปิดกลไก, และการทำซ้ำหลายซีด การสืบพันธุ์ถูกกำกับด้วยพลังงาน <i>และ</i> ความทนทานของร่างกาย "
            "(ความทนทาน 10 &rarr; เกิด 0; ความทนทาน 26 &rarr; เกิด 50 ภายใต้พลังงานเท่ากัน) "
            "จึงเป็นเหตุผลว่าทำไมพลังงานเหลือเฟืออย่างเดียวยังไม่ทำให้เกิดลูกทันที")]

    s += [p("ดัชนีแหล่งอ้างอิง (รายงานหลักใน repository)", "h1")]
    s += [table([
        ["หัวข้อ", "ไฟล์"],
        ["ผล Phase 1-3", "reports/phase3/phase1_to_phase3_research_success_report_2026-06-13.th.md"],
        ["การเรียนรู้คุณค่าอาหาร", "reports/food_value_learning_paper_2026-06-19.th.md"],
        ["การเรียนรู้รายตัว", "reports/agent_food_value_individual_tracking_2026-06-23.th.md"],
        ["การเสริมความเข้มสถิติ (Tier A)", "reports/tier_a_completion_summary_2026-06-30.th.md"],
        ["เศรษฐกิจพลังงาน", "reports/energy_economy_diagnosis_2026-06-19.th.md"],
        ["การแก้ foraging access (Option ก)", "reports/option_ga_foraging_access_results_2026-06-28.th.md"],
        ["คอขวด spatial-demographic (Option ข)", "reports/option_kho_demographic_telemetry_baseline_report_2026-06-28.th.md"],
        ["รายงานฉบับเต็มสำหรับการแข่งขัน", "reports/competition_full_report_artificial_evolution_2026-06-29.th.md"],
    ], [5.2 * cm, 11.0 * cm])]
    return s


# --------------------------------------------------------------------------- #
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONTS["regular"], 7.5)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawCentredString(A4[0] / 2, 0.85 * cm, f"Research Summary -- Chisanupong Injun -- page {doc.page}")
    canvas.restoreState()


def build(path: Path, story: list) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(path), pagesize=A4,
        rightMargin=1.6 * cm, leftMargin=1.6 * cm,
        topMargin=1.4 * cm, bottomMargin=1.4 * cm,
        title="Research Summary -- Artificial Life Simulation",
        author="Chisanupong Injun",
    ).build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return path


def main() -> None:
    en = build(OUT_DIR / "Research_Summary_EN_2026-06-30.pdf", story_en())
    th = build(OUT_DIR / "Research_Summary_TH_2026-06-30.pdf", story_th())
    print(en)
    print(th)


if __name__ == "__main__":
    main()

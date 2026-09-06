from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
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


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName=FONTS["bold"],
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17324D"),
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName=FONTS["regular"],
            fontSize=10.5,
            leading=13.5,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName=FONTS["bold"],
            fontSize=14,
            leading=17,
            textColor=colors.HexColor("#17324D"),
            spaceBefore=10,
            spaceAfter=5,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName=FONTS["bold"],
            fontSize=11.5,
            leading=14,
            textColor=colors.HexColor("#25636B"),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=FONTS["regular"],
            fontSize=9.2,
            leading=12.2,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName=FONTS["regular"],
            fontSize=7.8,
            leading=10,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=3,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName=FONTS["italic"],
            fontSize=7.8,
            leading=10,
            textColor=colors.HexColor("#4B5563"),
            alignment=TA_CENTER,
            spaceBefore=3,
            spaceAfter=6,
        ),
        "link": ParagraphStyle(
            "Link",
            parent=base["BodyText"],
            fontName=FONTS["regular"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1F5F99"),
            spaceAfter=3,
        ),
    }


S = styles()


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def bullet(items: list[str], level: int = 0) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item), leftIndent=10) for item in items],
        bulletType="bullet",
        leftIndent=12 + level * 8,
        bulletFontName=FONTS["regular"],
        bulletFontSize=8,
    )


def table(rows: list[list[str]], widths: list[float] | None = None) -> Table:
    tbl = Table(
        [[p(cell, "small") for cell in row] for row in rows],
        colWidths=widths,
        hAlign="LEFT",
    )
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F0F2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17324D")),
                ("FONTNAME", (0, 0), (-1, 0), FONTS["bold"]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return tbl


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONTS["regular"], 7)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawRightString(A4[0] - 1.35 * cm, 0.9 * cm, f"Page {doc.page}")
    canvas.restoreState()


def doc(path: Path) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=1.35 * cm,
        leftMargin=1.35 * cm,
        topMargin=1.25 * cm,
        bottomMargin=1.25 * cm,
    )


def figure(path: Path, caption: str, width_cm: float = 15.4, max_height_cm: float = 17.2) -> list:
    if not path.exists():
        return [p(f"Figure missing: {path.name}", "small")]
    img = Image(str(path))
    target_width = width_cm * cm
    target_height = img.imageHeight * (target_width / img.imageWidth)
    max_height = max_height_cm * cm
    if target_height > max_height:
        target_height = max_height
        target_width = img.imageWidth * (target_height / img.imageHeight)
    img.drawWidth = target_width
    img.drawHeight = target_height
    return [KeepTogether([img, p(caption, "caption")])]


def build_cv() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "CV_Chisanupong_Injun.pdf"
    story = []
    story += [
        p("Chisanupong Injun", "title"),
        p(
            "High School Student (Grade 10) | Deebuk Phangnga Wittayayon School | Phang Nga, Thailand",
            "subtitle",
        ),
        p("Email: chisanupong.injun@gmail.com", "link"),
        p("GitHub: https://github.com/sstangkh73/artificial-evolution", "link"),
        Spacer(1, 0.16 * cm),
        p("Research Interests", "h1"),
        p(
            "Artificial Life, emergent behavior, experience-based learning, population dynamics, complex systems, computational biology, and agent-based simulation.",
        ),
        p("Current Research Project", "h1"),
        p("<b>Artificial Life Simulation for Emergent Adaptive Behavior</b>", "h2"),
        p(
            "Independent research project investigating whether adaptive behavior can emerge from agent-environment interaction without predefined semantic labels or an explicit task utility function.",
        ),
        bullet(
            [
                "Designed and implemented a Python agent-based artificial-life simulation with ecology, energy, metabolism, memory, reproduction, and lineage-related telemetry.",
                "Collected simulation logs, quantitative behavioral data, selected figures, and report-style analyses across multiple experimental phases.",
                "Demonstrated an ecological substrate in which seed-to-plant-to-fruit-to-consumed cycles occur in the simulated world.",
                "Observed reward-place learning, seed-causality chains, and experience-based food-value learning under controlled experimental regimes.",
                "Identified population collapse as a current research bottleneck linked to energy access, reproduction gates, social clustering, and unstable population dynamics.",
                "Project scale: 22,000+ lines of Python and 9.6 GB of local generated simulation artifacts/logs.",
            ]
        ),
        p("Selected Evidence", "h1"),
        table(
            [
                ["Area", "Evidence summary"],
                ["Ecology", "Phase 1 passed 5/5 seeds for seed -> plant -> fruit -> consumed substrate."],
                ["Learning", "Phase 2 reward-place learning showed mean return lift of 41.7x over random-position baseline."],
                ["Food-value learning", "In an energy-surplus regime, low-value seed consumption fell from 236 to 5 per 1000 ticks with value-learning enabled."],
                ["Per-agent trace", "10/10 seed-skipping agents in a smoke run had direct taste records for both seed and plant; no social transmission claim yet."],
                ["Population dynamics", "Current blocker is long-run population stability, including boom-crash, Allee effects, and density-delay dynamics."],
            ],
            [3.0 * cm, 13.0 * cm],
        ),
        p("Technical Skills", "h1"),
        bullet(
            [
                "Programming: Python",
                "Research tooling: agent-based simulation, data analysis, scientific visualization, Git, GitHub",
                "Scientific workflow: hypothesis tracking, negative-result analysis, experiment logs, reproducibility notes",
            ]
        ),
        p("Education", "h1"),
        p("<b>Grade 10, 2026-Present</b><br/>Deebuk Phangnga Wittayayon School, Phang Nga, Thailand"),
        p("Selected Project Materials", "h1"),
        p("Repository: https://github.com/sstangkh73/artificial-evolution", "link"),
    ]
    doc(path).build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return path


def build_project_materials() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "Project_Materials_Artificial_Life_MRaD_Chisanupong_Injun.pdf"
    story = []
    story += [
        p("Project Materials", "title"),
        p(
            "Artificial Life Simulation for Emergent Adaptive Behavior | Prepared for advisor review | June 23, 2026",
            "subtitle",
        ),
        p("Student: Chisanupong Injun | Email: chisanupong.injun@gmail.com", "link"),
        p("GitHub: https://github.com/sstangkh73/artificial-evolution", "link"),
        p("Research Question", "h1"),
        p(
            "Can adaptive behavior or knowledge-like behavior emerge from interaction with a simulated environment when agents are not given predefined semantic labels, explicit instructions about resource use, or a hand-authored task utility function?",
        ),
        p("Working Framing", "h2"),
        p(
            "This project studies artificial agents living inside an ecology with energy, metabolism, food resources, plants, seeds, and population dynamics. The current evidence is strongest for experience-based learning and ecological interaction. It does not yet support claims of intentional farming, social transmission, or stable open-ended evolution.",
        ),
        p("Source Review", "h2"),
        p(
            "This document was synthesized after reviewing the historical report archive in the repository. Detailed claims are grounded primarily in the reports listed in the source index at the end of this document, including phase reports, food-value learning reports, metabolism reports, and population-dynamics investigations.",
        ),
        p("MRaD Structure", "h1"),
        p("The main body follows MRaD: Methods, Results, and Discussion, with limitations and next steps included in the discussion section."),
        PageBreak(),
        p("Methods", "h1"),
        p("Simulation Substrate", "h2"),
        p(
            "The system is a Python agent-based artificial-life simulation. The world includes a grid environment, food spawning, plant lifecycle, seeds, energy drain, metabolism, day-night and seasonal effects, agent memory, reproduction gates, lineage tracking, and experimental telemetry.",
        ),
        table(
            [
                ["Component", "Role in the project"],
                ["World ecology", "Provides plants, fruits, seeds, food availability, and delayed ecological consequences."],
                ["Agents", "Move, eat, remember food locations, interact with seeds, consume energy, and may reproduce when gates are satisfied."],
                ["Metabolism", "Turns food composition into embodied energy consequences rather than symbolic reward labels."],
                ["Telemetry", "Records logs, per-run summaries, event traces, diet-by-kind metrics, agent-level diet state, and population dynamics."],
                ["Controls", "Use baselines, random-position controls, current-position controls, memory ablations, state decoupling, and negative-result analysis."],
            ],
            [3.4 * cm, 12.6 * cm],
        ),
        p("Experimental Sequence", "h2"),
        bullet(
            [
                "Phase 1 tested whether the ecology can produce a seed -> plant -> fruit -> consumed cycle.",
                "Phase 2 tested reward-place learning by measuring return behavior after agents consumed plant-derived food.",
                "Phase 3 tested whether agent-moved seeds can re-enter the plant lifecycle and later produce consumed food.",
                "Phase 4 and 4.1 tested productive seed-drop patches and then narrowed the claim through falsification.",
                "Phase 5 tested seed-placement/site-selection and found hunger-state confounding rather than clear site-selection learning.",
                "Food-value studies tested whether agents can learn to avoid low-value edible resources from experience.",
                "Population-dynamics studies investigated why long-run mortal populations still collapse.",
            ]
        ),
        p("Measurement Philosophy", "h2"),
        p(
            "The project treats negative results as evidence. A result is not promoted from 'behavioral pattern' to 'knowledge' unless controls rule out simpler explanations such as food hotspots, hunger pressure, deterministic movement, or shared foraging corridors.",
        ),
        PageBreak(),
        p("Results", "h1"),
        p("1. Ecological substrate is present", "h2"),
        p(
            "Phase 1 passed 5/5 seeds in the tuned 100 x 100 world. The measured substrate produced seed germination, mature plants, fruiting, and plant-lifecycle food consumed by agents. Mean values included 139.0 germinated seeds, 33.6 mature plants, 68.6 fruiting events, and 47.8 plant-food consumptions per run.",
        ),
        p("2. Reward-place learning is measurable", "h2"),
        p(
            "Phase 2 passed 3/3 seeds using a strict leave-then-return metric. Agents returned near previous plant-food reward locations far more often than a random-position baseline. Mean owner return lift was 41.7x, with per-seed lifts of 52.7x, 38.7x, and 33.7x.",
        ),
        p("3. Agent actions can enter delayed ecological chains", "h2"),
        p(
            "Phase 3 passed 3/3 seeds. Agent-moved seeds entered seed-to-plant-to-fruit-to-consumed chains. Mean moved seeds were 162.3 per run, mean completed moved-seed chains were 16.3, and moved/control completed-chain lift averaged 1.40x. This supports a proto-farming substrate claim, not an intentional farming claim.",
        ),
        p("4. Patch productivity exists, but ownership claims narrowed", "h2"),
        p(
            "Phase 4 produced repeated productive patches in the tuned 100 x 100 world. Phase 4.1 then showed that non-dropper return lift was also high and the 200 x 200 condition failed under the tested budget. The revised claim is narrower: productive seed-drop patches exist in the tuned world, but agent-specific managed-patch ownership is not yet established.",
        ),
        p("5. Site selection is not yet supported", "h2"),
        p(
            "Phase 5.5 did not pass site-selection gates. Baseline drops were dominated by critical hunger, with critical-hunger drop fraction around 0.979. Blocking critical-hunger drops cleaned the state confound but collapsed activity to about 14-15 drops per run, too low for a strong chain signal. Reward-memory ablations did not change the pattern enough to explain site selection.",
        ),
        PageBreak(),
        p("Results Continued", "h1"),
        p("6. Experience-based food-value learning is the strongest current positive result", "h2"),
        p(
            "The food-value experiments added a low-value edible resource and measured whether agents could learn from the energy consequences of eating. The baseline architecture was value-blind at consumption time: agents consumed food that fit the mouth without considering long-term value. With experience-based value memory enabled and energy scarcity controlled, low-value seed consumption fell sharply over time.",
        ),
        table(
            [
                ["Window", "No value-learning", "Value-learning enabled"],
                ["0-1k ticks", "591 low-value seed meals", "236 low-value seed meals"],
                ["1-2k ticks", "613", "105"],
                ["2-3k ticks", "370", "15"],
                ["3-4k ticks", "336", "5"],
                ["4-5k ticks", "392", "5"],
                ["5-6k ticks", "334", "5"],
            ],
            [3.8 * cm, 6.0 * cm, 6.0 * cm],
        ),
        *figure(
            FIG_DIR / "fig4_learning_curve.png",
            "Figure 1. Food-value learning curve. Low-value seed consumption falls under value-learning while the value-blind baseline remains high.",
        ),
        p("7. Agent-level telemetry supports individual learning, not social transmission yet", "h2"),
        p(
            "A later telemetry smoke run tracked per-agent meals, skips, and learned values. Of 12 observed agents, 10 skipped raw_seed; all 10 had direct records of tasting both raw_seed and raw_plant. The metric 'agents skipped seed without recorded taste' was 0. This supports individual experience-based learning in the smoke run, while social transmission remains unproven.",
        ),
        *figure(
            FIG_DIR / "agent_food_value_individual_tracking_2026-06-23.png",
            "Figure 2. Per-agent trajectory: plant meals, raw seed meals, and raw seed skips differ by individual experience.",
        ),
        p("Results Continued", "h1"),
        p("8. Energy economy was a shared bottleneck", "h2"),
        p(
            "Earlier runs showed permanent hunger pressure. Direct telemetry found baseline energy drain around 4.99 per agent per tick, while intake was about 0.011 per agent per tick, a drain:intake ratio near 453:1. Adding more food increased standing food but barely changed the deficit, indicating that access and metabolism were bottlenecks, not only food quantity.",
        ),
        *figure(
            FIG_DIR / "fig1_energy_budget.png",
            "Figure 3. Baseline energy budget: drain dominated intake, explaining why hunger pressure masked higher-level behavior.",
        ),
        p("9. Reproduction can be unlocked, but not yet stabilized", "h2"),
        p(
            "Energy surplus alone was not sufficient for reproduction because the reproduction gate also required durability and social conditions. Body 37 had durability 10 and could not reproduce structurally under the gate. Body 38 had durability 26 and produced 50 births under the same surplus regime, increasing population from 50 to 100. This was the first observed reproduction event in the project, but it did not solve long-run stability.",
        ),
        *figure(
            FIG_DIR / "fig3_capstone_births.png",
            "Figure 4. Reproduction unlock: body durability determines whether surplus energy can lead to births.",
        ),
        p("10. Current population collapse is a dynamics problem", "h2"),
        p(
            "Population-sustainability investigations found that long-run mortal populations still collapse. The latest interpretation is not simply 'fecundity too low': female fecundity was near replacement in several generations, but delayed density dependence produced oscillation, boom-crash, and Allee-like tail collapse. This is the main current blocker before studying stable cross-generational transmission or evolution.",
        ),
        p("Discussion", "h1"),
        p("What the evidence supports", "h2"),
        bullet(
            [
                "The simulation is no longer only an idea; it has a working ecology, experiment logs, report history, figures, and reproducible driver scripts.",
                "Agents can show reward-place learning and experience-based food-value learning under controlled regimes.",
                "Agent actions can influence delayed ecological outcomes through seed movement and plant lifecycle chains.",
                "The project has found meaningful negative results: hunger confounds site selection, patch ownership is not established, and population stability remains unsolved.",
            ]
        ),
        p("What the evidence does not yet support", "h2"),
        bullet(
            [
                "It does not yet show intentional farming or semantic understanding of seeds.",
                "It does not yet show social transmission of food knowledge.",
                "It does not yet show stable open-ended evolution across generations.",
                "It does not yet have reliable multi-seed replication where movement dynamics fully depend on the experiment seed.",
            ]
        ),
        p("Why this is scientifically interesting", "h2"),
        p(
            "The strongest current story is that adaptive behavior can appear from embodied feedback when the environment gives agents usable signals and the energy economy permits choice. The same system also reveals why higher-level claims are difficult: population dynamics, hunger pressure, and confounded controls can create behavior that looks intelligent before the evidence is strong enough.",
        ),
        p("Main next experiments", "h2"),
        bullet(
            [
                "Bind movement randomness to experiment seed so multi-seed replication becomes valid.",
                "Run confirmatory food-value learning experiments across true independent seeds and report uncertainty.",
                "Design social exposure and parent-child tests to separate individual learning from social or inherited transmission.",
                "Stabilize mortal population dynamics by adding earlier density-dependent reproduction brakes and reducing delayed boom-crash oscillation.",
                "Revisit seed placement only after balanced-state seed handling produces enough non-hunger-confounded drops.",
            ]
        ),
        p("Limitations", "h2"),
        bullet(
            [
                "Some current positive results rely on tuned or energy-surplus regimes used to isolate mechanisms.",
                "Several older 'multiple seed' runs are deterministic n=1 because movement RNG was not tied to args.seed.",
                "The most reliable claims are substrate, learning, and diagnostic claims; long-run evolution remains future work.",
                "The project needs cleaner replication, tighter controls, and a stabilized mortal population before making cross-generational knowledge claims.",
            ]
        ),
        PageBreak(),
        p("Source Index", "h1"),
        p(
            "Key reports consulted in detail while preparing this sendable summary. The repository also contains earlier diagnostic reports, protocols, and data notes that were inventoried for context.",
        ),
        table(
            [
                ["Topic", "Source file"],
                ["Project synthesis", "reports/ISEF_MASTER_PLAN_2026-06-21/01_project_synthesis.md"],
                ["Full project status", "reports/project_status_full_2026-06-20.md"],
                ["Phase 1-3 results", "reports/phase3/phase1_to_phase3_research_success_report_2026-06-13.th.md"],
                ["Phase 4 falsification", "reports/phase4/phase4_1_falsification_summary_2026-06-13.th.md"],
                ["Phase 5 state decoupling", "reports/phase5/phase5_5_state_decoupled_analysis_2026-06-13.th.md"],
                ["Food-value learning", "reports/food_value_learning_paper_2026-06-19.th.md"],
                ["Per-agent food learning", "reports/agent_food_value_individual_tracking_2026-06-23.th.md"],
                ["Energy economy", "reports/energy_economy_diagnosis_2026-06-19.th.md"],
                ["Metabolism v2", "reports/metabolism_physics_v2_tier1_results_2026-06-18.th.md"],
                ["Population stability", "reports/population_sustainability_investigation_2026-06-20.th.md"],
                ["R0/fecundity dynamics", "reports/r0_fecundity_analysis_2026-06-20.th.md"],
                ["Concept proposal", "reports/proposal/TURC2026_Concept_Proposal_Chisanuong_Injun_EN.md"],
                ["Repository overview", "README.md; docs/PROJECT_OVERVIEW.md; docs/SIMULATION_ARCHITECTURE.md"],
            ],
            [4.5 * cm, 11.5 * cm],
        ),
    ]
    doc(path).build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return path


def main() -> None:
    cv = build_cv()
    materials = build_project_materials()
    print(cv)
    print(materials)


if __name__ == "__main__":
    main()

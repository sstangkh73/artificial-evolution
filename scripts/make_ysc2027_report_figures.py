"""Figures for the YSC 2027 (29YCSS00443) report draft, from pilot S2 data.

All figures show PILOT data (seeds 1050-1099), not the confirmatory run.

    python scripts/make_ysc2027_report_figures.py \
        --run-dir data/tool_discovery_pilot_s2_selected \
        --out "reports/YSC2027_29YCSS00443_รายงานฉบับสมบูรณ์/figures"
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path
from random import Random
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

CONDITIONS = ["C0", "C1", "C2", "C3", "C4"]
# Validated categorical palette (dataviz reference instance, light mode), fixed order.
COLORS = dict(zip(CONDITIONS, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]))
LABELS = {
    "C0": "C0 สุ่ม",
    "C1": "C1 เรียนจากผลจริง",
    "C2": "C2 ผลสลับ",
    "C3": "C3 oracle",
    "C4": "C4 จำรหัสวัตถุ",
}
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e4e3dd"
FOOTER = "ข้อมูล pilot S2 (seeds 1050–1099) ไม่ใช่ผลยืนยัน · กราฟสร้างจากข้อมูลของโครงงานด้วย Python (matplotlib) โค้ดเขียนโดยใช้ Claude Code"


def setup_font() -> None:
    path = Path("C:/Windows/Fonts/THSarabunNew.ttf")
    if path.exists():
        font_manager.fontManager.addfont(str(path))
        bold = Path("C:/Windows/Fonts/THSarabunNew Bold.ttf")
        if bold.exists():
            font_manager.fontManager.addfont(str(bold))
        plt.rcParams["font.family"] = "TH Sarabun New"
    plt.rcParams.update(
        {
            "font.size": 17,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "axes.axisbelow": True,
            "figure.dpi": 200,
            "axes.labelpad": 10,
        }
    )


def load_summary(run_dir: Path) -> dict[str, dict[int, dict]]:
    out: dict[str, dict[int, dict]] = {c: {} for c in CONDITIONS}
    with (run_dir / "summary.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["condition"]][int(row["seed"])] = row
    return out


def num(row: dict, key: str) -> float | None:
    value = row.get(key, "")
    return None if value in ("", "None") else float(value)


def bootstrap_ci(values: list[float], reps: int = 10000) -> tuple[float, float]:
    rng = Random(0)
    n = len(values)
    means = sorted(mean(rng.choice(values) for _ in range(n)) for _ in range(reps))
    return means[int(0.025 * reps)], means[int(0.975 * reps) - 1]


def footer(fig) -> None:
    fig.text(0.01, 0.005, FOOTER, fontsize=12, color=MUTED, ha="left", va="bottom")


def fig_primary(summary, out: Path) -> dict:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    jitter = Random(1)
    stats = {}
    for i, c in enumerate(CONDITIONS):
        vals = [num(r, "final_net_per_alive_tick") for r in summary[c].values()]
        xs = [i + (jitter.random() - 0.5) * 0.35 for _ in vals]
        ax.scatter(xs, vals, s=14, color=COLORS[c], alpha=0.55, linewidths=0)
        m = mean(vals)
        ax.plot([i - 0.28, i + 0.28], [m, m], color=INK, linewidth=2)
        ax.annotate(f"{m:.2f}", (i + 0.3, m), va="center", fontsize=15, color=INK)
        stats[c] = m
    ax.axhline(0, color=MUTED, linewidth=1)
    ax.set_xticks(range(len(CONDITIONS)), [LABELS[c] for c in CONDITIONS])
    ax.set_ylabel("อาหารสุทธิต่อ agent-tick (ช่วง 25% สุดท้าย)")
    ax.set_title("รูปที่ 2  อาหารสุทธิช่วงท้ายของแต่ละเงื่อนไข (จุด = 1 seed, เส้น = ค่าเฉลี่ย)", loc="left", fontsize=19)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    footer(fig)
    fig.savefig(out / "fig2_primary_by_condition.png")
    plt.close(fig)
    return stats


def fig_components(summary, out: Path) -> dict:
    seeds = sorted(set(summary["C1"]) & set(summary["C2"]))

    def comp(row):
        ticks = num(row, "final_agent_ticks")
        food_minus_effort = num(row, "final_food_per_alive_tick") - num(row, "final_effort") / ticks
        return {
            "อาหาร − แรง": food_minus_effort,
            "ต้นทุนการสร้าง (ลดลง)": num(row, "final_craft_cost") / ticks,
            "ต้นทุนการเก็บวัสดุ (ลดลง)": num(row, "final_gather_cost") / ticks,
        }

    parts = {}
    for name in ["อาหาร − แรง", "ต้นทุนการสร้าง (ลดลง)", "ต้นทุนการเก็บวัสดุ (ลดลง)"]:
        diffs = []
        for s in seeds:
            a, b = comp(summary["C1"][s])[name], comp(summary["C2"][s])[name]
            # cost components: C1 saves (C2 - C1); food side: C1 - C2. Both add to the net gap.
            diffs.append(a - b if name == "อาหาร − แรง" else b - a)
        parts[name] = (mean(diffs), *bootstrap_ci(diffs))
    total = [num(summary["C1"][s], "final_net_per_alive_tick") - num(summary["C2"][s], "final_net_per_alive_tick") for s in seeds]
    parts["รวม (อาหารสุทธิ)"] = (mean(total), *bootstrap_ci(total))

    names = list(parts)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    for i, name in enumerate(names):
        m, lo, hi = parts[name]
        color = INK if name.startswith("รวม") else COLORS["C1"]
        ax.barh(i, m, height=0.55, color=color)
        ax.plot([lo, hi], [i, i], color=MUTED, linewidth=2)
        ax.annotate(f"{m:.3f}", (hi + 0.006, i), va="center", fontsize=15, color=INK)
    ax.set_yticks(range(len(names)), names)
    ax.invert_yaxis()
    ax.axvline(0, color=MUTED, linewidth=1)
    ax.set_xlabel("ส่วนที่ C1 ได้เปรียบ C2 (อาหารสุทธิต่อ agent-tick) · เส้นสีเทา = bootstrap 95% CI")
    ax.set_title("รูปที่ 3  ความได้เปรียบของ C1 เหนือ C2 มาจากส่วนไหน", loc="left", fontsize=19)
    ax.set_xlim(0, max(p[2] for p in parts.values()) * 1.2)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    footer(fig)
    fig.savefig(out / "fig3_c1_c2_components.png")
    plt.close(fig)
    return {k: list(v) for k, v in parts.items()}


def fig_learning_curve(run_dir: Path, out: Path, window: int = 100) -> dict:
    curves: dict[str, list[float]] = {}
    for c in CONDITIONS:
        per_seed = []
        for path in sorted((run_dir / "runs").glob(f"seed*_{c}.ledger.csv.gz")):
            sums: dict[int, list[float]] = {}
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    b = int(row["tick"]) // window
                    net = float(row["food"]) - float(row["effort"]) - float(row["craft"]) - float(row["gather"])
                    acc = sums.setdefault(b, [0.0, 0])
                    acc[0] += net
                    acc[1] += 1
            per_seed.append([sums[b][0] / sums[b][1] for b in sorted(sums)])
        curves[c] = [mean(seed[i] for seed in per_seed) for i in range(len(per_seed[0]))]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    for c in CONDITIONS:
        xs = [(i + 0.5) * window for i in range(len(curves[c]))]
        ax.plot(xs, curves[c], color=COLORS[c], linewidth=2)
    # Direct labels at the line ends, nudged apart so close lines stay readable.
    ends = sorted(CONDITIONS, key=lambda c: curves[c][-1])
    min_gap, placed = 0.085, {}
    for c in ends:
        y = curves[c][-1]
        if placed:
            y = max(y, max(placed.values()) + min_gap)
        placed[c] = y
    x_end = (len(curves["C0"]) - 0.5) * window
    for c in CONDITIONS:
        ax.plot([x_end, x_end + 45], [curves[c][-1], placed[c]], color=COLORS[c], linewidth=1)
        ax.annotate(LABELS[c], (x_end + 55, placed[c]), va="center", fontsize=15, color=INK)
    ax.axhline(0, color=MUTED, linewidth=1)
    ax.axvspan(1200, 1600, color=GRID, alpha=0.6, linewidth=0)
    ax.set_xlim(0, 2050)
    ax.annotate("ช่วงวัดผลหลัก", (1400, ax.get_ylim()[1]), ha="center", va="top", fontsize=14, color=MUTED)
    ax.set_xlabel("เวลา (tick)")
    ax.set_ylabel(f"อาหารสุทธิต่อ agent-tick (เฉลี่ยทุก {window} tick)")
    ax.set_title("รูปที่ 4  อาหารสุทธิตามเวลา (เฉลี่ย 50 seeds)", loc="left", fontsize=19)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    footer(fig)
    fig.savefig(out / "fig4_learning_curve.png")
    plt.close(fig)
    return {c: [round(v, 4) for v in curves[c]] for c in CONDITIONS}


def fig_discovery(summary, out: Path) -> dict:
    metrics = [
        ("functional_rate", "อัตราวัตถุที่ใช้ได้จริง\n(ระดับ A ต่อวัตถุที่สร้าง)"),
        ("reuse_delta", "การใช้ซ้ำหลังผลดี\nลบ หลังผลเสีย"),
        ("rebuild_rate", "อัตราการสร้างซ้ำ\nกลุ่มสมบัติที่เคยสำเร็จ"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(10, 4.4))
    stats = {}
    for ax, (key, title) in zip(axes, metrics):
        seeds = [s for s in summary["C1"] if num(summary["C1"][s], key) is not None and num(summary["C2"][s], key) is not None]
        pairs = [(num(summary["C2"][s], key), num(summary["C1"][s], key)) for s in seeds]
        for c2, c1 in pairs:
            ax.plot([0, 1], [c2, c1], color=GRID, linewidth=1)
        ax.scatter([0] * len(pairs), [p[0] for p in pairs], s=14, color=COLORS["C2"], zorder=3, linewidths=0)
        ax.scatter([1] * len(pairs), [p[1] for p in pairs], s=14, color=COLORS["C1"], zorder=3, linewidths=0)
        up = sum(c1 > c2 for c2, c1 in pairs)
        ax.set_xticks([0, 1], ["C2", "C1"])
        ax.set_xlim(-0.4, 1.4)
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(f"C1 สูงกว่า C2 ใน {up}/{len(pairs)} seeds", fontsize=15, color=INK)
        stats[key] = {"n": len(pairs), "c1_higher": up}
    fig.suptitle("รูปที่ 5  หลักฐานการค้นพบ: C1 กับ C2 จับคู่ตาม seed (เส้นเทา = seed เดียวกัน)", x=0.01, ha="left", fontsize=19)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    footer(fig)
    fig.savefig(out / "fig5_discovery_evidence.png")
    plt.close(fig)
    return stats


def fig_information_boundary(out: Path) -> None:
    """Schematic: what the world knows vs what each condition may see."""
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    def box(x, y, w, h, title, lines, edge):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor="#fcfcfb", edgecolor=edge, linewidth=1.6))
        ax.text(x + 0.15, y + h - 0.18, title, fontsize=17, fontweight="bold", va="top", color=INK)
        for i, line in enumerate(lines):
            ax.text(x + 0.15, y + h - 0.62 - i * 0.36, line, fontsize=15, va="top", color=INK)

    box(0.1, 0.5, 3.6, 3.6, "โลก (ซ่อนจากเอเจนต์)", [
        "• สูตรฟิสิกส์ของวัตถุ", "• คะแนนวัตถุต่อการกระทำ", "• เกณฑ์ (threshold) ของอาหาร",
        "• ผลตอบแทนเมื่อสำเร็จ", "ใช้คำนวณอาหารที่ได้จริง"], MUTED)
    box(6.2, 0.5, 3.7, 3.6, "เอเจนต์ C0 / C1 / C2 / C4", [
        "เห็น: ชนิดอาหารตรงหน้า", "เห็น: สมบัติวัตถุ (มวล ความคม ...)", "เห็น: วัสดุในมือ, พลังงานตัวเอง",
        "ได้รับ: ผลจริงหลังใช้ (อาหาร − แรง)", "ไม่เห็น: สูตร คะแนน ชื่อเครื่องมือ"], COLORS["C1"])
    ax.annotate("", xy=(6.15, 2.9), xytext=(3.75, 2.9), arrowprops=dict(arrowstyle="->", color=INK, lw=1.6))
    ax.text(4.95, 3.05, "ผลหลังการกระทำเท่านั้น", ha="center", fontsize=15, color=INK)
    ax.annotate("", xy=(3.75, 1.7), xytext=(6.15, 1.7), arrowprops=dict(arrowstyle="->", color=INK, lw=1.6))
    ax.text(4.95, 1.85, "การกระทำ: เก็บ / สร้าง / ใช้", ha="center", fontsize=15, color=INK)
    ax.text(4.95, 0.75, "C3 (oracle) เท่านั้นที่อ่านคะแนน\nผ่าน OracleView เพื่อเป็นขอบเขตบน", ha="center",
            fontsize=14, color=MUTED, va="center")
    ax.set_title("รูปที่ 1  เส้นแบ่งข้อมูลระหว่างโลกกับเอเจนต์", loc="left", fontsize=19)
    fig.text(0.01, 0.005, "แผนภาพสร้างด้วย Python (matplotlib) โค้ดเขียนโดยใช้ Claude Code", fontsize=12, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out / "fig1_information_boundary.png")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=Path("data/tool_discovery_pilot_s2_selected"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    setup_font()
    summary = load_summary(args.run_dir)
    for c in CONDITIONS:
        assert len(summary[c]) == 50, (c, len(summary[c]))
    fig_information_boundary(args.out)
    numbers = {
        "primary_means": fig_primary(summary, args.out),
        "c1_c2_components": fig_components(summary, args.out),
        "learning_curve": fig_learning_curve(args.run_dir, args.out),
        "discovery_pairs": fig_discovery(summary, args.out),
    }
    (args.out / "figure_numbers.json").write_text(json.dumps(numbers, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in numbers.items() if k != "learning_curve"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()

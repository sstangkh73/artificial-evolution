# -*- coding: utf-8 -*-
"""Tier-A per-agent food-value figures (A1, A2, A3) for the NSRU report.

Reads a per-agent diet dump produced by scripts/food_value_study_driver.py
(--dump ...) and renders three figures from data that already exists -- no new
simulation is run:

  A1  fig_taste_vs_skip_2x2.png       2x2 of (experienced a better food) x (skips
                                      low-value seed). The off-diagonal cell
                                      "skips seed without ever experiencing a
                                      better food" is empty (0) -> behaviour is
                                      tied to direct individual experience.
  A2  fig_learned_value_threshold.png learned raw_seed vs raw_plant value with
                                      the pickiness skip-threshold drawn in, so
                                      the skip is visibly "below the line", not a
                                      hardcoded label.
  A3  fig_learning_speed_hist.png     histogram of per-agent learning speed
                                      (ticks between first plant taste and first
                                      seed skip).

Usage:
  python scripts/plot_per_agent_food_value_figures.py \
      --dump .codex-temp/food_tag_smoke.json --pickiness 0.5
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 11,
    "font.family": "Tahoma", "axes.unicode_minus": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "figure.autolayout": True,
})
C = {"seed": "#B7791F", "plant": "#1F8A5B", "threshold": "#C0392B",
     "neutral": "#7F8C8D", "fill": "#0E7C7B", "empty": "#ECECEC"}


def _load_agents(dump_path: Path) -> tuple[list[dict], dict]:
    data = json.loads(dump_path.read_text(encoding="utf-8"))
    agents = list(data.get("agent_diet_summary") or [])
    metrics = data.get("agent_diet_metrics") or {}
    if not agents:
        raise SystemExit(f"no agent_diet_summary in {dump_path}")
    return agents, metrics


def fig_a1_taste_vs_skip(agents: list[dict]) -> dict:
    """2x2: rows = skips raw_seed (yes/no); cols = tasted raw_plant (yes/no).

    The scientifically critical cell is (skip=yes, tasted_plant=no): an agent
    that avoids the low-value food without ever having experienced a better one.
    It is expected to be empty.
    """
    # grid[skip_idx][taste_idx]; idx 0 = yes, 1 = no
    grid = [[0, 0], [0, 0]]
    for a in agents:
        skipped = (a.get("raw_seed_skips", 0) or 0) > 0
        tasted_plant = bool(a.get("tasted_raw_plant"))
        si = 0 if skipped else 1
        ti = 0 if tasted_plant else 1
        grid[si][ti] += 1

    fig, ax = plt.subplots(figsize=(6.2, 5.0))
    labels = [["เลี่ยงเพราะ\nมีประสบการณ์", "เมินทั้งที่\nไม่เคยรู้จักของดีกว่า"],
              ["ชิมของดีแล้ว\nแต่ยังกิน seed", "ไม่เคยชิม plant\nและไม่เคยเมิน"]]
    for si in range(2):
        for ti in range(2):
            n = grid[si][ti]
            critical_empty = (si == 0 and ti == 1)
            if n > 0:
                color = C["fill"]
            else:
                color = "#F4D6D6" if critical_empty else C["empty"]
            ax.add_patch(plt.Rectangle((ti, 1 - si), 1, 1, facecolor=color,
                                       edgecolor="white", linewidth=3))
            txt_color = "white" if n > 0 else ("#C0392B" if critical_empty else "#9AA0A0")
            ax.text(ti + 0.5, 1 - si + 0.60, str(n), ha="center", va="center",
                    fontsize=30, fontweight="bold", color=txt_color)
            ax.text(ti + 0.5, 1 - si + 0.24, labels[si][ti], ha="center",
                    va="center", fontsize=8.5, color=txt_color)
    ax.set_xlim(0, 2); ax.set_ylim(0, 2)
    ax.set_xticks([0.5, 1.5]); ax.set_xticklabels(["เคยชิม raw_plant\n(รู้ว่ามีของดีกว่า)", "ไม่เคยชิม\nraw_plant"])
    ax.set_yticks([1.5, 0.5]); ax.set_yticklabels(["เมิน\nraw_seed", "ไม่เมิน"], rotation=0)
    ax.tick_params(length=0)
    ax.grid(False)
    total = sum(sum(r) for r in grid)
    no_taste_skip = grid[0][1]
    ax.set_title(f"เอเจนต์ทุกตัวอยู่บนแนวทแยง (n={total})\n"
                 f"{no_taste_skip}/{total} ตัวเมินอาหารค่าต่ำโดยไม่เคยชิมอาหารที่ดีกว่าก่อน",
                 fontsize=10.5)
    fig.savefig(OUT / "fig_taste_vs_skip_2x2.png")
    plt.close(fig)
    return {"grid": grid, "skip_without_better_experience": no_taste_skip, "n": total}


def fig_a2_learned_value(agents: list[dict], pickiness: float) -> dict:
    seed_vals = [a["learned_raw_seed_value"] for a in agents
                 if a.get("learned_raw_seed_value") is not None]
    plant_vals = [a["learned_raw_plant_value"] for a in agents
                  if a.get("learned_raw_plant_value") is not None]
    seed_v = sum(seed_vals) / len(seed_vals) if seed_vals else 0.0
    plant_v = sum(plant_vals) / len(plant_vals) if plant_vals else 0.0
    threshold = pickiness * plant_v  # skip if learned_value < pickiness * best_known

    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    bars = ax.bar(["raw_seed\n(ค่าต่ำ)", "raw_plant\n(ดีที่สุดที่รู้จัก)"],
                  [seed_v, plant_v], color=[C["seed"], C["plant"]], width=0.55)
    ax.axhline(threshold, color=C["threshold"], ls="--", lw=2)
    ax.text(1.45, threshold + 6, f"เกณฑ์ข้าม = {pickiness:g} × ดีที่สุด = {threshold:.0f}",
            color=C["threshold"], fontsize=9, ha="right")
    for bar, v in zip(bars, [seed_v, plant_v]):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 4, f"{v:.0f}",
                ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.annotate("ต่ำกว่าเส้น → ถูกข้าม\n(ไม่ใช่เพราะป้ายกำกับ)",
                xy=(0, seed_v), xytext=(0.05, threshold - 35), fontsize=9,
                color=C["seed"], arrowprops=dict(arrowstyle="->", color=C["seed"]))
    ax.set_ylabel("ค่าอาหารที่เรียนได้ (จากพลังงานจริง)")
    ax.set_ylim(0, plant_v * 1.18)
    ax.set_title("เอเจนต์ข้าม raw_seed เพราะค่าที่เรียนได้ต่ำกว่าเกณฑ์ pickiness\n"
                 "— เป็นการตัดสินเชิงปริมาณ ไม่ใช่กฎตายตัว")
    fig.savefig(OUT / "fig_learned_value_threshold.png")
    plt.close(fig)
    return {"seed_value": seed_v, "plant_value": plant_v, "threshold": threshold}


def fig_a3_learning_speed(agents: list[dict], metrics: dict) -> dict:
    deltas = [a["delta_learning_ticks"] for a in agents
              if a.get("delta_learning_ticks") is not None]
    n = len(deltas)
    mean_d = sum(deltas) / n if n else 0.0
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    bins = range(0, (max(deltas) // 10 + 2) * 10 + 1, 10) if deltas else range(0, 61, 10)
    ax.hist(deltas, bins=bins, color=C["fill"], edgecolor="white", alpha=0.9)
    ax.axvline(mean_d, color=C["threshold"], ls="--", lw=2)
    ax.text(mean_d + 1.0, ax.get_ylim()[1] * 0.92, f"เฉลี่ย = {mean_d:.1f} ticks",
            color=C["threshold"], fontsize=9.5)
    ax.set_xlabel("ความเร็วการเรียน: ticks จากชิม plant ครั้งแรกถึงเมิน seed ครั้งแรก")
    ax.set_ylabel("จำนวนเอเจนต์")
    learners = metrics.get("agents_with_learning_speed", n)
    ax.set_title(f"เรียนไม่พร้อมกันแต่เรียนกันเกือบทั้งกลุ่ม\n"
                 f"{learners} ตัวเรียนรู้การเลี่ยง (ช่วง {min(deltas)}-{max(deltas)} ticks)")
    fig.savefig(OUT / "fig_learning_speed_hist.png")
    plt.close(fig)
    return {"n": n, "mean": mean_d, "min": min(deltas) if deltas else None,
            "max": max(deltas) if deltas else None, "deltas": sorted(deltas)}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dump", default=".codex-temp/food_tag_smoke.json",
                   help="per-agent diet dump from food_value_study_driver.py")
    p.add_argument("--pickiness", type=float, default=0.5,
                   help="diet pickiness threshold used in the run (default 0.5)")
    a = p.parse_args()
    agents, metrics = _load_agents(Path(a.dump))
    r1 = fig_a1_taste_vs_skip(agents)
    r2 = fig_a2_learned_value(agents, a.pickiness)
    r3 = fig_a3_learning_speed(agents, metrics)
    print(json.dumps({"A1": r1, "A2": r2, "A3": r3}, ensure_ascii=False, indent=2))
    print("wrote:", sorted(p.name for p in OUT.glob("fig_*.png")))

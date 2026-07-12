# -*- coding: utf-8 -*-
"""Schematic of the uninformed 2D artificial-life world for the NSRU report.
Shows agents foraging, the food types (seed/plant/fruit) with no labels, and the
key hidden-state problem: fresh (toxic) and aged (safe) fruit look identical.
Output: reports/figures/fig_world_overview.png
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch

OUT = Path(__file__).resolve().parent.parent / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "Tahoma", "axes.unicode_minus": False,
                     "figure.dpi": 150, "savefig.dpi": 150})

SEED, PLANT, FRESH, AGED, AGENT = "#B7791F", "#1F8A5B", "#C0392B", "#0F6E56", "#1F4E79"

fig, ax = plt.subplots(figsize=(7.6, 4.7))
ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")

# world box
ax.add_patch(FancyBboxPatch((0.3, 1.5), 6.2, 5.1, boxstyle="round,pad=0.02",
             linewidth=1.4, edgecolor="#7F8C8D", facecolor="#F4F7F9"))
ax.text(3.4, 6.28, "โลกจำลองสิ่งมีชีวิต 2 มิติ (ไม่มีป้ายกำกับความหมาย)",
        ha="center", va="center", fontsize=11, fontweight="bold", color="#333333")

# agents (triangles) foraging
for (x, y) in [(1.2, 5.2), (2.6, 2.6), (4.6, 4.5), (5.6, 2.9)]:
    ax.plot(x, y, marker="^", ms=15, color=AGENT, zorder=5)
    ax.text(x, y - 0.42, "AI", ha="center", fontsize=7.5, color=AGENT)

# food items
def food(x, y, color, r=0.16):
    ax.add_patch(Circle((x, y), r, color=color, zorder=4))

for (x, y) in [(1.9, 4.3), (3.3, 5.4), (5.1, 5.6)]:
    food(x, y, SEED)
for (x, y) in [(1.5, 2.7), (3.8, 3.1), (4.2, 5.3)]:
    food(x, y, PLANT)
# a fresh/aged fruit pair that look identical
food(2.9, 3.9, FRESH); food(3.5, 3.9, AGED)
ax.annotate("", xy=(3.5, 3.9), xytext=(2.9, 3.9),
            arrowprops=dict(arrowstyle="-", color="#999999", lw=0.8))
ax.text(3.2, 3.45, "หน้าตาเหมือนกัน", ha="center", fontsize=7, color="#A32D2D")

# legend inside world (single row along the bottom)
ax.text(0.55, 1.72, "●", color=SEED, fontsize=11)
ax.text(0.9, 1.72, "เมล็ด", fontsize=7.6, va="center")
ax.text(2.0, 1.72, "●", color=PLANT, fontsize=11)
ax.text(2.35, 1.72, "พืช", fontsize=7.6, va="center")
ax.text(3.2, 1.72, "●", color=FRESH, fontsize=11)
ax.text(3.55, 1.72, "ผลไม้สด=พิษ", fontsize=7.6, va="center")
ax.text(5.05, 1.72, "●", color=AGED, fontsize=11)
ax.text(5.4, 1.72, "เก่า=ปลอดภัย", fontsize=7.6, va="center")

# right side: the learning loop
bx = 7.0
ax.add_patch(FancyBboxPatch((bx, 1.5), 2.7, 5.1, boxstyle="round,pad=0.02",
             linewidth=1.4, edgecolor="#B7791F", facecolor="#FBF6EE"))
ax.text(bx + 1.35, 6.28, "เรียนรู้จากผลจริง", ha="center", fontsize=10.5,
        fontweight="bold", color="#8A5A12")
steps = ["กินอาหาร 1 คำ", "ได้พลังงานสุทธิจริง\n(พิษ = หักพลังงาน)",
         "อัปเดตค่าที่จำ\nของอาหารชนิดนั้น", "ครั้งต่อไป: กิน/ข้าม\nตามค่าที่เรียน"]
ys = [5.7, 4.55, 3.4, 2.25]
for i, (t, y) in enumerate(zip(steps, ys)):
    ax.add_patch(FancyBboxPatch((bx + 0.2, y - 0.42), 2.3, 0.84,
                 boxstyle="round,pad=0.02", linewidth=1, edgecolor="#C9A15A",
                 facecolor="white"))
    ax.text(bx + 1.35, y, t, ha="center", va="center", fontsize=7.8, color="#333333")
    if i < len(steps) - 1:
        ax.annotate("", xy=(bx + 1.35, y - 0.5), xytext=(bx + 1.35, y - 0.42),
                    arrowprops=dict(arrowstyle="-|>", color="#B7791F", lw=1.6))

# bottom banner
ax.text(5.0, 0.7, "ไม่มี oracle: ไม่มีใครบอกว่าอะไรกินได้ มีค่า หรือมีพิษ — เอเจนต์ต้องเรียนเองจากพลังงานที่ได้รับจริง",
        ha="center", va="center", fontsize=9, style="italic", color="#555555",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#EEF3F8", edgecolor="#B9C9D8"))

fig.tight_layout()
fig.savefig(OUT / "fig_world_overview.png", bbox_inches="tight")
plt.close(fig)
print("wrote", OUT / "fig_world_overview.png")

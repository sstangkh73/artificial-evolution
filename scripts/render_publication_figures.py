from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1600
HEIGHT = 1000
MARGIN = 90
BG = "#fbfaf5"
FG = "#18324a"
GRID = "#d6d2c4"
COLORS = [
    "#0b6e4f",
    "#c97b2a",
    "#7b2cbf",
    "#b23a48",
    "#2d6cdf",
    "#6b705c",
    "#ef476f",
    "#118ab2",
]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: render_publication_figures.py <publication_package_dir>")
    package_dir = Path(sys.argv[1]).resolve()
    figure_manifest = json.loads((package_dir / "figure_manifest.json").read_text(encoding="utf-8"))
    figures_dir = package_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    fonts = load_fonts()
    rendered = {
        "figure_1": str(render_condition_matrix(Path(figure_manifest["figure_1_condition_matrix"]), figures_dir / "figure_1_condition_matrix.png", fonts)),
        "figure_2": str(render_population_trajectories(Path(figure_manifest["figure_2_population_trajectories"]), figures_dir / "figure_2_population_trajectories.png", fonts)),
        "figure_3": str(render_survival_curves(Path(figure_manifest["figure_3_survival_curves"]), figures_dir / "figure_3_survival_curves.png", fonts)),
        "figure_4": str(render_reproduction_funnel(Path(figure_manifest["figure_4_reproduction_funnel"]), figures_dir / "figure_4_reproduction_funnel.png", fonts)),
        "figure_5": str(render_technology_emergence(Path(figure_manifest["figure_5_technology_emergence"]), figures_dir / "figure_5_technology_emergence.png", fonts)),
        "figure_6": str(render_failure_reasons(Path(figure_manifest["figure_6_failure_reasons"]), figures_dir / "figure_6_failure_reasons.png", fonts)),
        "figure_7": str(render_lineage_outcomes(Path(figure_manifest["figure_7_lineage_outcomes"]), figures_dir / "figure_7_lineage_outcomes.png", fonts)),
        "figure_8": str(render_condition_statistics(Path(figure_manifest["figure_8_condition_statistics"]), figures_dir / "figure_8_condition_statistics.png", fonts)),
    }
    (package_dir / "rendered_figures_manifest.json").write_text(json.dumps(rendered, indent=2), encoding="utf-8")
    for _, path in rendered.items():
        print(path)


def load_fonts() -> dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    candidates = [
        ("C:/Windows/Fonts/tahomabd.ttf", 34),
        ("C:/Windows/Fonts/tahoma.ttf", 24),
        ("C:/Windows/Fonts/tahoma.ttf", 18),
    ]
    fonts = {}
    keys = ["title", "body", "small"]
    for key, (path, size) in zip(keys, candidates):
        try:
            fonts[key] = ImageFont.truetype(path, size=size)
        except Exception:
            fonts[key] = ImageFont.load_default()
    return fonts


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def new_canvas(title: str, fonts: dict[str, ImageFont.ImageFont]) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.text((MARGIN, 28), title, fill=FG, font=fonts["title"])
    draw.line((MARGIN, 74, WIDTH - MARGIN, 74), fill=GRID, width=3)
    return image, draw


def save(image: Image.Image, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path


def render_condition_matrix(source: Path, out: Path, fonts: dict[str, ImageFont.ImageFont]) -> Path:
    rows = read_csv_rows(source)
    image, draw = new_canvas("Figure 1. Condition Matrix", fonts)
    headers = ["condition_id", "body_index", "initial_population", "max_ticks", "founder_mode", "spawn_strategy"]
    widths = [300, 100, 140, 110, 250, 220]
    x = MARGIN
    y = 110
    for header, width in zip(headers, widths):
        draw.rectangle((x, y, x + width, y + 42), fill="#214e6b")
        draw.text((x + 8, y + 10), header, fill="white", font=fonts["small"])
        x += width
    y += 42
    for idx, row in enumerate(rows):
        x = MARGIN
        fill = "#edf2f4" if idx % 2 == 0 else "#dfe7eb"
        for header, width in zip(headers, widths):
            draw.rectangle((x, y, x + width, y + 44), fill=fill, outline="#c7d0d8")
            draw.text((x + 8, y + 12), str(row[header])[:32], fill=FG, font=fonts["small"])
            x += width
        y += 44
    return save(image, out)


def render_population_trajectories(source: Path, out: Path, fonts: dict[str, ImageFont.ImageFont]) -> Path:
    rows = read_csv_rows(source)
    grouped: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    max_tick = 0
    max_pop = 0.0
    for row in rows:
        condition = row["condition_id"]
        tick = int(float(row["tick"]))
        pop = float(row["population"])
        grouped[condition][tick].append(pop)
        max_tick = max(max_tick, tick)
        max_pop = max(max_pop, pop)
    image, draw = new_canvas("Figure 2. Population Trajectories", fonts)
    plot = (MARGIN, 140, WIDTH - MARGIN, HEIGHT - 120)
    draw_axes(draw, plot, max_tick, max_pop, fonts, "tick", "population")
    for idx, (condition, tick_map) in enumerate(grouped.items()):
        color = COLORS[idx % len(COLORS)]
        points = []
        for tick in sorted(tick_map):
            values = tick_map[tick]
            median = sorted(values)[len(values) // 2]
            points.append(scale_point(plot, tick, median, max_tick, max_pop))
        if len(points) > 1:
            draw.line(points, fill=color, width=4)
        draw.text((plot[2] - 300, 160 + idx * 28), condition, fill=color, font=fonts["small"])
    return save(image, out)


def render_survival_curves(source: Path, out: Path, fonts: dict[str, ImageFont.ImageFont]) -> Path:
    rows = read_csv_rows(source)
    grouped: dict[str, list[tuple[int, float]]] = defaultdict(list)
    max_tick = 0
    for row in rows:
        tick = int(float(row["tick"]))
        grouped[row["condition_id"]].append((tick, float(row["population_survival_fraction"])))
        max_tick = max(max_tick, tick)
    image, draw = new_canvas("Figure 3. Survival Curves", fonts)
    plot = (MARGIN, 140, WIDTH - MARGIN, HEIGHT - 120)
    draw_axes(draw, plot, max_tick, 1.0, fonts, "tick", "survival")
    for idx, (condition, items) in enumerate(grouped.items()):
        color = COLORS[idx % len(COLORS)]
        points = [scale_point(plot, tick, value, max_tick, 1.0) for tick, value in sorted(items)]
        if len(points) > 1:
            draw.line(points, fill=color, width=4)
        draw.text((plot[2] - 320, 160 + idx * 28), condition, fill=color, font=fonts["small"])
    return save(image, out)


def render_reproduction_funnel(source: Path, out: Path, fonts: dict[str, ImageFont.ImageFont]) -> Path:
    rows = read_csv_rows(source)
    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["condition_id"]][row["stage"]].append(float(row["count"]))
    stages = ["founders", "births", "matured_children", "gen3_success"]
    image, draw = new_canvas("Figure 4. Reproduction Funnel", fonts)
    left = MARGIN + 40
    top = 170
    max_value = max((sum(vals) / len(vals) for stage_map in grouped.values() for vals in stage_map.values()), default=1.0)
    for c_idx, (condition, stage_map) in enumerate(grouped.items()):
        draw.text((left + c_idx * 250, top - 40), condition, fill=FG, font=fonts["small"])
        for s_idx, stage in enumerate(stages):
            avg = sum(stage_map.get(stage, [0.0])) / max(1, len(stage_map.get(stage, [0.0])))
            bar_h = int((avg / max_value) * 520) if max_value else 0
            x0 = left + c_idx * 250 + s_idx * 48
            y0 = HEIGHT - 140 - bar_h
            draw.rectangle((x0, y0, x0 + 34, HEIGHT - 140), fill=COLORS[s_idx % len(COLORS)])
            draw.text((x0 - 4, HEIGHT - 132), stage[:6], fill=FG, font=fonts["small"])
    return save(image, out)


def render_technology_emergence(source: Path, out: Path, fonts: dict[str, ImageFont.ImageFont]) -> Path:
    rows = read_csv_rows(source)
    grouped: dict[str, list[float]] = defaultdict(list)
    max_tick = 1.0
    for row in rows:
        if row["first_technology_tick"]:
            tick = float(row["first_technology_tick"])
            grouped[row["condition_id"]].append(tick)
            max_tick = max(max_tick, tick)
    image, draw = new_canvas("Figure 5. Technology Emergence", fonts)
    plot = (MARGIN + 120, 170, WIDTH - MARGIN, HEIGHT - 140)
    draw.rectangle(plot, outline=GRID, width=2)
    conditions = list(grouped.keys())
    for idx, condition in enumerate(conditions):
        x = plot[0] + int(idx * (plot[2] - plot[0]) / max(1, len(conditions)))
        draw.text((x + 10, plot[3] + 10), condition[:20], fill=FG, font=fonts["small"])
        for tick in grouped[condition]:
            y = plot[3] - int((tick / max_tick) * (plot[3] - plot[1] - 20))
            draw.ellipse((x + 20, y, x + 32, y + 12), fill=COLORS[idx % len(COLORS)])
    draw.text((MARGIN, 200), "first tech tick", fill=FG, font=fonts["body"])
    return save(image, out)


def render_failure_reasons(source: Path, out: Path, fonts: dict[str, ImageFont.ImageFont]) -> Path:
    rows = read_csv_rows(source)
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    reason_keys = ["low_energy", "not_near_nest", "nest_food_low", "no_mate", "no_nest"]
    for row in rows:
        details = (row.get("details") or row.get("raw_text") or "")
        for reason in reason_keys:
            if reason in details:
                counts[row["condition_id"]][reason] += 1
    image, draw = new_canvas("Figure 6. Reproduction Failure Reasons", fonts)
    x = MARGIN + 100
    y = 170
    for idx, (condition, reason_map) in enumerate(counts.items()):
        draw.text((x, y + idx * 90), condition, fill=FG, font=fonts["small"])
        bar_x = x + 260
        total = sum(reason_map.values()) or 1
        cursor = bar_x
        for r_idx, reason in enumerate(reason_keys):
            width = int((reason_map.get(reason, 0) / total) * 800)
            draw.rectangle((cursor, y + idx * 90, cursor + width, y + idx * 90 + 28), fill=COLORS[r_idx % len(COLORS)])
            cursor += width
        legend_y = 780
    for r_idx, reason in enumerate(reason_keys):
        draw.rectangle((MARGIN + r_idx * 210, legend_y, MARGIN + r_idx * 210 + 24, legend_y + 24), fill=COLORS[r_idx % len(COLORS)])
        draw.text((MARGIN + r_idx * 210 + 30, legend_y + 2), reason, fill=FG, font=fonts["small"])
    return save(image, out)


def render_lineage_outcomes(source: Path, out: Path, fonts: dict[str, ImageFont.ImageFont]) -> Path:
    rows = read_csv_rows(source)
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        grouped[row["condition_id"]] += float(row.get("peak_population") or 0)
    items = sorted(grouped.items(), key=lambda item: item[1], reverse=True)
    max_value = items[0][1] if items else 1.0
    image, draw = new_canvas("Figure 7. Aggregate Lineage Peak Outcomes", fonts)
    for idx, (condition, value) in enumerate(items):
        y = 180 + idx * 90
        draw.text((MARGIN, y + 10), condition, fill=FG, font=fonts["small"])
        width = int((value / max_value) * 900)
        draw.rectangle((MARGIN + 320, y, MARGIN + 320 + width, y + 38), fill=COLORS[idx % len(COLORS)])
        draw.text((MARGIN + 330 + width, y + 10), f"{value:.0f}", fill=FG, font=fonts["small"])
    return save(image, out)


def render_condition_statistics(source: Path, out: Path, fonts: dict[str, ImageFont.ImageFont]) -> Path:
    rows = read_csv_rows(source)
    image, draw = new_canvas("Figure 8. Condition-Level Statistics", fonts)
    headers = ["condition_id", "gen3_success_rate", "extinction_rate", "first_technology_tick_mean", "peak_population_mean"]
    widths = [320, 170, 150, 220, 200]
    x = MARGIN
    y = 140
    for header, width in zip(headers, widths):
        draw.rectangle((x, y, x + width, y + 42), fill="#214e6b")
        draw.text((x + 8, y + 10), header, fill="white", font=fonts["small"])
        x += width
    y += 42
    for idx, row in enumerate(rows):
        x = MARGIN
        fill = "#edf2f4" if idx % 2 == 0 else "#dfe7eb"
        for header, width in zip(headers, widths):
            draw.rectangle((x, y, x + width, y + 44), fill=fill, outline="#c7d0d8")
            draw.text((x + 8, y + 12), str(row[header])[:24], fill=FG, font=fonts["small"])
            x += width
        y += 44
    return save(image, out)


def draw_axes(draw: ImageDraw.ImageDraw, plot: tuple[int, int, int, int], max_x: float, max_y: float, fonts: dict[str, ImageFont.ImageFont], x_label: str, y_label: str) -> None:
    x0, y0, x1, y1 = plot
    draw.rectangle(plot, outline=GRID, width=2)
    for i in range(6):
        y = y1 - int(i * (y1 - y0) / 5)
        draw.line((x0, y, x1, y), fill=GRID, width=1)
        value = round((i / 5) * max_y, 2)
        draw.text((x0 - 60, y - 10), str(value), fill=FG, font=fonts["small"])
    for i in range(6):
        x = x0 + int(i * (x1 - x0) / 5)
        draw.line((x, y0, x, y1), fill=GRID, width=1)
        value = round((i / 5) * max_x)
        draw.text((x - 10, y1 + 10), str(value), fill=FG, font=fonts["small"])
    draw.text((x1 - 50, y1 + 45), x_label, fill=FG, font=fonts["body"])
    draw.text((x0 - 70, y0 - 40), y_label, fill=FG, font=fonts["body"])


def scale_point(plot: tuple[int, int, int, int], x: float, y: float, max_x: float, max_y: float) -> tuple[int, int]:
    x0, y0, x1, y1 = plot
    px = x0 + int((x / max_x) * (x1 - x0)) if max_x else x0
    py = y1 - int((y / max_y) * (y1 - y0)) if max_y else y1
    return (px, py)


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path


def build_dashboard_artifacts(output_dir: Path, payload: dict[str, object]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "telemetry.json"
    html_path = output_dir / "index.html"

    json_text = json.dumps(payload, indent=2)
    json_path.write_text(json_text, encoding="utf-8")
    html_path.write_text(_build_html(payload), encoding="utf-8")
    return html_path, json_path


def _build_html(payload: dict[str, object]) -> str:
    embedded = json.dumps(payload)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Artificial Evolution Dashboard</title>
  <style>
    :root {{
      --bg: #f5efe3;
      --panel: #fffaf1;
      --ink: #1f2a2e;
      --muted: #6e7468;
      --line: #d4cab8;
      --safe-low: #dce8cc;
      --safe-high: #a9d67f;
      --danger-high: #f6b26b;
      --danger-low: #b85c38;
      --food: #277a3b;
      --death: #a61b1b;
      --nest: #5d4037;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #fff7d6 0, transparent 28%),
        linear-gradient(180deg, #f6f2e8 0%, #efe3ce 100%);
    }}
    .page {{
      max-width: 1500px;
      margin: 0 auto;
      padding: 20px;
    }}
    h1, h2 {{
      margin: 0 0 10px 0;
      letter-spacing: 0.02em;
    }}
    .lede {{
      color: var(--muted);
      margin-bottom: 18px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .card, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      box-shadow: 0 12px 28px rgba(73, 56, 32, 0.08);
    }}
    .card {{
      padding: 12px 14px;
    }}
    .card .label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .card .value {{
      font-size: 28px;
      font-weight: 700;
      margin-top: 6px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 1.25fr 0.75fr;
      gap: 16px;
    }}
    .panel {{
      padding: 14px;
      margin-bottom: 16px;
    }}
    .panel h2 {{
      font-size: 18px;
    }}
    .panel-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }}
    .controls {{
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }}
    .controls button, .controls select {{
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      padding: 8px 12px;
      border-radius: 999px;
      cursor: pointer;
    }}
    .controls input[type="range"] {{
      flex: 1;
      min-width: 220px;
    }}
    canvas {{
      width: 100%;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: #fffef9;
      display: block;
    }}
    #worldCanvas {{
      aspect-ratio: 1 / 1;
    }}
    #timelineCanvas {{
      height: 240px;
    }}
    #heatmapCanvas {{
      aspect-ratio: 1 / 1;
    }}
    .legend {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 10px;
      color: var(--muted);
      font-size: 12px;
    }}
    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 6px;
      vertical-align: middle;
    }}
    .list {{
      display: grid;
      gap: 8px;
      max-height: 420px;
      overflow: auto;
    }}
    .list-item {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 12px;
      background: rgba(255, 255, 255, 0.72);
    }}
    .list-item strong {{
      display: block;
      margin-bottom: 4px;
    }}
    .meta {{
      color: var(--muted);
      font-size: 13px;
    }}
    .footer-note {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 8px;
    }}
    @media (max-width: 1100px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <h1>Artificial Evolution World Dashboard</h1>
    <div class="lede" id="headline"></div>

    <div class="cards" id="summaryCards"></div>

    <div class="layout">
      <div>
        <div class="panel">
          <div class="panel-head">
            <h2>2D World Map</h2>
            <div class="meta">Biome colors, food, agents, nests, deaths, territory proxy</div>
          </div>
          <div class="controls">
            <button id="playButton">Play</button>
            <input id="snapshotSlider" type="range" min="0" max="0" value="0">
            <span class="meta" id="snapshotLabel"></span>
          </div>
          <canvas id="worldCanvas" width="700" height="700"></canvas>
          <div class="legend">
            <span><span class="dot" style="background: var(--food);"></span>Food</span>
            <span><span class="dot" style="background: var(--death);"></span>Deaths</span>
            <span><span class="dot" style="background: var(--nest);"></span>Nest / territory proxy</span>
          </div>
        </div>

        <div class="panel">
          <div class="panel-head">
            <h2>Timeline Graph</h2>
            <div class="meta">Population, births, deaths, storage</div>
          </div>
          <canvas id="timelineCanvas" width="980" height="240"></canvas>
          <div class="legend">
            <span><span class="dot" style="background: #304ffe;"></span>Population</span>
            <span><span class="dot" style="background: #2e7d32;"></span>Births</span>
            <span><span class="dot" style="background: #c62828;"></span>Deaths</span>
            <span><span class="dot" style="background: #8d6e63;"></span>Stored food</span>
          </div>
        </div>
      </div>

      <div>
        <div class="panel">
          <div class="panel-head">
            <h2>Heatmap</h2>
            <div class="controls">
              <select id="heatmapMetric">
                <option value="population">Population clustering</option>
                <option value="death">Death clustering</option>
                <option value="food">Food clustering</option>
              </select>
            </div>
          </div>
          <canvas id="heatmapCanvas" width="500" height="500"></canvas>
        </div>

        <div class="panel">
          <div class="panel-head">
            <h2>Lineage Tree</h2>
            <div class="meta">Founder lines and survival outcomes</div>
          </div>
          <div class="list" id="lineageList"></div>
        </div>

        <div class="panel">
          <div class="panel-head">
            <h2>Event Alerts</h2>
            <div class="meta">High-signal events only</div>
          </div>
          <div class="list" id="alertList"></div>
          <div class="footer-note">
            Replay snapshots are automatically preserved on regular intervals and important alert ticks.
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const TELEMETRY = {embedded};
    const worldCanvas = document.getElementById("worldCanvas");
    const worldCtx = worldCanvas.getContext("2d");
    const timelineCanvas = document.getElementById("timelineCanvas");
    const timelineCtx = timelineCanvas.getContext("2d");
    const heatmapCanvas = document.getElementById("heatmapCanvas");
    const heatmapCtx = heatmapCanvas.getContext("2d");
    const slider = document.getElementById("snapshotSlider");
    const playButton = document.getElementById("playButton");
    const snapshotLabel = document.getElementById("snapshotLabel");
    const heatmapMetric = document.getElementById("heatmapMetric");
    const headline = document.getElementById("headline");
    const summaryCards = document.getElementById("summaryCards");
    const lineageList = document.getElementById("lineageList");
    const alertList = document.getElementById("alertList");

    const snapshots = TELEMETRY.snapshots || [];
    const tickSummaries = TELEMETRY.tick_summaries || [];
    const alerts = TELEMETRY.alerts || [];
    const lineageStats = TELEMETRY.lineage_stats || [];
    const world = TELEMETRY.world || {{}};
    const heatmaps = TELEMETRY.heatmaps || {{}};
    let currentSnapshotIndex = 0;
    let playbackTimer = null;

    headline.textContent =
      `${{TELEMETRY.meta.title}} | body=${{TELEMETRY.meta.body_name}} | ` +
      `seed=${{TELEMETRY.meta.seed}} | ticks=${{TELEMETRY.meta.final_tick}}`;

    slider.max = Math.max(0, snapshots.length - 1);
    slider.addEventListener("input", () => {{
      currentSnapshotIndex = Number(slider.value);
      drawWorld();
    }});

    playButton.addEventListener("click", () => {{
      if (playbackTimer) {{
        clearInterval(playbackTimer);
        playbackTimer = null;
        playButton.textContent = "Play";
        return;
      }}
      playButton.textContent = "Pause";
      playbackTimer = setInterval(() => {{
        if (currentSnapshotIndex >= snapshots.length - 1) {{
          clearInterval(playbackTimer);
          playbackTimer = null;
          playButton.textContent = "Play";
          return;
        }}
        currentSnapshotIndex += 1;
        slider.value = String(currentSnapshotIndex);
        drawWorld();
      }}, 240);
    }});

    heatmapMetric.addEventListener("change", drawHeatmap);

    renderSummaryCards();
    renderLineages();
    renderAlerts();
    drawTimeline();
    drawHeatmap();
    drawWorld();

    function renderSummaryCards() {{
      const finalSummary = tickSummaries[tickSummaries.length - 1] || {{}};
      const cards = [
        ["Final population", finalSummary.population || 0],
        ["Peak population", TELEMETRY.meta.peak_population || 0],
        ["Total births", TELEMETRY.meta.total_births || 0],
        ["Settlements", finalSummary.settlements || 0],
        ["Stored food", finalSummary.stored_food || 0],
        ["Alerts", alerts.length],
      ];
      summaryCards.innerHTML = cards.map(([label, value]) => `
        <div class="card">
          <div class="label">${{label}}</div>
          <div class="value">${{value}}</div>
        </div>
      `).join("");
    }}

    function renderLineages() {{
      const sorted = [...lineageStats].sort((a, b) => (b.peak_population - a.peak_population) || a.lineage_id.localeCompare(b.lineage_id));
      lineageList.innerHTML = sorted.map((lineage) => `
        <div class="list-item">
          <strong>${{lineage.lineage_id}}</strong>
          <div class="meta">
            founder=${{lineage.founder_agent_id}} |
            peak=${{lineage.peak_population}} |
            births=${{lineage.total_births}} |
            alive=${{lineage.alive_now}} |
            extinct_tick=${{lineage.extinct_tick ?? "-"}}
          </div>
        </div>
      `).join("");
    }}

    function renderAlerts() {{
      alertList.innerHTML = alerts.map((alert) => `
        <div class="list-item">
          <strong>${{alert.type}}</strong>
          <div class="meta">tick=${{alert.tick}} | ${{alert.message}}</div>
        </div>
      `).join("");
    }}

    function drawWorld() {{
      const snapshot = snapshots[currentSnapshotIndex];
      if (!snapshot) {{
        return;
      }}

      snapshotLabel.textContent =
        `tick=${{snapshot.tick}} | pop=${{snapshot.population}} | births=${{snapshot.births}} | deaths=${{snapshot.deaths}}`;

      const width = world.width || 100;
      const height = world.height || 100;
      const scaleX = worldCanvas.width / width;
      const scaleY = worldCanvas.height / height;

      worldCtx.clearRect(0, 0, worldCanvas.width, worldCanvas.height);

      for (const biome of world.biomes || []) {{
        worldCtx.fillStyle = biome.color;
        worldCtx.fillRect(
          biome.x * scaleX,
          biome.y * scaleY,
          biome.width * scaleX,
          biome.height * scaleY
        );
      }}

      for (const nest of snapshot.nests) {{
        worldCtx.strokeStyle = "rgba(93, 64, 55, 0.35)";
        worldCtx.lineWidth = 1.2;
        worldCtx.beginPath();
        worldCtx.arc(
          (nest.x + 0.5) * scaleX,
          (nest.y + 0.5) * scaleY,
          (nest.safe_radius * scaleX),
          0,
          Math.PI * 2
        );
        worldCtx.stroke();

        worldCtx.fillStyle = "rgba(93, 64, 55, 0.95)";
        worldCtx.fillRect(nest.x * scaleX - 2, nest.y * scaleY - 2, 7, 7);
      }}

      worldCtx.fillStyle = "rgba(39, 122, 59, 0.8)";
      for (const food of snapshot.food_positions) {{
        worldCtx.fillRect(food[0] * scaleX, food[1] * scaleY, 2.5, 2.5);
      }}

      for (const death of snapshot.death_positions) {{
        worldCtx.strokeStyle = "rgba(166, 27, 27, 0.85)";
        worldCtx.beginPath();
        worldCtx.moveTo(death[0] * scaleX - 2, death[1] * scaleY - 2);
        worldCtx.lineTo(death[0] * scaleX + 2, death[1] * scaleY + 2);
        worldCtx.moveTo(death[0] * scaleX + 2, death[1] * scaleY - 2);
        worldCtx.lineTo(death[0] * scaleX - 2, death[1] * scaleY + 2);
        worldCtx.stroke();
      }}

      for (const agent of snapshot.agents) {{
        worldCtx.fillStyle = lineageColor(agent.lineage_id);
        const radius = agent.stage === "child" ? 2.6 : agent.stage === "adult" ? 4.2 : 3.4;
        worldCtx.beginPath();
        worldCtx.arc((agent.x + 0.5) * scaleX, (agent.y + 0.5) * scaleY, radius, 0, Math.PI * 2);
        worldCtx.fill();
      }}
    }}

    function drawTimeline() {{
      timelineCtx.clearRect(0, 0, timelineCanvas.width, timelineCanvas.height);
      if (!tickSummaries.length) {{
        return;
      }}

      const padding = 34;
      const plotWidth = timelineCanvas.width - (padding * 2);
      const plotHeight = timelineCanvas.height - (padding * 2);
      const maxTick = tickSummaries[tickSummaries.length - 1].tick || 1;
      const maxValue = Math.max(
        ...tickSummaries.map((item) => Math.max(item.population, item.births, item.deaths, item.stored_food))
      ) || 1;

      timelineCtx.strokeStyle = "#c9beab";
      timelineCtx.lineWidth = 1;
      timelineCtx.strokeRect(padding, padding, plotWidth, plotHeight);

      const series = [
        ["population", "#304ffe"],
        ["births", "#2e7d32"],
        ["deaths", "#c62828"],
        ["stored_food", "#8d6e63"],
      ];
      for (const [key, color] of series) {{
        timelineCtx.beginPath();
        timelineCtx.strokeStyle = color;
        timelineCtx.lineWidth = 2;
        tickSummaries.forEach((item, index) => {{
          const x = padding + (item.tick / maxTick) * plotWidth;
          const y = padding + plotHeight - ((item[key] || 0) / maxValue) * plotHeight;
          if (index === 0) {{
            timelineCtx.moveTo(x, y);
          }} else {{
            timelineCtx.lineTo(x, y);
          }}
        }});
        timelineCtx.stroke();
      }}
    }}

    function drawHeatmap() {{
      heatmapCtx.clearRect(0, 0, heatmapCanvas.width, heatmapCanvas.height);
      const key = heatmapMetric.value;
      const grid = heatmaps[key] || [];
      if (!grid.length) {{
        return;
      }}
      const rows = grid.length;
      const cols = grid[0].length;
      const cellWidth = heatmapCanvas.width / cols;
      const cellHeight = heatmapCanvas.height / rows;
      const maxValue = Math.max(...grid.flat()) || 1;

      for (let row = 0; row < rows; row += 1) {{
        for (let col = 0; col < cols; col += 1) {{
          const value = grid[row][col];
          const alpha = value / maxValue;
          const hue = key === "death" ? "0, 78%, 48%" : key === "food" ? "138, 59%, 34%" : "222, 89%, 58%";
          heatmapCtx.fillStyle = `hsla(${{hue}}, ${{Math.max(0.08, alpha * 0.92)}})`;
          heatmapCtx.fillRect(col * cellWidth, row * cellHeight, cellWidth, cellHeight);
        }}
      }}
    }}

    function lineageColor(lineageId) {{
      let hash = 0;
      for (let index = 0; index < lineageId.length; index += 1) {{
        hash = ((hash << 5) - hash) + lineageId.charCodeAt(index);
        hash |= 0;
      }}
      const hue = Math.abs(hash) % 360;
      return `hsl(${{hue}}, 70%, 46%)`;
    }}
  </script>
</body>
</html>
"""

# Artificial Evolution

## ภาษาไทย

โครงการนี้เป็นการจำลองสิ่งมีชีวิตประดิษฐ์ที่มุ่งศึกษาเรื่องการเอาชีวิตรอด
การแลกเปลี่ยนข้อดีข้อเสียของโครงสร้างร่างกาย และการเกิดพฤติกรรมซับซ้อนในระยะยาว

### ขอบเขตปัจจุบัน

รีโพซิทอรีนี้เริ่มต้นด้วยซิมเอาชีวิตรอดแบบพื้นฐาน:

- โลกขนาด `100x100`
- อาหารเกิดแบบสุ่มและมีจำนวนจำกัด
- เอเจนต์เสียพลังงานทุก tick
- ร่างกายถูกสร้างภายใต้งบต้นทุนคงที่
- ระบบกลางวัน/กลางคืนที่ทำให้การมองเห็นลดลงตอนกลางคืน
- ตัวรันซิมสำหรับเปรียบเทียบผลการอยู่รอดของแต่ละแบบ

### ทิศทางการวิจัย

เป้าหมายระยะยาวคือศึกษาว่าโครงสร้างร่างกายที่มีประสิทธิภาพ
และพฤติกรรมทางสังคมที่ซับซ้อนมากขึ้น
สามารถเกิดขึ้นเองได้หรือไม่ภายใต้แรงกดดันจากสิ่งแวดล้อมและข้อจำกัดด้านพลังงาน

### วิธีรัน

```powershell
python main.py
```

### โหมดแสดงผลโลก

สามารถสร้าง dashboard แบบ replay ได้ด้วย:

```powershell
python main.py --mode dashboard --seed 7 --dashboard-ticks 800 --snapshot-interval 10
```

ผลลัพธ์จะถูกสร้างใน `data/dashboards/...` เป็นทั้ง:

- `index.html` สำหรับดู world map, timeline, heatmap, lineage, alerts, replay
- `telemetry.json` สำหรับวิเคราะห์ต่อหรือทำ visualization เพิ่ม

### โหมดเก็บข้อมูลระดับงานวิจัย

สำหรับเก็บข้อมูลแบบพร้อมเขียน paper:

```powershell
python main.py --mode paper --seed 7 --paper-body-index 8 --dashboard-ticks 2000 --snapshot-interval 10
```

ผลลัพธ์จะอยู่ใน `data/research_runs/...` และประกอบด้วย:

- `metadata.json`
- `summary.json`
- `tick_metrics.csv`
- `events.jsonl`
- `lineages.csv`
- `agent_outcomes.csv`
- `methods.md`
- `dashboard/`

### โหมด publication batch

สำหรับเก็บข้อมูลหลายเงื่อนไข หลาย seed พร้อมตารางสถิติและ source data สำหรับ figure:

```powershell
python main.py --mode publication-batch --seed 7 --study-seeds 6 --dashboard-ticks 1200 --snapshot-interval 10
```

ผลลัพธ์จะกระจายเป็น 2 ชั้น:

- `data/research_runs/...` สำหรับ raw replicate bundles
- `data/publication_packages/...` สำหรับ `conditions.csv`, `replicate_index.csv`, `primary_outcomes.csv`, `condition_level_statistics.csv`, `figure_source_data/`, และไฟล์ methods / analysis plan

### โครงสร้างโปรเจกต์

- `docs/` บันทึกงานวิจัย แผนแต่ละเฟซ และกฎของโลก
- `agents/` ระบบร่างกายและตรรกะของเอเจนต์
- `world/` กฎของสภาพแวดล้อมและระบบเกิดอาหาร
- `simulation/` ลูปการทดลองและตัวจัดการซิม
- `data/` ผลลัพธ์จากการทดลอง
- `visualization/` ตัวช่วยแสดงผลและแดชบอร์ดในอนาคต

## English

This project is an artificial life simulation focused on survival, body
structure trade-offs, and long-term emergent behavior.

### Current Scope

This repository starts with a minimal survival simulation:

- A `100x100` world
- Random food spawning with a limited cap
- Agents that lose energy every tick
- Body structures built from a fixed cost budget
- Day/night cycles that reduce vision at night
- A simulation runner for comparing survival outcomes

### Research Direction

The long-term goal is to explore whether efficient body structures and more
complex social behaviors can emerge under environmental pressure and energy
constraints.

### Run

```powershell
python main.py
```

### World Dashboard Mode

You can generate a replayable dashboard with:

```powershell
python main.py --mode dashboard --seed 7 --dashboard-ticks 800 --snapshot-interval 10
```

This writes output into `data/dashboards/...` as:

- `index.html` for world-map replay, timeline, heatmap, lineage, and alert viewing
- `telemetry.json` for further analysis or custom visualization

### Research-Grade Paper Mode

For paper-ready data capture:

```powershell
python main.py --mode paper --seed 7 --paper-body-index 8 --dashboard-ticks 2000 --snapshot-interval 10
```

This writes a research bundle into `data/research_runs/...` including:

- `metadata.json`
- `summary.json`
- `tick_metrics.csv`
- `events.jsonl`
- `lineages.csv`
- `agent_outcomes.csv`
- `methods.md`
- `dashboard/`

### Publication Batch Mode

For multi-condition, multi-seed capture with aggregate statistics and figure-ready source data:

```powershell
python main.py --mode publication-batch --seed 7 --study-seeds 6 --dashboard-ticks 1200 --snapshot-interval 10
```

This writes two layers of outputs:

- `data/research_runs/...` for raw replicate bundles
- `data/publication_packages/...` for `conditions.csv`, `replicate_index.csv`, `primary_outcomes.csv`, `condition_level_statistics.csv`, `figure_source_data/`, and methods / analysis-plan files

### Robustness Batch Mode

For robustness sweeps across harsher technology-emergence and lower-food sexed conditions:

```powershell
python main.py --mode robustness-batch --seed 7 --study-seeds 4 --dashboard-ticks 1600 --snapshot-interval 20
```

### Render Publication Figures

To render PNG figures from any publication package:

```powershell
python scripts/render_publication_figures.py data/publication_packages/experiment_047_publication_batch
```

This creates `figures/` and `rendered_figures_manifest.json` inside the target package.

### Project Layout

- `docs/` research notes, phase plans, and world rules
- `agents/` body design and agent logic
- `world/` environment rules and food spawning
- `simulation/` execution loop and experiment orchestration
- `data/` generated experiment outputs
- `visualization/` simple render helpers and later dashboards

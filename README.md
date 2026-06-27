# Artificial Evolution

Artificial Evolution is an artificial life research project centered on one
primary question: can unlabeled agents learn how their world works on their
own, and can that learning compound into the emergence of technology?

The repository has moved beyond a minimal survival prototype. The current code
already includes ecological zones, family and nest systems, hidden behavioral
traits, food processing, material gathering, coordinated hunting, Tier 1 tools,
and multiple experiment pipelines for research capture.

## ภาษาไทย

### โปรเจ็กต์นี้คืออะไร

Artificial Evolution เป็นโปรเจ็กต์ artificial life ที่ตั้งคำถามหลักใหม่ว่า
เอเจนต์ที่ไม่ได้ถูกปักป้ายบอกความหมายของสิ่งต่าง ๆ ในโลก
จะเรียนรู้กติกา คุณค่าของทรัพยากร ความเสี่ยง และโอกาสได้เองหรือไม่
และเมื่อเรียนรู้ได้แล้ว ความรู้นั้นจะค่อย ๆ สะสมไปสู่การเกิดเทคโนโลยีได้หรือไม่
เช่น การใช้เครื่องมือ การแปรรูปอาหาร การจัดการทรัพยากร
และการสร้างระบบร่วมมือที่ซับซ้อนขึ้น

กล่าวอีกแบบ โปรเจ็กต์นี้ไม่ได้โฟกัสแค่ว่า "ใครรอด"
แต่โฟกัสว่า "การเรียนรู้แบบไม่มีป้ายบอกจะพาไปสู่ความสามารถใหม่ระดับเทคโนโลยีได้ไหม"

### คำถามวิจัยหลัก

- เอเจนต์จะเรียนรู้โลกโดยไม่มี label หรือ scripted strategy ได้มากแค่ไหน
- การเรียนรู้จากประสบการณ์จะสร้างพฤติกรรมที่ใช้ซ้ำและถ่ายทอดต่อได้หรือไม่
- เมื่อมีความจำ การร่วมมือ และข้อจำกัดด้านพลังงาน เทคโนโลยีอย่างง่ายจะเกิดขึ้นเองหรือไม่
- เทคโนโลยีที่เกิดขึ้นช่วยเพิ่มความอยู่รอด การสืบพันธุ์ หรือความต่อเนื่องของประชากรจริงหรือไม่

### สถานะปัจจุบัน

ระบบที่มีอยู่แล้วในโค้ด:

- โลกแบบกริด `100x100`
- เขตนิเวศ 4 แบบพร้อมความเสี่ยงและความหนาแน่นอาหารต่างกัน
- กลางวัน/กลางคืน และฤดูกาลที่กระทบการมองเห็นและการเกิดอาหาร
- โครงสร้างร่างกายภายใต้งบต้นทุนคงที่ พร้อมทั้ง morphology และ hidden traits
- วงจรชีวิตของเอเจนต์: เด็ก เยาวชน ผู้ใหญ่ และวัยชรา
- ระบบพ่อแม่ ลูก เครือญาติ ความผูกพัน และการเลี้ยงดู
- nest สำหรับความปลอดภัย การเก็บอาหาร และการเก็บวัสดุ
- ความจำเกี่ยวกับอาหาร อันตราย เขตปลอดภัย และตำแหน่ง nest
- การกินพืชและเนื้อแบบดิบ/สุก
- การเก็บวัสดุ เช่น `wood`, `stone`, `fiber`
- การล่าแบบร่วมมือ และเครื่องมือ Tier 1 เช่น `knife`, `spear`, `sickle`
- โหมดการทดลองหลายแบบสำหรับงานสำรวจ งานเก็บข้อมูล และงานทำ publication

ข้อจำกัดสำคัญตอนนี้:

- ยังไม่มี mutation-and-selection loop ที่เกิดขึ้นเองครบวงจรระหว่างการสืบพันธุ์
- ความหลากหลายเชิง morphology ยังแคบกว่าความหลากหลายใน trait space
- ระบบเศรษฐกิจ การแลกเปลี่ยน และ infrastructure ยังอยู่ในช่วงต้น

### การติดตั้ง

โปรเจ็กต์นี้รันได้ด้วย Python และตอนนี้ `requirements.txt` ระบุว่าใช้
standard library เป็นหลัก

```powershell
python --version
```

### วิธีรันแบบเร็ว

รันโหมดต้นแบบพื้นฐาน:

```powershell
python main.py
```

ดูตัวเลือกทั้งหมด:

```powershell
python main.py --help
```

### โหมดที่ใช้บ่อย

แดชบอร์ดแบบ replay:

```powershell
python main.py --mode dashboard --seed 7 --dashboard-ticks 800 --snapshot-interval 10
```

เก็บข้อมูลแบบ research bundle:

```powershell
python main.py --mode paper --seed 7 --paper-body-index 8 --dashboard-ticks 2000 --snapshot-interval 10
```

รันหลายเงื่อนไขหลาย seed เพื่อทำ publication package:

```powershell
python main.py --mode publication-batch --seed 7 --study-seeds 6 --dashboard-ticks 1200 --snapshot-interval 10
```

สำรวจความทนทานของระบบในหลายเงื่อนไข:

```powershell
python main.py --mode robustness-batch --seed 7 --study-seeds 4 --dashboard-ticks 1600 --snapshot-interval 20
```

ศึกษาการค้นพบโลกแบบแบ่งเฟส:

```powershell
python main.py --mode world-discovery --seed 7 --study-seeds 4 --dashboard-ticks 1600 --snapshot-interval 20
```

รันระยะยาวแบบ founder เป็นอมตะเพื่อดู emergence:

```powershell
python main.py --mode immortal-discovery --seed 7 --paper-body-index 8 --dashboard-ticks 8000 --snapshot-interval 25
```

ค้นหา body type ที่อยู่รอดได้:

```powershell
python main.py --mode distinct-search --seed 7 --target-body-types 50
```

### ผลลัพธ์จะถูกเก็บไว้ที่ไหน

- `data/dashboards/` สำหรับ replay dashboard
- `data/research_runs/` สำหรับ research bundles รายรัน
- `data/publication_packages/` สำหรับ aggregate statistics และ figure source data
- `data/experiment_history.json` สำหรับประวัติการทดลอง
- `reports/` สำหรับบันทึกวิเคราะห์ รายงาน และ manuscript

### โครงสร้างโปรเจ็กต์

- `agents/` ตรรกะเอเจนต์ โครงสร้างร่างกาย และพฤติกรรม
- `world/` ฟิสิกส์โลก เขตนิเวศ เมแทบอลิซึม และสิ่งแวดล้อม
- `simulation/` ตัวรันการทดลองและระบบสร้าง artifacts
- `visualization/` ตัวช่วยสำหรับ dashboard และงานแสดงผล
- `scripts/` สคริปต์สำหรับ batch runs, figure rendering, และงานรายงาน
- `docs/` เอกสารสถานะ สถาปัตยกรรม คำถามวิจัย และกติกาของโลก
- `data/` ข้อมูลผลลัพธ์จากการทดลอง
- `reports/` รายงานสรุปและเอกสารประกอบงานวิจัย

### เอกสารที่ควรอ่านต่อ

- `docs/CURRENT_STATE.md` สรุประบบที่ implement แล้ว, บางส่วน, และแผนในอนาคต
- `docs/PROJECT_OVERVIEW.md` ภาพรวมคำถามวิจัยและ roadmap
- `docs/WORLD_RULES.md` กติกาหลักของโลกจำลอง
- `docs/PAPER_DATA_PROTOCOL.md` รูปแบบข้อมูลสำหรับงานวิจัย

## English

### What This Project Does

Artificial Evolution is an artificial life simulation built around one primary
research question: can agents learn the structure of their world without
labels, hand-authored meaning, or pre-scripted strategies, and can that
learning accumulate into technology emergence?

In this repository, "technology" includes practical capabilities such as tool
use, food processing, resource handling, coordinated roles, and other reusable
behavioral structures that extend what agents can do.

### Primary Research Question

- How much can agents learn from experience alone without labeled concepts?
- Can repeated successful behavior become stable, reusable, and transmissible?
- Under memory, cooperation, and energy constraints, do simple technologies emerge?
- Do those technologies measurably improve survival, reproduction, or continuity?

### Current Implementation

Systems already present in the codebase:

- A `100x100` grid world
- Four ecological zones with different food density and danger profiles
- Day/night and seasonal dynamics
- Fixed-budget body construction with morphology plus hidden traits
- Agent life stages: child, juvenile, adult, and old
- Parent-child lineage, bonding, and caretaker behavior
- Nests for safety, food storage, and material storage
- Memory for danger, food, safe zones, and nest locations
- Raw/cooked plant and meat food processing
- Material gathering using `wood`, `stone`, and `fiber`
- Coordinated hunting and Tier 1 tools: `knife`, `spear`, `sickle`
- Multiple experiment modes for search, dashboards, research capture, and publication packaging

Important current limitations:

- There is not yet a fully endogenous mutation-and-selection loop during reproduction.
- Morphological diversity is still narrower than trait-space diversity.
- Economy, exchange, and infrastructure systems are still early-stage.

### Setup

The repository currently uses Python with only standard-library requirements.

```powershell
python --version
```

### Quick Start

Run the default prototype experiment:

```powershell
python main.py
```

Show all CLI options:

```powershell
python main.py --help
```

### Common Modes

Replayable dashboard:

```powershell
python main.py --mode dashboard --seed 7 --dashboard-ticks 800 --snapshot-interval 10
```

Research-grade capture bundle:

```powershell
python main.py --mode paper --seed 7 --paper-body-index 8 --dashboard-ticks 2000 --snapshot-interval 10
```

Multi-condition publication package:

```powershell
python main.py --mode publication-batch --seed 7 --study-seeds 6 --dashboard-ticks 1200 --snapshot-interval 10
```

Robustness sweep:

```powershell
python main.py --mode robustness-batch --seed 7 --study-seeds 4 --dashboard-ticks 1600 --snapshot-interval 20
```

Phase-separated world discovery study:

```powershell
python main.py --mode world-discovery --seed 7 --study-seeds 4 --dashboard-ticks 1600 --snapshot-interval 20
```

Long open-ended immortal founder run:

```powershell
python main.py --mode immortal-discovery --seed 7 --paper-body-index 8 --dashboard-ticks 8000 --snapshot-interval 25
```

Search for viable survivor body types:

```powershell
python main.py --mode distinct-search --seed 7 --target-body-types 50
```

### Output Locations

- `data/dashboards/` for replay dashboards
- `data/research_runs/` for per-run research bundles
- `data/publication_packages/` for aggregate statistics and figure-ready source data
- `data/experiment_history.json` for experiment history
- `reports/` for analyses, summaries, and manuscript artifacts

### Project Layout

- `agents/` agent logic, body construction, and behavioral systems
- `world/` world rules, metabolism, ecology, and environment
- `simulation/` experiment runners and research artifact generation
- `visualization/` dashboard helpers and visualization support
- `scripts/` batch runners, figure rendering, and report utilities
- `docs/` architecture, status notes, research framing, and world rules
- `data/` generated experimental output
- `reports/` research reports and publication-oriented documents

### Recommended Docs

- `docs/CURRENT_STATE.md` for the most accurate implementation snapshot
- `docs/PROJECT_OVERVIEW.md` for research framing and roadmap
- `docs/WORLD_RULES.md` for simulation rules
- `docs/PAPER_DATA_PROTOCOL.md` for research artifact structure

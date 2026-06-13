# Phase 5 Protocol: Site Selection / Seed Placement Quality

วันที่จัดทำ: 2026-06-13
พื้นที่ทดลอง: `C:\artificial-evolution`

## Abstract

Phase 5 ทดสอบว่า agent วางเมล็ดในพื้นที่ที่เหมาะต่อการงอก โต ออกผล และถูกกิน มากกว่า control หรือไม่ โดยใช้ `current_position_control` เป็น control หลัก

Phase 5 ไม่ใช้ `return_agents` เป็นหลักฐานหลัก เพราะ Phase 4.1 พบว่า return signal ปน food hotspot, shared traffic corridor และ world-size effect สูง

## Research Question

> ตอน agent ถือ seed อยู่ มัน drop seed ในจุดที่มีคุณภาพทางฟิสิกส์/ชีววิทยาดีกว่าจุดก่อนหน้าและจุดใกล้เคียงหรือไม่

## Primary Control

`current_position_control` สำคัญที่สุด:

```text
agent carries seed at tick t
-> record current position quality before action
-> if agent drops seed during that tick
-> compare drop-site quality against carried-position quality
```

control นี้ตอบว่า agent ไม่ได้แค่บังเอิญเดินผ่านที่ดี แต่จังหวะ drop ดีกว่าจุดที่มันถือ seed อยู่ก่อนหน้าไหม

## Quality Components

ทุก drop site และ control site ต้องเก็บ:

- `quality_score_total`
- `moisture_fit`
- `light_fit`
- `nutrient_score`
- `danger_penalty`
- `temperature_penalty`

ห้ามตีความจาก total เพียงค่าเดียวโดยไม่ดู components

## Quality Score

ใช้ observer score เท่านั้น ไม่ให้ agent เห็น score นี้:

```text
quality =
  moisture_fit * 0.30
+ light_fit * 0.24
+ nutrient_score * 0.24
+ temperature_fit * 0.14
- danger_penalty * 0.18
```

โดย:

```text
temperature_penalty = 1 - temperature_fit
```

## Early / Late Normalization

ไม่แบ่งครึ่ง run ตามเวลาโลก เพราะ ecology เปลี่ยนเองได้

ใช้ลำดับ agent-moved drops:

- early = first 30% of agent-moved drops
- middle = ignored
- late = last 30% of agent-moved drops

## Conditions

Phase 5 แยก stress test `200x200` เป็น diagnostics ไม่ใช่ hard gate ทันที:

1. `baseline_100x100`
2. `low_food_signal_100x100`
3. `large_world_200x200_same_density_long_budget`
4. `large_world_200x200_same_population_long_budget`

เหตุผล:

- same density แยกว่าโลกใหญ่ขึ้นแต่ resource density เท่าเดิมยังผ่านไหม
- same population แยกว่า fail เพราะ agent น้อยเกินเมื่อเทียบพื้นที่หรือไม่
- 200x200 เป็น blocker diagnosis ไม่ใช่ pass/fail หลักของ Phase 5 รอบแรก

## Success Criteria

ต่อ seed ต้องผ่านทุกข้อหลัก:

1. `drop_quality_vs_current_position > 1.10`
2. `drop_quality_vs_nearby_control > 1.05`
3. `high_quality_chain_rate > low_quality_chain_rate`
4. `late_drop_quality > early_drop_quality` by at least `5%`

Phase 5 core pass:

- อย่างน้อย `3/5` seeds ใน core 100x100 condition ผ่านทุกข้อหลัก
- directional consistency ต้องมีอย่างน้อย `4/5` seeds ที่:
  - `drop_quality_vs_current_position > 1.0`
  - `drop_quality_vs_nearby_control > 1.0`
  - `late_drop_quality > early_drop_quality`

## Failure Criteria

Phase 5 ยังไม่ผ่านถ้า:

- drop site ไม่ดีกว่า current position
- total score ดีขึ้นแต่เกิดจาก component เดียวโดยไม่มี downstream chain support
- high-quality site ไม่ให้ completed chain rate สูงกว่า low-quality site
- late quality ไม่ดีขึ้นเมื่อ normalize ตามลำดับ drops
- effect เกิดจาก seed เดียวแรงมาก แต่ directional consistency ไม่ถึง `4/5`

## Interpretation

ถ้าผ่าน:

> agent seed-drop behavior shows site-selection signal: drop sites are better than current carried positions and nearby controls, and better sites produce better downstream chains.

ถ้าไม่ผ่าน:

> Phase 4 patch productivity remains, but there is no strong evidence that agents select better seed-placement sites.

## Planned Output

- runner: `scripts/run_phase5_site_selection_probe.py`
- data: `data/phase5_site_selection_*`
- report: `reports/phase5_site_selection_*_2026-06-13.th.md`

# รายงานสรุป Phase 4.1: Return-Signal Falsification

วันที่สรุป: 2026-06-13
พื้นที่ทดลอง: `C:\artificial-evolution`

ไฟล์อ้างอิง:

- suite report: `reports/phase4_1_falsification_confirm01_2026-06-13.th.md`
- summary data: `data/phase4_1_falsification_confirm01_20260613/summary.json`
- per-run CSV: `data/phase4_1_falsification_confirm01_20260613/runs.csv`

## Abstract

Phase 4.1 ถูกออกแบบมาเพื่อทดสอบข้อสงสัยว่า metric `return_agents = 50` ใน Phase 4 อาจไม่ได้แปลว่า agent เจาะจงกลับ patch ของตัวเอง แต่อาจเกิดจาก food attraction, shared foraging corridor, หรือโลก `100x100` เล็ก/หนาแน่นเกินไป

ผลสรุป:

- `100x100` baseline ยังผ่าน `3/3`
- `100x100` แบบลด food signal ยังผ่าน `3/3`
- `200x200` แบบ scale food/seed density ตามพื้นที่ fail `0/3`
- non-dropper return lift ยังสูงมากในทุก condition ที่มี patch

ข้อสรุปสำคัญ:

> Phase 4 ยังยืนได้ในฐานะ patch-productivity evidence สำหรับโลก `100x100` tuned ecology แต่ claim เรื่อง agent-specific patch ownership / intentional managed patch ยังไม่ผ่านเกณฑ์เข้ม

## What Changed

เพิ่ม telemetry ใหม่โดยไม่เพิ่ม instruction ให้ agent:

- dropper return หลังออกจาก patch
- non-dropper return แยกจาก dropper
- pre-drop visit count
- visit delta หลัง first drop
- pre-fruit vs post-fruit return agents
- food-signal ablation:
  - `food_signal_radius_cap`
  - `plant_lifecycle_food_signal_weight`

เพิ่ม runner:

- `scripts/run_phase4_1_falsification_suite.py`

## Conditions

| condition | world | food signal | seeds | time/seed |
| --- | --- | --- | ---: | ---: |
| baseline_100x100 | 100x100 | radius default, plant weight 1.35 | 3 | 60s |
| low_food_signal_100x100 | 100x100 | radius cap 2, plant weight 1.0 | 3 | 60s |
| large_world_200x200 | 200x200 | radius default, plant weight 1.35 | 3 | 60s |

## Aggregate Results

| condition | pass | patches | patch food | return agents | dropper return rate | dropper lift | non-dropper lift |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 3/3 | 9.0 | 27.3333 | 50.0 | 0.8510 | 89.8897 | 31.7920 |
| low_food_signal_100x100 | 3/3 | 12.6667 | 27.6667 | 50.0 | 0.8601 | 129.5740 | 22.7460 |
| large_world_200x200 | 0/3 | 2.3333 | 1.3333 | 20.0 | 0.3519 | 52.4885 | 13.0900 |

## Interpretation

### 1. Patch productivity ใน 100x100 ยังแข็ง

ทั้ง baseline และ low-food-signal ผ่าน `3/3`:

- patch food ใกล้เคียงกัน: `27.3333` vs `27.6667`
- repeated patches ยังเกิด: `9.0` vs `12.6667`
- contamination events = `0`

นี่แปลว่า Phase 4 ไม่ได้พังเพราะลด food signal แค่ระดับ radius 2 และ plant weight 1.0

### 2. Return signal ยังปน food hotspot/social corridor สูง

แม้ลด food signal:

- `return_agents` ยังเป็น `50.0`
- `non-dropper lift` ยังสูง: `22.746`
- best patch non-dropper agents อยู่ระดับ `44-49` ใน 100x100

แปลว่า patch ที่ผ่านไม่ได้ดึงเฉพาะ dropper แต่ดึง agent อื่นจำนวนมากด้วย

### 3. Dropper return มีจริง แต่ยังไม่แยกจาก shared attraction

dropper return rate หลังออกจาก patch:

- baseline: `0.8510`
- low food signal: `0.8601`

นี่เป็น evidence สนับสนุนว่า dropper จำนวนมากกลับมา แต่เพราะ non-dropper ก็กลับมาสูงมากเหมือนกัน จึงยังไม่พอจะอ้าง agent-specific ownership

### 4. โลก 200x200 ทำให้ Phase 4 gate ล้ม

large world `200x200` fail `0/3`:

- patch food ลดเหลือ `1.3333`
- repeated patches ลดเหลือ `2.3333`
- return agents ลดเหลือ `20.0`
- plant food consumed ต่อ run อยู่แค่ `16-18`

นี่ชี้ว่า Phase 4 ในรูปปัจจุบัน sensitive ต่อ world size/run budget มาก และผล `100x100` ยังควรถูกตีความเป็น tuned testbed result

## Evidence Supporting

- มี patch productivity สูงใน `100x100` แม้ลด food signal
- dropper return หลังออกจาก patchเกิดจริงในหลาย watcher
- matched micro-site control ยังถูกใช้ใน runs ที่มี patch
- ไม่มี scaffold contamination

## Evidence Against

- non-dropper return สูงมาก แปลว่า signal ไม่เฉพาะตัว
- pre-drop visits บาง patch สูง เช่น `262` ใน low-signal seed `20260612`
- visit delta สูงมากใน 100x100 สะท้อนว่า patch อยู่ในพื้นที่ traffic สูง
- `200x200` fail ทั้งชุดใน 60s ทำให้ robustness ต่ำ
- ยังไม่ได้ปิด memory, social grouping, หรือ shuffled reward labels

## Verdict

Phase 4.1 ทำให้ต้องปรับคำกล่าวอ้าง:

เดิม:

> agent เริ่มจัดการ patch และกลับมาใช้ patch

ควรแก้เป็น:

> ในโลก `100x100` tuned ecology มี repeated productive seed-drop patches ที่ถูก agent จำนวนมากกลับมาใช้ซ้ำ แต่ยังแยกไม่ได้ว่าเป็น agent-specific managed patch หรือ shared food hotspot

## Confidence After Phase 4.1

| Claim | Confidence |
| --- | --- |
| repeated productive patches ใน 100x100 | สูง |
| patch productivity สูงกว่า control ใน 100x100 | สูงปานกลาง |
| dropper กลับ patch หลังออก | ปานกลาง |
| agent-specific patch ownership | ต่ำ |
| robust managed patch across world sizes | ต่ำ |
| intentional farming | ต่ำมาก |

## Next Required Gate

Phase 4.2 ควรบังคับ gate ใหม่:

- `dropper_return_rate_after_left > non_dropper_return_rate`
- `same_agent_patch_food_chains >= 2`
- `post_fruit return > pre_fruit return`
- `pre_drop_visit_count` ต้องต่ำ หรืออย่างน้อย post/pre lift ต้องสูง
- run ที่ `200x200` ต้องผ่านหลังปรับ time budget หรือ ecology density
- เพิ่ม ablation:
  - memory-disabled
  - shuffled reward labels
  - no plant-food signal bonus
  - no social group pull

## Conclusion

Phase 4.1 ไม่ได้ล้ม Phase 4 ทั้งหมด แต่ทำให้ claim แคบลงอย่างสำคัญ

ผลที่ควรถือไว้ตอนนี้:

```text
Phase 4 = patch productivity evidence ใน tuned 100x100 world
Phase 4.1 = return_agents metric เดิม inflated จาก shared attraction / world-size effect
```

ก้าวถัดไปควรเป็น Phase 4.2 ที่วัด ownership และ counterfactual controls ให้เข้มขึ้น ก่อนจะขยับไป Phase 5 เรื่อง site selection

# รายงาน Phase 4: Managed Patch / Proto-Farm Probe

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase4_managed_patch_confirm01_20260613`

## คำตัดสิน

Phase 4: ผ่าน

- รันทั้งหมด: 5 seeds
- ผ่าน: 5/5
- เกณฑ์ชุด: อย่างน้อย 3 runs ต้องผ่าน

## เกณฑ์ต่อ Run

- repeated-drop patches >= 1
- completed seed chains ใน patch >= 3
- consumed food จาก patch >= 3
- return agents หลัง drop >= 2
- productivity lift vs control >= 1.25
- return lift vs random >= 2.0
- contamination events ต้องเป็น 0: True

## Aggregate Metrics

- mean repeated-drop patch count: 25.4
- mean patch completed chains: 29.0
- mean patch food consumed: 75.4
- mean patch return agents: 50.0
- mean max patch moved-seed drops: 20.8
- mean max patch completed chains: 4.6
- mean productivity lift: 5.8216
- mean return lift: 25.7792
- total contamination events: 0

## Runs

| seed | pass | moved seeds | moved chains | patches | patch chains | patch food | return agents | max drops | prod lift | return lift | control | contam |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 20260610 | True | 111 | 13 | 20 | 18 | 49 | 50 | 22 | 6.052 | 35.245 | matched_micro_site | 0 |
| 20260611 | True | 116 | 15 | 20 | 28 | 67 | 50 | 21 | 5.363 | 29.313 | matched_micro_site | 0 |
| 20260612 | True | 141 | 14 | 23 | 21 | 55 | 50 | 22 | 6.315 | 15.39 | matched_micro_site | 0 |
| 20260613 | True | 234 | 30 | 39 | 46 | 123 | 50 | 24 | 6.445 | 26.091 | matched_micro_site | 0 |
| 20260614 | True | 142 | 16 | 25 | 32 | 83 | 50 | 15 | 4.933 | 22.857 | matched_micro_site | 0 |

## Interpretation

Phase 4 วัดว่า agent-moved seeds รวมตัวเป็น repeated-drop patch ที่มีผลผลิตและมีการกลับมาใช้พื้นที่ซ้ำหรือไม่ โดยไม่ใช้ `tend_food_patch` หรือ `managed_food_map` เป็นหลักฐานผ่าน

ถ้าผ่าน จึงควรเรียกอย่างระมัดระวังว่า managed patch / proto-farm evidence ไม่ใช่หลักฐานว่า agent เข้าใจการทำฟาร์มเชิงสัญลักษณ์

## Limitations

- control แบบ matched micro-site ใช้ข้อมูลคุณภาพ cell ณ เวลา summary จึงยังไม่เทียบเท่า causal counterfactual เต็มรูปแบบ
- agent ยัง immortal เพื่อคงเงื่อนไขทดลองเดิมของ Phase 1-4
- sample size ในรอบนี้ยังเป็น gate-level ไม่ใช่ paper-quality replication
- return lift อาจรวม food attraction และ social clustering จึงยังต้องมี ablation ในเฟสถัดไป

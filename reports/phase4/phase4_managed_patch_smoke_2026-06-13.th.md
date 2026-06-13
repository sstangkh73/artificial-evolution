# รายงาน Phase 4: Managed Patch / Proto-Farm Probe

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase4_managed_patch_smoke_20260613`

## คำตัดสิน

Phase 4: ยังไม่ผ่าน

- รันทั้งหมด: 1 seeds
- ผ่าน: 0/1
- เกณฑ์ชุด: อย่างน้อย 1 runs ต้องผ่าน

## เกณฑ์ต่อ Run

- repeated-drop patches >= 1
- completed seed chains ใน patch >= 3
- consumed food จาก patch >= 3
- return agents หลัง drop >= 2
- productivity lift vs control >= 1.25
- return lift vs random >= 2.0
- contamination events ต้องเป็น 0: True

## Aggregate Metrics

- mean repeated-drop patch count: 1.0
- mean patch completed chains: 2.0
- mean patch food consumed: 3.0
- mean patch return agents: 28.0
- mean max patch moved-seed drops: 5.0
- mean max patch completed chains: 2.0
- mean productivity lift: 7.12
- mean return lift: 16.454
- total contamination events: 0

## Runs

| seed | pass | moved seeds | moved chains | patches | patch chains | patch food | return agents | max drops | prod lift | return lift | control | contam |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 20260610 | False | 25 | 5 | 1 | 2 | 3 | 28 | 5 | 7.12 | 16.454 | matched_micro_site | 0 |

## Interpretation

Phase 4 วัดว่า agent-moved seeds รวมตัวเป็น repeated-drop patch ที่มีผลผลิตและมีการกลับมาใช้พื้นที่ซ้ำหรือไม่ โดยไม่ใช้ `tend_food_patch` หรือ `managed_food_map` เป็นหลักฐานผ่าน

ถ้าผ่าน จึงควรเรียกอย่างระมัดระวังว่า managed patch / proto-farm evidence ไม่ใช่หลักฐานว่า agent เข้าใจการทำฟาร์มเชิงสัญลักษณ์

## Limitations

- control แบบ matched micro-site ใช้ข้อมูลคุณภาพ cell ณ เวลา summary จึงยังไม่เทียบเท่า causal counterfactual เต็มรูปแบบ
- agent ยัง immortal เพื่อคงเงื่อนไขทดลองเดิมของ Phase 1-4
- sample size ในรอบนี้ยังเป็น gate-level ไม่ใช่ paper-quality replication
- return lift อาจรวม food attraction และ social clustering จึงยังต้องมี ablation ในเฟสถัดไป

# รายงาน Phase 4: Managed Patch / Proto-Farm Probe

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase4_1_falsification_confirm01_20260613\low_food_signal_100x100`

## คำตัดสิน

Phase 4: ผ่าน

- รันทั้งหมด: 3 seeds
- ผ่าน: 3/3
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

- mean repeated-drop patch count: 12.6667
- mean patch completed chains: 9.6667
- mean patch food consumed: 27.6667
- mean patch return agents: 50.0
- mean max patch moved-seed drops: 12.6667
- mean max patch completed chains: 2.3333
- mean productivity lift: 10.8067
- mean return lift: 25.0107
- mean dropper return rate after leaving: 0.8601
- mean best dropper return lift: 129.574
- mean best non-dropper return lift: 22.746
- total contamination events: 0

## Runs

| seed | pass | moved seeds | patches | patch chains | patch food | return agents | dropper return rate | dropper lift | non-dropper lift | prod lift | return lift | contam |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20260610 | True | 51 | 9 | 11 | 31 | 50 | 0.86207 | 121.951 | 21.901 | 22.727 | 25.149 | 0 |
| 20260611 | True | 82 | 17 | 13 | 35 | 50 | 0.86813 | 164.44 | 22.661 | 6.247 | 24.186 | 0 |
| 20260612 | True | 87 | 12 | 5 | 17 | 50 | 0.85 | 102.331 | 23.676 | 3.446 | 25.697 | 0 |

## Interpretation

Phase 4 วัดว่า agent-moved seeds รวมตัวเป็น repeated-drop patch ที่มีผลผลิตและมีการกลับมาใช้พื้นที่ซ้ำหรือไม่ โดยไม่ใช้ `tend_food_patch` หรือ `managed_food_map` เป็นหลักฐานผ่าน

ถ้าผ่าน จึงควรเรียกอย่างระมัดระวังว่า managed patch / proto-farm evidence ไม่ใช่หลักฐานว่า agent เข้าใจการทำฟาร์มเชิงสัญลักษณ์

## Limitations

- control แบบ matched micro-site ใช้ข้อมูลคุณภาพ cell ณ เวลา summary จึงยังไม่เทียบเท่า causal counterfactual เต็มรูปแบบ
- agent ยัง immortal เพื่อคงเงื่อนไขทดลองเดิมของ Phase 1-4
- sample size ในรอบนี้ยังเป็น gate-level ไม่ใช่ paper-quality replication
- return lift อาจรวม food attraction และ social clustering จึงยังต้องมี ablation ในเฟสถัดไป

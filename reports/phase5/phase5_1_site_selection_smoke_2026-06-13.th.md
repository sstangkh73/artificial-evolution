# รายงาน Phase 5: Site Selection / Seed Placement Quality

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase5_1_site_selection_smoke_20260613`

## Verdict

Phase 5 core pass: `False`

## Condition Summary

| condition | core | runs | pass | direction | current | nearby | visible | future | high chain | low chain | late/early |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | True | 1 | 0 | 0 | 0.9922 | 1.0012 | 0.9982 | 1.092 | 0.14286 | 0.14286 | 0.9792 |

## Runs

| condition | seed | pass | dir | moved drops | current | nearby | visible | future | high chain | low chain | late/early | moisture | light | nutrient | danger | temp penalty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 20260610 | False | False | 25 | 0.9922 | 1.0012 | 0.9982 | 1.092 | 0.14286 | 0.14286 | 0.9792 | 0.13003 | 0.45979 | 0.99375 | 0.08 | 0.38612 |

## Interpretation

- `current_position_control` เป็น control หลักของ Phase 5
- `visible_control` จำกัด control ให้อยู่ในระยะเห็นของ agent ตอน drop
- `future_path_control` ถามว่าจุด drop ดีกว่าจุดที่ agent เดินต่อไปหลังจากนั้นหรือไม่
- 200x200 conditions เป็น stress/blocker diagnosis ไม่ใช่ hard gate ในรอบนี้
- ถ้า total quality ผ่านแต่ component เดียว dominate ต้องตีความอย่างระวัง

## Limits

- ยังไม่ได้ทำ memory-disabled หรือ reward-shuffled ablation
- quality score ยังเป็น observer score แต่ control ถูกจำกัดตามระยะเห็นของ agent
- large-world failure ต้องแยกต่อว่าเป็น time budget, density, หรือ exploration limitation

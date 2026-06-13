# รายงาน Phase 5: Site Selection / Seed Placement Quality

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase5_site_selection_smoke_20260613`

## Verdict

Phase 5 core pass: `False`

## Condition Summary

| condition | core | runs | pass | direction | current lift | nearby lift | high chain | low chain | late/early |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | True | 1 | 0 | 0 | 0.9922 | 1.0012 | 0.14286 | 0.14286 | 0.9792 |

## Runs

| condition | seed | pass | dir | moved drops | current lift | nearby lift | high chain | low chain | late/early | moisture | light | nutrient | danger | temp penalty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 20260610 | False | False | 25 | 0.9922 | 1.0012 | 0.14286 | 0.14286 | 0.9792 | 0.13003 | 0.45979 | 0.99375 | 0.08 | 0.38612 |

## Interpretation

- `current_position_control` เป็น control หลักของ Phase 5
- 200x200 conditions เป็น stress/blocker diagnosis ไม่ใช่ hard gate ในรอบนี้
- ถ้า total quality ผ่านแต่ component เดียว dominate ต้องตีความอย่างระวัง

## Limits

- ยังไม่ได้ทำ memory-disabled หรือ reward-shuffled ablation
- quality score เป็น observer score ไม่ใช่ perception ของ agent
- large-world failure ต้องแยกต่อว่าเป็น time budget, density, หรือ exploration limitation

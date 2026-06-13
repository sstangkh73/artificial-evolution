# รายงาน Phase 5: Site Selection / Seed Placement Quality

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase5_4_hunger_decoupled_smoke_20260613`

## Verdict

Phase 5 core pass: `False`
Phase 5.4 hunger-decoupled pass: `False`

## Condition Summary

| condition | core | hunger bonus | runs | pass | direction | moved drops | hunger frac | food-contact frac | current | nearby | visible | future | high chain | low chain | late/early |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | True | 0.06 | 1 | 0 | 0 | 25.0 | 1.0 | 0.0 | 0.9922 | 1.0012 | 0.9982 | 1.0919 | 0.14286 | 0.14286 | 0.9792 |
| hunger_neutral_seed_drop_100x100 | False | 0.0 | 1 | 0 | 0 | 19.0 | 1.0 | 0.0 | 0.9843 | 1.0015 | 1.0007 | 1.0852 | 0.0 | 0.2 | 1.0625 |

## Context-Matched Summary

| condition | hunger count | hunger current | hunger visible | hunger future | hunger chain | food-contact count | food-contact current | food-contact visible | food-contact chain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 25.0 | 0.9922 | 0.9982 | 1.0919 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| hunger_neutral_seed_drop_100x100 | 19.0 | 0.9843 | 1.0007 | 1.0852 | 0.05263 | 0.0 | 0.0 | 0.0 | 0.0 |

## Runs

| condition | seed | pass | dir | moved drops | hunger frac | food-contact frac | current | nearby | visible | future | high chain | low chain | late/early | moisture | light | nutrient | danger | temp penalty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 20260610 | False | False | 25 | 1.0 | 0.0 | 0.9922 | 1.0012 | 0.9982 | 1.0919 | 0.14286 | 0.14286 | 0.9792 | 0.13003 | 0.45979 | 0.99375 | 0.08 | 0.38612 |
| hunger_neutral_seed_drop_100x100 | 20260610 | False | False | 19 | 1.0 | 0.0 | 0.9843 | 1.0015 | 1.0007 | 1.0852 | 0.0 | 0.2 | 1.0625 | 0.11101 | 0.50029 | 0.98355 | 0.08105 | 0.30352 |

## Interpretation

- `current_position_control` เป็น control หลักของ Phase 5
- `visible_control` จำกัด control ให้อยู่ในระยะเห็นของ agent ตอน drop
- `future_path_control` ถามว่าจุด drop ดีกว่าจุดที่ agent เดินต่อไปหลังจากนั้นหรือไม่
- `Context-Matched Summary` แยกถามว่า lift เกิดใน hunger/food-contact context หรือถูก context หนึ่งลากค่าเฉลี่ย
- 200x200 conditions เป็น stress/blocker diagnosis ไม่ใช่ hard gate ในรอบนี้
- ถ้า total quality ผ่านแต่ component เดียว dominate ต้องตีความอย่างระวัง

## Limits

- ยังไม่ได้ทำ memory-disabled หรือ reward-shuffled ablation
- quality score ยังเป็น observer score แต่ control ถูกจำกัดตามระยะเห็นของ agent
- large-world failure ต้องแยกต่อว่าเป็น time budget, density, หรือ exploration limitation

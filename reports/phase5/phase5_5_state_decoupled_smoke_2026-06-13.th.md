# รายงาน Phase 5: Site Selection / Seed Placement Quality

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase5_5_state_decoupled_smoke_20260613`

## Verdict

Phase 5 core pass: `False`
Phase 5.4 hunger-decoupled pass: `False`
Phase 5.5 state-decoupled pass: `False`

## Condition Summary

| condition | core | hunger bonus | block critical | safe only | runs | p5.5 pass | p5.5 dir | moved drops | hunger frac | safe/balanced frac | critical frac | current | recovery | safe-window | visible | future | high chain | low chain | late/early |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | True | 0.06 | False | False | 1 | 0 | 0 | 28.0 | 1.0 | 0.0 | 1.0 | 0.9931 | 0.9507 | 0.0 | 0.9968 | 1.1064 | 0.125 | 0.125 | 0.9425 |
| safe_window_seed_drop_only_100x100 | False | 0.06 | False | True | 1 | 0 | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Context-Matched Summary

| condition | hunger count | hunger current | hunger visible | hunger future | hunger chain | food-contact count | food-contact current | food-contact visible | food-contact chain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 28.0 | 0.9931 | 0.9968 | 1.1064 | 0.17857 | 0.0 | 0.0 | 0.0 | 0.0 |
| safe_window_seed_drop_only_100x100 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Runs

| condition | seed | p5.5 pass | p5.5 dir | moved drops | hunger frac | safe/balanced frac | critical frac | current | recovery | safe-window | visible | future | high chain | low chain | late/early | moisture | light | nutrient | danger | temp penalty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 20260610 | False | False | 28 | 1.0 | 0.0 | 1.0 | 0.9931 | 0.9507 | None | 0.9968 | 1.1064 | 0.125 | 0.125 | 0.9425 | 0.14058 | 0.44624 | 0.99442 | 0.08 | 0.36483 |
| safe_window_seed_drop_only_100x100 | 20260610 | False | False | 0 | 0.0 | 0.0 | 0.0 | None | None | None | None | None | 0.0 | 0.0 | None | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Interpretation

- `current_position_control` เป็น control หลักของ Phase 5
- `visible_control` จำกัด control ให้อยู่ในระยะเห็นของ agent ตอน drop
- `recovery` คือ control ที่ตำแหน่งแรกหลังถือ seed แล้วพ้นจาก hunger state
- `safe-window` คือ control ที่ตำแหน่งแรกขณะถือ seed และอยู่ใน balanced/safe state
- `future_path_control` ถามว่าจุด drop ดีกว่าจุดที่ agent เดินต่อไปหลังจากนั้นหรือไม่
- `Context-Matched Summary` แยกถามว่า lift เกิดใน hunger/food-contact context หรือถูก context หนึ่งลากค่าเฉลี่ย
- 200x200 conditions เป็น stress/blocker diagnosis ไม่ใช่ hard gate ในรอบนี้
- ถ้า total quality ผ่านแต่ component เดียว dominate ต้องตีความอย่างระวัง

## Limits

- reward-memory ablations เป็น diagnostic ไม่ใช่ hard gate ถ้า state-decoupled conditions ยังไม่ผ่าน
- quality score ยังเป็น observer score แต่ control ถูกจำกัดตามระยะเห็นของ agent
- large-world failure ต้องแยกต่อว่าเป็น time budget, density, หรือ exploration limitation

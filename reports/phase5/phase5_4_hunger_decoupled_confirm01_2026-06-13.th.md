# รายงาน Phase 5: Site Selection / Seed Placement Quality

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase5_4_hunger_decoupled_confirm01_20260613`

## Verdict

Phase 5 core pass: `False`
Phase 5.4 hunger-decoupled pass: `False`

## Condition Summary

| condition | core | hunger bonus | runs | pass | direction | moved drops | hunger frac | food-contact frac | current | nearby | visible | future | high chain | low chain | late/early |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | True | 0.06 | 5 | 0 | 0 | 79.8 | 0.97644 | 0.01715 | 1.00822 | 0.98952 | 0.98706 | 1.16066 | 0.15776 | 0.2137 | 1.18256 |
| hunger_neutral_seed_drop_100x100 | False | 0.0 | 5 | 0 | 0 | 101.8 | 0.98168 | 0.01515 | 0.9885 | 0.97432 | 0.97186 | 1.1217 | 0.11901 | 0.15564 | 1.09108 |
| low_food_signal_100x100 | False | 0.06 | 5 | 0 | 0 | 74.0 | 0.98244 | 0.00935 | 0.99574 | 0.99492 | 0.99348 | 1.09692 | 0.0475 | 0.22141 | 1.16102 |

## Context-Matched Summary

| condition | hunger count | hunger current | hunger visible | hunger future | hunger chain | food-contact count | food-contact current | food-contact visible | food-contact chain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 77.8 | 1.00918 | 0.9877 | 1.15986 | 0.1559 | 1.4 | 0.76832 | 0.75846 | 0.0 |
| hunger_neutral_seed_drop_100x100 | 99.6 | 0.98972 | 0.97298 | 1.12026 | 0.12884 | 1.8 | 0.54506 | 0.54816 | 0.0 |
| low_food_signal_100x100 | 72.4 | 0.99652 | 0.99464 | 1.0965 | 0.1276 | 1.0 | 0.34874 | 0.33206 | 0.0 |

## Runs

| condition | seed | pass | dir | moved drops | hunger frac | food-contact frac | current | nearby | visible | future | high chain | low chain | late/early | moisture | light | nutrient | danger | temp penalty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 20260610 | False | False | 65 | 0.98462 | 0.01538 | 0.9984 | 0.9872 | 0.9851 | 1.1471 | 0.15789 | 0.26316 | 1.2412 | 0.19663 | 0.53894 | 0.9976 | 0.08 | 0.31803 |
| baseline_100x100 | 20260611 | False | False | 64 | 0.95312 | 0.03125 | 1.0255 | 0.9774 | 0.9724 | 1.1807 | 0.10526 | 0.15789 | 1.2115 | 0.23006 | 0.5957 | 0.99756 | 0.08 | 0.28812 |
| baseline_100x100 | 20260612 | False | False | 88 | 0.97727 | 0.02273 | 0.9913 | 0.9885 | 0.9855 | 1.1691 | 0.19231 | 0.23077 | 1.0972 | 0.22327 | 0.59906 | 0.99822 | 0.08023 | 0.29482 |
| baseline_100x100 | 20260613 | False | False | 122 | 0.96721 | 0.01639 | 1.0087 | 0.9968 | 0.9948 | 1.1587 | 0.16667 | 0.25 | 1.2611 | 0.28421 | 0.54658 | 0.99027 | 0.08426 | 0.29178 |
| baseline_100x100 | 20260614 | False | False | 60 | 1.0 | 0.0 | 1.0172 | 0.9977 | 0.9975 | 1.1477 | 0.16667 | 0.16667 | 1.1018 | 0.21108 | 0.66044 | 1.0 | 0.08 | 0.32009 |
| hunger_neutral_seed_drop_100x100 | 20260610 | False | False | 112 | 0.97321 | 0.02679 | 0.9434 | 0.9434 | 0.9416 | 1.057 | 0.06061 | 0.12121 | 1.0597 | 0.33058 | 0.38598 | 0.93664 | 0.08946 | 0.26591 |
| hunger_neutral_seed_drop_100x100 | 20260611 | False | False | 126 | 0.94444 | 0.03968 | 0.9942 | 0.9696 | 0.9678 | 1.1066 | 0.18919 | 0.16216 | 1.0595 | 0.20304 | 0.44376 | 0.99256 | 0.08 | 0.31328 |
| hunger_neutral_seed_drop_100x100 | 20260612 | False | False | 99 | 1.0 | 0.0 | 1.004 | 0.9844 | 0.983 | 1.1165 | 0.10345 | 0.13793 | 1.1387 | 0.19293 | 0.4581 | 0.99684 | 0.08 | 0.32681 |
| hunger_neutral_seed_drop_100x100 | 20260613 | False | False | 108 | 0.99074 | 0.00926 | 1.0076 | 0.9823 | 0.9784 | 1.1036 | 0.03125 | 0.09375 | 1.2051 | 0.20437 | 0.46339 | 0.99566 | 0.08 | 0.34576 |
| hunger_neutral_seed_drop_100x100 | 20260614 | False | False | 64 | 1.0 | 0.0 | 0.9933 | 0.9919 | 0.9885 | 1.2248 | 0.21053 | 0.26316 | 0.9924 | 0.25423 | 0.61479 | 0.97503 | 0.0825 | 0.26944 |
| low_food_signal_100x100 | 20260610 | False | False | 25 | 1.0 | 0.0 | 0.991 | 1.0218 | 1.0195 | 1.0549 | 0.0 | 0.42857 | 1.0017 | 0.14971 | 0.52542 | 1.0 | 0.08 | 0.35381 |
| low_food_signal_100x100 | 20260611 | False | False | 63 | 0.96825 | 0.0 | 0.9941 | 0.9896 | 0.9872 | 1.0512 | 0.0 | 0.22222 | 1.075 | 0.16281 | 0.52402 | 0.99504 | 0.08063 | 0.41572 |
| low_food_signal_100x100 | 20260612 | False | False | 68 | 1.0 | 0.0 | 1.0262 | 1.0011 | 0.9992 | 1.1354 | 0.05 | 0.05 | 1.3618 | 0.24273 | 0.53262 | 0.98759 | 0.08235 | 0.34463 |
| low_food_signal_100x100 | 20260613 | False | False | 107 | 0.98131 | 0.01869 | 0.9716 | 0.9717 | 0.9719 | 1.0957 | 0.09375 | 0.1875 | 1.1954 | 0.27506 | 0.41561 | 0.98088 | 0.08449 | 0.30171 |
| low_food_signal_100x100 | 20260614 | False | False | 107 | 0.96262 | 0.02804 | 0.9958 | 0.9904 | 0.9896 | 1.1474 | 0.09375 | 0.21875 | 1.1712 | 0.20469 | 0.57668 | 1.0 | 0.08 | 0.27681 |

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

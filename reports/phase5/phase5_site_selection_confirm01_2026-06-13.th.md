# รายงาน Phase 5: Site Selection / Seed Placement Quality

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase5_site_selection_confirm01_20260613`

## Verdict

Phase 5 core pass: `False`

## Condition Summary

| condition | core | runs | pass | direction | current lift | nearby lift | high chain | low chain | late/early |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | True | 5 | 0 | 0 | 0.99484 | 0.97946 | 0.20878 | 0.12582 | 1.04074 |
| low_food_signal_100x100 | False | 5 | 0 | 0 | 0.98802 | 0.9807 | 0.11711 | 0.17036 | 1.09518 |
| large_world_200x200_same_density_long_budget | False | 3 | 0 | 1 | 1.003 | 0.9969 | 0.10268 | 0.11579 | 1.03783 |
| large_world_200x200_same_population_long_budget | False | 3 | 0 | 0 | 0.9888 | 1.0001 | 0.16667 | 0.03704 | 0.8963 |

## Runs

| condition | seed | pass | dir | moved drops | current lift | nearby lift | high chain | low chain | late/early | moisture | light | nutrient | danger | temp penalty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 20260610 | False | False | 111 | 0.9818 | 0.9752 | 0.21212 | 0.15152 | 1.1044 | 0.22212 | 0.52639 | 0.99859 | 0.08 | 0.31156 |
| baseline_100x100 | 20260611 | False | False | 111 | 1.004 | 0.9698 | 0.27273 | 0.12121 | 1.0676 | 0.23795 | 0.5559 | 0.9955 | 0.08018 | 0.28534 |
| baseline_100x100 | 20260612 | False | False | 139 | 0.9974 | 0.9863 | 0.12195 | 0.14634 | 1.0057 | 0.23475 | 0.5851 | 0.99888 | 0.08014 | 0.28705 |
| baseline_100x100 | 20260613 | False | False | 213 | 0.9973 | 0.9838 | 0.20635 | 0.15873 | 1.0335 | 0.32327 | 0.48867 | 0.96995 | 0.08657 | 0.28728 |
| baseline_100x100 | 20260614 | False | False | 133 | 0.9937 | 0.9822 | 0.23077 | 0.05128 | 0.9925 | 0.24059 | 0.5553 | 1.0 | 0.08 | 0.27223 |
| low_food_signal_100x100 | 20260610 | False | False | 80 | 0.9938 | 0.9748 | 0.125 | 0.25 | 1.0314 | 0.219 | 0.52255 | 1.0 | 0.08 | 0.29397 |
| low_food_signal_100x100 | 20260611 | False | False | 162 | 0.9733 | 0.9777 | 0.125 | 0.14583 | 1.1264 | 0.28805 | 0.50109 | 0.97084 | 0.08494 | 0.32287 |
| low_food_signal_100x100 | 20260612 | False | False | 133 | 1.0088 | 0.9974 | 0.07692 | 0.07692 | 1.1685 | 0.3108 | 0.502 | 0.98084 | 0.10767 | 0.2985 |
| low_food_signal_100x100 | 20260613 | False | False | 156 | 0.9742 | 0.971 | 0.13043 | 0.17391 | 1.0606 | 0.29359 | 0.41839 | 0.9739 | 0.08462 | 0.28752 |
| low_food_signal_100x100 | 20260614 | False | False | 130 | 0.99 | 0.9826 | 0.12821 | 0.20513 | 1.089 | 0.21094 | 0.56163 | 1.0 | 0.08015 | 0.27528 |
| large_world_200x200_same_density_long_budget | 20260610 | False | False | 78 | 1.0011 | 0.9959 | 0.04348 | 0.13043 | 1.0565 | 0.17645 | 0.57762 | 0.998 | 0.08 | 0.33134 |
| large_world_200x200_same_density_long_budget | 20260611 | False | False | 73 | 0.9943 | 0.9865 | 0.19048 | 0.14286 | 1.0275 | 0.17821 | 0.50122 | 1.0 | 0.08 | 0.32 |
| large_world_200x200_same_density_long_budget | 20260612 | False | True | 91 | 1.0136 | 1.0083 | 0.07407 | 0.07407 | 1.0295 | 0.17943 | 0.57099 | 1.0 | 0.08 | 0.31119 |
| large_world_200x200_same_population_long_budget | 20260610 | False | False | 15 | 0.9946 | 1.0092 | 0.25 | 0.0 | 0.786 | 0.1236 | 0.52904 | 1.0 | 0.08 | 0.40648 |
| large_world_200x200_same_population_long_budget | 20260611 | False | False | 33 | 0.9928 | 0.9957 | 0.0 | 0.11111 | 1.1262 | 0.142 | 0.58425 | 1.0 | 0.08 | 0.41581 |
| large_world_200x200_same_population_long_budget | 20260612 | False | False | 14 | 0.979 | 0.9954 | 0.25 | 0.0 | 0.7767 | 0.20593 | 0.50696 | 1.0 | 0.08 | 0.30449 |

## Interpretation

- `current_position_control` เป็น control หลักของ Phase 5
- 200x200 conditions เป็น stress/blocker diagnosis ไม่ใช่ hard gate ในรอบนี้
- ถ้า total quality ผ่านแต่ component เดียว dominate ต้องตีความอย่างระวัง

## Limits

- ยังไม่ได้ทำ memory-disabled หรือ reward-shuffled ablation
- quality score เป็น observer score ไม่ใช่ perception ของ agent
- large-world failure ต้องแยกต่อว่าเป็น time budget, density, หรือ exploration limitation

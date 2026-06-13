# รายงาน Phase 4.1: Return-Signal Falsification

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase4_1_falsification_confirm01_20260613`

## Objective

ทดสอบข้อสงสัยว่า Phase 4 ผ่านเพราะ agent กลับ patch เฉพาะตัวจริง หรือเพราะทุก agent ถูก food attraction / world density ดึงเข้าพื้นที่อาหารเหมือนกันหมด

## Conditions

- `baseline_100x100`: Phase 4 baseline world and food-signal settings. (world=100x100, food_signal_radius_cap=None, plant_weight=1.35)
- `low_food_signal_100x100`: Reduce food-signal radius and remove extra plant-lifecycle attraction weight. (world=100x100, food_signal_radius_cap=2, plant_weight=1.0)
- `large_world_200x200`: Scale world area 4x while keeping food and seed capacity density roughly similar. (world=200x200, food_signal_radius_cap=None, plant_weight=1.35)

## Aggregate Results

| condition | runs | pass | patches | patch food | return agents | dropper return rate | dropper lift | non-dropper lift | prod lift |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 3 | 3 | 9.0 | 27.3333 | 50.0 | 0.851 | 89.8897 | 31.792 | 7.757 |
| low_food_signal_100x100 | 3 | 3 | 12.6667 | 27.6667 | 50.0 | 0.8601 | 129.574 | 22.746 | 10.8067 |
| large_world_200x200 | 3 | 0 | 2.3333 | 1.3333 | 20.0 | 0.3519 | 52.4885 | 13.09 | 5.584 |

## Per-Run Results

| condition | seed | pass | patches | patch chains | patch food | return agents | dropper return rate | dropper lift | non-dropper lift | pre-drop visits | visit delta |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 20260610 | True | 9 | 11 | 33 | 50 | 0.69231 | 71.636 | 31.457 | 11 | 14273 |
| baseline_100x100 | 20260611 | True | 8 | 7 | 14 | 50 | 0.93617 | 144.673 | 44.818 | 109 | 5213 |
| baseline_100x100 | 20260612 | True | 10 | 12 | 35 | 50 | 0.92453 | 53.36 | 19.101 | 101 | 4218 |
| low_food_signal_100x100 | 20260610 | True | 9 | 11 | 31 | 50 | 0.86207 | 121.951 | 21.901 | 24 | 7981 |
| low_food_signal_100x100 | 20260611 | True | 17 | 13 | 35 | 50 | 0.86813 | 164.44 | 22.661 | 47 | 5929 |
| low_food_signal_100x100 | 20260612 | True | 12 | 5 | 17 | 50 | 0.85 | 102.331 | 23.676 | 262 | 10886 |
| large_world_200x200 | 20260610 | False | 0 | 0 | 0 | 0 | 0.0 |  |  | 0 | 0 |
| large_world_200x200 | 20260611 | False | 2 | 2 | 3 | 23 | 0.5 | 49.501 | 10.791 | 18 | 409 |
| large_world_200x200 | 20260612 | False | 5 | 1 | 1 | 37 | 0.55556 | 55.476 | 15.389 | 52 | 854 |

## Interpretation Rules

- ถ้า dropper return rate/lift ต่ำ แต่ non-dropper lift สูง แปลว่า signal หลักน่าจะเป็น food hotspot หรือ social/foraging attraction
- ถ้า low-food-signal แล้วยังมี patch productivity แต่ return ลดลงมาก แปลว่า Phase 4 productivity ยังอยู่ แต่ return metric เดิม inflated
- ถ้า world ใหญ่ขึ้นแล้ว return agents ลดลงมาก แปลว่าโลก 100x100 อาจเล็ก/หนาแน่นเกินสำหรับ claim เรื่อง patch-specific behavior

## Limitations

- นี่เป็น falsification gate ขนาดเล็ก ไม่ใช่ replication ระดับ paper
- ยังไม่ได้ปิด memory หรือ shuffled reward labels
- ยังไม่ได้บังคับ same-agent ownership เป็น success gate

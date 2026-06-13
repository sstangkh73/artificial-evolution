# รายงาน Phase 4.1: Return-Signal Falsification

วันที่รัน: 2026-06-13
ชุดข้อมูล: `data\phase4_1_falsification_smoke_20260613`

## Objective

ทดสอบข้อสงสัยว่า Phase 4 ผ่านเพราะ agent กลับ patch เฉพาะตัวจริง หรือเพราะทุก agent ถูก food attraction / world density ดึงเข้าพื้นที่อาหารเหมือนกันหมด

## Conditions

- `baseline_100x100`: Phase 4 baseline world and food-signal settings. (world=100x100, food_signal_radius_cap=None, plant_weight=1.35)

## Aggregate Results

| condition | runs | pass | patches | patch food | return agents | dropper return rate | dropper lift | non-dropper lift | prod lift |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 1 | 0 | 1.0 | 3.0 | 28.0 | 0.2 | 24.29 | 16.344 | 6.133 |

## Per-Run Results

| condition | seed | pass | patches | patch chains | patch food | return agents | dropper return rate | dropper lift | non-dropper lift | pre-drop visits | visit delta |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 20260610 | False | 1 | 2 | 3 | 28 | 0.2 | 24.29 | 16.344 | 11 | 4156 |

## Interpretation Rules

- ถ้า dropper return rate/lift ต่ำ แต่ non-dropper lift สูง แปลว่า signal หลักน่าจะเป็น food hotspot หรือ social/foraging attraction
- ถ้า low-food-signal แล้วยังมี patch productivity แต่ return ลดลงมาก แปลว่า Phase 4 productivity ยังอยู่ แต่ return metric เดิม inflated
- ถ้า world ใหญ่ขึ้นแล้ว return agents ลดลงมาก แปลว่าโลก 100x100 อาจเล็ก/หนาแน่นเกินสำหรับ claim เรื่อง patch-specific behavior

## Limitations

- นี่เป็น falsification gate ขนาดเล็ก ไม่ใช่ replication ระดับ paper
- ยังไม่ได้ปิด memory หรือ shuffled reward labels
- ยังไม่ได้บังคับ same-agent ownership เป็น success gate

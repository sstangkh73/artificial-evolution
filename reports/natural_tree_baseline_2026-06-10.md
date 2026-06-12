# Natural Tree Baseline Report - 2026-06-10

## Abstract

รอบนี้แก้ world physics ฝั่งพืชให้ต้นไม้แพร่เมล็ดเองตามธรรมชาติ มี origin ของเมล็ด/ต้นไม้ และมีเหตุผลการตายของพืช จากนั้นรัน probe เพื่อดูว่า chain `seed -> plant -> fruit -> agent/decay` เกิดจริงไหม ผลหลังแก้พบจุดเปลี่ยนชัดเจน: ผลไม้จาก plant lifecycle ถูกกิน 51 ครั้ง, เน่า 337 ครั้ง, ต้นไม้แพร่เมล็ดเอง 1,219 ครั้ง, และมีต้นไม้ตาย 865 ครั้ง โดยไม่มี `seed_picked` หรือ `seed_dropped` จาก agent เลย

## Introduction

คำถามหลักคือโลกควรมีต้นไม้โตเองตามธรรมชาติหรือไม่ และถ้าเมล็ดไม่ถูก agent พาไปไหน ควรสุ่มงอกใกล้บริเวณที่ตกหรือบริเวณต้นแม่หรือไม่ คำตอบเชิงระบบคือควรมี เพื่อไม่ให้โลกต้องพึ่ง agent ในการสร้าง ecology ขั้นแรกทั้งหมด แต่ต้องวัดแยกให้ได้ว่า ecology นั้นเกิดจากธรรมชาติหรือจาก agent

## Methods

Baseline ก่อนแก้ใช้ไฟล์:

`data/long_no_oracle_15min_20260610_body37_fate_tracking.json`

ผลหลังแก้ใช้คำสั่ง:

```powershell
python scripts\run_long_emergence_watch.py --time-limit-seconds 45 --progress-every-seconds 10 --evaluate-every-ticks 5000 --event-sample-limit 800 --width 40 --height 40 --max-food 320 --base-food-spawn-per-tick 4 --food-spawn-multiplier 0.7 --bootstrap-food-spawn-ticks 300 --wild-food-spawn-after-bootstrap-multiplier 0.10 --natural-seed-rain-per-tick 0 --max-plant-seeds 900 --seed 20260610 --body-index 37 --initial-population 50 --max-population 180 --output data\natural_tree_baseline_20260610_body37_v2.json
```

เงื่อนไขสำคัญ: `natural-seed-rain-per-tick=0` ดังนั้นเมล็ดธรรมชาติหลังช่วงเริ่มต้นต้องมาจากต้นที่โตในโลก ไม่ใช่ seed rain ที่ตกลงมาจากระบบ

## Implementation

เปลี่ยนหลัก:

- เพิ่ม metadata ให้ seed/plant: `parent_plant_id`, `dispersal_mode`, `dropped_by_agent_id`, `created_tick`
- เพิ่ม natural offspring seed drop จากต้นที่โตแล้ว โดยดรอปใกล้ต้นแม่และขึ้นกับ fertility/nutrients
- เพิ่ม plant death event พร้อมเหตุผล เช่น `no_biomass`, `max_age`, `low_viability`
- เพิ่ม telemetry แยก origin: `natural_drop`, `harvest_drop`, `agent_carried`, `agent_disturbed`, `natural_seed_rain`
- แก้ sample logger ให้เก็บตัวอย่างต่อ event kind ไม่ให้ event ช่วงต้นกิน buffer จนหลักฐานช่วงท้ายหาย

ไฟล์หลักที่แก้:

- `world/environment.py`
- `scripts/run_long_emergence_watch.py`

## Results

ก่อนแก้:

- tick/day: 1000 / 50
- `plant_fruited`: 2
- `plant_lifecycle_food_consumed`: 0
- `plant_lifecycle_food_decayed`: 1
- `natural_seed_dropped`: 0
- `plant_died`: 0
- `seed_picked`: 0
- `seed_dropped`: 0

หลังแก้:

- tick/day: 5000 / 250
- `plant_fruited`: 413
- `plant_lifecycle_food_consumed`: 51
- `plant_lifecycle_food_decayed`: 337
- `plant_lifecycle_food remaining`: 25
- `natural_seed_dropped`: 1,219
- `plant_died`: 865
- `seed_germinated`: 876
- `plant_matured`: 188
- `seed_picked`: 0
- `seed_dropped`: 0

Plant origin snapshot หลังแก้:

- `natural_drop`: 492
- `natural_drop_mature`: 51
- `natural_drop_sprout`: 235
- `natural_drop_seed`: 206
- `harvest_drop`: 23
- `harvest_drop_sprout`: 10
- `harvest_drop_seed`: 13

Hotspots ที่สำคัญ:

- natural seed drop กระจุกที่ `(10,23)`, `(10,25)`, `(8,26)`, `(8,25)`, `(8,27)`
- seed germination กระจุกที่ `(9,22)`, `(10,23)`, `(7,28)`, `(9,26)`, `(13,28)`
- fruit consumed กระจุกที่ `(9,22)`, `(11,24)`, `(9,26)`, `(7,26)`, `(17,22)`

ตัวอย่าง event:

```text
natural_seed_dropped -> seed=110 parent=103 x=10 y=25 mode=natural_drop depth_cm=0.61 distance=2
plant_fruited -> seed=103 species=wild_grain x=9 y=24 energy=9 biomass=0.84 light=0.31
plant_lifecycle_food_consumed -> agent=5 plant=153 x=13 y=22 energy=8 kind=raw_plant
plant_lifecycle_food_decayed -> plant=103 x=9 y=24 energy=9 age_ticks=86
plant_died -> seed=137 species=wild_grain x=9 y=20 state=mature age_ticks=901 reason=max_age mode=natural_drop parent=116
```

## Discussion

หลังแก้ โลกมี plant ecology ที่เดินเองได้ชัดเจน เมล็ดจากต้นแม่เกิดใกล้ต้นแม่ งอก โต ออกผล ถูกกินหรือเน่า และต้นไม้มีวงจรตาย สิ่งนี้ตอบโจทย์ว่าต้นไม้ควรโตเองตามธรรมชาติ ไม่ต้องรอ agent ค้นพบการปลูกก่อน เพราะในโลกจริงระบบพืชก็แพร่พันธุ์เองอยู่แล้ว

แต่ผลนี้ยังไม่ใช่หลักฐานว่า agent "ทำฟาร์ม" เพราะ `seed_picked=0` และ `seed_dropped=0` แปลว่า agent ยังไม่ได้เก็บ/ย้าย/วางเมล็ดเพื่อจัดการพื้นที่ สิ่งที่เกิดคือระบบนิเวศธรรมชาติสร้างอาหารขึ้นมา แล้ว agent บางตัวเดินไปกินผลไม้ที่เกิดในโลก

สิ่งที่น่าสนใจคือ fruit consumption เกิดหลัง tick 2930 ขณะที่ plant fruit/decay เกิดก่อนหน้านั้นมาก แปลว่า agent ไม่ได้เข้าใจ chain ตั้งแต่ต้น แต่ hunger/path interaction พาไปเจอแหล่งอาหารของ plant lifecycle ภายหลัง

## Limitations

- ยังไม่มีหลักฐานการสื่อสารหรือการเรียนรู้เชิงสัญลักษณ์เกี่ยวกับเมล็ด
- การดรอปเมล็ดธรรมชาติยังเป็น rule-based plant reproduction ไม่ใช่ผลจาก agent
- ต้นไม้ยังไม่มี pollination, genetic variation, canopy competition แบบละเอียด
- เปรียบเทียบก่อน/หลังไม่ใช่ controlled rate comparison เต็มรูปแบบ เพราะหลังแก้ตั้ง `evaluate_every_ticks=5000` เพื่อให้โลกเดินนานพอจับ natural lifecycle
- agent ยัง immortal ดังนั้นผลด้าน survival pressure ยังไม่เหมือนโลกจริงทั้งหมด

## Future Work

รอบถัดไปควรวัดเพิ่ม:

- เมล็ดที่ agent เหยียบ/รบกวนแล้วโต เทียบกับเมล็ดที่โตเอง
- ระยะห่างระหว่าง parent plant กับ offspring plant เมื่อ mature
- fruit consumption ต่อ agent เพื่อดูว่ามี specialist หรือ route learning หรือไม่
- seed pickup/drop ถ้าเกิดขึ้นในรันยาวกว่า 15 นาที
- spatial mutual information ระหว่าง agent visits, fruit locations, seed germination, mature plant clusters

## Conclusion

ระบบหลังแก้พร้อมกว่าเดิมมากสำหรับคำถาม "AI เรียนรู้อะไรจากโลกใหม่" เพราะตอนนี้โลกมี ecological feedback loop จริงให้เรียนรู้แล้ว แต่ยังต้องแยกให้ชัดว่า ecology ที่เกิดเองไม่เท่ากับ agriculture โดย agent เป้าหมายถัดไปจึงควรเป็นการวัดว่า agent เริ่มย้ายเมล็ดหรือวนกลับไปยังแหล่งผลไม้ซ้ำอย่างมีนัยสำคัญหรือไม่

# รายงาน Long Run: No-Oracle Plant Lifecycle Breakthrough

วันที่: 2026-06-10

## Abstract

รัน substrate-first/no-oracle เพื่อตรวจว่าหลังตัดตัวช่วยหลักออกแล้ว โลกยังเกิดจุดเปลี่ยนเองได้หรือไม่ โดยกำหนดเพดานเวลา 15 นาที แต่หยุดก่อนเพราะเจอ signal น่าสนใจ: เมล็ดที่เกิดจากการเก็บพืชและถูกฝังด้วย `surface_disturbed` สามารถงอก โตเต็มวัย และออกผลเป็น `plant_lifecycle` food ได้โดยไม่ใช้ oracle perception, cooking/share scaffold, `build_nest`, หรือ `tend_food_patch`.

## Experiment Setup

- Script: `scripts/run_long_emergence_watch.py`
- Output หลัก: `data/long_no_oracle_15min_20260610_body37_breakthrough_detailed.json`
- Stdout log: `data/long_no_oracle_15min_20260610_body37_breakthrough_detailed.out.log`
- Manual continuation log: `data/long_no_oracle_15min_20260610_body37.out.log`
- Seed: `20260610`
- Body: `body_index=37`, `sensor=2, muscle=2, armor=0, brain=2, profile=social_planner`
- Initial population: 50 immortal agents
- World: 40x40
- Max time: 900 seconds
- Stop detector: `plant_lifecycle_breakthrough`
- Natural seed rain: 0
- Wild food mode: bootstrap-limited
- No-oracle defaults:
  - `legacy_oracle_perception_enabled=False`
  - `legacy_scaffold_nest_enabled=False`
  - `scaffolded_social_support_enabled=False`

Run command:

```powershell
python scripts\run_long_emergence_watch.py --time-limit-seconds 900 --progress-every-seconds 30 --evaluate-every-ticks 100 --event-sample-limit 300 --width 40 --height 40 --max-food 320 --base-food-spawn-per-tick 4 --food-spawn-multiplier 0.7 --bootstrap-food-spawn-ticks 300 --wild-food-spawn-after-bootstrap-multiplier 0.10 --natural-seed-rain-per-tick 0 --max-plant-seeds 800 --seed 20260610 --body-index 37 --initial-population 50 --max-population 180 --output data\long_no_oracle_15min_20260610_body37_breakthrough_detailed.json
```

## Results

Official stopped run:

- Stop reason: `interesting_signal:plant_lifecycle_breakthrough`
- Wall time: 8.008 seconds
- Simulation tick/day: 900 / day 45
- Population: 50
- Peak population: 50
- Births: 0
- Nests: 0
- Food sources at stop: `plant_lifecycle=1`
- Plant counts: `seed=66`, `mature=1`
- Mean hunger: 0.983
- Mean safety: 0.004
- Instinct states: `hunger=50`

Event counts:

- `surface_disturbed`: 3357
- `harvest_seed_dropped`: 110
- `seed_buried_by_disturbance`: 44
- `seed_germinated`: 44
- `plant_matured`: 1
- `plant_fruited`: 1
- `build_nest`: 0
- `tend_food_patch`: 0
- `birth`: 0

First event ticks:

- `surface_disturbed`: 1
- `harvest_seed_dropped`: 2
- `seed_buried_by_disturbance`: 13
- `seed_germinated`: 40
- `plant_matured`: 811
- `plant_fruited`: 812

Key event chain:

```text
seed_buried_by_disturbance -> seed=103 x=9 y=24 depth_cm=0.34 disturbance=0.31
seed_germinated -> seed=103 species=wild_grain x=9 y=24 water=0.65 temp_k=281.7 oxygen=0.21 light=0.00 nutrients=0.81 depth_cm=1.0
plant_matured -> seed=103 species=wild_grain x=9 y=24 biomass=1.00 light=0.32 nutrients=0.77
plant_fruited -> seed=103 species=wild_grain x=9 y=24 energy=9 biomass=0.83 light=0.32
```

Manual continuation:

- Initial background run was allowed to continue after the first breakthrough.
- At elapsed 30 seconds: tick 4570 / day 228, `plant_matured=1`, `plant_fruited=3`.
- At elapsed 120 seconds: tick 20004 / day 1000, still `plant_matured=1`, `plant_fruited=3`.
- No `birth`, `build_nest`, `tend_food_patch`, or `technology_emerged` followed.

## Observation

จุดเปลี่ยนที่น่าสนใจเกิดขึ้นจริง: หลังปิดตัวช่วยหลัก เมล็ดสามารถผ่านวงจรฟิสิกส์ขั้นต่ำได้ครบจาก harvest seed drop -> burial by disturbance -> germination -> maturity -> fruiting.

แต่จุดเปลี่ยนนี้เป็นระดับ ecology ของโลกมากกว่าระดับ cognition ของ agent. Agents ยังไม่แสดงพฤติกรรมว่าเข้าใจหรือใช้ประโยชน์จาก plant lifecycle food ต่อ:

- ไม่มี seed pickup/drop ในรอบ official
- ไม่มีการสร้าง hotspot ฟาร์ม
- ไม่มี birth
- ทุกตัวเข้าสู่ hunger instinct
- mean hunger ค้างที่ 0.983

## Pattern

ระบบพืชเริ่มทำงานได้โดยไม่ต้องมี oracle หรือ scaffold แต่ agent economy ยังล้มเร็ว:

1. Agents เดินและรบกวนผิวดินจำนวนมาก
2. Wild bootstrap food ถูกกินและดรอปเมล็ด
3. เมล็ดบางส่วนถูก disturbance กลบจนถึง depth ที่ germinate ได้
4. เมล็ดจำนวนหนึ่งงอก
5. อย่างน้อยหนึ่งต้นโตและออกผล
6. ผลไม้/อาหารจาก plant lifecycle ไม่ถูกแปลงเป็น behavioral recovery

## Possible Causes

- Food bootstrap สั้นเกินไปเมื่อเทียบกับเวลาที่ agent ต้องรักษาพลังงาน
- Agents อยู่ใน hunger loop จน movement เป็น survival search มากกว่าการกลับไปใช้แหล่งพืช
- Perception หลังตัด oracle ยังเป็น scalar local signal แต่ไม่มี causal memory ว่า cell ไหนเคยมี seed/plant/fruit
- Plant lifecycle food มีน้อยมาก (`plant_lifecycle=1`) จึงยังไม่พอสร้าง safety/comfort window
- Body 37 แม้มี sensor/muscle แต่ metabolism และ food access ยังไม่พอให้หลุดจาก hunger

## Alternative Causes

- Light/season timing อาจทำให้พืชส่วนใหญ่ไม่โตต่อ แม้ germinate ได้
- Disturbance อาจฝังเมล็ดลึกเกิน optimal ในบางพื้นที่
- Event detector หยุดเร็วเมื่อเจอต้นแรกออกผล จึงยังไม่เห็นว่าถ้าปล่อยต่อเต็ม 15 นาทีจะเกิด cluster หรือไม่ อย่างไรก็ตาม manual continuation ถึง day 1000 ยังไม่เห็นการต่อยอด

## Conclusion

ตอนนี้ระบบพร้อมสำหรับการทดลอง discovery ขั้นแรกมากขึ้นแล้ว เพราะโลกสามารถสร้างอาหารจาก plant lifecycle ได้โดยไม่ต้องมีตัวช่วยเดิม นี่เป็น breakthrough ทาง substrate.

แต่ยังไม่พบหลักฐานว่า AI เรียนรู้ความสัมพันธ์เชิงเหตุผล `seed -> plant -> food` หรือใช้ประโยชน์จากผลลัพธ์นั้นเอง จุดต่อไปควรไม่ใช่เพิ่มคำสั่งให้มันปลูก แต่ควรเพิ่ม measurement และ memory แบบประสบการณ์ตรง เช่นจำว่า "เคยกินอาหารตรงนี้หลังจากเคยมีพืชตรงนี้" โดยไม่เฉลยว่าเมล็ดคือสาเหตุ.

## Recommended Verification

1. รันซ้ำหลาย seed เพื่อดูว่า `plant_lifecycle_breakthrough` reproducible แค่ไหน
2. เพิ่ม telemetry สำหรับ cell history:
   - seed buried location
   - germination location
   - mature/fruit location
   - agent revisit count after fruiting
   - agent consume plant_lifecycle food count
3. เพิ่ม detector สำหรับ "agent response to fruiting":
   - agent เข้าหา fruit cell หลัง `plant_fruited`
   - agent กิน `plant_lifecycle` food
   - agent กลับมาบริเวณเดิมซ้ำมากกว่าค่า random baseline
4. Sweep ecology:
   - bootstrap duration
   - plant growth rate
   - fruiting interval
   - local food signal radius

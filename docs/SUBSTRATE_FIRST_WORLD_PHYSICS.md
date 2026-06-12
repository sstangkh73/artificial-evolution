# Substrate-First World Physics

วันที่จัดทำ: 2026-06-08
สถานะ: design correction / next implementation direction

## Core Decision

โครงการควรเปลี่ยนจากการใส่ "ระบบสำเร็จรูป" ให้ agent เช่น `build_nest`, `farm`, `craft_tool`, `cook_food`
ไปเป็นการใส่กฎของโลก วัสดุ พืช น้ำ แรง และเวลาให้มากพอ แล้วปล่อยให้พฤติกรรมระดับสูงเกิดจาก primitive actions ของ agent เอง

หลักการ:

> Do not simulate the invention. Simulate the substrate that makes the invention possible.

ดังนั้นคำว่า `บ้าน`, `รัง`, `ฟาร์ม`, `เครื่องมือ`, `ครัว`, `เตา`, `สวน` ไม่ควรเป็น action หรือ reward สำเร็จรูปในระยะยาว
แต่ควรเป็น label ที่นักวิจัยตีความภายหลังจาก configuration ของวัตถุและผลกระทบที่เกิดจริงในโลก

## What Is Wrong With The Current Nest Abstraction

`Nest` ปัจจุบันยังเป็น scaffold:

- เกิดจาก action สำเร็จรูป `build_nest`
- ให้ `safe_radius` สำเร็จรูป
- มี `food_storage` และ `material_storage` สำเร็จรูป
- เป็น gate ของ reproduction
- กลายเป็นที่ตั้ง hearth โดยอัตโนมัติ

นี่มีประโยชน์สำหรับ prototype แต่ไม่เหมาะกับคำถามว่า AI ค้นพบบ้านเองหรือไม่

สถานะที่ถูกต้องกว่า:

- agent ไม่ควรรู้จัก "สร้างบ้าน"
- agent ควรทำได้แค่ move, pick, drop, push, pull, strike, scrape, cut, tie, stack, dig, cover, pour, wait
- ถ้าวัตถุถูกจัดเรียงจนกันลม/ลดอันตราย/เก็บความร้อน/กันเด็กหลง/เก็บอาหารได้ เราจึงค่อยตีความว่าเป็น shelter/home/nest

## Physics Layer Needed For Shelter

### Materials

เริ่มจากวัสดุที่มีโอกาสใช้สร้าง shelter:

- wood
- branch
- log
- leaf
- fiber
- vine
- grass
- stone
- clay
- soil
- sand
- water

แต่ละวัสดุควรมี:

- mass
- volume
- density
- shape class
- length / width / thickness
- compressive strength
- tensile strength
- bending strength
- shear strength
- friction coefficient
- moisture absorption
- decay rate
- flammability
- cutting resistance
- binding compatibility

ตัวอย่างกฎ:

```text
wood_beam รับแรงกดตามแนวแกนได้ X newtons
wood_beam รับ bending moment ได้น้อยกว่าแรงกดตามแนวแกน
fiber/vine รับแรงดึงได้ดี แต่รับแรงกดไม่ได้
leaf กันฝน/แดดได้บางส่วน แต่รับน้ำหนักต่ำ
clay เปียกขึ้นรูปได้ แห้งแล้วแข็งขึ้น แต่แตกเมื่อแรงดึงสูง
stone รับแรงกดสูง ตัดยาก หนัก เคลื่อนยาก
```

### Force And Contact

ไม่ต้องเริ่มด้วย rigid-body simulator เต็มรูปแบบ แต่ควรมี contact/structure model ที่วัดได้:

- object support graph
- load path
- normal force
- friction threshold
- bending stress
- tie/bind constraint strength
- collapse when stress exceeds material limit
- shelter coverage area derived from object geometry

ผลลัพธ์ที่เกิดเอง:

- pile
- wall-like barrier
- roof-like cover
- enclosure
- elevated platform
- collapsed pile

ห้าม hardcode ว่า "ถ้าวางไม้ 3 ชิ้น = บ้าน"

## Physics Layer Needed For Cutting And Tools

Agent ไม่ควร craft `knife` จาก recipe ตรง ๆ

ควรมี:

- edge sharpness
- hardness
- toughness
- contact pressure
- impact energy
- abrasion
- fracture
- wear
- handle leverage

กฎตัวอย่าง:

```text
ถ้า edge hardness > target cutting resistance
และ contact pressure สูงพอ
และ motion เป็น slicing/striking
วัสดุเป้าหมายจะเสียหายหรือถูกแยก
```

เครื่องมือเกิดจากวัตถุที่มี property ใช้งานได้ ไม่ใช่จากชื่อ recipe

## Biology Layer Needed For Seeds And Farming

ห้ามใช้กฎแบบ `bury seed -> plant grows`

Seed/plant ควรเป็น living process:

### Seed State

- species
- viability
- dormancy
- age
- moisture content
- nutrient reserve
- required germination temperature range
- required moisture range
- required oxygen range
- light sensitivity
- burial depth tolerance

### Soil Cell State

แต่ละ cell ควรมี:

- water content
- humidity
- temperature
- oxygen
- nitrogen
- phosphorus
- potassium
- organic matter
- pH approximation
- salinity approximation
- compaction
- microbial fertility proxy
- light exposure

### Germination

เมล็ดงอกเมื่อเงื่อนไขสะสมครบ ไม่ใช่ทันที:

```text
if seed.viable
and soil_water in species range
and temperature in species range
and oxygen enough
and burial_depth within range
and accumulated_good_hours >= threshold:
    seed -> sprout
```

### Growth

พืชโตจาก resource balance:

```text
growth_rate = f(light, water, nutrients, temperature, oxygen, age)
stress = drought + flooding + nutrient_deficit + heat/cold + shade
biomass += growth_rate - stress_cost
```

### Reproduction

พืชควรสร้าง seed เมื่อ:

- maturity reached
- season/temperature/light condition ผ่าน
- biomass/reserve พอ
- stress ไม่สูงเกินไป

ฟาร์มจึงไม่ใช่ action แต่เป็น pattern:

- agent ทำให้ seed กระจายซ้ำในพื้นที่หนึ่ง
- water/nutrient/light ดีขึ้นจากการกระทำ primitive
- plant survival/yield สูงกว่าพื้นที่ control

เราจึงตีความภายหลังว่าเป็น cultivation/farming

## Implemented First Substrate Slice

สถานะโค้ดหลังการแก้รอบแรก:

- `MaterialSpec` มีสมบัติแสง/คลื่นและแรงพื้นฐานเพิ่มแล้ว เช่น `photosynthetic_transmittance`, `solar_reflectance`, `solar_absorptance`, `infrared_transmittance`, `compressive_strength_mpa`, `tensile_strength_mpa`, `bending_strength_mpa`, `cutting_resistance_n`
- `leaf` ไม่ถูกตีความว่า "กันแดด" แบบคำสำเร็จรูป แต่เป็นผิววัสดุที่ยอมให้พลังงานบางช่วงผ่านได้บางส่วน และดูดกลืน/สะท้อนบางส่วน
- `Environment` มี `photosynthetic_light_map` และ soil nutrient maps สำหรับ nitrogen/phosphorus/potassium
- เพิ่ม `PlantSeed` และ `PlantSpeciesSpec` สำหรับ seed lifecycle
- seed ไม่งอกทันที แต่ต้องสะสมเงื่อนไขน้ำ อุณหภูมิ ออกซิเจน depth และเวลาครบก่อน
- plant growth ใช้ balance จาก light, water, nutrients, temperature, oxygen
- mature plant สร้าง `FoodResource(source="plant_lifecycle")` เมื่อ biomass และสภาพแวดล้อมพอ
- telemetry เพิ่ม `plants_total`, `plant_state_seed`, `plant_state_sprout`, `plant_state_mature`, `mean_photosynthetic_light`, `mean_soil_nutrients`

## Implemented Scaffold Removal And Instinct Slice

สถานะโค้ดหลังการแก้รอบถัดมา:

- `scaffolded_agent_actions_enabled=False` เป็นค่า default ของโลก
- `build_nest`, `tend_food_patch`, nest material collection, hearth maintenance, and nest object experimentation ไม่ถูกเรียกใน agent tick เมื่อ scaffold flag ปิด
- `Environment.build_nest()` และ `Environment.tend_food_patch()` guard ตัวเองด้วย flag เดียวกัน เพื่อกัน code path เก่าเรียกตรง
- `natural_seed_rain_per_tick=0` เป็นค่า default; โลกไม่โปรย seed ให้เองแล้ว
- raw plant ที่ถูก harvest จะสร้าง `harvest_seed_dropped` และฝาก `PlantSeed` ไว้ที่ cell นั้น
- seed ที่ตกใหม่เริ่มที่ `burial_depth_cm=0.0`; ต้องค่อยๆ settle จากผิวดิน/ความชื้นก่อน จึงจะเข้าเงื่อนไข germination depth ได้
- agent มี primitive seed handling แบบไม่สอนความหมาย: อาจ `seed_picked` / `seed_dropped` จาก curiosity/gather drive แต่ไม่มี reward หรือ recipe ว่า seed ใช้ปลูก
- starvation ไม่ฆ่า agent โดยตรงแล้ว แต่เข้าสู่ `instinct_state="hunger"` และบังคับให้หาอาหารเป็น priority แรก
- เพิ่ม instinct พื้นฐาน `hunger`, `cold`, `fear`; เมื่อ active จะข้าม high-level/reproduction behavior ใน tick นั้น
- ambient food ลดลงต่อเนื่องผ่าน `food_pressure_multiplier` และ `food_decay_resources`; food ที่ค้างในโลกไม่ควรสะสมจนกลบ plant lifecycle เหมือนรอบก่อน

ข้อจำกัดใหม่: ยังมี wild plant food spawn เป็นแหล่งตั้งต้นของอาหารและ seed เพราะถ้าไม่มีพืชตั้งต้นเลย seed ecology จะไม่มีต้นทางให้ agent harvest ได้ รอบทดลองถัดไปควรแยก source นี้จาก plant lifecycle ให้ชัดในการวิเคราะห์

## Agent Primitive Actions

ควรลด action ระดับสูงเหลือ primitives:

- move
- look / sense
- pick up
- drop
- carry
- push
- pull
- strike
- scrape
- cut / slice attempt
- dig
- cover
- uncover
- pour water
- stack
- tie / bind
- untie
- wait / observe
- eat

Action เหล่านี้ไม่มีคำว่า house/farm/tool

## Emergence Labels For Analysis Only

คำเหล่านี้ใช้ใน analysis ไม่ใช่ action:

- shelter: object arrangement reduces exposure/danger
- storage: repeated object/food placement in bounded location
- farm: planted/managed area yields more food over time than control
- tool: object repeatedly improves action efficiency
- hearth: sustained combustion region with heat field
- path/trail: repeated movement changes terrain/memory/use

## Measurement Criteria

### Shelter Emergence

วัดจาก:

- coverage area
- wind/rain/danger exposure reduction
- thermal stability
- child survival improvement
- repeated return behavior
- structural stability duration

### Tool Emergence

วัดจาก:

- object use count
- action success improvement
- wear pattern
- transfer between users
- shape/property correlation with utility

### Farming Emergence

วัดจาก:

- seed density generated by agent actions
- germination rate vs unmanaged control cells
- biomass/yield over time
- soil nutrient/water changes caused by agent actions
- repeated tending behavior

## Migration Plan

### Phase A: Freeze High-Level Scaffold

- Mark current `Nest`, `tend_food_patch`, and named tool recipes as prototype scaffolds
- Keep them only for old experiments
- Do not use them as evidence of true discovery

### Phase B: Add Substrate Objects

- Add physical object geometry/load fields
- Add primitive placement/carry/drop actions
- Add structure evaluator that emits `structure_state`, not `house_built`

### Phase C: Add Seed And Soil Biology

- Add seed objects
- Add soil nutrient/water/light state
- Add germination/growth/reproduction over time
- Remove direct managed-food boost from farming claims

### Phase D: Run Discovery Experiments

- Give agents primitive actions only
- Start with materials, seeds, water, soil, food pressure, seasons
- Measure whether shelter/farming/tool patterns emerge without named systems

## Success Criteria

We can claim discovery only if:

- no high-level action names encode the target behavior
- outcome labels are derived after the fact from physical state
- ablation of physical affordances removes the behavior
- behavior transfers to altered environments
- repeated runs show nontrivial recurrence, not one lucky artifact

## Immediate Conclusion

The current world has useful material/thermal physics, but shelter and farming are still too scaffolded.
The next serious step is to make house/farm/tool impossible to call directly, and make them emerge from material mechanics, plant biology, water, nutrients, time, and primitive actions.

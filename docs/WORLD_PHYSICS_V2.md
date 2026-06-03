# World Physics V2

## ภาษาไทย

### เป้าหมาย
ระบบนี้เปลี่ยนโลกจากการเขียนผลลัพธ์สำเร็จรูป เช่น `cook -> cooked_food` ไปสู่โลกที่อาศัย
`material properties + environmental fields + process rules`
แล้วปล่อยให้ผลลัพธ์เกิดจากปฏิสัมพันธ์ของระบบเอง

เป้าหมายของ V2 ไม่ใช่การจำลองระดับโมเลกุลเต็มรูปแบบ แต่คือการใช้
- ฟิสิกส์จริงในส่วนที่คุ้มกับซิม
- เคมีเชิงสถานะในส่วนที่ต้องการประสิทธิภาพ

แนวคิดหลักคือ `simulate causes, not predefined outcomes`

### ขอบเขตรุ่นแรก
รุ่นแรกของระบบรองรับวัสดุและสนามหลักดังนี้

- วัสดุ: `water`, `soil`, `clay`, `stone`, `sand`, `wood`, `leaf`, `fiber`, `ash`, `iron`
- สนามของโลก: `temperature`, `oxygen`, `moisture`
- กระบวนการหลัก: `drying`, `hearth combustion`, `pyrolysis/carbonization`, `oxidation-lite`, `softening`, `clay firing`, `stone thermal shock`

### สมการและกฎที่อิงโลกจริง

#### 1. ความร้อน
ใช้กรอบคิดจาก

`Q = m c ΔT`

และประมาณการการเปลี่ยนอุณหภูมิของวัตถุด้วยการผ่อนเข้าหาอุณหภูมิท้องถิ่นตาม
- thermal conductivity
- specific heat
- environmental moisture

ในโค้ดรุ่นแรกใช้ relaxation model แทน PDE เต็ม เพื่อคุมต้นทุนการคำนวณ

#### 2. การระเหย
น้ำในวัสดุจะลดลงเมื่อ
- อุณหภูมิสูงกว่าเกณฑ์ระเหย
- ความชื้นแวดล้อมต่ำ

แนวคิดอิงจากการระเหยจริง แต่ใช้รูปแบบ discretized:

`moisture_loss ~ f(T - 373.15K, local_moisture)`

#### 3. การเผาไหม้
การติดไฟต้องมีอย่างน้อย
- เชื้อเพลิง
- ออกซิเจน
- อุณหภูมิถึง ignition point

ในระบบรอบแรก hearth ใช้กฎ:

`burn_rate ~ hearth_intensity * oxygen_factor * moisture_penalty`

#### 4. Pyrolysis / Carbonization
วัสดุอินทรีย์ เช่นไม้และใบไม้ เมื่อได้รับความร้อนช่วงหนึ่งนานพอ จะเพิ่ม
- `carbon_fraction`
- `blackness`

ถ้าออกซิเจนต่ำ จะเอนเอียงไปทาง `charred`
ถ้าออกซิเจนสูงและร้อนเกิน ignition จะเอนเอียงไปทาง `ashy` หรือ `burned_out`

#### 5. Softening
วัสดุบางชนิด เช่นเหล็ก ใช้แนวคิด `softening point`
เมื่ออุณหภูมิสูงกว่าเกณฑ์ วัตถุจะถูก mark ว่า `softened`
เพื่อเปิดทางให้เฟสถัดไปเพิ่ม deformation และ forging

### Material Properties
วัสดุทุกชนิดมี property หลัก เช่น
- `density_kg_m3`
- `specific_heat_j_kgk`
- `thermal_conductivity_w_mk`
- `moisture_capacity`
- `ignition_point_k`
- `pyrolysis_point_k`
- `softening_point_k`
- `melting_point_k`
- `yield_strength_mpa`
- `char_yield`
- `oxidation_rate`
- `porosity`

ค่าที่ใช้ใน V2 เป็นค่า engineering-scale โดยประมาณเพื่อให้ซิมตอบสนองเชิงเหตุผล ไม่ใช่ค่าระดับห้องทดลองที่สมบูรณ์ทุกบริบท

### World Fields
ทุก cell ในโลกมีสนามหลัก:
- `ground_material`
- `temperature_k`
- `oxygen`
- `moisture`
- `surface_fuel`

การ map วัสดุพื้นผิวรุ่นแรกใช้ heuristic ตาม biome:
- พื้นที่ชุ่มและปลอดภัยเอนเอียงไปทาง `soil`
- พื้นที่แห้งเอนเอียงไปทาง `sand`
- พื้นที่รุนแรงเอนเอียงไปทาง `stone`
- ขอบโลกตั้งเป็น `water` เพื่อให้มี reservoir เชิงฟิสิกส์พื้นฐาน

### Object Physics
`PhysicalObject` ถูกขยายให้มี state ทางฟิสิกส์:
- `dominant_material`
- `temperature_k`
- `moisture_ratio`
- `oxygen_exposure`
- `volatile_fraction`
- `carbon_fraction`
- `ash_fraction`
- `thermal_dose`
- `blackness`
- `softened`
- `state_label`

สถานะที่เกิดได้ในรุ่นแรก:
- `raw`
- `waterlogged`
- `dried`
- `sun_dried`
- `blackened`
- `charred`
- `ashy`
- `fired_hard`
- `thermal_fractured`
- `packed_grit`
- `burned_out`

### Hearth Prototype
nest สามารถมี `hearth` ได้เมื่อมี
- wood / leaf / fiber
- oxygen พอ
- cognition ของผู้ดูแล hearth สูงพอ

V2 ยังไม่อ้างว่ามี “สูตรกองไฟสำเร็จรูป”
แต่ใช้การเผาไหม้แบบ field-driven แล้วให้ agent ทำแค่การ
- เติมเชื้อเพลิง
- รักษา hearth

### สิ่งที่ V2 ทำได้แล้ว
- โลกมี temperature / oxygen / moisture field
- nest มี hearth intensity, hearth fuel, hearth temperature, smoke
- object ใน nest ถูกความร้อนจริง
- ไม้/ใบไม้/ไฟเบอร์สามารถ dry / blacken / char / ash ได้
- ดินและ clay สามารถแห้งและแข็งตัวเป็น `fired_hard`
- หินสามารถเกิด `thermal_fractured` เมื่อร้อนจัดแล้วเจอความชื้น/thermal swing
- ash เริ่มเกิดเป็น byproduct ของ hearth
- ระบบ log physics events เช่น
  - `hearth_maintained`
  - `hearth_state`
  - `material_shift`

### สิ่งที่ยังไม่ทำใน V2
- fluid simulation ของน้ำ
- deformation จากแรงกดเต็มรูปแบบ
- fracture mechanics ของหิน
- metallurgy แบบ forge จริง
- phase diagram ของดิน/ทรายละเอียด
- gas transport แบบ PDE
- cooking chemistry ของอาหารแบบ digestibility/toxicity เต็มรูปแบบ

### ทิศทาง Phase ถัดไป
1. เพิ่ม `force / stress / deformation`
2. เพิ่ม `water transport` และ sediment
3. เพิ่ม `ore / bloom / hot-worked iron`
4. เปลี่ยน cooking จากระบบสำเร็จรูปไปเป็นผลจาก heat exposure
5. ให้ agent เรียนรู้จาก material outcomes แทน recipe

---

## English

### Goal
World Physics V2 shifts the simulation from predefined outcome rules such as `cook -> cooked_food`
toward a world governed by
`material properties + environmental fields + process rules`.

The purpose is not full molecular simulation. Instead, V2 uses
- real physics where it is computationally valuable
- state-based chemistry where abstraction is necessary

The guiding principle is `simulate causes, not predefined outcomes`.

### First-Scope Coverage
The first implementation introduces:

- Materials: `water`, `soil`, `clay`, `stone`, `sand`, `wood`, `leaf`, `fiber`, `ash`, `iron`
- World fields: `temperature`, `oxygen`, `moisture`
- Core processes: `drying`, `hearth combustion`, `pyrolysis/carbonization`, `oxidation-lite`, `softening`, `clay firing`, `stone thermal shock`

### Physics Basis

#### 1. Heat
The system is conceptually grounded in

`Q = m c ΔT`

Object temperature changes are approximated by relaxing toward local environmental temperature using
- thermal conductivity
- specific heat
- environmental moisture

The first implementation uses a lightweight relaxation model instead of a full PDE solver.

#### 2. Evaporation
Moisture decreases when
- temperature rises above evaporation thresholds
- local humidity is low

This is discretized as:

`moisture_loss ~ f(T - 373.15K, local_moisture)`

#### 3. Combustion
Ignition requires
- fuel
- oxygen
- temperature above ignition point

The first hearth model uses:

`burn_rate ~ hearth_intensity * oxygen_factor * moisture_penalty`

#### 4. Pyrolysis / Carbonization
Organic matter such as wood and leaves accumulates
- `carbon_fraction`
- `blackness`

under sufficiently high heat. Low oxygen biases outcomes toward `charred`, while high oxygen plus strong heat biases outcomes toward `ashy` or `burned_out`.

#### 5. Softening
Some materials, especially iron, expose a `softening point`.
Once exceeded, objects are marked `softened`, enabling later forging and deformation layers.

### Material Properties
Each material is described by a shared engineering-scale property schema:
- `density_kg_m3`
- `specific_heat_j_kgk`
- `thermal_conductivity_w_mk`
- `moisture_capacity`
- `ignition_point_k`
- `pyrolysis_point_k`
- `softening_point_k`
- `melting_point_k`
- `yield_strength_mpa`
- `char_yield`
- `oxidation_rate`
- `porosity`

These values are intended to be physically motivated rather than laboratory-complete.

### World Fields
Each world cell now carries:
- `ground_material`
- `temperature_k`
- `oxygen`
- `moisture`
- `surface_fuel`

The first ground-material map is biome-driven:
- wetter safe zones lean toward `soil`
- dry zones lean toward `sand`
- harsh terrain leans toward `stone`
- world borders are initialized as `water`

### Object Physics
`PhysicalObject` now stores thermal/material state:
- `dominant_material`
- `temperature_k`
- `moisture_ratio`
- `oxygen_exposure`
- `volatile_fraction`
- `carbon_fraction`
- `ash_fraction`
- `thermal_dose`
- `blackness`
- `softened`
- `state_label`

The first reachable object states are:
- `raw`
- `waterlogged`
- `dried`
- `sun_dried`
- `blackened`
- `charred`
- `ashy`
- `fired_hard`
- `thermal_fractured`
- `packed_grit`
- `burned_out`

### Hearth Prototype
Nests can maintain a `hearth` when they have
- wood / leaf / fiber fuel
- sufficient oxygen
- sufficiently capable cognitive agents tending it

V2 does not yet claim a full “fire recipe” system.
Instead, it implements field-driven burning and lets agents contribute by
- supplying fuel
- stabilizing the hearth

### What V2 Already Enables
- World temperature / oxygen / moisture fields
- Nest hearth intensity, fuel, temperature, and smoke
- Real thermal exposure for stored objects
- Wood/leaf/fiber drying, darkening, charring, and ash transitions
- Soil and clay drying/firing transitions
- Stone thermal-shock fracture states
- Ash as a hearth byproduct
- Physics event logs such as
  - `hearth_maintained`
  - `hearth_state`
  - `material_shift`

### Not Yet Included
- full water flow simulation
- full stress/deformation mechanics
- fracture mechanics for stone
- realistic metallurgy and forging
- detailed soil/sand phase behavior
- PDE-based gas transport
- full food chemistry and digestibility transformation

### Next Steps
1. Add `force / stress / deformation`
2. Add `water transport` and sediment behavior
3. Add `ore / bloom / hot-worked iron`
4. Replace hardcoded cooking with heat-exposure outcomes
5. Let agents learn from material outcomes rather than explicit recipes

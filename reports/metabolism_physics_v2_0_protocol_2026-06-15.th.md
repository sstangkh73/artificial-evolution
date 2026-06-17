# Protocol: Metabolism Physics v2.0 — Data-Model Scaffolding

วันที่: 2026-06-15
สถานะ: pre-implementation → implementing
อ้างอิงออกแบบหลัก: `reports/metabolism_physics_v2_design_2026-06-15.th.md`
ขอบเขต stage นี้: **v2.0 เท่านั้น** — เพิ่ม data model + ตาราง + pure functions + unit test ตัวแรกของ repo
**ไม่แตะ runtime:** `consume_food()` ยังใช้ v1 (`FOOD_ENERGY`) เหมือนเดิม → พฤติกรรม agent ไม่เปลี่ยนใน stage นี้

## Goal / Non-goal

Goal:
- วาง schema + ค่าคงที่ + ฟังก์ชันบริสุทธิ์ของ metabolism v2 ให้พร้อมต่อยอด v2.1
- ผูกยีนย่อยใน `BodyPlan` เข้ากับสูตรพลังงาน
- มี unit test ตัวแรกที่ตรวจ energy accounting และ ingestion gate

Non-goal (เลื่อนไป v2.1+):
- ยังไม่ wire พลังงานใหม่เข้า `consume_food()`
- ยังไม่ทำ gut/excretion (v2.2)
- ยังไม่ถอด `seed_hunger_drop_bonus` (รอ v2.2 ตอน gut เป็นช่องหลัก)

## ค่าคงที่ (โมดูลใหม่ `world/metabolism.py`)

`NUTRIENTS = [sugar, protein, fiber, shell, water, toxin]`

`ENERGY_DENSITY` (พลังงานต่อ 1 หน่วยมวล ถ้าย่อยสารนั้นได้ 100%):

| nutrient | density |
| --- | ---: |
| sugar | 18 |
| protein | 24 |
| fiber | 9 |
| shell | 0 |
| water | 0 |
| toxin | 0 |

`COMPOSITION` (สัดส่วนต่อชนิดอาหาร รวม = 1.0):

| kind | sugar | protein | fiber | shell | water |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw_plant | 0.20 | 0.05 | 0.30 | 0.10 | 0.35 |
| raw_meat | 0.00 | 0.55 | 0.00 | 0.00 | 0.45 |

`FOOD_MASS = {raw_plant: 1.0, raw_meat: 1.5}`
`FOOD_SIZE = {raw_plant: 2.0, raw_meat: 5.0}`

## ยีนย่อยใหม่ใน `BodyPlan` (heritable, มี default — ไม่กระทบโค้ดเดิม)

| field | default | บทบาท |
| --- | ---: | --- |
| `gape` | 5.0 | ขนาดปาก — ingestion gate |
| `gut_capacity` | 8.0 | ความจุท้อง (ใช้ v2.2) |
| `gut_transit_ticks` | 6 | เวลาผ่านท้อง (ใช้ v2.2) |
| `acid_strength` | 0.4 | กัดเปลือกเมล็ด (ใช้ v2.2) |
| `cellulose_efficiency` | 0.25 | ย่อย fiber |
| `toxin_tolerance` | 0.2 | ทนพิษ (ใช้ v2.3) |

`enzyme_profile` (property ที่ derive จากยีน):

```
sugar   = 0.9                              (universal baseline)
protein = 0.7 * meat_efficiency            (ใช้ยีนเดิม)
fiber   = cellulose_efficiency * plant_efficiency
shell   = 0.0                              (เปลือกย่อยด้วย enzyme ไม่ได้ ต้องใช้ acid_strength vs shell_hardness ใน v2.2)
water   = 0.0
```

## การเปลี่ยนโครงสร้างอื่น (additive, default-safe)

- `FoodResource` (env:357): + `seed_payload: int | None = None` (เตรียม v2.2 — ผลไม้พาเมล็ด)
- `Environment` (env:499): + field `metabolism_model: str = "v1"` (default v1 → pipeline เดิมไม่กระทบ)

## Pure functions (`world/metabolism.py`)

- `digestible_energy(composition, mass, enzyme) -> float`
  = `mass * Σ composition[n] * enzyme.get(n,0) * ENERGY_DENSITY[n]`
- `can_ingest(object_size, gape) -> bool` = `object_size <= gape`

## Unit test cases (`tests/test_metabolism.py` — ตัวแรกของ repo)

1. ทุก `COMPOSITION[kind]` รวม ≈ 1.0
2. `digestible_energy(raw_plant, default body enzyme)` ≈ **4.755** (คำนวณมือ: 3.24 + 0.84 + 0.675)
3. `digestible_energy(raw_meat, default body enzyme)` ≈ **13.86** (1.5 × 0.55×0.7×24)
4. `can_ingest(raw_meat size 5.0, gape 5.0)` = True; `can_ingest(6.0, 5.0)` = False
5. v1 ยังไม่เปลี่ยน: `FOOD_ENERGY[raw_plant]==6`, `FOOD_ENERGY[raw_meat]==18`

## Gate ก่อนไป v2.1

- unit test ทั้ง 5 ผ่าน
- import `world.environment` / `agents.body` ไม่พัง
- baseline พลังงาน v2 ≈ 4.76 (plant) / 13.86 (meat) เทียบ v1 6/18 → **คาดว่าต้อง re-tune ใน v2.1** (บันทึกไว้ ไม่ใช่ bug)

## Risk เฉพาะ v2.0

ต่ำ — ทุกการเปลี่ยนเป็น additive + default-safe และไม่แตะ runtime path. ความเสี่ยงจริงเริ่มที่ v2.1 ตอน wire energy ใหม่เข้า `consume_food()` แล้วต้อง re-run Phase 1 gate

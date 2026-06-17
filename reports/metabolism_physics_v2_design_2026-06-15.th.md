# Design Doc: Metabolism Physics v2 (Eating / Digestion / Gut / Excretion)

วันที่: 2026-06-15
สถานะ: **design / pre-implementation** (ยังไม่เขียนโค้ด)
ขอบเขต: รื้อระบบการกินทั้งหมดให้ฟิสิกส์เป็นผู้ตัดสิน แทนการ hard-code ว่าอะไรกินได้/อะไรเป็นเมล็ด
อ้างอิงโค้ดปัจจุบัน: `world/environment.py`, `agents/agent.py`, `agents/body.py`

---

## 1. วัตถุประสงค์และ root cause

### ปัญหาที่พบ (จาก Phase 5.5 + อ่านโค้ด 2026-06-15)

- เมล็ดกับอาหารเป็นคนละชนิดวัตถุ: อาหารอยู่ใน `food_positions` กินผ่าน `consume_food()`; เมล็ดอยู่ใน `plant_seeds` ทำได้แค่ pick/drop. **ไม่มี code path ใดเปลี่ยนเมล็ดเป็นพลังงาน**
- agent ไม่ได้ "เลือกไม่กินเมล็ด" — โลกไม่เคยให้ affordance การกินเมล็ดตั้งแต่แรก
- การวางเมล็ด 97.8% เกิดตอน critical hunger ส่วนหนึ่งเพราะ **`seed_hunger_drop_bonus` ที่ hard-code ไว้** (`agents/agent.py:794-795`) อีกส่วนเพราะ mean hunger = 0.983 ทำให้ทุกอย่างถูกแท็กว่า "เกิดตอนหิว"

### Root cause

ระบบการกินปัจจุบันเป็น **categorical + scripted**: ชนิดอาหารถูกกำหนดว่ากินได้ (`FOOD_ENERGY`), เมล็ดถูกกำหนดว่ากินไม่ได้, และการจัดการเมล็ดถูก bias ด้วยกฎที่เขียนมือ. สิ่งนี้ขัดกับ thesis หลักของงาน: *uninformed world — ให้ฟิสิกส์ตัดสิน ไม่ใช่ผู้ออกแบบ*

### เป้าหมาย

แทนที่ด้วยระบบ **physics-based metabolism**: วัตถุทุกชนิดมีขนาดและองค์ประกอบ; ร่างกายมีขนาดปากและความสามารถย่อยเป็นยีน; กินได้/ได้พลังงาน/กระจายเมล็ด **emerge จากฟิสิกส์ ไม่ใช่จากกฎที่เขียนมือ**

---

## 2. หลักการออกแบบ (ห้ามละเมิด)

1. **ไม่สอน semantics** — ห้ามมีคำว่า farm/plant/bury/seed-purpose/edible ในตรรกะการตัดสินใจของ agent
2. **ฟิสิกส์ตัดสิน ไม่ใช่ category** — "กินได้ไหม" = ขนาดเทียบขนาดปาก; "ได้พลังงานไหม" = องค์ประกอบเทียบความสามารถย่อย
3. **ความสามารถย่อยเป็นยีน** — อยู่ใน `BodyPlan` ถ่ายทอด/กลายพันธุ์ได้ ไม่ใช่ค่าคงที่ที่ผู้ออกแบบใส่
4. **ไม่มี oracle** — agent ไม่รู้ล่วงหน้าว่าอะไรมีพิษ/มีคุณค่า ต้องเรียนรู้จากผล (หรือถูก selection คัด)
5. **observable** — ทุก ingestion/digestion/excretion event ต้อง log พร้อม context พอให้ falsify ได้
6. **versioned** — เก็บ v1 ไว้ผ่าน config flag เพื่อให้ผล Phase 1-5 เดิม reproduce ได้

---

## 3. โมเดล 4 ชั้น

### ชั้น 1 — Ingestion gate (กลืนได้ไหม)

- วัตถุทุกชนิดมี `size` (หน่วยนามธรรมคงเส้นคงวา)
- `BodyPlan` เพิ่ม `gape` (ขนาดปาก) — เสนอ derive จาก `muscle_units`/morphology หรือเป็นยีนแยก
- **กฎ:** ingest ได้ถ้า `object.size <= body.gape`
- เลิกแบ่ง "เมล็ด vs อาหาร" — ทั้งคู่เป็น "ingestible object" ที่มี size + composition
- (อนาคต: วัตถุใหญ่กว่าปากเล็กน้อย อาจ "กัด" เป็นชิ้นได้ถ้ามี muscle/teeth พอ — เลื่อนไป v3)

### ชั้น 2 — Digestion (ได้พลังงานเท่าไร)

- วัตถุมี `composition`: สัดส่วน macronutrient เช่น
  `{sugar, protein, fiber, shell, water, toxin}` (รวม = 1.0)
- `BodyPlan` มี enzyme profile = ประสิทธิภาพย่อยต่อสารแต่ละชนิด เช่น
  `{sugar: 0.95, protein: 0.7, fiber: 0.2, shell: 0.0}`
  - **ใช้ของเดิมเป็นฐาน:** `plant_efficiency`, `meat_efficiency` มีอยู่แล้วใน `BodyPlan` → generalize
- **พลังงานที่ได้** = `mass * Σ (composition[n] * enzyme[n] * ENERGY_DENSITY[n])`
- `shell` = เปลือกเมล็ด ย่อยไม่ได้ (`enzyme[shell] ≈ 0`) → เมล็ดกลืนได้แต่ได้พลังงานน้อย เว้นแต่กัดเปลือกแตก

### ชั้น 3 — Gut transit + excretion (จุดพีค: dispersal ที่ emerge เอง)

- วัตถุที่กลืน เข้า `gut` (คิว) พร้อม `entry_tick`
- `BodyPlan` เพิ่ม `gut_transit_ticks`, `gut_capacity`, `acid_strength`
- แต่ละ tick: ดูดซับสารที่ย่อยได้ → เพิ่มพลังงาน; เลื่อน transit
- เมื่อครบ transit: **ขับถ่ายส่วนที่ย่อยไม่ได้ที่ตำแหน่งปัจจุบัน** (คนละที่กับที่กิน เพราะ agent เดินมาแล้ว)
- **เมล็ดในท้อง:**
  - ถ้า `acid_strength < seed.shell_hardness` → เปลือกไม่แตก → เมล็ดถูกขับออก **ทั้งเป็น** ที่ตำแหน่งใหม่ → **endozoochory (การกระจายเมล็ดผ่านระบบย่อย)**
  - ถ้า `acid_strength >= seed.shell_hardness` → เปลือกแตก → agent ได้พลังงานจากเนื้อใน แต่ **เมล็ดตาย** (`viability = 0`)
- **Migration จากของเดิม:** ปัจจุบัน `consume_food()` เรียก `_drop_harvest_seed()` หย่อนเมล็ดที่จุดกิน (ระยะ 0). v2 reroute เมล็ดนี้เข้า gut แทน → ออกที่ระยะ > 0 = dispersal จริง

### ชั้น 4 — Toxicity / cost (selection pressure — มีผลจริงเมื่อปิด immortality)

- บางวัตถุมี `toxin` > 0
- `BodyPlan` เพิ่ม `toxin_tolerance`
- ถ้า `toxin ingested > toxin_tolerance` → เสียพลังงาน/บาดเจ็บ
- สร้างเหตุผลให้ "การเลือกกิน" มีค่า → ต่อยอด Phase 6 (selection) โดยตรง

---

## 4. การเปลี่ยน data model (อ้างฟิลด์จริง)

| โครงสร้าง | ฟิลด์ที่เพิ่ม | หมายเหตุ |
| --- | --- | --- |
| `FoodResource` (env:357) | `size`, `composition`, `seed_payload` | เริ่มจากตาราง lookup ตาม `kind` ก่อน (เหมือน `FOOD_ENERGY`) แล้วค่อยทำ per-instance |
| `PlantSpeciesSpec` (env:366) | `seed_size`, `shell_hardness`, `seed_nutrient_payload` | frozen — เพิ่มใน spec ของ `wild_grain` |
| `PlantSeed` (env:412) | ใช้ `viability` เดิม + `dispersal_mode="gut_passed"` | gut passage แก้ viability (scarification เพิ่ม / acid ฆ่า) |
| `BodyPlan` (body:134) | `gape`, `gut_capacity`, `gut_transit_ticks`, `acid_strength`, `cellulose_efficiency`, `toxin_tolerance` | ยีนถ่ายทอดได้ ต่อจาก `plant_efficiency`/`meat_efficiency` |
| `Agent` (agent.py) | `gut: list[GutItem]` | คิวของที่กลืน + entry_tick |
| `Environment` config | `metabolism_model = "v1"\|"v2"` | backward compat |

ค่าคงที่ใหม่: `ENERGY_DENSITY` (ต่อ nutrient), `COMPOSITION` (ต่อ food kind) — แทนที่ `FOOD_ENERGY` คงที่

---

## 5. ผลที่คาดว่าจะ emerge (สมมติฐานเชิงบวก)

1. **Endozoochory** — เมล็ดที่รอด gut ถูกขับออกที่ระยะ > 0 จากจุดกิน = การกระจายเมล็ดที่ไม่ได้ถูก code (ต่างจาก `seed_hunger_drop_bonus` ที่เขียนมือ)
2. **Nutrient loop** — มูลที่ย่อยไม่ได้อาจคืน fertility ให้ดิน (เชื่อม `_consume_soil_nutrients`/fertility เดิม) → เมล็ดงอกในดินที่ปุ๋ยดีขึ้น ณ จุดขับถ่าย → วงจรปิด
3. **Diet trade-off (สำคัญสุดเชิงวิวัฒนาการ)** — ท้องกรดแรง = ได้พลังงานจากเมล็ดมาก แต่ฆ่าเมล็ด (seed predator); ท้องกรดอ่อน = ได้พลังงานน้อย แต่กระจายเมล็ดเป็น (seed disperser). เมื่อเปิด selection (Phase 6) แรงกดดันอาจดัน 2 ทางตาม ecology — นี่คือ trade-off จริงในธรรมชาติ
4. **ลด hunger confound** — แหล่งพลังงานหลากหลายขึ้น → mean hunger น่าจะต่ำกว่า 0.983 → คลาย confound ที่ทำ Phase 5 พัง

---

## 6. การออกแบบการทดลองต่อชั้น (ตาม experiment-design skill)

### Layer 1+2 — Ingestion + Digestion

- **IV:** distribution ของ object size; body `gape`; enzyme profile
- **DV:** energy intake rate; diet composition (อะไรถูกกิน); mean hunger level
- **Control:** v1 metabolism (ของเดิม) เป็น baseline; matched ecology config
- **Metric:** energy accounting balance (unit test); hunger เฉลี่ย; % object ที่ถูกกินภายใน gape
- **Success:** mean hunger < 0.7 โดยไม่สอน foraging; agent กินเฉพาะ object ภายใน gape; พลังงานตรงกับสูตร composition×enzyme
- **Failure:** hunger ไม่ลด/แย่ลง; agent กินของใหญ่กว่าปาก (bug); energy ไม่ balance

### Layer 3 — Gut + excretion (endozoochory)

- **IV:** `seed.shell_hardness` เทียบ `body.acid_strength`; gut_transit_ticks
- **DV:** % เมล็ดที่ถูกขับออกทั้งเป็น; dispersal distance (จุดขับ − จุดกิน); germination rate ของเมล็ดผ่าน gut เทียบ control
- **Control:**
  - null model: random-walk เพื่อหา expected distance ถ้าไม่มี dispersal จริง
  - matched: เมล็ดที่หย่อนที่จุดกิน (v1 `_drop_harvest_seed`, ระยะ 0)
- **Metric:** mean/median dispersal distance; survive-gut fraction; germination lift
- **Success:** เมล็ดที่ `shell_hardness > acid_strength` รอด gut อัตราสูง + ขับที่ระยะ > null model อย่างมีนัย โดยไม่มีกฎ hunger/farming
- **Failure (falsification):** dispersal distance ≈ 0 (agent ขับที่เดิมที่กิน) → ไม่ใช่ dispersal จริง แค่ delay

### Layer 4 — Toxicity / selection (ต้องรอ Phase 6 mortality)

- **IV:** สัดส่วน object มีพิษ; `toxin_tolerance` ของ lineage
- **DV:** survival เทียบความเสี่ยงอาหาร; diet shift ข้ามรุ่น
- **Success:** lineage ที่เลี่ยงพิษอยู่รอด/สืบพันธุ์ดีกว่า โดยไม่มีการสอน
- **Failure:** ไม่มี diet shift แม้มี selection → toxicity ไม่สร้างแรงกดดันจริง

---

## 7. แผน falsification ต่อ claim (ตาม hypothesis-testing skill)

| Claim | สิ่งที่จะ falsify มัน |
| --- | --- |
| "ระบบการกินเป็น physics-based ไม่ใช่ scripted" | grep หา hard-coded edibility/seed bias ที่หลงเหลือ — ต้องเป็นศูนย์ |
| "เกิด endozoochory จริง" | dispersal distance ไม่ต่างจาก random-walk null → reject |
| "ลด hunger confound" | mean hunger ยัง ≈ 0.98 หลังเปลี่ยน → ระบบไม่ช่วย |
| "diet trade-off เป็น emergent" | ถ้า acid_strength ไม่ส่งผลต่อ survive-gut fraction → กลไกไม่ทำงาน |

ทุกรายงานต้องมี: Evidence Supporting / Evidence Against / Alternative Explanations / Missing Evidence / Confidence Level

---

## 8. ความเสี่ยง / สิ่งที่จะพัง (ตาม engineering skill: "what can break?")

1. **Re-tuning ecology ทั้งหมด (เสี่ยงสูงสุด)** — Phase 1 tune fruiting/seed params ให้ balance กับ `FOOD_ENERGY` คงที่. เปลี่ยน energy model = ต้อง **re-run Phase 1 gate ใหม่**. นี่คือต้นทุนเวลาใหญ่สุด
2. **Performance** — gut digestion loop ต่อ tick = O(agents × gut_items). ต้อง cap `gut_capacity`. 100×100/50 agents โอเค; 200×200 ต้องวัด
3. **Backward compatibility** — ผล Phase 1-5 อยู่ใต้ physics v1. ต้อง version ชัด ไม่งั้นเทียบผลข้าม physics = apples-to-oranges
4. **Confound ใหม่** — worst case: ระบบใหม่สร้าง confound ใหม่ (เช่น excretion clustering) หรือทำ hunger แย่ลง
5. **`FoodResource` เป็น frozen dataclass** — เพิ่มฟิลด์ต้องอัปเดตทุกจุดที่สร้าง (env:2192, 2303, 2519, ...) — ใช้ default value ลดความเสี่ยง

**Assumptions ที่ต้องระบุ:** หน่วย size/energy เป็นนามธรรมแต่คงเส้นคงวา; digestive traits ถ่ายทอดได้; immortality ยังเปิดในชั้น 1-3 (ปิดเมื่อทดสอบชั้น 4)

---

## 9. Backward compatibility / versioning

- เพิ่ม config `metabolism_model`; default = `"v1"` เพื่อไม่กระทบ pipeline เดิม
- v2 เป็น opt-in ต่อ experiment
- รายงาน v2 ทุกฉบับระบุ `metabolism_model=v2` ชัดเจนบนหัว
- เก็บ `FOOD_ENERGY` เดิมไว้สำหรับ v1; v2 ใช้ `COMPOSITION × ENERGY_DENSITY`

---

## 10. Roadmap การ implement (build order)

| Stage | ขอบเขต | Gate ก่อนไป stage ถัดไป |
| --- | --- | --- |
| **v2.0** | data model + config flag + COMPOSITION/ENERGY_DENSITY tables | unit test: energy accounting balance; v1 ยัง reproduce ได้ |
| **v2.1** | ชั้น 1+2 (gape gate + digestion energy) แทน `FOOD_ENERGY` | re-run Phase 1 ecology gate ผ่านใต้ v2; mean hunger วัดได้ |
| **v2.2** | ชั้น 3 (gut + excretion + reroute `_drop_harvest_seed`) | endozoochory smoke: dispersal distance > null model |
| **v2.3** | ชั้น 4 (toxin) — โครงไว้ก่อน เปิดจริงตอน Phase 6 | toxin ลดพลังงานได้จริงใน unit test |

**ลำดับสำคัญ:** อย่าแตะ Phase 5 site-selection จนกว่า v2.1 จะผ่าน Phase 1 gate ใหม่ — เพราะ hunger confound อาจหายไปเองหลังเปลี่ยน energy model

---

## 11. คำถามออกแบบที่ต้องตัดสินใจก่อนเขียนโค้ด

1. **หน่วย** — ใช้ค่านามธรรม (เร็ว, พอสำหรับงานวิจัย) หรืออิง cm/แคลอรีจริง (สมจริงแต่ tune ยาก)? → เสนอ **นามธรรม**
2. **เก็บช่อง hand-carry เมล็ดไว้ไหม** หรือใช้ gut-only? ถ้าเก็บ ต้อง **ถอด `seed_hunger_drop_bonus`** ออก (จุดที่ไม่ซื่อสัตย์) → เสนอ gut เป็นช่องหลัก, hand-carry เก็บได้แต่ตัด hunger bias
3. **มูลคืน fertility ให้ดินไหม** (nutrient loop) — ทำใน v2.2 เลย หรือเลื่อน? → เสนอ **เลื่อนเป็น v2.2b** กันซับซ้อนเกิน
4. **ยอมรับต้นทุน re-tune Phase 1 ใหม่ไหม** — นี่คือ commitment เวลาจริง
5. **digestive traits กลายพันธุ์ได้เลยไหม** — ถ้าใช่ ปลดล็อก selection-on-diet ใน Phase 6 → เสนอ **ใช่ (heritable)**

---

## Decisions Locked (2026-06-15)

ผู้วิจัยตัดสินใจแล้ว:

1. **Seed channel = Gut หลัก + ถอด `seed_hunger_drop_bonus`** — endozoochory เป็นช่องกระจายเมล็ดหลัก; เก็บการคาบด้วยมือ (pick/drop) ไว้ได้ แต่ **ต้องถอด `seed_hunger_drop_bonus` (`agents/agent.py:794-795`) ออก** เพื่อปิดจุดที่ไม่ซื่อสัตย์ การวางเมล็ดที่เหลือต้องมาจากฟิสิกส์ (carry transit / jostling) ไม่ใช่กฎ hunger
2. **Build scope = ถึง v2.2 (รวม endozoochory)** — ยอมรับต้นทุน re-run Phase 1 gate ใต้ physics ใหม่
3. (default ตามข้อเสนอ) หน่วยนามธรรม; nutrient loop เลื่อนเป็น v2.2b; digestive traits heritable

---

## สรุป

นี่ไม่ใช่ feature ใหม่ แต่เป็นการ **แก้ root cause เชิงปรัชญาของงาน** — เปลี่ยนจาก "ผู้ออกแบบบอกว่าอะไรกินได้" เป็น "ฟิสิกส์ตัดสิน" ผลพลอยได้คือ endozoochory และ diet trade-off ที่ emerge เอง ซึ่งเป็น centerpiece ที่แข็งกว่าระบบ pick/drop เดิมมาก

ต้นทุนหลักคือการ re-tune ecology ใต้ physics ใหม่ (ต้อง re-run Phase 1 gate) ก่อนกลับไปแตะ Phase 5

**ขั้นต่อไป:** ตอบคำถามข้อ 11 (โดยเฉพาะข้อ 2 และ 4) แล้วจึงเริ่ม v2.0

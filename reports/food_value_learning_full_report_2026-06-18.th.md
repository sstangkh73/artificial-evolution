# รายงานฉบับเต็ม: agent เรียนรู้ไหมว่าอาหารบางอย่าง "กินได้แต่ไม่คุ้ม"?

**โครงการ:** Artificial Evolution (ส่วนทดลองของข้อเสนอ TURC2026)
**วันที่:** 2026-06-18
**ผู้ทดลอง:** Chisanupong
**commit ที่เกี่ยวข้อง:** `6add9c1` (study A scaffold), `d627bd4` (study B mechanism), `45b1d82` (รายงานย่อ)
**สถานะ:** การทดลองครบและ verify แล้ว · โค้ดทั้งหมด default-off · v1 byte-identical · unit tests 25/25

---

## บทคัดย่อ (Abstract)

รายงานนี้ตอบคำถามว่า agent ในระบบจำลองชีวิตเทียม **เรียนรู้ภายในช่วงชีวิต** ได้หรือไม่ว่าอาหารบางชนิด "กินได้แต่ไม่คุ้มค่าพลังงาน" ในเมื่อด่านการกินปัจจุบันตัดสินด้วย **ขนาดปากเทียบขนาดอาหารเท่านั้น** (ปากใหญ่กว่า = กินได้ทุกอย่าง)

เราตรวจสถาปัตยกรรมจากโค้ดจริง พบว่า (1) การกินเป็น **value-blind** — `_consume_current_food` กินทุกสิ่งที่ปากรับได้ทุก tick โดยไม่มีการตัดสิน "ความคุ้ม", (2) ความจำเป็น **เชิงตำแหน่งล้วน** (จำว่าเคยกินตรงไหน ไม่จำชนิด/ค่า)

จากนั้นทำ 2 การทดลอง: **A (baseline)** เพิ่มอาหารค่าต่ำ `raw_seed` (พลังงาน ~1 เทียบผล ~5) แล้ววัดว่า agent กินมั่วไหม; **B** เพิ่มกลไกเรียนรู้ค่าอาหารจากประสบการณ์ แล้ววัดว่าเกิดการเลี่ยงไหม

ผลหลัก 3 ข้อ: (1) **ไม่มีกลไก → ไม่เรียนรู้** — agent กินอาหารค่าต่ำในอัตราคงที่ ~400 หน่วย/1000 ticks ตลอด 6000 ticks ไม่เคยลด; (2) **มีกลไก experience-driven value-learning → เรียนรู้จริง** — เกิด acquisition curve ที่อัตราการกินดิ่งสู่ 0 (เลิกกินสนิทหลัง ~3000 ticks) โดยเรียนจากพลังงานที่ได้จริง ไม่ใช่ฮาร์ดโค้ด; (3) **แต่ภายใต้เศรษฐกิจพลังงานจริง การเรียนรู้ถูกกลบสนิท** เพราะ agent อยู่ที่พลังงาน ≤ 0 เกือบตลอด (perma-starvation) → กฎ "กำลังอดตายก็กินทุกอย่าง" เด้งทุกครั้ง

ข้อสรุปสำคัญ: **เศรษฐกิจพลังงาน (ภาวะอดอยากถาวร) คือคอขวดร่วม** ที่บล็อกพฤติกรรมระดับสูงทุกอย่างในระบบ — การเลือกกิน (B), การเลือกที่ดรอปเมล็ด (Phase 5), การสืบพันธุ์ (births=0) และ Phase 6 selection การแก้เศรษฐกิจพลังงานคือกุญแจร่วมที่ปลดล็อกทั้งหมด

---

## 1. บทนำ (Introduction)

### 1.1 ปัญหา
หลักการแกนของโครงการคือ **"โลกไม่บอก semantics ปล่อยให้ฟิสิกส์ตัดสิน"** (uninformed world, let physics decide) ในด้านการกิน หลักการนี้สะท้อนผ่าน Metabolism Physics v2: วัตถุจะกินได้ก็ต่อเมื่อ **ขนาดพอดีปาก** (`can_ingest`) และให้พลังงานเท่าที่ร่างกายย่อยองค์ประกอบของมันได้ (`digestible_energy`)

แต่หลักการนี้เปิดช่องคำถาม: ถ้าการตัดสินใจกิน "ดูแค่ขนาด" agent ที่มีปากใหญ่จะกินทุกอย่างที่เจอ รวมถึงของที่ให้พลังงานน้อยจนแทบไม่คุ้ม **แล้ว agent จะ "ฉลาดขึ้น" ได้ไหม — เรียนรู้จากการกินซ้ำๆ ว่าของบางอย่างไม่คุ้ม แล้วเลิกเสียเวลากับมัน?** นี่คือพฤติกรรม optimal foraging ที่สัตว์จริงทำได้

### 1.2 ช่องว่างงานวิจัย (research gap)
Phase 2 ของโครงการพิสูจน์แล้วว่า agent มี **place-based learning** (จำตำแหน่งที่เคยได้รางวัล แล้วกลับไป, return lift 33–52×) แต่ยังไม่เคยตรวจว่ามี **value/diet learning** หรือไม่ — คือการเรียนรู้ "คุณค่าของชนิดอาหาร" ไม่ใช่แค่ "ตำแหน่ง"

### 1.3 สมมติฐาน (hypotheses)
- **H1 (null):** ด้วยสถาปัตยกรรมปัจจุบัน agent ไม่เรียนรู้ค่าอาหาร — กินของค่าต่ำในอัตราคงที่ตลอดชีวิต
- **H2:** ถ้าเพิ่มกลไกที่จำพลังงานที่ได้จริงต่อชนิด แล้วใช้ตัดสินใจกิน agent จะเกิดการเลี่ยงอาหารค่าต่ำแบบ emergent (อัตราการกินลดลงตามเวลา)
- **H3 (ค้นพบระหว่างทาง):** แม้กลไกจะทำงาน เศรษฐกิจพลังงานที่ทำให้ agent อดอยากถาวรจะกลบการเลี่ยง (สัตว์ที่กำลังอดตายย่อมกินทุกอย่าง)

---

## 2. การวิเคราะห์สถาปัตยกรรม (จากโค้ดจริง)

การกินและการเรียนรู้แยกได้เป็น 3 ชั้น มีเพียงชั้นเดียวที่ "ค่าอาหาร" มีผล และมันไม่ใช่การเรียนรู้:

| ชั้น | กลไก (ไฟล์:บรรทัด) | ใช้ "ความคุ้ม"? | เป็นการเรียนรู้? |
| --- | --- | --- | --- |
| เดินเข้าหา | `food_signal_at` ถ่วงด้วย `energy/(ระยะ+1)²` (`world/environment.py`) | ✅ พลังงานสูง = สัญญาณแรงกว่า | ❌ sensory ทันที (เอาอาหารออกสัญญาณก็หาย) |
| ตัดสินใจกิน | `_consume_current_food` → `_fits_mouth` (ขนาดอย่างเดียว) (`agents/agent.py:174`, `:764`) | ❌ ปากใหญ่กว่า = กินหมด | ❌ ไม่มีการตัดสินใจ — เรียกทุก tick ไม่มีเงื่อนไข |
| ความจำ | `remembered_food`, `remembered_food_sources` = list พิกัด (x,y) (`agents/agent.py:75`) | ❌ จำแค่ตำแหน่ง | ✅ แต่เชิงตำแหน่งเท่านั้น (Phase 2) |

**นัยสำคัญ:** ก่อนการทดลอง ระบบ **ไม่มี substrate** ใดๆ ที่จะให้ "เรียนรู้ค่าอาหาร" ได้เลย — แม้แต่ความจำก็ไม่เก็บว่าอาหารชนิดไหนให้พลังงานเท่าไร

### 2.1 โครงสร้างพลังงานอาหาร (`world/metabolism.py`)
พลังงานย่อยได้ = `mass × Σ (สัดส่วนสารอาหาร × เอนไซม์ของร่างกาย × ความหนาแน่นพลังงาน)`
เอนไซม์ default body 37: sugar 0.9, protein 0.7, fiber 0.25, **shell 0.0**, water 0.0

| food kind | องค์ประกอบ | mass | size | พลังงานย่อยได้ (default body) |
| --- | --- | ---: | ---: | ---: |
| raw_plant (ผล) | sugar .20 / protein .05 / fiber .30 / shell .10 / water .35 | 1.0 | 2.0 | 4.755 → **5** |
| raw_meat (เนื้อ) | protein .55 / water .45 | 1.5 | 5.0 | ~13.9 → **14** |
| **raw_seed (เมล็ด, เพิ่มใหม่)** | sugar .10 / fiber .25 / **shell .60** / water .05 | 0.4 | 1.0 | 0.873 → **1** |

raw_seed ถูกออกแบบให้ **"กินได้แต่ไม่คุ้ม"**: ขนาดเล็ก (1.0) พอดีทุกปาก, แต่ 60% เป็นเปลือก (shell) ที่ย่อยไม่ได้ → ได้พลังงานแค่ ~20% ของผล

---

## 3. ระเบียบวิธี (Methods)

### 3.1 การออกแบบการทดลอง

| | Experiment A | Experiment B |
| --- | --- | --- |
| **IV (ตัวแปรต้น)** | เวลา (tick) | เวลา + เปิด/ปิดกลไกเรียนรู้ค่าอาหาร |
| **DV (ตัวแปรตาม)** | จำนวนเมล็ดค่าต่ำที่กินต่อ window | เดียวกัน + learned value ต่อชนิด |
| **Control** | seed/world/config เดียวกัน, หาร availability ออก (`seed_frac`) | เดียวกัน + sweep starvation floor |
| **Success (H2)** | — | seed กิน/seed_frac **ลดลงตามเวลา** = เกิดการเรียนรู้ |
| **Failure / null (H1)** | seed กินคงที่ ไม่ลด = value-blind | ไม่ลด = กลไกไม่ทำงาน |

### 3.2 คอนฟิกร่วม (canonical gate config)
body 37 (`sensor=2, muscle=2, armor=0, brain=2, social_planner`), โลก 100×100, `max_food=2000`, `max_plant_seeds=7600`, `base_food_spawn_per_tick=4`, `food_spawn_multiplier=0.70`, `bootstrap_food_spawn_ticks=300`, plant lifecycle multipliers (growth 2.0, fruiting interval 0.25, fruiting chance 2.0 ฯลฯ), `immortal=True`, ประชากรเริ่ม 50, **`metabolism_model=v2`**, seed 20260610
อาหารค่าต่ำ: `low_value_food_spawn_per_tick=6` (raw_seed 6 หน่วย/tick กระจายสุ่มทั่วโลก, สลายตามปกติ)

### 3.3 กลไก Experiment B (เรียนรู้จากประสบการณ์ ไม่ฮาร์ดโค้ด)
- `food_value_memory: dict[kind→float]` — ค่าเฉลี่ยเคลื่อนที่ (EMA, α=0.3) ของ **พลังงานที่ได้จริง** เมื่อกินชนิดนั้น (`_learn_food_value`)
- กฎตัดสินใจ optimal-diet (`_food_worth_eating`):
  1. ชนิดที่ยังไม่รู้ค่า → **กิน (ชิมก่อน 1 ครั้ง)** เสมอ
  2. พลังงาน ≤ `diet_starvation_energy` (floor) → **กินทุกอย่าง** (กำลังอดตาย)
  3. ไม่งั้น → ข้ามถ้า `value[kind] < diet_pickiness(0.5) × ค่าที่ดีที่สุดที่รู้จัก`
- **แยกจาก hunger flag โดยตั้งใจ** เพราะ metric ความหิวตัน (ดู §4.4)

### 3.4 หมายเหตุเรื่อง replication (สำคัญต่อการตีความ)
ผลทุก seed **identical เป๊ะ** เพราะการเคลื่อนที่ของ agent ใช้ `Random(self.agent_id + self.age)` (`agents/agent.py:909,938`) ซึ่งไม่ผูกกับ `args.seed` → ระบบเป็น **deterministic n=1** ตัวเลขในรายงานนี้จึง **reproducible เป๊ะ** ไม่ใช่ค่าสุ่มที่ต้องหา CI (ข้อจำกัด: ยังเคลม multi-seed replication ไม่ได้จนกว่าจะผูก seed เข้า movement RNG)

### 3.5 เมตริก
- `seed_eat` / `plant_eat` = จำนวนมื้อต่อชนิดต่อ window (จาก `diet_by_kind` = ผลรวม `meals_by_type` ทุก agent)
- `seed_frac` = `seed_eat / seed_available` (หาร availability ออก; `food_spawned_by_kind` นับทั้ง wild spawn + ผลจาก plant lifecycle)
- `seed_share` = `seed_eat / (seed_eat + plant_eat)` (สัดส่วนในมื้อ)
- `learned_food_value` = ค่าเฉลี่ย `food_value_memory` ต่อชนิดข้าม agent

---

## 4. ผลการทดลอง (Results)

### 4.1 Experiment A — value-blind baseline

| window | seed กิน | seed_frac | plant กิน | plant_frac | seed_share |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0–1000 | 513 | 0.092 | 93 | 0.274 | 0.847 |
| 1000–2000 | 507 | 0.091 | 141 | 0.691 | 0.782 |
| 2000–3000 | 351 | 0.063 | 322 | 0.465 | 0.522 |
| 3000–4500 | 409 | 0.050 | 1114 | 0.471 | 0.269 |
| 4500–6000 | 375 | 0.046 | 1699 | 0.361 | 0.181 |

- **seed กินคงที่ ~350–510/window ตลอด 6000 ticks ไม่เคยดิ่งสู่ 0** (รวม 2155 มื้อ) → สนับสนุน H1: ไม่มีการเรียนรู้
- มี selectivity (plant_frac > seed_frac ~3–7 เท่า) **ตั้งแต่ window แรก** (0.274 vs 0.092) → มาจาก sensory gradient ไม่ใช่การเรียนรู้ (ไม่ได้ค่อยๆ แรงขึ้น)
- `seed_share` ลด 85%→18% **เป็น artifact ของ availability** — ผลไม้ค่าสูงเยอะขึ้นมาก (plant กิน 93→1699) ไม่ใช่การเลี่ยงเมล็ด (seed_frac แทบนิ่ง 0.092→0.046)

### 4.2 Experiment B — เปิดกลไก, ใช้ starvation floor ปกติ (=6)

| window | seed กิน | seed_frac | plant กิน | seed_share | learned (seed, plant) |
| --- | ---: | ---: | ---: | ---: | --- |
| 0–1000 | 498 | 0.090 | 82 | 0.859 | 1.0, 5.0 |
| 1000–2000 | 463 | 0.083 | 153 | 0.752 | 1.0, 5.0 |
| 2000–3000 | 425 | 0.077 | 365 | 0.538 | 1.0, 5.0 |
| 3000–4500 | 467 | 0.057 | 900 | 0.342 | 1.0, 5.0 |
| 4500–6000 | 436 | 0.053 | 1165 | 0.272 | 1.0, 5.0 |

- agent **เรียนรู้ค่าถูกต้อง** (seed=1.0 ≪ plant=5.0) แต่ **seed กินเท่ากับ A เป๊ะ — ไม่มี avoidance** → กลไกถูกบางอย่างกลบ

### 4.3 Experiment B — sweep starvation floor (แยกสาเหตุ)

วัด seed กินสะสมที่ T≈2000:

| starvation floor | seed กินสะสม (T2000) | ตีความ |
| --- | ---: | --- |
| 6 (default) | ~961 | ≈ A |
| 0 | ~1008 | ≈ A |
| −1,000,000 (ปิด override สนิท) | **355** | **−65%** |

- floor=6 ≈ floor=0 ≈ A แต่ floor=−∞ ต่างมาก → **พลังงาน agent ≤ 0 แทบตลอดเวลา** (ความต่างระหว่าง floor=0 กับ floor=−∞ คือเคสที่พลังงาน ≤ 0) → กฎ "อดตายก็กินทุกอย่าง" เด้งเกือบทุกครั้ง

### 4.4 Experiment B — learning curve (ปิด override) **[ผลชี้ขาด]**

| window | seed กิน | seed_frac | plant กิน | seed_share |
| --- | ---: | ---: | ---: | ---: |
| 0–500 | 125 | 0.045 | 47 | 0.727 |
| 500–1000 | 103 | 0.037 | 30 | 0.774 |
| 1000–2000 | 127 | 0.023 | 241 | 0.345 |
| 2000–3000 | **5** | 0.001 | 515 | 0.010 |
| 3000–6000 | **0** | 0.000 | 3209 | 0.000 |

- **acquisition curve แบบตำรา:** ชิม/กินช่วงแรก → พอเรียนรู้ → **ดิ่งสู่ 0** (เลิกกินเมล็ดสนิทหลัง ~3000 ticks) หันไปกินผลค่าสูงเต็มที่ (plant กิน 47→3209)
- รวม seed ทั้งรัน 360 มื้อ vs A 2155 มื้อ = **ลด 83%** → สนับสนุน H2 ชัดเจน

### 4.5 สภาวะพลังงาน/ความหิว (จาก dump ของ A)
| T | mean_hunger_level | instinct: hunger / balanced |
| --- | ---: | --- |
| 3000 | 0.983 | 43 / 7 |
| 6000 | 0.983 | 49 / 1 |
→ agent อยู่ในภาวะหิว/อดอยากเกือบ 100% สอดคล้องกับหลักฐานพลังงาน ≤ 0 ใน §4.3

---

## 5. อภิปราย (Discussion)

### 5.1 ตอบคำถามวิจัย
1. **out-of-the-box: ไม่เรียนรู้ (ยืนยัน H1)** — การกินเป็น value-blind (ตัดสินแค่ขนาด) ความจำเชิงตำแหน่ง ไม่มี substrate ให้เรียนค่าอาหาร A พิสูจน์เชิงประจักษ์: กินเมล็ดค่าต่ำคงที่ตลอดชีวิต
2. **มีกลไก: เรียนรู้ได้จริง (ยืนยัน H2)** — เกิด avoidance แบบ emergent (curve ดิ่งสู่ 0) เรียนจากพลังงานจริง ไม่ใช่กฎที่เขียนว่า "เมล็ดแย่" จึงไม่ขัดหลักการ "ฟิสิกส์/ประสบการณ์ตัดสิน"
3. **เศรษฐกิจพลังงานกลบการเรียนรู้ (ยืนยัน H3)** — agent ที่พลังงาน ≤ 0 ตลอดย่อมกินทุกอย่างเพราะกำลังอดตาย (เชิงเหตุผลถูกต้องตาม optimal foraging — เมื่อใกล้ตาย ค่า opportunity ของการเลือกกินเป็นศูนย์)

### 5.2 selectivity ที่มีอยู่ ≠ การเรียนรู้
ข้อควรระวังเชิงตีความ: A มี selectivity (กินผลสัดส่วนสูงกว่าเมล็ด 3–7 เท่า) แต่ **ไม่ใช่การเรียนรู้** เพราะ (ก) มีตั้งแต่ window แรกก่อนสะสมประสบการณ์ และ (ข) มาจาก `food_signal` ที่ถ่วงพลังงาน (sensory gradient) — เป็นการ "ได้กลิ่นของดีแต่ไกล" ไม่ใช่ "จำได้ว่าของนี้ไม่คุ้ม" ความแตกต่างนี้สำคัญต่อการไม่ overclaim

### 5.3 ข้อค้นพบที่สำคัญที่สุด: คอขวดร่วมคือพลังงาน
ผลที่ทรงพลังที่สุดไม่ใช่ "กลไกทำงาน" แต่คือ **เศรษฐกิจพลังงาน (ภาวะอดอยากถาวร) เป็นคอขวดร่วม** ของพฤติกรรมระดับสูงทั้งหมด:
- **การเลือกกิน** (รายงานนี้) — ถูกกลบเพราะอดตาย
- **การเลือกที่ดรอปเมล็ด** (Phase 5) — ~97.8% ของการดรอปเกิดตอนหิววิกฤต
- **การสืบพันธุ์** — births=0 (เงื่อนไข `wants_reproduction` ที่ต้องการพลังงานไม่เคยถึง)
- **Phase 6 selection** — ไม่มีรุ่นลูกให้คัดเลือก
ทั้งหมดชี้รากเดียว: agent ไม่มีพลังงานเหลือพอจะทำอะไรนอกจากดิ้นรนเอาตัวรอด → **แก้เศรษฐกิจพลังงานคือกุญแจร่วมที่ปลดล็อกทุกอย่างพร้อมกัน**

---

## 6. ข้อจำกัด (Limitations)

1. **n=1 deterministic** — `args.seed` ไม่กระทบผล (movement RNG แยก) ยังเคลม multi-seed replication ไม่ได้ ตัวเลข reproducible เป๊ะแต่ไม่ใช่ตัวอย่างสุ่ม
2. **raw_seed เป็นอาหารสังเคราะห์เพื่อการทดลอง** — ไม่ใช่เมล็ด `plant_seeds` จริงในระบบ (ซึ่งเข้า gut เป็น byproduct ไม่ใช่อาหารที่เลือกกิน) เป็น proxy ของ "อาหารค่าต่ำที่กินได้"
3. **กลไก B แยกจาก hunger flag โดยตั้งใจ** เพื่อแยกตัวแปร — โมเดลใช้งานจริงต้องผูกกลับเมื่อแก้พลังงานแล้ว
4. **immortal mode** — ไม่มีการตาย ผลภายใต้ mortality อาจต่าง (โดยเฉพาะ trade-off ของการเลี่ยงอาหารแล้วพลังงานตก)
5. learned value เป็น mass-fixed (ไม่สะท้อนความแปรผันของ biomass ผล) ตาม v2 ปัจจุบัน

---

## 7. งานต่อไป (Future Work)

1. **[ลำดับแรก] เจาะเศรษฐกิจพลังงาน** — หาเหตุพลังงาน ≤ 0 ตลอด (passive drain > intake? ต้นทุนการกิน? spawn อาหารน้อยไป?) ให้ agent มีพลังงานเหลือ — ปลดล็อกร่วม (diet/Phase5/repro/Phase6)
2. ผูก `args.seed` เข้า movement RNG → ได้ replication จริง รายงานแบบ multi-seed ได้
3. รัน B ซ้ำหลังแก้พลังงาน (ผูก floor กลับเข้า hunger) → ดูว่าการเลือกกินโผล่เองในโลกจริงไหม
4. ทางเลือก B': ตัดสินใจเลี่ยงเมื่อ "เซนส์เจอผลค่าสูงในระยะมองเห็น" แทนผูกกับพลังงานสัมบูรณ์ (optimal-diet เต็มรูป)
5. ทดสอบภายใต้ mortality + ข้ามรุ่น → เชื่อมกับ Phase 6 (diet เป็น trait ที่ถูกคัดเลือกได้)

---

## 8. กรอบหลักฐาน (ตาม hypothesis-testing skill)

| หลักฐาน | รายละเอียด |
| --- | --- |
| **Supporting** | A: seed กินคงที่ 6000 ticks (H1); B(off): learning curve ดิ่งสู่ 0, ลด 83% (H2); learned value ถูก (seed 1, plant 5); floor sweep พิสูจน์พลังงาน ≤ 0 (H3) |
| **Against / Alternative** | seed_share ที่ลดใน A อาจถูกมองว่าเป็นการเรียนรู้ — แต่ควบคุม availability (seed_frac) แล้วพบว่าไม่ใช่; selectivity ใน A เป็น sensory gradient ไม่ใช่ learning (มีตั้งแต่ window แรก) |
| **Missing** | การรันที่มี reproduction/มี mortality; seed ที่ผูกกับ movement (replication จริง); การวัด per-agent encounter เพื่อยืนยัน consumption-on-contact |
| **Confidence** | กลไกเรียนรู้ทำงาน = **สูง** (curve ชัด + learned value ถูก) · พลังงานเป็น bottleneck = **สูง** (floor sweep) · พร้อมใช้ในโลกจริง = **ต่ำ** (ต้องแก้พลังงานก่อน) · multi-seed generalization = **ต่ำ** (n=1) |

---

## 9. การทำซ้ำ (Reproducibility)

**โค้ด (default-off ทั้งหมด, v1 byte-identical, tests 25/25):**
- `world/metabolism.py` — food kind `raw_seed`
- `world/environment.py` — `low_value_food_spawn_per_tick`, `_spawn_low_value_food`, `food_value_learning_enabled`, `diet_pickiness`, `diet_learning_rate`, `diet_starvation_energy`, counter `food_spawned_by_kind`
- `agents/agent.py` — `food_value_memory`, `_food_worth_eating`, `_learn_food_value`
- `scripts/run_long_emergence_watch.py` — `diet_by_kind`, `learned_food_value`, wiring
- driver: `.codex-temp/gate_run.py`

**คำสั่งหลัก:**
```
# A (value-blind baseline)
python .codex-temp/gate_run.py --model v2 --ticks 6000 --low-value-food 6 --dump A.json
# B (กลไกเปิด, floor ปกติ — ถูกพลังงานกลบ)
python .codex-temp/gate_run.py --model v2 --ticks 6000 --low-value-food 6 --value-learning --dump B.json
# B (ปิด override — learning curve ชี้ขาด)
python .codex-temp/gate_run.py --model v2 --ticks 6000 --low-value-food 6 --value-learning --starvation-energy -1000000 --dump Bcurve.json
```

**commit:** `6add9c1` (A), `d627bd4` (B), `45b1d82` (รายงาน)

---

## ภาคผนวก: อ้างอิงโค้ดสำคัญ
- ด่านกินขนาดอย่างเดียว: `agents/agent.py` `_fits_mouth` / `_consume_current_food` (เรียกทุก tick ที่ `:174`)
- กลไกเรียนรู้ B: `agents/agent.py` `_food_worth_eating`, `_learn_food_value`
- พลังงานองค์ประกอบ: `world/metabolism.py` `digestible_energy`, `COMPOSITION`
- spawn อาหารค่าต่ำ: `world/environment.py` `_spawn_low_value_food`
- movement RNG แยก seed: `agents/agent.py:909,938`

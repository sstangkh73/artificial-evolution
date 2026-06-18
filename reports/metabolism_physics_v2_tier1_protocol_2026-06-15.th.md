# Protocol: Metabolism v2 — Tier 1 (make v2 research-grade)

วันที่เขียน: 2026-06-15
สถานะ: pre-implementation (เปิดมาทำได้เลย)
อ้างอิง: `reports/metabolism_physics_v2_session_report_2026-06-15.th.md` (ผล adversarial panel ที่เป็นที่มาของ 3 fix นี้)
เป้าหมายรวม: ทำให้ v2 เทียบกับ v1 ได้อย่างซื่อสัตย์และวัดผลได้จริง ก่อนจะไป Phase 6 (selection)

> commit ฐาน ณ ตอนเขียน: `c9419a1` (v2 roadmap ครบ แต่มี 3 known limitations)

---

## ภาพรวม

Tier 1 = 3 fix จาก adversarial panel เรียงตามลำดับ dependency:

| fix | ปัญหา (จาก panel) | ปลดล็อก |
| --- | --- | --- |
| 1. Fixed-tick gate | "v1==v2 เท่ากัน" เป็น wall-clock artifact | baseline v1-vs-v2 ที่ซื่อสัตย์ |
| 2. Runner parse `gut_seed_*` | endozoochory ถูกนับเข้า control group | วัด chain completion ของ gut seed |
| 3. Heritability + `gut_capacity` | ยีน digestion ค้าง default + capacity no-op | diet trade-off แปรผันได้ → Phase 6 |

ทำตามลำดับ 1 → 2 → 3 (fix 3 เป็น prerequisite ของ Phase 6)

---

## Fix 1 — Fixed-tick gate (v1 vs v2 ที่ยุติธรรม)

### ปัญหา
panel พบว่า v2 ช้ากว่า v1 ต่อ tick → รัน wall-clock 60s เท่ากันได้จำนวน tick ต่างกัน บังเอิญตรงที่ช่วง activity ต่ำ จึงดู "เท่ากัน" จริงๆ ต่างกันทุก metric เมื่อเทียบ fixed-tick

### Method
รัน `scripts/run_long_emergence_watch.py` ด้วย tuned Phase-1 config (body 37) **แต่ล็อก tick ไม่ใช่เวลา**:
```
--max-ticks 3000 --time-limit-seconds 999999
```
รัน 2 model × 3 seeds (20260610, 20260611, 20260612), เทียบที่ tick 3000 เท่ากัน

### Experiment design
- **IV:** `metabolism_model` (v1 / v2)
- **DV:** seed_germinated, plant_matured, plant_fruited, plant_lifecycle_food_consumed, mean_hunger_level, gut_seed_ingested/excreted, mean energy
- **Control:** seed/world/config เดียวกัน, tick budget เท่ากัน (3000)
- **Metric:** เทียบ DV ต่อ model ที่ tick เท่ากัน + ตรวจว่า v2 ยังเกิดวงจร seed→plant→fruit→consumed
- **Success (gate ผ่าน):** v2 ยังมี `plant_fruited > 0` และ `plant_lifecycle_food_consumed > 0` ทั้ง 3 seeds (ecology ไม่พังใต้ energy ใหม่)
- **Failure:** v2 ไม่มี fruiting/consumption → energy model ต่ำเกิน ต้อง **re-tune `ENERGY_DENSITY`** ใน `world/metabolism.py` (ปัจจุบัน plant baseline ~4.76 vs v1 6 → ลองยก sugar/protein density จน plant ≈ 6)

### หมายเหตุ
v1 และ v2 **คาดว่าจะต่างกัน** ที่ fixed-tick — นั่นคือผลที่ถูกต้อง ไม่ใช่ bug ห้ามรายงาน "เท่ากัน" อีก

---

## Fix 2 — Runner parse `gut_seed_*` (attribute endozoochory ให้ agent)

### ปัญหา
`consume_food` emit `harvest_seed_dropped` ก่อนเมล็ดเข้า gut แล้ว `gut_seed_ingested`/`gut_seed_excreted`/`gut_seed_killed` **ไม่ถูก parse เลย** → seed_record มี `agent_moved=False`, ถูกนับเข้า control group (ตรงข้ามความหมาย) + ใช้ตำแหน่งจุดกินเก่าเป็น origin

### จุดแก้ (file:line จาก panel)
- `scripts/run_long_emergence_watch.py:27-44` — `SAMPLED_EVENT_KINDS` ไม่มี gut events → เพิ่ม `gut_seed_ingested`, `gut_seed_excreted`, `gut_seed_killed`
- event parsing loop — เพิ่ม branch parse 3 event นี้
- `:2032-2034` — origin_x/y ถูก set จาก `harvest_seed_dropped` (จุดกิน) → ต้องอัปเดตเป็นจุดขับเมื่อเจอ `gut_seed_excreted`
- `:883-887` (phase3 control), `:988-994` (phase4 control), `:1316-1324` (phase5 exclude) — record ที่ผ่าน gut ต้องถูกจัดเป็น agent_moved

### ทางเลือกการแก้ (เลือก 1)
- **(a) attribute ให้ agent:** parse `gut_seed_excreted` → set `agent_moved=True`, `moved_by_agent=agent_id`, `last_drop_x/y = excretion coords` → endozoochory นับเป็น agent dispersal (ตรงความหมายชีวภาพ) **[แนะนำ]**
- **(b) แยกหมวด:** tag `source_kind="gut_transit"` แล้วกันออกจากทั้ง agent_moved และ harvest control → ไม่ปนทั้งสองฝั่ง

### Verify
หลังรัน v2: `agent_moved_seed_count > 0` รวม gut seed; site position = จุดขับ ไม่ใช่จุดกิน; เทียบ phase3 completed-chain ของ gut-dispersed seed กับ control ได้

### Success / Failure
- **Success:** gut seed ถูกนับเป็น agent_moved; วัด chain completion (seed→plant→fruit→กิน) ของเมล็ดที่ผ่าน gut ได้
- **Failure:** ยังนับเข้า control / ตำแหน่งยังเป็นจุดกิน → parsing ยังผิด

> เพิ่ม metadata `metabolism_model` ลง output JSON ของทุก run ด้วย เพื่อกันเอา v1/v2 มาเทียบปนกันโดยไม่รู้ตัว

---

## Fix 3 — Heritability + `gut_capacity` (ปลดล็อก diet trade-off)

### ปัญหา
ยีน digestion 6 ตัวไม่อยู่ใน `TRAIT_FIELDS` → ไม่ถูก thread ผ่าน `inherit_body_plan` → ค้าง default ตลอด (acid 0.4, shell 0.6 ทุกตัว → 0 killed เสมอ). และ `gut_capacity` ไม่ถูกบังคับ

### จุดแก้ (file:line จาก panel)
- `agents/body.py:77-91` `TRAIT_FIELDS`, `:100` `TRAIT_BOUNDS`, `:116` `TRAIT_MUTATION_STEPS` — เพิ่ม `gape`, `gut_capacity`, `gut_transit_ticks`, `acid_strength`, `cellulose_efficiency`, `toxin_tolerance` พร้อม bounds + mutation step ที่สมเหตุผล (เช่น acid_strength ∈ [0.1, 0.9], shell ของ wild_grain = 0.6 → ให้ acid คร่อม 0.6 ได้ จะได้เกิดทั้ง disperser และ predator)
- `agents/body.py:443-455` `inherit_body_plan` — thread การ draw ยีนใหม่

### ⚠️ ข้อควรระวังสำคัญ (RNG stream)
การเพิ่มยีนเข้า `TRAIT_FIELDS` จะ **เปลี่ยนลำดับการ draw RNG** → ทำลาย reproducibility ของ Phase 1-5 (panel ยืนยันว่าตอนนี้ยีนใหม่ "ไม่อยู่ใน TRAIT_FIELDS" จึงรักษา stream ไว้ได้)

**วิธีแก้ที่รักษา v1 ได้:** ให้การ draw ยีนใหม่ **ต่อท้ายหลัง draw ของยีนเดิมทั้งหมด** ใน `inherit_body_plan` → prefix ของ stream เดิมไม่เปลี่ยน → Phase 1-5 (v1) ยัง byte-identical, ยีนใหม่ได้ค่าจาก draw ที่ tail. ทดสอบ: รัน Phase 1 v1 seed เดิม เทียบผลก่อน/หลัง ต้องเท่ากันเป๊ะ

- `world/environment.py:2017-2031` `_route_seed_to_gut` — เพิ่ม `if len(eater.gut_seeds) >= int(eater.body.gut_capacity): return` (ไม่ route ถ้าเต็มท้อง)

### Verify / Success
- offspring มี gape/acid_strength/ฯลฯ แปรผัน (ไม่ใช่ default หมด)
- บาง lineage acid > shell → เริ่มมี `gut_seed_killed > 0`
- gut seed ต่อ agent ไม่เกิน gut_capacity
- **regression gate:** Phase 1 v1 seed เดิม ผล byte-identical ก่อน/หลัง fix 3

### Failure
- Phase 1 v1 ผลเปลี่ยน → RNG stream พัง (ไม่ได้ต่อท้าย) ต้องแก้
- ยีนยังค้าง default → threading ไม่สำเร็จ

---

## ลำดับและ gate

```
Fix 1 (fixed-tick gate)  → ได้ baseline ซื่อสัตย์ + ยืนยัน ecology ไม่พัง
   ↓
Fix 2 (parse gut events) → วัด endozoochory chain completion ได้
   ↓
Fix 3 (heritability)     → diet trade-off แปรผันได้  [regression: v1 ต้อง identical]
   ↓
=> พร้อมเข้า Phase 6 (ดูล่าง)
```

---

## หลัง Tier 1: Phase 6 (selection — ผลตอบแทนจริง)

เมื่อ Tier 1 ครบ + ปิด `immortal`:

**คำถาม:** lineage ที่ `acid < shell` (seed disperser) กับ `acid > shell` (seed predator) ถูกคัดเลือกต่างกันตาม ecology ไหม? seed-handling สืบทอดข้ามรุ่นโดยไม่ถูกสอนไหม?

**Metrics:** survival time, reproduction count, lineage persistence, trait shift (acid_strength เฉลี่ยข้ามรุ่น), completed-chain rate ต่อ lineage

**Success:** lineage ที่มีพฤติกรรม seed/gut ที่เหมาะกับ ecology อยู่รอด/สืบพันธุ์ดีกว่า control และ trait เลื่อนข้ามรุ่นโดยไม่มีคำสั่ง → **emergent evolution of seed dispersal** (centerpiece)

**Falsification:** trait ไม่เลื่อนแม้มี selection → toxicity/dispersal ไม่สร้างแรงกดดันจริง; หรือ disperser/predator อยู่รอดเท่ากัน → trade-off ไม่มีผล

---

## Risks
- Fix 2 แตะ runner 2900+ บรรทัด — แก้เฉพาะจุด parse, อย่าไปกระทบ logic phase อื่น; รัน v1 ก่อน/หลังเทียบว่าไม่เปลี่ยน
- Fix 3 RNG stream — ถ้าไม่ต่อท้าย จะพัง Phase 1-5 reproducibility (ดู gate ข้างบน)
- re-tune ENERGY_DENSITY (ถ้า Fix 1 fail) จะกระทบ unit test `test_raw_plant_energy_matches_hand_calc` (4.755) — อัปเดต expected ด้วย

## ตาม skill
ทุก fix รายงานแบบ: Evidence Supporting / Against / Alternative / Missing / Confidence; commit แยกต่อ fix พร้อม regression note

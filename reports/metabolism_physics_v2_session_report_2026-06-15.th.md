# Session Report: Metabolism Physics v2 (v2.0 → v2.3) + Adversarial Verification

วันที่: 2026-06-15
พื้นที่ทดลอง: `C:\artificial-evolution`
อ้างอิง: `reports/metabolism_physics_v2_design_2026-06-15.th.md` (design), `reports/metabolism_physics_v2_0_protocol_2026-06-15.th.md` (protocol v2.0)
สถานะ: v2.0/v2.1(energy) committed · v2.1(gape)/v2.2/v2.3 **ยังไม่ commit** (รอแก้ issue จาก adversarial panel)

---

## Abstract

รายงานนี้สรุปการ implement ระบบ Metabolism Physics v2 ทั้ง roadmap (§10 ของ design doc) — เปลี่ยนการกินจาก categorical+scripted เป็น physics-based (ขนาดปาก + องค์ประกอบ × เอนไซม์ + gut transit + พิษ) — พร้อมการทดลองและการตรวจสอบเชิงปฏิปักษ์ (adversarial verification) ด้วย panel 5 ตัว

ผลหลัก: **กลไก endozoochory ทำงานจริงและผ่านการ verify อิสระ** (เมล็ดกระจายผ่านระบบย่อยเฉลี่ย 4.59 ช่อง, 80.4% ที่ระยะ > 0) และ **v1 reproducibility ไม่เสีย** แต่ panel จับ issue สำคัญ 3 จุด: (1) การเทียบ gate แบบ wall-clock ทำให้ "v1==v2 เท่ากัน" เป็น artifact, (2) v2 endozoochory ถูกจัดหมวดผิดใน runner metrics, (3) ยีน `gut_capacity` เป็น no-op และยีนใหม่ยังไม่ถูก thread ผ่าน inheritance ทั้งหมดนี้ถูกจับ **ก่อน commit**

---

## 1. Roadmap และสิ่งที่สร้าง

| stage | เนื้อหา | สถานะ |
| --- | --- | --- |
| v2.0 | `world/metabolism.py` (COMPOSITION/ENERGY_DENSITY/FOOD_SIZE/FOOD_MASS + `digestible_energy`/`can_ingest`); 6 ยีนใน `BodyPlan` (`gape`, `gut_capacity`, `gut_transit_ticks`, `acid_strength`, `cellulose_efficiency`, `toxin_tolerance`) + `enzyme_profile`; unit test ตัวแรกของ repo | committed `68f0a7f` |
| v2.1 (energy) | `_metabolic_base_energy` wire `digestible_energy` หลัง flag; `--metabolism-model {v1,v2}` | committed `a38906c` |
| v2.1 (gape gate) | `_fits_mouth` — กินได้เฉพาะ object ที่ size ≤ gape | uncommitted |
| v2.2 | `_route_seed_to_gut` + `excrete_gut_seed` + `_process_gut` + `PlantSpeciesSpec.shell_hardness` (=0.6) → endozoochory; ถอด `seed_hunger_drop_bonus` (gate เหลือ v1) | uncommitted |
| v2.3 | `toxin_load`/`toxin_penalty` (pure scaffold, ยังไม่ wire) | uncommitted |
| tests | 20/20 ผ่าน (`tests/test_metabolism.py`) | uncommitted |

หลักการที่ยึด: ไม่สอน semantics, ฟิสิกส์ตัดสิน, v2 เป็น opt-in (`metabolism_model` default `"v1"`)

---

## 2. Methods

### 2.1 Phase-1-v2 gate
รัน `scripts/run_long_emergence_watch.py` ด้วย tuned Phase-1 config (`--body-index 37 --width 100 --height 100 --max-food 2000 --max-plant-seeds 7600 --base-food-spawn-per-tick 4 --food-spawn-multiplier 0.70 --bootstrap-food-spawn-ticks 300` + multipliers + `--plant-food-decay-chance 0.0015`) เทียบ `--metabolism-model v1` vs `v2`, time-limit 60s, seed 20260610

**ข้อบกพร่องเชิงวิธี (พบภายหลังโดย panel):** เทียบแบบ wall-clock (60s) ไม่ใช่ fixed-tick ดูข้อ 4 (claim 4)

### 2.2 Endozoochory dispersal measurement
`.codex-temp/measure_endo.py` — monkeypatch `Environment.excrete_gut_seed`: ก่อนเรียก original อ่าน `(plant.x, plant.y)` = ตำแหน่งกิน (เพราะ gut seed ไม่ถูกย้ายจนกว่าจะขับ), args `(x,y)` = ตำแหน่งขับ → Manhattan distance = ระยะกระจาย แล้วเรียก `run_watch` ในโปรเซส

---

## 3. Results

### 3.1 Phase-1-v2 gate (เทียบ wall-clock 60s — ตีความด้วยความระวัง)

| metric | v1 | v2 |
| --- | ---: | ---: |
| seed_germinated | 41 | 41 |
| plant_matured | 11 | 11 |
| plant_fruited | 14 | 14 |
| plant_lifecycle_food_consumed | 7 | 7 |
| mean_hunger_level | 0.983 | 0.983 |
| พลังงาน agent ตอน event | 5.25 (max 8) | 4.0 |

ตัวเลข ecology เท่ากัน → **ภายหลังพิสูจน์ว่าเป็น artifact** (claim 4)

### 3.2 Endozoochory (v2, 2194–2198 ticks)

| metric | ค่า |
| --- | ---: |
| excretions | 214 |
| survived / killed | 214 / 0 |
| dispersal distance mean | 4.59 |
| median | 4.0 |
| max | 12 |
| fraction > 0 | 0.804 |

`gut_seed_ingested = gut_seed_excreted = 74` (ในรัน gate 800-tick) — กลไกยิงจริง ทุกเมล็ดรอด (acid 0.4 < shell 0.6)

---

## 4. Adversarial Verification (panel 5 skeptics, อ่านโค้ดจริง)

| # | claim | verdict | confidence |
| --- | --- | --- | --- |
| 1 | endozoochory เป็น dispersal จริง ไม่ใช่ artifact | **ไม่ refuted (ยืนยัน)** | high |
| 2 | v1 reproducibility เดิมไม่เสีย | **ไม่ refuted (ยืนยัน)** | high |
| 3 | gut code ไม่มี bug | **REFUTED** | high |
| 4 | "v1==v2 ecology เท่ากัน" ถูกต้อง | **REFUTED** | high |
| 5 | phase3/4/5 metrics ไม่เสีย | **REFUTED** | high |

### Claim 1 — CONFIRMED
panel รัน `measure_endo.py` ซ้ำได้เลขเป๊ะ (mean 4.59, median 4, 80.4%>0) ยืนยันว่า:
- gut seed `(plant.x, plant.y)` = จุดกิน และไม่ถูกแก้ระหว่างอยู่ใน gut (lifecycle ข้าม carried seed ที่ `environment.py:2081-2085` ก่อนอ่าน/เขียน x/y)
- excrete อ่านจุดกินก่อน overwrite เป็นจุดขับ; วัดก่อนเรียก original → ระยะถูกต้อง
- ขับครั้งเดียวต่อเมล็ด (no double-count), same-tick excretion เป็นไปไม่ได้ (transit=6)
- **caveat (ไม่ refute):** dispersal เป็น byproduct ของการเดิน ไม่ได้ถูก select มาเพื่อกระจาย; acid 0.4 < shell 0.6 → 0 killed = survival ถูกล็อกด้วยยีน

### Claim 2 — CONFIRMED
ทุก v2 branch gate ถูก: `_metabolic_base_energy` (agent.py:1275), `_fits_mouth` (:800), `_process_gut` (:785), `seed_hunger_drop_bonus` (:831, คงไว้เมื่อ !=v2), gut routing (environment.py:725, ==v2 เท่านั้น)
- `consume_food(eater=None)` backward-compatible; legacy caller (env:969) ไม่ส่ง eater
- **สำคัญ:** ยีนใหม่ 6 ตัวไม่อยู่ใน `TRAIT_FIELDS`/`TRAIT_BOUNDS`/`TRAIT_MUTATION_STEPS` → `inherit_body_plan` ดึง RNG sequence เดิมเป๊ะ → seeded reproducibility ของ Phase 1-5 ไม่เสีย
- **bonus finding:** เพราะเหตุผลเดียวกัน ยีนใหม่ **ไม่เคยถูก thread ผ่าน inheritance** → แม้ใน v2 ก็ค้างที่ default = "heritable" ยังเป็นแค่ความตั้งใจ ยังไม่ wire จริง

### Claim 3 — REFUTED
- 🟠 **[major] `gut_capacity` เป็น no-op** — doc บอก "ใช้ v2.2" แต่ `_route_seed_to_gut` (environment.py:2017-2031) append โดยไม่เช็ค capacity เลย (จำกัดทางอ้อมแค่ `max_plant_seeds`=450 รวม)
- 🟡 **[minor]** orphaned gut seed ตอน agent ตาย (`_resolve_life_state` ไม่ cleanup `gut_seeds`/ไม่ปล่อย `carried_by_agent_id`) — ถือ plant_seeds slot และงอกไม่ได้จนกว่า decay reap (~900 ticks, ไม่ leak ถาวร)
- 🟡 **[minor]** `excrete_gut_seed` early-return ตอน non-walkable ไม่ clear carried flag หลัง pop จาก gut_seeds (dead path — agent อยู่ cell walkable เสมอ)
- ✅ ที่ถูกต้อง: ไม่ double-route/excrete, killed seed ถูก reap รอบถัดไป, carried seed ไม่ถูกนับใน census state counts, `_process_gut` รันทั้ง balanced/non-balanced branch

### Claim 4 — REFUTED (สำคัญต่อความซื่อสัตย์)
- 🔴 **[major] "v1==v2 ecology เท่ากัน" เป็น artifact ของ wall-clock comparison** — v2 ช้ากว่าต่อ tick → 60s เท่ากันได้จำนวน tick ต่างกัน บังเอิญตรงที่ช่วง activity ต่ำ
- panel เทียบ **fixed-tick** (800 & 2400 ticks, seed/world เดียวกัน) → v1/v2 **ต่างทุก active metric**: seed_germinated 0 vs 2, food_consumed 22 vs 15, seed_picked 8 vs 0, harvest_seed_dropped 19 vs 14, gut 0 vs 14; energy แตกที่ tick 3, position แตกที่ tick 2
- v2 **ไม่ inert** — ทำงานจริง (energy 5 vs 6, gut 14 events) เพียงแต่ผลต่างจาก v1 อย่างที่ควรเป็น
- 0.983 hunger ที่ "เท่ากัน" = เพดานอิ่มตัวของ immortal-starvation (energy ~1) ไม่ใช่สัญญาณ equivalence — ใช้เป็น sanity check ไม่ได้
- **คำแก้:** gate ต้องเทียบ fixed-tick; คาดว่า ecology จะต่าง (และนั่นถูกต้อง)

### Claim 5 — REFUTED
- 🔴 **[major] v2 endozoochory ถูกจัดหมวดผิด** — `consume_food` emit `harvest_seed_dropped` ก่อนเมล็ดเข้า gut แล้ว `gut_seed_*` events **runner ไม่ parse** (ไม่อยู่ใน `SAMPLED_EVENT_KINDS`) → record มี `agent_moved=False`, ถูกนับเข้า **control group (agent-independent)** ที่ run_long_emergence_watch.py:883-887 / phase4 control 988-994 / phase5 ตัดทิ้ง 1316-1324 = ตรงข้ามความหมายชีวภาพ
- 🔴 **[major]** ใช้ตำแหน่งจุดกินเก่า (ingestion) เป็น origin ของ site-signature control แทนจุดงอกจริง (excretion)
- 🔵 **[minor/safe]** ข้อมูลเก่าไม่เสีย — ทุก probe resolve เป็น v1 (CLI default + `_watch_args` ไม่มี key) แต่ **ถ้าเอา v2 ไปรายงานผ่าน metrics เหล่านี้จะ invalid**

---

## 5. Honest Assessment

**ที่แข็งจริง (verified):**
- endozoochory ทำงานและถูก verify อิสระ — เมล็ดกระจายเองจาก gut transit แทน `seed_hunger_drop_bonus` ที่เขียนมือ (ตรง thesis "ให้ฟิสิกส์ตัดสิน")
- v1 reproducibility ไม่เสีย — งาน Phase 1-5 ปลอดภัย
- 20/20 unit tests ผ่าน
- panel จับ issue **ก่อน commit** — ไม่มีของเสียลง git

**ที่ยังไม่ถึง research-grade:**
1. gate ต้องเทียบ fixed-tick ไม่ใช่ wall-clock
2. runner ต้อง parse `gut_seed_*` ไม่งั้นเทียบ v1-vs-v2 ผ่าน phase metrics ไม่ได้
3. `gut_capacity` ต้องบังคับ + ยีนใหม่ต้อง thread ผ่าน inheritance
4. cleanup gut seed ตอนตาย (เมื่อถึง Phase 6)

---

## 6. Limitations / ข้อควรเขียนในรายงานวิจัย
- dispersal เป็น **byproduct ของการเดิน** ไม่ใช่พฤติกรรมที่ถูก select มาเพื่อกระจายเมล็ด
- body 37 มี acid 0.4 < shell 0.6 ทุกตัว → 0 killed = survival ถูกล็อกด้วยยีน ไม่ใช่ความบังเอิญ
- ยีน digestion ยังค้าง default (ยังไม่ heritable จริง) → diet trade-off / Phase 6 selection ยังทดสอบไม่ได้จนกว่าจะ wire inheritance

---

## 7. Git State
- committed: `68f0a7f` (v2.0), `ea5083d` (phase4/5 code), `a38906c` (v2.1 energy)
- uncommitted (working tree): v2.1 gape gate, v2.2 endozoochory + remove hunger bias, v2.3 toxin scaffold, tests, `world/environment.py` (shell_hardness + gut methods)
- ยังไม่ commit จนกว่าจะแก้ 3 issue major หรือ commit พร้อม document limitation ชัดเจน

---

## 8. Next Steps (เรียงตามผลกระทบ)
1. **แก้ gate methodology** → fixed-tick (`--max-ticks N` + time-limit สูง) เทียบ v1/v2 หลาย seed → รายงานว่าต่างกัน (ถูกต้อง)
2. **runner parse `gut_seed_excreted`** → set `agent_moved=True` + ตำแหน่งจุดขับ (หรือ tag `source_kind` ใหม่กันปน control)
3. **บังคับ `gut_capacity`** ใน `_route_seed_to_gut` + thread ยีน 6 ตัวผ่าน `inherit_body_plan`
4. cleanup orphaned gut seed ตอนตาย (Phase 6)
5. commit v2.1-gape + v2.2 + v2.3 พร้อม note limitation

---

## Evidence Supporting / Against / Confidence (ตาม hypothesis-testing skill)

**Supporting:** endozoochory verified อิสระ (panel รันซ้ำได้เลขเป๊ะ); v1 gate ทุก branch; 20/20 tests; ยีนใหม่ไม่กวน RNG stream

**Against / Alternative:** "v1==v2 เท่ากัน" เป็น wall-clock artifact (fixed-tick ต่างกัน); dispersal เป็น byproduct ไม่ใช่ adaptive; metrics miscategorization ทำให้ v2 เทียบ v1 ไม่ได้จนกว่าจะแก้ runner; ยีนยังไม่ heritable จริง

**Confidence:**
| claim | confidence |
| --- | --- |
| endozoochory dispersal เกิดจริง | สูง |
| v1 reproducibility ไม่เสีย | สูง |
| v2 ทำงาน (ไม่ inert) | สูง |
| v2 พร้อมใช้ในงานวิจัยเทียบ v1 | **ต่ำ** (ต้องแก้ runner metrics + fixed-tick gate ก่อน) |
| dispersal เป็น adaptive behavior | ต่ำมาก (เป็น byproduct) |

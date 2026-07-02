# รายงานการพัฒนา: Aging Physics v1 — โมดูลอายุขัยที่อิงฟิสิกส์/ชีววิทยาที่พิสูจน์แล้ว

**Implementing a biologically-grounded aging module so intrinsic death EMERGES from accumulated damage — validated against the proven longevity literature**

ผู้จัดทำ: Chisanupong · โครงการ Artificial Evolution (ALife → YSC/ISEF)
วันที่: 2026-07-01
สถานะ: **implemented + tested + validated** (opt-in, byte-identical เมื่อปิด)
ต่อจาก: `reports/physics_realism_audit_aging_2026-07-01.th.md` (audit 11 ช่องว่าง) · `papers/longevity/human_lifespan_determinants_review.md`

> **ความซื่อสัตย์ทางวิทยาศาสตร์ (อ่านก่อน):** โมดูลนี้ไม่ได้จำลอง "ฟิสิกส์ระดับโมเลกุลของความแก่จริงทุกอะตอม" — สิ่งนั้นเป็นไปไม่ได้ในซิมระดับ agent สิ่งที่ทำคือแปลง **หลักการเชิงกลไกที่งานวิจัยพิสูจน์แล้ว** (Disposable Soma, rate-of-living, allometric scaling, caloric restriction) เป็น **สมการนามธรรมที่ซื่อตรงต่อหลักการ** แล้วพิสูจน์ว่าผลลัพธ์ที่เปเปอร์รายงาน **emerge ออกมาเอง** จากสมการเหล่านั้น จุดแข็งของงานคือความตรงนี้ ไม่ใช่การอ้างเกินจริง

---

## สารบัญ
1. [สิ่งที่เปลี่ยนไป (ก่อน→หลัง)](#1-สิ่งที่เปลี่ยนไป-ก่อนหลัง)
2. [สมการหลัก + การแมปกับเปเปอร์](#2-สมการหลัก--การแมปกับเปเปอร์)
3. [ยีนอายุ (aging genome) + การถ่ายทอด](#3-ยีนอายุ-aging-genome--การถ่ายทอด)
4. [ไฟล์ที่แก้ + knob ทั้งหมด](#4-ไฟล์ที่แก้--knob-ทั้งหมด)
5. [ผลการ validate เทียบเปเปอร์](#5-ผลการ-validate-เทียบเปเปอร์)
6. [การรักษา reproducibility (byte-identical)](#6-การรักษา-reproducibility-byte-identical)
7. [วิธีรัน](#7-วิธีรัน)
8. [ช่องว่างที่ปิดแล้ว vs ที่เหลือ](#8-ช่องว่างที่ปิดแล้ว-vs-ที่เหลือ)
9. [ข้อจำกัด + งานต่อ](#9-ข้อจำกัด--งานต่อ)

---

## 1. สิ่งที่เปลี่ยนไป (ก่อน→หลัง)

| | ก่อน (audit) | หลัง (Aging Physics v1) |
|---|---|---|
| การตายภายใน | นาฬิกาจับเวลา `age >= MAX_AGE=200` | **`damage ≥ threshold` → "senescence"** (emerge) |
| ความเสียหายสะสม | ไม่มี | `damage: float` สะสมทุก tick |
| การซ่อมแซม (maintenance) | ไม่มี | ยีน `somatic_maintenance` จ่ายพลังงานลด damage (Disposable Soma) |
| มวลกาย | ไม่มี | ยีน `body_mass` + allometric scaling |
| เมตาบอลิซึม→ความแก่ | ไม่เชื่อม | damage ∝ mass-specific metabolic rate |
| อายุขัยถ่ายทอดได้ | ไม่ (ค่าคงที่) | ยีนอายุ 4 ตัว inherit + mutate ได้ |
| CR ยืดอายุ | ทำไม่ได้ | emerge ผ่าน intake-damage term |

**หลักการออกแบบ:** ทุกอย่าง **opt-in** (`aging_physics_enabled=False` เป็นค่าเริ่มต้น) → เมื่อปิด ซิมทำงานเหมือนเดิมทุกประการ (พิสูจน์ byte-identical ในข้อ 6) เคารพวินัย reproducibility ที่โครงการยึดมาตลอด (แบบเดียวกับ Metabolism v2)

---

## 2. สมการหลัก + การแมปกับเปเปอร์

ทุก tick (เมื่อเปิด aging และไม่ immortal) เมธอด `Agent._apply_aging` ทำ:

```
# 1) ความเสียหายจากเมตาบอลิซึม (rate-of-living / mitochondrial ROS)
mass_specific_metab = metabolism_rate * body_mass^(-aging_mass_exponent)   # Kleiber
gross = aging_damage_rate * mass_specific_metab / damage_resistance
        + aging_intake_damage_coeff * energy_absorbed_this_tick            # CR lever

# 2) การซ่อมแซม (Disposable Soma) — ซ่อมได้ไม่เกินเพดาน จึงแก่แน่นอน
repair = min(aging_max_repair_fraction * gross,
             somatic_maintenance * repair_efficiency * aging_repair_gain)

# 3) สะสม (net > 0 เสมอ → ความแก่หลีกเลี่ยงไม่ได้)
damage += gross - repair

# 4) ราคาของ Disposable Soma (จ่ายใน tick(): maintenance กินพลังงานที่ควรไปสืบพันธุ์)
energy -= somatic_maintenance * aging_maintenance_cost

# 5) การตายที่ emerge เอง
if damage >= aging_damage_threshold:  ตาย "senescence"
```

| องค์ประกอบสมการ | เปเปอร์ที่รองรับ | หลักการ |
|---|---|---|
| `damage += gross - repair`, ตายเมื่อ ≥ threshold | López-Otín 2013/2023 (Hallmarks) | ความแก่ = การสะสมความเสียหาย |
| `repair` แลกด้วยพลังงาน (ข้อ 4) | **Kirkwood 1977** (Disposable Soma) | พลังงานซ่อม = พลังงานที่ไม่ได้สืบพันธุ์ |
| `mass^(-exponent)` | **Speakman 2005** (Kleiber) | ตัวใหญ่เผาผลาญต่อมวลช้า → อายุยืน |
| `/ damage_resistance` แยกจาก metabolism_rate | **Hulbert 2007, Kitazoe 2017** | "อัตราสะสมความเสียหาย ≠ อัตราเผาผลาญ" (บทเรียนนก) |
| `intake_damage_coeff * absorbed` | **Ravussin 2015, Waziry 2023** (CALERIE) | กินน้อย → ความเสียหายน้อย → อายุยืน |
| `max_repair_fraction < 1` | López-Otín | ไม่มีสิ่งมีชีวิตซ่อมสมบูรณ์ → mortality การันตี |

---

## 3. ยีนอายุ (aging genome) + การถ่ายทอด

เพิ่ม 4 ยีนใน `BodyPlan` (`agents/body.py`, `AGING_TRAIT_FIELDS`) ถ่ายทอด+กลายพันธุ์ได้เหมือนยีนอื่น:

| ยีน | ช่วง | ค่าเริ่มต้น | ความหมายชีววิทยา |
|---|---|---|---|
| `body_mass` | 0.5–4.0 | 1.0 | ขนาดกาย (allometry; Speakman) |
| `somatic_maintenance` | 0.0–1.0 | 0.3 | สัดส่วนพลังงานที่ทุ่มซ่อม (Disposable Soma; **ยีน trade-off หลัก**) |
| `repair_efficiency` | 0.0–1.0 | 0.5 | ประสิทธิภาพการซ่อมต่อพลังงาน |
| `damage_resistance` | 0.5–2.0 | 1.0 | คุณภาพเยื่อ/ไมโทคอนเดรีย (Hulbert/Kitazoe) |

**เพราะเป็นยีน → วัด heritability ของ lifespan ในซิมได้จริง** (ปิดช่องว่าง G2; ตรงกับ Herskind 1996 / Science 2025) และวิวัฒนาการเลือกสัดส่วน maintenance ตาม extrinsic mortality ได้ (สมมติฐาน Kirkwood ที่ทดสอบได้)

**การถ่ายทอดแบบไม่ทำลาย reproducibility:** ยีนอายุถูก draw ที่ **ท้ายสุด** ของ `inherit_body_plan` หลังยีน metabolism gated ด้วย `draw_aging_genes` (เปิดเฉพาะเมื่อ aging เปิด) → เมื่อปิดใช้ RNG **ศูนย์ draw** สตรีม Phase 1–5 และ metabolism-v2 จึง byte-identical (แบบเดียวกับ Fix 3 ของ metabolism v2)

---

## 4. ไฟล์ที่แก้ + knob ทั้งหมด

| ไฟล์ | การเปลี่ยนแปลง |
|---|---|
| `agents/body.py` | `AGING_TRAIT_FIELDS` + 4 ยีน (fields/bounds/steps), property `aging_values`/`mass_specific_metabolic_rate`, tail-draw ใน `inherit_body_plan(draw_aging_genes=...)` |
| `agents/agent.py` | state `damage`/`drain_maintenance_total` + accumulators; charge maintenance ใน `tick()`; เมธอด `_apply_aging`; สาขา aging ในลอจิกการตาย; `draw_aging_genes` ใน `spawn_child` |
| `world/environment.py` | 8 env knobs (ดูล่าง) |
| `simulation/runner.py` | telemetry ต่อ agent: `damage`, `body_mass`, ยีนอายุ, `maintenance_energy_total` |
| `scripts/run_long_emergence_watch.py` | forward 8 knob จาก args → `Environment(...)` |
| `scripts/food_value_study_driver.py` | argparse `--aging` + 7 knob + wiring |
| `scripts/run_aging_validation.py` | **ใหม่** — การทดลองควบคุม 4 arm เทียบเปเปอร์ |
| `tests/test_aging_physics.py` | **ใหม่** — 10 unit/property/regression tests |

**env knobs (ค่าเริ่มต้น = ปิด/inert):** `aging_physics_enabled=False`, `aging_damage_rate=0.4`, `aging_repair_gain=0.5`, `aging_maintenance_cost=2.0`, `aging_damage_threshold=100.0`, `aging_mass_exponent=0.25`, `aging_max_repair_fraction=0.95`, `aging_intake_damage_coeff=0.0`

---

## 5. ผลการ validate เทียบเปเปอร์

`python scripts/run_aging_validation.py` — ขับ **โค้ดจริง** `Agent._apply_aging` แบบควบคุมทีละตัวแปร ผลทั้ง 4 arm **PASS**:

| Arm | เปเปอร์ | ผลที่ได้ | Verdict |
|---|---|---|---|
| **1. Allometry** | Speakman 2005 (อายุ ∝ มวล^0.15–0.3) | มวล 0.5→4.0 ให้อายุ 211→354; **exponent = 0.250** (อยู่ในแบนด์) | ✅ |
| **2. Disposable Soma** | Kirkwood 1977 | maintenance 0.0→1.0 ให้อายุ 250→5001 ticks (เพิ่มทางเดียว) | ✅ |
| **3. Membrane/mito** | Hulbert 2007, Kitazoe 2017 | damage_resistance 0.5→2.0 ให้อายุ 126→500 (เพิ่มเข้ม, แยกจากเมตาบอลิซึม) | ✅ |
| **4. Caloric restriction** | CALERIE (Ravussin/Waziry) | intake/tick 0→40 ให้อายุ 250→84 (กินน้อย=อยู่นาน) | ✅ |

นอกจากนี้ `tests/test_aging_physics.py` (10 tests) ยืนยันเชิงหน่วย: damage สะสม→senescence, mortality การันตีแม้ยีนดีสุด, exponent = 0.25 เป๊ะ, ยีนถ่ายทอดในขอบเขต, และ **off-path byte-identical**

**หมายเหตุ arm 4 (สำคัญ):** ในมนุษย์ CR พิสูจน์แล้วแค่ "ชะลอมาร์กเกอร์ความแก่" ยังไม่ยืนยัน "ยืดอายุขัยจริง" (Waziry 2023) — สคริปต์ระบุ caveat นี้ในผลลัพธ์

---

## 6. การรักษา reproducibility (byte-identical)

หลักฐาน 3 ชั้นว่าการเปลี่ยนนี้ **ไม่กระทบพฤติกรรมเดิมเมื่อปิด aging**:

1. **ชุดทดสอบเต็ม 77 tests ผ่านหมด** (67 เดิม + 10 ใหม่) รวม `test_seed_independence`
2. **test เจาะจง** `test_off_is_byte_identical_zero_extra_rng`: `draw_aging_genes=False` ใช้ RNG เท่ากับตอนไม่มี flag เป๊ะ (tail RNG draw เท่ากัน + trait เท่ากัน)
3. **regression จริง:** รัน driver แบบไม่เปิด `--aging` 2 ครั้ง (seed เดียว) → dump ต่างกันแค่ field เดียวคือ `elapsed_seconds` (นาฬิกา wall-clock) **ทุก field สถานะซิมเหมือนกันเป๊ะ**

---

## 7. วิธีรัน

```bash
# validate โมเดล aging เทียบเปเปอร์ (4 arm)
python scripts/run_aging_validation.py

# รันซิมจริงเปิด aging (การตายภายในเป็น senescence จาก damage)
python scripts/food_value_study_driver.py --model v2 --ticks 1200 --mortal --aging \
  --population 40 --world 60 --dump data/aging_run.json
# ปรับพารามิเตอร์: --aging-damage-rate --aging-maintenance-cost --aging-mass-exponent
#   --aging-damage-threshold --aging-intake-damage-coeff (เปิด CR) ฯลฯ

# ทดสอบหน่วย
python tests/test_aging_physics.py
```

สโมกจริง (world 60, pop 40, mortal, aging): founder ตาย **"senescence" ที่ tick ~287** (= threshold 100 / net-damage ~0.349) แทนเพดานอายุ 200 เดิม — การตายมาจากฟิสิกส์ ไม่ใช่ตัวนับ

---

## 8. ช่องว่างที่ปิดแล้ว vs ที่เหลือ (เทียบ audit)

| ช่องว่างใน audit | สถานะ |
|---|---|
| G1 การตาย = timer | ✅ **ปิด** — เป็น damage≥threshold |
| G2 อายุไม่ถ่ายทอด | ✅ **ปิด** — 4 ยีนอายุ heritable |
| G3 ไม่มี maintenance | ✅ **ปิด** — Disposable Soma มีราคาพลังงาน |
| G4 ไม่มีมวล/allometry | ✅ **ปิด** — `body_mass` + exponent 0.25 (validated) |
| G5 เมตาบอลิซึมไม่เชื่อมการตาย | ✅ **ปิด** — damage ∝ mass-specific metab, แยก `damage_resistance` |
| G6 CR ยืดอายุไม่ได้ | ✅ **ปิด** — intake-damage term (opt-in) |
| G8 พลังงานปัดจำนวนเต็มกลบสัญญาณ | ✅ **บรรเทา** — damage เป็น float + maintenance ใช้ debt-accumulator (สัญญาณยีนอายุไม่ถูกปัดทิ้ง) |
| G7 พลังงานไม่อนุรักษ์ | ⏳ เหลือ — ยังไม่ทำ energy-conservation audit (นอกขอบเขต aging) |
| G9 ความร้อนเมตาบอลิซึม | ⏳ เหลือ — ยังไม่ผูก metabolic heat |
| G10 ช่วงวัย = อายุตายตัว | ⏳ บางส่วน — ยังใช้เกณฑ์อายุ (ยังไม่ผูก stage กับ damage/mass) |
| G11 toxin→damage | ⏳ เหลือ — scaffold ยังไม่ต่อเข้า damage |

---

## 9. ข้อจำกัด + งานต่อ

**ข้อจำกัด (ต้องเขียนไว้ในรายงานประกวด):**
1. **เป็นโมเดลนามธรรมที่ซื่อตรงต่อหลักการ ไม่ใช่ชีวเคมีจริง** — 1 tick ≠ 1 หน่วยเวลาจริง, `damage` เป็นหน่วยนามธรรม, ค่าคงที่ (rate/threshold) ปรับได้ ไม่ได้ fit กับข้อมูลสัตว์จริง (calibration เป็นงานต่อ)
2. **การ validate เป็นการทดลองควบคุม** (ขับ `_apply_aging` โดยตรง) — จงใจแยกฟิสิกส์อายุออกจาก foraging/reproduction เพื่อพิสูจน์กลไก ยัง **ไม่ใช่** การเห็น allometry emerge จากประชากรที่วิวัฒนาการเต็มรูปแบบ เพราะประชากรยังไม่เสถียร (คอขวด foraging/energy — ดู `lifespan_masks_starvation`)
3. **exponent 0.25 ถูกตั้งเป็น knob** (`aging_mass_exponent`) แล้ววัดว่าออกมา 0.25 — เป็นการยืนยันว่า "โมเดลให้ค่าที่ตั้ง" (self-consistent) ไม่ใช่ทำนายค่าจากหลักการอิสระ การอ้างที่ปลอดภัย: "โมเดลสร้าง scaling law แบบ power-law ที่ควบคุมได้ ตรงรูปแบบ Speakman"
4. **CR ในคน** พิสูจน์แค่มาร์กเกอร์ (Waziry) — อย่าเขียนว่า "ซิมพิสูจน์ CR ยืดอายุคน"

**งานต่อ (ลำดับแนะนำ):**
- **A.** ทำประชากรให้เสถียร (งาน foraging/energy ที่ค้าง) แล้ว **วัด heritability ของ lifespan** + ดูวิวัฒนาการของ `somatic_maintenance` ตาม extrinsic mortality (ทดสอบ Kirkwood โดยตรง) = ผลเด่นสำหรับ ISEF
- **B.** calibrate ค่าคงที่กับข้อมูลสัตว์จริง (เช่น อัตราส่วนอายุหนู:นก) เพื่อยกจาก "self-consistent" เป็น "predictive"
- **C.** ปิด G7/G9/G11 (energy conservation, metabolic heat, toxin→damage)
- **D.** ผูกช่วงวัย (G10) กับ damage/mass แทนอายุตายตัว

---

*จบรายงาน — Aging Physics v1: การตายภายใน emerge จากความเสียหายสะสมตามทฤษฎีที่พิสูจน์แล้ว, opt-in, byte-identical เมื่อปิด, ผ่าน 77 tests + 4 validation arms. อ้างอิงเปเปอร์: ดู `papers/longevity/human_lifespan_determinants_review.md`*

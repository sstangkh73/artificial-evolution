# รายงานฉบับเต็ม: การสอบสวนเศรษฐกิจพลังงาน และการปลดล็อกการสืบพันธุ์ครั้งแรก

**โครงการ:** Artificial Evolution (ส่วนทดลองของข้อเสนอ TURC2026)
**วันที่:** 2026-06-19
**ผู้ทดลอง:** Chisanupong
**commit เครื่องมือ:** `cef1af4` (telemetry + knobs, default-neutral, v1 byte-identical)
**สถานะ:** สอบสวนครบ · แก้ความเชื่อผิด 2 ข้อ · ปลดล็อก births ครั้งแรกของโปรเจกต์

---

## บทคัดย่อ (Abstract)

งานก่อนหน้าชี้ว่าพฤติกรรมระดับสูงทุกอย่าง (การเลือกกิน, การเลือกที่ดรอปเมล็ด Phase 5, การสืบพันธุ์, Phase 6) ดู "ติดที่พลังงาน" รายงานนี้สอบสวนเศรษฐกิจพลังงานอย่างละเอียดด้วยการวัดตรง (ไม่ใช่อนุมาน) และพบว่าสมมติฐานเดิมของเราผิดหลายจุด

ผลหลัก: (1) **การตายในโหมด mortal ไม่ใช่การอดตาย** แต่เป็น **อายุขัย** — founder ทั้ง 50 ตัวเกิดอายุเท่ากัน (67) ตายพร้อมกันที่ MAX_AGE (200) = tick 133; `energy<=0` แค่ reset เป็น 1 ไม่เคยฆ่า (2) **drain ≈ 5/tick** (base 1 + brain 2 + move 2) เทียบ **intake ≈ 0.01/tick** (กินเพียง ~1 มื้อ/455 ticks ทั้งที่อาหารเหลือ → คอขวดคือการเข้าถึง ไม่ใช่ปริมาณ) (3) `hunger_level = 1 − energy/58` เป็นฟังก์ชันของพลังงานตรงๆ (4) การสืบพันธุ์ต้องครบ **3 ชั้น: พลังงาน ≥ 92, durability ≥ 18, และเงื่อนไขสังคม** — **body 37 มี durability = 10 จึงสืบพันธุ์ไม่ได้เชิงโครงสร้าง** ตลอดกาล

ผลชี้ขาด: regime ที่ดัน drain ลง + พลังงานอาหารขึ้น ทำให้เศรษฐกิจ **เกินดุล** (mean energy หลักพัน, hunger→0) และเมื่อใช้ร่วมกับ **body มีเกราะ (index 38, durability 26)** เกิด **การสืบพันธุ์ครั้งแรก: births 50, ประชากร 50→100** ขณะที่ body 37 ในสภาวะเดียวกันยังให้ 0 births สรุป: พลังงานเป็นเงื่อนไข**จำเป็นแต่ไม่พอ** — เป็น 1 ใน 3 ตัวบล็อก

---

## 1. บทนำ (Introduction)

### 1.1 ปัญหาและคำถามวิจัย
หลายการทดลอง (food-value learning, Phase 5 site-selection, Phase 6) ลงเอยว่า "agent จนเกินกว่าจะแสดงพฤติกรรม" คำถาม: **เศรษฐกิจพลังงานเป็นปัญหาจริงไหม เป็นเรื่องอาหารไม่พอหรือเมแทบอลิซึม และห่วงโซ่สาเหตุที่แท้จริงคืออะไร?**

### 1.2 สมมติฐานเริ่มต้น (ที่ต่อมาถูกแก้)
- H-เดิม: "agent อดตาย (perma-starvation) พลังงาน ≤ 0 → ตาย → ประชากรล่ม" — **ผิด** (ดู §3.3)
- H-เดิม: "อาจเป็นเพราะอาหารในโลกไม่พอ" — **ผิด** (ดู §3.2)

### 1.3 อุปสรรคเชิงวิธี
โหมด `immortal=True` (ที่ gate ทุกตัวใช้) บังคับ `energy = max(1, energy)` ทุก tick → อัดพลังงานฟรีเพื่อกันตาย → **บดบังเศรษฐกิจจริง** เราจึงสร้าง telemetry วัด "พลังงานที่ clamp อัดเข้าไป" = ขนาดการขาดดุลที่แท้จริง

---

## 2. ระเบียบวิธี (Methods)

### 2.1 เครื่องมือวัด (commit `cef1af4`, ปิดเป็น default)
- `clamp_energy_injected_total` — พลังงานที่ immortal floor อัดเข้าต่อ tick = การขาดดุลจริง
- ตัวสะสม drain แยกองค์ประกอบ: `drain_base/brain/move_total`
- `energy_gained_total` — พลังงานที่กินได้จริง
- `agent_death_reasons` — นับสาเหตุการตาย
- knob ปรับสมดุล (default 1.0 = byte-identical): `food_energy_multiplier`, `metabolic_drain_multiplier`

### 2.2 การทดลอง
1. **Budget decomposition** — baseline v2 immortal, แยก drain/intake/ความถี่กิน
2. **Food-supply test** — กวาดความหนาแน่นอาหาร (low_value 0/6/30) ดูว่าการขาดดุลเปลี่ยนไหม
3. **Mortality test** — immortal off, ดูว่าตายเมื่อไร/ด้วยเหตุใด, อาหารมีผลไหม
4. **Regime ladder** — กวาด drain↓ × density↑ × food-energy↑ (immortal) วัดว่าพลังงานแตะ 92 / hunger < 0.35 ได้ไหม
5. **Surplus-births check** — ในสภาวะเกินดุล births เกิดไหม หรือติด gate อื่น
6. **Capstone** — สภาวะเกินดุล × body มีเกราะ (38) vs ไม่มีเกราะ (37): births ปลดล็อกไหม

### 2.3 คอนฟิก
body 37 (sensor 2, muscle 2, armor 0, brain 2, social_planner) เว้นแต่ capstone, โลก 100×100, pop 50, v2, seed 20260610, 3000 ticks ต่อรัน
หมายเหตุ: ผล deterministic (seed ไม่กระทบ — movement RNG = `Random(agent_id+age)`) ตัวเลขจึง reproducible เป๊ะ

---

## 3. ผลการทดลอง (Results)

### 3.1 งบพลังงาน baseline
| รายการ | ค่า /agent/tick |
| --- | ---: |
| drain: base | 1.0 |
| drain: brain (passive) | 2.0 |
| drain: movement | 2.0 |
| **drain รวม** | **4.99** |
| intake (กินได้) | 0.011 |
| **ขาดดุลสุทธิ (clamp อัด)** | **4.93** |

ความถี่กิน: 330 มื้อรวม → **1 มื้อ/455 ticks/ตัว** · drain:intake = **453:1** · 1 มื้อ (~5 พลังงาน) ≈ อยู่ได้ **1 tick** · mean energy 1.12 (max 4)

### 3.2 Food-supply test (immortal) — อาหารไม่ใช่ปัญหา
| อาหาร/tick | ขาดดุล/tick | intake/tick | อาหารคงค้าง | เมล็ดที่กิน |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 4.93 | 0.011 | 36 | — |
| 6 | 4.91 | 0.028 | 757 | 1,371 |
| 30 | 4.84 | 0.095 | 2,654 | 14,103 |

เติมอาหาร 0→30/tick (คงค้าง 36→2,654, กิน 14,103 เม็ด) **ขาดดุลแทบไม่ขยับ** → ไม่ใช่ปัญหาปริมาณอาหาร อาหารเหลือเพียบ

### 3.3 Mortality test (immortal off) — ตายเพราะอายุขัย ไม่ใช่อด
ทุกเงื่อนไข (รวม drain÷20, food×50): **สูญพันธุ์ที่ tick 133 เป๊ะ**, `death_reason = lifespan_completed` ทั้ง 50 ตัว
สาเหตุ: `FOUNDER_START_AGE = 67` + `MAX_AGE = 200` → ตายที่ tick 133; founder รุ่นเดียวแก่พร้อมกัน ไม่มีรุ่นใหม่แทน (births=0)
ใน `_resolve_life_state`: `energy<=0 → energy=1` (ไม่ตาย); ตายจริงจาก durability/อายุ/child-isolation เท่านั้น → **knob พลังงานไม่กระทบ tick 133**

### 3.4 Regime ladder (immortal) — เศรษฐกิจเกินดุลทำได้
| เงื่อนไข | mean E | max E | hunger | ขาดดุล | มื้อ/tick |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 1.12 | 4 | 0.983 | 4.93 | 0.002 |
| drain ÷5 | 1.84 | 6 | 0.983 | 0.93 | 0.005 |
| drain ÷5 + density 20 | 1.05 | 1.8 | 0.983 | 0.90 | 0.050 |
| drain ÷5 + density 20 + food ×10 | 62.8 | 649 | 0.62 | 0.39 | 0.051 |
| **drain ÷10 + density 30 + food ×20** | **3185** | **8225** | **0.0** | **0.0006** | 0.076 |

- drain ÷5 ลดขาดดุล 4.93→0.93 (ตามสัดส่วน) แต่พลังงานยังไม่สะสม (intake < drain)
- ต้อง **drain↓ + density↑ + food-energy↑ พร้อมกัน** จึงพลิกเป็นเกินดุล (เงื่อนไขสุดท้าย: พลังงานล้น, hunger→0)
- หมายเหตุประสิทธิภาพ: `food_signal_at` เป็น O(จำนวนอาหาร) → รัน density สูงช้ามาก

### 3.5 Surplus-births check (body 37) — พลังงานพอแล้วแต่ยังไม่เกิด
ในสภาวะเกินดุล (mean E 3185, hunger 0, instinct=balanced ทุกตัว): **births = 0**
`low_energy`/`hunger` หลุดจากรายการ blocker แล้ว แต่ยังติด: `low_durability`, `no_mate`, `short_pair_bond`, `short_safety_window`, `low_safety/comfort/attachment`, `mate_stressed`
→ **พลังงานไม่ใช่ตัวบล็อกเดียว**

### 3.6 Capstone — เกราะปลดล็อกการสืบพันธุ์
สภาวะเกินดุล (drain ÷20 + food ×50, ความหนาแน่นปกติ), immortal, 3000t:

| body | durability | **births** | ประชากร | mean E | blocker เด่น |
| --- | ---: | ---: | --- | ---: | --- |
| 37 (armor 0) | 10 | **0** | 50→50 | 1256 | `low_durability` (10<18) + social |
| **38 (armor 2)** | 26 | **50** | **50→100** | 75 | (เกิดแล้ว; ที่เหลือติด social/low_energy หลังประชากรโต) |

**body 37 พลังงานล้น 1256 ก็ births=0** เพราะ `durability_ok` ต้อง ≥ 18 แต่ body.durability = 10 + armor×8 = 10 → เป็นไปไม่ได้ตายตัว · **body 38 (durability 26) → births 50, ประชากรเท่าตัว = การสืบพันธุ์ครั้งแรกของโปรเจกต์**

---

## 4. อภิปราย (Discussion)

### 4.1 ห่วงโซ่สาเหตุที่สมบูรณ์
```
drain ~5/tick ≫ intake ~0.01/tick (กิน 1 มื้อ/455 ticks; อาหารเหลือ = access จำกัด)
   ↓ energy ตันที่ ~1 → hunger = 1 − energy/58 = 0.983
reproduction gate (can_reproduce) ต้องครบ 3 ชั้น:
   ① energy ≥ 92          ← เศรษฐกิจพลังงาน
   ② durability ≥ 18       ← body 37 = 10  เป็นไปไม่ได้ตายตัว
   ③ mate + pair-bond + safety/comfort/attachment streaks
   ↓ ไม่ครบ → births = 0
founder รุ่นเดียว (อายุ 67) → ตายตามอายุขัยที่ tick 133 พร้อมกัน → สูญพันธุ์
```

### 4.2 แก้ความเชื่อผิด
- "อดตาย" → จริงๆ ตาย**ตามอายุขัย**; การอดไม่เคยฆ่า (reset เป็น 1)
- "อาหารไม่พอ" → อาหารเหลือเพียบ; คอขวด intake คือ**ความถี่กิน** (1/455 ticks) จากการเข้าถึง/หาอาหาร + อัตราส่วน drain:มื้อ
- "พลังงานคือตัวบล็อกเดียว" → เป็น **1 ใน 3** (พลังงาน + durability/เลือก body + social gates)

### 4.3 นัยเชิงปฏิบัติที่สำคัญ
- **การเลือก body กำหนดว่าจะสืบพันธุ์ได้ไหมเลย** — งาน gate ทั้งหมดใช้ body 37 (durability 10) ซึ่งสืบพันธุ์ไม่ได้เชิงโครงสร้าง → births=0 จึงถูก over-determined มาตลอด งาน generation/Phase 6 **ต้องใช้ body ที่ armor ≥ 1 (durability ≥ 18)**
- knob ที่ใช้ (food ×50, drain ÷20) เป็น **คันโยกหยาบและเทียม** — พิสูจน์ว่า "แก้ได้" แต่ไม่ใช่โมเดลที่สมจริง ควร rebalance แบบมีหลักการ (ดู §6)

---

## 5. ข้อจำกัด (Limitations)
1. **n=1 deterministic** — seed ไม่กระทบผล (movement RNG แยก) reproducible เป๊ะแต่ไม่ใช่ตัวอย่างสุ่ม
2. knob พลังงานเป็นการคูณหยาบ ไม่ได้สะท้อนกลไกจริง
3. ทดสอบในกรอบ immortal เป็นหลัก (เพื่อตัด confound อายุขัย); พลวัตภายใต้ mortality เต็มรูปยังไม่ครบ
4. หลัง birth wave ประชากรเท่าตัวแต่ energy ร่วง (75) hunger 0.857 → **ยังไม่ steady-state** (births เกิดแต่ไม่ยั่งยืน)
5. social gates (pair-bond/safety streak) ผ่านได้บางส่วน — ยังไม่ได้ศึกษาว่าอะไรกำหนดอัตรา

---

## 6. แนวทางที่จะทำต่อ (Future Work)

### เฟส S — ประชากรยั่งยืน (precondition จริงของ Phase 6) **[ทำก่อน]**
- หา regime ที่ **births ≈ deaths, energy นิ่ง, ประชากรคงตัว** โดย **ปิด immortal** (carrying capacity จริง)
- ตัวแปร: food density/energy, drain, ขนาดประชากรเริ่ม, **กระจายอายุ founder** (เลี่ยงตายพร้อมกันที่ 133)
- เกณฑ์ผ่าน: ประชากรอยู่ได้ > หลายช่วงอายุขัย โดยไม่พึ่ง immortal และ energy ไม่ collapse

### เฟส B — มาตรฐาน body สำหรับงาน generation
- กำหนด body มาตรฐานใหม่ที่ armor ≥ 1 (durability ≥ 18) เช่น index 38 (social_planner, armor 2) — เทียบ profile กับ 37 ได้
- รัน regression: body ใหม่ใน v1 ต้องไม่กระทบงานเดิม (หรือ document ว่าเปลี่ยน baseline)

### เฟส M — rebalance แบบมีหลักการ (แทนคันโยกเทียม)
- เป้าหมาย: 1 มื้อควรอยู่ได้ ~20–50 ticks (ไม่ใช่ 1) ที่ความถี่กินจริง → ปรับ drain/meal ให้สมจริง ไม่ใช่ ×50
- (ลึก) เจาะ **"ทำไมกินแค่ 1 มื้อ/455 ticks"** — แก้ foraging/access ที่รากจะลดการพึ่ง food density เทียม และเร่ง `food_signal_at` (O(n) → spatial index) เพื่อรัน density สูงได้เร็ว

### เฟส 6 — selection (เมื่อ S+B+M พร้อม)
- เมื่อมีประชากรยั่งยืน + ความแปรผัน (ผูก seed เข้า movement RNG) + heritability (Fix 3 เดิม) → ทดสอบ emergent evolution of seed-handling ได้จริง

ลำดับ: **S (ยั่งยืน) → B (body) ทำคู่กัน → M (rebalance) → Phase 6**

---

## 7. กรอบหลักฐาน (ตาม hypothesis-testing skill)
| | |
| --- | --- |
| **Supporting** | death=lifespan (tally 50/50 @133); drain decomposition วัดตรง; เกินดุลทำได้ (mean E 3185); **births 50 กับ body 38** (capstone) |
| **Against / Alternative** | body 37 พลังงานล้นยัง births=0 (durability) → พลังงานไม่พอเดียว; "เกินดุล" ใช้ knob เทียม; หลัง birth wave ยังไม่ steady-state |
| **Missing** | regime ยั่งยืนแบบ mortal; rebalance สมจริง; เหตุของความถี่กิน 1/455; multi-seed |
| **Confidence** | death=lifespan = **สูง** · เศรษฐกิจแก้ได้ = **สูง** · durability เป็น hard block ของ body 37 = **สูง** · births ปลดล็อกด้วยเกราะ = **สูง** · ประชากรยั่งยืนพร้อม Phase 6 = **ยังไม่** |

---

## 8. การทำซ้ำ (Reproducibility)
**commit:** `cef1af4` (telemetry + knobs) · driver: `.codex-temp/gate_run.py` (มี `--food-energy-mult`, `--drain-mult`, `--mortal`, `--body`)

```
# baseline budget
python .codex-temp/gate_run.py --model v2 --ticks 3000 --dump base.json
# mortality test (ตายเพราะอายุขัย)
python .codex-temp/gate_run.py --model v2 --ticks 600 --mortal --dump mort.json
# เศรษฐกิจเกินดุล
python .codex-temp/gate_run.py --model v2 --ticks 3000 --drain-mult 0.1 --low-value-food 30 --food-energy-mult 20 --dump surplus.json
# CAPSTONE: births ปลดล็อกด้วยเกราะ
python .codex-temp/gate_run.py --model v2 --ticks 3000 --body 38 --drain-mult 0.05 --food-energy-mult 50 --dump births.json
```

## ภาคผนวก: ค่าคงที่และอ้างอิงโค้ด
- `INITIAL_ENERGY=140`, `MAX_AGE=200`, `FOUNDER_START_AGE=67`, `ADULT_AGE=61` — ไม่มีเพดานพลังงาน
- `REPRODUCTION_THRESHOLD=150` (floor 92 ใน `can_reproduce`), `HUNGER_PRIORITY_ENERGY=58`, `MINIMUM_REPRODUCTION_HEALTH=18`
- `body.durability = 10 + armor_units×8` (`agents/body.py`)
- การตาย/clamp: `_resolve_life_state` (`agents/agent.py`); drain: `_base_energy_drain`/`_brain_energy_drain` + movement; gate: `can_reproduce`
- hunger: `hunger_level = clamp01((HUNGER_PRIORITY_ENERGY − energy)/HUNGER_PRIORITY_ENERGY)`

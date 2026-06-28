# รายงานการทดลอง: density brake แก้การสูญพันธุ์ได้ไหม — ผลคือ "ไม่" (พร้อมวินิจฉัยที่คมขึ้น)

**Does a proportional food-per-capita reproduction brake fix extinction? A multi-seed falsification + sharpened structural diagnosis**

ผู้วิจัย: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-27
สถานะ: implement กลไกครบ + verify (61 tests, byte-identical) · **multi-seed หักล้างว่าแก้ไม่ได้** · วินิจฉัยรากที่ลึกขึ้น
ต่อยอดจาก: `reports/r0_fecundity_analysis_2026-06-20.th.md`, `reports/extinction_final_blocker_consolidated_2026-06-27.th.md`

---

## บทคัดย่อ

ตามแผน "ทางแก้ที่คาดว่าจะได้ผล" จาก R₀ fecundity analysis — ใส่ **proportional density brake ที่อิง food-per-capita** เพื่อ damp การ oscillate แบบ delayed-logistic ให้ประชากร converge สู่ K. งานนี้ (1) **implement กลไกครบ** (opt-in, default-neutral, byte-identical, +7 unit tests) พร้อม telemetry `food_per_capita`/`standing_food` และเปิด knob `mortality_onset_fraction` สำหรับ de-synchronize การตาย; (2) **ทดสอบ multi-seed อย่างเป็นระบบ** — control vs brake (3 targets) vs de-sync vs ทุก combination. **ผลชี้ขาด: ทุกเงื่อนไข ทุก seed สูญพันธุ์หมด** — brake ทำงานเชิงกลไกจริง (กด peak 310→139) แต่**ไม่ยืดอายุประชากร** (มักแย่ลง). สาเหตุที่หักล้างแผนเดิม: ใน regime นี้ **อาหารไม่เคยถูกใช้จนจำกัด** (standing food คงที่ ~3,500) → ไม่มี carrying capacity จริงให้ brake ไป converge; และตัวฆ่าคือ **synchronized lifespan death** (85–95% ของการตาย) ที่ reproduction-throttle แก้ไม่ได้ — ส่วนการ de-sync การตายก็ลด lifespan → ลด R₀ → จางเร็วขึ้น (trade-off ที่หนีไม่พ้น). **ข้อสรุปที่คมขึ้น: ความเสถียรของประชากรแก้ด้วยการจูนฝั่งสืบพันธุ์/การตายไม่ได้ ตราบใดที่อาหารยังอุดมแบบเทียม — keystone จริงคือเศรษฐกิจอาหารสมจริงที่ foraging access จำกัด intake จน overpopulation เกิด starvation จริง (logistic K จริง)** ซึ่งวนกลับไปที่รากเศรษฐกิจพลังงานที่โปรเจกต์ระบุไว้แต่ยังไม่ได้สร้าง

---

## 1. สมมติฐานและสิ่งที่สร้าง

**สมมติฐาน (H):** ถ้าเบรกอัตราสืบพันธุ์แบบ proportional ตาม food-per-capita ที่ลดลง *ก่อน* ประชากร overshoot K การ oscillate จะถูก damp → ประชากร converge สู่ K เสถียร (ไม่สูญพันธุ์)

**กลไกที่ implement (ทั้งหมด opt-in, default = ปิด → v1 byte-identical):**

| ส่วน | ไฟล์ | ราย​ละเอียด |
|---|---|---|
| density brake | `agents/agent.py` | `_continuous_repro_food_brake(fpc, target)` = `min(1, fpc/target)`; คูณเข้า prob ของ continuous reproduction; target≤0 → 1.0 (×1.0 exact = byte-identical) |
| env knob | `world/environment.py` | `continuous_repro_food_target` (default 0.0 = off) + `food_per_capita` (telemetry ต่อ tick) |
| คำนวณ fpc | `scripts/run_long_emergence_watch.py` | `env.food_per_capita = len(food_positions) / max(1, len(agents))` ต่อ tick + เพิ่ม `standing_food`/`food_per_capita` ใน population_trajectory |
| de-sync knob | `world/environment.py` + driver | เปิด `mortality_onset_fraction` (เดิม hardcode 0.85) ให้ปรับได้ — ลดค่า = hazard ค่อยขึ้นตั้งแต่วัยผู้ใหญ่ |
| driver flags | `scripts/food_value_study_driver.py` | `--continuous-repro-food-target`, `--mortality-onset-fraction` |
| tests | `tests/test_density_brake.py` | 7 ข้อ: off=1.0, abundant=1.0, proportional, zero-food=0, guard ลบ, monotonic, env default off |

**Verify:** `test_density_brake` 7/7 · full suite **61/61** · `compileall` OK · brake off = byte-identical by construction

---

## 2. วิธีทดลอง (experiment-design skill)

- **IV:** `continuous_repro_food_target` (off / 18 / 28 / 40), `mortality_onset_fraction` (0.85 / 0.5 / 0.3), `founder_age_spread` (0 / 1)
- **DV:** ประชากรสูญพันธุ์ไหม (bool) · tick ที่สูญพันธุ์ · peak population · births
- **Control:** brake off = สูตรดีสุดของ fecundity report (continuous repro 0.35 + home-fidelity + scaffolded + stochastic mortality + starvation death + dense food)
- **Replication:** 3 seeds (20260610/11/12) — reproduction RNG ผูกกับ args.seed จึงได้ความผันแปรเชิงประชากรจริง
- **Metrics/criteria:** **สำเร็จ** = ประชากรอยู่รอดถึงครบ run (6000 ticks) ไม่สูญพันธุ์; **ล้มเหลว** = สูญพันธุ์ หรือ brake แรงจน fade ทันที
- config: body 14, world 100×100, mortal, 4000–6000 ticks, `PYTHONHASHSEED=0`

---

## 3. ผลการทดลอง

### 3.1 Control (brake off) — multi-seed
| seed | สูญพันธุ์ที่ tick | births | peak | deaths |
|---|---:|---:|---:|---|
| 20260610 | 2892 | 1124 | 310 | lifespan 1076 / starv 94 / dur 4 |
| 20260611 | 680 | 202 | — | lifespan 224 / starv 26 |
| 20260612 | 892 | 240 | — | lifespan 260 / starv 26 |

→ สูญพันธุ์ทุก seed · **85–95% ของการตายเป็น lifespan_completed** · standing food คงที่ ~3,500 ตลอด (อาหารไม่เคยหมด)

### 3.2 Density brake — single-seed sweep (seed 20260610)
| target | peak | สูญพันธุ์ที่ tick | หมายเหตุ |
|---:|---:|---:|---|
| off | 310 | 2892 | (control) |
| 18 (เบาสุด) | 196 | 569 | กด peak ได้ แต่ตายเร็วกว่า control |
| 28 | 160 | 1294 | ดีสุดใน 3 ค่า — ยังแพ้ control |
| 40 (แรงสุด) | 139 | 576 | กด peak มากสุด แต่ตายเร็ว |

### 3.3 Density brake t28 — multi-seed
| seed | control (off) | brake t28 | ผล |
|---|---:|---:|---|
| 20260610 | 2892 | 1294 | brake แย่ลง |
| 20260611 | 680 | 834 | brake ดีขึ้นนิด |
| 20260612 | 892 | 575 | brake แย่ลง |

→ **brake ไม่ช่วยให้อยู่นานขึ้นอย่างเชื่อถือได้** (2/3 seed แย่ลง) · ทุก seed ยังสูญพันธุ์

### 3.4 De-synchronize การตาย (± brake) — multi-seed
| เงื่อนไข | seed range สูญพันธุ์ที่ tick | births | ผล |
|---|---:|---:|---|
| founder-age-spread (ไม่มี brake) | 522–560 | 46–60 | **แย่กว่ามาก** — founder แก่ตายก่อนผสมพันธุ์ |
| brake + founder-spread | 375–694 | 8–104 | แย่ที่สุด |
| brake + mortality onset 0.5 | 591–794 | 134–216 | สูญพันธุ์ |
| brake + mortality onset 0.3 | 577–769 | 150–158 | สูญพันธุ์ (onset ต่ำ = ตายเร็ว) |

### 3.5 สรุปทุกเงื่อนไข
**ทุกเงื่อนไข ทุก seed → สูญพันธุ์ 100%** ไม่มีอันใดอยู่รอดถึง 6000 ticks · brake กด peak ได้จริง (310→139) แต่ไม่เปลี่ยนผลลัพธ์สุดท้าย

---

## 4. การตีความ — ทำไมแผน "ที่คาดว่าจะได้ผล" ถึงล้มเหลว (log-analysis skill)

**Observation:** brake กด peak สำเร็จแต่ไม่ยืดอายุ; ทุกชุดสูญพันธุ์; deaths ~90% เป็น lifespan

**สาเหตุที่หักล้างสมมติฐานเดิม:**

1. **อาหารไม่เคยจำกัด → ไม่มี K จริง.** standing food คงที่ ~3,500 ไม่ว่าประชากรเท่าไร (spawn เลี้ยงไว้สูง เพราะต้องชดเชยปัญหา foraging access "กิน 1 มื้อ/455 ticks"). brake ออกแบบมาให้ converge สู่ carrying capacity ที่ "อาหารต่อหัว" กำหนด — แต่เมื่ออาหารไม่ลดตามประชากร `food_per_capita` กลายเป็นแค่ proxy ของ `1/ประชากร` (ความหนาแน่นล้วน) ไม่มีจุดสมดุลทรัพยากรจริงให้เกาะ → brake ได้แค่ลดอัตราเกิด ไม่ได้สร้างเสถียรภาพ

2. **ตัวฆ่าคือ synchronized lifespan death ไม่ใช่ food competition.** 85–95% ของการตายเป็น `lifespan_completed` — cohort แก่ตายพร้อมกัน. reproduction-throttle แก้เรื่องนี้ไม่ได้ และยัง**ลบกลไกเอาตัวรอดของ control** (control อยู่ได้นานเพราะ re-boom ชดเชยหลัง crash ทุกครั้ง; brake กด re-boom → ตายเร็วขึ้น)

3. **De-sync การตาย trade-off กับ R₀.** ลด `mortality_onset_fraction` หรือ spread founder age → กระจายการตายได้จริง แต่**ลด lifespan เฉลี่ย → ลดผลผลิตการสืบพันธุ์ต่อ female (fecundity อยู่ที่ replacement พอดี ต้องใช้ lifespan เต็ม)** → R₀ ตกใต้ 1 มากขึ้น → จางเร็ว. หนีจาก boom-bust ไปเจอ sub-replacement fade

**Possible/Alternative causes ที่ตัดออก:** n=1 noise (หักล้างด้วย multi-seed — pattern เหมือนกันทุก seed); brake bug (telemetry ยืนยัน brake engage ถูก เช่น tick200 pop160 fpc21 target28 → brake 0.76)

---

## 5. ข้อสรุปและข้อเสนอเชิงโครงสร้าง

**ข้อสรุป:** สมมติฐาน "proportional food brake จะทำให้ประชากร converge สู่ K" **ถูกหักล้างด้วยการทดลองโดยตรง** (multi-seed). กลไกฝั่งสืบพันธุ์ (brake) และฝั่งการตาย (de-sync) — เดี่ยวหรือรวมกัน — แก้การสูญพันธุ์ไม่ได้ในระบบนี้ ผลนี้**ยืนยันและทำให้ข้อสรุป R₀-ceiling เดิมคมขึ้น**: ระบบ bistable ไม่มี stable fixed point ที่เอื้อมถึง และตอนนี้รู้ชัดว่า **ทำไมการจูนฝั่ง demographic ถึงข้ามไม่ได้**

**Keystone จริง (ข้อเสนอ):** ปัญหาวนกลับไปที่ **เศรษฐกิจอาหารสมจริง** ที่โปรเจกต์ระบุไว้แต่ยังไม่ได้สร้าง — ต้องทำให้ **foraging access จำกัด intake จริง** เพื่อให้ standing food *ลดลงเมื่อประชากรมาก* → overpopulation สร้าง food competition → starvation จริง → **logistic K จริง** แล้ว density brake (ที่สร้างไว้แล้ว) จึงจะมีจุดสมดุลให้ converge. ลำดับที่ถูก:
1. **แก้ราก foraging access** ("ทำไมกินแค่ 1 มื้อ/455 ticks") เพื่อให้ลดอาหารหนาแน่นเทียมได้โดยไม่ทำ agent อดตายทันที
2. ให้อาหารธรรมชาติ (mult 1) + drain สมจริง → standing food ผันตามการบริโภค
3. เปิด density brake + starvation death → food คุม K จริง
4. (รอง) de-sync การตายแบบไม่ลด lifespan — เช่น hazard คงที่ต่ำตั้งแต่ adult แทน ramp ตอนแก่ ต้องชดเชย R₀ ด้วย fecundity/litter

> นี่ไม่ใช่การจูน แต่เป็นการแก้ลำดับที่ถูก: **K ต้องมาก่อน brake** — brake ที่ดีไม่มีประโยชน์ถ้าไม่มี K ให้เบรกเข้าหา

---

## 6. สิ่งที่เก็บไว้ในโค้ด (kept) และเหตุผล

แม้ไม่แก้การสูญพันธุ์ กลไกที่สร้างถูกเก็บไว้เพราะ **ถูกต้อง ทดสอบแล้ว opt-in และเป็นเครื่องมือ/telemetry ที่จำเป็นต่องาน keystone ข้างหน้า** (สอดคล้องกับที่โปรเจกต์เก็บ home-fidelity/continuous-repro/stochastic-mortality ไว้แม้ยังไม่แก้ปัญหาเดี่ยว ๆ):

- `continuous_repro_food_target` — density brake ที่พิสูจน์แล้วว่า *กด boom ได้จริง* (peak 310→139); จะมีประโยชน์เมื่อมี K จริง
- `food_per_capita` / `standing_food` telemetry — **เป็นตัวที่เผยข้อค้นพบหลัก** (อาหารไม่เคยจำกัด) ควรเก็บไว้เฝ้าทุก sustainability run
- `mortality_onset_fraction` — knob ที่ควรมีอยู่แล้ว (เดิม hardcode) สำหรับศึกษา de-sync
- `_continuous_repro_food_brake` + 7 tests — pure, testable

ทั้งหมด default-neutral; ไม่กระทบผล food-value learning / การทดลองเดิมใด ๆ

---

## 7. กรอบหลักฐาน (hypothesis-testing skill)

| | |
|---|---|
| **Supporting** | brake กด peak (310→139) ทุก target = กลไกทำงาน; telemetry ยืนยัน fpc/brake ถูกต้อง |
| **Against (หักล้าง H)** | ทุกเงื่อนไข/ทุก seed สูญพันธุ์; brake ไม่ยืดอายุ (2/3 seed แย่ลง); de-sync ทุกแบบก็สูญพันธุ์ |
| **Alternative ที่ยืนยัน** | อาหารไม่จำกัด (standing food ~3500 flat) + lifespan-sync death (90%) = รากจริง ไม่ใช่ reproduction rate |
| **Missing** | regime ที่อาหารจำกัดจริง (ยังสร้างไม่ได้ — ติด foraging access); de-sync แบบไม่ลด lifespan |
| **Confidence** | "food brake เดี่ยวไม่แก้สูญพันธุ์" = **สูง** (multi-seed, multi-mechanism) · "keystone คือเศรษฐกิจอาหารสมจริง/foraging access" = **สูง** (สอดคล้องหลักฐานเดิม + ผลนี้) |

---

## 8. การทำซ้ำ (Reproducibility)

```bash
# control (brake off) — สูญพันธุ์
PYTHONHASHSEED=0 python scripts/food_value_study_driver.py --model v2 --ticks 6000 --mortal --body 14 \
  --scaffolded --home-fidelity --continuous-repro --continuous-repro-rate 0.35 \
  --starvation-death --stochastic-mortality --mortality-hazard 0.04 --drain-mult 0.03 \
  --max-pop 5000 --food-energy-mult 1 --low-value-food 45 --repro-litter-min 2 --repro-max-age 300 \
  --dump control.json

# + density brake (เพิ่ม flag เดียว) — ยังสูญพันธุ์
  ... --continuous-repro-food-target 28 --dump brake.json

# + de-sync การตาย — ยังสูญพันธุ์
  ... --continuous-repro-food-target 28 --mortality-onset-fraction 0.5 --dump brake_desync.json
```
batch multi-seed: `scratchpad/run_batch.py`, `run_batch2.py`, `run_batch3.py` · วิเคราะห์: `analyze.py` (อ่าน population_trajectory: standing_food/food_per_capita/generation_counts)

commit เครื่องมือ: (LOCAL ยังไม่ push) — density brake + food-per-capita telemetry + mortality_onset_fraction knob + 7 tests

---

*รายงานนี้รันการทดลองจริง (≥18 รัน, 3 seeds, 6 เงื่อนไข) — ตัวเลขทั้งหมดมาจาก dump จริง; กลไกถูก verify ด้วย 61 unit tests และ byte-identical guarantee*

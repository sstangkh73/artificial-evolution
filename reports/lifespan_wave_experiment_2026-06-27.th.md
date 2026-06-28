# รายงานการทดลอง: คลื่นการตายตามอายุขัย คือ root cause ของการสูญพันธุ์หรือไม่?

**Is the synchronized lifespan-death wave the extinction root cause? Testing memoryless death physics**

ผู้วิจัย: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-27
สถานะ: ทดสอบสมมติฐานเสร็จ — **คลื่นมีจริง แต่ไม่ใช่ root cause** (ระบบอยู่ที่ R₀≈1 knife-edge ไม่มี buffer)
ต่อจาก: `reports/density_brake_experiment_2026-06-27.th.md`

---

## บทคัดย่อ
สมมติฐาน (จากผู้วิจัย): การสูญพันธุ์เกิดจาก **ฟิสิกส์อายุขัยที่ทำให้ agent ตายพร้อมกันเป็นคลื่น** (cohort รุ่นเดียวแก่ตายพร้อมกัน). ทดสอบโดยเพิ่มโหมดการตายแบบ **memoryless constant hazard จากวัยผู้ใหญ่** (อายุขัยแบบ exponential = ไม่มีคลื่นเลย) โดย**คุม mean lifespan ให้เท่าเดิม** เพื่อแยก "คลื่น" ออกจาก "อายุสั้นลง". ผล: (1) **ยืนยันว่าคลื่นมีจริง** — control มี deaths/window CV=0.60 แกว่ง 9→193 ต่อ window; (2) constant-hazard **ลดคลื่นได้จริง** (CV 0.60→0.47, ไม่มี boom: peak 310→119, deaths เรียบขึ้น) **แต่ทุก 9 รัน (3 hazard × 3 seeds) ยังสูญพันธุ์** — เร็วกว่า control ด้วยซ้ำ. กลไก: การกำจัดคลื่น**แปลง boom-bust-crash เป็น smooth sub-replacement fade** — ทั้งคู่จบที่สูญพันธุ์ เพราะ **fecundity อยู่ที่ระดับทดแทนพอดี (R₀≈1) ไม่มี buffer** และการ de-sync ยังทำให้ adult บางส่วนตายก่อนได้สืบพันธุ์ → R₀ ตกใต้ 1. **ข้อสรุป: คลื่นการตายเป็น *อาการ* ของการอยู่บน R₀≈1 knife-edge ไม่ใช่ *สาเหตุ* — แก้คลื่นไม่ได้แก้การสูญพันธุ์**

---

## 1. สมมติฐานและการทดสอบ
**H:** agent ตายพร้อมกันเป็นคลื่น (synchronized lifespan death) → ประชากรล่มเป็นพัลส์ → สูญพันธุ์. ถ้ากระจายการตายให้ไม่เป็นคลื่น (โดยไม่ลด mean lifespan) ประชากรจะเสถียร

**ฟิสิกส์การตายเดิม (`agent.py` stochastic mortality):** hazard = 0 จนถึงอายุ 0.85×max_age (=255) แล้ว ramp ขึ้น → cohort รอดอิสระถึง 255 แล้วตายในหน้าต่างแคบ = **คลื่น**

**โหมดใหม่ (opt-in, default off, byte-identical):** `mortality_constant_hazard` — hazard คงที่ต่อ tick ตั้งแต่ ADULT_AGE → อายุขัยแบบ exponential, memoryless, **อายุการตายไม่ขึ้นกับ cohort = ไม่มีคลื่นทางทฤษฎี**. mean adult lifespan ≈ 1/hazard → เลือก h เพื่อคุม mean ให้ใกล้ของเดิม

---

## 2. วิธี
- **IV:** `mortality_constant_hazard` ∈ {0.004, 0.005, 0.006} (mean adult lifespan ≈ 250/200/167 ticks ใกล้ของเดิม ~220)
- **Control:** โหมดเดิม (late-onset ramp) — สูตรดีสุดของ fecundity report
- **DV:** สูญพันธุ์ไหม · tick · peak · **deaths/window CV** (วัดความเป็นคลื่น: สูง=คลื่น ต่ำ=เรียบ)
- **Replication:** 3 seeds · 6000 ticks · `PYTHONHASHSEED=0`
- **Success:** ประชากรอยู่รอดถึง 6000 ticks · **Falsify H:** de-sync สำเร็จ (CV ลด) แต่ยังสูญพันธุ์

---

## 3. ผล

### 3.1 ยืนยันว่าคลื่นมีจริง (control)
deaths/window แกว่ง: 9 → 150 → 63 → 79 → 97 → 64 → 16 → 26 → 52 → 110 → 180 → 193 → 77 → 51 · **CV = 0.60** · peak pop 310

### 3.2 Constant hazard ลดคลื่นได้ แต่ยังสูญพันธุ์ทุกรัน
| hazard | seeds สูญพันธุ์ที่ tick | peak | deaths CV | ผล |
|---:|---|---:|---:|---|
| 0.004 | 633 / 671 / 1350 | 105–143 | 0.47* | สูญพันธุ์ 3/3 |
| 0.005 | 538 / 780 / 789 | 80–124 | ~0** | สูญพันธุ์ 3/3 |
| 0.006 | 692 / 697 / 782 | 83–101 | ~0** | สูญพันธุ์ 3/3 |

\* รันที่อยู่นานสุด (ch0.004 seed12, 1350t): CV 0.47 < control 0.60 = **de-sync สำเร็จ**
\** รันสั้น (<800t) มี window น้อยเกินวัด CV เชื่อถือได้

### 3.3 Pattern ที่เปลี่ยนไป (ch0.004 seed12 — ตัวอย่างชัด)
| tick | 200 | 400 | 600 | 800 | 1000 | 1200 |
|---|---:|---:|---:|---:|---:|---:|
| pop | 119 | 64 | 40 | 44 | 31 | 9 |
| deaths/win | 63 | 85 | 52 | 36 | 35 | 22 |

ประชากร**ค่อย ๆ จางแบบ monotonic** (ไม่ใช่ oscillate) · deaths เรียบลง · **= sub-replacement fade** (births 252 < deaths 302)

---

## 4. การตีความ — ทำไมแก้คลื่นแล้วยังสูญพันธุ์
1. **De-sync สำเร็จจริง** — ไม่มี boom (peak 310→119), deaths เรียบ (CV 0.60→0.47), boom-bust หายไป
2. **แต่แปลงเป็น sub-replacement fade** — เมื่อ death เป็น memoryless จากวัยผู้ใหญ่ adult บางส่วน**ตายก่อนได้สืบพันธุ์** (การสืบพันธุ์ต้องใช้เวลา streak หลายสิบ tick หลังโตเต็มวัย) → ผลผลิตการสืบพันธุ์ที่แท้จริงตก → R₀ < 1
3. **รากที่แท้: R₀≈1 knife-edge ไม่มี buffer** — fecundity อยู่ที่ระดับทดแทนพอดี (~2.0, จาก fecundity report) ฉะนั้น:
   - death เป็นคลื่น → boom-bust → crash
   - death ไม่เป็นคลื่น → ตายก่อนสืบพันธุ์ → fade
   - **ทั้งสองทางจบที่สูญพันธุ์** เพราะไม่มี surplus ให้ดูดซับความผันผวนแบบใดเลย

> **คลื่นเป็นอาการ ไม่ใช่สาเหตุ** — สาเหตุคือระบบไม่มี reproductive surplus (R₀ ไม่ขึ้นเหนือ 1 อย่างมี margin). การปรับฟิสิกส์การตายแค่ย้ายโหมดความล้มเหลว ไม่ได้สร้าง surplus

---

## 5. ข้อสรุปและก้าวต่อไป
**สมมติฐาน "คลื่นการตายคือ root cause" ถูกหักล้าง** (multi-seed): คลื่นมีจริงและกำจัดได้ แต่ไม่ทำให้ประชากรเสถียร เพราะระบบอยู่บน R₀≈1 knife-edge. รวมกับผล density-brake (รายงานก่อนหน้า) ตอนนี้**ปิดทั้งฝั่งสืบพันธุ์ (brake) และฝั่งการตาย (de-sync) แล้ว — ไม่มีทางใดในการจูน demographic ที่แก้ได้**

**สิ่งที่เหลือคือสร้าง reproductive surplus จริง** ซึ่งต้องยกระดับการอยู่รอด/ผลผลิตที่ราก = **เศรษฐกิจอาหารสมจริงที่ foraging access ไม่เป็นคอขวด** (keystone). → เริ่มงานถัดไป: วินิจฉัย foraging access ("ทำไมกินแค่ 1 มื้อ/455 ticks") เพื่อให้ลดอาหารหนาแน่นเทียมได้และให้อาหารคุม K จริง — ดู `reports/foraging_access_*` (กำลังทำ)

---

## 6. โค้ดที่เพิ่ม (kept, opt-in, byte-identical, 61 tests)
`mortality_constant_hazard` (env field + driver flag `--mortality-constant-hazard`) — โหมดการตาย memoryless; default 0 = off (else-branch รันโค้ดเดิมเป๊ะ, RNG ไม่เปลี่ยน). เป็นเครื่องมือวิจัยพลวัตประชากรที่ใช้ต่อได้

## 7. กรอบหลักฐาน
| | |
|---|---|
| **Supporting H** | control มีคลื่นจริง (CV 0.60, swing 9→193) |
| **Against H (หักล้าง)** | de-sync สำเร็จ (CV→0.47, peak 310→119) แต่ทุก 9 รันสูญพันธุ์ → คลื่นไม่ใช่สาเหตุ |
| **Alternative ที่ยืนยัน** | R₀≈1 knife-edge: de-sync ฆ่า adult ก่อนสืบพันธุ์ → sub-replacement fade |
| **Confidence** | "คลื่นไม่ใช่ root cause" = **สูง** (multi-seed) · "ต้องสร้าง reproductive surplus ที่ราก (foraging access)" = **สูง** |

## 8. การทำซ้ำ
```bash
PYTHONHASHSEED=0 python scripts/food_value_study_driver.py --model v2 --ticks 6000 --mortal --body 14 \
  --scaffolded --home-fidelity --continuous-repro --continuous-repro-rate 0.35 \
  --starvation-death --stochastic-mortality --mortality-hazard 0.04 --drain-mult 0.03 \
  --max-pop 5000 --food-energy-mult 1 --low-value-food 45 --repro-litter-min 2 --repro-max-age 300 \
  --mortality-constant-hazard 0.004 --dump ch.json
```
batch: `scratchpad/run_batch4.py` · วิเคราะห์ (มี deaths/window CV): `scratchpad/analyze.py`

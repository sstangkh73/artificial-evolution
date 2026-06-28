# รายงาน: อายุขัยบดบังการอดตาย — generational overlap กับการ unmask ตัวฆ่าที่แท้จริง

**Lifespan death was masking chronic starvation: the generational-overlap test unmasks the true mortality**

ผู้วิจัย: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-27
สถานะ: ทดสอบสมมติฐาน "อายุขัย/generational overlap" → **อายุยืนไม่แก้การสูญพันธุ์ แต่ unmask ว่าตัวฆ่าจริงคือ starvation (พลังงาน)**
ต่อจาก: `lifespan_wave_experiment_2026-06-27`, `foraging_access_keystone_diagnosis_2026-06-27`

---

## บทคัดย่อ
สมมติฐาน (ผู้วิจัย): ในครอบครัวมนุษย์รุ่นปู่อยู่ทันหลานโตเต็มวัย (overlap ~3 รุ่น); ในซิม agent อาจ**อายุสั้นเกินจน generations ไม่ซ้อนทับ** → คลื่นกลิ้ง → ไม่เสถียร. ตรวจข้อมูล: **ยืนยันว่ารุ่นกลิ้งไปข้างหน้าจริง** (founder รุ่น0 ตายหมดที่ tick ~400 ก่อนเหลนเกิด). ทดสอบอายุยืน (repro_max_age 300→600→1200) ± density brake (3 seeds). ผล: (1) อายุยืน**ทำให้ founder อยู่นานขึ้นจริง** (gen0 อยู่ถึง tick 1000) และ overlap เพิ่ม; **แต่ทุกชุดยังสูญพันธุ์** และ births **ไม่เพิ่ม** (เท่าเดิมเป๊ะต่อ seed) — เพราะประชากร crash ใน boom-bust รอบแรกก่อนที่อายุยืนจะมีผล แล้ว stragglers อายุยืนแค่ลากยาวโดยไม่สืบพันธุ์ (Allee). (2) **การค้นพบสำคัญ: ยิ่งอายุยืน สาเหตุการตายพลิกจาก "แก่ตาย" เป็น "อดตาย"** — maxage300: starvation 8%; maxage600: ~44-58%; maxage1200: ~62-72%. **"lifespan_completed ~90%" ในทุกการทดลองก่อนหน้าบดบังภาวะอดตายเรื้อรัง** — agent แก่ตายก่อนที่พลังงานต่ำเรื้อรังจะฆ่า. **ข้อสรุป: อายุขัยไม่ใช่ตัวแก้ แต่การทดสอบมันได้ unmask ว่า binding constraint คือ เศรษฐกิจพลังงาน/foraging (starvation) ไม่ใช่ demographics** — ยืนยัน keystone (งาน ก) ชี้ขาด

---

## 1. ยืนยันสัญชาตญาณ: รุ่นกลิ้งไปข้างหน้า ไม่ซ้อนทับเสถียร
control (maxage 300), generation_counts ตามเวลา:
| tick | 200 | 400 | 600 | 800 |
|---|---|---|---|---|
| รุ่นที่อยู่ | 0-3 (รุ่น0=45) | 2-6 (**รุ่น0,1 หาย**) | 4-8 | 6-11 |

→ founder (รุ่น0) **ตายหมดที่ tick ~400** ก่อนเหลนเกิด · แต่ละ cohort สืบพันธุ์แล้วตายพร้อมกัน = คลื่นกลิ้ง (ตรงกับสัญชาตญาณ "ปู่ไม่อยู่ทันหลาน")

## 2. อายุยืน: founder อยู่นานขึ้นจริง แต่ไม่แก้
| เงื่อนไข | สูญพันธุ์ที่ tick | births | peak | gen0 อยู่ถึง tick |
|---|---:|---:|---:|---:|
| control (maxage300) | 680–2892 | 202–1124 | 310 | ~200 |
| maxage600 | 958–1118 | 192–240 | 194–218 | **400** |
| maxage1200 | 1525–1630 | 192–240 | 194–218 | **1000** |
| maxage1200 + brake | 1425–1649 | 120–248 | 156–217 | 1000 |

- founder อยู่นานขึ้นชัด (gen0_last 200→1000) — overlap เพิ่มตามที่ทำนาย
- **แต่ births เท่าเดิมเป๊ะ** (life600 vs life1200 ต่อ seed) → อายุยืนที่เพิ่มมา**ไม่ถูกใช้สืบพันธุ์**: ประชากร crash ในรอบแรกก่อน แล้ว stragglers อายุยืนลากยาวโดยไม่สืบพันธุ์ (หาคู่/เงื่อนไขไม่ครบหลัง crash = Allee)
- **ทุกชุดสูญพันธุ์**

## 3. การค้นพบสำคัญ: อายุขัยบดบัง starvation
| repro_max_age | ตาย starvation | ตาย lifespan | **%starvation** |
|---:|---:|---:|---:|
| 300 (control) | 94 | 1076 | **8%** |
| 600 | 75–181 | 81–140 | **44–58%** |
| 1200 | 93–214 | 55–77 | **62–72%** |

**dose-response ชัด: ยิ่งอายุยืน ยิ่งตายเพราะอดแทนที่จะแก่ตาย.** กลไก: agent พลังงานต่ำเรื้อรัง (จาก foraging access) อยู่ใกล้ starvation ตลอด; ที่อายุสั้น **แก่ตายก่อน** (เพดานอายุ "เมตตา" บดบัง); ที่อายุยืน อยู่นานพอจน starvation (energy≤0 > 15 ticks) ฆ่าได้

ตัวอย่าง maxage1200 seed10: peak 194 → ค่อยจาง 132→100→67→31→19→0, **starvation 158 / lifespan 59**, max_generation ค้างที่ 5 (หยุดสืบพันธุ์หลัง boom) ทั้งที่ standing food ~3000 → ภาวะพลังงานเป็นคอขวด ไม่ใช่ปริมาณอาหารรวม

## 4. ข้อสรุป — เหตุใดนี่สำคัญ
สมมติฐานอายุขัยของผู้วิจัย**ให้ผลสูง** ไม่ใช่เพราะอายุขัยเป็นตัวแก้ แต่เพราะการทดสอบมัน **unmask ตัวฆ่าที่แท้จริง**:
```
foraging access แย่ → พลังงานต่ำเรื้อรัง (ใกล้ starvation ตลอด)
        ↓                              ↓
แก่ตายก่อน (maxage สั้น)        อยู่นานพอ → อดตาย (maxage ยาว)
   = บดบัง starvation              = starvation โผล่ 62-72%
        ↓
พลังงานต่ำ → ประตูสืบพันธุ์ไม่เปิด → R₀≈1 → boom-bust → Allee → สูญพันธุ์
```
**ทุกเส้นทาง (wave, lifespan, brake, de-sync) ลงรากเดียวกัน: เศรษฐกิจพลังงาน/foraging.** การปรับ demographic ทั้งหมดล้มเหลวเพราะแก้ปลายเหตุ. **ต้องแก้ที่ foraging access (งาน ก) ให้ agent ได้พลังงานเกินดุลจริง → ประตูสืบพันธุ์เปิด + ไม่อดตาย → ออกจาก knife-edge**

## 5. กรอบหลักฐาน
| | |
|---|---|
| **Supporting (สมมติฐาน overlap)** | รุ่นกลิ้งจริง (gen0 หายที่ tick 400); อายุยืนทำ founder อยู่นานขึ้น |
| **Against (อายุขัยเป็นตัวแก้)** | ทุกชุดสูญพันธุ์; births ไม่เพิ่มตามอายุ; stragglers ลากยาวไม่สืบพันธุ์ |
| **Discovery** | อายุยืน → death พลิกเป็น starvation 62-72% → lifespan-death บดบัง energy เป็นตัวฆ่าจริง |
| **Confidence** | "อายุขัยบดบัง starvation; energy/foraging คือ binding constraint" = **สูง** (dose-response, multi-seed) |

## 6. การทำซ้ำ
```bash
# อายุยืน -> death เปลี่ยนเป็น starvation
PYTHONHASHSEED=0 python scripts/food_value_study_driver.py --model v2 --ticks 6000 --mortal --body 14 \
  --scaffolded --home-fidelity --continuous-repro --continuous-repro-rate 0.35 \
  --starvation-death --stochastic-mortality --mortality-hazard 0.04 --drain-mult 0.03 \
  --max-pop 5000 --food-energy-mult 1 --low-value-food 45 --repro-litter-min 2 \
  --repro-max-age 1200 --dump life1200.json
# เทียบ agent_death_reasons: starvation พุ่ง, lifespan ตก
```
batch: `scratchpad/run_batch5.py`

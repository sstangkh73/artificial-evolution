# รายงานฉบับเต็ม (Session Report): การสอบสวนการสูญพันธุ์ของประชากร — โค้ด + การทดลอง + ข้อสรุป

**Full session report: the population-extinction investigation — mechanisms built, experiments run, and the unified conclusion**

ผู้วิจัย: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-27
ขอบเขต: รวบยอดงานทั้ง session — โค้ดที่เพิ่ม 4 ไฟล์ + เทสต์, การทดลอง ~40 รัน, รายงานย่อย 5 ฉบับ
สถานะ: root cause ชี้ขาดแล้ว (5 เส้นทางอิสระยืนยันตรงกัน) · ยังไม่ได้ประชากรเสถียร · โค้ดทั้งหมด opt-in/byte-identical, 61 tests เขียว · **ยังเป็น local ไม่ push**

---

## 0. บทคัดย่อ (อ่าน 1 นาที)

โจทย์: ประชากร mortal สูญพันธุ์เสมอ = โซ่เส้นสุดท้ายก่อน Phase 6 (วิวัฒนาการจริง). Session นี้เริ่มจากสรุปงานเก่า แล้ว**ทดสอบทางแก้ที่เป็นไปได้ทุกทางอย่างเป็นระบบ (multi-seed)** พร้อมสร้างกลไก+telemetry ที่จำเป็น. ผลทุกการทดลองสูญพันธุ์ — **แต่ปิดทุกสมมติฐานทีละข้อจนเหลือรากเดียว**:

| สมมติฐานที่ทดสอบ | ผล | ปิดประเด็น |
|---|---|---|
| reproduction rate ต่ำ (fecundity) | fecundity = 2.0 = replacement พอดี | ไม่ใช่ |
| density brake (food-per-capita) จะ damp oscillation | สูญพันธุ์ทุก seed; อาหารไม่เคยจำกัด | ไม่ใช่ |
| คลื่นการตายตามอายุขัย (synchronized wave) | กำจัดคลื่นได้ (CV 0.60→0.47) แต่ยังสูญพันธุ์ | อาการ ไม่ใช่สาเหตุ |
| อายุขัยสั้น/generations ไม่ซ้อนทับ | อายุยืนไม่แก้ + births ไม่เพิ่ม | ไม่ใช่ตัวแก้ |
| **foraging access (เศรษฐกิจพลังงาน)** | **agent มองอาหารไม่เห็น → พลังงานต่ำเรื้อรัง** | **ใช่ — root cause** |

**ข้อสรุปชี้ขาด:** binding constraint คือ **เศรษฐกิจพลังงาน/foraging** ไม่ใช่ demographics. หลักฐานเด็ด — เมื่อยืดอายุขัย สาเหตุการตายพลิกจาก "แก่ตาย 92%" เป็น "อดตาย 72%": lifespan-death **บดบัง** การอดตายเรื้อรังมาตลอด. การจูน demographic ทุกแบบแก้ปลายเหตุ. ทางแก้จริง = แก้ foraging access (งาน ก) ให้พลังงานเกินดุล → ประตูสืบพันธุ์เปิด + ไม่อดตาย

---

## 1. คำถามและบริบท

**เป้าหมายปลายทาง:** วิวัฒนาการจริงในซิม (mortal + heritable + selection ข้ามรุ่น). **Precondition เดียวที่ค้าง:** ประชากรต้องไม่สูญพันธุ์. ถ้าสูญพันธุ์ใน 2-6 รุ่น selection เกิดไม่ได้

**สถานะก่อน session (จากงานเก่า 2026-06-02 → 06-20):** Phase 1-3 ผ่าน (ecology, reward-place, seed causality); Phase 4-5 ติด; ประชากรสูญพันธุ์ทุกชุด (~33 รัน, R₀ ติดเพดาน 0.75-0.88); fecundity report (06-20) พลิกว่า fecundity = replacement แล้ว ปัญหาคือ "พลวัต" — เสนอ density brake เป็นทางแก้

---

## 2. โค้ดที่เพิ่ม (opt-in ทั้งหมด, default-neutral, byte-identical, +7 tests → suite 61/61)

| กลไก / telemetry | ไฟล์หลัก | knob / flag | จุดประสงค์ |
|---|---|---|---|
| **density brake** (food-per-capita) | `agents/agent.py` (`_continuous_repro_food_brake`), `world/environment.py` | `continuous_repro_food_target` / `--continuous-repro-food-target` | เบรกการเกิดตามอาหารต่อหัวก่อน overshoot |
| **food_per_capita** state + telemetry | `run_long_emergence_watch.py`, env | (อัตโนมัติต่อ tick) | วัดความหนาแน่น/อาหารต่อหัว |
| **mortality_onset_fraction** (เปิด knob เดิม) | env, driver | `--mortality-onset-fraction` | เลื่อนจุดเริ่ม hazard เพื่อ de-sync |
| **mortality_constant_hazard** (โหมดใหม่) | `agents/agent.py` aging block, env | `--mortality-constant-hazard` | การตาย memoryless = ไม่มีคลื่น (คุม mean lifespan) |
| **foraging-access telemetry** | `run_long_emergence_watch.py` | (sample 40 agents/200t) | `mean_food_dist`, `frac_sensing_food`, `standing_food` |
| **unit tests** | `tests/test_density_brake.py` | — | 7 ข้อ (brake math + env defaults) |

**ไฟล์ที่แตะ:** `agents/agent.py` (+94), `world/environment.py` (+85), `scripts/run_long_emergence_watch.py` (+25), `scripts/food_value_study_driver.py` (+19), `tests/test_density_brake.py` (ใหม่)

**การยืนยัน:** `compileall` OK · full suite **61/61** (PYTHONHASHSEED=0) · byte-identical by construction (ทุก knob default = ปิด → code path เดิมเป๊ะ, RNG ไม่เปลี่ยน) · ตรวจ claim ระดับโค้ดกับซอร์สจริง (durability=10+armor×8, MIN_REPRO_HEALTH=18, energy≤0 reset เป็น 1 ใน mortal ปกติ)

---

## 3. แคมเปญการทดลอง (~40 รัน, multi-seed, PYTHONHASHSEED=0)

ทุกการทดลองใช้สูตรดีสุดของ fecundity report เป็นฐาน: body 14, world 100×100, scaffolded + home-fidelity + continuous-repro 0.35 + starvation-death + stochastic-mortality + dense food (lvf 45) + drain 0.03, mortal

### 3.1 Density brake → สูญพันธุ์ทุก seed
| target | peak | สูญพันธุ์ (3 seeds) |
|---:|---:|---|
| off (control) | 310 | 680 / 892 / 2892 |
| 18 / 28 / 40 | 196 / 160 / 139 | สูญพันธุ์ทุกค่า (t28 ดีสุด: 575-1294) |

กด peak ได้จริง แต่ไม่ยืดอายุ (2/3 seed แย่ลง) · **standing food คงที่ ~3500 ตลอด = อาหารไม่เคยจำกัด → ไม่มี K จริงให้ brake converge**

### 3.2 De-synchronize การตาย → สูญพันธุ์ทุกแบบ
| วิธี | ผล |
|---|---|
| founder-age-spread | แย่กว่ามาก (founder แก่ตายก่อนผสมพันธุ์, births 8-104) |
| mortality onset 0.3/0.5 | สูญพันธุ์ (ลด lifespan → ลด R₀) |
| **constant hazard 0.004-0.006** | **กำจัดคลื่นได้จริง (CV 0.60→0.47, ไม่มี boom) แต่สูญพันธุ์ทุก 9 รัน** = แปลง boom-bust เป็น smooth sub-replacement fade |

→ **คลื่นการตายเป็นอาการ ไม่ใช่สาเหตุ** ระบบอยู่บน **R₀≈1 knife-edge ไม่มี buffer**: sync→boom-bust / de-sync→ตายก่อนสืบพันธุ์ ทั้งคู่จบที่สูญพันธุ์

### 3.3 Foraging access probe (immortal, สวีปความหนาแน่น) → เจอ root cause
| อาหาร/tick | standing | ระยะถึงอาหาร | **sense ได้** | **มื้อ/agent/tick** |
|---:|---:|---:|---:|---:|
| 0 (พืชล้วน) | **2** | 6.8 | **0%** | **0.0001** |
| 45 (crutch) | 2517 | 2.7 | 83% | 0.39 |

**meal rate ∝ การ sense อาหารได้** · `food_signal_at` รับรู้อาหารแค่ในรัศมีสายตา ~4 ช่อง; ที่อาหารเบาบางจริง ระยะ > สายตา → มองไม่เห็น → กินไม่ได้ · **ระบบนิเวศพืชล้วนผลิตอาหารแค่ ~2 ชิ้น** → โลกสมจริงแทบไร้อาหารเข้าถึงได้, อาหารหนาแน่นคือ crutch

### 3.4 อายุขัย / generational overlap (สมมติฐานผู้วิจัย) → unmask ตัวฆ่าจริง
ยืนยัน: รุ่นกลิ้งไปข้างหน้า (founder รุ่น0 ตายที่ tick ~400 ก่อนเหลนเกิด). ทดสอบอายุยืน 600/1200:
| repro_max_age | สูญพันธุ์ | gen0 อยู่ถึง | **%ตายเพราะอด** |
|---:|---|---:|---:|
| 300 (control) | ทุก seed | tick 200 | **8%** |
| 600 | ทุก seed | tick 400 | ~50% |
| 1200 | ทุก seed | tick 1000 | **65-72%** |

อายุยืนทำ founder อยู่นานขึ้นจริง แต่ births ไม่เพิ่ม (crash ก่อน, stragglers ลากยาวไม่สืบพันธุ์ = Allee) · **การค้นพบเด็ด: ยิ่งอายุยืน สาเหตุการตายพลิกจาก "แก่ตาย" เป็น "อดตาย" → lifespan-death บดบัง starvation มาตลอด**

---

## 4. ห่วงโซ่ข้อสรุปที่ปิดสนิท

```
foraging access แย่ (มองอาหารได้แค่ ~4 ช่อง + พืชผลิตน้อย)
        ↓
พลังงานต่ำเรื้อรัง (ใกล้ starvation ตลอด, ต้องใช้ crutch อาหารหนาแน่นกลบ)
        ├─ ประตูสืบพันธุ์ (energy/safety/comfort) ไม่เปิด → R₀≈1 (ไม่มี surplus)
        │       ↓
        │   sync death → boom-bust → crash → Allee → สูญพันธุ์
        │   de-sync death → ตายก่อนสืบพันธุ์ → fade → สูญพันธุ์
        │   (ทุกการจูน demographic แก้ปลายเหตุ → ล้มเหลว)
        └─ (พอเอาเพดานอายุออก) → starvation โผล่เป็นตัวฆ่า 72%
```

**5 เส้นทางอิสระ (fecundity, brake, wave, lifespan, foraging) ลงรากเดียวกัน = เศรษฐกิจพลังงาน/foraging access**

---

## 5. การค้นพบสำคัญ

1. **อาหารไม่เคยจำกัดในสูตรทดลอง** (standing food ~3500 flat) → density brake ไม่มี K ให้เกาะ; แต่นั่นเพราะ **crutch** — เศรษฐกิจสมจริงผลิตอาหารแค่ ~2 ชิ้น
2. **R₀≈1 knife-edge ไม่มี buffer** — fecundity = replacement พอดี ฉะนั้นการจูนการเกิด/การตายแค่ย้ายโหมดความล้มเหลว (boom-bust ↔ fade)
3. **คลื่นการตายเป็นอาการ ไม่ใช่สาเหตุ** — กำจัดได้แต่ไม่ช่วย
4. **lifespan-death บดบัง starvation** — "แก่ตาย 90%" ใน log จริงคือพลังงานต่ำเรื้อรัง; ยืดอายุ → อดตาย 72% (หลักฐานเด็ดว่า energy คือ binding constraint)
5. **foraging access = sensing range << ความเบาบางของอาหาร** — agent มองอาหารไม่เห็นที่ความหนาแน่นสมจริง → กินไม่พอ → ไม่มี surplus

---

## 6. ดัชนีรายงานย่อย 5 ฉบับ (session นี้)

1. [extinction_final_blocker_consolidated](extinction_final_blocker_consolidated_2026-06-27.th.md) — สรุปรวมจากงานเก่าทั้งหมด + ยืนยัน claim ระดับโค้ด
2. [density_brake_experiment](density_brake_experiment_2026-06-27.th.md) — brake หักล้าง (multi-seed): อาหารไม่จำกัด + sync death
3. [lifespan_wave_experiment](lifespan_wave_experiment_2026-06-27.th.md) — คลื่นเป็นอาการ; R₀≈1 knife-edge
4. [foraging_access_keystone_diagnosis](foraging_access_keystone_diagnosis_2026-06-27.th.md) — เจอ root cause: sensing range << ความเบาบาง
5. [lifespan_masks_starvation](lifespan_masks_starvation_2026-06-27.th.md) — อายุขัยบดบัง starvation → energy คือ binding constraint

---

## 7. สถานะ + ขั้นต่อไป (งาน ก: แก้ foraging access จริง)

**ยังไม่ได้ประชากรเสถียร** — แต่ระบุ root cause ชี้ขาดแล้ว (honest negative result เชิงโครงสร้างที่มีค่า). กลไก/telemetry ที่สร้างถูกเก็บไว้เป็นเครื่องมือ (เหมือนที่เก็บ home-fidelity/continuous-repro/stochastic-mortality)

**แผนแก้จริง (ยังไม่ทำ):**
1. **ยกผลผลิตพืช** ให้เป็น standing crop ยั่งยืนที่ sense ได้ (ปรับ plant lifecycle)
2. **เปิด memory-return foraging** (Phase 2 พิสูจน์แล้ว return lift 41×) ใช้ตำแหน่งพืชที่คาดเดาได้ชนะความเบาบาง
3. **(เลือก) แยก food-sensing radius จาก vision** — ทดสอบว่ายก frac_sensing → meal rate
4. **เมื่อ access พอ** → ลด crutch → อาหารคุม K จริง → density brake (สร้างแล้ว) มีจุด converge → ทดสอบ R₀>1 with surplus

**เกณฑ์สำเร็จขั้นถัดไป:** ที่ lvf ต่ำ + drain สมจริง — frac_sensing > 0.5 และ energy เป็นบวกโดยไม่ใช้อาหารหนาแน่นเทียม

**นัยเชิงกลยุทธ์ (ISEF roadmap):** การสูญพันธุ์อาจวางเป็น honest structural negative result (มีคุณค่าวิทยาศาสตร์) แล้วเดินหน้า neuroevolution เป็นผลหลัก — หรือลุยแก้ foraging access ต่อ (เสี่ยง/ลึก แต่เป็นทางเดียวสู่ open-ended evolution)

---

## 8. การทำซ้ำ + verification

- **Tests:** `PYTHONHASHSEED=0 python -m unittest discover -s tests` → **61/61 OK**
- **Compile:** `python -m compileall agents world scripts tests` → OK
- **Byte-identical:** ทุก knob default = ปิด; brake×1.0 exact; constant-hazard else-branch รันโค้ดเดิม (RNG ไม่เปลี่ยน)
- **Reproducibility note:** ซิมไม่ deterministic ข้าม process เว้นแต่ล็อก `PYTHONHASHSEED`; movement RNG ยังไม่ผูก args.seed (n=1 ต่อ seed config — แต่ reproduction RNG ผูก seed จึงได้ความผันแปรเชิงประชากรข้าม seed)
- **drivers:** `scripts/food_value_study_driver.py` (flags ครบ) · batch/probe: `scratchpad/run_batch*.py`, `run_probe.py`, `analyze.py`

> งานทั้งหมดเป็นการทดลองจริง (~40 รัน, multi-seed); กลไกผ่าน 61 unit tests + byte-identical guarantee. ตัวเลขทุกตัวมาจาก dump จริง. โค้ด+รายงานยังเป็น local ยังไม่ commit/push

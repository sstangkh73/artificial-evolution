# แผนงาน ข (ฉบับละเอียด): ทำให้ประชากรเสถียรด้วย de-synchronized death + carrying capacity จริง

**Option ข detailed plan: stabilize the mortal population by combining de-synchronized mortality with a real (depletable) carrying capacity — in the access-fixed, crutch-free world that Option ก produced**

ผู้จัดทำ: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-28
สถานะ: แผน (ยังไม่ลงมือ) · ต่อจาก `option_ga_foraging_access_results_2026-06-28` (งาน ก เสร็จ: access แก้แล้ว, root cause เลื่อนเป็น demographic)
เครื่องมือพร้อม: continuous vision (`food_detection_threshold`), plant economy (`natural_seed_rain` + `initial_plant_population`), real K, density brake (`continuous_repro_food_target`), constant-hazard mortality (`mortality_constant_hazard`), stochastic mortality, home-fidelity, continuous-repro, fecundity/funnel/trajectory telemetry

---

## 1. เป้าหมายและสมมติฐานกลาง

**เป้าหมาย:** ประชากร mortal อยู่รอด **ข้ามหลาย generation (≥10 lifespan, ~30+ รุ่น)** ในโลกที่งาน ก ทำให้ honest แล้ว (อาหารพืชจริง depletable, ไม่มี uniform crutch, access แก้ด้วย continuous vision) โดย **(a) ไม่ boom-bust, (b) มี K จริง (อาหารคุมประชากร), (c) R₀ converge ~1 ที่ K** — ปลดล็อก Phase 6 (วิวัฒนาการจริง)

**สมมติฐานกลาง (H-ข):**
> งาน ก พิสูจน์แล้วว่า **มี carrying capacity จริง** (standing food แปรผกผันกับประชากร ต่างจาก crutch ที่แบน). แคมเปญเดิมล้มเหลวเพราะทดสอบ de-sync death **ในโลกที่อาหารไม่จำกัด** (de-sync เดี่ยว → sub-replacement fade; density brake เดี่ยว → ไม่มี K ให้ converge). **เมื่อรวม de-synchronized death (ลบ death-wave) เข้ากับ K จริง (density-dependent feedback) ในโลก honest → ที่ความหนาแน่นต่ำ อาหารเหลือเฟือ → R₀>1 (ชดเชย fecundity ที่ลดจาก constant hazard); เมื่อเข้าใกล้ K อาหาร/หัวลด → repro throttle → R₀→1 → ประชากรเสถียรแบบ logistic ไม่ boom-bust**

**กลไกเชิงทฤษฎี:** ปัญหาเดิมคือระบบอยู่บน **R₀≈1 knife-edge ไม่มี buffer** (fecundity = replacement พอดี → sync death = boom-bust, de-sync = fade). **density-dependence จาก K จริงคือ buffer ที่หายไป**: ต่ำกว่า K → R₀>1, ที่ K → R₀=1 (logistic). คำถามชี้ขาด = density feedback **แรงและเร็วพอ**จะเอาชนะ (i) fecundity loss จาก constant hazard และ (ii) lag (maturation + starvation delay → delayed-logistic overshoot) หรือไม่ → density brake ช่วยลด lag

**หลักการชี้นำ (ความซื่อสัตย์/ISEF):** ห้ามกลับไปใช้ crutch (flat food, drain÷33) เพื่อบังคับให้รอด. ทุกกลไกต้องเป็น demographic/ecological จริง. negative result ที่ชี้คอขวดถัดไปได้ = ความก้าวหน้า

---

## 2. ภูมิหลัง (หลักฐานจากงาน ก ที่ทำให้ ข เป็นไปได้)

| ข้อค้นพบจาก ก | นัยต่อ ข |
|---|---|
| access แก้แล้ว (continuous vision: starvation 88→1, energy surplus 200–550 บนพืชล้วน) | ตัด confound พลังงาน/foraging ออก → เหลือ demographic ล้วน |
| **K จริงมีแล้ว** (standing food แปรผกผันกับ pop; crutch แบน ~3500) | density brake มี K ให้ converge แล้ว (เดิมไม่มี) |
| residual extinction ตายเพราะ **lifespan_completed (sync cohort) เป็นหลัก** | death-wave คือเป้า de-sync |
| home-fidelity ON → local depletion; OFF → Allee (หาคู่ไม่ได้) | clustering⟂dispersal tension = sub-risk ของ ข (เฟส ข.4) |
| de-sync เดี่ยว (campaign) → fade; brake เดี่ยว → no K | **ต้องรวมในโลกที่มี K จริง** = หัวใจ H-ข |

**บทเรียนสำคัญ:** อย่าทดสอบกลไก demographic แยกเดี่ยวอีก — แคมเปญเดิมทำแล้วล้มทุกตัวเพราะ**ขาด K จริง**. ข จึงทดสอบ **combination ในโลก honest** เป็นหลัก

---

## 3. แผนเป็นเฟส (แต่ละเฟสมี IV/DV/control/metrics/success/failure)

> ลำดับ dependency: ต้องมี **telemetry วินิจฉัย (ข.0)** ก่อน → **ยืนยัน K จริง + ตั้ง baseline (ข.1)** → **de-sync + brake บน K จริง (ข.2 = หัวใจ)** → ถ้าติด Allee → **ข.3** → **integration + multi-seed (ข.4)**

### เฟส ข.0 — สร้าง telemetry วินิจฉัยที่ขาด (precondition)
ก่อนทดลอง ต้องวัดให้ตรงจุด (สกิล log-analysis): การวินิจฉัย demographic ต้องแยก local จาก global และเห็น cohort sync

- **IV:** ไม่มี (สร้างเครื่องมือ)
- **สิ่งที่ต้องเพิ่ม (opt-in, additive, ไม่แตะ RNG/behavior → byte-identical):**
  1. **local food-per-capita** — อาหารต่อหัวในรัศมี home/cluster (แผน ก §5 ทำนาย local depletion; global food/capita หลอกตา)
  2. **age-structure / cohort-synchronization** — histogram อายุ + CV ของ deaths/หน้าต่างเวลา (วัด death-wave โดยตรง)
  3. **R₀-at-density estimator** — ลูกที่รอดถึงวัยเจริญพันธุ์ต่อตัวเมีย แยกตามความหนาแน่น (มี fecundity telemetry แล้ว ต่อยอด)
  4. **K estimator** — food-per-capita ณ จุดที่ births≈deaths (ใช้ตั้ง brake target ใน ข.2)
- **DV/Metrics:** ตัวเลขเหล่านี้อ่านได้จริงใน population_trajectory
- **เกณฑ์สำเร็จ:** telemetry ทำงาน, default byte-identical, tests เขียว
- **โค้ดที่คาดแตะ:** `scripts/run_long_emergence_watch.py` (trajectory block), อาจ helper ใน env (อ่าน state เฉยๆ)

### เฟส ข.1 — ยืนยัน K จริง + ตั้ง demographic baseline (ในโลก honest)
ตั้งฐาน: access fix (continuous vision + seed rain + initial plants) + ไม่มี uniform crutch + drain ที่รอด bootstrap ได้ (จาก ก: drain_mult ~0.1 หรือ body brain ถูกลง) + age-ramp death เดิม (sync) — เพื่อเห็น death-wave/boom-bust ชัดเป็น control

- **IV:** ไม่มี (baseline)
- **DV:** survival, **corr(pop, standing food)** (ยืนยัน K จริง = ลบ), death-wave CV, per-female fecundity, R₀, local vs global food/capita, generation overlap
- **Control:** crutch regime เดิม (flat food) — เทียบให้เห็นว่า K จริงต่างจริง
- **เกณฑ์สำเร็จ:** ยืนยัน corr(pop,standing) เป็นลบชัด (K จริง) + characterize death-wave/Allee เชิงปริมาณ
- **เกณฑ์ล้มเหลว:** ถ้า corr ≈ 0 (อาหารไม่ depletable จริง) → กลับไปตรวจ plant economy/initial plants ก่อน

### เฟส ข.2 — de-synchronized death + density brake บน K จริง (หัวใจของแผน)
**สมมติฐาน:** constant-hazard mortality (ลบ age-wave) + density brake keyed to K จริง → logistic convergence (ไม่ boom-bust, ไม่ fade)

- **IV:**
  - mortality mode: `mortality_constant_hazard` (memoryless, ลบ wave) เทียบ age-ramp (control); กวาด hazard ให้ mean lifespan ใกล้เคียงกัน (แยก "ลบ wave" จาก "อายุสั้นลง")
  - `continuous_repro_food_target` (density brake) ตั้งรอบค่า food/capita ที่ K (จาก ข.0/ข.1); กวาด 0 (off) → calibrated
  - `continuous_repro_base_rate` (กวาดหา R₀>1 ที่ low density แต่ throttle ได้ที่ K)
- **DV:** death-wave CV (ควรลด), **boom-bust amplitude** (peak/trough ratio), survival duration, R₀ vs density (ควรเห็น >1 ที่ต่ำ, →1 ที่ K), standing food คงตัวรอบ K
- **Control:** ข.1 baseline (age-ramp sync, no brake)
- **เกณฑ์สำเร็จ (ชี้ขาดของ ข):** ประชากร**เข้าใกล้ K แล้วคงตัว** (ไม่ fade ไม่ boom-bust) อย่างน้อย ~5–10 lifespan; death-wave CV ลงชัด; R₀ converge ~1 ที่ K
- **เกณฑ์ล้มเหลว:**
  - ยัง fade → constant hazard ตัด fecundity ต่ำกว่า replacement แม้ที่ low density → density buffer ไม่พอ → ไป ข.3 (Allee/fecundity) หรือปรับ hazard/maturation
  - ยัง boom-bust → lag ยาวเกิน brake → ลด lag (เร่ง maturation, brake ไวขึ้น) หรือ K feedback อ่อน
- **โค้ด:** ส่วนใหญ่ใช้ knob ที่มี; อาจปรับ brake ให้ keyed กับ **local** food/capita (จาก ข.0) แทน global

### เฟส ข.3 — คลาย Allee / clustering⟂dispersal (ถ้า ข.2 ติด mate-finding)
**สมมติฐาน (จาก ก):** home-fidelity ON → local depletion; OFF → หาคู่ไม่ได้. ต้องกระจุก "พอจะผสมพันธุ์" แต่ไม่ถึงกับ deplete local

- **IV (เลือกตามผล ข.0 local food/capita):**
  - **elastic home radius** — ขยาย home_radius เมื่อ local food/capita ต่ำ (ออกไปกินไกลขึ้นเมื่อรอบบ้านพร่อง)
  - **forage-trip-then-return** — ออกไปกิน (continuous vision ชี้แหล่งไกล) แล้วกลับ home มาผสมพันธุ์
  - **mate-search radius** — ขยายรัศมีหาคู่ชั่วคราว / temporary breeding aggregation
- **DV:** birth rate ที่ low density, local food/capita (depletion ลดไหม), mate-find success, ยังคง cluster พอผสมพันธุ์ไหม
- **Control:** ข.2 ที่ดีสุด (home-fidelity คงที่)
- **เกณฑ์สำเร็จ:** births ยั่งยืนที่ low density **โดยไม่เกิด local depletion** (local food/capita ไม่ทรุด)
- **เกณฑ์ล้มเหลว:** แก้ depletion แล้วเสีย mate-finding (หรือกลับกัน) → tension เป็น structural → รายงานเป็น honest finding + พิจารณา mate/Allee mechanism อื่น
- **โค้ด:** น่าจะต้องเพิ่มกลไก (elastic radius / trip) ใน `agents/agent.py` home-fidelity block — opt-in, default = พฤติกรรมเดิม

### เฟส ข.4 — integration + drain สมจริง + multi-seed (เกณฑ์ชี้ขาดสุดท้าย)
**สมมติฐาน:** เมื่อ ข.2 (+ข.3) ให้ประชากรเสถียรที่ drain ที่รอด bootstrap → ดันไป **drain สมจริงขึ้น**ด้วยกลไกจริง (ไม่ใช่ crutch): body brain ถูกลง หรือ nest+hearth drain reduction (กลไกในโค้ด: near_nest+hearth ลด drain ~2-4)

- **IV:** body index (brain cost), nest/hearth (scaffolded), drain_mult → ดันสูงสุดที่ยังเสถียร; seeds ≥5
- **DV:** survival ≥10 lifespan, gen depth, K stability, R₀, death-cause mix (starvation ควรเป็น regulator ส่วนน้อย ไม่ใช่ mass killer), boom-bust amplitude — **ทุกอย่างข้าม seeds (mean±CI)**
- **Control:** crutch regime เดิม (สูญพันธุ์)
- **เกณฑ์สำเร็จ (ปลดล็อก Phase 6):** ประชากรอยู่รอด ≥10 lifespan **ทุก seed** ด้วยอาหารพืชล้วน + drain สมจริง(ที่สุดเท่าที่กลไกจริงทำได้) + K เสถียร + ไม่ boom-bust
- **เกณฑ์ล้มเหลว:** เสถียรเฉพาะที่ drain crutch เท่านั้น → honest result: "demographic แก้ได้แต่พลังงาน body-brain ยังเป็นเพดาน" → ระบุคอขวด energy/morphology เป็นชั้นถัดไป

---

## 4. เกณฑ์สำเร็จรวมและ decision gates

| Gate | เงื่อนไขผ่าน | ถ้าไม่ผ่าน |
|---|---|---|
| หลัง ข.0 | telemetry (local food/capita, cohort CV, R₀-by-density, K) อ่านได้, byte-identical | แก้ telemetry ก่อน |
| หลัง ข.1 | corr(pop,standing) ลบชัด (K จริง) + death-wave/Allee วัดได้ | ตรวจ plant economy/initial plants |
| **หลัง ข.2** | **ประชากรคงตัวที่ K ≥5–10 lifespan, CV death ลด, R₀→1 ที่ K** | fade→ข.3/ปรับ hazard·maturation; boom-bust→ลด lag/เร่ง brake |
| หลัง ข.3 | births ยั่งยืน low density, ไม่มี local depletion | tension structural → honest finding |
| **หลัง ข.4** | **รอด ≥10 lifespan ทุก seed, K เสถียร, ไม่ boom-bust, drain สมจริง** | เสถียรเฉพาะ drain crutch → ระบุคอขวด energy/morphology |

**นิยามสำเร็จสุดท้าย:** ประชากรไม่สูญพันธุ์ ≥10 lifespan หลาย seed บนอาหารพืชล้วน + density-regulated K + de-synchronized death ไม่ boom-bust → **ปลดล็อก Phase 6 (mortal + heritable + selection ข้ามรุ่น)**

---

## 5. ความเสี่ยงและการ falsify (สกิล hypothesis-testing)

- **ความเสี่ยงหลัก #1 — R₀ knife-edge ไม่มี buffer แม้มี K:** ถ้า density feedback อ่อน/ช้าเกิน, ต่ำกว่า K ก็ยังไม่ได้ R₀>1 → fade. **Falsify H-ข:** de-sync + K จริง + brake calibrated แล้ว **ยัง fade/boom-bust ทุก seed** → demographic stability ไม่ถึงได้ในโมเดลนี้ → คอขวดเป็น structural (maturation lag / mate-finding / per-female output เพดาน)
- **ความเสี่ยง #2 — lag (delayed logistic):** maturation ~61 ticks + starvation delay → overshoot. บรรเทาด้วย brake ที่ throttle ก่อน overshoot + เร่ง maturation (ทดสอบเป็น IV)
- **ความเสี่ยง #3 — clustering⟂dispersal (Allee):** จาก ก เป็น tension จริง; ข.3 รองรับ แต่ถ้าแก้ทางหนึ่งเสียอีกทาง = structural
- **ความเสี่ยง #4 — constant hazard ตัด fecundity:** memoryless hazard ฆ่าบางตัวก่อนสืบพันธุ์ → R₀↓. ต้องให้ density buffer ที่ low density ชดเชย; ถ้าไม่พอ ลอง age-ramp ที่ onset ต่ำ (de-sync แต่ไม่ memoryless) เป็นทางสายกลาง
- **กับดักที่ต้องเลี่ยง:** กลับไปใช้ flat-food/drain÷33 crutch เพื่อบังคับรอด (กลบปัญหา demographic — เคยพลาดมาแล้วทั้งแคมเปญ)

**กรอบหลักฐานที่จะรายงาน:** Evidence For / Against / Alternative / Missing / Confidence — ต่อทุกเฟส (เหมือนงาน ก)

---

## 6. เครื่องมือ: พร้อมแล้ว vs ต้องสร้าง

**พร้อม (opt-in, byte-identical):** continuous vision (`food_detection_threshold`+`vision_horizon`), `food_sensing_radius`, plant economy (`natural_seed_rain`, `initial_plant_population`, `seed_initial_plants`), `memory_return_enabled`, density brake (`continuous_repro_food_target`), `mortality_constant_hazard`, stochastic mortality (`mortality_hazard`,`mortality_onset_fraction`), home-fidelity, continuous-repro, starvation-death; telemetry: fecundity, funnel, population_trajectory (standing/food_per_capita/frac_sensing/multi-radius), `ga_probe/ga_batch/ga4_analyze` harness

**ต้องสร้าง (ข.0, opt-in/additive):** local food-per-capita telemetry; age-structure + cohort-sync (deaths/window CV); R₀-by-density estimator; K estimator. (ข.3 อาจต้องเพิ่ม elastic-home / forage-trip / mate-search — opt-in, default เดิม)

**perf note:** continuous vision เป็น O(n_food)/perception (ช้า ~2× ที่ standing food สูง). ถ้ารัน multi-seed ยาว/ประชากรใหญ่ ควร optimize เป็น spatial-grid + early-stop ก่อน (หรือใช้ `food_sensing_radius` เป็น proxy เร็วในสวีปกว้าง แล้วยืนยันด้วย continuous)

---

## 7. ลำดับลงมือที่แนะนำ
1. **ข.0** telemetry (local food/capita, cohort CV, R₀-by-density, K) + tests
2. **ข.1** baseline honest-world + ยืนยัน K จริง (immortal ยืนยัน access; mortal วัด demographic)
3. **ข.2** หัวใจ: สวีป mortality mode × brake target × repro rate บน K จริง (multi-seed ตั้งแต่ต้นในจุดที่ดู promising)
4. **ข.3** ถ้า ข.2 ติด Allee → คลาย clustering⟂dispersal
5. **ข.4** integration + ดัน drain สมจริง (cheaper brain / nest-hearth) + multi-seed ชี้ขาด

> scope: ข.0–ข.1 เตรียม; ข.2 คือบทพิสูจน์หลัก (de-sync + K จริง); ข.3 รองรับ Allee; ข.4 คือเกณฑ์ชี้ขาดที่ปลดล็อก Phase 6. ถ้า ข.2 ผ่าน = ใกล้ open-ended evolution ที่สุดเท่าที่เคย. ถ้าไม่ผ่าน = honest negative ที่ระบุได้ว่าคอขวดคือ structural demographic (lag / mate / per-female output) — ก้าวหน้าทั้งสองทาง

> หมายเหตุความต่อเนื่อง: แผนนี้โจมตี **คอขวดที่งาน ก เลื่อนมา** (synchronized lifespan death + Allee บน R₀≈1 knife-edge) ในโลกที่ access แก้แล้ว — เป็นครั้งแรกที่ทดสอบ demographic stability ใน economy ที่ honest จริง (มี K, ไม่มี crutch) ซึ่งเป็นเงื่อนไขที่แคมเปญเดิมไม่เคยมี

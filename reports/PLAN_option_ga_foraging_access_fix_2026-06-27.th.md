# แผนงาน ก (ฉบับละเอียด): แก้ foraging access เพื่อสร้าง reproductive surplus จริง

**Option ก detailed plan: fix foraging access so the energy economy yields a real reproductive surplus (escape the R₀≈1 knife-edge)**

ผู้จัดทำ: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-27
สถานะ: แผน (ยังไม่ลงมือ) · ต่อจาก root-cause ที่ยืนยันแล้วใน `SESSION_REPORT_extinction_investigation_2026-06-27`
เครื่องมือพร้อม: telemetry `frac_sensing_food` / `mean_food_dist` / `food_per_capita` / `standing_food` + density brake (สร้างแล้ว session ก่อนหน้า)

---

## 1. เป้าหมายและสมมติฐานกลาง

**เป้าหมาย:** ให้ประชากร mortal อยู่รอดข้ามหลาย lifespan โดย **ไม่พึ่งอาหารหนาแน่นเทียม (crutch)** — เป็น precondition ของ Phase 6

**สมมติฐานกลาง (H-ก):**
> การสูญพันธุ์มีรากที่ **foraging access**: agent รับรู้อาหารได้แค่รัศมีสายตา ~4 ช่อง และระบบนิเวศพืชผลิต standing food น้อยมาก (~2) → ที่ความหนาแน่นสมจริง agent หาอาหารไม่เจอ → พลังงานต่ำเรื้อรัง → (a) ประตูสืบพันธุ์ไม่เปิด (R₀≈1) และ (b) อดตาย. **ถ้าทำให้ agent หาอาหารจากแหล่งที่คาดเดาได้ (พืช) ด้วยความจำ + การรับรู้ที่เหมาะ → พลังงานเกินดุล → R₀>1 with surplus → ประชากรเสถียร**

**หลักการชี้นำ (สำคัญต่อความซื่อสัตย์/ISEF):** ทุกการแก้ต้องทำให้โลก**สมจริงขึ้น ไม่ใช่เพิ่ม crutch** — ใช้กลไกที่สัตว์จริงใช้และโปรเจกต์พิสูจน์แล้ว:
- **พืช = patch อาหารที่คงที่และงอกใหม่** (predictable resource patches)
- **ความจำเชิงพื้นที่** (Phase 2 พิสูจน์แล้ว return lift 41×)
- **การรับรู้อาหารระยะไกลกว่าสายตา = กลิ่น** (realistic)

---

## 2. ภูมิหลัง (สรุป root cause ที่ยืนยันแล้ว)

dose-response (immortal, สวีปความหนาแน่น): meal rate ∝ สัดส่วนที่ sense อาหารได้

| อาหาร/tick | standing food | ระยะถึงอาหาร | sense ได้ | มื้อ/agent/tick |
|---:|---:|---:|---:|---:|
| 0 (พืชล้วน) | **2** | 6.8 | **0%** | **0.0001** |
| 45 (crutch) | 2517 | 2.7 | 83% | 0.39 |

กลไก (โค้ด): `food_signal_at` (env.py:846) รวมเฉพาะอาหารในรัศมีสายตา (`_effective_vision` ~4); กิน = ยืนทับเป๊ะ; เดิน 1 ช่อง/tick ตาม gradient. หลักฐานยืนยันว่า energy คือ binding constraint: ยืดอายุขัย → death พลิกจากแก่ตาย 92% เป็นอดตาย 72%

---

## 3. แผนเป็นเฟส (แต่ละเฟสมี IV/DV/control/เกณฑ์)

> ลำดับตาม dependency: ต้องมี**อาหารให้เจอก่อน (ก.1)** → จึง**จำและกลับไปได้ (ก.2)** → ปรับการรับรู้ (ก.3) → รวมแล้วถอด crutch (ก.4)

### เฟส ก.1 — ยกผลผลิตพืชให้เป็น standing crop ที่ sense ได้ (keystone ของ keystone)

**สมมติฐาน:** พืชที่ออกผลถี่ขึ้น/ผลอยู่นานขึ้น จะสร้าง standing crop ที่ clustered อยู่ที่ตำแหน่งพืช (คาดเดาได้) มากพอให้ frac_sensing สูงขึ้น โดยไม่ต้องโปรยอาหารสุ่มทั้งแมพ

- **IV:** plant lifecycle params (`plant_fruiting_interval_multiplier`, `plant_fruiting_chance_multiplier`, `plant_growth_rate_multiplier`, จำนวน seed/plant เริ่มต้น, fruit decay/persistence)
- **DV:** standing plant-food, frac_sensing_food, mean_food_dist, meal rate (immortal probe), การกระจุกของอาหาร (ที่พืช vs uniform)
- **Control:** lvf 0 ปัจจุบัน (standing ~2)
- **Metrics/เกณฑ์สำเร็จ:** standing plant-food พอให้ frac_sensing > 0.5 รอบ patch พืช, **ยั่งยืน** (ไม่ใช่ spike แล้วหมด), และอาหาร**กระจุกที่พืช** (ไม่ใช่ทั้งแมพ = ไม่ใช่ crutch)
- **เกณฑ์ล้มเหลว:** ต้องโปรยทั้งแมพจึงจะพอ (= crutch), หรือ standing crop ไม่ยั่งยืน
- **โค้ดที่คาดว่าแตะ:** `world/environment.py` `_update_plant_lifecycle` / `_maybe_fruit_plant` / fruit decay; อาจเพิ่ม knob ผลผลิต (opt-in)
- **ความเสี่ยง:** ยกมากไป = crutch รูปแบบใหม่; ต้อง calibrate ให้อาหาร**กระจุกและจำกัด** (เพื่อให้ memory + competition ทำงาน)

### เฟส ก.2 — memory-return foraging (ใช้แหล่งพืชที่คาดเดาได้)

**สมมติฐาน:** เมื่ออาหารกระจุกที่พืช (ก.1) agent ที่จำตำแหน่ง reward แล้วกลับไป จะกินได้สม่ำเสมอแม้ความหนาแน่นรวมต่ำ — ชนะการเดินสุ่ม

- **IV:** memory-return เปิด/แรง, อายุความจำ (มี `remembered_food` + `_move_toward` ที่ `agent.py:877` แต่ fire เฉพาะตอน signal=0 — ต้องตรวจว่าทำงานจริง)
- **DV:** return rate ไป patch พืช, meal rate ที่อาหารเบาบาง-แต่กระจุก, energy เฉลี่ย
- **Control:** ก.1 ที่ดีสุด แต่ปิด memory-return
- **เกณฑ์สำเร็จ:** meal rate ที่ความหนาแน่นต่ำ (ก.1) ใกล้เคียง crutch โดยอาศัย return ไป patch; energy เป็นบวก
- **เกณฑ์ล้มเหลว:** memory ไม่ fire / patch ถูกกินหมดเร็วกว่า re-fruit / return ไม่ช่วย
- **โค้ดที่คาดว่าแตะ:** ตรวจ/ปรับ `_move_toward(remembered_food)` ใน `agents/agent.py`; อาจให้ memory-return มี priority สูงขึ้นเมื่ออิ่มพอจะวางแผน

### เฟส ก.3 — แยก food-sensing radius จาก vision (กลิ่น, เลือกทำ)

**สมมติฐาน:** ให้รับรู้แหล่งอาหารไกลกว่าสายตา (เหมือนกลิ่น) จะยก frac_sensing → meal rate ที่อาหารเบาบาง (ตรงกับ dose-response ที่วัดไว้)

- **IV:** `food_sensing_radius` knob (> vision; opt-in)
- **DV:** frac_sensing → meal rate ที่ความหนาแน่นต่ำ
- **เกณฑ์สำเร็จ:** dose-response ยืนยันว่าเพิ่ม radius → meal rate ขึ้นแบบคาดได้ (พิสูจน์ไม่มีคอขวดซ่อนอื่น เช่น เดินไปไม่ถึง)
- **โค้ดที่คาดว่าแตะ:** `food_signal_at` radius ใน `_move_toward_food_signal` (`agents/agent.py:911`) ให้ใช้ knob แทน vision; default = vision (byte-identical)
- **หมายเหตุ:** ทำเป็นทางเลือก — ถ้า ก.1+ก.2 พอแล้วอาจไม่ต้อง; ถ้าทำ ควร justify เชิงชีววิทยา (กลิ่น) เพื่อ ecological validity

### เฟส ก.4 — ถอด crutch + integration test (เกณฑ์ชี้ขาด)

**สมมติฐาน:** เมื่อ access พอ (ก.1-ก.3) ที่อาหารสมจริง (ไม่มี uniform crutch) + drain สมจริง → energy เกินดุล → ประตูสืบพันธุ์เปิด → R₀>1; และอาหารจะ**ถูกบริโภคจนจำกัด** เมื่อประชากรมาก → starvation คุม K จริง → density brake (สร้างแล้ว) มีจุด converge → ประชากรเสถียร

- **IV:** ถอด lvf (→ 0 หรือต่ำ), drain → สมจริง, เปิด density brake (food target)
- **DV:** ประชากรอยู่รอด (extinct?), standing food **ลดเมื่อประชากรมาก** (มี K จริง), R₀, lifetime fecundity, death reason (starvation ควรเป็น regulator ไม่ใช่ mass killer), gen overlap
- **Control:** crutch regime ปัจจุบัน (สูญพันธุ์)
- **เกณฑ์สำเร็จ (ชี้ขาด):** ประชากรอยู่รอด > หลาย lifespan โดยไม่มี uniform crutch; standing food แปรผกผันกับประชากร (logistic K); R₀ converge ~1 ที่ K โดยไม่ boom-bust
- **เกณฑ์ล้มเหลว:** ยังสูญพันธุ์แม้ access ดีขึ้น → root cause ยังไม่ครบ (กลับไป diagnose ชั้นถัดไป)

---

## 4. เกณฑ์สำเร็จรวมและ decision gates

| Gate | เงื่อนไขผ่าน | ถ้าไม่ผ่าน |
|---|---|---|
| หลัง ก.1 | frac_sensing > 0.5 จากพืช, ยั่งยืน, ไม่ใช่ crutch | ลอง ก.3 (sensing) ก่อน หรือ rethink plant model |
| หลัง ก.2 | meal rate พอที่ energy เป็นบวก ที่ความหนาแน่นต่ำ | เพิ่ม ก.3 |
| หลัง ก.4 | **ประชากรอยู่รอด + K จริง + ไม่ boom-bust** | diagnose ชั้นถัดไป (mate-finding? local depletion? social gates?) |

**นิยามสำเร็จสุดท้าย:** ประชากรไม่สูญพันธุ์เกิน ~10 lifespan โดยใช้อาหารพืชล้วน (ไม่มี uniform crutch) + drain สมจริง → ปลดล็อก Phase 6

---

## 5. ความเสี่ยงและการ falsify (hypothesis-testing skill)

- **ความเสี่ยงหลัก:** แม้ access ดีขึ้น อาจเจอคอขวดชั้นถัดไป (mate-finding ที่ความหนาแน่นต่ำ = Allee; local food depletion ที่ home cluster; social gates). แผนรองรับด้วย decision gate ที่ ก.4
- **Local depletion hypothesis (จากข้อมูล lifespan):** home-fidelity ทำ agent กระจุก → อาจกินอาหารรอบ cluster หมดเร็วกว่า re-fruit แม้ standing food รวมสูง → ต้องวัด **local** food-per-capita ไม่ใช่แค่ global (เพิ่ม telemetry ได้)
- **สิ่งที่จะ falsify H-ก:** ถ้ายก plant productivity + memory + sensing จน frac_sensing สูงและ energy เกินดุลแล้ว**ยังสูญพันธุ์** → foraging access ไม่ใช่ root เดียว (กลับไปดู mate/social)
- **กับดักที่ต้องเลี่ยง:** การ "แก้" ด้วยการเพิ่มอาหาร/ลด drain แบบ crutch (เคยทำแล้ว — กลบปัญหา ไม่แก้)

---

## 6. เครื่องมือที่พร้อมแล้ว (จาก session ก่อนหน้า)
- telemetry: `frac_sensing_food`, `mean_food_dist`, `standing_food`, `food_per_capita` (ใน population_trajectory)
- density brake: `continuous_repro_food_target` (รอ K จริงจาก ก.4)
- mortality modes: onset / constant-hazard (สำหรับคุมการตายเมื่อถึง ก.4)
- driver: `scripts/food_value_study_driver.py` + probe `scratchpad/run_probe.py` + `analyze.py`

## 7. ลำดับลงมือที่แนะนำ
1. **ก.1** plant productivity (วัดด้วย immortal probe — เร็ว, แยก access จากการตาย)
2. **ก.2** memory-return (immortal probe ต่อ)
3. **ก.3** sensing radius (ถ้า gate ก.2 ไม่ผ่าน)
4. **ก.4** integration mortal multi-seed (เกณฑ์ชี้ขาด)
5. ระหว่างทาง: ถ้าพบ local-depletion → เพิ่ม local food-per-capita telemetry

> หมายเหตุ scope: ก.1-ก.3 เป็นการ unblock; ก.4 คือบทพิสูจน์. ถ้า ก.4 ผ่าน = ปลดล็อก Phase 6 (วิวัฒนาการจริง). ถ้าไม่ผ่าน = honest negative result ที่ระบุคอขวดชั้นถัดไปได้ ซึ่งก็เป็นความก้าวหน้า

# รายงานวินิจฉัย (เริ่มงาน ก): คอขวด foraging access — รากของการสูญพันธุ์ที่แท้จริง

**Foraging-access keystone diagnosis: sensing range << food sparsity, and a near-barren plant economy**

ผู้วิจัย: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-27
สถานะ: วินิจฉัยคอขวดด้วยการวัดตรง (dose-response ชัด) · เสนอแผนแก้เชิงโครงสร้าง · **ยังไม่ได้แก้** (kickoff)
ต่อจาก: `lifespan_wave_experiment_2026-06-27` (คลื่นไม่ใช่สาเหตุ; R₀≈1 knife-edge → ต้องสร้าง reproductive surplus ที่ราก)

---

## บทคัดย่อ
รายงานก่อนหน้าปิดทุกทางฝั่ง demographic (brake/de-sync) และสรุปว่าต้องสร้าง **reproductive surplus ที่ราก** = เศรษฐกิจอาหารที่ foraging ไม่เป็นคอขวด. งานนี้วินิจฉัย foraging access ด้วยการวัดตรง: เพิ่ม telemetry (ระยะถึงอาหารใกล้สุด + สัดส่วน agent ที่ sense อาหารได้ในรัศมีสายตา) แล้วกวาดความหนาแน่นอาหาร. **พบ 2 ชั้น:** (1) **meal rate ผูกกับ "sense อาหารได้หรือไม่" เกือบสมบูรณ์** — `food_signal_at` รับรู้อาหารแค่ในรัศมีสายตา (~4 ช่อง Manhattan, ถ่วง 1/d²); ที่อาหารเบาบาง ระยะถึงอาหารเฉลี่ย (6.8) > รัศมีสายตา → **0% ของ agent sense อาหารได้ → กินแทบเป็นศูนย์ (0.0001 มื้อ/agent/tick)**; (2) **ระบบนิเวศพืชล้วนผลิต standing food แค่ ~2 ชิ้นทั้งโลก** — โลก "สมจริง" (ไม่มีอาหารหนาแน่นเทียม) แทบไม่มีอาหารเข้าถึงได้เลย จึงต้องพึ่ง low-value-food เป็น crutch. **ข้อสรุป: คอขวดคือ agent มองอาหารได้แค่ระยะสั้น + พืชผลิตอาหารน้อย/ไม่ยั่งยืน → ที่ความหนาแน่นสมจริง agent หาอาหารไม่เจอ → อดตาย/ไม่มี surplus. นี่คือ root cause ที่แท้จริงของห่วงโซ่ทั้งหมด (Phase 5 hunger confound, births=0, R₀<1, สูญพันธุ์)**

---

## 1. หลักฐานเชิงตัวเลข (dose-response)
วัดที่ immortal (agent หิวตลอด → forage ตลอด, แยก access ออกจากการตาย), drain 1.0, body 14, 1500 ticks, world 100×100:

| low-value-food/tick | standing food | ระยะถึงอาหารเฉลี่ย | **สัดส่วน sense ได้ (≤4)** | **มื้อ/agent/tick** |
|---:|---:|---:|---:|---:|
| 0 (พืชล้วน) | **2** | 6.8 | **0.00** | **0.0001** |
| 5 | 534 | 7.4 | 0.18 | 0.0247 |
| 15 | 1270 | 4.9 | 0.45 | 0.1057 |
| 45 (crutch) | 2517 | 2.7 | 0.83 | 0.3887 |

**meal rate ∝ สัดส่วนที่ sense อาหารได้** เกือบเป็นเส้นตรง (0.00→~0, 0.83→0.39) → **"sense ไม่ได้ = กินไม่ได้"** ยืนยันคอขวดคือระยะการรับรู้อาหาร เทียบกับความเบาบาง

---

## 2. กลไก (อ่านจากโค้ดจริง)
- **การกิน** (`agent.py:1052`, `env.consume_food`): กินเฉพาะอาหารที่**ยืนทับเป๊ะ** (self.x, self.y)
- **การหาอาหาร** (`agent.py:910 _move_toward_food_signal`): เดิน 1 ช่อง/tick ไปทาง `food_signal_at` ที่สูงกว่า
- **สัญญาณอาหาร** (`env.py:846 food_signal_at`): `Σ energy/(dist+1)²` เฉพาะอาหารใน**รัศมีสายตา** (`_effective_vision` ~3-5, กลางคืนหาร 2)
- **ผล:** ถ้าไม่มีอาหารในรัศมีสายตา → signal = 0 → gradient แบน (`minimum_improvement` ไม่ถึง) → agent ไม่มีทิศ → เดินสุ่ม → เจออาหารโดยบังเอิญเท่านั้น → ที่อาหารเบาบาง ระยะ > สายตา จึงเจอแทบไม่ได้
- **การกระจายอาหาร** (`env.py:2575 _spawn_low_value_food`): uniform random ทั้งแมพ — ไม่ช่วยให้คาดเดาตำแหน่งได้
- **พืช** (ecology): ผลิต standing food น้อยมาก (~2) ในคอนฟิกนี้ — อาหารพืชถูกกินเร็ว/ออกผลห่าง จึงไม่สะสมเป็น standing crop ที่ sense ได้

---

## 3. ทำไมนี่คือ root cause ที่แท้จริง
ห่วงโซ่ปัญหาทั้งหมดของโปรเจกต์ลงรากที่นี่:
```
พืชผลิตอาหารน้อย + agent มองอาหารได้แค่ ~4 ช่อง
        ↓
ที่ความหนาแน่นสมจริง: หาอาหารไม่เจอ (sense 0%)
        ↓
ต้องใส่อาหารหนาแน่นเทียม (lvf 45) เป็น crutch เพื่อให้กินได้
        ↓
crutch ทำให้ standing food คงที่ ~3500 ไม่ลดตามประชากร → ไม่มี K จริง (รายงาน density-brake)
        ↓
energy economy ต้องใช้ drain เทียม → R₀ แตะแค่ replacement (ไม่มี surplus)
        ↓
ทุกการจูน demographic ล้มเหลว → สูญพันธุ์
```
> เดิมเข้าใจว่า "อาหารไม่ใช่ปัญหา (เหลือเพียบ)" — จริง **แต่อาหารที่เหลือคือ crutch เทียม**; เศรษฐกิจอาหาร**สมจริง**ผลิตอาหารเข้าถึงได้แค่ ~2 ชิ้น = ขาดแคลนเข้าถึงรุนแรง

---

## 4. แผนแก้เชิงโครงสร้าง (prioritized — งานถัดไป)
เป้าหมาย: ให้ **เศรษฐกิจอาหารสมจริง (ไม่มี crutch) เลี้ยงประชากรที่มี surplus** โดย agent หาอาหารได้จาก**แหล่งที่คาดเดาได้** ไม่ใช่ความบังเอิญ

1. **[หลัก] ยกผลผลิตพืชให้เป็น standing crop ที่ยั่งยืน** — ปรับ plant lifecycle (fruiting interval/biomass/density) ให้พืชเป็นแหล่งอาหารคงที่ที่ออกผลซ้ำ → มี standing food พอให้ sense ได้ โดยไม่ต้องใช้ random crutch
2. **[หลัก] เปิด memory-based return foraging จริง** — โปรเจกต์พิสูจน์ reward-place memory แล้ว (Phase 2, return lift 41×); ให้ agent กลับไปแหล่งพืชที่จำได้แทนเดินสุ่ม → ใช้ความ"คาดเดาได้"ของพืช (fixed location) ชนะความเบาบาง — โค้ดมี `remembered_food` แล้ว (`agent.py:877`) ต้องตรวจว่าทำงานเมื่อ signal=0 หรือไม่
3. **[เสริม] แยก food-sensing radius ออกจาก vision** — เพิ่ม knob ให้รับรู้แหล่งอาหาร (กลิ่น/ระยะไกล) กว้างกว่าสายตา; ทดสอบว่ายก frac_sensing → meal rate ที่อาหารเบาบางได้ (ตรงกับ dose-response)
4. **[ผล] เมื่อ access พอแล้ว** → ลด crutch (lvf↓, drain→สมจริง) → อาหารคุม K จริง → density brake (สร้างแล้ว) มีจุด converge → ทดสอบ R₀>1 with surplus

**เกณฑ์สำเร็จขั้นถัดไป:** ที่ lvf ต่ำ/0 + drain สมจริง — frac_sensing > 0.5 และ meal rate พอให้ energy เป็นบวก โดยไม่ใช้อาหารหนาแน่นเทียม

---

## 5. สิ่งที่เพิ่ม (telemetry, additive ไม่กระทบ behavior/RNG)
`population_trajectory` เพิ่ม `mean_food_dist` + `frac_sensing_food` (sample 40 agents/200 ticks) — วัด foraging access โดยตรง; ใช้เฝ้าทุก run ของงาน ก

## 6. กรอบหลักฐาน
| | |
|---|---|
| **Supporting** | dose-response: meal rate ∝ frac_sensing (0.00→0.0001, 0.83→0.39); โค้ด food_signal_at จำกัดที่รัศมีสายตา |
| **Alternative ที่ตรวจ** | "อาหารไม่พอ" (เดิมว่าไม่ใช่) — จริงสำหรับ crutch แต่เศรษฐกิจสมจริงผลิตแค่ ~2 = ขาดแคลนเข้าถึง |
| **Missing** | ทดสอบว่ายก plant productivity / sensing radius / memory-return แก้ได้จริงไหม (งานถัดไป) |
| **Confidence** | "คอขวดคือ sensing range << ความเบาบาง + พืชผลิตน้อย" = **สูง** (วัดตรง) · "แก้ได้ด้วย plant productivity + memory" = **ปานกลาง** (ต้องทดลอง) |

## 7. การทำซ้ำ
```bash
# probe สวีปความหนาแน่น (immortal, วัด access)
python scripts/food_value_study_driver.py --model v2 --ticks 1500 --body 14 --population 50 \
  --drain-mult 1.0 --food-energy-mult 1 --world 100 --low-value-food 0 --dump probe.json
# อ่าน mean_food_dist / frac_sensing_food ใน population_trajectory
```
batch: `scratchpad/run_probe.py`

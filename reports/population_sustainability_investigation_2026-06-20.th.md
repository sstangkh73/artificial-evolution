# รายงานวิจัย: ทำไมประชากรอยู่รอดเองข้ามรุ่นไม่ได้ (และต้องแก้เชิงโครงสร้างอย่างไร)

**Why the population cannot self-sustain across generations — a structural population-dynamics investigation**

ผู้วิจัย: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-20
สถานะ: root-cause ครบ · ยังไม่ได้ประชากรเสถียร (negative result เชิงวินิจฉัย) · เสนอทางแก้เชิงโครงสร้าง
commit เครื่องมือ: `e34f375`, `5cadd55`, `504b22c`, `87597de` (knob/telemetry ทั้งหมด default-neutral, v1 byte-identical)

---

## บทคัดย่อ
เป้าหมาย: ประชากร mortal ที่ **ไม่สูญพันธุ์** ไหลต่อเนื่องไม่ว่ารันนานแค่ไหน (precondition ของ Phase 6 / วิวัฒนาการ) งานนี้ใช้ reproduction-funnel + การทดลองยาว ~18 ชุด root-cause พบว่า: พลังงานและ durability **แก้แล้ว**; กำแพงคือ **กระจุกของด่านสังคม/อารมณ์** (funnel: low_safety 0.83, short_pair_bond 0.76, low_comfort 0.72, ... → "ready" เพียง 8%) รากลึก = ทั้งชั้น settlement/social (รัง, การส่งต่ออาหาร) ถูกปิด → agent ไม่เกาะกลุ่ม → social_buffer≈0 → safety ค้าง ระบบถูกบีบระหว่าง **Allee** (เบาบาง→หาคู่ไม่ได้) กับ **boom-bust** (หนาแน่น→cohort รุ่นเดียวแก่ตายพร้อมกัน) **ไม่มีช่องเสถียร** การจูนทุกแบบไปได้ถึง gen ~6 แล้วสูญพันธุ์ และโหมดสืบพันธุ์ต่อเนื่อง (logistic) ที่สร้างใหม่ก็ยังติด mate-finding **ข้อสรุป: เป็นปัญหาพลวัตประชากรเชิงโครงสร้างที่ต้องออกแบบระบบ clustering↔reproduction↔mortality ร่วมกัน ไม่ใช่จูนพารามิเตอร์**

---

## 1. คำถามและภูมิหลัง
ก่อนหน้านี้ปลดล็อก: พลังงาน (regime เกินดุล), durability (body มีเกราะ) → เกิด births ครั้งแรก แต่ประชากรยัง**สูญพันธุ์เสมอ** คำถาม: ทำไมประชากรถึงไม่ self-sustain และต้องแก้ตรงไหน?

## 2. วิธีการ
- **reproduction funnel**: นับสัดส่วนการถูกบล็อกของแต่ละด่านใน `can_reproduce` ตลอดทุก adult-female-check
- **การทดลองยาว**: body 38/14, regime เกินดุล (drain÷20 + food×50), อาหารหนาแน่น, mortal 8000–15000 ticks, วัด max_generation + วิถีประชากร
- **knob ที่ทำให้ปรับได้** (default-neutral): เกณฑ์สืบพันธุ์ (safety/comfort/streak/litter/max_age), founder_age_spread, ชั้น scaffolded (nest/food-share), โหมดสืบพันธุ์ต่อเนื่อง, ขนาดโลก

## 3. ผลการทดลอง (สรุปแคมเปญ)

### 3.1 Funnel — กำแพงคือด่านสังคม/อารมณ์
อิ่มจริง (hunger 0): low_safety **0.83** · short_pair_bond 0.76 · low_comfort 0.72 · short_safety_window 0.70 · mate_stressed/no_mate ~0.45 · **energy/durability 0.08** · **ready เพียง 8%**
→ แต่ละด่านบล็อก ~70-83% และต้องผ่าน**พร้อมกันทั้งหมด** = สำเร็จ 8% = ต่ำกว่าทดแทน ("แผลเล็กหลายจุดต่อกัน")

### 3.2 รากของด่านสังคม — ไม่เกาะกลุ่ม
`safety = 0.50 + safe_area(0.12) + social_buffer + ... − fear(0.08)`; `social_buffer` ต้องมีพวก ~5 ตัวรอบข้าง แต่ทั้งชั้น settlement/social (`scaffolded_*_enabled`) ปิดเป็น default และไม่เคยถูกเปิด → agent forage กระจาย ไม่เกาะกลุ่ม → social_buffer≈0 → safety ค้าง 0.53 (ใต้เกณฑ์ 0.66)

### 3.3 ตารางการทดลอง (ทุกชุด → สูญพันธุ์)
| เงื่อนไข | max gen | ผล |
| --- | ---: | --- |
| ประตูปกติ (energy+durability แก้แล้ว) | 1–2 | สูญพันธุ์ |
| ผ่อนประตูปานกลาง + litter2 + life300 | 3 | สูญพันธุ์ |
| **สูตรรวม (carrying cap + ผ่อน + litter2)** | **6** | สูญพันธุ์ (~85% ทดแทน) |
| ผ่อนหนัก + litter3 | 2 | boom→250→crash |
| max_age 600 | 3 | สูญพันธุ์ (อายุไม่ใช่คอขวด) |
| เปิด scaffolded (รัง+food-share) | 4 | สร้างรัง 32, births↑ แต่สูญพันธุ์ |
| เริ่มหนาแน่น pop 120 | 1 | boom→250→crash |
| **continuous logistic repro** | 1–2 | births น้อยมาก (หาคู่ไม่เจอ) |
| โลกเล็ก 30×30 + continuous | 2 | สูญพันธุ์ |

### 3.4 การบีบ 2 ด้าน (ไม่มีช่องเสถียร)
- **Allee** (เบาบาง): หาคู่/เกาะกลุ่มไม่ได้ → สืบพันธุ์ ~75-85% ทดแทน → จางช้าๆ
- **boom-bust** (หนาแน่น): ประตูเปิดพร้อมกัน → cohort รุ่นเดียว → แก่ตายพร้อมกันที่ MAX_AGE → crash

### 3.5 continuous mode (โครงสร้างใหม่) ยังไม่พอ
สร้างโหมดสืบพันธุ์แบบ logistic (prob ต่อ tick = base × readiness × (1−crowding), stochastic) เพื่อ de-synchronize + คุม overshoot — แต่ births น้อยมาก (12–25) เพราะยังติด **mate requirement** ในประชากรเบาบาง → ยืนยันว่า **clustering/mate-finding คือคอขวดที่ลึกสุด**

## 4. อภิปราย — รากที่แท้จริง
ปัญหาไม่ใช่ค่าพารามิเตอร์ตัวใดตัวหนึ่ง แต่เป็น **การคัปปลิงของ 4 ระบบ**:
```
การเคลื่อนที่ (forage→กระจาย) ⟂ การจับคู่ (ต้องอยู่ใกล้กัน)
        ↓                              ↓
ไม่เกาะกลุ่ม → safety ต่ำ + หาคู่ไม่เจอ → สืบพันธุ์ต่ำ (Allee)
        ↑                              ↓
ถ้าเกาะกลุ่ม+ประตูเปิดพร้อมกัน → cohort sync → แก่ตายพร้อมกัน (boom-bust)
```
agent ต้อง**ก่อตัวและรักษากลุ่มผสมพันธุ์ที่เสถียร** แต่พฤติกรรมหลัก (forage) ทำให้กระจาย และเมื่อเกาะกลุ่มสืบพันธุ์ก็เป็นพัลส์ที่ตายพร้อมกัน

## 5. ทางแก้เชิงโครงสร้าง (โครงการถัดไป — ออกแบบ ไม่ใช่จูน)
ต้องออกแบบ **clustering ↔ reproduction ↔ mortality ร่วมกัน** ให้เกิดพลวัต logistic ที่เสถียร:
1. **แรงเกาะกลุ่ม/home fidelity จริง** — ให้ agent (ตอนอิ่ม) กลับ/อยู่กับกลุ่ม-รังแทนเร่ร่อน → social_buffer + คู่พร้อมเสมอ (แก้ Allee + safety)
2. **สืบพันธุ์ต่อเนื่อง density-dependent** (โหมด continuous ที่สร้างไว้แล้ว) + จูน base rate ให้ R₀ มากกว่า 1 เมื่อมีกลุ่ม → births กระจายเวลา (แก้ boom-bust)
3. **de-synchronize mortality** — เมื่อ births ต่อเนื่อง อายุจะกระจายเอง (ไม่ต้อง founder_age_spread ที่ทำแย่ลง)
4. **อาหาร scale กับประชากร + perf fix `food_signal_at` O(n)→grid** — ยก carrying capacity ให้มีช่องเสถียร
> ทั้ง 4 ต้องทำพร้อมกัน เพราะมัน couple กัน — แก้ทีละตัว (ที่ทำมา) จึงชน wall ตัวถัดไปเสมอ

## 6. ข้อจำกัด
- n=1 deterministic (seed ไม่กระทบ — ดูรายงานก่อนหน้า)
- regime พลังงาน/อาหารใช้คันโยกเทียม (food×50)
- continuous mode ยังไม่ได้จูนเต็มที่ (base rate/local cap) — ค่าที่ลองทำให้ fertility ต่ำไป
- ทดสอบเฉพาะ body 14/38 (nest-capable มี durability เพียง 18 = ขอบเขต)

## 7. การทำซ้ำ
driver: `scripts/food_value_study_driver.py` (flags: `--scaffolded`, `--continuous-repro[-rate|-cap]`, `--repro-*`, `--founder-age-spread`, `--world`, `--body`)
```bash
# สูตรที่ลึกสุด (gen 6) — gated + carrying cap + ผ่อน
python scripts/food_value_study_driver.py --model v2 --ticks 8000 --mortal --body 38 \
  --drain-mult 0.05 --food-energy-mult 50 --low-value-food 15 \
  --repro-safety 0.50 --repro-comfort 0.45 --repro-safety-streak 6 --repro-pair-bond-streak 8 --repro-litter-min 2
# โครงสร้างใหม่ — continuous + scaffolded
python scripts/food_value_study_driver.py --model v2 --ticks 15000 --mortal --body 14 --scaffolded \
  --continuous-repro --drain-mult 0.05 --food-energy-mult 50 --low-value-food 15
```

## 8. กรอบหลักฐาน
- **Supporting**: funnel quantifies the social-gate wall (ready 8%); scaffolded raises births/gen; gen 6 reached
- **Against/Alternative**: ทุก config สูญพันธุ์ → tuning ไม่พอ; continuous mode ยังติด mate-finding
- **Confidence**: รากคือ clustering/density coupling = **สูง**; การจูนแก้ไม่ได้ = **สูง**; structural rework จะแก้ได้ = **ปานกลาง** (ต้องทดลอง)

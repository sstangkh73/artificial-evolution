# รายงาน: เศรษฐกิจพลังงานสมจริง + carrying capacity — เร่งความเร็ว สำเร็จ, ประชากรยั่งยืน ยังไม่สำเร็จ (R₀ ceiling)

**Realistic energy economy & food-regulated carrying capacity — perf win, but a structural sub-replacement (R₀<1) ceiling**

ผู้วิจัย: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-20
commit: `ea4967c` (food-signal spatial grid) + กลไกโครงสร้างก่อนหน้า (`6d473d9` starvation, `e5d0253` home-fidelity, `87597de` continuous repro, `90c3179` stochastic mortality)
สถานะ: perf fix สำเร็จ+verify · ประชากรเสถียร **ยังไม่สำเร็จ** หลัง ~33 รัน (negative result เชิงโครงสร้าง)

---

## บทคัดย่อ
ต่อจากการ redesign ให้ประชากรถูกคุมด้วยฟิสิกส์ (อดตายจริง + ถอดเพดานปลอม) งานนี้ (1) **แก้ perf `food_signal_at` ด้วย spatial grid → เร็วขึ้น 76×** บนอาหารหนาแน่น โดย v1 byte-identical (อาหารเบาบางใช้ loop เดิม); (2) calibrate เศรษฐกิจพลังงาน**สมจริง** (อาหารพลังงานธรรมชาติ mult=1, ไม่มี band-aid food×50) แล้วกวาด drain/ความหนาแน่น/อัตราสืบพันธุ์ พร้อมกลไกครบ 6 อย่าง (home-fidelity, continuous repro, stochastic mortality, starvation death, dense food, repro knobs) **ผลชี้ขาด: ทุกชุดได้ births/deaths ≈ 0.75–0.88 (< 1) เสมอ → สูญพันธุ์** ระบบมี **R₀ ceiling ใต้ 1 เชิงโครงสร้าง** ที่การจูน+กลไกทั้งหมดข้ามไม่ได้ — เป็น bistable (fade เมื่อ repro ต่ำ / boom-crash เมื่อ repro สูง) ไม่มี fixed point เสถียรตรงกลาง

---

## 1. Perf fix — food-signal spatial grid (สำเร็จ)
`food_signal_at`/`nearby_food_count` เดิมเป็น O(n_food) ต่อครั้ง → รันอาหารหนาแน่นช้าเป็นนาที
แก้: `_food_candidates` แบบ hybrid — อาหาร ≤ 400 ชิ้น iterate dict ตามลำดับ (bit-identical), เกินกว่านั้นใช้ spatial grid (rebuild ต่อ tick, ข้าม entry ที่เพิ่งถูกกิน)
**ผล:** micro-benchmark 2000 อาหาร × 20000 calls: **7.38s → 0.10s (76×)**; v1 3000-tick byte-identical
**หมายเหตุ:** รันที่ประชากรโต 250+ ยังช้าจาก **O(P²) social grouping** (คอขวดคนละตัว) — regime ฟิสิกส์จริง (food คุม K เล็กลง) ชนน้อยกว่า

## 2. เศรษฐกิจพลังงานสมจริง — การ calibrate
ทิ้งคันโยกเทียม (food×50): ใช้ **อาหารพลังงานธรรมชาติ (mult=1)** + drain ต่ำ (ให้อาหารธรรมชาติเลี้ยงได้) + ความหนาแน่นเพื่อแก้ foraging access + starvation death (อาหารคุม K) + ถอดเพดาน

### ตารางผล (mortal, body 14, ครบกลไก, 15000–18000 ticks)
| เงื่อนไข | peak | births | deaths (starv/lifespan) | R₀≈ | ผล |
| --- | ---: | ---: | --- | ---: | --- |
| drain0.02 + dense40 | 159 | 128 | 4 / 173 | 0.72 | สูญพันธุ์ |
| drain0.04 + dense40 | 153 | 140 | 17 / 173 | 0.74 | สูญพันธุ์ |
| drain0.02 + dense60 | 155 | 136 | 5 / 181 | 0.73 | สูญพันธุ์ |
| drain1.0 (เต็ม) + food1 | 88 | 40 | 90 / 0 | — | อดตายหมด (drain สูงไป) |
| **ครบ: drain0.03 + dense45 + starv + stochastic-mort + litter2 + life300** | **217** | **182** | 29 / 199 | **0.78** | สูญพันธุ์ |

→ ไม่ว่าจูนอย่างไร R₀ ติดเพดาน ~0.75–0.88

## 3. อภิปราย — R₀ ceiling เชิงโครงสร้าง
รวมแคมเปญทั้งหมด (~33 รัน, 6 กลไกโครงสร้าง):
- **repro ต่ำ → R₀ < 1 → fade** (ถึง gen 6–8 แล้วจาง)
- **repro สูง → boom ชนทรัพยากร/เพดาน → cohort crash** (gen 1–3)
- **ไม่มีจุดกึ่งกลางเสถียร** — ระบบ bistable, ไม่มี stable fixed point ที่ค่าพารามิเตอร์ที่เอื้อมถึง

deaths เกือบทั้งหมดเป็นอายุขัย (แม้เปิด stochastic) — แปลว่าทุก agent ตายในที่สุด และต้องทิ้งทายาท ≥ 1 ที่สืบพันธุ์ต่อ แต่ผลผลิตการสืบพันธุ์ต่อตัว-ตลอดชีวิต < 1 อย่างดื้อ สาเหตุที่เป็นไปได้ (ยังไม่ยืนยัน): เงื่อนไขสืบพันธุ์ (balanced × mate × safety × cooldown) สำเร็จเป็นเศษส่วนเล็กของเวลา × หน้าต่างสืบพันธุ์ × litter → ทายาทที่รอด+สืบพันธุ์ < 1; และการดันเศษส่วน/อัตราขึ้น → boom-crash

## 4. สรุป
- **perf fix = ชัยชนะจริง** (76×, byte-identical) ปลดล็อกการทดลองอาหารหนาแน่น
- **ประชากรยั่งยืน = ยังไม่สำเร็จ** — R₀ ceiling ใต้ 1 เชิงโครงสร้าง ข้ามไม่ได้ด้วยกลไก+จูน 6 อย่าง
- เป็น honest negative result ที่สำคัญ: ปัญหาไม่ใช่ "ขาดกลไก" (สร้างครบแล้ว: clustering, continuous birth, spread death, starvation-K) แต่เป็น **โครงสร้างการสืบพันธุ์ให้ผลผลิตต่อตัว < replacement** และ dynamics เป็น bistable

## 5. งานต่อไป (เปลี่ยนจาก manual tuning → วิเคราะห์โครงสร้าง)
1. **วิเคราะห์ผลผลิตการสืบพันธุ์ต่อ female-ตลอดชีวิต** ตรงๆ (กี่ทายาทที่รอดถึงวัยสืบพันธุ์) เพื่อหา**สาเหตุเชิงโครงสร้าง**ที่ทำให้ < 1 — ตัวไหนคือ binding (cooldown? หน้าต่าง? fraction balanced? mate?)
2. ถ้าพบ structural cap → แก้ที่ตรงนั้น(เช่น ลด cooldown/ลดวัยเริ่มสืบพันธุ์/เพิ่ม fecundity ต่อ event) แล้วหา R₀>1 ที่ไม่ boom
3. (เลือก) O(P²) social grouping → spatial index เพื่อรองรับประชากรใหญ่
4. systematic parameter sweep (grid เร็วแล้ว) แทน manual

## 6. การทำซ้ำ
driver: `scripts/food_value_study_driver.py` — flags ครบ: `--starvation-death --max-pop --home-fidelity --continuous-repro[-rate] --stochastic-mortality --drain-mult --food-energy-mult --low-value-food --repro-* --body`
```bash
# สูตรที่ดีสุดของแคมเปญ (R0~0.78, ยังสูญพันธุ์)
python scripts/food_value_study_driver.py --model v2 --ticks 18000 --mortal --body 14 \
  --scaffolded --home-fidelity --continuous-repro --continuous-repro-rate 0.35 \
  --starvation-death --stochastic-mortality --mortality-hazard 0.04 --drain-mult 0.03 \
  --max-pop 5000 --food-energy-mult 1 --low-value-food 45 --repro-litter-min 2 --repro-max-age 300
```

## 7. กรอบหลักฐาน
- **Supporting:** perf 76× (micro-bench); v1 byte-identical; กลไกครบทำงาน (home-fidelity→peak↑, continuous→gen 8)
- **Against/Alternative:** R₀ ติด ~0.78 ทุกชุด → กลไก+จูนไม่พอ; bistable ไม่มี stable middle
- **Confidence:** perf fix ถูกต้อง = สูง · R₀ ceiling เชิงโครงสร้าง = สูง (33 รัน robust) · แก้ได้ด้วยการวิเคราะห์โครงสร้างการสืบพันธุ์ = ปานกลาง

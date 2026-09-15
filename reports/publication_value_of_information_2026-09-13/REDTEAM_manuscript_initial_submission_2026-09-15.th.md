# Red-team report: ต้นฉบับ *When Does a Better Representation Pay?* (ฉบับ initial submission draft)

- เอกสารที่ตรวจ: `submission/manuscript_initial_submission_draft.pdf` (35 หน้า, build ล่าสุดตาม commit `626d8a9`)
- วารสารเป้าหมาย: *Artificial Life* (ตาม `cover_letter_draft.en.md`)
- วันที่ตรวจ: 2026-09-15
- ผู้ตรวจ: Claude (Anthropic) ใน Claude Code ตามคำขอของผู้เขียน. **การตรวจครั้งนี้เป็นการใช้ AI ที่ต้องเพิ่มลงใน `AI_USE_LOG.md` และ Generative-AI Disclosure** ถ้านำข้อเสนอแนะไปแก้ต้นฉบับ
- บทบาทที่สวม: reviewer ที่เข้มงวดที่สุดของ *Artificial Life* ซึ่งตั้งใจหาเหตุผลเพื่อ reject

---

## 0. สรุปสำหรับผู้เขียน (อ่านส่วนนี้ก่อน)

**คำตัดสิน: ยังไม่ควรส่งในสภาพนี้.** เหตุผลไม่ได้อยู่ที่ความซื่อตรง (ต้นฉบับซื่อตรงมากกว่างานทั่วไป) หรือ provenance (แข็งมาก). ปัญหาคือ **ข้อมูลดิบของงานเองมีคำอธิบายทางเลือกที่ต้นฉบับยังไม่ได้พูดถึง** และบางข้อขัดกับกลไกที่ Discussion เสนอโดยตรง. reviewer ที่เปิด raw dump หรืออ่านโค้ดจะเจอประเด็นเหล่านี้

ประเด็นร้ายแรง 4 ข้อ (รายละเอียดในหมวด 2):

| # | ประเด็น | ผลต่อข้อสรุป |
|---|---|---|
| C1 | **พลังงาน 10 เป็นคนละ regime กับ 4–8.** เกณฑ์ `0.6 × ค่าที่ดีที่สุด` เท่ากับ 6 ซึ่งเกินค่าอาหารหลัก (5) B2 จึงเริ่มปฏิเสธอาหารหลัก (acceptance 0.44) และการตายส่วนใหญ่กลายเป็นความชรา (74–76%) | slope บวกของ H6.1 มาจากจุดนี้ทั้งหมด จึงอาจเป็นผลของ threshold discontinuity + ceiling ไม่ใช่ "ข้อมูลคุ้มขึ้นเมื่อผลไม้มีค่า" |
| C2 | **ชื่อเรื่องและ abstract ไม่ตรงกับผล.** B2 ไม่ชนะ sham ที่ระดับใดเลย ผลบวกเดียวคือ B2-B1 ซึ่งเป็น secondary | reviewer จะมองว่า framing เกินหลักฐาน |
| C3 | **control ไม่ใช่สิ่งที่คำบรรยายสื่อ.** A3/A3O/A3R ได้พลังงาน 6 ต่อคำเสมอหลังปัดเศษ จึงไม่เคยปฏิเสธผลไม้ (acceptance 1.000) และ dose ที่ได้รับจริงไม่เท่ากัน. A3O กับ A3R ต่างกันแค่ chronic damage ราว 3.6% | T2-RB ไม่ได้ทดสอบ "พิษซ่อน vs พิษเห็นได้" และคำว่า "สอง control ให้ผลตรงกัน" แทบไม่เพิ่มความทนทาน |
| C4 | **กลไกใน Discussion ขัดกับจำนวนมื้อจริง.** ที่พลังงาน 4 B2 กินผลไม้และอาหารหลัก *มากกว่า* B1 และได้รับพิษเท่ากัน. B3 ได้รับพิษมากที่สุดแต่อยู่ได้นานที่สุด | คำอธิบาย "การปฏิเสธอย่างเลือกสรรเสียพลังงาน" ยังไม่มีหลักฐานรองรับ |

ข่าวดี: **ส่วนใหญ่แก้ได้ด้วยการวิเคราะห์ข้อมูล 600 รันที่มีอยู่แล้วและเขียนใหม่ ไม่ต้องรันใหม่** (แผนในหมวด 7)

---

## 1. สิ่งที่ตรวจ และตัวเลขที่ยืนยันแล้วว่าถูก

### 1.1 แหล่งหลักฐานที่เปิดดูจริง

- ข้อความ PDF ทั้งฉบับ (pdftotext) และรูปทั้ง 5 รูป (PNG ต้นฉบับใน `confirmatory/figures/`)
- `PREREG_E6_representation_payoff_2026-09-14.th.md` และ `../prereg/PREREG_toxin_ecological_trap_2026-09-12.th.md`
- `confirmatory/e6/E6_analysis.json`, `E6_secondary_and_mechanism.json`, `confirmatory/t2rb/T2RB_analysis.json`
- raw dump ทั้ง 450 ไฟล์ของ E6 และ 150 ไฟล์ของ T2-RB ใน `data/confirmatory_resource_age_2026-09-14/`
- โค้ด: `agents/agent.py` (`_food_worth_eating`, `_food_value_key`, `_scramble_bin`, `_learn_food_value`, `_realised_toxin_excess`, `_charge_toxin`, `_note_encounter`, `_metabolic_base_energy`)
- `../E1_lure_cost_results_2026-09-13.th.md`, `../E2_rescue_arm_results_2026-09-13.th.md`, `AI_USE_LOG.md`, `cover_letter_draft.en.md`
- Git: tag `prereg-resource-age-2026-09-14` และเวลาสร้างไฟล์ผลลัพธ์

### 1.2 ตัวเลขที่ตรงกับหลักฐาน (ไม่ต้องแก้)

- Table 1 ทุกช่อง, B2-B3 Holm p (0.0120 ×3, 0.00265, 0.4448) และ B2-B1 exploratory Holm (0.02125, 0.10456, 0.22638, 0.96870 ×2)
- slope 0.890 (SD 2.227, median 0.381, t CI 0.059–1.722, bootstrap 0.130–1.696, p = 0.0365, บวก 18/ลบ 12)
- leave-one-energy-out ตัด 10: −0.58 (−1.85 ถึง 0.70, p = 0.36)
- T2-RB: −7.928 (−11.046 ถึง −4.810), p = 0.000020, 38/12 และ A3O −7.102 (−10.218 ถึง −3.985), Cliff's δ −0.134/−0.118
- ช่วง D ของ B1/B2/B3 ใน E6, E4 ratio 4.6 เท่า และ ~62 เท่า (1/0.0161)
- E1 p = 5.72×10⁻⁶ = Holm×3 ของค่าต่ำสุดที่เป็นไปได้ 2/2²⁰ ถูกต้อง
- ค่าพลังงานผลไม้จริงถูก scale หลังปัดเศษรอบแรก และไม่แตะอาหารหลักตามที่เขียน (`agent.py:1891-1896`)
- sham ไม่ใช้ RNG และคีย์คงที่ต่อชิ้นอาหาร (`agent.py:1219-1260`) ตรงกับ Methods

---

## 2. ประเด็นร้ายแรง (Critical)

### C1 — slope บวกของ H6.1 อาจเป็น artifact ของ threshold discontinuity และ senescence ceiling ที่พลังงาน 10

**reviewer จะเขียนว่า:** "The positive slope is driven entirely by the energy-10 level, where the model's decision rule changes qualitatively. The linear model across 4–10 is misspecified."

**กลไกในโค้ด** (`agents/agent.py:1212-1217`):

```python
known_values = [v for v in self.food_value_memory.values()]   # ทุกคีย์ รวมอาหารหลัก
best_known = max(known_values)
return self.food_value_memory[key] >= pickiness * best_known    # pickiness = 0.6
```

- safe fruit = 10 → เกณฑ์ = 6 > อาหารหลัก 5 → **อาหารหลักถูกปฏิเสธ** ยกเว้นตอนอดอาหาร (energy ≤ 6)
- safe fruit = 8 → เกณฑ์ = 4.8 < 5 → อาหารหลักผ่านเสมอ
- ดังนั้นระหว่างพลังงาน 8 กับ 10 มี **จุดตัดเชิงคุณภาพ** ของ policy ซึ่งไม่เกี่ยวกับ "คุณค่าของข้อมูลอายุ" โดยตรง

**หลักฐานจาก raw dump** (ค่าเฉลี่ยต่อ founder แล้วเฉลี่ยข้าม 30 seed; สคริปต์ในภาคผนวก A):

| พลังงาน | แขน | มื้ออาหารหลัก | ครั้งที่ข้ามอาหารหลัก | acceptance อาหารหลัก | สัดส่วน founder ที่เคยข้ามอาหารหลัก |
|---:|---|---:|---:|---:|---:|
| 4–8 | B1/B2/B3 | 17.5–23.7 | **0.0** | **1.000** | **0.00** |
| 10 | B1 | 27.4 | 1.1 | 0.958 | 0.05 |
| 10 | B2 | 22.3 | **29.2** | **0.436** | **0.72** |
| 10 | B3 | 24.0 | 19.2 | 0.563 | 0.54 |

**สาเหตุการตาย** (จาก `E6_secondary_and_mechanism.json`) สัดส่วนความชราของ B1 ที่พลังงาน 4, 5, 6, 8, 10 คือ 0.19, 0.22, 0.27, 0.41, **0.76**. การอดอาหารลดจาก 0.76 เหลือ **0.08**. ที่พลังงาน 10 founder เกือบทุกตัวตายด้วยความชรา ความต่างระหว่างแขนจึงถูกบีบเข้าหาศูนย์ (ceiling compression). ข้อสังเกตที่สนับสนุนคือ B3-B1 (−1.9) และ B2-B1 (−0.5) ก็หดเข้าหาศูนย์ที่ระดับเดียวกัน ไม่ใช่เฉพาะ B2-B3

**ทำไมร้ายแรง:** ต้นฉบับตีความว่าเป็น "attenuation of a survival cost at the upper tested payoff" และเสนอว่า "a high safe-fruit payoff better compensates the costs of sampling" (หน้า 28). คำอธิบายทางเลือกสองข้อที่อธิบายข้อมูลได้เท่ากันหรือดีกว่ายังไม่ถูกกล่าวถึง:
1. policy เปลี่ยน regime (ปฏิเสธอาหารหลัก) เฉพาะที่ 10
2. outcome ชนเพดานความชรา ความต่างทุกคู่จึงหดลง

การออกแบบ energy `{4,5,6,8,10}` ยังให้ leverage สูงสุดแก่ 10 ด้วย (ระยะจากค่าเฉลี่ย +3.4 จาก Sxx = 23.2)

**วิธีแก้:**
- (ต้องทำ, ไม่ต้องรันใหม่) เพิ่มย่อหน้าใน Results/Discussion ที่รายงานตารางด้านบนและสาเหตุการตาย และระบุคำอธิบายทางเลือกทั้งสองอย่างตรงไปตรงมา
- (ต้องทำ) เปลี่ยนภาษาจาก "attenuation at upper payoff" เป็น "the only non-negative B2-B3 contrast occurred at the single level where (i) the relative-value threshold exceeded the staple value and (ii) senescence dominated mortality; the design cannot separate these from a payoff effect"
- (ควรทำ) วิเคราะห์ outcome ที่ไม่ชนเพดาน เช่น สัดส่วนการตายจากการอดอาหาร หรือ follow-up ของ founder ที่ initial age ต่ำ เป็น post hoc descriptive
- (ถ้ามีเวลา, prereg ใหม่) รัน variant ที่ `best_known` คำนวณภายในชนิดอาหารเดียวกัน หรือใส่ระดับพลังงาน 7 และ 9 (0.6×9 = 5.4 ข้ามเกณฑ์เช่นกัน จึงช่วยแยกผลของจุดตัด)

---

### C2 — ชื่อเรื่อง, abstract และ contribution สื่อเกินผล

**reviewer จะเขียนว่า:** "The title asks when a better representation pays. The registered answer is: never, relative to the capacity control."

หลักฐาน:
- B2-B3 **ติดลบอย่างมีนัยสำคัญที่ 4 จาก 5 ระดับ** และที่ 10 CI คร่อมศูนย์ (Table 1)
- ผลบวกเดียวที่ผ่าน family-wise correction คือ B2-B1 ที่พลังงาน 4 ซึ่งเป็น **secondary ที่ prereg ไม่ได้กำหนด multiplicity**. Holm ถูกเพิ่มทีหลังในฐานะ exploratory แต่ถูกวางเป็นประโยคผลลัพธ์แรกของ abstract
- slope = 0.890 **ต่ำกว่า SESOI (1.0)** และ CI ล่าง 0.059 ใกล้ศูนย์มาก. การทดสอบว่ามากกว่า SESOI (minimum-effect test) จะไม่ผ่าน
- Contribution 2 (หน้า 5) บอกว่า sham "identify information as the cause of restored discrimination" ข้อนี้ถูกสำหรับ discrimination แต่ H1 เกือบเป็น **tautology โดยการสร้าง**: learner แบบตารางที่ได้คีย์ตรงกับตัวแปรที่กำหนดผลย่อมแยกได้ (Cliff's δ = 1.00). reviewer จะไม่นับเป็นการค้นพบ
- Contribution 1 "full-ecology failure of type-only food valuation" เกินจริง เพราะ B1 กับ B2 รอดชีวิตพอ ๆ กันในเกือบทุกระดับ ความล้มเหลวอยู่ที่ discrimination ไม่ใช่ที่ survival
- Abstract รายงานผล T2-RB (A2 แย่กว่า) แต่ **ไม่รายงานผลลบของ E1** (ความซ่อนเร้นไม่เพิ่มต้นทุนที่ drain 0.2) ซึ่งเป็นผลยืนยันตาม prereg และมีทิศทางตรงข้าม reviewer อาจมองว่าเลือกรายงาน

**วิธีแก้:**
- เปลี่ยนชื่อเรื่องให้บอกผลจริง เช่น *"Resource-Age Information Restores Discrimination but Not Survival: A Capacity-Controlled Test in an Artificial Foraging Ecology"* หรือ *"Correct State Information Is Not Enough: …"*
- เรียง abstract ใหม่: (1) B2 แยกแยะได้ (2) **B2 แย่กว่า sham ที่ 4–8** (3) slope บวกแต่ต่ำกว่า SESOI และขึ้นกับจุดที่ policy เปลี่ยน regime (4) E1 null + T2-RB deficit คู่กัน (5) B2-B1 ใส่เป็นประโยครอง
- ยกผลที่น่าสนใจที่สุดขึ้นเป็นแกน: **การแบ่งคีย์แบบไร้ข้อมูล (sham) ช่วยให้รอดนานกว่าการแบ่งตามสถานะจริง** ข้อนี้คือ novelty จริงของงาน (ดู C4)

---

### C3 — control arm ทำงานต่างจากคำบรรยาย

**(ก) A3/A3O/A3R ไม่มีปัญหาการตัดสินใจเลย**

- potency 0.757811 → excess = 0.36×0.758 − 0.20 = 0.0728 → acute = 3.64 → พลังงานต่อคำ `int(round(10 − 3.64))` = **6 ทุกคำ** (`agent.py:1368-1370`)
- 6 > 0.6×6 และ 6 > อาหารหลัก 5 → **ไม่เคยปฏิเสธผลไม้**
  - E1: A3 acceptance 1.000, learned value 6.00 (`E1_lure_cost_results`:43, Figure 1B)
  - T2-RB: A3O และ A3R มี fruit skips = **0.0**, learned fruit value = **6.0** ทุก founder
- ผลคือ A2−A3 **ไม่ได้เทียบ "พิษซ่อน vs พิษที่เห็นได้"** แต่เทียบ "ผลตอบแทนแปรปรวนที่ต้องเลือก" กับ "ผลตอบแทนคงที่ที่กินทุกครั้ง". ต้นฉบับเขียนว่า constant control "separated age dependence from the amount of fruit available" (หน้า 7) และ "distinguish temporal state dependence from … approximate toxin dose" (หน้า 30) ซึ่งไม่ครบ

**(ข) dose ที่ได้รับจริงไม่เท่ากัน และต้นฉบับไม่รายงาน**

- E1: A2 ได้รับพิษจริง **น้อยกว่า A3 34%** (บันทึกไว้เองใน `E1_lure_cost_results`:136)
- T2-RB (คำนวณจาก raw dump):

| แขน | มื้อผลไม้/founder | ครั้งที่ข้ามผลไม้ | พิษสะสม (excess) | พิษต่อมื้อ | toxin damage |
|---|---:|---:|---:|---:|---:|
| A2 | 27.07 | 1.91 | **1.877** | 0.0693 | 9.38 |
| A3O | 28.93 | 0.00 | 2.107 | 0.0728 | 10.53 |
| A3R | 29.16 | 0.00 | 2.048 | 0.0702 | 10.24 |

A2 ได้รับพิษน้อยกว่า A3R 8% และพลังงานเฉลี่ยต่อคำน่าจะสูงกว่าด้วย (ประมาณ 6.5 เทียบกับ 6 ของ A3R ที่ถูกปัดทิ้ง 0.49) **แต่ A2 กลับอยู่ได้สั้นกว่า 7.9 tick.** ข้อนี้น่าสนใจมากและต้นฉบับยังไม่ได้อธิบาย. ข้อสันนิษฐานที่ต้องตรวจคือจำนวนมื้อที่น้อยกว่า, ช่วงเวลาที่กินผลไม้พิษแรง (อายุน้อย, net = 2), หรือต้นทุนการเดินหาอาหารที่ drain 0.5

**(ค) "สอง control ให้ข้อสรุปตรงกัน" เป็นหลักฐานความทนทานที่อ่อน**

A3O กับ A3R ให้พลังงานต่อคำเท่ากัน (6) หลังปัดเศษ ต่างกันแค่ chronic damage 0.364 vs 0.351 ต่อคำ (~3.6%). ค่าเฉลี่ย follow-up 166.36 vs 167.19 จึงแทบเป็นแขนเดียวกัน. การที่ทั้งสองให้ผลตรงกันแทบไม่บอกอะไรเรื่อง "ความไวต่อวิธี dose matching" ตามที่ prereg ตั้งใจ

**(ง) B2/B3 แบ่งคีย์ของอาหารหลักด้วย แต่ Methods ไม่ได้เขียน**

`_food_value_key` ใช้กับทุกชนิดอาหาร. raw dump แสดงคีย์ `raw_plant@0 … raw_plant@8` ใน B2 (`agent.py:1245-1260`). หมายความว่า B2/B3 ต้อง "ชิมครั้งแรก" อาหารหลักถึง 9 คีย์ ในขณะที่ B1 ชิมคีย์เดียว ข้อนี้เปลี่ยนภาระการสำรวจและค่า `best_known`. Methods หน้า 8 เขียนเหมือนแบ่งเฉพาะผลไม้

**วิธีแก้:**
- Methods: เขียนชัดว่า A3 ได้พลังงาน 6 คงที่ต่อคำหลังปัดเศษ จึงถูกยอมรับทุกครั้ง และเขียนว่า B2/B3 แบ่งคีย์ทุกชนิดอาหาร
- Results: รายงาน realized dose ทุกแขนของ E1 และ T2-RB
- Discussion: เปลี่ยนการตีความ T2-RB เป็น "a cost of variable, choice-requiring toxicity relative to a fixed-payoff control that required no discrimination; realized dose was lower, not higher, in A2" และเลิกใช้ความตรงกันของ A3O/A3R เป็นหลักฐานความทนทาน

---

### C4 — กลไกที่ Discussion เสนอขัดกับจำนวนมื้อและพิษที่ได้รับจริง

**ข้อความในต้นฉบับ** (หน้า 27, 28):
- "B2's higher discrimination meant that it rejected more toxic fruit. Rejection lowered toxin exposure but also relinquished energy"
- "B2's selective rejection sacrifices energy at lower fruit payoffs"

**ข้อมูลจริง E6** (ค่าเฉลี่ยต่อ founder; skip counter ไม่ได้ dedupe จึงสูงเกินจริงบ้าง):

| พลังงาน | แขน | มื้อผลไม้ | มื้ออาหารหลัก | ข้ามผลไม้ | พิษสะสม | follow-up (Table 1) |
|---:|---|---:|---:|---:|---:|---:|
| 4 | B1 | 17.2 | 17.5 | 32.3 | 2.07 | 144.2 |
| 4 | B2 | **18.4** | **20.1** | 30.3 | **2.10** | 150.7 |
| 4 | B3 | 19.7 | **23.7** | 26.3 | **2.39** | **156.1** |
| 8 | B1 | 21.6 | 21.0 | 44.5 | 2.57 | 172.6 |
| 8 | B2 | 20.1 | 19.3 | 45.4 | 2.24 | 171.3 |
| 8 | B3 | 21.7 | 23.6 | 42.4 | 2.61 | 179.0 |

สิ่งที่ตารางบอก:
1. ที่พลังงาน 4–6 **B2 ไม่ได้ได้รับพิษน้อยกว่า B1** และกินอาหาร *มากกว่า* B1 ด้วย. คำอธิบาย "ปฏิเสธแล้วเสียพลังงาน" จึงไม่ตรงข้อมูล
2. **B3 ได้รับพิษมากที่สุดแต่รอดนานที่สุด** และมีมื้ออาหารหลักมากที่สุดทุกระดับ 4–8. อายุขัยสอดคล้องกับจำนวนมื้ออาหารหลักมากกว่าปริมาณพิษ
3. B1 มีคีย์ผลไม้คีย์เดียวซึ่งต่ำกว่าเกณฑ์ใน **99% ของ founder ที่พลังงาน 4** (ณ ตอนตาย) แต่ B1 ยังกินผลไม้ 17 มื้อ. การกินผลไม้ส่วนใหญ่จึงน่าจะเกิดผ่าน **starvation override (energy ≤ 6)** ไม่ใช่ผ่าน learned policy. ถ้าจริง survival effect ของ representation ถูกกรองผ่านกฎอดอาหารเป็นหลัก ซึ่งต้นฉบับไม่ได้วิเคราะห์
4. B2 มี P(eat | safe) = **1.000 ทุกระดับ** แม้ที่พลังงาน 4 ซึ่งผลไม้ปลอดภัย (4) มีค่าต่ำกว่าอาหารหลัก (5). "ข้อมูล" จึงทำให้ B2 กินอาหารค่าต่ำโดยไม่ลังเล (4 ≥ 0.6×5 = 3). นี่คือกลไกที่เป็นไปได้ของต้นทุนเทียบ sham ที่ควรพูดถึง

**วิธีแก้:**
- เพิ่มตาราง intake (มื้อผลไม้, มื้ออาหารหลัก, พิษสะสม, สาเหตุการตาย) เป็น secondary descriptive ซึ่ง **prereg §5 ข้อ 3, 4, 6 สัญญาไว้แล้ว** (ดู M1)
- ลบหรือลดข้อความกลไกที่ข้อมูลไม่รองรับ แล้วแทนด้วย "survival differences tracked staple intake more closely than toxin intake; the causal path remains unidentified"
- (ควรทำ) ถ้า telemetry มีข้อมูลพอ ให้แยกมื้อที่เกิดใต้ starvation override. ถ้าไม่มี ให้ระบุเป็นข้อจำกัดและ next test

---

## 3. ประเด็นหลัก (Major)

### M1 — ผลรองที่ prereg สัญญาไว้ไม่ได้อยู่ในต้นฉบับ (selective-reporting risk)

prereg E6 §5 ระบุให้รายงาน: (3) toxin dose ต่อ encounter, (4) สัดส่วนสาเหตุการตาย, (5) encounter และ P(eat | encounter), (6) learned values ต่อ bin ของ B2 **และของ B3**. ต้นฉบับรายงานแค่ D, encounter gate และ "B2 safe bin > toxic bin". ข้อมูลข้อ 3, 4, 6 มีครบใน JSON และ raw dump แล้ว. reviewer ที่อ่าน prereg จะถามทันที
**แก้:** เพิ่ม supplementary table ครบทุกข้อใน §5 และอ้างใน Results

### M2 — การทำนายที่ลงทะเบียนไว้แต่ไม่เป็นจริงไม่ได้ถูกเรียกว่า "ไม่เป็นจริง"

- **H2 ในต้นฉบับ** เขียนแบบไม่ระบุทิศ ("changes systematically") แต่ **prereg H6.1 ระบุทิศบวก** พร้อมเหตุผลเชิงกลไก "เมื่อผลไม้ปลอดภัยมีค่าสูง ข้อมูลอายุเปิดให้กินทรัพยากรที่มีค่าและลดการกินพิษ". เหตุผลนี้ไม่เป็นจริง (B2 < B3 ที่ 4–8) แต่ต้นฉบับไม่ได้บอก ควรใช้ถ้อยคำเดียวกับ prereg
- **prereg E1–E5 H2.2** ทำนาย D(B3) ≈ 0 และ **H2.3** บอกว่า D(B1) = 0 "โดยโครงสร้าง". ค่าจริงคือ D(B3) = −0.08 ถึง −0.11 และ D(B1) = +0.06/−0.05 ถึง −0.08 ด้วย CI แคบมาก. เอกสาร `E2_rescue_arm_results` ให้ ✅ ทั้งสองข้อ แต่ **ต้นฉบับยอมรับว่า sham "not behaviorally neutral" โดยไม่บอกว่าขัดกับคำทำนายที่ลงทะเบียนไว้**
- ต้นฉบับยังไม่ได้เปิดเผยว่า oracle B4 และ D ถูก implement **หลัง** freeze (commit `e668829`, deviation log ใน prereg บรรทัด 276)

**แก้:** เพิ่มตาราง "Preregistered prediction → observed → verdict" ครบทุกข้อ (ทั้ง E1–E5 และ E6) และตาราง deviation ใน supplement

### M3 — D ของแขนที่ "มองไม่เห็นอายุโดยโครงสร้าง" ไม่เป็นศูนย์ ซึ่งตั้งคำถามกับ validity ของ outcome หลักของ H1

ถ้า B1 ไม่มีทางรู้อายุ D ที่ไม่เป็นศูนย์ ±0.1 แปลว่า D ปนเปื้อนด้วยอย่างอื่น เช่น การเจอซ้ำ, สถานะพลังงานตอนเจอ หรือ starvation override. telemetry dedupe แค่ `(tick, x, y)` เดียวกันที่ติดกัน (`agent.py:1120-1124`). ถ้า agent ยืนอยู่บนอาหารที่ปฏิเสธหลาย tick จะนับ encounter ซ้ำทุก tick ทำให้ชิ้นที่ถูกปฏิเสธมีน้ำหนักใน denominator มากกว่าชิ้นที่ถูกกิน. ต้นฉบับยอมรับว่า "telemetry does not separate pseudo-category learning from this exposure feedback" แต่ยังตีความเครื่องหมายลบของ B3 ใน Discussion
**แก้:**
- ระบุว่า |D| ≈ 0.1 คือ "noise floor เชิงโครงสร้าง" ของ metric นี้. B2 (0.65–0.75) ยังเกินชัด H1 จึงไม่เสีย แต่ห้ามตีความเครื่องหมายของ B1/B3
- (ควรทำ) คำนวณ D แบบนับชิ้นอาหารไม่ซ้ำ หรือเฉพาะ encounter แรกต่อชิ้น ถ้าข้อมูลพอ

### M4 — ขนาดผล, power และ effect size

- slope SD ที่สังเกตได้ **2.227** เทียบกับที่ใช้วางแผน **1.624**. power จริงสำหรับ slope = 1 ที่ n = 30 จึงราว 0.69 ไม่ใช่ 0.92 ตามแผน (normal approximation, SE ≈ 0.41) ควรรายงาน
- Cliff's δ ที่รายงานเป็นแบบ **unpaired** บนข้อมูลแบบจับคู่ (บางที่ระบุ บางที่ไม่ระบุ เช่น E1 δ = −0.635) และได้ "negligible" แทบทุก contrast ของ E6/T2-RB. ควรใช้ paired effect size (d_z หรือ paired probability of superiority) เป็นหลัก หรือระบุชัดทุกจุดว่าเป็น unpaired
- E1/E3/E4 p-values ชนค่าต่ำสุดที่เป็นไปได้ของ exact test ควรเขียนแบบนั้นแทนตัวเลขทศนิยมยาว (เช่น "p = 2/2²⁰, the minimum attainable")

### M5 — การตีความ mechanism gate ถูกเลือกหลังเห็นข้อมูล

prereg §5 เขียนว่า "จำนวน encounter ต่ำกว่า 30 ต่อ founder **ในระดับใด**" ซึ่งกำกวม. `E6_secondary_and_mechanism.json` ระบุ `analysis_timing: post-prereg implementation after primary-result reveal` และเลือกอ่านเป็น "level mean" ทั้งที่ค่าต่ำสุดรายรันคือ 19.26 (B2) และ 15.98 (B3) ที่พลังงาน 4. ต้นฉบับเขียนว่า gate "passed"
**แก้:** เขียนว่า "the gate text was ambiguous; under the level-mean reading it passed, under a per-run reading it failed at energies 4–6; the reading was fixed after the primary result was known" และจัดเป็น deviation

### M6 — preregistration ตรวจสอบจากภายนอกไม่ได้

- tag `prereg-resource-age-2026-09-14` สร้างเวลา 00:43:02 และไฟล์ผล E6 แรกเกิดเวลา 00:44:59 ซึ่งสอดคล้องกันภายใน repo
- แต่ **ไม่พบ prereg tag บน remote** (`git ls-remote --tags origin`; ถ้าเครือข่ายขัดข้องให้ตรวจซ้ำ) และ tag ของ E1–E5 เป็น lightweight tag ที่ไม่มี tagger date. เวลาของ Git commit แก้ได้โดยผู้เขียน reviewer จึงมอง "preregistered" ว่าเป็นคำอ้างที่ยืนยันไม่ได้
**แก้:** ในต้นฉบับใช้คำว่า "internally frozen at a Git tag before data generation" แทน "preregistered" แบบไม่มีเงื่อนไข หรือระบุชัดว่าไม่ได้ลงทะเบียนในระบบสาธารณะ. สำหรับการทดลองครั้งต่อไปให้ใช้ OSF/AsPredicted หรืออย่างน้อย push tag ขึ้น GitHub ก่อนรัน

### M7 — โครงเรื่องแบบรวมทุกการทดลอง ทำให้ผู้อ่านหลงประเด็น

ต้นฉบับมี 7 ชุด (E1–E6, T2-RB), 2 โปรไฟล์พิษ, 2 ค่า drain, 3 horizon (400/800/3000), 2 ชื่อ outcome (attained age กับ follow-up) และ 3 ระบบชื่อ (Study A–F, E1–E6, H1–H3/H6.1). E3 (selection differential) และ E4 (denominator) ไม่ได้ตอบคำถามในชื่อเรื่อง
**แก้:** เรื่องหลักใช้ E2 → E6 → T2-RB (+ E1 เป็นบริบท). ย้าย E3 และ E4 ไป supplement หรือย่อเหลือย่อหน้าเดียว. ใช้ระบบชื่อเดียวตลอดเล่ม

### M8 — ความทั่วไปของผล: พารามิเตอร์ที่ตั้งด้วยมือยังไม่มี sensitivity analysis

pickiness 0.6, α 0.3, starvation 6, bin 20 tick, cap 8, acute 50, chronic 5 ล้วนตั้งด้วยมือ. C1 แสดงแล้วว่าข้อสรุปหลักขึ้นกับ pickiness × ค่าอาหารหลักโดยตรง. reviewer ของ *Artificial Life* จะขอ sensitivity อย่างน้อยสำหรับ pickiness และ starvation threshold
**แก้:** อย่างน้อยให้ระบุเป็นข้อจำกัดเฉพาะเจาะจงใน 4.7 (ไม่ใช่ประโยคกว้าง ๆ). ถ้ามีเวลาให้ทำ sweep เล็ก ๆ แบบ exploratory

### M9 — วรรณกรรมบางเกินไปและขาดงานที่ตรงประเด็นที่สุด

มี 11 แหล่งวิชาการ. งานที่ reviewer น่าจะถามหา (**ต้องตรวจ metadata ทุกรายการก่อนอ้าง** เพราะรายการนี้มาจากความรู้ของผู้ตรวจ ไม่ได้เปิดดูต้นฉบับ):
- **McCallum (1996)** วิทยานิพนธ์เรื่อง utile distinction memory / selective perception and hidden state ซึ่งตรงกับคำถาม "ความแตกต่างของสถานะที่ *มีประโยชน์* ต่อ utility" ที่สุด
- **Howard (1966)** *Information value theory* ต้นทางของ value of information
- **Stephens & Krebs (1986)** *Foraging Theory* เพราะกฎ pickiness คือ prey/diet-choice model ที่ใช้เกณฑ์สัมพัทธ์
- **Janzen (1977)** *Why fruits rot, seeds mold, and meat spoil* และ **Cipollini & Levey (1997)** เรื่อง secondary metabolites/directed toxicity ในผลไม้. โปรไฟล์ toxic–safe–toxic คือ ดิบ–สุก–เน่า และจะยึดงานกับชีววิทยาจริงได้ดีมาก
- **Provenza (1995)** เรื่อง post-ingestive feedback ซึ่งตรงกับกลไก learner
- งาน ALife คลาสสิกเรื่อง learning/sensing ที่คุ้มหรือไม่คุ้ม เช่น **Todd & Miller (1991)** และ **Ackley & Littman (1991)**

---

## 4. ประเด็นรอง (Minor)

1. **ชื่อ outcome ปนกัน:** E1–E3 ใช้ attained age, E6/T2-RB ใช้ follow-up, Figure 2B label "attained-age difference". ควรอธิบายครั้งเดียวว่าความต่างแบบจับคู่เท่ากัน แล้วใช้ชื่อเดียว
2. **หน้า 17 (3.3):** B2-B1 +3.80/−1.29 และ oracle −51.96/−55.47 ไม่มี CI และ "sharply increasing starvation deaths" ไม่มีตัวเลข
3. **หน้า 21:** "Mean fruit encounters per founder ranged from 48.7 to 65.5" เป็นค่าของ B2 เท่านั้น ควรระบุ. ที่พลังงาน 10 B1 มี 78.6 ซึ่งต่างจาก B2 (61.9) มาก
4. **D ของ B2 ไม่ monotonic** (สูงสุดที่ 8 แล้วตกที่ 10, Figure 4B) สอดคล้องกับ C1 แต่ไม่ถูกกล่าวถึง
5. **"Matched seeds"** ใช้ seed เริ่มต้นร่วมกัน แต่ trajectory แยกกันทันทีที่พฤติกรรมต่าง ควรเขียนให้ชัดใน 2.4 (4.6 เขียนไว้ถูกแล้ว)
6. **Declarations 6 จุดยังเป็น placeholder** (Funding, Competing interests, Ethics, CRediT, AI approval, Data DOI). `manuscript_submission_audit.json` ระบุ `submission_ready: false`
7. **AI disclosure:** log ระบุว่า AI "executed the frozen E6 and T2-RB protocols" และร่างเกือบทุกส่วน. สำหรับผู้เขียนคนเดียวที่เป็นนักเรียน ข้อความ "The human author made the scientific decisions" ควรมีตัวอย่างการตัดสินใจที่ผู้เขียนทำเองจริง และผู้เขียนต้องอธิบาย C1–C4 ได้ด้วยตัวเองถ้าถูกถาม. **ต้องเพิ่มการใช้ Claude (red-team นี้) ถ้านำไปใช้**
8. **หน้า 7:** "potency_scale" ของ A3O/A3R มีทศนิยม 16 หลัก (0.7506672222220914) ดูเหมือน over-precision ควรเขียน ≈ 0.7507 และให้ค่าเต็มใน supplement
9. **หน้า 24:** "The point estimate exceeded the preregistered 5-tick SESOI, although the t interval narrowly included −5" ควรเสริมว่ายังไม่ได้ทดสอบ minimum effect อย่างเป็นทางการ

---

## 5. รูป (Figures)

| รูป | ปัญหา | แก้ |
|---|---|---|
| Fig 1 | แกน x มีแต่รหัส A0–A3 ผู้อ่านต้องกลับไปอ่าน caption. **A3 acceptance = 1.000** เป็นข้อเท็จจริงสำคัญ (C3) แต่ไม่มีคำอธิบาย | ใส่ label สั้นใต้รหัส และเพิ่มประโยคใน caption ว่า A3 ได้ 6 energy คงที่จึงไม่เคยปฏิเสธ |
| Fig 2 | legend ด้านล่าง **ทับจุดข้อมูล**: panel A ทับจุด B3 ต่ำสุด (~−0.17) และ panel B ทับจุด B4 ที่ −80 ถึง −84 | ย้าย legend ออกนอกกรอบหรือไว้ด้านบน |
| Fig 3B | annotation "mean encounters = 26,945.3" ชิดขอบขวา และตำแหน่งข้อความลอยห่างจุด | ย้ายไปใต้ label แกน x หรือใส่ใน caption |
| Fig 4A | marker B2-B1 และ B3-B1 ซ้อนกันที่พลังงาน 10. เส้นเทาไม่มีใน legend. แกน y label ยาวจนเบียด | ใช้ horizontal dodge, เพิ่ม "within-seed B2-B3" ใน legend, ย่อ label. พิจารณาทำเครื่องหมาย regime เปลี่ยนระหว่าง 8–10 (C1) |
| Fig 5 | กล่อง legend "SESOI = −5 ticks" **ทับจุด A3R ที่ต่ำสุด (~−36)**. label "recalibrated control" **ถูกตัดที่ขอบขวา** | ย้าย legend ขึ้นบน และเพิ่ม margin ขวา |

หมายเหตุ: pdftotext อ่านข้อความในรูปของ PDF เป็นตัวอักษรซ้อนกัน (เช่น "origAin2a-lAc3oOntrol") ซึ่งอาจเป็นเพียงลำดับการวางข้อความในเวกเตอร์. ควรเปิด PDF ด้วยตาและลอง copy ข้อความรูปอีกครั้ง เพราะระบบ ScholarOne/เครื่องมือค้นหาจะอ่านแบบเดียวกัน

---

## 6. จุดแข็งที่ต้องรักษาไว้ (reviewer จะชม)

- ความซื่อตรง: รายงาน null (E1 T2, E3 H3.2), ผลทิศตรงข้าม และ endpoint dependence ด้วยตัวเอง รวมถึง leave-one-out
- provenance ระดับหายาก: tag, clean worktree, validator ทุก cell, SHA-256 manifest 616/696 ไฟล์ และ launch-parameter origin ทุกแขน
- sham ที่ไม่ใช้ RNG จึงรักษา seed pairing ได้ (ออกแบบดีจริง)
- แยก within-generation selection ออกจาก evolution อย่างเข้มงวด
- E4 ชี้ปัญหา denominator ที่ใช้ได้กว้างกว่าโมเดลนี้
- การใช้ภาษาระวังเรื่อง EVPI/fitness value ถูกต้องตาม Donaldson-Matasci et al.

---

## 7. แผนแก้ไขเรียงตามลำดับความสำคัญ

### ระดับ 1 — ต้องทำก่อนส่ง (ใช้ข้อมูลเดิม ไม่ต้องรันใหม่)

1. [ ] เปลี่ยนชื่อเรื่อง, abstract และ contribution ตาม C2
2. [ ] เพิ่มการวิเคราะห์ regime ที่พลังงาน 10 (acceptance อาหารหลัก + สาเหตุการตาย) และเขียนคำอธิบายทางเลือกตาม C1
3. [ ] เขียน Methods ใหม่: A3 ได้ 6 energy คงที่และไม่เคยปฏิเสธ, B2/B3 แบ่งคีย์อาหารหลักด้วย, กฎ `best_known` ใช้ค่าสูงสุดข้ามทุกชนิดอาหาร
4. [ ] รายงาน realized dose ทุกแขน (E1, T2-RB, E6) และแก้การตีความ T2-RB ตาม C3
5. [ ] แก้ข้อความกลไกใน 4.2/4.3 ให้ตรงกับตาราง intake ตาม C4
6. [ ] เพิ่มผลรองที่ prereg สัญญาไว้ครบ (M1) และตาราง prediction → verdict + deviation (M2, M5)
7. [ ] ปรับถ้อยคำ "preregistered" ให้ตรงกับระดับที่ตรวจสอบได้ (M6)
8. [ ] แก้รูป 2, 4, 5 (legend ทับข้อมูล, label ถูกตัด)
9. [ ] เติม declarations ทั้ง 6 จุด และเพิ่มการใช้ Claude ใน AI log/disclosure
10. [ ] เพิ่มวรรณกรรมหลักใน M9 หลังตรวจ metadata

### ระดับ 2 — ควรทำ (วิเคราะห์เพิ่มจากข้อมูลเดิม, post hoc descriptive)

- [ ] D แบบนับชิ้นอาหารไม่ซ้ำ / encounter แรก (M3)
- [ ] paired effect size แทน unpaired Cliff's δ และ power จริง (M4)
- [ ] minimum-effect test ของ slope เทียบกับ SESOI = 1
- [ ] outcome ที่ไม่ชนเพดานความชราสำหรับพลังงาน 10
- [ ] ย้าย E3/E4 ไป supplement (M7)

### ระดับ 3 — ถ้ามีเวลา (ต้องลงทะเบียนและรันใหม่ อาจเป็น paper ถัดไป)

- [ ] variant ที่ relative threshold คำนวณภายในชนิดอาหาร หรือระดับพลังงาน 7, 9, 12 เพื่อแยกผล threshold ออกจาก payoff
- [ ] sensitivity sweep ของ pickiness และ starvation threshold
- [ ] ลงทะเบียนสาธารณะ (OSF) ก่อนรัน
- [ ] ศึกษาว่าทำไม sham ช่วยให้รอด: นี่อาจเป็น paper ที่น่าสนใจกว่า paper ปัจจุบัน

---

## 8. รายงาน reviewer จำลอง (สั้น)

> **Reviewer 2 — Recommendation: Major revision (borderline reject)**
>
> The manuscript is unusually transparent and its provenance is exemplary. However, the headline confirmatory result (a positive B2−B3 slope) rests on a single endpoint at which the agents' relative-value rule begins rejecting the staple food and mortality becomes dominated by senescence; the authors' payoff-compensation interpretation is not distinguished from these alternatives. The constant-potency controls yield a fixed post-rounding payoff that is always accepted, so the A2−A3 contrasts do not isolate concealment, and realized doses are unequal in the direction opposite to the observed survival effect. The mechanistic narrative in the Discussion is not supported by intake data the authors possess. The capacity-matched sham outperforms the informed learner at most payoffs, which is the most interesting finding but is treated as a nuisance. Several preregistered secondary outcomes are not reported, and preregistered predictions for the sham and type-only discrimination were not met but are not labeled as such. I would reconsider a version that re-centres the paper on "correct state information did not improve survival relative to an uninformative partition," reports all preregistered outcomes, and analyses the regime change at the highest payoff.

ความเห็นของผู้ตรวจ: ถ้าแก้ระดับ 1 ครบ งานนี้มีโอกาสผ่าน review ดีขึ้นมาก เพราะข้อบกพร่องส่วนใหญ่อยู่ที่การตีความ ไม่ใช่ข้อมูลเสีย

---

## ภาคผนวก A — สคริปต์ที่ใช้คำนวณตาราง intake (descriptive, ไม่มี CI)

ข้อควรระวัง:
- ค่าเป็นค่าเฉลี่ยของตัวนับต่อ founder ณ ตอนจบรัน แล้วเฉลี่ยข้าม seed
- `skipped_food_by_type` ไม่ได้ dedupe ต่อ tick จึงอาจสูงเกินจริง
- "fraction of fruit keys below threshold" ใช้ค่า memory ณ ตอนตาย
- ควรทำเป็นสคริปต์ใน `scripts/` พร้อม test ก่อนนำตัวเลขใส่ต้นฉบับ

```python
import json, glob, os, collections, statistics as st
rows = collections.defaultdict(list)
for f in glob.glob("data/confirmatory_resource_age_2026-09-14/e6/E6_V*_B*_s*.json"):
    _, lv, arm, _ = os.path.basename(f)[:-5].split("_")
    ags = [a for a in json.load(open(f))["agent_diet_summary"] if a.get("generation") == 0]
    m = lambda fn: sum(fn(a) for a in ags) / len(ags)
    fruit = m(lambda a: a["meals_by_type"].get("raw_fruit", 0))
    plant = m(lambda a: a["meals_by_type"].get("raw_plant", 0))
    fskip = m(lambda a: a["skipped_food_by_type"].get("raw_fruit", 0))
    pskip = m(lambda a: a["skipped_food_by_type"].get("raw_plant", 0))
    tox = m(lambda a: a["toxin_ingested_total"])
    rows[(lv, arm)].append((fruit, plant, fskip, pskip, plant / (plant + pskip), tox))
for k in sorted(rows):
    print(k, *[round(st.mean(c), 3) for c in zip(*rows[k])])
```

ผลเต็ม (E6):

| lvl | arm | fruit meals | plant meals | fruit skips | plant skips | plant accept | toxin ingested | max learned value | founders skipping plant | fruit keys < threshold |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | B1 | 17.211 | 17.525 | 32.289 | 0.000 | 1.000 | 2.066 | 3.322 | 0.000 | 0.988 |
| 4 | B2 | 18.354 | 20.051 | 30.348 | 0.000 | 1.000 | 2.101 | 3.889 | 0.000 | 0.740 |
| 4 | B3 | 19.680 | 23.684 | 26.281 | 0.000 | 1.000 | 2.386 | 3.838 | 0.000 | 0.936 |
| 5 | B1 | 18.175 | 18.365 | 34.856 | 0.000 | 1.000 | 2.178 | 3.645 | 0.000 | 0.975 |
| 5 | B2 | 18.871 | 20.251 | 33.418 | 0.000 | 1.000 | 2.149 | 4.223 | 0.000 | 0.740 |
| 5 | B3 | 20.183 | 23.965 | 29.310 | 0.000 | 1.000 | 2.446 | 4.184 | 0.000 | 0.924 |
| 6 | B1 | 19.025 | 18.953 | 37.249 | 0.000 | 1.000 | 2.256 | 3.892 | 0.000 | 0.949 |
| 6 | B2 | 19.061 | 20.025 | 37.081 | 0.000 | 1.000 | 2.150 | 5.128 | 0.000 | 0.739 |
| 6 | B3 | 20.822 | 23.660 | 32.402 | 0.000 | 1.000 | 2.518 | 4.677 | 0.000 | 0.879 |
| 8 | B1 | 21.599 | 21.035 | 44.517 | 0.000 | 1.000 | 2.566 | 4.415 | 0.000 | 0.748 |
| 8 | B2 | 20.103 | 19.343 | 45.361 | 0.000 | 1.000 | 2.237 | 7.114 | 0.000 | 0.663 |
| 8 | B3 | 21.655 | 23.578 | 42.383 | 0.000 | 1.000 | 2.614 | 5.783 | 0.000 | 0.759 |
| 10 | B1 | 26.507 | 27.405 | 52.059 | 1.091 | 0.958 | 3.181 | 5.014 | 0.047 | 0.456 |
| 10 | B2 | 25.724 | 22.275 | 36.214 | 29.186 | 0.436 | 2.984 | 9.587 | 0.717 | 0.686 |
| 10 | B3 | 25.447 | 24.008 | 40.035 | 19.152 | 0.563 | 3.093 | 7.556 | 0.540 | 0.676 |

ข้อสังเกตเพิ่ม (ตรวจซ้ำแล้ว): "max learned value" ที่พลังงาน 4–6 ต่ำกว่า 5 ไม่ได้เกิดจากค่าอาหารหลักถูกดึงลง. ทุก founder ที่มีคีย์อาหารหลักมีค่า **5.0 พอดี**. ค่าเฉลี่ยต่ำเพราะ (ก) founder ส่วนหนึ่งไม่เคยชิมอาหารหลักเลย memory จึงมีแต่คีย์ผลไม้ซึ่งอาจติดลบ และ (ข) founder ราว 1% ที่ memory ว่างถูกนับเป็น 0 ในสคริปต์นี้ (ค่าเฉลี่ยเฉพาะ memory ไม่ว่าง: พลังงาน 4 = 3.36/3.94/3.88; พลังงาน 10 = 5.06/9.70/7.61 สำหรับ B1/B2/B3). ข้อ (ก) ควรรายงานด้วย เพราะแปลว่า founder จำนวนไม่น้อยอยู่ได้โดยไม่เคยกินอาหารหลัก

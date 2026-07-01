# อายุขัยของมนุษย์ขึ้นอยู่กับอะไร — รายงานสรุปงานวิจัย (Literature Review)

**จัดทำ:** 2026-07-01 · **สำหรับโครงงาน:** artificial-evolution (ALife → YSC/ISEF)
**เป้าหมาย:** สรุปหลักฐานที่ "พิสูจน์แล้ว" ว่าอายุขัยของสิ่งมีชีวิต (เน้นมนุษย์) ถูกกำหนดโดยปัจจัยอะไรบ้าง เพื่อนำมาออกแบบกลไก aging/lifespan ในโมเดลจำลองของเรา

> **หมายเหตุความซื่อสัตย์ทางวิทยาศาสตร์:** ปัจจัยด้านล่างแยกระดับความเชื่อมั่นชัดเจน — บางอย่าง "พิสูจน์แน่นในมนุษย์", บางอย่าง "แน่นในสัตว์ทดลองแต่ยังไม่ยืนยันในมนุษย์", และบางอย่าง "ยังถกเถียง" อย่านำไปเขียนในรายงานประกวดโดยตัดคำ caveat ออก เพราะจุดแข็งของงานเราคือความตรงไปตรงมา

---

## สารบัญ
1. [ตารางสรุป 6 ปัจจัยหลัก](#1-ตารางสรุป-6-ปัจจัยหลัก)
2. [สรุปรายเปเปอร์อย่างละเอียด](#2-สรุปรายเปเปอร์อย่างละเอียด)
3. [สังเคราะห์: อะไรพิสูจน์แล้ว vs ยังถกเถียง](#3-สังเคราะห์-อะไรพิสูจน์แล้ว-vs-ยังถกเถียง)
4. [การนำไปใช้ในโมเดล ALife ของเรา](#4-การนำไปใช้ในโมเดล-alife-ของเรา)
5. [รายการอ้างอิงทั้งหมด + ลิงก์](#5-รายการอ้างอิงทั้งหมด--ลิงก์)

---

## 1. ตารางสรุป 6 ปัจจัยหลัก

| # | ปัจจัย | สรุปหนึ่งบรรทัด | ระดับหลักฐาน | เปเปอร์หลัก |
|---|--------|----------------|--------------|-------------|
| 1 | **วิถีชีวิต** (บุหรี่/อาหาร/ออกกำลัง/เหล้า/น้ำหนัก) | ตัวแปรที่พิสูจน์แน่นที่สุดในมนุษย์ ครบ 5 ข้อดี +12–14 ปี | ⭐⭐⭐ | Li 2018; Stenholm 2016 |
| 2 | **พันธุกรรม (heritability)** | ยีนมีผลจริง แต่ %ยังถกเถียง (เดิม ~25%, ใหม่ ~50%) | ⭐⭐⭐ ว่ามีผล / ⭐ ตัวเลข | Herskind 1996; Science 2025 |
| 3 | **Trade-off พลังงาน** (สืบพันธุ์/โต ↔ ซ่อมแซม) | พลังงานจำกัด ทุ่มสืบพันธุ์มาก → ซ่อมตัวน้อย → แก่เร็ว | ⭐⭐⭐ (โต) / ⭐⭐ (สืบพันธุ์) | Kirkwood 1977; Yuan 2023 |
| 4 | **เมตาบอลิซึม & ขนาดตัว** | ข้ามสปีชีส์ตัวใหญ่อยู่นาน; ในสปีชีส์เดียวตัวใหญ่/โตเร็วอายุสั้น | ⭐⭐⭐ รูปแบบ / ⭐⭐ กลไก | Speakman 2005; Hulbert 2007; Kitazoe 2017 |
| 5 | **การจำกัดแคลอรี (CR)** | ยืดอายุในสัตว์ชัด; ในคนพิสูจน์แค่ "ชะลอมาร์กเกอร์ความแก่" | ⭐⭐⭐ (สัตว์) / ⭐⭐ (คน) | Ravussin 2015; Waziry 2023 |
| 6 | **กลไกระดับเซลล์ (Hallmarks of aging)** | แผนที่กลไกความแก่ 12 อย่าง (เทโลเมียร์, DNA, เซลล์ชรา ฯลฯ) | ⭐⭐⭐ กรอบมาตรฐาน | López-Otín 2013/2023 |

ระดับหลักฐาน: ⭐⭐⭐ = พิสูจน์แน่น/ยอมรับกว้าง · ⭐⭐ = หลักฐานดีแต่มีข้อจำกัด · ⭐ = ยังถกเถียง/ตัวเลขไม่นิ่ง

---

## 2. สรุปรายเปเปอร์อย่างละเอียด

### ปัจจัยที่ 1 — วิถีชีวิต (Lifestyle) 🟢 แข็งแรงที่สุดในมนุษย์

#### 📄 Li Y, Pan A, Wang DD, et al. (2018). *Impact of Healthy Lifestyle Factors on Life Expectancies in the US Population.* **Circulation** 138(4):345–355.
- **ทำอะไร:** ศึกษาแบบ prospective cohort ในผู้ใหญ่อเมริกัน ~123,000 คน (Nurses' Health Study + Health Professionals Follow-up Study) ติดตามหลายสิบปี ดู "ปัจจัยเสี่ยงต่ำ" 5 ข้อ ได้แก่ (1) ไม่สูบบุหรี่ (2) BMI 18.5–24.9 (3) ออกกำลังระดับปานกลาง–หนัก ≥30 นาที/วัน (4) ดื่มแอลกอฮอล์พอประมาณ (5) คุณภาพอาหารดี (top 40% ของ Alternate Healthy Eating Index)
- **ผลหลัก:** ที่อายุ 50 ปี คนที่ทำครบทั้ง 5 ข้อ เทียบกับไม่ทำเลย มีอายุคาดเฉลี่ยยาวขึ้น **~14.0 ปีในผู้หญิง** (93.1 vs 79.0) และ **~12.2 ปีในผู้ชาย** (87.6 vs 75.5) และเห็นความสัมพันธ์แบบ **dose-response** (ทำมากข้อ ยิ่งอยู่นาน)
- **ระดับความเชื่อมั่น:** ⭐⭐⭐ กลุ่มตัวอย่างใหญ่มาก ติดตามยาว **ข้อจำกัด:** เป็นการศึกษาเชิงสังเกต (observational) → บอก "ความสัมพันธ์" ไม่ใช่ "เหตุ-ผล" 100% (อาจมี confounder)
- **ใช้กับงานเรา:** ยืนยันหลักการว่า "พฤติกรรม/สภาพแวดล้อม" มีผลต่ออายุขัยมากกว่าพันธุกรรมล้วน ๆ — ในซิมของเรา ปัจจัยสภาพแวดล้อม (อาหาร, การเคลื่อนที่, ความเครียดจากการแข่งขัน) จึงควรมีน้ำหนักต่อ lifespan ของ agent

#### 📄 Stenholm S, Head J, Kivimäki M, et al. (2016). *Smoking, physical inactivity and obesity as predictors of healthy and disease-free life expectancy between ages 50 and 75: a multicohort study.* **International Journal of Epidemiology** 45(4):1260–1270. *(Open Access, CC BY)*
- **ทำอะไร:** รวมข้อมูลหลาย cohort ในยุโรป ดูว่าปัจจัยเสี่ยง 3 ตัว (สูบบุหรี่, ไม่ออกกำลัง, อ้วน) ทำนาย "จำนวนปีที่มีชีวิตแบบ**ไม่มีโรคเรื้อรัง**" (disease-free life expectancy) ช่วงอายุ 50–75 ได้แค่ไหน
- **ผลหลัก:** แต่ละปัจจัยเสี่ยงตัดทั้ง "อายุขัย" และ "ปีสุขภาพดี" อย่างมีนัยสำคัญ และเมื่อมีปัจจัยเสี่ยงหลายตัวพร้อมกัน ผลเสียยิ่งทวีคูณ — เน้นว่าไม่ใช่แค่ "อยู่นาน" แต่ "อยู่แบบสุขภาพดี" ก็ขึ้นกับพฤติกรรม
- **ระดับความเชื่อมั่น:** ⭐⭐⭐ (multicohort, จำนวนมาก)
- **ใช้กับงานเรา:** แนวคิด **healthspan ≠ lifespan** (ช่วงมีสุขภาพดี ≠ ช่วงชีวิตทั้งหมด) — เราอาจแยกวัด "อายุที่ agent ยัง productive/สืบพันธุ์ได้" ออกจาก "อายุตายจริง"

---

### ปัจจัยที่ 2 — พันธุกรรม (Heritability) 🟡 มีผลจริง แต่ตัวเลขยังถกเถียง

#### 📄 Herskind AM, et al. (1996). *The heritability of human longevity: a population-based study of 2872 Danish twin pairs born 1870–1900.* **Human Genetics** 97(3):319–323.
- **ทำอะไร:** เปรียบเทียบความคล้ายของอายุขัยระหว่างแฝดแท้ (identical) กับแฝดเทียม (fraternal) ในแฝดเดนมาร์ก 2,872 คู่
- **ผลหลัก:** heritability ของอายุขัย ≈ **0.26 (ชาย), 0.23 (หญิง)** → นี่คือค่าคลาสสิกที่อ้างกันมานานว่า **"ยีนกำหนดอายุขัยราว ~25% ที่เหลือเป็นสิ่งแวดล้อม/โชค"**
- **ระดับความเชื่อมั่น:** ⭐⭐⭐ (เป็น baseline มาตรฐานที่อ้างมา ~30 ปี)

#### 📄 (2025). *Heritability of intrinsic human life span is about 50% when confounding factors are addressed.* **Science** (doi:10.1126/science.adz1187) + พรีปรินต์ bioRxiv 2025.04.20.649385
- **ทำอะไร:** ใช้โมเดลคณิตศาสตร์กับข้อมูลแฝด (ทั้งที่โตด้วยกันและแยกกันโต) แล้ว**หักส่วน "การตายจากปัจจัยภายนอก"** (extrinsic mortality เช่น อุบัติเหตุ โรคระบาด สงคราม) ออก เหลือเฉพาะ "การตายจากภายใน" (intrinsic)
- **ผลหลัก:** heritability ของ intrinsic lifespan ≈ **50–55%** สูงกว่าค่าคลาสสิกเท่าตัว โดยชี้ว่างานเก่าประเมินต่ำเพราะการตายจากอุบัติเหตุ/โรคระบาดไป "เจือจาง" สัญญาณพันธุกรรม
- **ระดับความเชื่อมั่น:** ⭐ (งานใหม่ปี 2025 ยังต้องรอการยืนยันซ้ำ/ถกเถียงในวงการ)
- **สรุปที่ปลอดภัยสำหรับเขียนรายงาน:** *"พันธุกรรมมีผลต่ออายุขัยจริง สัดส่วนราว 25–50% ขึ้นกับวิธีนับ (โดยเฉพาะการจัดการ extrinsic mortality) — แต่ทั้งสองค่าล้วนบอกว่า 'ปัจจัยที่ไม่ใช่ยีน' (สิ่งแวดล้อม พฤติกรรม โชค) ยังสำคัญมาก"*
- **ใช้กับงานเรา:** ประเด็น extrinsic vs intrinsic mortality **ตรงกับซิมเรามาก** — ในโมเดล เราแยก "ตายเพราะอดอาหาร/ถูกแย่งพื้นที่/สุ่มตาย (extrinsic)" ออกจาก "ตายเพราะแก่ตามพันธุกรรม (intrinsic)" ได้ และวัด heritability ของ lifespan ใน agent ได้จริงเพราะเรารู้ genome ทุกตัว

---

### ปัจจัยที่ 3 — Trade-off พลังงาน (Disposable Soma) 🟢 ตรงกับ energy economy ของเราที่สุด

#### 📄 Kirkwood TBL (1977). *Evolution of ageing.* **Nature** 270:301–304. — ต้นกำเนิดทฤษฎี Disposable Soma
- **แนวคิดหลัก:** สิ่งมีชีวิตมีพลังงาน/ทรัพยากรจำกัด ต้อง "จัดสรร" ระหว่าง 3 อย่าง: **การเติบโต (growth)**, **การสืบพันธุ์ (reproduction)**, และ **การซ่อมแซม-ดูแลร่างกาย (somatic maintenance/repair)** วิวัฒนาการเลือก "ลงทุนสืบพันธุ์ให้สำเร็จ" มากกว่า "ซ่อมร่างให้อมตะ" เพราะในธรรมชาติสัตว์มักตายจากปัจจัยภายนอกก่อนอยู่ดี → ร่างกาย (soma) จึงเป็นของ "ใช้แล้วทิ้ง" (disposable) → เกิดการสะสมความเสียหาย → แก่และตาย
- **ผลเชิงทำนาย:** ทุ่มพลังงานให้สืบพันธุ์/โตเร็ว → เหลือให้ซ่อมแซมน้อย → อายุสั้นลง (trade-off)
- **ระดับความเชื่อมั่น:** ⭐⭐⭐ ในระดับ "โต ↔ อายุ" (พิสูจน์แน่น) / ⭐⭐ ในระดับ "สืบพันธุ์ ↔ อายุ" ในมนุษย์ (ยังไม่สรุปเด็ดขาด)

#### 📄 Yuan R, Hascup E, Hascup K, et al. (2023). *Relationships among Development, Growth, Body Size, Reproduction, Aging, and Longevity — Trade-Offs and Pace-Of-Life.* **Biochemistry (Moscow)** 88(11):1692–1703. *(Open Access)*
- **ทำอะไร:** รีวิวสังเคราะห์หลักฐานเชิงประจักษ์เรื่อง trade-off ระหว่าง โต/ขนาดตัว/สืบพันธุ์/ความแก่ ภายใต้กรอบ **"pace of life"** (จังหวะชีวิตเร็ว = โตเร็ว สืบพันธุ์เยอะ อายุสั้น; จังหวะช้า = ตรงข้าม)
- **ผลหลัก:** ยืนยันว่ามี trade-off จริงในหลายสปีชีส์ และ "ความเร็วของการเติบโต" เป็นตัวทำนายอายุขัยที่ดี (โตเร็ว → ความเสียหายสะสมเร็ว → อายุสั้น)
- **ใช้กับงานเรา:** เป็น**รีวิวอ้างอิงชั้นดี**ที่เชื่อม Kirkwood เข้ากับข้อมูลจริง เหมาะใช้อ้างในส่วน background ของรายงานประกวด

---

### ปัจจัยที่ 4 — เมตาบอลิซึม & ขนาดตัว 🟢 ตรงกับ energy economy ของเรา

#### 📄 Speakman JR (2005). *Body size, energy metabolism and lifespan.* **Journal of Experimental Biology** 208:1717–1730.
- **ตัวเลข scaling ที่สำคัญ (จำไว้ใช้ตรวจสอบซิม):**
  - อายุขัย ∝ (มวลกาย)^**0.15–0.3**  → ตัวใหญ่อยู่นานกว่า (ข้ามสปีชีส์)
  - อัตราเมตาบอลิซึมขณะพัก (RMR) ∝ (มวลกาย)^**0.66–0.8**  (สอดคล้อง Kleiber ~¾)
  - เมตาบอลิซึมต่อกรัม (mass-specific) ∝ (มวลกาย)^**−0.2 ถึง −0.33** → ตัวใหญ่เผาผลาญต่อกรัม "ช้ากว่า"
- **ผลหลัก & ความละเอียดสำคัญ:** สนับสนุนทฤษฎี "rate of living" **บางส่วน** (สัตว์เลี้ยงลูกด้วยนมที่เผาผลาญเร็วเกินขนาดตัว → ตายเร็วกว่า, P<0.001) **แต่ค้านบางส่วน** — **นกเผาผลาญพลังงานต่อกรัมมากกว่าสัตว์เลี้ยงลูกด้วยนมขนาดเท่ากัน ~3.5 เท่า แต่กลับอายุยืนกว่า** → แปลว่า "เผาผลาญเร็ว = ตายเร็ว" ไม่จริงเสมอไป
- **ระดับความเชื่อมั่น:** ⭐⭐⭐ (รูปแบบ scaling) / ⭐⭐ (กลไกเชิงสาเหตุ)
- **ใช้กับงานเรา:** **นี่คือ benchmark ที่เอามาตรวจซิมได้ตรง ๆ** — ถ้าเราให้ agent มี "ขนาด" และ "อัตราเผาผลาญ" แล้ววัดว่า emergent lifespan ในซิมออกมาสัมพันธ์กับมวลด้วย exponent ~0.15–0.3 หรือไม่ = การ validate โมเดลกับกฎชีววิทยาจริง (จุดขายใหญ่สำหรับ ISEF)

#### 📄 Hulbert AJ, Pamplona R, Buffenstein R, Buttemer WA (2007). *Life and Death: Metabolic Rate, Membrane Composition, and Life Span of Animals.* **Physiological Reviews** 87(4):1175–1213.
- **แนวคิดหลัก ("membrane pacemaker theory"):** ไม่ใช่แค่ "อัตราเผาผลาญ" ที่กำหนดอายุ แต่เป็น **องค์ประกอบของไขมันในเยื่อหุ้มเซลล์** — เยื่อที่มีกรดไขมันไม่อิ่มตัวสูง (เช่น DHA) จะถูกออกซิไดซ์ (peroxidation) ง่าย → เสียหายเร็ว → อายุสั้น; สัตว์อายุยืนมักมีเยื่อหุ้มเซลล์ที่ทน peroxidation กว่า
- **ทำไมสำคัญ:** อธิบาย "ข้อยกเว้น" ของ rate-of-living (เช่น นก, หนูตุ่นเปลือย naked mole-rat ที่อายุยืนผิดปกติ) ได้ดีกว่าทฤษฎีเผาผลาญล้วน ๆ
- **ระดับความเชื่อมั่น:** ⭐⭐ (ทฤษฎีที่มีหลักฐานหนุนดี แต่ยังไม่ใช่ข้อสรุปเดียว)
- **ใช้กับงานเรา:** สอนบทเรียนสำคัญ — **"อัตราการสะสมความเสียหาย" อาจสำคัญกว่า "อัตราการใช้พลังงาน"** → ในซิม ตัวแปร damage-accumulation ควรแยกจาก energy-burn-rate

#### 📄 Kitazoe Y, Hasegawa M, Tanaka M (2017). *Mitochondrial determinants of mammalian longevity.* **Open Biology** 7(10):170083. *(Open Access, Royal Society)*
- **ทำอะไร:** วิเคราะห์ความสัมพันธ์ระหว่างคุณสมบัติของ**ไมโทคอนเดรีย/mtDNA** กับอายุขัยสูงสุดในสัตว์เลี้ยงลูกด้วยนม
- **ผลหลัก:** อายุขัยเชื่อมโยงกับประสิทธิภาพของไมโทคอนเดรียและอัตราการผลิตอนุมูลอิสระ (เทียบคลาสสิก: หนูกับนกพิราบมวลใกล้กัน แต่ไมโทคอนเดรียหนูผลิตอนุมูลอิสระมากกว่า ~10 เท่า → หนูอายุ ~4 ปี, นกพิราบ ~40 ปี)
- **ระดับความเชื่อมั่น:** ⭐⭐
- **ใช้กับงานเรา:** สนับสนุนการมีตัวแปร "อัตราการสะสมความเสียหายจากเมตาบอลิซึม" ต่อหน่วยพลังงานที่ใช้

---

### ปัจจัยที่ 5 — การจำกัดแคลอรี (Caloric Restriction) 🟡 แน่นในสัตว์ ยังไม่ยืนยันในคน

#### 📄 Ravussin E, Redman LM, Rochon J, et al. (2015). *A 2-Year Randomized Controlled Trial of Human Caloric Restriction: Feasibility and Effects on Predictors of Health Span and Longevity.* **J Gerontol A Biol Sci Med Sci** 70(9):1097–1104. — การทดลอง CALERIE-2
- **ทำอะไร:** **RCT** (randomized controlled trial — มาตรฐานทองของการพิสูจน์เหตุ-ผล) ครั้งแรกในคนสุขภาพดีที่ไม่อ้วน ให้ลดแคลอรีลง (ทำได้จริง ~**12%** เฉลี่ยตลอด 2 ปี)
- **ผลหลัก:** ปรับปรุงตัวชี้วัดความเสี่ยง (cardiometabolic) หลายตัว, พิสูจน์ว่า "คนทั่วไปทำ CR ระยะยาวได้จริง"
- **ระดับความเชื่อมั่น:** ⭐⭐⭐ (เป็น RCT) แต่วัด "ตัวทำนายสุขภาพ/อายุ" ไม่ใช่ "อายุขัยจริง"

#### 📄 Waziry R, et al. (2023). *Effect of long-term caloric restriction on the pace of biological aging in healthy adults: the CALERIE-2 randomized clinical trial.* **Nature Aging** 3:248–257. *(ฉบับ Open Access ที่โหลดได้ในโฟลเดอร์นี้คือบทคัดย่อ Innovation in Aging 2023, Belsky D — PMC10737863)*
- **ผลหลัก:** CR ~12% เป็นเวลา 2 ปี **ชะลอ "อัตราความแก่ทางชีวภาพ"** ที่วัดด้วยนาฬิกาเอพิเจเนติกส์ **DunedinPACE** อย่างมีนัยสำคัญ — เป็นหลักฐาน RCT ชิ้นแรก ๆ ที่หนุน "geroscience hypothesis" ในมนุษย์
- **⚠️ caveat สำคัญมาก (ต้องเขียนไว้):** ในมนุษย์ CR พิสูจน์แล้วแค่ว่า **"ชะลอมาร์กเกอร์ความแก่"** — **ยังไม่มีหลักฐานว่า "ยืดอายุขัยจริง/ลดอัตราตาย"** (ต้องติดตามยาวกว่านี้มาก) ส่วนในสัตว์ทดลอง (หนู, ยีสต์, หนอน, ลิง) การยืดอายุจาก CR นั้น "แน่น" กว่าเยอะ
- **ใช้กับงานเรา:** **ทดลองง่ายและทรงพลังในซิม** — ลด food intake ของ agent กลุ่มหนึ่งแล้ววัดว่า lifespan ยืดขึ้นไหม เทียบกับ CALERIE เป็นการเชื่อมผลซิมกับ RCT จริง

---

### ปัจจัยที่ 6 — กลไกระดับเซลล์ (Hallmarks of Aging) 🟢 กรอบมาตรฐานของวงการ

#### 📄 López-Otín C, Blasco MA, Partridge L, Serrano M, Kroemer G (2013). *The Hallmarks of Aging.* **Cell** 153(6):1194–1217. → ฉบับปรับปรุง (2023) *Hallmarks of aging: An expanding universe.* **Cell** 186(2):243–278.
- **สาระ:** จัดระเบียบ "กลไกที่ทำให้แก่" เป็นหมวดหมู่ชัดเจน ฉบับ 2013 มี **9 ข้อ**, ฉบับ 2023 เพิ่มเป็น **12 ข้อ**:
  1. Genomic instability (DNA เสียหายสะสม)
  2. Telomere attrition (เทโลเมียร์สั้นลง)
  3. Epigenetic alterations
  4. Loss of proteostasis (โปรตีนพับผิด)
  5. **Disabled macroautophagy** *(เพิ่ม 2023)*
  6. Deregulated nutrient-sensing (ระบบรับรู้สารอาหารรวน — เชื่อมกับ CR!)
  7. Mitochondrial dysfunction
  8. Cellular senescence (เซลล์ชราหยุดแบ่งตัว)
  9. Stem cell exhaustion
  10. Altered intercellular communication
  11. **Chronic inflammation** *(เพิ่ม 2023)*
  12. **Dysbiosis** (จุลินทรีย์ในลำไส้เสียสมดุล) *(เพิ่ม 2023)*
- **แบ่ง 3 กลุ่ม:** primary (ต้นเหตุความเสียหาย) → antagonistic (การตอบสนองที่กลับมาทำร้าย) → integrative (ผลรวมที่แสดงออกเป็นความแก่)
- **ระดับความเชื่อมั่น:** ⭐⭐⭐ (เป็น "แผนที่" มาตรฐานที่ใช้อ้างทั่ววงการ aging research)
- **ใช้กับงานเรา:** ไม่ต้อง model ครบ 12 ข้อ (ซับซ้อนเกิน) แต่ใช้เป็น "เมนู" เลือก 1–2 กลไกมาทำเป็นตัวแปร damage ในซิม เช่น **nutrient-sensing (เชื่อม CR)** และ **damage accumulation (เชื่อม genomic instability)**

---

## 3. สังเคราะห์: อะไรพิสูจน์แล้ว vs ยังถกเถียง

### ✅ พิสูจน์แน่น (เขียนได้เต็มปาก)
- **วิถีชีวิตมีผลใหญ่มากต่ออายุขัยมนุษย์** — สูบบุหรี่/ไม่ออกกำลัง/อ้วน/อาหารแย่ ตัดอายุได้ >10 ปี (Li 2018, Stenholm 2016)
- **มี trade-off ระหว่าง "โตเร็ว/ตัวใหญ่" กับ "อายุขัย" ภายในสปีชีส์** (สุนัขพันธุ์ใหญ่อายุสั้นกว่าพันธุ์เล็ก; Yuan 2023)
- **ข้ามสปีชีส์ ตัวใหญ่มักอายุยืนกว่า** ตามกฎ scaling (อายุ ∝ มวล^0.15–0.3; Speakman 2005)
- **พันธุกรรมมีส่วนจริง** (อย่างน้อย ~25%; Herskind 1996)
- **CR ยืดอายุในสัตว์ทดลอง** และ **ชะลอมาร์กเกอร์ความแก่ในคน** (Ravussin 2015, Waziry 2023)

### ⚠️ ยังถกเถียง / ต้องใส่ caveat
- **สัดส่วน heritability ที่แท้จริง** (25% vs 50%) — ขึ้นกับวิธีนับ extrinsic mortality (Science 2025 ยังใหม่)
- **"เผาผลาญเร็ว = ตายเร็ว" (rate of living)** — จริงบางกลุ่ม แต่ค้านด้วยนก/หนูตุ่นเปลือย (Speakman 2005, Hulbert 2007)
- **CR ยืด "อายุขัยจริง" ในมนุษย์หรือไม่** — ยังไม่มีหลักฐาน (แค่มาร์กเกอร์)
- **Trade-off "สืบพันธุ์ ↔ อายุ" ในมนุษย์** — ยังไม่สรุปเด็ดขาด

### 🧭 ข้อสรุปหนึ่งประโยคสำหรับงานเรา
> อายุขัยไม่ได้ถูกกำหนดโดยปัจจัยเดียว แต่เป็นผลรวมของ **(ก) การจัดสรรพลังงานภายใน** (โต/สืบพันธุ์ vs ซ่อมแซม), **(ข) อัตราการสะสมความเสียหาย** (เชื่อมกับเมตาบอลิซึม/ขนาดตัว), **(ค) พันธุกรรม**, และ **(ง) สภาพแวดล้อม/พฤติกรรม** — ซึ่ง **ทั้ง 4 กลุ่มนี้จำลองได้ในโมเดล ALife ของเรา**

---

## 4. การนำไปใช้ในโมเดล ALife ของเรา

ปัจจัยที่ **แปลงเป็นสมการในซิมได้เลย** และมีหลักฐานหนุน (เชื่อมกับ energy economy + reproduction ที่เรามีอยู่):

### 4.1 แกนหลัก — Disposable Soma budget (อ้าง Kirkwood 1977)
ให้ agent แต่ละตัวมีงบพลังงานต่อ tick แล้วแบ่ง 3 ทาง:
```
E_total  =  E_growth  +  E_reproduction  +  E_maintenance
```
- ถ้า E_maintenance ต่ำ → damage สะสมเร็ว → ตายเร็ว
- ให้ยีน (genome) กำหนด "สัดส่วนการจัดสรร" เป็น trait ที่วิวัฒนาการได้
- **สมมติฐานทดสอบได้:** วิวัฒนาการจะเลือกสัดส่วน maintenance สูงขึ้นเมื่อ extrinsic mortality ต่ำ (สภาพแวดล้อมปลอดภัย) — ตรงตามทฤษฎี

### 4.2 Damage accumulation ↔ metabolism (อ้าง Speakman 2005, Hulbert 2007, Kitazoe 2017)
```
damage(t+1) = damage(t) + k_burn * metabolic_rate  −  E_maintenance * repair_efficiency
death เมื่อ damage ≥ threshold (intrinsic death)
```
- **บทเรียนจาก Hulbert:** แยก `k_burn` (อัตราสะสมความเสียหายต่อพลังงาน) ออกจาก `metabolic_rate` เอง → ให้เป็นคนละยีน จะได้จำลอง "ข้อยกเว้นแบบนก" (เผาผลาญเยอะแต่ damage ต่ำ) ได้

### 4.3 Body-size scaling (อ้าง Speakman 2005) — ตัว validate โมเดล
- ถ้า agent มี trait "ขนาด": ตั้ง metabolic_rate ∝ size^0.75 (Kleiber)
- **การตรวจสอบ:** วัด emergent lifespan แล้วดูว่า `lifespan ∝ size^0.15–0.3` ออกมาเองไหม → ถ้าใช่ = โมเดลสอดคล้องชีววิทยาจริง (**จุดขาย ISEF**)

### 4.4 Caloric restriction experiment (อ้าง Ravussin 2015, Waziry 2023)
- ลด food intake ของ agent กลุ่มทดลอง ~12–40% แล้ววัด lifespan เทียบกลุ่มควบคุม
- **คาดการณ์:** ถ้าโมเดลถูก จะเห็น lifespan ยืดขึ้น (เพราะ metabolic_rate ลด → damage สะสมช้า) — reproduce ผล CR ได้ในซิม

### 4.5 Intrinsic vs extrinsic mortality + heritability (อ้าง Herskind 1996, Science 2025)
- แยกนับ "ตายเพราะแก่ (intrinsic)" กับ "ตายเพราะอดอาหาร/แย่งพื้นที่/สุ่ม (extrinsic)"
- เพราะเรารู้ genome ทุกตัว → **คำนวณ heritability ของ lifespan ในซิมได้จริง** แล้วเทียบว่าตรงตามที่ Science 2025 ทำนายไหม (heritability ของ intrinsic สูงกว่า overall)

### 4.6 กลไกที่ควรใส่ (เลือกจาก Hallmarks — López-Otín)
เลือกแค่ 1–2 พอ อย่าใส่ครบ 12: **deregulated nutrient-sensing** (เชื่อม CR) + **damage/genomic instability** (เชื่อม maintenance) — ครอบคลุมและ traceable

---

## 5. รายการอ้างอิงทั้งหมด + ลิงก์

| # | อ้างอิง | ลิงก์ | PDF ในโฟลเดอร์นี้? |
|---|---------|-------|:---:|
| 1 | Li Y, et al. (2018). Impact of Healthy Lifestyle Factors on Life Expectancies in the US Population. *Circulation* 138(4):345–355. | [PMC6207481](https://pmc.ncbi.nlm.nih.gov/articles/PMC6207481/) | ⛔ paywall/robot |
| 2 | Stenholm S, et al. (2016). Smoking, physical inactivity and obesity... disease-free life expectancy. *Int J Epidemiol* 45(4):1260–1270. | [PMC6937009](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6937009/) | ✅ OA (ดูสคริปต์) |
| 3 | Herskind AM, et al. (1996). The heritability of human longevity: 2872 Danish twin pairs. *Hum Genet* 97(3):319–323. | [PubMed 8786073](https://pubmed.ncbi.nlm.nih.gov/8786073/) | ⛔ paywall |
| 4 | (2025). Heritability of intrinsic human life span is about 50%... *Science*. | [science.org/adz1187](https://www.science.org/doi/10.1126/science.adz1187) · [bioRxiv](https://www.biorxiv.org/content/10.1101/2025.04.20.649385v1) | ⛔ paywall/403 |
| 5 | Kirkwood TBL (1977). Evolution of ageing. *Nature* 270:301–304. | [nature.com](https://www.nature.com/articles/270301a0) · [Disposable soma (Wikipedia)](https://en.wikipedia.org/wiki/Disposable_soma_theory_of_aging) | ⛔ paywall |
| 6 | Yuan R, et al. (2023). Relationships among Development, Growth, Body Size, Reproduction, Aging, and Longevity. *Biochemistry (Mosc)* 88(11):1692–1703. | [PMC10792675](https://pmc.ncbi.nlm.nih.gov/articles/PMC10792675/) | ✅ OA (ดูสคริปต์) |
| 7 | Speakman JR (2005). Body size, energy metabolism and lifespan. *J Exp Biol* 208:1717–1730. | [journals.biologists.com](https://journals.biologists.com/jeb/article/208/9/1717/9377/) | ⚠️ ฟรีอ่าน (ดูสคริปต์) |
| 8 | Hulbert AJ, et al. (2007). Life and Death: Metabolic Rate, Membrane Composition, and Life Span. *Physiol Rev* 87(4):1175–1213. | [journals.physiology.org](https://journals.physiology.org/doi/full/10.1152/physrev.00047.2006) | ⚠️ ฟรีอ่าน |
| 9 | Kitazoe Y, et al. (2017). Mitochondrial determinants of mammalian longevity. *Open Biol* 7(10):170083. | [PMC5666079](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5666079/) | ✅ OA (ดูสคริปต์) |
| 10 | Ravussin E, et al. (2015). A 2-Year RCT of Human Caloric Restriction (CALERIE). *J Gerontol A* 70(9):1097–1104. | [PMC4841173](https://pmc.ncbi.nlm.nih.gov/articles/PMC4841173/) | ⛔ paywall/robot |
| 11 | Waziry R, et al. (2023). Effect of long-term caloric restriction on the pace of biological aging (CALERIE-2). *Nat Aging* 3:248–257. | [PMC10737863 (abstract)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10737863/) | ✅ OA (abstract) |
| 12 | López-Otín C, et al. (2013). The Hallmarks of Aging. *Cell* 153(6):1194–1217. | [PMC3836174](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3836174/) | ⛔ paywall/robot |
| 13 | López-Otín C, et al. (2023). Hallmarks of aging: An expanding universe. *Cell* 186(2):243–278. | [PubMed 36599349](https://pubmed.ncbi.nlm.nih.gov/36599349/) | ⛔ paywall |

**หมายเหตุการโหลด PDF:** สภาพแวดล้อมที่รันสคริปต์นี้ (sandbox) บล็อกการดาวน์โหลดไฟล์ binary จึงยังไม่มี PDF จริงในโฟลเดอร์ ให้รัน `download_pdfs.ps1` บนเครื่องของคุณ (เน็ตปกติ) เพื่อดึงฉบับ Open Access (#2, #6, #9, #11) ส่วนที่เหลือเป็น paywall — เปิดลิงก์ในตารางแล้วโหลดผ่าน browser (ถ้ามีสิทธิ์เข้าถึงผ่านโรงเรียน/ห้องสมุด) รายละเอียดใน `README.md`

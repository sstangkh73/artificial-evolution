# Red-team รอบที่ 2: ต้นฉบับฉบับแก้ *Correct State Information Is Not Enough*

- เอกสารที่ตรวจ: `submission/manuscript_initial_submission_draft.pdf` (37 หน้า, build 2026-09-16; ไฟล์แก้ไขยังไม่ได้ commit)
- เทียบกับ: `REDTEAM_manuscript_initial_submission_2026-09-15.th.md` (รอบที่ 1)
- ผู้ตรวจ: Claude Opus 5 (model ID `claude-opus-5`) ใน Claude Code desktop app, 2026-09-16

---

## 0. สรุป

**คำตัดสิน: ดีขึ้นมาก ประเด็นร้ายแรงทั้ง 4 ข้อของรอบแรกได้รับการแก้แล้ว** ต้นฉบับตอนนี้บอกผลตรงกับข้อมูล ข้อจำกัดเฉพาะเจาะจง และตัวเลขใหม่ที่ผมสุ่มตรวจถูกทุกตัว

**ยังส่งไม่ได้ด้วยเหตุผลเชิงเอกสาร:**
- placeholder 6 จุดยังอยู่ (`submission_ready: false`)
- archive bundle ต้อง build ใหม่
- **ลำดับหมายเลขรูปไม่ตรงลำดับการอ้าง** (R4)
- **ข้อความ "For this major revision"** ใน Data Availability ทำให้ submission ครั้งแรกดูเหมือนฉบับแก้ (R8)

ประเด็นทางวิทยาศาสตร์ที่เหลือเป็นระดับ major/minor ไม่มีข้อไหนเปลี่ยนข้อสรุปหลัก (หมวด 2)

---

## 1. สถานะของประเด็นจากรอบแรก

| รอบ 1 | สถานะ | หลักฐานในฉบับแก้ |
|---|---|---|
| C1 energy 10 = regime change + ceiling | ✅ แก้ | §3.3, Table 2, Fig 4A มีเส้น policy boundary, §4.3 และ limitations |
| C2 ชื่อเรื่อง/abstract เกินผล | ✅ แก้ | ชื่อใหม่ และ abstract เปิดด้วยผลลบเทียบ sham |
| C3 control ไม่ใช่อย่างที่บรรยาย | ✅ แก้ | §2.1–2.3 (net 6, split staple keys), §3.5, Table 3, Fig 1 labels |
| C4 กลไกขัดกับ intake | ✅ แก้ | §4.2 เขียนใหม่ พร้อมระบุว่า causal path ยังไม่รู้ |
| M1 ผลรองที่ prereg สัญญา | ✅ ส่วนใหญ่ | Table 2/3 + CSV (learned values ต่อ key อยู่ใน CSV เท่านั้น) |
| M2 คำทำนายที่ไม่เป็นจริง | ✅ แก้ | §1.4 H2/H6.1 ระบุทิศ, §3.6 prediction audit |
| M3 D ของแขนที่มองไม่เห็นอายุ | 🟡 แก้บางส่วน | ดู R1 |
| M4 effect size/power | ✅ แก้ | d_z, power 0.69, minimum-effect test p = 0.607 |
| M5 encounter gate | ✅ แก้ | §2.5 และ limitations |
| M6 prereg ตรวจสอบภายนอกไม่ได้ | ✅ แก้ | ใช้คำว่า "internally frozen" ทั้งเล่ม |
| M7 โครงเรื่องรวมทุกการทดลอง | 🟡 บางส่วน | E3/E4 ย้ายไป §3.7 แต่ยังอยู่ใน Methods และ Figure 3 เต็มรูป |
| M8 sensitivity | ✅ ระบุเป็นข้อจำกัดเฉพาะ | limitations + next tests |
| M9 วรรณกรรม | ✅ แก้ | เพิ่ม McCallum, Stephens & Krebs, Provenza, Cipollini & Levey |
| Fig 2, Fig 5 legend/label | ✅ แก้ | ตรวจจากภาพ render จริง |

### ตัวเลขใหม่ที่ตรวจซ้ำแล้วว่าถูก

- **d_z ของ B2-B3:** −0.597, −0.544, −0.596, −0.748, +0.146 (คำนวณจาก mean/SD ใน JSON)
- **minimum-effect test เทียบกับ slope 1:** p = 0.607 (ผมรัน sign-flip แบบ one-sided ซ้ำ 200,000 draws ได้ 0.6065)
- **Table 2:** ตรงกับการคำนวณอิสระของผมจาก raw dump ในรอบแรก และ toxin damage = 5 × excess
- **ข้อมูลอื่น:**
  - E1 realized excess 2.114 vs 2.371 (จาก `e1_seed_outcomes.csv`, toxin damage ÷ 5)
  - toxin damage ของ A3O vs A3R ต่างกัน 2.9%
- **DOI ใหม่:**
  - Cipollini & Levey (1997) *Ecology* 78(3):782–798 และ Provenza (1995) *J. Range Manage.* 48(1) ตรงกับ Crossref
  - handle ของ McCallum redirect ได้
  - **ข้อจำกัด:** ผมตรวจแค่ metadata ไม่ได้อ่านเนื้อหา ผู้เขียนต้องยืนยันเองว่า Cipollini & Levey มี "nutrient-toxin titration experiments" จริง
- **test ใหม่** `tests/test_redteam_mechanism_analysis.py` และ `tests/test_redteam_revision_release_inventory.py`: 6 passed
- **Table 2 แสดงผลถูกต้องใน PDF** ผมตรวจจากภาพ render (pdftotext อ่านคอลัมน์เลื่อน แต่เป็นแค่ artifact ของการ extract)

### แก้ข้อผิดพลาดของรายงานรอบแรก

รอบแรกผมเขียนว่า "E1: A2 ได้รับพิษจริงน้อยกว่า A3 34%" ตัวเลข 34% มาจาก `E1_lure_cost_results`:136 ซึ่งเป็น **พิษต่อมื้อ** (0.0483 vs 0.0728) ส่วนพิษรวมต่อ founder น้อยกว่า **11%** (2.114 vs 2.371) ต้นฉบับฉบับแก้ใช้ตัวเลขต่อ founder ถูกต้องแล้ว

---

## 2. ประเด็นที่เหลือหรือเกิดใหม่

### Major

**R1 — "structural noise floor" ถูกเขียนเหมือนข้อเท็จจริง ทั้งที่ยังไม่ได้พิสูจน์สาเหตุ**
- abstract, §3.1, §4.1 และ limitations เขียนว่า re-encounter/exposure "create a structural noise floor of about |0.1|"
- แต่ §3.3 และ limitations ยอมรับว่า unique-item และ first-encounter D "could not be reconstructed" จึงยังไม่มีหลักฐานว่าสาเหตุคือ re-encounter
- ค่านี้เป็น **offset เชิงระบบ** (B1 และ B3 ติดลบทุกระดับพลังงาน CI แคบ) ไม่ใช่ noise
- **แก้:** เปลี่ยนเป็น "a systematic offset of up to about |0.1| in age-blind arms, whose source (candidates: re-encounter counting, starvation-override timing) was not identified" แล้วใช้ถ้อยคำเดียวกันทุกที่

**R2 — Contribution 3 และบางประโยคยังอ้างเกินการออกแบบ**
- Contribution 3 บอกว่า "demonstrates that the survival consequence is an interaction among representation, learning, a relative decision threshold, and resource economy"
  - การทดลองไม่ได้เปลี่ยน learning rule หรือ threshold จึงอ้างว่า *แสดง interaction* ไม่ได้
  - เสนอ: "indicates that … depends on the fixed learning rule and relative threshold, which were not varied"
- §3.2 เขียนว่า "without producing a survival advantage over the equal-capacity sham at any tested level" แต่ที่พลังงาน 10 CI ขึ้นไปถึง +4.85
  - เสนอ: "without a detected survival advantage"

**R3 — การวิเคราะห์ intake แบบยอดรวมตอบคำถามไม่ได้ แต่มีทางเลือกที่ทำได้ทันที**
- §3.3 ใช้ r = 0.994 (staple meals) กับ 0.844 (toxin excess) และยอมรับเองว่าทั้งสองโตตามเวลาที่มีชีวิต ข้อมูลนี้จึงแทบไม่มีข้อมูลเชิงกลไก
- ผมลองทำ post hoc โดยใช้ residual ภายใน cell เดียวกับสคริปต์ (450 seed-arm-energy rows จาก `e6_seed_mechanisms.csv`) แต่เปลี่ยนเป็น **อัตรา**:

| ตัวแปร (within-cell) | r กับ follow-up |
|---|---:|
| staple meals ต่อ tick ที่มีชีวิต | **+0.985** |
| toxin excess ต่อ tick | −0.706 |
| fruit meals ต่อ tick | −0.621 |
| toxin excess ต่อมื้อผลไม้ (ไม่มี follow-up ในตัวหาร) | **−0.483** |

- **ข้อควรระวัง:** อัตราที่หารด้วย follow-up มี spurious negative bias จากตัวหาร
  - staple rate ยังเป็นบวกสูงแม้มี bias นี้ จึงเป็นสัญญาณที่ค่อนข้างแข็ง
  - ส่วน −0.706 และ −0.621 อาจเป็น artifact บางส่วน
  - toxin ต่อมื้อ (−0.48) ไม่มีปัญหานี้
- **แก้:** แทนประโยค "survival tracked cumulative staple intake more closely…" ใน §3.3/§4.2 ด้วยการวิเคราะห์แบบอัตรา โดยติดป้าย post hoc descriptive
  - ภาพที่ได้ชัดกว่าเดิม: seed ที่ founder กินอาหารหลักถี่กว่าและได้พิษต่อมื้อน้อยกว่าอยู่ได้นานกว่า
  - แต่ยังไม่ใช่หลักฐานเชิงสาเหตุ

**R4 — หมายเลขรูปไม่เรียงตามลำดับการอ้างครั้งแรก**
- ลำดับที่อ้างในเนื้อความคือ Figure 2A (§3.1) → 4 (§3.2) → 1 (§3.5) → 5 (§3.5) → 3 (§3.7)
- ลำดับที่รูปปรากฏในเล่มก็เป็น 2, 4, 1, 5, 3
- วารสารส่วนใหญ่ (รวมถึง MIT Press) กำหนดให้รูปเรียงตามลำดับที่อ้าง
- Figure 2 ยังอยู่หน้า 15 **ก่อนหัวข้อ 3. Results**
- **แก้:** เปลี่ยนหมายเลขเป็น 1 = discrimination (เดิม 2), 2 = E6 (เดิม 4), 3 = E1 (เดิม 1), 4 = T2-RB (เดิม 5), 5 = E3/E4 (เดิม 3) และย้ายรูปแรกให้อยู่หลังหัวข้อ Results
- ควรเพิ่มการตรวจลำดับนี้ใน submission auditor ด้วย เพราะ auditor ตรวจแค่หน้าที่มี caption

### Minor

**R5 — ตำแหน่ง policy boundary และคำอธิบายสาเหตุ**
- Fig 4A วางเส้นที่ 9 แต่จุดตัดจริงคือ safe value > 8.33 (0.6v > 5) ควรวางที่ 8.33 หรือระบุใน caption
- limitations เขียนว่า "Pickiness 0.6 **and the starvation override at energy 6** directly create the energy-10 regime boundary"
  - boundary เกิดจาก pickiness × `best_known` เทียบกับค่าอาหารหลัก 5 เท่านั้น
  - starvation override เป็นตัวปรับ ไม่ใช่ตัวสร้าง boundary

**R6 — Fig 1B:** ข้อความ "A3 net fruit value = 6 / observed acceptance = 1.000" ทับจุดข้อมูลและ diamond ของ A3 ควรย้ายลงใต้ข้อมูลหรือใส่ใน caption

**R7 — การจัดหน้า**
- หัวตาราง Table 3 ตัดกลางคำ ("Excess/me al", "Senescenc e") ควรขยายคอลัมน์หรือย่อหัว เช่น "Excess/meal" แบบสองบรรทัดที่ตัดตรงเครื่องหมาย /
- ค่าคณิตศาสตร์ในเนื้อความ (`0.6 x 10 = 6`, `r=0.994`, `d_z=-0.720`) แสดงเป็น monospace code font ควรเป็นตัวเอียงแบบคณิตศาสตร์ (*r* = 0.994, *d*<sub>z</sub> = −0.720, 0.6 × 10)

**R8 — ภาษาภายในกระบวนการหลุดเข้าไปในต้นฉบับ**
- "Supplementary **Red-team** Revision Tables" (§3.1), "red-team mechanism tables" (Supplementary Materials)
- **"For this major revision, …"** (Data and Code Availability) ทั้งที่นี่คือ initial submission บรรณาธิการอาจเข้าใจว่าเป็นการส่งซ้ำ
- **แก้:** ใช้ชื่อกลาง เช่น "Supplementary Mechanism Tables" และเขียน Data Availability ใหม่ให้ไม่อ้างถึง revision ภายใน
- ชื่อไฟล์ใน supplement (`REDTEAM_REVISION_TABLES.en.md`) ควรเปลี่ยนก่อน build archive

**R9 — AI disclosure: ข้อมูลรุ่นที่ขาด ผมให้ได้**
- การตรวจทั้งสองรอบใช้ **Claude Opus 5 (model ID `claude-opus-5`)** ผ่าน **Claude Code desktop app** ในวันที่ 15 และ 16 กันยายน 2026
- แทนข้อความ "model/version was not recorded" และแก้ reference เป็น เช่น *Anthropic. (2026). Claude Opus 5 [Large language model]. https://www.anthropic.com/claude*
- ตรวจรูปแบบ APA ที่วารสารต้องการอีกครั้ง
- เพิ่มรอบที่ 2 นี้ลงใน `AI_USE_LOG.md`

**R10 — ความยาวและความหนาแน่นของ abstract**
- abstract 248 คำ มีตัวเลขราว 15 ค่า และบทความ 7,415 คำ (conservative count)
- ตรวจขีดจำกัดของ *Artificial Life* ในคู่มือผู้เขียนอีกครั้ง (ผมไม่ได้ตรวจตัวเลขจำกัดจริง)
- ถ้าต้องตัด เสนอให้เหลือ CI แค่ของ contrast ที่พลังงาน 10 และค่า slope

**R11 — สิ่งที่ Methods สัญญาไว้แต่ไม่แสดง**
- §2.4 บอกว่ารายงาน "paired probability of superiority" แต่ค่านี้มีเฉพาะใน CSV (`e6_paired_contrasts.csv`, `t2rb_paired_contrasts.csv`) ไม่อยู่ในเนื้อความหรือ supplement table
- learned values ต่อ bin ของ B3 (prereg §5 ข้อ 6) ก็อยู่ใน CSV เท่านั้น
- **แก้:** ใส่ในตาราง supplement หรือเขียน §2.4 ให้ตรงกับสิ่งที่แสดงจริง

**R12 — เรื่องเล็กที่ยังเหลือ**
- ระบบชื่อ Study A–F และ E1–E6 ยังใช้คู่กัน
- Fig 2B ยังใช้ label "attained-age difference" ขณะที่ E6 ใช้ follow-up (ความต่างแบบจับคู่เท่ากัน แต่ควรมีหมายเหตุใน caption)

---

## 3. สิ่งที่ต้องทำก่อนส่ง (เรียงตามลำดับ)

1. [ ] เปลี่ยนหมายเลขและตำแหน่งรูปให้ตรงลำดับการอ้าง (R4)
2. [ ] ลบคำว่า "red-team" และ "major revision" ออกจากต้นฉบับและชื่อไฟล์ supplement (R8)
3. [ ] แก้ถ้อยคำ "structural noise floor" และ contribution 3 (R1, R2)
4. [ ] แทนการวิเคราะห์ intake แบบยอดรวมด้วยแบบอัตรา หรือลบประโยคนั้นออก (R3)
5. [ ] แก้ Fig 1B annotation, ตำแหน่ง boundary ใน Fig 4A, หัว Table 3 และรูปแบบตัวเลขในเนื้อความ (R5–R7)
6. [ ] ใส่ข้อมูลรุ่น Claude ใน disclosure/reference/AI log (R9)
7. [ ] เติม declarations 6 จุด, build archive ใหม่ และใส่ DOI
8. [ ] ยืนยันเนื้อหาของ Cipollini & Levey ด้วยตัวเอง
9. [ ] commit ไฟล์ revision ทั้งหมดที่ยังไม่ได้ commit (สคริปต์, test, derived CSV, supplement)

ความเห็นของผู้ตรวจ: หลังแก้ข้อ 1–6 ต้นฉบับจะอยู่ในสภาพที่ reviewer วิจารณ์ได้เฉพาะขอบเขตของการออกแบบ (learner คงที่, cue สมบูรณ์, ไม่มี sensitivity sweep) ซึ่งต้นฉบับยอมรับไว้แล้วอย่างตรงไปตรงมา

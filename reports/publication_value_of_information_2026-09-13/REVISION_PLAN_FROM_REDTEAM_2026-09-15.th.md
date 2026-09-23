# แผนแก้ต้นฉบับจากรายงาน Red Team

**ต้นฉบับ:** *When Does a Better Representation Pay? Survival Effects of Resource-Age Information in Artificial Foraging Under Temporal Toxicity*
**รายงานต้นทาง:** `REDTEAM_manuscript_initial_submission_2026-09-15.th.md`
**วันที่จัดทำแผน:** 2026-09-15
**สถานะ:** แผนดำเนินงาน ยังไม่ใช่ผลวิเคราะห์หรือคำยืนยันว่าข้อสังเกตของ Red Team ถูกต้องทั้งหมด

---

## 1. ข้อสรุปเชิงตัดสินใจ

ต้นฉบับควรผ่าน **major rewrite** ก่อนส่ง โดยเปลี่ยนจากเรื่อง “เมื่อใด representation ที่ดีกว่าจึงคุ้ม” ไปเป็นเรื่องที่ข้อมูลรองรับตรงกว่า:

> ใน ecology แบบ toxic–safe–toxic ข้อมูลอายุช่วยให้ agent แยกผลไม้ปลอดภัยกับผลไม้พิษได้จริง แต่ภายใต้ learning rule และ decision policy ที่กำหนดไว้ ความถูกต้องทางพฤติกรรมไม่ได้แปลเป็น survival advantage เหนือ capacity-matched sham และผลที่ระดับพลังงานสูงสุดยังแยกออกจาก policy regime change และ senescence ceiling ไม่ได้

ชื่อเรื่องที่แนะนำ:

> *Correct State Information Is Not Enough: Discrimination and Survival Diverge in a Toxic–Safe–Toxic Artificial Ecology*

รอบแก้ครั้งแรกจะใช้ข้อมูล 600 รันเดิม ไม่รัน simulation เพิ่มจนกว่าจะ:

1. ตรวจซ้ำข้อกล่าวอ้างสำคัญของ Red Team ด้วย analysis ที่ทำซ้ำได้;
2. เขียนต้นฉบับใหม่ให้ตรงกับหลักฐานเดิม;
3. ประเมินอีกครั้งว่าคำถามที่เหลือจำเป็นต้องใช้การทดลองใหม่จริงหรือไม่

---

## 2. หลักการควบคุมการแก้ไข

1. **รายงาน Red Team เป็นแหล่งคำวิจารณ์ ไม่ใช่แหล่งข้อมูลขั้นสุดท้าย**
   ตัวเลขที่คำนวณจากสคริปต์ในภาคผนวกต้อง reproduce จาก raw dump ก่อนนำเข้าต้นฉบับ

2. **แยกสถานะของผลทุกชิ้นให้ชัด**
   ใช้คำกำกับ `frozen/registered`, `prespecified secondary`, `exploratory`, `post hoc descriptive` และ `future test` อย่างสม่ำเสมอ

3. **ไม่เปลี่ยน null หรือผลตรงข้ามให้กลายเป็นผลสนับสนุน**
   Prediction ที่ไม่สำเร็จต้องระบุว่าไม่สำเร็จ ไม่ใช้การเปลี่ยนถ้อยคำของ hypothesis เพื่อลดความชัดของทิศทางเดิม

4. **ไม่กล่าว causal mechanism เกิน telemetry**
   ถ้าข้อมูลแยก starvation override, search cost, meal timing หรือ re-encounter ไม่ได้ ให้รายงานว่า causal path ยังไม่ทราบ

5. **รักษาแกน toxin ecology เดิม**
   ใช้ toxic–safe–toxic phenomenon เป็นแกนชีววิทยา และใช้ sham result เพื่ออธิบายข้อจำกัดของ representation–policy interaction ไม่เปลี่ยนบทความเป็น generic RL benchmark

6. **ไม่แก้ raw confirmatory data**
   การวิเคราะห์ใหม่ต้องสร้าง derived artifacts แยก พร้อม provenance, tests และ checksum ตามสมควร

---

## 3. ลำดับงานและเกณฑ์ผ่าน

## Phase 0 — รักษา baseline และกำหนดขอบเขต

### งาน

- [ ] บันทึก commit, hash และรายการไฟล์ของ manuscript/PDF/analysis/figures ก่อนแก้
- [ ] ยืนยันว่า raw E6 มี 450 รัน และ raw T2-RB มี 150 รัน
- [ ] สร้าง revision checklist ที่อ้าง C1–C4, M1–M9 และประเด็นรูปทีละข้อ
- [ ] กำหนดไฟล์ derived ใหม่โดยไม่ overwrite ผล confirmatory เดิมจนกว่าจะตรวจเทียบเสร็จ

### ผลส่งมอบ

- baseline manifest
- claim-to-evidence checklist

### Gate 0

- จำนวนรันและ hash ตรงกับ archive ที่ต้นฉบับอ้าง
- ไม่มี raw dump ถูกแก้ระหว่างการ revise

---

## Phase 1 — Reproduce ข้อวิจารณ์ C1–C4

### 1.1 สร้าง analysis ที่ทำซ้ำได้

สร้างสคริปต์ใหม่ใน `scripts/` สำหรับอ่าน raw dump และสร้างผลระดับ founder → seed → arm/energy โดยไม่คัดลอกตัวเลขจาก Red Team ด้วยมือ

ตัวแปรขั้นต่ำ:

- founder follow-up และสาเหตุการตาย
- fruit meals และ staple meals
- fruit/staple skips พร้อมคำเตือนเรื่องการนับซ้ำ
- `P(eat | encounter)` แยกชนิดอาหาร
- realized toxin excess/dose และ toxin damage
- learned values และค่าสูงสุดที่เข้าสู่ relative threshold
- สัดส่วน founder ที่เคยปฏิเสธ staple
- seed-level paired contrasts

ผลลัพธ์ควรเขียนเป็น:

- JSON สำหรับค่าที่ manuscript จะอ้าง
- CSV สำหรับ supplementary tables และ source data
- machine-readable metadata ระบุ source files, commit และ analysis timing

### 1.2 ทดสอบข้ออ้าง C1: energy-10 regime

- [ ] ยืนยันว่า `0.6 × 10 = 6 > staple value 5`
- [ ] เปรียบเทียบ staple acceptance ที่พลังงาน 4, 5, 6, 8 และ 10
- [ ] รายงาน mortality composition ทุก arm ไม่ใช่เฉพาะ B1
- [ ] แสดง B2−B3, B2−B1 และ B3−B1 ที่พลังงาน 10
- [ ] ทำ leave-one-energy-out โดยเฉพาะการตัด 10
- [ ] วิเคราะห์ outcome ที่ไม่ชน senescence ceiling ถ้ากำหนดจากข้อมูลเดิมได้อย่างสมเหตุผล

### 1.3 ทดสอบข้ออ้าง C3: constant controls

- [ ] ยืนยันจากโค้ดและ raw dump ว่า A3/A3O/A3R ได้ post-rounding energy เท่ากับ 6 ต่อคำ
- [ ] ยืนยัน acceptance และ fruit skips ของ A3/A3O/A3R
- [ ] รายงาน realized dose, dose/meal, meals และ toxin damage ของ A2/A3O/A3R
- [ ] วัดความต่างจริงระหว่าง A3O กับ A3R หลัง rounding
- [ ] ยืนยันว่า B2/B3 แบ่ง key ของ `raw_plant` ด้วย

### 1.4 ทดสอบข้ออ้าง C4: intake และกลไก

- [ ] เปรียบเทียบ staple intake, fruit intake และ toxin intake กับ follow-up
- [ ] ตรวจว่า telemetry ระบุมื้อที่เกิดภายใต้ starvation override ได้หรือไม่
- [ ] ถ้าแยกไม่ได้ ให้บันทึก limitation แทนการอนุมาน
- [ ] ห้ามใช้ skip count เป็น independent encounter count หากยังไม่ได้ deduplicate

### 1.5 สถิติ

- [ ] ใช้ seed เป็น independent replicate
- [ ] ใช้ paired CI และ paired effect size สำหรับ matched-seed contrasts
- [ ] รายงาน unpaired Cliff's delta เป็นรองหรือถอดออก
- [ ] ทำ minimum-effect test ของ slope เทียบ SESOI = 1 หากวิธีสอดคล้องกับ protocol
- [ ] รายงาน observed variance/power เป็น sensitivity statement ไม่ใช้เป็นหลักฐานย้อนหลังว่าผลจริงหรือไม่จริง

### Tests ที่ต้องเพิ่ม

- fixture ขนาดเล็กพิสูจน์การ aggregate founder → seed → arm
- test การจับคู่ seed และการตรวจ missing/duplicate cells
- test สูตร acceptance/dose/paired contrast
- regression test ว่า output deterministic
- test ว่า analysis ไม่รวม generation อื่นเมื่อกำหนด founder-only

### Gate 1

- ตัวเลข C1–C4 reproduce ได้หรือระบุความต่างจาก Red Team พร้อมสาเหตุ
- ทุกค่าที่จะเข้าต้นฉบับมี source JSON/CSV และ test รองรับ
- ยังไม่มีการแก้ claim ใน manuscript ก่อนผ่าน gate นี้

---

## Phase 2 — เปลี่ยน framing ของบทความ

### 2.1 Title

ใช้ชื่อที่ไม่สื่อว่า representation “จ่ายคืน” หรือให้ survival benefit แล้ว เช่น:

> *Correct State Information Is Not Enough: Discrimination and Survival Diverge in a Toxic–Safe–Toxic Artificial Ecology*

### 2.2 Abstract

เรียงผลใหม่ตามลำดับ evidential priority:

1. B2 คืนความสามารถในการแยก safe versus toxic fruit;
2. primary B2−B3 contrast เป็นลบที่พลังงาน 4–8 และไม่ชัดที่ 10;
3. slope เป็นบวกแต่ต่ำกว่า SESOI และขึ้นกับ endpoint 10;
4. endpoint 10 ตรงกับ staple-rejection regime และ senescence-dominated mortality;
5. E1 null และ T2-RB deficit ต้องรายงานคู่กัน;
6. B2−B1 เป็น secondary/exploratory finding ไม่ใช่ headline;
7. สรุปว่า information sufficiency ไม่เท่ากับ survival value ภายใต้ fixed policy

### 2.3 Contributions

แทน contribution เดิมด้วยข้อที่หลักฐานรองรับ:

1. type-only representation ไม่สามารถสร้าง age-conditional discrimination ภายใต้ temporal toxicity;
2. age-aligned keys เปลี่ยนพฤติกรรมเมื่อเทียบกับ equal-capacity sham แต่ไม่ได้ให้ survival advantage ใน primary comparison;
3. survival consequence เกิดจาก interaction ระหว่าง representation, learning rule, decision threshold และ resource economy;
4. งานเปิดเผย regime boundary ที่ทำให้การตีความ payoff slope ไม่เป็นเอกลักษณ์

### 2.4 Hypotheses และคำตัดสิน

- คืนถ้อยคำทิศทางของ H6.1 ให้ตรงกับ frozen protocol
- ระบุว่า prediction เชิงกลไกของ H6.1 ไม่สำเร็จตาม level-specific contrasts
- แยก “decision rule met” ออกจาก “effect exceeded SESOI”
- ไม่เรียก D(B1)/D(B3) ว่าเป็นศูนย์เมื่อค่าจริงมี structural deviation

### Gate 2

- Title, abstract, contributions และ hypotheses สอดคล้องกับ primary comparison
- ไม่มี secondary result นำหน้า primary negative result
- ไม่มีคำว่า “pays”, “benefit” หรือ “caused survival improvement” ที่เกินหลักฐาน

---

## Phase 3 — แก้ Methods ให้ตรงกับ implementation

### Learning and decision rule

- [ ] ระบุว่า `best_known` คือค่าสูงสุดข้ามทุก food key และทุก food type
- [ ] ระบุ relative threshold 0.6 และ starvation override ที่ energy ≤ 6
- [ ] ระบุว่า unfamiliar key ถูก sample ก่อนมี learned value
- [ ] ระบุว่า B2/B3 แบ่ง key ของอาหารทุกชนิด รวม `raw_plant`
- [ ] อธิบาย sham hash โดยไม่สื่อว่า exposure histories ถูก match กัน

### Constant controls

- [ ] ระบุ post-rounding payoff 6 ของ A3/A3O/A3R
- [ ] ระบุว่า controls เหล่านี้ไม่ต้องแก้ discrimination problem และถูกยอมรับทุกครั้งใน observed runs
- [ ] ลดทศนิยม `potency_scale` ใน main text และเก็บค่าครบใน supplement
- [ ] อธิบายว่าการ calibrate target dose ไม่รับประกัน realized dose เท่ากันเมื่อ behavior ต่างกัน

### Design and provenance

- [ ] ใช้คำว่า “internally frozen at a Git tag before data generation” เมื่อไม่มี public timestamp
- [ ] ระบุว่า matched seeds จับคู่ initial stochastic inputs แต่ trajectories แยกทันทีที่ behavior ต่าง
- [ ] ระบุว่า oracle และ D implementation เกิดหลัง freeze ใน deviation table
- [ ] อธิบาย ambiguity ของ encounter gate และเวลาที่ fix interpretation

### Gate 3

- Methods สามารถอธิบาย C1 และ C3 ได้โดยไม่ต้องอ่านโค้ด
- คำอธิบาย control ไม่สื่อว่าได้ isolate hidden-versus-visible toxicity หรือ realized dose โดยสมบูรณ์

---

## Phase 4 — สร้าง Results ใหม่รอบ primary evidence

ลำดับ Results ที่แนะนำ:

1. **Information sufficiency:** B2 restores safe–toxic discrimination
2. **Primary survival contrast:** B2−B3 across five energies
3. **Energy-10 regime analysis:** staple acceptance, intake และ mortality composition
4. **Secondary contrast:** B2−B1 พร้อม multiplicity label ที่ถูกต้อง
5. **E1 and T2-RB:** E1 null และ high-drain deficit พร้อม realized-dose table
6. **Prediction audit:** registered prediction → observed result → verdict
7. **Deviation audit:** implementation/interpretation timing และผลต่อ claim

### ตารางหลักที่ต้องเพิ่ม

- E6 intake/dose/mortality table
- T2-RB realized-dose and meals table
- preregistered secondary outcomes table
- prediction-to-verdict table
- deviation table

### ผลรองที่ต้องรายงานให้ครบ

- toxin dose per encounter
- cause-of-death fractions
- encounters และ `P(eat | encounter)`
- learned values per bin ของ B2 และ B3
- discrimination index พร้อมคำอธิบาย structural noise floor

### Gate 4

- ผลทุกข้อที่ protocol สัญญาไว้ปรากฏใน main text หรือ supplement และถูกอ้างถึง
- ทุก table cell trace กลับไปยัง derived artifact ได้
- ผลที่ไม่เป็นไปตาม prediction ถูกระบุว่าไม่เป็นไปตาม prediction

---

## Phase 5 — เขียน Discussion ใหม่

### ข้อความที่ต้องถอนหรือลดระดับ

- “B2 rejected more toxic fruit and therefore relinquished energy”
- “selective rejection sacrifices energy at lower payoffs”
- “high safe-fruit payoff compensates sampling cost”
- การใช้ agreement ระหว่าง A3O/A3R เป็น robustness evidence ที่แรง
- การกล่าวว่า constant controls isolate hidden state หรือ realized toxin dose โดยสมบูรณ์

### ข้อความทดแทนที่หลักฐานรองรับ

> Survival differences tracked staple intake more closely than total toxin intake, but the available telemetry does not identify the causal path.

คำอธิบายทางเลือกที่ต้องวางคู่กัน:

- threshold discontinuity เมื่อ learned safe-fruit value ทำให้ threshold สูงกว่า staple value
- senescence ceiling ที่พลังงาน 10
- starvation override
- first-sample burden จากการแบ่ง staple keys
- timing ของ toxic meals
- search/metabolic cost และ behavior-generated exposure

### การตีความ T2-RB

ใช้กรอบ:

> variable, choice-requiring toxicity versus a fixed-payoff control that required no discrimination; realized dose was lower, not higher, in A2

ไม่ใช้กรอบ “hidden toxicity versus equivalent visible toxicity” จนกว่าจะมี control ที่ isolate ความต่างนั้นจริง

### Limitations ที่ต้องระบุเฉพาะเจาะจง

- pickiness 0.6 และ starvation threshold 6 สร้าง regime boundary โดยตรง
- learning rate, age-bin width/cap และ toxin coefficients ยังไม่มี sensitivity analysis
- D มี structural noise floor จาก exposure/re-encounter process
- current telemetry อาจแยก starvation-override meals ไม่ได้
- internal freeze ไม่เท่ากับ externally timestamped preregistration

### Gate 5

- ทุก causal sentence มี analysis รองรับหรือถูกระบุเป็น hypothesis
- Discussion อธิบาย primary negative result ก่อน secondary positive result
- toxic–safe–toxic ecology ยังคงเป็นแกนของเรื่อง

---

## Phase 6 — ลดความซับซ้อนและแก้ Figures

### โครงเรื่อง

- Main narrative: E2 → E6 → T2-RB
- E1: บริบทและ falsification/null ที่ต้องรายงาน
- E3/E4: ย้ายไป supplement หรือย่อเหลือหนึ่งย่อหน้าใน main text
- ใช้ระบบชื่อเดียวตลอด เช่น E1/E2/E6/T2-RB และแสดง arm mapping ครั้งเดียว
- ใช้คำว่า founder follow-up เป็น outcome หลัก และอธิบายความสัมพันธ์กับ attained age ครั้งเดียว

### Figures

- [ ] Figure 1: ใส่ label arm ที่อ่านได้และอธิบาย A3 payoff/acceptance
- [ ] Figure 2: ย้าย legend ไม่ให้ทับข้อมูล
- [ ] Figure 3: ย้าย annotation และพิจารณาย้ายทั้งรูปไป supplement
- [ ] Figure 4: dodge markers, เพิ่ม gray-line legend และทำเครื่องหมาย regime boundary ระหว่าง 8–10
- [ ] Figure 5: ย้าย SESOI legend และเพิ่ม right margin
- [ ] regenerate PNG/PDF และ source-data tables จาก script
- [ ] ตรวจ visual rendering และ text extraction ของ figure labels

### Gate 6

- ไม่มี legend/label ทับข้อมูลหรือถูกตัด
- caption ระบุ arm และ interpretation ที่จำเป็นโดยไม่ต้องย้อนหา Methods
- PDF text extraction ไม่สร้าง label ซ้อนที่รบกวนการค้นหรือ accessibility

---

## Phase 7 — Literature, declarations และ AI disclosure

### Literature

ตรวจ metadata จากแหล่งต้นฉบับก่อนเพิ่มทุกชิ้น โดยพิจารณากลุ่มต่อไปนี้:

- value of information
- utile distinctions/selective perception และ hidden state
- foraging/diet-choice threshold
- post-ingestive feedback
- fruit secondary metabolites และ toxic–safe–toxic biological analogy
- Artificial Life work เรื่อง learning/sensing cost

ห้ามเพิ่ม citation จากรายชื่อใน Red Team โดยยังไม่ได้เปิดและตรวจแหล่งจริง

### Declarations

- [ ] Funding — ผู้เขียนยืนยัน
- [ ] Competing interests — ผู้เขียนยืนยัน
- [ ] Ethics statement — ผู้เขียนยืนยัน
- [ ] CRediT author contributions — ผู้เขียนยืนยันทีละบทบาท
- [ ] Data/code DOI และ public archive — เติมหลัง deposit/download-back verification

### AI disclosure

- [ ] เพิ่ม Claude red-team review หากข้อเสนอแนะถูกนำไปใช้
- [ ] เพิ่ม Codex-assisted analysis/revision ใน task-level AI log
- [ ] ระบุสิ่งที่ AI ช่วยทำอย่างเจาะจง: analysis code, checking, figures, drafting หรือ editing
- [ ] ระบุการตัดสินใจและการตรวจที่ผู้เขียนทำเองจริง พร้อมให้ผู้เขียนอนุมัติข้อความสุดท้าย
- [ ] ตรวจ wording ตามนโยบายวารสารล่าสุดก่อนส่ง

### Gate 7

- ไม่มี placeholder ใน declarations
- citation ทุกตัวมี metadata ที่ตรวจแล้ว
- AI-use log, manuscript disclosure และ cover letter ไม่ขัดกัน

---

## Phase 8 — Final verification ก่อนส่ง

### Code and analysis

- [ ] รัน targeted tests ของ analysis ใหม่
- [ ] รัน existing confirmatory validation tests
- [ ] regenerate analysis JSON/CSV และตรวจ deterministic output
- [ ] regenerate figures จาก source data
- [ ] ตรวจ raw-data checksum ว่าไม่เปลี่ยน

### Manuscript

- [ ] build submission PDF ใหม่
- [ ] รัน `audit_submission_manuscript.py`
- [ ] ตรวจตัวเลขทุกตัวกับ authoritative JSON/CSV
- [ ] ตรวจชื่อ arm, outcome และ multiplicity labels ตลอดเล่ม
- [ ] ตรวจว่า registered, exploratory และ post hoc ถูกติดป้ายครบ
- [ ] ตรวจ references/citations แบบสองทาง
- [ ] ตรวจทุกหน้าและทุกรูปด้วยตา
- [ ] ทดลอง copy/search figure text จาก PDF

### Submission readiness

- [ ] ไม่มี placeholder
- [ ] archive/DOI เปิดได้และ download-back hash ตรง
- [ ] manuscript, supplement, figures และ AI disclosure เป็น revision เดียวกัน
- [ ] ผู้เขียนสามารถอธิบาย C1–C4 และเหตุผลที่ลดระดับ claim ได้ด้วยตนเอง

### Gate 8 — Definition of done

ต้นฉบับพร้อมส่งต่อเมื่อ:

1. ข้อกล่าวอ้าง C1–C4 ผ่าน reproducible analysis;
2. primary negative result เป็นแกนของ abstract/results/discussion;
3. alternative explanations ของ energy 10 ถูกเปิดเผยครบ;
4. prediction, secondary outcomes และ deviations รายงานครบ;
5. control interpretation ตรงกับ implementation และ realized behavior;
6. figures และ PDF ผ่าน technical/visual QA;
7. declarations, archive และ AI disclosure ไม่มีช่องว่าง;
8. submission audit รายงานพร้อมส่งโดยไม่มี blocking item

---

## 4. สิ่งที่ไม่ทำใน revision รอบแรก

- ไม่เพิ่มระดับพลังงาน 7, 9 หรือ 12 เข้าใน confirmatory dataset เดิม
- ไม่รัน sensitivity sweep แล้วนำมาปะปนกับ frozen analysis โดยไม่มีป้าย exploratory
- ไม่เปลี่ยน decision rule เพื่อทำให้ผลดีขึ้นย้อนหลัง
- ไม่อ้างว่า sham เป็น “ผลค้นพบใหม่ทั่วไปของ RL” เกินขอบเขต ecology นี้
- ไม่อ้าง causal mechanism จาก correlation ระหว่าง meals, dose และ survival
- ไม่ส่งก่อน declarations และ public archive เสร็จ

การทดลองใหม่ เช่น within-food threshold, denser energy series, pickiness/starvation sweep หรือการแยกกลไก sham ต้องมี protocol และ public timestamp ใหม่ และควรพิจารณาเป็น follow-up study หรือบทความถัดไป

---

## 5. ลำดับไฟล์ที่คาดว่าจะต้องแก้หรือสร้าง

### สร้างใหม่

- `scripts/analyze_redteam_mechanisms.py` หรือชื่อเฉพาะที่สื่อ E6/T2-RB ชัดกว่า
- `tests/test_redteam_mechanism_analysis.py`
- derived JSON/CSV สำหรับ intake, dose, mortality, paired effects และ prediction audit
- supplementary tables สำหรับ secondary outcomes และ deviations

### แก้

- `manuscript_v0.en.md`
- `references.bib`
- `AI_USE_LOG.md`
- figure-generation scripts และ figure source data
- `SUBMISSION_CHECKLIST_2026-09-14.th.md`
- submission audit rules หากมี field/table ใหม่
- cover letter หลัง claim ของ manuscript คงที่แล้ว

### Regenerate

- confirmatory figures ที่แก้ layout/content
- `submission/manuscript_initial_submission_draft.pdf`
- `submission/manuscript_submission_audit.json`
- release inventory/checksum เฉพาะ derived/manuscript package โดยไม่เปลี่ยน raw dumps

---

## 6. ลำดับลงมือที่แนะนำแบบสั้น

1. Freeze baseline
2. เขียนและทดสอบ mechanism analysis
3. Lock evidence tables
4. ตัดสิน framing/title
5. แก้ Methods
6. เขียน Results ใหม่
7. เขียน Discussion ใหม่
8. จัด main text/supplement ใหม่
9. แก้ figures
10. ตรวจ literature และเติม declarations/disclosures
11. Build, audit และ visual QA
12. Author sign-off

**ห้ามสลับไปแก้ prose ก่อนข้อ 2–3** เพราะจะทำให้ตัวเลขและคำอธิบายเปลี่ยนซ้ำเมื่อ analysis อย่างเป็นทางการต่างจากสคริปต์เฉพาะกิจใน Red Team

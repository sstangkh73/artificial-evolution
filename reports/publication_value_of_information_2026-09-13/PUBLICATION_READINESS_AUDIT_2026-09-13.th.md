# Publication-readiness audit

วันที่ตรวจ: 2026-09-13

สถานะ: **มีแกนบทความที่ส่งวารสารได้ แต่ยังไม่พร้อม submit**

## คำตัดสิน

จุดแข็งที่สุดไม่ใช่การมีระบบจำลองขนาดใหญ่ แต่คือหลักฐานเชิงสาเหตุสามชั้นที่ต่อกันได้:

1. representation แบบชนิดอย่างเดียวแยกพิษที่เปลี่ยนตามอายุไม่ได้
2. age-informed key แก้ discrimination ได้ ขณะที่ capacity-matched sham แก้ไม่ได้
3. discrimination ที่ดีขึ้นไม่รับประกัน survival benefit และ E6 ทดสอบขอบเขตของผลนี้โดยตรง

กรอบนี้เหมาะกับ *Artificial Life* มากกว่ากรอบ ecological trap เดิม หากบทความย้ำว่าเป็นข้อค้นพบเกี่ยวกับ embodied adaptive behavior ภายใต้ resource trade-off และไม่อ้างว่าเป็น RL novelty, EVPI, การค้นพบ cue ด้วยตนเอง หรือวิวัฒนาการข้ามรุ่น

## ช่องว่างเรียงตามผลต่อโอกาสตีพิมพ์

| ลำดับ | ช่องว่าง | ผลหากไม่ปิด | สิ่งที่ต้องทำ |
|---:|---|---|---|
| 1 | E6 ยังไม่มี confirmatory data | คำถามในชื่อเรื่องยังไม่มีคำตอบ | freeze/tag addendum แล้วรัน E6 30 seed × 15 arms = 450 รัน |
| 2 | จำนวน seed เดิมของ T2 ต่ำ | replication มีโอกาสให้ผลก้ำกึ่งสูง | ใช้ 50 seed × 3 arms = 150 รัน พร้อมรายงาน CI แม้ p ไม่ผ่าน |
| 3 | deviation log เดิมไม่ครบ | จุดขายเรื่อง preregistration ถูกผู้ประเมินหักล้างได้ | บันทึก E2 implementation, E4 post-freeze spec และสถานะ exploratory ของ E5 T2 ใน §11 แล้ว |
| 4 | novelty ยังไม่ได้เทียบงานใกล้เคียงแบบตรงตัว | editor อาจมองว่าเป็น perceptual aliasing ที่ทราบอยู่แล้ว | ทำ claim-to-literature matrix และเขียนหนึ่งย่อหน้าว่า contribution ต่างจาก POMDP/RL และงาน foraging learning rules อย่างไร |
| 5 | model description ยังไม่พอให้สร้างซ้ำ | งาน simulation อาจถูกปฏิเสธเพราะตรวจกลไกไม่ได้ | เติม ODD supplement, equations, scheduling, initialization, RNG และ parameter table |
| 6 | ยังไม่มี independent reproduction | code availability อย่างเดียวไม่พิสูจน์ว่า pipeline ทำซ้ำได้ | หลัง freeze ให้ clean clone รัน smoke ทุก arm และให้บุคคลอื่นทำซ้ำอย่างน้อยหนึ่ง seed ต่อ arm |
| 7 | figures/source data ยังไม่มี | reviewer ตรวจ pattern และ uncertainty ยาก | สร้าง vector figures พร้อม CSV ที่ใช้วาดและสคริปต์ deterministic |
| 8 | AI disclosure ยังเป็น placeholder | ขัดนโยบาย MIT Press/Artificial Life | เก็บ log ตั้งแต่ตอนนี้และเปิดเผย tool, provider, model/version, วันที่, งานที่ทำ และการตรวจโดยมนุษย์ |

## Sample-size sensitivity ที่ใช้แก้ร่าง

### E6

- smallest effect of scientific interest: slope 1 tick ต่อหน่วยพลังงาน หรือ 6 tick จากพลังงาน 4 ถึง 10
- external variance: SD ของ paired B2-B3 lifespan ใน E2-W = 7.822 tick
- ภายใต้สมมติฐานความคลาดเคลื่อนระหว่างระดับพลังงานเป็นอิสระ SD ของ seed-level slope ≈ 1.624
- normal approximation: 20 seed ให้ power ≈ 0.79; 30 seed ≈ 0.92
- 30 seed ให้ 95% CI half-width โดยประมาณ 0.58 tick ต่อหน่วยพลังงาน

นี่เป็น sensitivity analysis เพราะ covariance ข้ามระดับยังไม่ทราบ ไม่ใช่การรับประกันผล และไม่มีการเพิ่ม seed หลังเห็น p-value

### T2-RB replication

- smallest effect of scientific interest: 5 tick
- external variance จาก E5: SD ของ paired A2-A3 = 12.521 tick
- normal approximation: 20 seed ให้ power ≈ 0.43; 50 seed ≈ 0.81
- 50 seed ให้ 95% CI half-width โดยประมาณ 3.47 tick

ดังนั้น 20 seed เดิมไม่เหมาะกับ replication ที่ตั้งใจให้ชี้ขาด ร่างถูกแก้เป็น 50 seed ก่อน freeze

## โครงบทความที่ควรรักษา

ผลหลักควรเรียงดังนี้:

1. **Failure:** type-only learner รวมสถานะพิษต่างกันไว้ในค่าเดียว
2. **Causal rescue:** B2-B3 แสดงว่าข้อมูลอายุ ไม่ใช่จำนวนคีย์ ทำให้ discrimination ดีขึ้น
3. **Behavior-survival dissociation:** การแยกได้ดีขึ้นให้ survival benefit ต่ำหรือเป็นลบใน ecology เดิม
4. **Boundary test:** E6 แสดงผล B2-B3 ตลอดแกน resource energy พร้อม uncertainty
5. **Mechanism:** learned value by age bin, encounter-conditioned choice, toxin dose และ starvation อธิบายว่าทำไมเส้นจึงเกิด
6. **Transfer/replication:** T2-RB เป็นคำถาม replication แยกจากข้ออ้างหลัก หากผลไม่ทำซ้ำให้รายงานเป็น boundary โดยไม่ลดคุณค่าของ E6

อย่าให้ E3 selection differential หรือประวัติ ecological-trap เดิมกินพื้นที่บทความมากกว่ากลไก E2/E6 ทั้งสองส่วนควรเป็นผลสนับสนุนหรือ supplement

## Robustness ที่คุ้มและไม่คุ้ม

ควรทำหลังผลหลักโดยประกาศสถานะให้ชัด:

- sensitivity ต่อการ censor ที่ tick 800: empirical RMST เป็นหลัก และ complete-case deaths เป็นผลรอง
- แสดงผลทุกระดับพลังงาน ไม่พึ่งเส้น regression เพียงเส้นเดียว
- แสดง seed-level paired lines และ distribution ของ slopes
- ตรวจผลเมื่อเอา seed ออกทีละหนึ่งเพื่อประเมิน influence โดยไม่ใช้เป็นเกณฑ์คัด seed
- clean-clone reproduction บน environment ใหม่

ยังไม่ควรเพิ่มก่อน E6:

- learner รุ่นใหม่หรือ neural network
- cue noise หลายระดับ
- body plan จำนวนมาก
- การวิวัฒนาการหลายรุ่น
- การทดลองเก็บอาหารให้หายพิษ

สิ่งเหล่านี้เพิ่ม scope และเปิดคำถามใหม่โดยไม่ทำให้ causal chain ปัจจุบันแข็งขึ้นเท่ากับการปิด E6, model documentation และ reproducibility

## Figures ที่จำเป็น

1. แผนภาพ toxin profile แบบ toxic-safe-toxic พร้อม age bins และ representation B1/B2/B3
2. discrimination ของ B1/B2/B3 แยก M/W พร้อม paired seeds
3. lifespan และ starvation ของ B1/B2/B4 เพื่อแสดง behavior-survival dissociation
4. E6: B2-B3 lifespan difference ต่อ realized energy พร้อม paired seed slopes และ CI
5. mechanism panel: learned values by age bin, `P(eat|safe/toxic)`, toxin exposure และ starvation
6. T2-RB replication เป็น figure รองหรือ supplement

ทุก figure ต้องสร้างจากสคริปต์ มี source-data CSV และ export vector PDF/SVG ตามข้อกำหนดวารสาร

## Literature anchors ที่ต้องอ่านฉบับเต็ม

| บทบาท | แหล่งเริ่มต้น | สิ่งที่ต้องเทียบ |
|---|---|---|
| ecological information | Dall et al. (2005), *Information and its use by animals in evolutionary ecology* | information acquisition/use และ ecological cost |
| formal information value | Donaldson-Matasci et al. (2010), *The fitness value of information* | เหตุผลที่ผลปัจจุบันไม่ใช่ EVPI หรือ reproductive fitness |
| information ecology | Bergman & Beehner (2023), *Information Ecology* | context-dependent value และ acquisition/use |
| partial observability | Kaelbling, Littman, and Cassandra (1998), *Planning and Acting in Partially Observable Stochastic Domains* | perceptual aliasing เป็นพื้นฐานที่ทราบแล้ว |
| ALife competitor | Giannakakis et al. (2025), *Network Bottlenecks and Task Structure Control the Evolution of Interpretable Learning Rules in a Foraging Agent* | งานปัจจุบันศึกษาผลของ supplied state information และ ecological payoff ไม่ได้ evolve learning rules |
| model reporting | Grimm et al. (2020), ODD protocol update | โครง supplement ให้ตรวจและสร้างโมเดลซ้ำได้ |

ห้ามใส่ reference จาก abstract อย่างเดียว ต้องอ่าน full text และผูกแต่ละ citation กับประโยคที่รองรับจริง

## Reproducibility package ก่อน submit

- frozen code commit และ prereg tag
- raw dumps ทุก run พร้อม checksums
- machine-readable specifications และ exact commands
- environment lock: Python version และ dependency versions
- analysis scripts ที่หยุดด้วย nonzero exit เมื่อ seed/provenance ไม่ครบ
- source-data CSV และ vector figures
- ODD model description และ parameter dictionary
- `README` แบบ start-to-finish สำหรับ clean machine
- public archive พร้อม DOI และ license ที่ผู้เขียนเลือก
- Data Availability Statement และ AI disclosure ที่ตรงกับ log

## Submission fit

*Artificial Life* ระบุว่า Article โดยทั่วไปยาว 6,000–12,000 คำ ต้องมี cover letter อธิบายความเข้ากับ scope และต้องส่ง supplementary material ที่จำเป็นต่อการประเมินพร้อมบทความ วารสารและ MIT Press กำหนดให้เปิดเผยการใช้ generative AI อย่างชัดเจน รวมถึงการใช้กับ text, code, data, mathematics, reasoning หรือ algorithms

แหล่งตรวจล่าสุด:

- https://direct.mit.edu/artl/pages/submission-guidelines
- https://direct.mit.edu/journals/pages/authors
- https://doi.org/10.18564/jasss.4259

## Gate ก่อน freeze

ต้องผ่านทั้งหมด:

- [ ] ผู้เขียนตรวจ wording ของ H6.1, SESOI และ claim ที่อนุญาต
- [x] JSON spec ตรงกับเอกสาร: E6 30 seed; T2-RB 50 seed
- [x] analyzer ตรวจจำนวน seed, missing arm, dirty tree และ revision change
- [x] deviation log เดิมครบ
- [ ] สร้าง commit สะอาดและ tag preregistration addendum
- [ ] ทดสอบ clean-clone smoke โดยไม่เปิดผล confirmatory

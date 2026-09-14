# รายงานผลชุดยืนยัน E6 และ T2-RB

ผู้จัดทำ: Chisanupong Injun

วันที่วิเคราะห์: 2026-09-14

สถานะ: ผลยืนยันเสร็จสมบูรณ์และตรวจ provenance แล้ว; ยังไม่ใช่ต้นฉบับพร้อมส่ง

## สรุปที่ใช้ตัดสินใจ

E6 ผ่าน decision rule ที่ลงทะเบียนล่วงหน้า: ค่าเฉลี่ยของ slope แบบจับคู่ B2-B3 เทียบกับพลังงานผลไม้เป็นบวกและช่วงความเชื่อมั่น 95% ไม่คร่อมศูนย์ อย่างไรก็ดี ขนาดจุดประมาณ 0.890 tick ต่อหนึ่งหน่วยพลังงานต่ำกว่า SESOI ที่กำหนดไว้ 1 tick เล็กน้อย และ sensitivity หลังเห็นผลพบว่า slope นี้ขึ้นกับจุดพลังงาน 10 อย่างมีนัยสำคัญต่อการตีความ

รูปแบบข้อมูลจริงไม่ใช่ “ข้อมูลอายุทำให้อยู่รอดดีขึ้นเรื่อย ๆ” ที่พลังงาน 4, 5, 6 และ 8 กลุ่ม B2 อยู่รอดสั้นกว่า sham B3 ส่วนที่พลังงาน 10 ผลต่างแยกจากศูนย์ไม่ได้ ผลหลักจึงเป็นการลดลงจนตรวจไม่พบต้นทุนที่ปลายบนของช่วงทดสอบ ไม่ใช่ประโยชน์ด้านการอยู่รอดที่ยืนยันได้ทุกระดับ

T2-RB สนับสนุนผลที่ลงทะเบียนไว้ในทิศทางเดียวกันทั้งสอง control: age-varying toxicity (A2) ทำให้เวลาอยู่รอดหลังเริ่มติดตามสั้นกว่า constant-potency control ทั้งแบบ recalibrated (A3R) และแบบเดิม (A3O)

## ความสมบูรณ์และ provenance

| ชุด | แบบทดลอง | จำนวนรัน | ผล validator | failure | censored founder | revision ที่ใช้รัน |
|---|---:|---:|---|---:|---:|---|
| E6 | 30 seed × 5 พลังงาน × 3 representation | 450 | VALID 450/450 | 0 | 0 | `3f1af32f9e37655ed9bee5462526921eff226c8a` |
| T2-RB | 50 seed × 3 arm | 150 | VALID 150/150 | 0 | 0 | `3f1af32f9e37655ed9bee5462526921eff226c8a` |

ทั้งสองชุดรันจาก clean detached worktree ที่ annotated tag `prereg-resource-age-2026-09-14`; revision และ dirty-state ไม่เปลี่ยนระหว่างรัน E6 ใช้เวลา 2811.7 วินาทีและ T2-RB ใช้เวลา 1007.7 วินาทีบน Python 3.14.3 / Windows 11

หมายเหตุด้าน audit: หัวข้อ checklist ข้อ 8 บรรทัดแรกในเอกสาร preregistration ที่ tag ไว้ยังมีข้อความเดิมว่า JSON spec เป็น DRAFT ทั้งที่ส่วนสถานะด้านบนและ JSON ทั้งสองไฟล์ถูกเปลี่ยนเป็น `PREREGISTERED_CONFIRMATORY_FROZEN` ก่อนสร้าง manifest และ tag ข้อความ checklist ที่ค้างอยู่นี้เป็นข้อผิดพลาดเชิงบรรณาธิการในเอกสารที่เก็บถาวร จึงไม่แก้ย้อนหลังและไม่มีผลต่อ spec ที่ runner ฝังไว้หรือ provenance ของผล

## E6: ผลหลักที่ลงทะเบียนล่วงหน้า

ตัวแปรหลักคือ `founder_mean_followup_ticks` และ contrast เชิงสาเหตุคือ B2-B3 ภายใน seed เดียวกัน โดย B2 ใช้ type × resource-age bin ส่วน B3 มีจำนวนคีย์เท่ากันแต่คีย์ไม่บรรจุข้อมูลอายุอาหาร

- จำนวน slope ที่สมบูรณ์: 30
- ค่าเฉลี่ย slope: 0.890402 tick ต่อหนึ่งหน่วยพลังงาน
- SD: 2.227007; median: 0.381207
- 95% t CI: 0.058918 ถึง 1.721887
- bootstrap 95% CI: 0.130236 ถึง 1.695776
- two-sided Monte Carlo sign-flip: `p = 0.0364848` จาก 200,000 draws
- slope เป็นบวก 18 seed และเป็นลบ 12 seed
- SESOI: 1 tick ต่อหนึ่งหน่วยพลังงาน

ผลนี้ผ่านเกณฑ์ H6.1 ที่กำหนดว่า mean slope ต้องเป็นบวกและ 95% CI ต้องไม่คร่อมศูนย์ แต่หลักฐานยังไม่แสดงว่าขนาดผลมากกว่า SESOI อย่างชัดเจน เพราะ point estimate ต่ำกว่า 1 และ CI คร่อม 1

## E6: ผลรายระดับที่กำหนดไว้ล่วงหน้า

| พลังงาน | mean B1 | mean B2 | mean B3 | B2-B3 | 95% CI | Holm p | การตีความ |
|---:|---:|---:|---:|---:|---|---:|---|
| 4 | 144.239 | 150.713 | 156.145 | -5.431 | -8.826 ถึง -2.037 | 0.0120 | B2 สั้นกว่า B3 |
| 5 | 150.314 | 156.063 | 161.639 | -5.576 | -9.403 ถึง -1.749 | 0.0120 | B2 สั้นกว่า B3 |
| 6 | 156.123 | 160.169 | 166.309 | -6.141 | -9.989 ถึง -2.293 | 0.0120 | B2 สั้นกว่า B3 |
| 8 | 172.624 | 171.341 | 178.991 | -7.650 | -11.470 ถึง -3.830 | 0.00265 | B2 สั้นกว่า B3 |
| 10 | 207.595 | 207.078 | 205.713 | +1.365 | -2.122 ถึง 4.852 | 0.4448 | แยกจากศูนย์ไม่ได้ |

ไม่มีระดับใดที่แสดงประโยชน์ด้านการอยู่รอดของ B2 เทียบ B3 อย่างยืนยันได้ ข้อมูลนี้รองรับข้ออ้างว่า survival effect เปลี่ยนตาม regime และต้นทุนหายไปที่ endpoint ที่ทดสอบ รองรับได้ไม่ถึงข้ออ้างว่ามี break-even point ทั่วไปหรือเส้นตอบสนองราบรื่น

## E6: กลไกและ exposure

กลไกการเรียนรู้ทำงานตามที่ออกแบบไว้ทุกระดับ ค่า discrimination เฉลี่ยของ B2 อยู่ระหว่าง 0.654 ถึง 0.748 ขณะที่ B3 อยู่ระหว่าง -0.112 ถึง -0.097 ทุก B2 run มี resource-age key ครบทั้งเก้าคีย์ และ learned value ของ safe bins สูงกว่า toxic bins

ค่าเฉลี่ย encounter ต่อ founder ของ B2 เท่ากับ 48.695, 52.280, 56.130, 65.459 และ 61.938 ที่พลังงาน 4, 5, 6, 8 และ 10 ตามลำดับ จึงผ่าน gate ที่ preregistration เขียนไว้เป็นค่า “per founder at each energy level” อย่างไรก็ดี การตรวจแบบเข้มกว่าหลังเห็นผลพบว่า minimum ของแต่ละ run ต่ำกว่า 30 ที่พลังงาน 4-6 ประเด็นนี้ต้องระบุเป็น post hoc sensitivity และห้ามใช้เปลี่ยนคำตัดสิน H6.1

## E6: sensitivity หลังเห็นผล

Leave-one-energy-out เป็นการวิเคราะห์หลังเห็นผลเพื่อวินิจฉัยรูปทรง ไม่ใช่การทดสอบยืนยันเพิ่มเติม เมื่อเอาพลังงาน 4, 5, 6 หรือ 8 ออก slope ยังเป็นบวกและ CI ไม่คร่อมศูนย์ แต่เมื่อเอาพลังงาน 10 ออก slope เป็น -0.58 (95% CI -1.85 ถึง 0.70; `p = 0.36`) ดังนั้นข้อสรุป linear slope ขึ้นกับ endpoint พลังงาน 10 อย่างมีสาระ

## T2-RB replication

Primary contrast A2-A3R จาก 50 matched seeds:

- A2 mean 159.2608; A3R mean 167.1888
- mean paired difference -7.928 tick
- 95% t CI -11.045859 ถึง -4.810141
- bootstrap 95% CI -10.9668 ถึง -4.9384
- two-sided Monte Carlo sign-flip `p = 0.000020`
- 12 seed สนับสนุน A2, 38 seed สนับสนุน A3R, ไม่มี tie
- unpaired Cliff's delta -0.1336 (negligible)

Secondary direct-replication contrast A2-A3O ให้ผลสอดคล้องกัน: mean difference -7.1016 tick, 95% CI -10.217872 ถึง -3.985328, `p = 0.000035`, Cliff's delta -0.1184

point estimate ของ primary contrast มีขนาดมากกว่า SESOI 5 tick แต่ t CI คร่อม -5 เล็กน้อย จึงเขียนได้ว่าจุดประมาณเกิน SESOI แต่ยังไม่ควรอ้างว่าขนาดจริงเกินเกณฑ์นี้อย่างแน่นอน Cliff's delta ที่เล็กไม่ขัดกับ paired result เพราะ seed matching ลดความแปรปรวนระหว่าง seed และตอบคำถามคนละแบบกับการเปรียบเทียบ distribution แบบไม่จับคู่

## ข้ออ้างที่อนุญาตในต้นฉบับ

- ข้อมูล resource age เพียงพอให้ fixed learner แยก safe และ toxic age states ได้ ส่วน capacity-matched sham ทำไม่ได้
- E6 ผ่าน decision rule ของ positive slope ที่ลงทะเบียนล่วงหน้า
- slope สะท้อนต้นทุน survival ของ B2 ที่ตรวจไม่พบแล้วที่พลังงาน 10 และขึ้นกับ endpoint นั้น
- T2-RB ทำซ้ำ survival deficit ของ age-varying toxicity เทียบ constant-potency control ได้ทั้งสองนิยาม
- representational sufficiency กับ ecological survival benefit เป็นคำถามคนละข้อในระบบนี้

## ข้ออ้างที่หลักฐานยังไม่รองรับ

- ข้อมูลอายุเพิ่ม survival โดยทั่วไป
- มี monotonic หรือ smooth payoff-response curve
- ระบุ break-even energy ได้
- เป็น expected value of perfect information หรือ optimal policy result
- เป็น Darwinian fitness benefit หรือวิวัฒนาการข้ามรุ่น
- agent ค้นพบ cue อายุด้วยตนเอง

## แฟ้มหลักฐาน

- frozen specifications: `reports/prereg/E6_representation_payoff_spec.json`, `reports/prereg/T2_RB_replication_spec.json`
- preregistration manifest: `reports/prereg/preregistration_manifest_2026-09-14.json`
- batch, validation และ primary analysis: `confirmatory/e6/` และ `confirmatory/t2rb/`
- E6 secondary/mechanism analysis: `confirmatory/e6/E6_secondary_and_mechanism.json`
- figure source data: `confirmatory/source_data/`
- figures: `confirmatory/figures/`
- raw 600 dumps: `data/confirmatory_resource_age_2026-09-14/`
- SHA-256 inventory: `confirmatory/checksums.sha256`

ก่อนส่งตีพิมพ์ raw dumps และไฟล์วิเคราะห์ต้องถูกเก็บใน public versioned archive พร้อม DOI และตรวจ hash กับ inventory นี้อีกครั้ง

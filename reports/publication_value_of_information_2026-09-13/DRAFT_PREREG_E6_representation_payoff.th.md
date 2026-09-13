# ร่าง preregistration addendum: E6 ผลของข้อมูลอายุทรัพยากรต่อการอยู่รอด

ผู้จัดทำ: Chisanupong Injun

วันที่ร่าง: 2026-09-13
สถานะ: **DRAFT — ยังไม่ตรึง ห้ามรันชุดยืนยันจากเอกสารนี้**

## 1. ที่มาและการเปิดเผย pilot

ร่างนี้เขียนหลังเห็น exploratory pilot seed `20260960` แล้ว จึงไม่อ้างว่าคำทำนายเกิดขึ้นโดยไม่เห็นข้อมูล pilot ข้อมูล pilot ใช้เลือกช่วงและตรวจกลไกเท่านั้น จะไม่รวมในสถิติของชุดยืนยัน

pilot ที่ใช้:

- `E6P`: B1/B2 ที่ multiplier 1.0, 0.75, 0.50, 0.25 รวม 8 รัน
- `E6PX`: B3/B4 ที่ 1.0, 0.75, 0.50 และ B1-B4 ที่ 0.40 รวม 10 รัน
- ทั้งหมดใช้ seed เดียว จึงไม่ใช้ประมาณ uncertainty หรือยืนยันรูปของผล

pilot พบข้อเท็จจริงทางวิศวกรรมสามข้อ:

1. multiplier ทำงานใน simulation หลัง `63fd324`
2. พลังงานที่ agent ได้ถูกปัดเป็นจำนวนเต็ม: multiplier 1.0, 0.75, 0.50, 0.40 ให้พลังงานผลไม้ปลอดภัย 10, 8, 5, 4 หน่วย ขณะที่อาหารหลักให้ 5 หน่วย
3. B2 ยังแยกช่วงปลอดภัยกับเป็นพิษได้ที่ 4 หน่วย (`D=0.69` ใน seed pilot) แต่ผลต่ออายุขัยเทียบ B3 เปลี่ยนจาก +5.78 tick ที่ 10 หน่วยเป็น -17.26 tick ที่ 4 หน่วย

## 2. คำถามวิจัย

เมื่อ learner และระบบนิเวศถูกตรึงไว้ ผลของการเพิ่มข้อมูล **อายุผลไม้/อายุทรัพยากร** ลงใน representation ต่ออายุขัยเปลี่ยนตามพลังงานของผลไม้เสี่ยงหรือไม่? อายุในที่นี้คือเวลาตั้งแต่ผลไม้ถูกสร้าง (`current tick - created_tick`) ไม่ใช่อายุของ agent

คำว่า **survival effect of resource-age information** ในนิยามนี้คือ `อายุขัย(B2) - อายุขัย(B3)` ภายใน seed และระดับพลังงานเดียวกัน ไม่ใช่ expected value of perfect information และไม่ใช่ Darwinian fitness value

## 3. แบบทดลอง

### 3.1 โปรไฟล์และพารามิเตอร์คงที่

- ใช้โปรไฟล์ W: พิษก่อน tick 40, ปลอดภัย tick 40-80, แล้วกลับเป็นพิษ
- ใช้ base flags เดียวกับ E2_W และ E6 pilot
- `ticks=800`; simulation หยุดเมื่อประชากรสูญพันธุ์ได้ตามปกติ
- seed ชุดยืนยันใหม่: `20260970` ถึง `20260999` รวม 30 seed

### 3.2 ระดับพลังงาน

| multiplier | พลังงานผลไม้ปลอดภัยที่ agent ได้จริง | บทบาท |
|---:|---:|---|
| 1.00 | 10 | สูงกว่าสิ่งทดแทนมาก |
| 0.80 | 8 | สูงกว่าสิ่งทดแทน |
| 0.60 | 6 | เหนือขอบเขตการทดแทนเล็กน้อย |
| 0.50 | 5 | เท่ากับอาหารหลัก |
| 0.40 | 4 | ต่ำกว่าอาหารหลัก แต่ pilot ยังมี exposure และ B2 discrimination เพียงพอ |

รายงานทั้ง multiplier และพลังงานจำนวนเต็มที่ใช้จริง ห้ามวิเคราะห์เสมือนพลังงานเปลี่ยนต่อเนื่องตามค่าก่อนปัดเศษ

### 3.3 แขน

| แขน | representation | บทบาท |
|---|---|---|
| B1 | `type` | baseline ของระบบเดิม |
| B2 | `type_age` | ได้ข้อมูลอายุของชิ้นอาหาร |
| B3 | `type_sham` | จำนวนคีย์และกฎสำรวจเท่า B2 แต่คีย์ไม่มีข้อมูลอายุของชิ้นอาหาร |

ไม่ใช้ B4 เป็นแขนหลักของ E6 เพราะ B4 optimize การหลบพิษ ไม่ได้ optimize อายุขัย และไม่ใช่นโยบายที่เหมาะที่สุด

ขนาดรวม: 5 ระดับ × 3 แขน × 30 seed = **450 รัน**

### 3.4 เหตุผลของจำนวน seed

กำหนด smallest effect of scientific interest ของแนวโน้มไว้ที่ **1 tick ต่อหน่วยพลังงาน** หรือผลต่าง B2-B3 เปลี่ยน 6 tick ระหว่างพลังงาน 4 กับ 10 ซึ่งเท่ากับราว 2% ของอายุ founder โดยทั่วไปใน regime นี้

ใช้ SD ของ paired B2-B3 lifespan ใน E2-W เท่ากับ 7.822 tick เป็นค่าความแปรปรวนภายนอก E6 และสมมติอย่างเปิดเผยว่าความคลาดเคลื่อนระหว่างห้าระดับพลังงานเป็นอิสระ จะได้ SD ของ seed-level slope โดยประมาณ `7.822 / sqrt(23.2) = 1.624` tick ต่อหน่วยพลังงาน การคำนวณแบบ normal approximation ให้ power ราว 0.79 ที่ 20 seed และ 0.92 ที่ 30 seed สำหรับ slope 1.0; 95% CI half-width โดยประมาณลดจาก 0.71 เป็น 0.58

การคำนวณนี้เป็น sensitivity analysis ไม่ใช่การรับประกัน power เพราะ covariance ข้ามระดับพลังงานยังไม่ทราบ เลือก 30 seed ก่อนรันยืนยันและจะรายงาน uncertainty ตามจริง ไม่เพิ่ม seed หลังดู p-value

## 4. สมมติฐานและการทดสอบหลัก

สำหรับแต่ละ seed และพลังงาน `E` คำนวณ

`Delta_i(E) = founder_mean_followup_ticks(B2, i, E) - founder_mean_followup_ticks(B3, i, E)`

แล้ว fit เส้นตรง `Delta_i(E) = intercept_i + slope_i * E` แยกต่อ seed บนค่าพลังงานจริง `{4,5,6,8,10}`

### H6.1 — ผลของข้อมูลอายุดีขึ้นเมื่อผลไม้มีค่ามากขึ้น

- คำทำนาย: ค่าเฉลี่ย `slope_i > 0`
- การทดสอบหลัก: seeded Monte Carlo two-sided sign-flip test บน `slope_i` จำนวน 30 ค่า ใช้ 200,000 draws และ seed `20260912`; alpha 0.05
- รายงาน: mean/SD/median ของ slope, 95% t CI, 95% bootstrap CI, exact p, จำนวน slope บวก/ลบ และผลทุกระดับ
- ถ้าค่าเฉลี่ย slope ≤ 0 หรือ CI คร่อม 0 ให้ถือว่าสมมติฐานไม่ได้รับการยืนยัน

เหตุผลเชิงกลไก: B2 และ B3 มี capacity และกฎสำรวจเท่ากัน จึงแยกผลของโครงสร้างข้อมูลออกจากจำนวนคีย์ เมื่อผลไม้ปลอดภัยมีค่าสูง ข้อมูลอายุเปิดให้กินทรัพยากรที่มีค่าและลดการกินพิษ เมื่อผลไม้ปลอดภัยมีค่าต่ำ การแยกสภาพอาจไม่มีประโยชน์หรือมีต้นทุนภายใต้ learner ที่ตรึงไว้

## 5. ผลรองและ mechanism checks

ผลรองทั้งหมดไม่มีสิทธิ์เปลี่ยนข้อสรุปของ H6.1:

1. `B2-B3` ต่อระดับพลังงาน พร้อม Holm correction ข้าม 5 ระดับ
2. `B2-B1` ต่อระดับ เพื่อเชื่อมกับ baseline เดิม
3. discrimination index, `P(eat|safe)`, `P(eat|toxic)` และ toxin dose ต่อ encounter
4. สัดส่วนสาเหตุการตาย โดยเฉพาะ starvation กับ durability depletion
5. จำนวน encounter ต่อ founder และ `P(eat|encounter)`
6. learned values ต่อ age bin สำหรับ B2 และ sham bin สำหรับ B3

mechanism gate: ถ้า B2 ไม่แสดงข้อมูลอายุใน learned values หรือจำนวน encounter ต่ำกว่า 30 ต่อ founder ในระดับใด ให้รายงานระดับนั้นครบแต่ห้ามอธิบายผลอายุขัยว่าเกิดจากการใช้ข้อมูลสำเร็จ

## 6. censoring, failure และ exclusion

- outcome หลักคือ `founder_mean_followup_ticks`: ค่าเฉลี่ย `final age - deterministic initial age` ของ founder ทุกตัว โดยใช้เวลาถึงตายหรือ censor ณ tick 800 จึงเป็น empirical restricted mean follow-up time; รายงานจำนวน founder ที่ยังมีชีวิตทุกแขน
- initial age กระจาย 61–199 แบบ deterministic และเหมือนกันระหว่างแขนที่จับคู่ seed ค่า `founder_mean_age` เดิมจึงให้ผลต่างระหว่างแขนเท่ากัน แต่ไม่ใช่เวลาติดตามโดยตรงและจะไม่ใช้เป็นชื่อ outcome หลัก
- ถ้ามี founder ถูก censor ให้คง empirical restricted mean follow-up เป็นหลัก และทำ sensitivity analysis เฉพาะผู้ตายเป็นผลรอง
- ไม่มีการตัด seed จากค่าผิดปกติ
- runtime failure ให้แก้สาเหตุแล้วรันซ้ำเฉพาะ arm-seed เดิม พร้อมบันทึกทั้งไฟล์เสียและเหตุผล
- ถ้า HEAD เปลี่ยนระหว่าง batch ให้ batch นั้นไม่มีสิทธิ์เป็น confirmatory evidence และรันใหม่จาก revision เดียว
- ต้องเริ่มจาก tracked tree สะอาด และบันทึก revision เริ่ม/จบ, Python, OS, flags และ raw dump ทุก run

## 7. ข้ออ้างที่อนุญาตตามผล

- H6.1 ผ่าน: representation ที่มีข้อมูลอายุมีผลต่ออายุขัยที่ขึ้นกับค่าพลังงานของทรัพยากร ภายใต้ learner และ ecology ที่ทดสอบ
- H6.1 ไม่ผ่าน: age information แก้ discrimination ได้ แต่ยังไม่มีหลักฐานว่าผลต่ออายุขัยเปลี่ยนอย่างเป็นระบบตามพลังงานในช่วงที่ทดสอบ
- ห้ามเรียกผลว่า EVPI, optimal value of information, reproductive fitness, หรือวิวัฒนาการข้ามรุ่น

## 8. สิ่งที่ต้องทำก่อน freeze

1. เขียน JSON spec ที่ถอดแบบจากตารางนี้ — **เสร็จแล้ว (ยังมีสถานะ DRAFT)**
2. เพิ่ม analyzer สำหรับ per-seed slope และทดสอบกับข้อมูลสังเคราะห์ที่รู้คำตอบ — **เสร็จแล้ว**
3. ตรวจว่า telemetry ส่ง learned value แยก age bin ออกมาครบ — **เสร็จแล้ว; raw dump และ summary ที่แก้แล้วมี `raw_fruit@0...@8`**
4. บันทึก deviation ของงานเดิมให้ครบ — **เสร็จแล้วใน prereg หลัก commit `42ed7fb`**
5. commit เอกสาร spec, analyzer, tests และ runner; รัน test suite; tag preregistration
6. หลัง tag เท่านั้นจึงเริ่ม E6 450 รันและ T2-RB 150 รัน

## 9. T2-RB replication ที่จะตรึงใน addendum เดียวกัน

ผล E5 ที่ `--drain-mult 0.5` พบ A2-A3 = -6.15 tick แต่เป็น exploratory และ A3 เดิมรับ dose ต่อ encounter 0.0728 เทียบ A2 0.0650 เมื่อดูจากมื้อที่กิน; diagnostic encounter-weighted dose เฉลี่ยต่อ run ของ A2 เท่ากับ 0.0702402

ชุดทำซ้ำใช้ seed ใหม่ `20261000` ถึง `20261049` รวม 50 seed และสามแขน:

| แขน | นิยาม | บทบาท |
|---|---|---|
| A2 | `--toxin-detox-ticks 120` | พิษเปลี่ยนตามอายุ |
| A3O | `--toxin-potency-scale 0.757811` | ทำซ้ำ control เดิมโดยตรง |
| A3R | `--toxin-potency-scale 0.7506672222220914` | control ที่ recalibrate จาก mean run-level encounter dose ของ E5 A2 |

ขนาดรวม 3 แขน × 50 seed = **150 รัน** การ recalibrate ใช้ exposure/dose ของ E5 ไม่ใช้ผลอายุขัย และเปิดเผยว่าเป็นการออกแบบหลังเห็น E5

จำนวน seed อิง smallest effect of scientific interest ที่ 5 tick และ SD ของ paired A2-A3 ใน E5 เท่ากับ 12.521 tick การคำนวณแบบ normal approximation ให้ power เพียงราว 0.43 ที่ 20 seed แต่ราว 0.81 ที่ 50 seed และ 95% CI half-width โดยประมาณ 3.47 tick การคำนวณนี้ใช้ E5 เพื่อวางขนาด replication อย่างเปิดเผย และไม่มีสิทธิ์เปลี่ยนจำนวน seed หลังดูผลชุดใหม่

primary contrast คือ A2-A3R บน `founder_mean_followup_ticks` ที่ censor horizon 400 tick โดยทำนายค่าติดลบ ทดสอบด้วย seeded Monte Carlo two-sided sign-flip 200,000 draws ที่ alpha 0.05 รายงาน CI และ effect size ตาม E1-E5 ส่วน A2-A3O เป็น direct-replication secondary contrast ถ้าสอง control ให้ข้อสรุปต่างกัน ให้ถือว่าผลไวต่อวิธี dose matching และห้ามอ้างต้นทุนของความซ่อนเร้นเป็นข้อสรุปทั่วไป

E6 H6.1 เป็นข้ออ้างหลักของบทความ ส่วน T2-RB เป็น replication question ที่แยกต่างหาก จึงกำหนด family และ alpha 0.05 แยกกัน การทดสอบรองภายในแต่ละ family ใช้ Holm ตามที่ระบุและไม่มีสิทธิ์เปลี่ยนข้อสรุปหลัก

`--drain-mult` เปลี่ยนทั้งการใช้พลังงานและการสะสมความเสียหาย ชุดนี้จึงทำซ้ำเฉพาะผลใน R-B และไม่มีสิทธิ์ระบุว่าสาเหตุมาจาก food scarcity เพียงอย่างเดียว

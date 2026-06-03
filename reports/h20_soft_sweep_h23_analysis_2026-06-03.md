# รายงานหลังทดลอง: H20 Soft Sweep และ H23 Temporal Synchronization

วันที่จัดทำ: 2026-06-03  
สถานะ: รายงานหลังทดลอง  
โฟลเดอร์ข้อมูล: `C:\artificial-evolution\data\hypothesis_diagnostics\h20_soft_sweep_h23_2026-06-03`  
สคริปต์ทดลอง: `C:\artificial-evolution\scripts\run_h20_soft_sweep_h23_diagnostics.py`

## Abstract

การทดลองรอบนี้ทดสอบ H20 ใหม่เป็น `soft sweep` หลายรูปแบบ แทน hard throttling แบบเดิมที่ทำให้ first-wave births เหลือประมาณ `3.0` และไม่เกิด Gen1 birth. ผลรวม 16 conditions x 4 seeds ยัง extinct 100% ทุก condition แต่ให้ข้อมูลสำคัญมาก:

1. H13 แข็งขึ้นในฐานะ possible necessary condition ของ second wave เพราะ H20 เดี่ยวทุกแบบไม่มี Gen1 birth และ H20 ที่มี Gen1 birth ล้วนต้องมี H13 หรือ H1+H11 เป็นฐานเวลา
2. H20a, H20b, H20d, H20e แทบไม่เปลี่ยนผลจาก baseline/H13 เลย แปลว่าใน current branch ยังไม่มี repeat-birth/litter-burst มากพอให้ soft throttle เหล่านี้ออกแรง
3. H20c เปลี่ยนผลจริง แต่เปลี่ยนไปทาง hard throttle: births ลดเหลือ `3.0`, matured ลด, Gen1 birth = 0
4. H1+H11 ยังเป็น reference ที่ดีที่สุด: `Gen1 births = 0.5`, `matured = 5.75`, `final_tick = 195.5`
5. H23 Temporal Synchronization ได้รับการสนับสนุน: ปัญหาไม่ใช่แค่มีอาหารหรือมีลูก แต่เป็นการที่ energy, mate, nest food, adulthood และ family overlap ไม่พร้อมในช่วงเวลาเดียวกัน

ข้อสรุปสั้นที่สุด:

> H20 soft sweep รอบนี้ยังไม่ชนะ H13 หรือ H1+H11. หลักฐานชี้ว่า second wave ต้องการ temporal overlap ก่อน แล้วค่อยทดสอบ pacing/throttling ใน context ที่มี first-wave overproduction จริง เช่น H17 หรือ H1+H11+H17.

## Introduction

จาก H1-H22 pattern เด่นคือ intervention ที่ดีมักแตะเรื่องเวลา:

- H11 ดีขึ้นเพราะเพิ่ม reproductive life และลด development time
- H13 ดีขึ้นเพราะเพิ่ม parent-child overlap
- H1+H11 ดีที่สุดเพราะ breeder allocation ทำงานร่วมกับ lifespan economics
- H17 เพิ่ม births แต่ไม่เพิ่ม Gen1 births จึงเหมือน first-wave ceiling หรือ overproduction without continuity

คำถามของรอบนี้คือ:

> ถ้า H13 เป็นเงื่อนไขจำเป็นของ second wave แล้ว H20 แบบนุ่มสามารถจัดจังหวะ first wave ให้ Gen1 มีโอกาส reproduce มากขึ้นได้ไหม

## Methods

### Control Variables

| Variable | Value |
|---|---:|
| body_index | 14 |
| initial_population | 250 |
| max_population | 375 |
| max_ticks | 800 |
| seeds | 7, 8, 11, 13 |
| replicates ต่อ condition | 4 |
| จำนวน conditions | 16 |

### Independent Variables

H20 ถูกแยกเป็น 5 รูปแบบ:

| Variant | ความหมาย |
|---|---|
| H20a Litter Cap Only | จำกัด litter size ของ Gen0 ใน early phase เป็น 1 แต่ไม่ block birth |
| H20b Soft Birth Spacing | เพิ่ม cooldown หลัง Gen0 birth เฉพาะแม่และ mate |
| H20c Household Buffer Only | ให้ Gen0 birth ช่วงต้นต้องมี nest food และ energy buffer เพิ่ม |
| H20d First Birth Free, Repeat Gated | birth แรกปล่อยตามปกติ แต่ repeat birth ช่วงต้นต้องมี child bridge หรือ surplus |
| H20e Temporal Window Matching | รวม repeat gate แบบอ่อน, early litter cap และ block late low-energy birth |

ทดสอบ interaction:

- H20a-e เดี่ยว
- H20a-e + H13
- H20d + H13 + H21
- H20d + H13 + H22
- reference: baseline, H13, H1+H11, H17

### Dependent Variables

ตัวแปรตามหลัก:

- total births
- matured children
- Gen1 births
- second-wave success rate
- Gen1 exact-ready ticks
- Gen1 spawn events
- final tick

ตัวแปรตามเชิงกลไก:

- Gen1 energy_ok rate
- Gen1 nest_food_ok rate
- Gen1 mate_ok rate
- Gen1 ready-no-want ticks
- Gen1 want-no-spawn ticks

### Success Criteria

ถือว่า H20 soft sweep สำเร็จถ้า condition ใด condition หนึ่ง:

- เพิ่ม Gen1 births มากกว่า H13
- เพิ่ม Gen1 exact-ready ticks มากกว่า H13
- ไม่ทำให้ total births collapse ต่ำกว่า 5
- ไม่เพิ่มแค่ final tick/nest food โดยไม่มี offspring continuity

## Results

### Condition Summary

| Condition | Births | Matured | Gen1 Births | 2nd Wave | Final Tick | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| baseline | 6.00 | 2.00 | 0.00 | 0.00 | 132.00 | control collapse |
| H13 | 6.25 | 6.00 | 0.25 | 0.25 | 128.00 | parent-child overlap creates one second-wave signal |
| H17 | 9.00 | 2.75 | 0.00 | 0.00 | 157.50 | more births, no second wave |
| H20a | 6.00 | 2.00 | 0.00 | 0.00 | 132.00 | identical to baseline |
| H20b | 6.00 | 2.00 | 0.00 | 0.00 | 132.00 | identical to baseline |
| H20c | 3.00 | 1.75 | 0.00 | 0.00 | 150.25 | behaves like hard throttle |
| H20d | 6.00 | 2.00 | 0.00 | 0.00 | 132.00 | identical to baseline |
| H20e | 6.00 | 2.00 | 0.00 | 0.00 | 132.00 | identical to baseline |
| H1+H11 | 6.50 | 5.75 | 0.50 | 0.25 | 195.50 | best current second-wave signal |
| H20a+H13 | 6.25 | 6.00 | 0.25 | 0.25 | 128.00 | identical to H13 |
| H20b+H13 | 6.25 | 6.00 | 0.25 | 0.25 | 128.00 | identical to H13 |
| H20c+H13 | 3.00 | 2.50 | 0.00 | 0.00 | 159.50 | throttles too much |
| H20d+H13 | 6.25 | 6.00 | 0.25 | 0.25 | 128.00 | identical to H13 |
| H20e+H13 | 6.25 | 6.00 | 0.25 | 0.25 | 128.00 | identical to H13 |
| H20d+H13+H21 | 6.25 | 6.00 | 0.25 | 0.25 | 169.25 | survival improves, no extra Gen1 birth |
| H20d+H13+H22 | 6.25 | 6.00 | 0.25 | 0.25 | 145.00 | survival improves slightly, no extra Gen1 birth |

### Seed-Level Second-Wave Events

Gen1 birth เกิดเฉพาะ seed 7:

| Condition | Seed | Final Tick | Births | Matured | Gen1 Births | First Gen1 Ready Tick | Nest Food Remaining |
|---|---:|---:|---:|---:|---:|---:|---:|
| H13 | 7 | 164 | 7 | 7 | 1 | 67 | 100 |
| H1+H11 | 7 | 359 | 8 | 8 | 2 | 100 | 888 |
| H20a+H13 | 7 | 164 | 7 | 7 | 1 | 67 | 100 |
| H20b+H13 | 7 | 164 | 7 | 7 | 1 | 67 | 100 |
| H20d+H13 | 7 | 164 | 7 | 7 | 1 | 67 | 100 |
| H20e+H13 | 7 | 164 | 7 | 7 | 1 | 67 | 100 |
| H20d+H13+H21 | 7 | 261 | 7 | 7 | 1 | 67 | 185 |
| H20d+H13+H22 | 7 | 244 | 7 | 7 | 1 | 67 | 138 |

การตีความ:

- H20a/b/d/e + H13 ไม่ได้สร้าง event ใหม่ แต่รักษา event เดิมของ H13
- H21/H22 เพิ่ม final tick และ food remaining บางส่วน แต่ Gen1 birth event ยังเป็น event เดิม
- H1+H11 เป็นตัวเดียวที่เพิ่ม Gen1 births เป็น 2 ใน seed 7 และยืด final tick ชัดเจน

## Gate Analysis

### Gen1 Gate Rates

| Condition | Gen1 Samples | Gen1 Females | Exact Ready | Spawn | Energy OK | Nest Food OK | Mate OK |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 148 | 11 | 0 | 0 | 0.07 | 0.74 | 0.12 |
| H13 | 253 | 11 | 1 | 1 | 0.00 | 0.26 | 0.17 |
| H17 | 270 | 19 | 0 | 0 | 0.26 | 0.52 | 0.05 |
| H20c | 141 | 4 | 0 | 0 | 0.03 | 0.93 | 0.24 |
| H1+H11 | 205 | 11 | 2 | 2 | 0.16 | 0.56 | 0.33 |
| H20d+H13+H21 | 350 | 11 | 1 | 1 | 0.00 | 0.47 | 0.12 |
| H20d+H13+H22 | 385 | 11 | 1 | 1 | 0.00 | 0.53 | 0.11 |

หมายเหตุ: ค่า Energy OK ของ H13/H21/H22 ถูก round เป็น `0.00` ในตารางนี้ เพราะต่ำมาก ไม่ใช่แปลว่าไม่มี tick ใดผ่านเลยในทุก seed.

### Decision Quality Check

ผลตรวจเหมือน H19:

- ready_no_want_ticks = 0
- want_no_spawn_ticks = 0
- เมื่อ female exact-ready ระบบ spawn ได้

แปลว่า H20 soft sweep ไม่พบ bug ประเภท:

> female พร้อมทุก gate แล้ว AI ไม่ยอม reproduce

ปัญหายังอยู่ก่อนถึง decision policy คือ Gen1 แทบไม่ exact-ready.

## Hypothesis Testing

### H13: Parent-Child Overlap

หลักฐานสนับสนุน:

- H13 เป็น condition เดี่ยวที่ทำให้ Gen1 births > 0
- H20 variants ที่ไม่มี H13 ไม่มี Gen1 birth
- H20a/b/d/e เมื่อรวม H13 ได้ Gen1 birth เท่ากับ H13

หลักฐานคัดค้าน:

- H13 ยังไม่พอให้ระบบรอด
- Gen1 birth เกิดแค่ 1 จาก 4 seeds
- H1+H11 ชนะ H13 ใน final tick และ Gen1 births

ระดับความมั่นใจ:

> สูงระดับ exploratory ว่า H13 เป็น necessary-condition candidate แต่ยังไม่ใช่ sufficient condition

### H20: First-Wave Throttling / Pacing

หลักฐานสนับสนุน:

- H20c แสดงว่าการแตะ birth gate เปลี่ยน system trajectory ได้จริง
- H20d/e แนวคิดยังไม่ถูก falsify ใน context ที่มี repeat births มาก เพราะ current baseline แทบไม่มี repeat-birth pressure

หลักฐานคัดค้าน:

- H20a/b/d/e เดี่ยวให้ผลเหมือน baseline
- H20a/b/d/e + H13 ให้ผลเหมือน H13
- H20c ลด births เหลือ `3.0` และทำลาย Gen1 cohort

ระดับความมั่นใจ:

> H20 เวอร์ชันที่ทดสอบในรอบนี้ยังไม่ supported. แต่ H20 concept ยังไม่ควรถูกทิ้ง เพราะเงื่อนไขทดลองรอบนี้อาจไม่มี first-wave overproduction มากพอให้ soft throttle ทำงาน

### H21: Nest Inheritance

หลักฐานสนับสนุน:

- H20d+H13+H21 เพิ่ม final tick จาก 128.0 เป็น 169.25
- nest food remaining ใน seed 7 เพิ่มจาก 100 เป็น 185
- Gen1 nest_food_ok ดีขึ้นเมื่อเทียบกับ H13

หลักฐานคัดค้าน:

- Gen1 births ไม่เพิ่ม
- exact-ready ยังเท่า H13
- energy_ok ยังต่ำมาก

ระดับความมั่นใจ:

> ยังอ่านยาก. H21 อาจช่วย local continuity แต่ยังไม่แก้ temporal/energy gate

### H22: Mate Synchronization

หลักฐานสนับสนุน:

- final tick เพิ่มจาก H13 บางส่วน: 128.0 เป็น 145.0
- รักษา Gen1 birth event เดิมได้

หลักฐานคัดค้าน:

- Gen1 births ไม่เพิ่ม
- mate_ok ไม่ได้ดีขึ้นชัดเมื่อเทียบกับ H13 ใน aggregate
- exact-ready ยังเท่า H13

ระดับความมั่นใจ:

> ยังต่ำ. ต้องทดสอบใหม่เมื่อ Gen1 cohort ใหญ่กว่านี้

### H23: Temporal Synchronization

หลักฐานสนับสนุน:

- H1+H11 ยังดีที่สุด เพราะจัดเวลา lifespan + development + breeder allocation ได้ดีกว่า
- H13 ช่วยเพราะเพิ่ม overlap ของรุ่นพ่อแม่กับลูก
- H17 เพิ่ม births แต่ไม่มี Gen1 birth แปลว่า birth volume อย่างเดียวไม่พอ
- H21/H22 เพิ่ม survival/nest food บางส่วนแต่ไม่เพิ่ม Gen1 exact-ready แปลว่าทรัพยากรหรือ mate เดี่ยวๆ ไม่พอ
- decision policy ไม่ใช่ bottleneck หลัง exact-ready เพราะ ready-to-spawn conversion ยังดี

หลักฐานคัดค้าน:

- sample size ยังมีแค่ 4 seeds ต่อ condition
- H23 ยังเป็น hypothesis ระดับ system pattern ไม่ใช่ patch เดี่ยว
- ยังไม่ได้วัด overlap ของ male/female adult windows แบบละเอียดทุก lineage

ระดับความมั่นใจ:

> สูงขึ้นมากในฐานะ main explanatory hypothesis ของ H1-H23

## Discussion

### 1. H13 ดูเหมือนเงื่อนไขจำเป็นมากขึ้น

ผลใหม่ทำให้ประโยคนี้แข็งขึ้น:

> ถ้าไม่มี two-generation overlap ระบบแทบไม่มีทางสร้าง second wave

H20 เดี่ยวทุกแบบไม่มี Gen1 birth. H20 ที่มี Gen1 birth เกิดได้เมื่อจับกับ H13 หรืออยู่ใน reference H1+H11 เท่านั้น. นี่ไม่ได้แปลว่า H13 แก้ปัญหาแล้ว แต่แปลว่า H13 อาจเป็นฐานเวลาที่ต้องมีก่อนการแก้อื่นจะออกผล.

### 2. H20 soft sweep รอบนี้ไม่ได้แสดงพลัง เพราะผิด context

H20a/b/d/e ถูกออกแบบมาแก้ first-wave burst หรือ repeat-birth trap. แต่ baseline ปัจจุบัน birth เฉลี่ยแค่ `6.0` และส่วนใหญ่ไม่เกิด repeat-birth pressure ที่ชัด. ดังนั้นหลาย variant ไม่ได้แตะ trajectory จริง ผลจึง identical.

นี่เป็น negative result ที่มีประโยชน์:

> H20 soft throttle ต้องทดสอบใน condition ที่มี overproduction จริง เช่น H17 หรือ H1+H11+H17 ไม่ใช่ baseline ที่ birth น้อยอยู่แล้ว

### 3. H20c คือคำเตือน

H20c เป็น variant เดียวที่เปลี่ยนผลชัด แต่เปลี่ยนไปทางผิด:

- births ลดเหลือ 3.0
- matured ต่ำ
- Gen1 birth = 0
- nest_food_ok สูงขึ้น แต่ offspring continuity ไม่เกิด

นี่คือภาพเดิมของ hard throttle:

> wealth หรือ buffer เพิ่ม แต่ reproduction chain หาย

### 4. H1+H11 ยังเป็น baseline ใหม่ที่ควรใช้เทียบ

H1+H11 ชนะทุก H20 soft condition ในรอบนี้:

- Gen1 births = 0.5
- final_tick = 195.5
- matured = 5.75
- seed 7 มี Gen1 births = 2

แปลว่า next experiment ควรใช้ H1+H11 หรือ H13+H1+H11 เป็นฐาน ไม่ใช่ baseline เดิมอย่างเดียว.

### 5. H21/H22 ยังไม่ควรถูกตัดสินเดี่ยวๆ

H21/H22 เพิ่ม final tick และ local food continuity บางส่วน แต่ไม่เพิ่ม Gen1 birth. ข้อมูลนี้ยังไม่พอจะบอกว่า H21/H22 ผิด เพราะ Gen1 cohort ยังเล็กเกินและ energy gate ยังต่ำมาก.

ภาพตอนนี้คือ:

> H21/H22 อาจเป็น amplifier หลังจากมี Gen1 cohort พอแล้ว แต่ยังไม่ใช่ root cause

## Limitations

- ใช้ 4 seeds ต่อ condition จึงเป็น exploratory diagnostic ไม่ใช่ statistical proof
- patch เป็น monkeypatch ระหว่างทดลอง ไม่ใช่ implementation ถาวร
- ยังไม่ได้ sweep parameter strength ของ H20 แต่ละแบบ
- ยังไม่ได้ทดสอบ H20 soft variants ใน high-birth context โดยตรง
- H23 ยังต้องมี metric เพิ่ม เช่น male-female adult overlap, household two-generation duration, และ synchronized gate windows

## Future Work

### Experiment A: H13 + H1 + H11

คำถาม:

> ถ้า H13 เป็น necessary condition และ H1+H11 เป็น best timing base เมื่อนำมารวมกันจะเกิด second wave มากกว่าเดิมไหม

Conditions:

- baseline
- H13
- H1+H11
- H13+H1+H11
- H13+H1+H11+H21
- H13+H1+H11+H22
- H13+H1+H11+H21+H22

### Experiment B: H20 ใน High-Birth Context

คำถาม:

> H20 soft throttle ช่วยจริงไหมเมื่อระบบมี first-wave overproduction

Conditions:

- H17
- H20d+H17
- H20e+H17
- H13+H17
- H20d+H13+H17
- H20e+H13+H17
- H1+H11+H17
- H20d+H1+H11+H17
- H20e+H1+H11+H17

### Experiment C: H24 Energy Synchronization

สมมุติฐานใหม่ที่ควรเพิ่ม:

> H24: Energy Synchronization Hypothesis  
> ระบบไม่ได้ขาด energy เฉลี่ย แต่ Gen1 female ไม่มี energy พอใน tick เดียวกับที่ mate/nest/adulthood พร้อม

ตัวแปรที่ควรวัด:

- Gen1 energy_ok streak length
- overlap ระหว่าง energy_ok และ mate_ok
- overlap ระหว่าง energy_ok และ nest_food_ok
- ticks ที่ขาดเพียง 1 gate ก่อน exact-ready
- energy recovery time หลัง birth และหลัง caregiving

## Conclusion

ผลรอบนี้ทำให้ลำดับน้ำหนักเปลี่ยนเป็น:

1. H23 Temporal Synchronization / Gen1 gate alignment
2. H13 Parent-child overlap as necessary-condition candidate
3. H1+H11 as best current timing base
4. H20 soft throttling only in high-birth context
5. H21/H22 as possible amplifiers, not root cause yet

คำตอบต่อ ranking เดิม:

- เห็นด้วยที่ให้ H13 สูงมาก และหลักฐานรอบนี้ยิ่งทำให้ H13 ดูจำเป็น
- H20 soft throttling ยังน่าสนใจ แต่ต้องย้ายไปทดลองใน context ที่ births เยอะ เช่น H17/H1+H11+H17
- H21/H22 ยังไม่น่าตัดสิน เพราะ cohort เล็กและ energy gate ยังเป็นคอขวด
- H23 ควรถูกยกเป็น hypothesis หลักของรอบถัดไป เพราะอธิบาย pattern จาก H1-H23 ได้ดีที่สุด

สรุปแบบตรงที่สุด:

> โลกนี้ไม่ได้แค่ขาดอาหาร และไม่ได้แค่ขาดลูก. มันขาดช่วงเวลาที่คนรุ่นต่างๆ พร้อมพร้อมกันพอจะเปลี่ยน birth เป็น lineage continuation.

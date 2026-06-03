# รายงานวิเคราะห์ H20-H22: First-Wave Throttling, Nest Inheritance, Mate Synchronization

วันที่ทดลอง: 2026-06-03  
รายงานก่อนทดลอง: `reports/pre_experiment_plan_h20_h22_family_chain_2026-06-03.md`  
สคริปต์ทดลอง: `scripts/run_h20_h22_family_chain_diagnostics.py`  
รายงานอัตโนมัติ: `reports/h20_h22_family_chain_diagnostics_2026-06-03.md`  
ผลดิบ: `data/hypothesis_diagnostics/h20_h22_family_chain_2026-06-03/`

## Abstract

ทดลอง H20-H22 ครบ 48 runs เพื่อทดสอบ ranking ใหม่:

1. H20 First-wave Throttling
2. H13 Parent-child Overlap
3. H21 Nest Inheritance
4. H22 Mate Synchronization

ผลรอบนี้บอกว่า H20 implementation แรก throttle แรงเกินไป. มันลด births จาก baseline `6.0` เหลือ `3.0`, ทำให้ first wave เบาลงจริง และบาง interaction เพิ่ม final tick ได้มาก เช่น H20+H13 final tick `209.5`. แต่ Gen1 births ยัง `0.0` ทุก H20 condition.

ดังนั้นยังไม่ควรสรุปว่า H20 ผิด. ควรสรุปว่า:

> H20 direction ยังน่าสนใจ แต่ H20 version แรก under-produces first wave จนมี Gen1 น้อยเกินไปและยังไม่สร้าง second wave

H13 และ H1+H11 ยังเป็น positive controls ที่สำคัญที่สุด เพราะเป็น condition เดียวที่มี Gen1 births.

## Methods

Control variables:

- body_index: `14`
- initial_population: `250`
- max_population: `375`
- max_ticks: `800`
- seeds: `7, 8, 11, 13`
- total runs: `48`

Conditions:

- baseline
- H13
- H1+H11
- H17
- H20
- H20+H13
- H20+H21
- H20+H22
- H20+H13+H21
- H20+H13+H22
- H20+H21+H22
- H20+H13+H21+H22

H20 diagnostic intervention:

- stagger founder births
- require household food buffer before early founder birth
- cap early founder litter size to 1
- block repeated founder birth until adult child exists or sufficient time passes

H21 diagnostic intervention:

- force Gen1 to prefer parent/shared nest owner when parent nest exists
- allow limited inherited nest withdrawal for Gen1 juvenile/adult

H22 diagnostic intervention:

- route Gen1 adults back to inherited nest for rendezvous when energy is sufficient

## Results

### 1. Main Summary

| Condition | Final Tick | Births | Matured | Gen1 Births | Second Wave | Gen1 Ready |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 132.0 | 6.0 | 2.0 | 0.0 | 0.00 | 0.0 |
| H13 | 128.0 | 6.25 | 6.0 | 0.25 | 0.25 | 0.25 |
| H1+H11 | 195.5 | 6.5 | 5.75 | 0.5 | 0.25 | 0.5 |
| H17 | 157.5 | 9.0 | 2.75 | 0.0 | 0.00 | 0.0 |
| H20 | 145.5 | 3.0 | 1.5 | 0.0 | 0.00 | 0.0 |
| H20+H13 | 209.5 | 3.25 | 3.0 | 0.0 | 0.00 | 0.0 |
| H20+H21 | 160.0 | 3.0 | 1.5 | 0.0 | 0.00 | 0.0 |
| H20+H22 | 145.5 | 3.0 | 1.5 | 0.0 | 0.00 | 0.0 |
| H20+H13+H21 | 174.5 | 3.25 | 3.0 | 0.0 | 0.00 | 0.0 |
| H20+H13+H22 | 209.5 | 3.25 | 3.0 | 0.0 | 0.00 | 0.0 |
| H20+H21+H22 | 160.0 | 3.0 | 1.5 | 0.0 | 0.00 | 0.0 |
| H20+H13+H21+H22 | 174.5 | 3.25 | 3.0 | 0.0 | 0.00 | 0.0 |

ทุก condition ยังสูญพันธุ์ 100%.

### 2. H20 ลด first wave จริง แต่แรงเกินไป

H20 ลด births:

- baseline: `6.0`
- H20: `3.0`
- H20+H13: `3.25`

ผลดี:

- H20 เพิ่ม final tick จาก `132.0` เป็น `145.5`
- H20+H13 เพิ่ม final tick เป็น `209.5`

ผลเสีย:

- matured ลดใน H20 เดี่ยว จาก `2.0` เป็น `1.5`
- H20+H13 matured `3.0`, ต่ำกว่า H13 เดี่ยว `6.0`
- Gen1 births ยัง `0.0`

ตีความ:

H20 ไม่ผิดในเชิงทิศทาง แต่ implementation รอบนี้ throttle มากเกิน ทำให้ first wave เล็กเกินจนไม่มีฐาน Gen1 ที่แข็งแรงพอ

### 3. H13 ยังเป็น signal ที่แข็งที่สุดร่วมกับ H1+H11

มีเพียงสอง condition ที่มี Gen1 births:

- H13: `0.25`
- H1+H11: `0.5`

H20+H13 เพิ่ม final tick สูงกว่า H13 แต่ Gen1 birth กลับหายไป.

แปลว่า parent-child overlap ยังสำคัญ แต่ถ้า throttle first wave แรงเกินไป H13 ก็ไม่มี cohort พอให้ second wave เกิด

### 4. H21 ยังอ่านผลไม่ได้เต็มที่

H21 เมื่อจับกับ H20:

- H20+H21 final tick `160.0`, births `3.0`, Gen1 births `0.0`
- H20+H13+H21 final tick `174.5`, ต่ำกว่า H20+H13 `209.5`

Gen1 gate rates ใน H20+H13+H21:

- energy_ok `0.000`
- near_nest `1.000`
- nest_food_ok `0.529`
- mate_ok `0.082`

ตีความ:

H21 ทำให้ Gen1 อยู่กับ nest ได้ แต่ไม่ได้แก้ energy. จึงอาจทำให้ near_nest ดีขึ้นแต่ไม่พอสร้าง full-ready.

### 5. H22 แทบไม่มีผลในรูปแบบนี้

H20+H22 เท่ากับ H20 แทบทุกค่า. H20+H13+H22 เท่ากับ H20+H13.

ตีความ:

H22 แบบ rendezvous อย่างเดียวไม่พอ หรือยังไม่มี Gen1 cohort/energy พอให้ mate synchronization แสดงผล

### 6. Gen1 gate rates

| Condition | Gen1 Samples | Energy OK | Near Nest | Nest Food OK | Mate OK | Top Blocks |
|---|---:|---:|---:|---:|---:|---|
| baseline | 148 | 0.068 | 1.000 | 0.736 | 0.115 | low_energy, no_mate, nest_food_low |
| H13 | 253 | 0.004 | 1.000 | 0.261 | 0.166 | low_energy, no_mate, nest_food_low |
| H1+H11 | 205 | 0.156 | 0.966 | 0.556 | 0.327 | low_energy, no_mate, nest_food_low |
| H17 | 270 | 0.259 | 0.630 | 0.522 | 0.052 | no_mate, low_energy, nest_food_low |
| H20 | 168 | 0.000 | 1.000 | 0.946 | 0.018 | low_energy, no_mate |
| H20+H13 | 317 | 0.167 | 0.868 | 0.691 | 0.054 | no_mate, low_energy, nest_food_low |
| H20+H13+H21 | 208 | 0.000 | 1.000 | 0.529 | 0.082 | low_energy, no_mate, nest_food_low |
| H20+H13+H22 | 317 | 0.167 | 0.868 | 0.691 | 0.054 | no_mate, low_energy, nest_food_low |

ข้อสรุปจาก gates:

- H20 เดี่ยวทำให้ nest_food_ok สูงมาก `0.946` แต่ energy_ok เป็น `0.000`
- H20+H13 ดีขึ้นด้าน energy_ok `0.167` และ nest_food_ok `0.691` แต่ mate_ok ต่ำ `0.054`
- H1+H11 ยังสมดุลที่สุด: energy_ok `0.156`, nest_food_ok `0.556`, mate_ok `0.327`

## Hypothesis Testing

### H20: First-wave Throttling

Evidence supporting:

- ลด births ได้จริง
- เพิ่ม final tick ได้ โดยเฉพาะ H20+H13
- ลดแรง first-wave shock ได้บางส่วน

Evidence against:

- Gen1 exact-ready ไม่เพิ่ม
- Gen1 births ยัง `0.0`
- matured ลดหรือไม่ชนะ H13/H1+H11

Alternative explanation:

- H20 implementation แรงเกิน ไม่ใช่ H20 concept ผิด
- throttle ลด cohort size จนไม่มี Gen1/mate pool พอ

Confidence:

- H20 concept: ยังเปิดอยู่
- H20 implementation รอบนี้: ไม่ผ่าน

### H13: Parent-child Overlap

Evidence supporting:

- H13 เดี่ยวมี Gen1 birth
- H13 ทำ matured สูงกว่า H20+H13

Evidence against:

- H20+H13 ไม่เกิด Gen1 birth

Alternative explanation:

- H13 ต้องการ cohort size พอสมควร ถ้า H20 ลด first wave มากไป H13 แสดงผลไม่ได้

Confidence: สูงว่ายังสำคัญ

### H21: Nest Inheritance

Evidence supporting:

- near_nest ดีมากเมื่อ H21 อยู่ใน stack

Evidence against:

- energy_ok เป็น 0 ใน H20+H13+H21
- Gen1 birth ไม่เพิ่ม

Alternative explanation:

- H21 อาจทำให้ Gen1 อยู่รัง แต่รังไม่ได้แก้ energy/mate

Confidence: ยังไม่พอ ต้องทดสอบหลัง H20 อ่อนลง

### H22: Mate Synchronization

Evidence supporting:

- ยังไม่เห็นชัด

Evidence against:

- H22 ไม่เปลี่ยน outcome ใน stack ที่รัน

Alternative explanation:

- mate sync ต้องมี Gen1 energy/cohort มากกว่านี้ก่อน

Confidence: ต่ำใน implementation นี้

## Discussion

ผลรอบนี้สอนสิ่งสำคัญ: การ throttle first wave เป็นแนวคิดที่น่าถูก แต่ไม่ควร throttle แบบลด birth ลงครึ่งหนึ่งทันที.

ระบบต้องมี first wave มากพอให้:

- มี Gen1 female
- มี Gen1 male
- มี overlap ระหว่างสองเพศ
- มีแรงงานช่วย household

แต่ first wave ต้องไม่มากจน household bankrupt.

ดังนั้น H20 ที่ดีควรเป็น `soft throttling` ไม่ใช่ `hard throttling`.

สิ่งที่ H20 version นี้ทำได้:

- ลด birth pressure
- เพิ่ม survival time
- เพิ่ม food availability บางส่วน

สิ่งที่ยังทำไม่ได้:

- สร้าง Gen1 exact-ready
- เพิ่ม mate_ok
- เพิ่ม Gen1 births

## Next Experiment

ควรทำ H20 sweep แทน H20 เดี่ยว:

### H20a: Litter Cap Only

- cap litter size = 1
- ไม่ stagger birth
- ไม่เพิ่ม household buffer

ทดสอบว่าปัญหาคือ litter burst หรือไม่

### H20b: Soft Birth Spacing

- หลังแม่มีลูก ให้ cooldown/spacing เพิ่มเฉพาะแม่คนเดิม
- ไม่ block founder คนอื่นมากเกิน

### H20c: Household Buffer Only

- ต้องมี nest food buffer ก่อน birth เพิ่ม
- ไม่ stagger

### H20d: Gen1-Ready Throttle

- founder มีลูกได้ครั้งแรกปกติ
- birth รอบต่อไปถูก block จนมี Gen1 juvenile/adult หรือ household buffer สูง

### Candidate next condition list

ควรรัน:

- baseline
- H13
- H1+H11
- H20a
- H20b
- H20c
- H20d
- H20a+H13
- H20b+H13
- H20d+H13
- H20b+H13+H21
- H20b+H13+H22

## Final Conclusion

Ranking ของคุณยังดี:

1. H20
2. H13
3. H21
4. H22

แต่ผลรอบนี้บอกว่า H20 ต้องเป็น soft control ไม่ใช่ hard throttle. H20 version แรกประหยัดเกินจน first-wave cohort เล็กเกินไป และไม่สร้าง second wave.

คำสรุป:

> ไม่ใช่ "ยิ่งมีลูกน้อยยิ่งดี" แต่คือ "มีลูกพอดีและเว้นจังหวะให้ household ข้ามเป็นสองรุ่นได้"


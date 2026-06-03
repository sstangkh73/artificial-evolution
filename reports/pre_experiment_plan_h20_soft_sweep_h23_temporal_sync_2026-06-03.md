# รายงานก่อนทดลอง: H20 Soft Sweep และ H23 Temporal Synchronization

วันที่จัดทำ: 2026-06-03  
สถานะ: รายงานก่อนทดลอง  
ฐานอ้างอิง: H1-H22 diagnostics

## Abstract

ผล H1-H22 เริ่มชี้ pattern เดียวกัน: intervention ที่ดีขึ้นมักเกี่ยวกับเวลา ไม่ใช่ทรัพยากรดิบ. H11 ช่วยเพราะยืด reproductive life และลด development time. H13 ช่วยเพราะเพิ่ม parent-child overlap. H1+H11 ดีที่สุดเพราะจัด breeder allocation ร่วมกับ lifespan economics. ส่วน food, technology, mutation, cooldown และ support tweaks หลายตัวให้ผลน้อยหรือเป็น false positive.

ดังนั้นรายงานนี้ตั้งกรอบใหม่:

> H23: Temporal Synchronization Hypothesis

ระบบอาจไม่ได้ขาดทรัพยากรเป็นหลัก แต่ขาดช่วงเวลาที่ gate สำคัญพร้อมพร้อมกัน: แม่พร้อมแต่ลูกยังเด็ก, ลูกพร้อมแต่แม่ตาย, ตัวเมียพร้อมแต่ตัวผู้ไม่พร้อม, ตัวผู้พร้อมแต่อาหารหมด, nest พร้อมแต่ energy ไม่พอ.

ภายใต้ H23 จะทดลอง H20 ใหม่เป็น `soft sweep` ไม่ใช่ hard throttle แบบเดิม. H20 เวอร์ชันเก่าลด births เหลือประมาณ `3.0` และทำให้ second wave หาย. รอบนี้จะทดสอบ H20 หลายรูปแบบที่นุ่มกว่า เพื่อหา birth pacing ที่ไม่ทำลาย Gen1 cohort.

## 1. Research Problem

คำถามหลัง H19-H22:

> ถ้า Gen1 ไม่มีลูกเพราะ gate ต่างๆ ไม่ sync กัน เราควรจัดเวลา first-wave birth อย่างไรให้เกิด two-generation household จริง

หลักฐานเดิม:

- H13 มี Gen1 birth > 0 หลายรอบของการวิเคราะห์
- H1+H11 เป็น best second-wave signal
- H20 hard throttle เพิ่ม final tick ได้ แต่ Gen1 birth = 0 เพราะ first-wave cohort เล็กเกิน
- H17 เพิ่ม birth/matured แต่ Gen1 birth = 0 จึงเป็น first-wave overproduction warning

## 2. Revised Ranking

ลำดับสมมุติฐานหลัง H22:

1. H13 Parent-child Overlap
2. H20 Soft Throttling
3. H23 Gen1 Gate Alignment / Temporal Synchronization
4. H21 Nest Inheritance
5. H22 Mate Synchronization

เหตุผล:

- H13 อาจเป็น necessary condition ของ second wave
- H20 ต้องช่วยจัดจังหวะ ไม่ใช่ลด birth อย่างแข็ง
- H21/H22 ยังอ่านยาก เพราะ Gen1 cohort เล็กเกินใน H20 hard throttle

## 3. H23: Temporal Synchronization Hypothesis

สมมุติฐาน:

> ระบบไม่ขาด gate ทีละตัว แต่ gate เหล่านั้นไม่พร้อมใน tick เดียวกันพอให้ Gen1 reproduce

ตัวอย่าง temporal mismatch:

- mother ready แต่ child ยังไม่โต
- child ready แต่ mother/household ตายแล้ว
- female ready แต่ male ยัง juvenile หรือตายแล้ว
- mate ready แต่ local nest food หมด
- food ready แต่ female energy ต่ำ
- nest exists แต่ Gen1 household identity ไม่ sync

ตัวแปรตาม:

- Gen1 exact-ready ticks
- Gen1 spawn events
- Gen1 gate overlap rates
- parent-child adult overlap
- Gen1 male/female adult overlap
- first birth tick distribution
- spacing between founder births

Success criteria:

- ไม่จำเป็นต้องเพิ่ม total births
- ต้องเพิ่ม Gen1 exact-ready หรือ Gen1 births
- ต้องลด false positive แบบ births/matured สูงแต่ Gen1 birth = 0

## 4. H20 Soft Sweep

### H20a: Litter Cap Only

สมมุติฐาน:

> ปัญหาไม่ได้อยู่ที่ birth แรกเร็วเกิน แต่อยู่ที่ litter burst หรือจำนวนลูกต่อครั้งมากเกิน

ตัวแปรต้น:

- cap litter size ของ Gen0 เป็น 1 ใน early phase
- ไม่ block birth tick
- ไม่ require extra household buffer

ตัวแปรตาม:

- total births
- matured children
- Gen1 exact-ready
- Gen1 births
- Gen1 energy_ok

คาดการณ์:

- births อาจลดเล็กน้อย ไม่ควรลดเหลือ 3
- ถ้าช่วยจริง Gen1 energy_ok หรือ Gen1 exact-ready ต้องเพิ่ม

### H20b: Soft Birth Spacing

สมมุติฐาน:

> birth ไม่ควรถูก block ทั้ง population แต่ mother คนเดิมควรเว้นรอบหลังคลอด

ตัวแปรต้น:

- หลังแม่ Gen0 มีลูกแล้ว เพิ่ม spacing เฉพาะแม่คนนั้น
- ไม่ block mothers คนอื่น
- ไม่ cap first birth ทั่ว population

ตัวแปรตาม:

- second birth probability
- Gen1 exact-ready
- Gen1 births
- mother post-birth survival

คาดการณ์:

- ลด first-wave pressure โดยไม่ทำให้ cohort เล็กเกิน

### H20c: Household Buffer Only

สมมุติฐาน:

> birth ควรเกิดเมื่อ household มี local buffer พอ ไม่ใช่ลด birth โดยไม่ดูสถานะรัง

ตัวแปรต้น:

- require nest food buffer ก่อน birth
- buffer อาจขึ้นกับ local child load
- ไม่ stagger และไม่ cap litter โดยตรง

ตัวแปรตาม:

- nest_food_ok
- Gen1 energy_ok
- Gen1 exact-ready
- births

คาดการณ์:

- ถ้าปัญหาเป็น household bankruptcy H20c จะช่วย Gen1 energy/nest food
- ถ้า buffer สูงเกิน จะกลายเป็น H20 hard throttle อีกครั้ง

### H20d: First Birth Free, Repeat Birth Gated

สมมุติฐาน:

> first birth จำเป็นเพื่อสร้าง Gen1 cohort แต่ repeat birth ก่อน Gen1/household พร้อมคือจุดที่ทำให้ระบบพัง

ตัวแปรต้น:

- ให้ Gen0 first birth เกิดตามปกติ
- block repeat birth จนกว่า:
  - มี Gen1 juvenile/adult ใน household, หรือ
  - nest food buffer สูงพอ, หรือ
  - mother energy สูงกว่า threshold

ตัวแปรตาม:

- first-wave size
- second birth timing
- Gen1 adult count
- Gen1 exact-ready
- Gen1 births

คาดการณ์:

- นี่น่าจะเป็น H20 variant ที่น่าสนใจที่สุด เพราะไม่ตัด first-wave cohort

### H20e: Temporal Window Matching

สมมุติฐาน:

> birth timing ควรพยายามให้ Gen1 adult window overlap กับ parent/household survival window

ตัวแปรต้น:

- encourage births in early-but-not-too-early window
- discourage birth ถ้า mother energy ต่ำหลัง household already stressed
- combine mild spacing + mild buffer

ตัวแปรตาม:

- parent-child adult overlap
- Gen1 exact-ready
- Gen1 births

คาดการณ์:

- อาจทำงานดีที่สุดเมื่อรวมกับ H13

## 5. Conditions

รอบทดลองควรใช้ 16 conditions:

| Condition | เหตุผล |
|---|---|
| baseline | control |
| H13 | possible necessary condition |
| H1+H11 | best prior second-wave signal |
| H17 | first-wave overproduction warning |
| H20a | litter cap only |
| H20b | soft birth spacing |
| H20c | household buffer only |
| H20d | first birth free, repeat gated |
| H20e | temporal window matching |
| H20a+H13 | test cap under overlap |
| H20b+H13 | test spacing under overlap |
| H20c+H13 | test buffer under overlap |
| H20d+H13 | candidate strongest |
| H20e+H13 | temporal sync candidate |
| H20d+H13+H21 | inheritance after cohort exists |
| H20d+H13+H22 | mate sync after cohort exists |

## 6. Control Variables

- body_index: `14`
- initial_population: `250`
- max_population: `375`
- max_ticks: `800`
- seeds: `7, 8, 11, 13`
- same trace engine as H19/H20-H22

## 7. Metrics

Primary metrics:

- Gen1 births
- Gen1 exact-ready ticks
- Gen1 spawn events
- second-wave success rate
- max generation observed

Secondary metrics:

- total births
- matured children
- Gen1 adult females seen
- Gen1 energy_ok rate
- Gen1 nest_food_ok rate
- Gen1 mate_ok rate
- parent-child adult overlap
- final tick

Diagnostic interpretation:

- Good: births stable/moderate, Gen1 exact-ready increases
- Bad: births low and Gen1 cohort small
- False positive: final tick/nest food increases but Gen1 birth stays 0
- False positive: births/matured increases but Gen1 birth stays 0

## 8. Hypothesis Testing Plan

### Test H13 as Necessary Condition

Compare:

- H20a vs H20a+H13
- H20b vs H20b+H13
- H20c vs H20c+H13
- H20d vs H20d+H13
- H20e vs H20e+H13

If H20 variants only produce Gen1 birth when paired with H13, H13 becomes near-necessary for second wave.

### Test H20 Soft Forms

Compare H20a-H20e:

- H20a tests litter burst
- H20b tests mother-level spacing
- H20c tests household bankruptcy
- H20d tests repeat-birth trap
- H20e tests temporal alignment

### Test H21/H22 Only After H20d+H13

Do not judge H21/H22 from small cohorts. Only interpret:

- H20d+H13+H21
- H20d+H13+H22

because these should preserve first-wave cohort better.

## 9. Success Criteria

A condition is promising if:

- Gen1 births > baseline and preferably > H13
- Gen1 exact-ready > H13
- total births not collapsed below 5
- matured children at least comparable to H13
- ready-to-spawn conversion remains 1.0

H20 soft sweep succeeds if at least one H20 variant:

- produces Gen1 births in more seeds than H13, or
- produces higher Gen1 exact-ready without collapsing cohort size

## 10. Failure Criteria

Reject a H20 variant if:

- births collapse to 3 or lower like hard H20
- Gen1 adult females seen drops too low
- final tick improves but Gen1 exact-ready stays 0
- nest food increases but offspring chain does not improve

## 11. Expected Results

Expected ranking before experiment:

1. H20d+H13
2. H20e+H13
3. H20b+H13
4. H1+H11 reference
5. H13 reference
6. H20a+H13
7. H20c+H13

H20c is risky because buffer-only can behave like hard throttle if buffer is too strict.

## 12. Limitations

- Diagnostic monkeypatch only
- 4 seeds exploratory sample
- H20 variants need strength tuning
- H21/H22 still hard to judge if Gen1 cohort remains small

## 13. Summary Before Experiment

The current best scientific statement is:

> Second wave likely requires temporal synchronization, and H13 may be a necessary condition. H20 should not reduce first wave blindly; it should pace births so a two-generation household can exist.

This experiment tests H20 as timing control, not birth suppression.


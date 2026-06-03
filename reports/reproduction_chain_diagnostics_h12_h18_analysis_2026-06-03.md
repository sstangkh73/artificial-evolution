# รายงานวิเคราะห์ผลทดลอง H12-H18: Reproduction Chain และ Second-Wave Bottleneck

วันที่ทดลอง: 2026-06-03  
รายงานก่อนทดลอง: `reports/pre_experiment_plan_h12_h18_2026-06-03.md`  
สคริปต์ทดลอง: `scripts/run_reproduction_chain_diagnostics.py`  
รายงานอัตโนมัติ: `reports/reproduction_chain_diagnostics_h12_h18_2026-06-03.md`  
ผลดิบ: `data/hypothesis_diagnostics/h12_h18_2026-06-03/`

## 1. สรุปสั้นที่สุด

ผล H12-H18 ยืนยันว่า bottleneck หลัง H11 คือ second-wave reproduction จริง.

หลาย condition ทำให้ลูกโตมากขึ้นได้ แต่แทบไม่มี condition ไหนทำให้ gen-1 females มีลูกต่อ. นี่แปลว่าเรายังไม่ได้แก้ "สายพานสืบรุ่น" แค่ทำให้ first-wave offspring โตทันมากขึ้นเท่านั้น.

ผลสำคัญ:

- ทุก condition ยังสูญพันธุ์ 100%
- baseline: births `6.0`, matured `2.0`, gen1 births `0.0`
- H13: births `6.25`, matured `6.0`, gen1 births `0.25`
- H16: births `6.0`, matured `6.0`, gen1 births `0.0`
- H17: births `9.0`, matured `2.75`, gen1 births `0.0`
- H13+H17: births `9.0`, matured `8.25`, gen1 births `0.0`
- H16+H17: births `9.0`, matured `8.75`, gen1 births `0.0`
- H1+H11: births `6.5`, matured `5.75`, gen1 births `0.5`
- H1+H11+H14+H17: births `12.0`, matured `9.75`, gen1 births `0.0`

ข้อสรุปที่สำคัญมาก:

> การเพิ่มจำนวน birth รุ่นแรก หรือทำให้ลูกโตมากขึ้น ไม่เท่ากับการสร้าง second-wave reproduction

## 2. วิธีทดลอง

ใช้ control เดียวกับ H1-H11:

- body: `body_index=14`
- initial population: `250`
- max population: `375`
- max ticks: `800`
- seeds: `7, 8, 11, 13`
- 16 conditions รวม 64 runs

condition ที่รัน:

- baseline
- H11 reference
- H1+H11 reference
- H12-H18
- H12+H13
- H12+H14
- H13+H17
- H14+H15
- H16+H17
- H1+H11+H14+H17

รอบนี้เพิ่มตัวชี้วัดใหม่:

- `gen1_births`
- `second_wave_success_rate`
- `first_gen1_birth_tick`
- `gen1_adult_females_seen`
- `gen1_full_ready_ticks`
- `gen1_opportunity_windows`
- `parent_child_adult_overlap`
- `mother_post_birth_survival`
- `food_liquidity_failure_ticks`
- `mean_local_food_gap_at_nest_food_low`

## 3. ตารางสรุปผลหลัก

| Condition | Births | Matured | Gen1 Births | 2nd Wave | Final Tick | Gen1 Adult F | Gen1 Ready | Gen1 Opp | Parent-Child Overlap | Nest Left |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 6.0 | 2.0 | 0.0 | 0.00 | 132.0 | 1.25 | 0.00 | 0.25 | 2.25 | 85.5 |
| H11 | 6.0 | 5.25 | 0.0 | 0.00 | 115.5 | 2.5 | 0.00 | 0.58 | 8.0 | 99.75 |
| H12 | 6.0 | 2.0 | 0.0 | 0.00 | 132.0 | 1.25 | 0.00 | 0.25 | 2.25 | 85.5 |
| H13 | 6.25 | 6.0 | 0.25 | 0.25 | 128.0 | 2.5 | 0.08 | 0.92 | 6.02 | 97.25 |
| H14 | 6.0 | 2.0 | 0.0 | 0.00 | 129.5 | 1.25 | 0.00 | 0.25 | 2.5 | 75.5 |
| H15 | 6.0 | 2.25 | 0.0 | 0.00 | 123.5 | 0.75 | 0.00 | 0.25 | 0.0 | 115.75 |
| H16 | 6.0 | 6.0 | 0.0 | 0.00 | 195.75 | 2.75 | 0.00 | 0.75 | 5.71 | 219.0 |
| H17 | 9.0 | 2.75 | 0.0 | 0.00 | 157.5 | 1.75 | 0.00 | 0.63 | 2.81 | 118.5 |
| H18 | 6.0 | 2.0 | 0.0 | 0.00 | 124.75 | 1.25 | 0.00 | 0.25 | 0.0 | 77.0 |
| H12+H13 | 6.25 | 6.0 | 0.25 | 0.25 | 123.75 | 2.5 | 0.08 | 0.83 | 6.02 | 94.25 |
| H12+H14 | 6.0 | 2.0 | 0.0 | 0.00 | 129.5 | 1.25 | 0.00 | 0.25 | 2.5 | 75.5 |
| H13+H17 | 9.0 | 8.25 | 0.0 | 0.00 | 150.5 | 4.25 | 0.00 | 0.60 | 1.5 | 152.75 |
| H14+H15 | 6.0 | 2.25 | 0.0 | 0.00 | 123.5 | 0.75 | 0.00 | 0.25 | 0.0 | 115.75 |
| H16+H17 | 9.0 | 8.75 | 0.0 | 0.00 | 176.25 | 4.5 | 0.00 | 1.08 | 5.10 | 176.25 |
| H1+H11 | 6.5 | 5.75 | 0.5 | 0.25 | 195.5 | 2.25 | 0.17 | 0.83 | 2.11 | 316.5 |
| H1+H11+H14+H17 | 12.0 | 9.75 | 0.0 | 0.00 | 104.0 | 4.75 | 0.00 | 0.95 | 2.53 | 63.0 |

## 4. วิเคราะห์แต่ละ Hypothesis

### H12: Second-Wave Support

ตัวแปรต้น: ให้ gen-1 adult females ถอนอาหารจาก household ได้มากขึ้นเมื่อมี mate และใกล้รัง  
ตัวแปรตาม: gen1 births, gen1 full-ready ticks, second-wave success

ผล: เท่ากับ baseline แทบทุกค่า. gen1 births ยัง `0.0`.

ตีความ: H12 แบบนี้เข้าไม่ถึงคอขวดจริง เพราะ gen-1 ไม่ได้ติดแค่ถอนอาหารไม่พอ. gen-1 full-ready ticks ยังเป็น `0.0`, แปลว่ามี gate อื่นขวางก่อนถึงจังหวะที่ support นี้จะช่วยได้

### H13: Parent-Child Time Gap

ตัวแปรต้น: ลด child/juvenile duration และเพิ่ม adult window  
ตัวแปรตาม: parent-child overlap, matured, gen1 births

ผล: H13 เป็นหนึ่งในไม่กี่ condition ที่ทำให้ second wave เกิด:

- matured เพิ่มจาก `2.0` เป็น `6.0`
- gen1 births เพิ่มจาก `0.0` เป็น `0.25`
- second-wave success rate เพิ่มเป็น `0.25`
- seed 7 มี gen1 birth ที่ tick `67`

ตีความ: H13 ได้รับการสนับสนุน. parent-child timing เป็น bottleneck จริง แต่ยังไม่พอ เพราะเกิด second wave ได้แค่ 1 ใน 4 seeds

### H14: Food Liquidity

ตัวแปรต้น: transfer food จาก surplus nests ไป nest ของ reproductive female เมื่อติด nest-food gate  
ตัวแปรตาม: nest_food_low, food liquidity failures, births, gen1 births

ผล:

- births ยัง `6.0`
- matured ยัง `2.0`
- gen1 births ยัง `0.0`
- nest food remaining ลดจาก `85.5` เป็น `75.5`

ตีความ: H14 intervention แบบนี้ไม่ช่วย. แต่นี่ไม่ได้แปลว่า food liquidity ไม่ใช่ปัญหา เพราะ metric ยังเห็น `food_liquidity_failure_ticks` สูงมาก. ความหมายคือ food transfer ตอน can_reproduce อาจมาช้าเกินไป หรือปัญหาเกิดร่วมกับ low_energy/no_mate จนแก้ food อย่างเดียวไม่ได้

### H15: Reproductive Role Protection

ตัวแปรต้น: ให้ likely breeder/mate อยู่ใกล้รังและลด drain บางบทบาท  
ตัวแปรตาม: gen1 readiness, mature, births

ผล:

- matured เพิ่มเล็กน้อย `2.0 -> 2.25`
- gen1 births ยัง `0.0`
- parent-child overlap เป็น `0.0`

ตีความ: role protection แบบนี้ไม่สำเร็จ และอาจทำให้ระบบติดรัง/ลด production. คล้ายสัญญาณจาก H4 เดิมที่ทำให้เจอกันใกล้รังแต่ outcome แย่ลง

### H16: Early Energy Debt Relief

ตัวแปรต้น: ลด energy drain ช่วง early settlement  
ตัวแปรตาม: final tick, matured, gen1 readiness, gen1 births

ผล:

- final tick เพิ่มมาก `132.0 -> 195.75`
- matured เพิ่ม `2.0 -> 6.0`
- gen1 adult females เพิ่มเป็น `2.75`
- gen1 opportunity windows เพิ่มเป็น `0.75`
- gen1 full-ready ticks ยัง `0.0`
- gen1 births ยัง `0.0`

ตีความ: H16 ช่วย survival และ maturation จริง แต่ไม่ใช่ reproduction-chain fix. มันทำให้ระบบอยู่ได้นานขึ้นและลูกโตมากขึ้น แต่ gen-1 ยังไม่พร้อมครบ gate

### H17: Lower Birth Cost

ตัวแปรต้น: ลด mother energy cost และ nest food cost ตอน birth  
ตัวแปรตาม: births, matured, mother survival, gen1 births

ผล:

- births เพิ่ม `6.0 -> 9.0`
- matured เพิ่มเล็กน้อย `2.0 -> 2.75`
- gen1 births ยัง `0.0`

ตีความ: H17 เพิ่ม first-wave births ได้ แต่ยังไม่สร้าง second wave. ถ้าลด cost แล้ว birth เพิ่มแต่ matured/second-wave ไม่ตาม แปลว่าเราอาจกำลังสร้าง first-wave cohort มากขึ้นโดยยังไม่มีระบบเลี้ยงให้เป็น reproductive adults

### H18: Settlement Trap

ตัวแปรต้น: ลดการ default กลับรังเมื่อควรออกหาอาหาร  
ตัวแปรตาม: food, energy, births, matured, gen1 births

ผล:

- final tick ลดเล็กน้อย
- births/matured/gen1 births ไม่ดีขึ้น
- parent-child overlap เป็น `0.0`

ตีความ: H18 แบบนี้ไม่ช่วย. การแก้ settlement trap ต้องละเอียดกว่า "ให้ออกจากรังมากขึ้น" เพราะอาจทำให้ child/parent overlap และ reproduction coordination แย่ลง

## 5. วิเคราะห์ Interaction

### H12+H13

ผลคล้าย H13 เดี่ยว:

- matured `6.0`
- gen1 births `0.25`
- second-wave success `0.25`

ตีความ: signal มาจาก H13 เป็นหลัก. H12 ไม่ได้เพิ่มเหนือ H13

### H12+H14

ผลเท่ากับ H14:

- matured `2.0`
- gen1 births `0.0`

ตีความ: second-wave support + liquidity ยังไม่พอถ้า timing/energy/gate alignment ไม่พร้อม

### H13+H17

ผล:

- births `9.0`
- matured `8.25`
- gen1 births `0.0`

ตีความ: ชุดนี้ทำให้ first-wave offspring โตดีมาก แต่กลับไม่เกิด second wave. นี่เป็น false positive ที่สำคัญ: matured สูง แต่ chain ไม่เกิด

### H14+H15

ผลเท่ากับ H15:

- matured `2.25`
- gen1 births `0.0`

ตีความ: liquidity + role protection แบบนี้ไม่ช่วย และอาจยังติด settlement/production problem

### H16+H17

ผล:

- births `9.0`
- matured `8.75`
- final tick `176.25`
- gen1 births `0.0`
- gen1 opportunity windows `1.075`
- gen1 full-ready ticks `0.0`

ตีความ: นี่เป็นหลักฐานแรงมากว่า gen-1 มี "โอกาสบางส่วน" แต่ไม่เคยพร้อมครบทุก gate. H16+H17 ช่วย survival, birth, maturation แต่ยังไม่สร้าง reproduction chain

### H1+H11+H14+H17

ผล:

- births สูงสุด `12.0`
- matured สูงสุด `9.75`
- final tick ลดเหลือ `104.0`
- gen1 births `0.0`

ตีความ: การเพิ่ม first-wave birth มากเกินไปอาจทำให้ household/lifespan economics พังเร็วขึ้น. ระบบได้ลูกจำนวนมากขึ้น แต่ไม่เหลือเวลาหรือทรัพยากรคุณภาพพอให้ลูกเหล่านั้นสืบรุ่นต่อ

## 6. ข้อค้นพบหลัก

### 6.1 Second-wave bottleneck ได้รับการยืนยัน

baseline ไม่มี gen1 birth. H13 และ H1+H11 ทำให้เกิด gen1 birth ได้เฉพาะบาง seed:

- H13 seed 7: gen1 birth `1`, first gen1 birth tick `67`
- H12+H13 seed 7: gen1 birth `1`, first gen1 birth tick `68`
- H1+H11 seed 7: gen1 births `2`, first gen1 birth tick `100`

นอกนั้น gen1 births เป็น `0`.

### 6.2 Gen-1 opportunity ไม่เท่ากับ gen-1 readiness

บาง condition มี gen1 opportunity windows แต่ full-ready ticks ยังเป็นศูนย์:

- H16+H17: gen1 opportunity `1.075`, full-ready `0.0`
- H1+H11+H14+H17: gen1 opportunity `0.95`, full-ready `0.0`
- H13+H17: gen1 opportunity `0.60`, full-ready `0.0`

แปลว่า gen-1 เข้าสู่ช่วงที่ดูเหมือน "มีโอกาส" แต่ยังขาด gate สำคัญ เช่น energy, nest food, mate, cooldown, durability หรือ near-nest alignment

### 6.3 Birth count เป็น metric หลอกได้

H17 และ H1+H11+H14+H17 เพิ่ม birth ได้มาก:

- H17: births `9.0`
- H1+H11+H14+H17: births `12.0`

แต่ gen1 births ยัง `0.0`. ดังนั้น birth count สูงไม่ได้แปลว่า population sustain ได้

### 6.4 Matured count ก็เป็น metric หลอกได้

H16+H17 มี matured `8.75`, H13+H17 มี matured `8.25`, H1+H11+H14+H17 มี matured `9.75`. แต่ไม่มี second wave.

ต้องใช้ `gen1_births` และ `matured generation-2` เป็นตัวชี้วัดหลักแทนการดู matured รวมอย่างเดียว

### 6.5 Energy debt เป็น final failure mode แต่ไม่ใช่คำตอบเดียว

H16 ทำให้ final tick และ matured ดีขึ้นมาก แต่ gen1 birth ไม่เกิด. ระบบยังตายด้วย `energy_depleted` เกือบทั้งหมด

ตีความ: energy เป็นทางที่ระบบล้มในท้ายสุด แต่ reproduction chain ยังขาด gate alignment

### 6.6 Food liquidity ยังน่าสงสัย แต่ H14 แบบนี้ไม่พอ

food liquidity failure ticks สูงมาก เช่น:

- baseline `402.25`
- H11 `808.0`
- H16 `2082.5`
- H16+H17 `2907.25`

ตัวเลขสูงขึ้นบาง condition เพราะ simulation อยู่ได้นานขึ้นและเจอ block บ่อยขึ้น. H14 intervention ไม่ช่วย แปลว่า food transfer ตอนท้าย gate อาจช้าเกินไป หรือ nest_food_low มักเกิดพร้อม low_energy/no_mate

## 7. สถานะของ H12-H18 หลังทดลอง

| H | สถานะ | เหตุผล |
|---|---|---|
| H12 | ไม่สนับสนุนในรูปแบบนี้ | gen-1 priority withdrawal ไม่เปลี่ยน outcome |
| H13 | สนับสนุนบางส่วน | สร้าง gen1 birth ได้บาง seed และเพิ่ม matured |
| H14 | ยังไม่สรุป | liquidity metric สูง แต่ intervention ไม่ช่วย |
| H15 | ไม่สนับสนุนในรูปแบบนี้ | role protection ไม่เพิ่ม chain และอาจลด overlap |
| H16 | สนับสนุนเป็น survival/maturation helper | เพิ่ม final tick/matured แต่ไม่เพิ่ม gen1 birth |
| H17 | สนับสนุนว่า birth cost จำกัด first-wave birth | เพิ่ม births แต่ไม่แก้ second wave |
| H18 | ไม่สนับสนุนในรูปแบบนี้ | settlement commute ไม่ช่วย outcome |

## 8. สมมุติฐานใหม่ที่ควรเพิ่ม

### H19: Gen-1 Full-Ready Gate Alignment Bottleneck

สมมุติฐาน:

> Gen-1 females มี opportunity windows แต่ gate ไม่พร้อมครบใน tick เดียวกัน ทำให้ full-ready ticks เป็นศูนย์

ตัวแปรที่ต้องวัด:

- gen1 energy_ok ticks
- gen1 mate_ok ticks
- gen1 near_nest ticks
- gen1 nest_food_ok ticks
- gen1 cooldown_ok ticks
- overlap ระหว่าง gate เหล่านี้

เป้าหมายคือไม่ใช่เพิ่ม gate ใด gate หนึ่ง แต่ทำให้ gate เหล่านี้พร้อมพร้อมกัน

### H20: First-Wave Overproduction Trap

สมมุติฐาน:

> การเพิ่ม births รุ่นแรกเร็วเกินไปทำให้ household ใช้ energy/food/time หมดก่อน gen-1 reproduction

หลักฐาน:

- H1+H11+H14+H17 births `12.0`, matured `9.75`, final tick `104.0`, gen1 births `0.0`

ควรทดลอง:

- จำกัด first-wave litter/cooldown
- birth spacing
- one-child-until-gen1-ready policy
- household buffer ก่อน birth เพิ่ม

### H21: Gen-1 Nest Inheritance/Ownership Bottleneck

สมมุติฐาน:

> Gen-1 adults โตแล้ว แต่ไม่ inherit หรือเข้าถึง nest/household food/mate network ได้ถูกต้อง

เหตุผล:

- gen1 opportunity windows มี แต่ full-ready ticks ไม่มี
- H14 food transfer ไม่ช่วย อาจเพราะ owner/home identity ไม่ตรง gate ของ gen-1

ตัวแปรที่ต้องวัด:

- gen1 owner_id
- gen1 nest_position
- parent nest still active?
- gen1 near inherited nest?
- food available to inherited nest

## 9. คำแนะนำรอบถัดไป

1. อย่าเพิ่ม mutation ตอนนี้

ยังไม่มี reproduction chain ให้ mutation แสดงผลอย่างมีความหมาย

2. ให้เพิ่ม gen1 gate instrumentation ถาวร

ต้องรู้ว่า gen1 female ติด gate ไหนแบบแยกราย tick:

- energy
- mate
- near nest
- nest food
- cooldown
- durability

3. ทดลอง H19 ก่อน patch ใหม่ใหญ่

Instrumentation-only ก่อน: baseline, H13, H16+H17, H1+H11, H1+H11+H14+H17

4. ระวัง H17

H17 เพิ่ม birth ได้จริง แต่ถ้าไม่มี birth spacing หรือ household buffer อาจกลายเป็น first-wave overproduction trap

5. H13 ยังควรเก็บไว้

H13 เป็นหนึ่งในไม่กี่ทางที่ทำให้ second wave เกิด แม้จะยังอ่อนมาก

## 10. สรุปสุดท้าย

H12-H18 ยืนยันว่าปัญหาตอนนี้คือ second-wave reproduction chain.

เราแก้ให้เกิดได้มากขึ้นแล้ว เราแก้ให้โตได้มากขึ้นแล้ว แต่เรายังแก้ให้ "รุ่นที่โตแล้วมีลูกต่อ" ไม่ได้.

เส้นทางที่น่าจะถูกที่สุดตอนนี้คือ:

1. ใช้ H13/H1+H11 เป็นฐาน เพราะมี signal second-wave จริง
2. เพิ่ม H19 instrumentation เพื่อหา gate ที่ gen-1 ไม่เคย full-ready
3. ทดลอง birth spacing/first-wave throttling แทนการเพิ่ม birth ตรงๆ
4. ตรวจ nest inheritance/household identity ของ gen-1

คำวินิจฉัย ณ ตอนนี้:

> ระบบไม่ได้ขาดแค่ทรัพยากรหรือ lifespan แต่ขาดการซิงก์ gate ของ gen-1 reproduction ใน tick เดียวกัน


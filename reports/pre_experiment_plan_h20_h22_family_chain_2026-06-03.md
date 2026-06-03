# รายงานก่อนทดลอง H20-H22: First-Wave Throttling และ Two-Generation Household

วันที่จัดทำ: 2026-06-03  
สถานะ: รายงานก่อนทดลอง  
ฐานอ้างอิง: H12-H19 diagnostic results

## Abstract

ผล H19 ชี้ว่าเมื่อ female พร้อมจริง ระบบ spawn child ทันที ไม่มีหลักฐานว่า AI decision policy ปฏิเสธ reproduction. ปัญหาหลักจึงขยับไปอยู่ก่อน decision point: Gen1 females แทบไม่เคย exact full-ready.

ลำดับความสำคัญรอบนี้:

1. H20 First-wave Throttling
2. H13 Parent-child Overlap
3. H21 Nest Inheritance
4. H22 Mate Synchronization

คำถามหลัก:

> ถ้าระบบไม่รีบผลิต first-wave มากเกินไป และทำให้ Gen1 เข้าสู่ household เดิมได้จริง Gen1 จะมี exact-ready ticks และ births เพิ่มขึ้นหรือไม่

## 1. Problem

ข้อมูลก่อนหน้า:

- H17 เพิ่ม births เป็น `9.0` แต่ Gen1 births ยัง `0.0`
- H1+H11+H14+H17 เพิ่ม births เป็น `12.0` และ matured เป็น `9.75` แต่ Gen1 births ยัง `0.0`
- H16+H17 ทำให้ matured สูง `8.75` แต่ Gen1 exact-ready ยัง `0.0`
- H13 และ H1+H11 เป็นเงื่อนไขไม่กี่ชุดที่ทำให้ Gen1 birth เกิดจริงบาง seed

นี่ชี้ว่า first-wave births อาจไม่ใช่สิ่งที่ควรเพิ่มตรงๆ. ถ้า first-wave มากเกินไป มันอาจดึง energy/food/time จาก household จน Gen1 ไม่มีทางพร้อม reproduce.

## 2. Research Question

คำถามหลัก:

> การ throttle first-wave birth ทำให้ household เปลี่ยนจาก 1-generation household เป็น 2-generation household ได้ไหม

คำถามย่อย:

1. H20 เพิ่ม Gen1 exact-ready ticks หรือไม่
2. H20 เพิ่ม Gen1 births หรือไม่
3. H20 ลด first-wave overproduction trap หรือไม่
4. H13 ช่วย H20 ผ่าน parent-child overlap หรือไม่
5. H21 ช่วยให้ Gen1 inherit nest/food identity ถูกต้องหรือไม่
6. H22 ช่วยให้ Gen1 male/female sync กันหรือไม่

## 3. Hypotheses

### H20: First-Wave Throttling

สมมุติฐาน:

> การเกิด first-wave เร็วหรือมากเกินไปทำให้ household พัง ก่อน Gen1 จะพร้อม reproduce

ตัวแปรต้น:

- เพิ่ม household buffer requirement ก่อน birth
- จำกัด founder/Gen0 ให้มีลูกได้ไม่ถี่
- ลดโอกาส litter > 1
- ลด birth ถ้า household ยังไม่มี food/energy buffer

ตัวแปรตาม:

- Gen1 exact-ready ticks
- Gen1 births
- Gen1 energy_ok rate
- Gen1 nest_food_ok rate
- parent-child overlap
- total births และ matured children

Success criteria:

- Gen1 exact-ready เพิ่ม
- Gen1 births เพิ่ม
- ไม่ใช่แค่ final tick หรือ nest food เพิ่ม

Failure criteria:

- births ลดจนไม่มี Gen1 adult พอ
- stored/nest food เพิ่ม แต่ Gen1 readiness ไม่เพิ่ม

### H13: Parent-Child Overlap

สมมุติฐาน:

> ระบบต้องมีช่วงที่แม่/พ่อกับลูก adult อยู่ร่วมกันพอ เพื่อเกิด household สองรุ่น

ตัวแปรต้น:

- ลด child/juvenile duration
- เพิ่มช่วง adult window

ตัวแปรตาม:

- parent-child adult overlap
- Gen1 exact-ready ticks
- Gen1 births
- Gen2 births/matured

Success criteria:

- overlap เพิ่มพร้อม Gen1 exact-ready/birth เพิ่ม

### H21: Nest Inheritance

สมมุติฐาน:

> Gen1 โตแล้วไม่ inherit household/nest/food access ถูกต้อง ทำให้ local abundance ไม่ตรงกับ global abundance

ตัวแปรต้น:

- บังคับให้ child/juvenile/adult Gen1 ใช้ parent nest/shared home owner อย่างต่อเนื่อง
- sync nest_position กับ parent nest เมื่อ parent nest ยังมีอยู่
- ให้ Gen1 ถอนอาหารจาก inherited nest ได้แบบจำกัด

ตัวแปรตาม:

- Gen1 near_nest rate
- Gen1 nest_food_ok rate
- Gen1 owner/nest missing count
- Gen1 exact-ready ticks
- Gen1 births

Success criteria:

- Gen1 nest_food_ok เพิ่ม
- Gen1 exact-ready/birth เพิ่ม

### H22: Mate Synchronization

สมมุติฐาน:

> Gen1 males/females โตไม่พร้อมกัน อยู่คนละ household หรือหาไม่เจอ ทำให้ mate_ok ต่ำ

ตัวแปรต้น:

- rendezvous เฉพาะ Gen1 adults ที่มี inherited nest
- ให้ Gen1 adults กลับ parent/shared nest เมื่อ energy พอ
- ลดการกระจายตัวของ Gen1 mates

ตัวแปรตาม:

- Gen1 mate_ok rate
- Gen1 adult male/female overlap
- Gen1 exact-ready ticks
- Gen1 births

Success criteria:

- mate_ok เพิ่มโดยไม่ทำ energy_ok/nest_food_ok พัง

## 4. Conditions

ควรรัน 12 conditions:

| Condition | เหตุผล |
|---|---|
| baseline | control |
| H13 | overlap reference |
| H1+H11 | prior best second-wave signal |
| H17 | high first-wave birth warning |
| H20 | throttle เดี่ยว |
| H20+H13 | throttle + overlap |
| H20+H21 | throttle + inheritance |
| H20+H22 | throttle + mate sync |
| H20+H13+H21 | candidate core fix |
| H20+H13+H22 | overlap + mate sync |
| H20+H21+H22 | inheritance + mate sync |
| H20+H13+H21+H22 | full family-chain stack |

## 5. Control Variables

- body_index: `14`
- initial_population: `250`
- max_population: `375`
- max_ticks: `800`
- seeds: `7, 8, 11, 13`
- same environment/spawn setup as H19

## 6. Metrics

Primary metrics:

- `gen1_births`
- `gen1_exact_ready_ticks`
- `gen1_spawn_events`
- `second_wave_success_rate`
- `max_generation_observed`

Secondary metrics:

- `gen1_energy_ok_rate`
- `gen1_nest_food_ok_rate`
- `gen1_mate_ok_rate`
- `gen1_near_nest_rate`
- `parent_child_adult_overlap`
- `total_births`
- `matured_children`
- `nest_food_remaining`

Interpretation rules:

- ถ้า births ลดแต่ Gen1 births เพิ่ม ถือว่าดี
- ถ้า births/matured เพิ่มแต่ Gen1 births ไม่เพิ่ม ถือว่า false positive
- ถ้า food เพิ่มแต่ Gen1 readiness ไม่เพิ่ม ถือว่า wealth without offspring
- ถ้า H20+H13 ดีที่สุด แปลว่าปัญหาคือ timing + first-wave pressure
- ถ้า H20+H21 ดีที่สุด แปลว่าปัญหาคือ household inheritance
- ถ้า H20+H22 ดีที่สุด แปลว่าปัญหาคือ mate synchronization

## 7. Expected Outcomes

คาดการณ์ก่อนทดลอง:

- H20 เดี่ยวอาจลด births แต่ควรเพิ่ม Gen1 energy_ok ถ้าหลักการถูก
- H20+H13 น่าจะเป็นชุดที่ดีที่สุดในเชิง second-wave เพราะ H13 มี signal เดิม
- H21 อาจช่วย nest_food_ok มากกว่า mate_ok
- H22 อาจช่วย mate_ok แต่เสี่ยงลด energy_ok ถ้าบังคับกลับ nest มากเกินไป
- full stack อาจไม่ดีที่สุด เพราะ interventions อาจชนกัน

## 8. Falsification

H20 จะถูกหักล้างถ้า:

- first-wave births ลดลง แต่ Gen1 exact-ready/birth ไม่เพิ่มเลย
- Gen1 energy_ok ไม่ดีขึ้น
- ระบบแค่ตายนานขึ้นหรือมีอาหารเหลือมากขึ้น

H13 จะถูกลดน้ำหนักถ้า:

- overlap เพิ่ม แต่ Gen1 exact-ready ไม่เพิ่ม

H21 จะถูกสนับสนุนถ้า:

- nest_food_ok เพิ่มพร้อม Gen1 exact-ready/birth เพิ่ม

H22 จะถูกสนับสนุนถ้า:

- mate_ok เพิ่มพร้อม Gen1 exact-ready/birth เพิ่ม

## 9. Limitations

- เป็น diagnostic intervention ผ่าน monkeypatch ไม่ใช่ patch ถาวร
- 4 seeds ต่อ condition ยังเป็น exploratory sample
- ถ้า H20 ลด births มากเกินไป อาจต้อง sweep throttle strength เพิ่ม
- ถ้าไม่มี Gen1 adult พอ จะยังแยก H21/H22 ยาก

## 10. Summary Before Experiment

ลำดับนี้มีเหตุผลแข็งแรง:

1. H20 กัน first-wave ไม่ให้กินอนาคต
2. H13 ทำให้สองรุ่นทับซ้อนจริง
3. H21 ให้ Gen1 เข้าถึง household economy
4. H22 ทำให้ Gen1 เจอ mate ในจังหวะที่ยังมี energy/food

เป้าหมายไม่ใช่เพิ่ม birth รวม แต่คือเพิ่ม `Gen1 exact-ready -> Gen1 spawn`.


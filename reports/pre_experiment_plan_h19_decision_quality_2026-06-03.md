# รายงานก่อนทดลอง H19: Reproduction Decision Quality / Gate-to-Action Integrity

วันที่จัดทำ: 2026-06-03  
สถานะ: รายงานก่อนทดลอง  
ฐานอ้างอิง: ผล H1-H18 และข้อสังเกตเรื่อง Gen1 ไม่มีลูก

## 1. ปัญหาที่ต้องพิสูจน์

ผล H12-H18 ทำให้คำถามหลักเปลี่ยนจาก:

> เกิดลูกได้ไหม

เป็น:

> Gen1 โตแล้วทำไมไม่มีลูก

มีข้อมูลหลายจุดที่บอกว่า first-wave births และ matured children เพิ่มได้ แต่ second-wave reproduction ยังไม่เกิด. โดยเฉพาะ:

- H17 เพิ่ม births เป็น `9.0` แต่ gen1 births ยัง `0.0`
- H16+H17 เพิ่ม matured children เป็น `8.75` แต่ gen1 births ยัง `0.0`
- H1+H11+H14+H17 เพิ่ม births เป็น `12.0` และ matured เป็น `9.75` แต่ gen1 births ยัง `0.0`
- H1+H11 และ H13 เป็นไม่กี่ condition ที่มี gen1 birth บาง seed

สิ่งที่ยังไม่รู้คือ gen1 female ไม่ reproduce เพราะ:

1. ไม่เคยพร้อมครบทุก gate จริง
2. พร้อมครบแล้ว แต่ action handoff จาก decision ไป birth หลุด
3. พร้อมครบแล้ว แต่ policy/decision ไม่เลือก reproduce
4. measurement เดิมคลาดเคลื่อน เพราะ `full_ready_ticks` อาจอ่าน debug จาก tick ก่อนหน้า

H19 จะทดสอบจุดนี้โดย trace ราย tick ตั้งแต่ gate readiness ไปจนถึง spawn child.

## 2. สมมุติฐาน H19

ชื่อ:

> H19: Reproduction Decision Quality / Gate-to-Action Integrity

สมมุติฐานหลัก:

> มี female บางตัว โดยเฉพาะ gen1 females ที่เข้าสู่สถานะพร้อม reproduction แล้ว แต่ birth ไม่เกิด เพราะ decision policy, action handoff, timing instability, หรือ measurement lag

สมมุติฐานย่อย:

- H19a: `full_ready=True` แต่ `wants_reproduction=False`
- H19b: `wants_reproduction=True` แต่ runner ไม่ spawn child
- H19c: previous metric `full_ready_ticks` นับ tick เก่าหรือ tick lag ไม่ใช่ readiness ณ action tick
- H19d: gen1 females มี opportunity windows แต่ gate ไม่ sync พร้อมกันใน tick เดียว จึง `exact_full_ready_ticks=0`

## 3. ตัวแปรต้น

ตัวแปรต้นคือ condition ที่ใช้ trace ไม่ใช่การแก้ policy ใหม่:

| Condition | เหตุผล |
|---|---|
| baseline | control ของ current branch |
| H11 | reference จาก lifetime opportunity |
| H13 | parent-child overlap มี second-wave signal |
| H16 | energy debt relief เพิ่ม survival/matured แต่ไม่เพิ่ม gen1 birth |
| H17 | lower birth cost เพิ่ม first-wave births |
| H13+H17 | matured สูง แต่ gen1 birth ยัง 0 |
| H16+H17 | matured สูงและ gen1 opportunity สูง แต่ gen1 full-ready 0 |
| H1+H11 | best prior condition ที่มี gen1 birth บาง seed |
| H1+H11+H14+H17 | births/matured สูงสุด แต่ gen1 birth 0 |

ยังไม่เปลี่ยน mutation และยังไม่แก้ core decision policy.

## 4. ตัวแปรตาม

ตัวแปรตามหลัก:

- `exact_ready_ticks`: จำนวน tick ที่ `agent.tick()` คืนค่า eligible พร้อม reproduction จริง ณ tick นั้น
- `wants_reproduction_ticks`: จำนวน tick ที่ tick return เป็น `True`
- `spawn_events`: จำนวนครั้งที่ runner spawn child หลัง wants reproduction
- `ready_no_want_ticks`: ready แต่ tick ไม่ return reproduction
- `want_no_spawn_ticks`: wants reproduction แต่ child ไม่ spawn
- `ready_to_spawn_conversion`: spawn events / exact ready ticks
- `gen1_exact_ready_ticks`
- `gen1_want_no_spawn_ticks`
- `gen1_ready_no_want_ticks`
- `gen1_births`
- `gen1_gate_ok_rates`: energy, mate, near nest, nest food, cooldown, durability
- `gen1_top_block_reasons`

ตัวแปรตามรอง:

- `first_gen1_ready_tick`
- `first_gen1_spawn_tick`
- `female_decision_rows`: ราย female ว่า ready กี่ tick และ birth กี่ครั้ง
- `decision_trace.csv`: trace ราย event ที่ ready/want/spawn หรือ gen1 adult female block

## 5. Control Variables

- body_index: `14`
- initial_population: `250`
- max_population: `375`
- max_ticks: `800`
- seeds: `7, 8, 11, 13`
- same environment, same body plan, same initial spawn strategy as H12-H18

## 6. เกณฑ์สนับสนุน / หักล้าง

### สนับสนุน H19a/H19b: decision/action bug

ถ้าพบ:

- `exact_ready_ticks > 0`
- แต่ `spawn_events = 0`
- และ `ready_no_want_ticks > 0` หรือ `want_no_spawn_ticks > 0`

โดยเฉพาะใน gen1 females

แปลว่ามีปัญหา decision policy หรือ action handoff.

### สนับสนุน H19c: measurement lag

ถ้าพบ:

- previous `full_ready_ticks` จากรายงานเก่า > 0
- แต่ `exact_ready_ticks` จาก H19 ต่ำกว่ามาก หรือเป็น 0

แปลว่า metric เดิมอาจอ่าน `reproduction_debug` จาก tick ก่อนหน้าและทำให้ตีความ readiness สูงเกินจริง.

### สนับสนุน H19d: gate alignment bottleneck

ถ้าพบ:

- gen1 opportunity windows > 0
- gate บางตัว ok บ่อย
- แต่ exact full-ready ticks = 0
- ไม่มี ready_no_want หรือ want_no_spawn

แปลว่า gen1 ไม่ได้ติด policy แต่ติด gate synchronization: energy, mate, nest, food, cooldown ไม่พร้อมพร้อมกันใน tick เดียว.

## 7. Success Criteria

การทดลองสำเร็จถ้าตอบได้อย่างน้อยหนึ่งข้อ:

- มีหรือไม่มี exact ready to spawn mismatch
- gen1 ไม่มีลูกเพราะไม่เคย exact ready หรือเพราะ ready แล้ว action หลุด
- gate ใดเป็นตัวที่ทำให้ gen1 ไม่ full-ready
- metric `full_ready_ticks` เดิมเชื่อถือได้แค่ไหน

## 8. Failure Criteria

การทดลองยังไม่พอถ้า:

- trace ไม่มี gen1 adult female พอให้วิเคราะห์
- exact ready event น้อยเกินไปในทุก condition
- ข้อมูล decision trace ไม่บอก gate state ครบ
- ไม่สามารถแยก measurement lag จาก policy bug ได้

## 9. สิ่งที่คาดว่าจะเห็น

คาดการณ์ก่อนทดลอง:

- ส่วนใหญ่จะไม่พบ `want_no_spawn` เพราะ runner น่าจะ spawn ทันทีเมื่อ `wants_reproduction=True`
- ถ้าพบ mismatch จะเป็น bug สำคัญมาก
- มีโอกาสสูงกว่า H19 จะสรุปว่า gen1 females ไม่เคย exact full-ready มากพอ ไม่ใช่พร้อมแล้วไม่ยอมมีลูก
- H1+H11 seed 7 น่าจะเป็น positive control เพราะมี gen1 birth จริง
- H16+H17 และ H1+H11+H14+H17 จะเป็น negative control ที่ดี เพราะมี gen1 adult/opportunity แต่ไม่มี gen1 birth

## 10. ข้อจำกัด

- เป็น diagnostic instrumentation ไม่ใช่ patch ถาวร
- ใช้ sample 4 seeds เพื่อเทียบกับ H1-H18 เดิม
- ถ้า trace ชี้ว่าเป็น gate alignment ต้องทำ H20/H21 ต่อเพื่อเจาะ first-wave overproduction และ gen1 nest inheritance

## 11. สรุปก่อนเริ่มทดลอง

H19 คือการตรวจความซื่อสัตย์ของ chain:

> Gate ready -> decision true -> runner spawn -> child exists

ถ้า chain นี้ไม่ขาด แปลว่า Gen1 ไม่มีลูกเพราะไม่เคยพร้อมจริง. ถ้า chain นี้ขาด แปลว่าเราพบ decision/action bug ที่ต้องแก้ก่อนทดลอง hypothesis อื่นต่อ.


# รายงานก่อนทดลอง H12-H18: Second Wave, Parent-Child Overlap, Food Liquidity

วันที่จัดทำ: 2026-06-03  
สถานะ: รายงานก่อนทดลอง  
ฐานข้อมูลอ้างอิง: ผล H1-H11 จาก `reports/hypothesis_diagnostics_h1_h11_analysis_2026-06-03.md`

## 1. เหตุผลที่ต้องมี H12-H18

ผล H1-H11 ชี้ว่า H11 ถูกทาง แต่ยังไม่พอ. H11 เพิ่มจำนวนลูกที่โตทันจาก baseline `2.0` เป็น `5.25` และ `H1 + H11` เพิ่มเป็น `5.75` แต่ทุก condition ยังสูญพันธุ์ 100%.

ปัญหาที่เหลือไม่ใช่แค่ "มีลูกได้ไหม" แต่คือระบบไม่สามารถสร้างสายพาน reproduction ต่อรุ่นได้. birth ส่วนใหญ่เกิดเป็น first wave จาก founder แล้วหยุด ระบบยังไม่สร้าง second wave ที่ gen-1 โตแล้วมีลูกต่อได้จริง.

ดังนั้น H12-H18 จะย้ายคำถามจาก food/mutation/general survival ไปที่:

- รุ่นลูกโตแล้วมีลูกต่อได้ไหม
- พ่อแม่อยู่ทับซ้อนกับลูกตอนลูกโตพอไหม
- อาหารที่มีอยู่เป็นอาหารที่ reproductive female ใช้ได้จริงหรือไม่
- บทบาทแม่/พ่อ/ผู้ช่วยทำให้ reproduction window มีคุณภาพพอหรือไม่
- ค่าใช้จ่ายของ birth ทำให้ household พังเร็วเกินไปหรือไม่
- settlement behavior กำลังช่วยหรือดักระบบไว้กันแน่

## 2. คำถามวิจัยหลัก

คำถามหลัก:

> อะไรขวางไม่ให้ระบบเปลี่ยน first-wave birth เป็น second-wave reproduction chain?

คำถามย่อย:

1. Gen-1 adult females มี full-ready reproduction tick หรือไม่
2. พ่อแม่ตายก่อนลูกโตหรือไม่
3. ตอนที่ตัวเมียติด `nest_food_low` มีอาหารรวมในระบบ/รังอื่นเหลืออยู่หรือไม่
4. การปกป้อง reproductive role ช่วยเพิ่ม birth จริง หรือแค่เพิ่ม survival
5. birth cost สูงเกิน lifespan economics หรือไม่
6. settlement/rendezvous behavior กำลังทำให้ production ลดลงหรือไม่

## 3. Control และ baseline

ใช้ baseline เดียวกับ H1-H11 เพื่อเทียบผลตรง:

- body: `body_index=14`
- profile: `nurturing_settler`
- initial population: `250`
- max population: `375`
- max ticks: `800`
- seeds: `7, 8, 11, 13`

ควรมี condition อ้างอิง:

- `baseline`: current branch
- `h11_extend_reproductive_life`: H11 เดี่ยว
- `i_h1_h11`: best condition จาก H1-H11

เหตุผล: H12-H18 ต้องตอบว่าแก้เหนือ H11/H1+H11 ได้หรือไม่ ไม่ใช่แค่ดีกว่า baseline ที่อ่อนมาก

## 4. ตัวชี้วัดกลางที่ต้องเพิ่ม

ตัวชี้วัดจาก H1-H11 ยังดี แต่ยังไม่พอสำหรับคำถาม second-wave. ต้องเพิ่ม metric ต่อไปนี้:

| Metric | ความหมาย |
|---|---|
| `births_by_generation` | จำนวน birth ที่แม่แต่ละ generation สร้าง |
| `matured_by_generation` | จำนวนลูกที่โตถึง adult แยกตาม generation |
| `first_gen1_birth_tick` | tick แรกที่ gen-1 female มีลูก |
| `gen1_adult_female_count` | จำนวน gen-1 female ที่โตเป็น adult |
| `gen1_full_ready_ticks` | tick ที่ gen-1 female พร้อม reproduction ครบทุก gate |
| `gen1_births_per_adult_female` | gen-1 female เปลี่ยนเป็น birth ได้แค่ไหน |
| `parent_child_adult_overlap_ticks` | จำนวน tick ที่แม่ยังอยู่ตอนลูกเป็น adult |
| `mother_post_birth_survival_ticks` | แม่อยู่รอดหลังคลอดนานแค่ไหน |
| `food_liquidity_failure_ticks` | tick ที่ติด `nest_food_low` ทั้งที่มี food รวมเหลือ |
| `local_food_gap_at_repro_block` | nest food ที่ female ใช้ได้ ลบด้วย food รวม/active nest food |
| `full_ready_to_birth_conversion` | full-ready tick เปลี่ยนเป็น birth ได้จริงกี่ครั้ง |
| `second_wave_success` | มี gen-1 birth อย่างน้อย 1 หรือไม่ |

## 5. H12-H18

### H12: Second-Wave Reproduction Bottleneck

สมมุติฐาน:

> ระบบไม่ได้หยุดเพราะ founder ไม่มีลูก แต่หยุดเพราะ gen-1 ที่โตแล้วไม่สามารถมีลูกต่อได้

ตัวแปรต้น:

- ปรับ support/energy/food เฉพาะ gen-1 adult females แบบ diagnostic
- หรือเพิ่ม instrumentation โดยไม่แก้พฤติกรรม เพื่อดูว่า gen-1 ติด gate ใด

ตัวแปรตาม:

- `first_gen1_birth_tick`
- `gen1_full_ready_ticks`
- `gen1_births_per_adult_female`
- `births_by_generation`
- `max_generation_observed`

คำทำนาย:

- baseline และ H11 จะมี gen-1 adult females บางส่วน แต่ gen-1 births ต่ำมากหรือเป็นศูนย์
- ถ้า H12 intervention ถูกทาง `births_by_generation[1]` ต้องเพิ่ม และ `max_generation_observed` ต้องเกิน 2 บ่อยขึ้น

เกณฑ์สนับสนุน:

- gen-1 births เพิ่มอย่างน้อย `+1.0` เฉลี่ยต่อ seed เทียบ H1+H11
- first gen-1 birth เกิดก่อน extinction อย่างสม่ำเสมอ

### H13: Parent-Child Time Gap

สมมุติฐาน:

> พ่อแม่ตายก่อนลูกโตพอจะช่วย household หรือสืบพันธุ์ต่อ ทำให้รุ่นต่อรุ่นขาดสะพาน

ตัวแปรต้น:

- ลด child/juvenile duration
- เพิ่ม parent survival buffer หลังคลอด
- ลด parent post-birth energy shock

ตัวแปรตาม:

- `parent_child_adult_overlap_ticks`
- `mother_post_birth_survival_ticks`
- `matured_children`
- `gen1_births`
- `second_wave_success`

คำทำนาย:

- ถ้า overlap ต่ำมาก ลูกโตหลัง household collapse
- การเพิ่ม overlap ควรเพิ่ม gen-1 full-ready ticks และ gen-1 birth

เกณฑ์สนับสนุน:

- parent-child adult overlap เพิ่มพร้อมกับ gen-1 births เพิ่ม
- ถ้า overlap เพิ่มแต่ birth ไม่เพิ่ม แปลว่าต้องไปดู food liquidity หรือ role protection

### H14: Food Liquidity Bottleneck

สมมุติฐาน:

> อาหารมีอยู่ในระบบ แต่ไม่อยู่ในรัง/owner/time ที่ reproductive female ใช้ได้จริง

ตัวแปรต้น:

- allow emergency food transfer ระหว่าง household ที่เกี่ยวข้อง
- ให้ reproductive female เห็น/ใช้ active nest food pool เฉพาะ diagnostic
- แยกวัด local nest food กับ global active nest food ตอนติด blocker

ตัวแปรตาม:

- `nest_food_low` blockers
- `food_liquidity_failure_ticks`
- `local_food_gap_at_repro_block`
- `births`
- `matured_children`
- `gen1_births`

คำทำนาย:

- จะพบ tick จำนวนมากที่ `nest_food_low` ทั้งที่ active/abandoned food ยังเหลือ
- ถ้า emergency liquidity ช่วยจริง `nest_food_low` ต้องลด และ births/gen1 births ต้องเพิ่ม

เกณฑ์สนับสนุน:

- ลด `nest_food_low` อย่างน้อย 20%
- เพิ่ม births หรือ gen-1 births ไม่ใช่แค่เพิ่ม food remaining

### H15: Reproductive Role Protection

สมมุติฐาน:

> ตัวเมียที่ควรสืบพันธุ์ต้องหาอาหาร/เดิน/ดูแลลูกมากเกินไป ทำให้ full-ready window มีน้อยและสั้น

ตัวแปรต้น:

- mother/candidate breeder role priority
- ให้ mate หรือ helper อยู่ใกล้รังและช่วยถอน/หาอาหาร
- ลด movement pressure ของ reproductive female ช่วงพร้อมมีลูก

ตัวแปรตาม:

- `full_ready_ticks`
- `opportunity_windows`
- `births_per_adult_female`
- `mother_post_birth_survival_ticks`
- `child_survival_to_adult`

คำทำนาย:

- full-ready ticks จะเพิ่มมากกว่า opportunity windows
- ถ้า role protection ดีจริง birth และ matured children ต้องเพิ่ม ไม่ใช่แค่ survival

เกณฑ์สนับสนุน:

- `full_ready_ticks` เพิ่มอย่างมีนัยทิศทาง
- `births_per_adult_female` หรือ gen-1 births เพิ่ม

### H16: Early Energy Debt Spiral

สมมุติฐาน:

> ระบบมี energy debt ตั้งแต่ต้นจนทุก bottleneck แสดงเป็น `energy_depleted` ในท้ายสุด

ตัวแปรต้น:

- ลด base/movement/brain energy drain ช่วง early settlement
- เพิ่ม initial energy buffer แบบ diagnostic
- เพิ่ม food conversion efficiency เฉพาะช่วงก่อน first child matures

ตัวแปรตาม:

- `death_tick_distribution`
- `energy_at_first_birth`
- `energy_after_birth`
- `mother_post_birth_survival_ticks`
- `gen1_adult_count`
- `second_wave_success`

คำทำนาย:

- ถ้า energy debt เป็นรากหลัก การลด debt จะเพิ่ม final tick และ gen-1 readiness
- ถ้าเพิ่มแต่ survival ไม่เพิ่ม birth แปลว่า energy เป็น final failure mode แต่ไม่ใช่ reproductive gate หลัก

เกณฑ์สนับสนุน:

- final tick เพิ่ม
- gen-1 adult female full-ready ticks เพิ่ม
- gen-1 births เพิ่มอย่างน้อยบาง seed

### H17: Birth Cost Too Expensive Relative To Lifetime

สมมุติฐาน:

> การคลอดลูกหนึ่งครั้งแพงเกินไป ทำให้แม่และ household ล้มก่อนจะมีรอบที่สองหรือก่อนลูกช่วยระบบได้

ตัวแปรต้น:

- ลด `REPRODUCTION_COST`
- ลด `BIRTH_NEST_FOOD_COST`
- ลด mate energy cost
- ลด child dependency cost

ตัวแปรตาม:

- `mother_post_birth_survival_ticks`
- `second_birth_probability`
- `births_per_mother`
- `matured_children`
- `gen1_births`

คำทำนาย:

- ลด cost แล้ว mothers ต้องอยู่รอดหลัง birth นานขึ้น
- ถ้า cost เป็นคอขวดจริง จะเห็น second birth หรือ gen-1 birth เพิ่ม

เกณฑ์สนับสนุน:

- births เพิ่มเกิน first-wave ceiling เดิมประมาณ `6`
- matured per birth ไม่ตกมากจนเป็น false positive

### H18: Settlement Trap

สมมุติฐาน:

> การกลับรัง/อยู่รังช่วย mating แต่ทำให้ production ลดหรือทำให้ adult ติดพื้นที่ที่อาหารไม่พอ

ตัวแปรต้น:

- ปรับ nest radius/return-home bias
- จำกัด rendezvous เฉพาะช่วงที่ energy และ nest food พร้อม
- เพิ่ม foraging commute efficiency จาก nest

ตัวแปรตาม:

- `food_collected_per_adult`
- `active_nest_food`
- `no_mate`
- `not_near_nest`
- `nest_food_low`
- `births`
- `matured_children`

คำทำนาย:

- ถ้า settlement trap จริง condition ที่ลดการติดรังควรเพิ่ม food/energy โดยไม่ทำให้ no_mate กลับมาสูงเกินไป
- ถ้ากลับรังมากขึ้นแล้ว food เหลือแต่ birth ไม่เพิ่ม แปลว่า trap คือ liquidity/role alignment ไม่ใช่ location อย่างเดียว

เกณฑ์สนับสนุน:

- เพิ่ม production และลด blockers พร้อมกัน
- ถ้าเพิ่มเฉพาะ stored food แต่ offspring ไม่เพิ่ม ถือว่ายังเป็น wealth without offspring

## 6. Interaction ที่ต้องทดสอบ

ควรทดสอบ interaction ที่มีเหตุผล ไม่ใช่ stack ทุกอย่าง:

| Interaction | เหตุผล |
|---|---|
| `H12 + H13` | second-wave อาจต้อง parent-child overlap |
| `H12 + H14` | gen-1 อาจติด food liquidity |
| `H13 + H17` | birth cost อาจฆ่า parent-child bridge |
| `H14 + H15` | food ต้องพร้อมและ breeder ต้องถูกปกป้อง |
| `H16 + H17` | energy debt กับ birth cost อาจเป็นก้อนเดียวกัน |
| `H1 + H11 + H14 + H17` | best old stack + food liquidity + birth cost |

หลีกเลี่ยงการรวม H6 ตอนนี้ เพราะ H6 จากชุดก่อนทำให้ collapse ทันที. ใช้ H6 เป็น stress test หลังพบ condition ที่มี second-wave reproduction แล้วเท่านั้น

## 7. แผนทดลอง

ขั้นที่ 1: Instrumentation-only

- รัน baseline, H11, H1+H11
- เพิ่ม metric H12-H18 โดยไม่แก้ behavior
- เป้าหมายคือหาว่า second wave หายตรง gate ไหน

ขั้นที่ 2: Single-factor interventions

- H12 second-wave support
- H13 parent-child overlap
- H14 food liquidity
- H15 reproductive role protection
- H16 early energy debt relief
- H17 lower birth cost
- H18 settlement trap adjustment

ขั้นที่ 3: Interaction minimal set

- H12+H13
- H12+H14
- H13+H17
- H14+H15
- H16+H17
- H1+H11+H14+H17

ขั้นที่ 4: Ranking

จัดอันดับด้วย:

1. gen-1 births
2. matured female offspring per adult female
3. max generation observed
4. final tick
5. food remaining ที่ไม่ใช่ wealth-only false positive

## 8. สิ่งที่คาดว่าจะเห็นก่อนทดลอง

คาดการณ์หลัก:

- H12 จะยืนยันว่า second wave เป็นจุดขาด
- H14 น่าจะสำคัญมาก เพราะ H1-H11 พบ `nest_food_low` สูงทั้งที่ food remaining ยังมี
- H17 น่าจะช่วย birth count ทะลุ first-wave ceiling เดิม
- H16 อาจเพิ่ม final tick แต่ถ้าไม่เพิ่ม gen-1 birth จะเป็นแค่ survival buffer
- H15 อาจช่วยถ้า full-ready ticks เพิ่ม ไม่ใช่แค่ opportunity windows
- H18 ต้องระวัง เพราะ H4 เคยลด no-mate แต่ทำ outcome แย่ลง

## 9. เกณฑ์สำเร็จ

condition ที่ถือว่าน่าสนใจต้องผ่านอย่างน้อย 2 ใน 4 ข้อนี้:

- มี `gen1_births > 0` เฉลี่ยมากกว่า baseline/H1+H11 ชัดเจน
- `max_generation_observed >= 2` หลาย seed และมีบาง seed ไปถึง gen-3
- `matured_female_children_per_adult_female` เพิ่มขึ้น ไม่ใช่แค่ final tick เพิ่ม
- births สูงกว่า first-wave ceiling เดิม `6` อย่างสม่ำเสมอ

condition ที่ควรตัดทิ้ง:

- เพิ่ม stored/nest food แต่ offspring ไม่เพิ่ม
- เพิ่ม final tick แต่ไม่มี gen-1 birth
- ลด blocker หนึ่งตัวแต่ matured children ลด
- ทำให้ extinction เร็วขึ้นเหมือน H6

## 10. สรุปก่อนทดลอง

H12-H18 จะทดสอบว่าปัญหาหลัง H11 คืออะไร ระหว่าง:

- second-wave reproduction ไม่เกิด
- parent-child overlap ไม่พอ
- food liquidity ไม่ตรงจังหวะ reproduction
- reproductive female ไม่มี role protection
- early energy debt ทำให้ทุกอย่างล้ม
- birth cost แพงเกิน lifespan economics
- settlement behavior เป็นกับดัก

สมมุติฐานที่ผมให้น้ำหนักก่อนทดลองมากที่สุดคือ H14 และ H17 รองลงมาคือ H12/H13. เหตุผลคือ H1-H11 แสดงชัดว่าอาหารยังเหลือแต่ไม่กลายเป็น offspring และ births ยังติด ceiling ใกล้ `6` เหมือนระบบมี first wave แต่ไม่มี second wave.


# รายงานวิเคราะห์ผลทดลอง H1-H11: Reproduction, Household, Energy, Food, Mutation

วันที่ทดลอง: 2026-06-03  
สคริปต์ทดลอง: `scripts/run_hypothesis_diagnostics.py`  
ผลดิบ: `data/hypothesis_diagnostics/h1_h11_2026-06-03/`  
รายงานอัตโนมัติ: `reports/hypothesis_diagnostics_h1_h11_2026-06-03.md`

## 1. คำตอบสั้นที่สุด

ผลทดลองชุดนี้ชี้ว่า bottleneck หลักตอนนี้ไม่ใช่ mutation และไม่ใช่ food scarcity แบบรวมทั้งระบบ แต่เป็น reproduction economics ที่ไม่สามารถแปลงทรัพยากรและเวลาชีวิตให้กลายเป็น offspring ที่โตทันได้

ทุก condition ยังสูญพันธุ์ 100% ภายใน `800` tick. ดังนั้นยังไม่มี hypothesis ใดแก้ปัญหา self-sustaining population ได้ แต่ H11 ได้รับการสนับสนุนแรงมากในฐานะ bottleneck จริง: baseline มี matured children เฉลี่ย `2.0` แต่ H11 เพิ่มเป็น `5.25`; และ interaction `H1 + H11` เพิ่มเป็น `5.75` พร้อม final tick สูงสุดเฉลี่ย `195.5`.

ประโยคสำคัญจากผลทดลองคือ:

> ระบบยังสร้าง wealth ได้ในบาง condition แต่ยังสร้าง replacement offspring ไม่ได้

ตัวอย่างชัดคือ `H1 + H11` มี nest food remaining เฉลี่ย `316.5` ตอนจบ แต่ population ยังเป็น `0`. นี่ตรงกับข้อสังเกตของคุณว่า "stored food สูงมาก แต่ population = 0" เป็นสัญญาณอันตรายกว่าการขาดอาหารเฉยๆ เพราะอาหารไม่ได้ถูกแปลงเป็น fertility ที่พอจะทดแทนรุ่นแม่ได้

## 2. ขอบเขตและวิธีทดลอง

การทดลองนี้เป็น diagnostic intervention ไม่ใช่ patch ถาวรใน simulation core. สคริปต์ใช้ monkeypatch เพื่อทดสอบทิศทางของแต่ละ hypothesis แบบควบคุม seed เดียวกัน

- body: `body_index=14`
- profile: `nurturing_settler`
- initial population: `250`
- max population: `375`
- max ticks: `800`
- seeds: `7, 8, 11, 13`
- replicates ต่อ condition: `4`
- เงื่อนไขที่รัน: baseline, H1-H11, และ interaction 4 ชุด

มี sanity check เพิ่มกับ core runner โดยตรง: seed `7` ของ baseline ให้ผล `final_tick=114`, `births=6`, `matured=3`, `death_reasons={'energy_depleted': 256}` ซึ่งตรงกับ diagnostic runner. ดังนั้น collapse ที่เห็นในชุดนี้เป็นพฤติกรรมของ current branch ไม่ใช่ artifact จากสคริปต์ diagnostic

ข้อควรระวัง: ผลนี้ต่างจาก artifact/report เก่าบางชุดที่เคยไปได้ไกลกว่านี้ จึงควรถือว่า current branch ตอนนี้อยู่ในสภาวะ early-collapse หรือมี regression ด้าน survival/reproduction อยู่

## 3. ตัวแปรตามที่ใช้วัด

ตัวแปรตามหลัก:

- `extinction_rate`: สูญพันธุ์หรือไม่
- `mean_final_tick`: อยู่รอดได้นานแค่ไหน
- `mean_total_births`: จำนวนเกิด
- `mean_matured_children`: จำนวนลูกที่โตถึงวัย mature
- `mean_matured_female_children_per_adult_female`: replacement proxy สำคัญที่สุด
- `mean_opportunity_windows`: หน้าต่างโอกาส reproduction ต่อ adult female lifetime
- `share_adult_females_below_2_opportunities`: สัดส่วนตัวเมียที่มีโอกาสน้อยกว่า 2 ครั้ง
- `mean_nest_food_remaining`, `mean_stored_food_total`: wealth ที่เหลือ
- reproduction blockers: `nest_food_low`, `low_energy`, `no_mate`, `cooldown`, `not_near_nest`

เกณฑ์ตีความ H11:

- ถ้า `opportunity_windows < 2` เฉลี่ย แปลว่า female lifetime มีรอบ reproduction ไม่พอ
- ถ้า `matured_female_children_per_adult_female < 1` แปลว่า replacement ยังไม่ถึง
- ใน baseline ค่านี้คือ `0.0098` เท่านั้น

## 4. ตารางสรุปผลทุก condition

| Condition | H | ตัวแปรต้นที่ทดสอบ | Final Tick | Births | Matured | Opp/Female | Female <2 Opp | Nest Food Left | ผลตีความ |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| baseline | - | current branch | 132.0 | 6.0 | 2.0 | 1.01 | 0.97 | 85.5 | collapse เร็ว, replacement ไม่ถึง |
| h1_breeder_tuned | H1 | breeder energy/storage tuning | 141.0 | 6.0 | 1.75 | 1.03 | 0.95 | 106.0 | ช่วย survival เล็กน้อย แต่ไม่เพิ่ม offspring |
| h2_canonical_household | H2 | canonical household owner | 181.25 | 6.25 | 1.75 | 0.99 | 1.00 | 187.5 | wealth เพิ่ม แต่ offspring ไม่เพิ่ม |
| h3_pipeline_priority | H3 | juvenile/new-adult priority | 132.0 | 6.0 | 2.0 | 1.01 | 0.97 | 85.5 | ไม่มีผลใน current collapse |
| h4_mate_rendezvous | H4 | mate/nest rendezvous | 119.0 | 6.0 | 1.0 | 0.98 | 0.99 | 186.0 | ลดบาง blocker แต่ outcome แย่ลง |
| h5_soft_cooldown | H5 | reproduction cooldown softer | 132.0 | 6.0 | 2.0 | 1.01 | 0.97 | 85.5 | cooldown ไม่ใช่คอขวดหลัก |
| h6_earned_nest_support | H6 | ลด scaffold/support เหลือ active-earned | 41.5 | 0.25 | 0.0 | 0.02 | 1.00 | 45.0 | catastrophic collapse |
| h7_managed_patch_productivity | H7 | food patch productivity | 126.25 | 6.0 | 2.25 | 0.97 | 1.00 | 103.0 | ช่วยเล็กน้อย แต่ไม่แก้ reproduction |
| h8_adult_energy_saver | H8 | adult near-nest energy saver | 150.0 | 6.0 | 1.5 | 1.20 | 0.78 | 124.25 | เพิ่มโอกาส แต่ไม่แปลงเป็นลูกโต |
| h9_disable_mutation | H9 | ปิด inherited mutation | 160.0 | 6.25 | 2.25 | 0.98 | 0.99 | 122.0 | mutation ไม่ใช่จุดควรลงตอนนี้ |
| h10_delay_technology | H10 | delay hearth/technology | 132.0 | 6.0 | 2.0 | 1.01 | 0.97 | 85.5 | technology ยังไม่ active ก่อน collapse |
| h11_extend_reproductive_life | H11 | เพิ่ม reproductive opportunity | 115.5 | 6.0 | 5.25 | 1.25 | 0.72 | 99.75 | เพิ่มลูกที่ mature ชัด แต่ยังไม่พอ |
| i_h1_h11 | H1+H11 | breeder tuning + opportunity | 195.5 | 6.5 | 5.75 | 1.28 | 0.69 | 316.5 | interaction ดีที่สุด แต่ยังสูญพันธุ์ |
| i_h2_h4_h11 | H2+H4+H11 | household + rendezvous + opportunity | 121.5 | 6.25 | 5.25 | 1.08 | 0.89 | 86.5 | H11 ช่วย mature แต่ stack ไม่ชนะ |
| i_h6_h7 | H6+H7 | active support + food productivity | 35.0 | 0.0 | 0.0 | 0.02 | 1.00 | 42.25 | food patch ชดเชย scaffold removal ไม่ได้ |
| i_reproduction_stack | stack | H1+H2+H3+H4+H5+H8+H11 | 156.25 | 6.0 | 5.75 | 1.21 | 0.78 | 169.75 | ได้ matured สูง แต่แพ้ H1+H11 |

## 5. วิเคราะห์ H1-H11

### H1: Breeder-Priority Tuning

ตัวแปรต้น: ปรับ energy reserve และ storage behavior ของ breeder/general adult  
ตัวแปรตาม: survival, births, matured children, opportunity windows

ผล: final tick เพิ่มจาก `132.0` เป็น `141.0` และ opportunity windows เพิ่มเล็กน้อยจาก `1.01` เป็น `1.03` แต่ matured children ลดจาก `2.0` เป็น `1.75`.

สรุป: H1 เดี่ยวๆ ไม่ใช่คำตอบ แต่เป็นส่วนประกอบสำคัญเมื่อรวมกับ H11. ถ้ามีเวลาชีวิตพอแล้ว การจัด energy/storage ให้ breeder จะช่วยให้ระบบไปต่อได้ดีขึ้น

### H2: Canonical Household Owner

ตัวแปรต้น: แก้ household/nest ownership ให้ canonical มากขึ้น  
ตัวแปรตาม: owner mismatch, food distribution, births, matured children

ผล: owner mismatch ลดเป็น `0.0` และ final tick เพิ่มเป็น `181.25`; nest food remaining เพิ่มเป็น `187.5`. แต่ matured children ลดเหลือ `1.75`.

สรุป: H2 สร้างความเป็นระเบียบและ wealth ได้ แต่ยังไม่สร้าง offspring. นี่เป็นหลักฐานตรงของ "wealth without offspring"

### H3: Juvenile/New-Adult Pipeline Priority

ตัวแปรต้น: ให้ juvenile/new adult มี priority ถอนอาหารหรือรับ support มากขึ้น  
ตัวแปรตาม: matured children, survival, births

ผล: ผลเท่ากับ baseline แทบทุกค่า

สรุป: current branch collapse เร็วเกินกว่าที่ pipeline intervention นี้จะแสดงผล หรือ gate ที่ขวางอยู่ก่อนหน้า pipeline หนักกว่า

### H4: Mate/Nest Rendezvous

ตัวแปรต้น: bias ให้ adult กลับ nest/rendezvous เพื่อหา mate  
ตัวแปรตาม: no-mate blocker, not-near-nest blocker, births, matured children

ผล: `no_mate` blocker ลดจาก `1885` เป็น `1652`; `not_near_nest` ลดจาก `177` เป็น `100`. แต่ matured children ลดจาก `2.0` เป็น `1.0` และ final tick ลดเป็น `119.0`.

สรุป: การทำให้เจอกันใกล้รังไม่พอ และอาจทำให้ adult อยู่ในตำแหน่ง/พฤติกรรมที่ไม่ผลิตอาหารหรือรักษาพลังงานได้ดีพอ

### H5: Soft Reproduction Cooldown

ตัวแปรต้น: ลด cooldown pressure  
ตัวแปรตาม: cooldown blockers, births, matured children

ผล: `cooldown` blockers ลดจาก `420` เป็น `216` แต่ births และ matured children ไม่เปลี่ยน

สรุป: cooldown ไม่ใช่ bottleneck หลักตอนนี้. ต่อให้ลด cooldown ระบบก็ยังติด energy, nest food, และ opportunity quality

### H6: Earned Active Nest Support

ตัวแปรต้น: ลด initial nest food และให้ support เฉพาะ active/earned nest  
ตัวแปรตาม: births, matured children, extinction speed

ผล: final tick เหลือ `41.5`, births เหลือ `0.25`, matured children เป็น `0.0`.

สรุป: scaffold/support ปัจจุบันยังจำเป็นมาก. การถอด support ตอนนี้ทำให้ระบบพังทันที แปลว่าระบบยังไม่ได้ self-sustain จาก production จริง

### H7: Managed Patch Productivity

ตัวแปรต้น: เพิ่ม/ผ่อนเงื่อนไข productivity ของ food patch  
ตัวแปรตาม: active nest food, births, matured children

ผล: matured children เพิ่มเล็กน้อยจาก `2.0` เป็น `2.25`; active nest food mean เพิ่มเป็น `28.29`, แต่ opportunity windows ลดเป็น `0.97`.

สรุป: food production ช่วยได้เล็กน้อย แต่ไม่แก้คอขวด reproduction. ปัญหาน่าจะเป็น food usability, timing, household routing, หรือ gate alignment มากกว่า global food amount

### H8: Adult Energy Saver

ตัวแปรต้น: ลด energy drain ของ adult ใกล้รัง  
ตัวแปรตาม: survival, opportunity windows, matured children

ผล: final tick เพิ่มเป็น `150.0`, opportunity windows เพิ่มเป็น `1.20`, share female below 2 opportunities ลดเป็น `0.78`. แต่ matured children ลดเหลือ `1.5`.

สรุป: จำนวนโอกาสไม่พอ ต้องมีคุณภาพของโอกาสด้วย. Adult อยู่รอดและมี window มากขึ้น แต่ window เหล่านั้นไม่พร้อมครบเงื่อนไข reproduction/child survival

### H9: Disable Mutation

ตัวแปรต้น: ปิด inherited mutation  
ตัวแปรตาม: survival, births, matured children

ผล: final tick เพิ่มเป็น `160.0`, births เพิ่มเป็น `6.25`, matured children เพิ่มเป็น `2.25`.

สรุป: สนับสนุนความเห็นว่าตอนนี้ยังไม่ควรลง mutation. mutation ไม่ใช่ bottleneck และการปิด mutation ไม่ทำให้แย่ลงใน current branch

### H10: Delay Technology

ตัวแปรต้น: delay hearth/object experimentation  
ตัวแปรตาม: technology event, survival, births, matured children

ผล: เท่ากับ baseline

สรุป: technology ยังไม่ใช่ตัวแปรสำคัญในช่วงนี้ เพราะระบบ collapse ก่อน technology จะมีแรงพอให้เปลี่ยน outcome

### H11: Reproduction Opportunity Bottleneck

ตัวแปรต้น: เพิ่มช่วง reproductive life และลด development time เพื่อให้ female มีจำนวนรอบ reproduction จริงมากขึ้น  
ตัวแปรตาม: opportunity windows per female, matured children, matured female replacement

ผลสำคัญ:

- matured children เพิ่มจาก `2.0` เป็น `5.25`
- opportunity windows/female เพิ่มจาก `1.01` เป็น `1.25`
- share adult females below 2 opportunities ลดจาก `0.97` เป็น `0.72`
- matured female children per adult female เพิ่มจาก `0.0098` เป็น `0.0196`
- births ยังเท่าเดิมที่ `6.0`

สรุป: H11 ถูกต้องในเชิงทิศทาง แต่ยังไม่พอ. มันช่วยให้ลูกที่เกิดแล้วโตทันมากขึ้น แต่ยังไม่ได้ทำให้จำนวน birth เพิ่ม และยังห่างจาก replacement rate มาก

จุดละเอียดสำคัญ: `opportunity_windows` เพิ่ม แต่ `full_ready_ticks` ยังอยู่แค่ประมาณ `0.047` ต่อ adult female. แปลว่าตัวเมียอาจมี "หน้าต่างเวลา" มากขึ้น แต่มี tick ที่พร้อมครบเงื่อนไขจริงน้อยมาก

## 6. Interaction ระหว่างสมมุติฐาน

### H1 + H11: interaction ที่ดีที่สุด

ผล:

- final tick: `195.5` เทียบ baseline `132.0`
- births: `6.5` เทียบ baseline `6.0`
- matured children: `5.75` เทียบ baseline `2.0`
- opportunity windows/female: `1.28` เทียบ baseline `1.01`
- nest food remaining: `316.5` เทียบ baseline `85.5`

seed `7` ใน condition นี้เป็น run ที่ดีที่สุด: `final_tick=359`, `births=8`, `matured=8`, `max_generation=2`, แต่สุดท้ายยังสูญพันธุ์

ตีความ: H11 เปิดพื้นที่เวลาให้ reproduction economics ทำงาน ส่วน H1 ช่วยเรื่อง breeder allocation. แต่ยังเกิด wealth accumulation โดยไม่เกิด replacement chain

### H2 + H4 + H11: H11 ช่วย แต่ household/rendezvous ไม่พอ

ผล matured children เท่ากับ `5.25` ซึ่งน่าจะมาจาก H11 เป็นหลัก แต่ final tick อยู่แค่ `121.5`, ต่ำกว่า baseline เล็กน้อย

ตีความ: การแก้ ownership กับ mating location ไม่พอถ้า energy/food gate และ opportunity quality ยังไม่ align

### H6 + H7: productivity ชดเชย scaffold removal ไม่ได้

ผล final tick `35.0`, births `0`, matured `0`

ตีความ: ถ้าตัด support เร็วเกินไป ระบบพังทันที แม้จะเพิ่ม food patch productivity แล้วก็ตาม. จึงไม่ควรใช้ H6 เป็น fix ในตอนนี้ ควรใช้เป็น stress test หลังระบบสร้าง replacement ได้แล้ว

### Reproduction Stack: รวมหลายอย่างแล้วไม่ชนะ H1+H11

ผล matured children `5.75` เท่ากับ H1+H11 แต่ final tick แค่ `156.25`, ต่ำกว่า H1+H11 มาก

ตีความ: การ stack หลาย intervention ทำให้บางส่วนชนกัน. ชุดที่สะอาดกว่าอย่าง H1+H11 ให้ signal ดีกว่า

## 7. Reproduction Opportunity Lifetime Analysis

จาก `female_lifetimes.csv`:

| Condition | Adult Females | Female <2 Opp | Share <2 Opp | Birth 0 | Birth 1 | Birth 2+ | Matured Female 0 | Matured Female 1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 511 | 497 | 0.97 | 487 | 24 | 0 | 506 | 5 |
| H11 | 511 | 367 | 0.72 | 487 | 24 | 0 | 501 | 10 |
| H1+H11 | 513 | 356 | 0.69 | 488 | 24 | 1 | 503 | 9 |
| reproduction stack | 511 | 399 | 0.78 | 487 | 24 | 0 | 501 | 10 |
| H6 | 500 | 500 | 1.00 | 499 | 1 | 0 | 500 | 0 |

ข้อค้นพบ:

- baseline มี adult female `97%` ที่มี opportunity ต่ำกว่า 2 ครั้ง
- H11 ลดเหลือ `72%`, H1+H11 ลดเหลือ `69%`
- แต่ female ส่วนใหญ่ยัง birth `0`
- ตัวเมียที่ผลิต matured female offspring ได้ยังมีน้อยมาก

ดังนั้น hypothesis ของคุณถูกจุด: bottleneck ไม่ใช่แค่ "พร้อมมีลูกไหม" แต่คือ "มีโอกาสจริงกี่รอบตลอดชีวิต และแต่ละรอบพร้อมครบเงื่อนไขหรือไม่"

## 8. Reproduction Blockers

baseline blockers รวม 4 seeds:

| Blocker | Count |
|---|---:|
| nest_food_low | 16000 |
| low_energy | 13607 |
| no_mate | 1885 |
| cooldown | 420 |
| not_near_nest | 177 |

H11 blockers:

| Blocker | Count |
|---|---:|
| nest_food_low | 14930 |
| low_energy | 13017 |
| no_mate | 1836 |
| cooldown | 415 |
| not_near_nest | 172 |

H1+H11 blockers:

| Blocker | Count |
|---|---:|
| nest_food_low | 14593 |
| low_energy | 13004 |
| no_mate | 1964 |
| cooldown | 451 |
| not_near_nest | 276 |

ข้อสรุปจาก blockers:

- H11 และ H1+H11 ลด `nest_food_low` และ `low_energy` ได้บางส่วน แต่ไม่มากพอ
- `nest_food_low` ยังสูงแม้มี nest food remaining สูง แปลว่าอาหารรวมไม่ได้แปลว่าอาหารพร้อมใช้ใน household/time/owner ที่ reproductive female ต้องการ
- H4 ลด `no_mate` และ `not_near_nest` ได้จริง แต่ outcome แย่ลง แปลว่า mating-location gate ไม่ใช่คอขวดเดี่ยว
- H5 ลด cooldown blockers ได้จริง แต่ births ไม่เพิ่ม แปลว่า cooldown เป็น secondary gate

## 9. สมมุติฐานที่ได้รับการสนับสนุน / ไม่สนับสนุน

สนับสนุนแรง:

- H11: reproduction opportunity bottleneck เป็นปัญหาจริง
- H6 ในเชิงลบ: scaffold removal ตอนนี้ทำให้ collapse ทันที แปลว่าระบบยังพึ่ง support
- H9: mutation ยังไม่ควรเป็น priority

สนับสนุนแบบมีเงื่อนไข:

- H1: ดีเมื่อรวมกับ H11 แต่เดี่ยวๆ ไม่พอ
- H2: แก้ wealth/ownership ได้ แต่ไม่แก้ fertility
- H7: food productivity ช่วยนิดเดียว
- H8: เพิ่ม opportunity quantity แต่ไม่เพิ่ม offspring quality

ไม่ใช่ bottleneck หลักตอนนี้:

- H3: pipeline priority ไม่มีผล
- H5: cooldown ไม่ใช่คอขวดหลัก
- H10: technology ยังไม่ active ทันก่อน collapse

## 10. ข้อสรุปเชิงระบบ

### 10.1 ระบบติด "wealth-to-offspring conversion"

อาหารมีอยู่ในบาง condition แต่ไม่ถูกแปลงเป็นลูกที่โตและมีลูกต่อ. นี่สำคัญกว่าการถามว่า food total พอไหม

ตัวอย่าง:

- H2: nest food remaining `187.5`, matured `1.75`
- H4: nest food remaining `186.0`, matured `1.0`
- H1+H11: nest food remaining `316.5`, matured `5.75`, แต่ population `0`

### 10.2 opportunity quantity ไม่เท่ากับ opportunity quality

H8 เพิ่ม opportunity windows เป็น `1.20` แต่ matured ลดเหลือ `1.5`. H11 เพิ่ม matured ได้เพราะลด development/เพิ่ม lifespan economics ไม่ใช่แค่ทำให้ adult อยู่ใกล้รังนานขึ้น

ควรแยก metric ใหม่:

- `opportunity_window_count`: จำนวนรอบที่พอมีโอกาส
- `full_ready_ticks`: จำนวน tick ที่พร้อมครบทุก gate
- `quality_opportunity_windows`: window ที่ energy, mate, nest, food, cooldown, child survival path พร้อมครบ

### 10.3 current branch collapse ด้วย energy เป็นหลัก

death reason แทบทั้งหมดคือ `energy_depleted`. baseline มี `energy_depleted=1023` จาก 4 seeds. แม้ condition ที่ดีขึ้นก็ยังตายด้วย energy เป็นหลัก

นี่ไม่ได้แปลว่า energy เป็น hypothesis เดียวที่ต้องแก้ แต่แปลว่า energy เป็น final failure mode ที่กลบ reproduction economics อยู่

### 10.4 replacement rate ยังห่างมาก

baseline `matured_female_children_per_adult_female = 0.0098`  
H11 `= 0.0196`  
H1+H11 `= 0.0214`

แม้เพิ่มขึ้นสองเท่า แต่ยังห่างจาก `1.0` มาก จึงยังไม่มีทาง sustain population

## 11. คำแนะนำลำดับงานถัดไป

1. อย่าเริ่ม mutation ตอนนี้

Mutation ยังไม่ใช่ bottleneck และมีโอกาสเปลืองพลังการทดลอง เพราะระบบยังไม่สร้าง replacement chain ได้

2. ทำ H11 เป็น instrumentation ถาวร

ควรเพิ่ม metric ต่อไปนี้เข้า core run/report:

- reproduction opportunities per female lifetime
- full-ready reproduction ticks
- opportunity windows split by gate: energy, mate, near nest, nest food, cooldown
- births per adult female lifetime
- matured female offspring per adult female lifetime
- household food available to reproductive female at decision tick

3. ทดลอง factorial เฉพาะ H11

แยก H11 ออกเป็นตัวแปรย่อย:

- shorter childhood
- shorter juvenile phase
- longer adult phase
- delayed old age
- lower child-care duration
- lower child energy cost

ตอนนี้ H11 รวมหลายแกนเข้าด้วยกัน จึงรู้ว่าทิศทางถูก แต่ยังไม่รู้แกนย่อยไหนสำคัญที่สุด

4. เอา H1+H11 เป็น candidate fix แรก

เพราะเป็น interaction ที่ดีที่สุดและสะอาดที่สุด ควรเอาไปทดสอบแบบละเอียดกว่า stack ใหญ่

5. แก้ food usability ไม่ใช่เพิ่ม food total อย่างเดียว

ควรวัดว่าใน tick ที่ female จะ reproduce:

- nest ที่เธอใช้มี food จริงไหม
- owner/household ตรงไหม
- food ถูกล็อกอยู่กับ abandoned nest หรือไม่
- food อยู่ใน agent storage แต่ไม่ถูกใช้หรือไม่
- breeder ต้องเสียเวลาไปหาอาหารเองจนพลาด reproduction window หรือไม่

6. ใช้ H6 เป็น stress test ตอนท้าย

H6 ไม่ควรเป็น fix ตอนนี้ เพราะตัด scaffold แล้วระบบ collapse ทันที. ควรรอจน H1+H11 หรือชุดใหม่ทำ replacement chain ได้ก่อน แล้วค่อยลด support เพื่อดูว่า self-sustain จริงไหม

## 12. สรุปสุดท้าย

ผลทดลองสนับสนุน H11 ชัดเจน: ระบบมี reproduction opportunity bottleneck จริง และค่าเฉลี่ย opportunity ต่ำกว่า 2 ต่อ female lifetime ทำให้ replacement แทบเป็นไปไม่ได้

แต่ H11 เดี่ยวๆ ยังไม่พอ เพราะจำนวน birth ไม่เพิ่ม และ full-ready ticks ยังต่ำมาก. bottleneck ที่แท้จริงตอนนี้น่าจะเป็นชุดร่วมกันของ:

- lifespan economics
- breeder energy/storage allocation
- food usability ณ tick ที่ reproduction decision เกิด
- child maturation timing
- household routing

ทางที่มี signal ดีที่สุดจากชุดนี้คือ `H1 + H11`, ไม่ใช่ mutation, ไม่ใช่ technology, และไม่ใช่การเพิ่ม food total อย่างเดียว


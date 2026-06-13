# รายงานวิเคราะห์ Phase 5.1-5.3: Site Selection Controls

วันที่: 2026-06-13
ข้อมูลรัน: `data\phase5_1_site_selection_confirm01_20260613`
รายงานตารางดิบ: `reports\phase5_1_site_selection_confirm01_2026-06-13.th.md`
Protocol: `reports\phase5_1_site_selection_controls_protocol_2026-06-13.th.md`

## Verdict

Phase 5.1-5.3 ยังไม่ผ่าน core gate

Baseline 100x100 ได้:

- `passing_runs = 0/5`
- `direction_consistent_runs = 0/5`
- `phase5_core_pass = false`

ข้อสรุปหลัก: agent มีการขยับ seed และ chain จาก seed ไป plant ไป fruit ไป agent ยังเกิดจริง แต่หลักฐานยังไม่พอที่จะเรียกว่า learned site selection เพราะจุด drop ไม่ชนะ current-position, nearby, และ visible controls

## ผลหลัก

| condition | pass | direction | current | nearby | visible | visible-best | future | drops |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_100x100 | 0/5 | 0/5 | 0.99576 | 0.97942 | 0.97574 | 0.91344 | 1.16256 | 137.2 |
| low_food_signal_100x100 | 0/5 | 0/5 | 0.98892 | 0.98108 | 0.97842 | 0.90030 | 1.13546 | 144.2 |
| 200x200 same-density | 0/3 | 0/3 | 1.00123 | 0.99303 | 0.98993 | 0.95260 | 1.16520 | 95.0 |
| 200x200 same-population | 0/3 | 0/3 | 0.98840 | 0.99497 | 0.99297 | 0.96037 | 1.15137 | 24.33 |

อ่านตาราง:

- `future` ผ่านทุก condition แต่ `current`, `nearby`, `visible` ไม่ผ่าน
- `visible-best` ต่ำกว่า 1 ทุก condition แปลว่าในระยะที่ agent เห็นได้มีจุดที่ดีกว่าจุด drop อยู่เสมอโดยเฉลี่ย
- 200x200 same-population มี activity ต่ำมากเมื่อเทียบกับ same-density

## Evidence Supporting

มี evidence สนับสนุนว่าระบบ ecological chain ทำงาน:

- baseline มี `mean_agent_moved_drop_count = 137.2`
- baseline มี `mean_high_quality_chain_rate = 0.20556` เทียบกับ `mean_low_quality_chain_rate = 0.13109`
- 200x200 same-density ยังรักษา activity ได้พอสมควรที่ `mean_agent_moved_drop_count = 95.0`
- future-path lift มากกว่า 1 ในทุก condition แปลว่าหลัง drop แล้ว agent มักเดินต่อไปยังจุดที่ quality ต่ำกว่า

## Evidence Against

หลักฐานคัดค้าน site selection แข็งกว่า:

- baseline `current_lift = 0.99576` ต่ำกว่าเกณฑ์ 1.10 และต่ำกว่า 1
- baseline `nearby_lift = 0.97942` ต่ำกว่าเกณฑ์ 1.05 และต่ำกว่า 1
- baseline `visible_lift = 0.97574` ต่ำกว่าเกณฑ์ 1.00
- baseline `visible_best_lift = 0.91344` แปลว่าจุด drop แย่กว่าจุดดีที่สุดในระยะเห็นอย่างชัดเจน
- baseline `late_vs_early = 1.0364` ยังต่ำกว่าเกณฑ์ 1.05
- direction consistency เป็น 0/5 ใน baseline

ดังนั้น random/future lift ที่ดูดีไม่พอ เพราะ controls ที่ถามตรงกว่าไม่สนับสนุนว่า agent เลือกพื้นที่

## Drop Context

drop context รวมต่อ condition:

| condition | total moved drops | hunger | food_contact | balanced_random |
| --- | ---: | ---: | ---: | ---: |
| baseline_100x100 | 686 | 668 | 16 | 2 |
| low_food_signal_100x100 | 721 | 691 | 26 | 4 |
| 200x200 same-density | 285 | 270 | 13 | 2 |
| 200x200 same-population | 73 | 70 | 2 | 1 |

การอ่านผล:

- มากกว่า 94% ของ agent-moved drops เกิดใน context `hunger`
- ใน baseline seed 20260610 ค่า `seed_drop_hunger` เฉลี่ย 0.9701 และ `seed_drop_energy` เฉลี่ย -0.0462
- นี่ทำให้ future-path lift ต้องตีความระวัง เพราะหลัง drop agent อาจเดินต่อภายใต้ hunger pressure ไม่ใช่เพราะมันเลือกปลูกในจุดดี

## 200x200 Diagnosis

same-density:

- drops เฉลี่ย 95.0
- current lift ประมาณ 1.00123
- visible lift 0.98993
- future lift 1.16520

same-population:

- drops เฉลี่ย 24.33
- current lift 0.98840
- visible lift 0.99297
- future lift 1.15137

สรุป: ความล้มเหลวในโลก 200x200 มี density/population effect ชัดเจน แต่แม้ same-density จะมี activity มากกว่า ก็ยังไม่ผ่าน site-selection controls

## Alternative Explanations

1. Hunger-pressure explanation
   - seed movement ส่วนใหญ่เกิดตอนหิว
   - agent อาจเก็บและปล่อย seed เป็นผลข้างเคียงของการหาอาหาร

2. Local-opportunity explanation
   - visible-best control สูงกว่าจุด drop
   - แปลว่า agent ไม่ได้เลือกจุดที่ดีที่สุดในพื้นที่ที่เข้าถึงได้ ณ ตอนนั้น

3. Nutrient saturation explanation
   - nutrient score เฉลี่ยสูงมากทุก condition เช่น baseline 0.99309
   - total quality อาจถูกบีบให้ต่างกันน้อย และทำให้ moisture/light/temp เป็นตัวแยกจริง

4. Future-path artifact
   - future lift สูงอาจเกิดจาก agent เดินต่อไปสู่พื้นที่แย่เพราะ hunger หรือ movement policy ไม่ใช่เพราะ drop point ดีเป็นพิเศษ

## Missing Evidence

ยังขาดหลักฐานเหล่านี้ก่อนเรียก learning:

- control ที่ใช้ sensory features จริงของ agent แทน observer plant-quality score
- test ที่ลด hunger-driven seed drop โดยไม่สอนการปลูก
- memory-disabled หรือ shuffled-memory ablation
- counterfactual แบบจำลองคู่ขนานที่ agent ถือ seed ต่อจริง ๆ ไม่ใช่ใช้ future path หลัง drop
- world calibration ที่ลด nutrient saturation
- population-scaling sweep ใน 200x200 เช่น 50, 100, 200 agents

## Confidence Level

ความมั่นใจสูงว่า Phase 5.1-5.3 ยังไม่ผ่าน site selection

ความมั่นใจปานกลางถึงสูงว่า seed movement ตอนนี้ถูก hunger/food loop ครอบเป็นส่วนใหญ่

ความมั่นใจปานกลางว่า 200x200 failure เกี่ยวข้องกับ density/population เพราะ same-population drops ลดเหลือ 24.33 เทียบกับ same-density 95.0

## Next Step

งานถัดไปควรเป็น Phase 5.4: hunger-decoupled seed handling

เป้าหมายคือไม่สอน agent ว่า seed ใช้ปลูก แต่แยก seed behavior ออกจากภาวะหิวให้สะอาดพอจะทดสอบ learning ได้:

1. เพิ่ม condition `hunger_neutral_seed_drop`
   - ไม่เพิ่มโอกาส drop ตอน hunger
   - ยังปล่อยให้ pick/drop แบบ curiosity/food_contact ได้

2. เพิ่ม condition `seed_drop_context_matched`
   - เทียบเฉพาะ drops ที่ context เดียวกัน เช่น hunger-only กับ hunger-only

3. เพิ่ม condition `nutrient_desaturated_world`
   - ทำให้ nutrient score ไม่ saturate ใกล้ 1 ตลอด

4. เพิ่ม condition `visible_opportunity_gap_gate`
   - ถ้า visible-best สูงกว่า drop มาก ให้ถือว่ายังไม่ผ่าน แม้ future lift ผ่าน

5. เพิ่ม population sweep สำหรับ 200x200
   - 50, 100, 200 agents
   - แยก density effect ออกจาก world-size effect

## Final Interpretation

ตอนนี้ระบบพิสูจน์ได้ว่า seed ecology chain มีอยู่จริง แต่ยังไม่พิสูจน์ว่า agent เรียนรู้หรือเลือกพื้นที่ปลูก

ผลสำคัญที่สุดของรอบนี้คือเราเจอช่องโหว่ที่ชัด: future/random controls สามารถดูดีได้ แต่ current/nearby/visible controls ทำให้เห็นว่านั่นยังไม่ใช่ site selection จริง

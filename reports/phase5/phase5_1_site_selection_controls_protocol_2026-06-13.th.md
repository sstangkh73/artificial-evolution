# Protocol: Phase 5.1-5.3 Site Selection Controls

วันที่: 2026-06-13

## Objective

ทดสอบว่า agent ไม่ได้แค่พา seed ไปเจอพื้นที่ดีโดยบังเอิญ แต่มีหลักฐานว่าจังหวะ `drop seed` ดีกว่า control ที่เหมาะสมกว่าเดิม

## Hypothesis

H5.1: ถ้า agent มีพฤติกรรมเลือกพื้นที่ปลูกจริง จุด drop ควรดีกว่าจุดที่ agent ถือ seed อยู่ก่อนหน้า

H5.2: จุด drop ควรดีกว่า control ในระยะที่ agent มองเห็นได้ ไม่ใช่แค่ดีกว่า random world

H5.3: จุด drop ควรดีกว่าจุดที่ agent เดินต่อไปหลังจากนั้น ถ้าไม่เช่นนั้น drop timing ยังตีความเป็นการเลือกไม่ได้

## Independent Variables

- world size: 100x100, 200x200
- resource density: same-density vs same-population/resource count
- food signal strength: default vs low-food-signal ablation
- seed/run id

## Dependent Variables

- `drop_quality_vs_current_position_lift`
- `drop_quality_vs_nearby_control_lift`
- `drop_quality_vs_visible_control_lift`
- `drop_quality_vs_visible_best_control_lift`
- `drop_quality_vs_future_path_control_lift`
- `high_quality_completed_chain_rate`
- `low_quality_completed_chain_rate`
- `late_vs_early_drop_quality_lift`

## Controls

1. `current_position_control`
   - คุณภาพจุดที่ agent ถือ seed อยู่ก่อนหน้า drop
   - เป็น control หลักที่สุด เพราะถามว่า agent เลือก drop ในจุดที่ดีกว่าจุดที่มันมีอยู่แล้วหรือไม่

2. `nearby_control`
   - ค่าเฉลี่ยคุณภาพพื้นที่เดินได้รอบจุด drop ใน radius 3

3. `visible_control`
   - ค่าเฉลี่ยคุณภาพพื้นที่เดินได้ในระยะมองเห็นของ agent ตอน drop
   - ยังเป็น observer quality score แต่จำกัดพื้นที่ control ตาม perception radius ของ agent

4. `visible_best_control`
   - จุดดีที่สุดในระยะมองเห็นของ agent ตอน drop
   - ใช้เป็น diagnostic ไม่ใช่ hard gate เพราะ agent ไม่ได้ถูกสอนให้รู้ quality score

5. `future_path_control`
   - คุณภาพตำแหน่งของ agent หลัง drop ที่ offsets 10, 25, 50 ticks
   - ใช้ถามว่า drop timing ดีกว่าการเดินต่อหรือไม่

## Quality Components

ต้องรายงานทั้ง total และ component:

- `quality_score_total`
- `moisture_fit`
- `light_fit`
- `nutrient_score`
- `danger_penalty`
- `temperature_penalty`

เหตุผล: `nutrient_score` มีแนวโน้ม saturate ใกล้ 1.0 จึงห้ามตีความ total quality ตัวเดียว

## Gate

หนึ่ง seed ผ่านเมื่อผ่านทุกข้อ:

1. `drop_quality_vs_current_position_lift > 1.10`
2. `drop_quality_vs_nearby_control_lift > 1.05`
3. `drop_quality_vs_visible_control_lift > 1.00`
4. `drop_quality_vs_future_path_control_lift > 1.00`
5. `high_quality_completed_chain_rate > low_quality_completed_chain_rate`
6. `late_vs_early_drop_quality_lift >= 1.05`

Condition ผ่านเมื่อ:

- อย่างน้อย 3/5 seeds ผ่านทุกข้อหลัก
- direction consistency อย่างน้อย 4/5 seeds

Direction consistency ต้องเป็น:

- drop quality > current-position control
- drop quality > nearby control
- drop quality > visible control
- drop quality > future-path control
- late quality > early quality

## Stress Tests

200x200 ยังเป็น blocker diagnosis ไม่ใช่ hard gate

ต้องแยก:

- `large_world_200x200_same_density_long_budget`
- `large_world_200x200_same_population_long_budget`

เพื่อแยกว่าปัญหาเกิดจาก world size, population density, resource density หรือ time budget

## Added Observability

Agent event logs เพิ่ม context:

- seed pick/drop instinct
- hunger/fear/cold/comfort/safety
- food_contact
- drop_chance
- seed pathway hotspots: pickup, drop, completed-chain pickup/drop

## Interpretation Rule

ถ้า random-world lift ผ่านแต่ current/visible/future controls ไม่ผ่าน ให้ตีความว่า evidence ยังไม่พอสำหรับ learned site selection

ถ้า visible-best control สูงกว่าจุด drop มาก ให้ตีความว่า agent ยังไม่ได้เลือกจุดดีที่สุดในพื้นที่ที่มันเข้าถึงได้ แม้จุด drop อาจดีกว่า average visible control

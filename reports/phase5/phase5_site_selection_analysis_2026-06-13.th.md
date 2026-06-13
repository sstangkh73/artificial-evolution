# รายงานวิเคราะห์ Phase 5: Seed Site Selection

วันที่: 2026-06-13
ข้อมูลรัน: `data\phase5_site_selection_confirm01_20260613`
รายงานตารางดิบ: `reports\phase5_site_selection_confirm01_2026-06-13.th.md`

## สรุปผล

Phase 5 ยังไม่ผ่าน core gate

ผล baseline 100x100 ได้ `passing_runs = 0/5` และ `direction_consistent_runs = 0/5` ในขณะที่เกณฑ์ผ่านต้องการอย่างน้อย `3/5` seeds ผ่านทุกข้อหลัก และทิศทางผลต้อง consistent อย่างน้อย `4/5` seeds

ข้อสรุปสำคัญคือ agent มีพฤติกรรมขยับ seed และสร้าง chain จาก seed ไป plant ไป fruit ไป agent ได้ต่อเนื่อง แต่ยังไม่มีหลักฐานพอว่า agent เลือก drop seed ในตำแหน่งที่ดีกว่าจุดที่มันถือ seed อยู่ก่อนหน้า

## Gate ที่ใช้

หนึ่ง seed จะผ่านเมื่อผ่านทุกข้อ:

1. `drop_quality_vs_current_position_lift > 1.10`
2. `drop_quality_vs_nearby_control_lift > 1.05`
3. `high_quality_chain_rate > low_quality_chain_rate`
4. `late_drop_quality / early_drop_quality >= 1.05`

ระดับ condition ผ่านเมื่อมี seed ผ่านอย่างน้อย 3/5 และมี directional consistency อย่างน้อย 4/5 seeds

200x200 ใช้เป็น stress test และ blocker diagnosis ไม่ใช่ hard gate ในรอบนี้

## ผลหลัก: baseline 100x100

Baseline เป็น core gate ของ Phase 5

- `passing_runs`: 0/5
- `direction_consistent_runs`: 0/5
- `mean_agent_moved_drop_count`: 141.4
- `mean_current_lift`: 0.99484
- `mean_nearby_lift`: 0.97946
- `mean_random_lift`: 1.03882
- `mean_high_quality_chain_rate`: 0.20878
- `mean_low_quality_chain_rate`: 0.12582
- `mean_late_vs_early_lift`: 1.04074

การอ่านผล:

- เมื่อเทียบกับ random-world control เหมือนจะดีขึ้นเล็กน้อย (`1.03882`) แต่ control นี้อ่อนกว่าที่เราต้องการ
- เมื่อเทียบกับ current-position control ผลกลับต่ำกว่า 1 (`0.99484`) หมายความว่าโดยเฉลี่ยจุดที่ drop ไม่ได้ดีกว่าจุดที่ agent ถือ seed อยู่ก่อนหน้า
- เมื่อเทียบกับ nearby control ผลยิ่งต่ำกว่า 1 (`0.97946`) หมายความว่าพื้นที่ใกล้ ๆ จุด drop มักดีกว่าหรือพอ ๆ กัน
- high-quality chain rate ดีกว่า low-quality chain rate ในภาพรวม แต่ยังไม่พอ เพราะตำแหน่งที่ drop เองยังไม่ชนะ current/nearby controls
- late vs early ดีขึ้นเล็กน้อย (`1.04074`) แต่ต่ำกว่าเกณฑ์ 5% และไม่ consistent พอ

## Quality components

Baseline 100x100 มีค่าเฉลี่ย component ของ drop site:

- `moisture_fit`: 0.25174
- `light_fit`: 0.54227
- `nutrient_score`: 0.99258
- `danger_penalty`: 0.08138
- `temperature_penalty`: 0.28869

จุดที่ต้องระวังคือ `nutrient_score` เกือบ saturate ใกล้ 1.0 แล้ว ทำให้ total quality อาจดูดีจาก nutrient อย่างเดียว ขณะที่ moisture, light และ temperature ยังเป็นตัวแยกคุณภาพจริงมากกว่า รอบถัดไปไม่ควรอ่าน total score เพียงค่าเดียว

## Low-food ablation

เงื่อนไข `low_food_signal_100x100` ลด food signal radius และ plant-lifecycle attraction weight

- `passing_runs`: 0/5
- `direction_consistent_runs`: 0/5
- `mean_current_lift`: 0.98802
- `mean_nearby_lift`: 0.98070
- `mean_high_quality_chain_rate`: 0.11711
- `mean_low_quality_chain_rate`: 0.17036
- `mean_late_vs_early_lift`: 1.09518

การอ่านผล:

พอเราลดแรงช่วยจาก food signal และ plant attraction แล้ว high-quality chain แพ้ low-quality chain โดยเฉลี่ย นี่เป็นสัญญาณว่า chain ที่เคยเกิดใน baseline อาจถูก ecology/attraction พาไปมากกว่าการเลือกพื้นที่อย่างมีนัยของ agent

## 200x200 stress diagnosis

### Same density, long budget

- `passing_runs`: 0/3
- `direction_consistent_runs`: 1/3
- `mean_agent_moved_drop_count`: 80.66667
- `mean_current_lift`: 1.00300
- `mean_nearby_lift`: 0.99690
- `mean_high_quality_chain_rate`: 0.10268
- `mean_low_quality_chain_rate`: 0.11579

แม้เพิ่ม food/seed capacity ตามพื้นที่และเพิ่มเวลาเป็น 180 วินาทีต่อ seed แต่จำนวน moved drops ลดจาก baseline 141.4 เหลือ 80.7 และ high-quality chain ไม่ชนะ low-quality chain โดยเฉลี่ย แปลว่าโลกใหญ่ทำให้ search/return/exploitation ยากขึ้นจริง

### Same population/resource count, long budget

- `passing_runs`: 0/3
- `direction_consistent_runs`: 0/3
- `mean_agent_moved_drop_count`: 20.66667
- `mean_current_lift`: 0.98880
- `mean_nearby_lift`: 1.00010
- `mean_high_quality_chain_rate`: 0.16667
- `mean_low_quality_chain_rate`: 0.03704
- `mean_late_vs_early_lift`: 0.89630

เมื่อโลกใหญ่ขึ้นแต่ population และ resource count เท่าเดิม จำนวน moved drops ลดแรงมาก เหลือเฉลี่ย 20.7 เท่านั้น สรุปได้ว่าปัญหาใน 200x200 ไม่ใช่เวลาอย่างเดียว แต่รวมถึง density และการค้นพบพื้นที่สำคัญด้วย

## สิ่งที่ Phase 5 พิสูจน์แล้ว

1. current-position control จำเป็นมาก เพราะมันทำให้เรารู้ว่า random-world lift ที่ดูดีไม่พอใช้เป็นหลักฐาน learning
2. agent ขยับ seed จริง แต่ยังไม่แสดงว่าขยับไปจุดที่ดีกว่าจุดตั้งต้น
3. chain seed -> plant -> fruit -> agent ยังเกิดจริง แต่ chain success ยังอาจถูกผลักโดย ecology/food attraction
4. 200x200 แยกปัญหาได้ว่า same-density ยังพอมี activity แต่ same-population activity หายแรง
5. total quality ต้องถูกอ่านคู่กับ component เพราะ nutrient saturation ทำให้ตีความเกินได้ง่าย

## ข้อสรุปเชิงวิจัย

ตอนนี้ระบบยังอยู่ที่ระดับ ecological interaction ไม่ใช่ demonstrated learned site selection

พูดให้ตรงคือ agent ยังเหมือนกำลัง "พา seed ไปมาในระบบที่มีแรงดึงและทรัพยากร" มากกว่ากำลัง "เลือกพื้นที่ปลูกที่ดีขึ้นจากประสบการณ์" หลักฐานที่ทำให้ไม่ผ่านคือ drop site ไม่ชนะ current-position control และ nearby control

## งานถัดไปที่ควรทำ

1. ทำ perception-matched control: control ต้องใช้เฉพาะข้อมูลที่ agent มองเห็นได้ ไม่ใช่ observer score ทั้งโลก
2. ลด nutrient saturation หรือปรับ weight เพื่อให้ moisture/light/temperature มีอำนาจแยก site quality มากขึ้น
3. เพิ่ม counterfactual carry test: ถ้า agent ไม่ drop ตอนนั้น แล้วเดินต่ออีก N ticks คุณภาพจุดที่เจอหลังจากนั้นดีกว่าหรือแย่กว่า
4. แยก seed handling policy ออกจาก food seeking ให้ชัดขึ้น โดยยังไม่สอนวิธีปลูก แต่ลดการที่ hunger/food attraction บังพฤติกรรม seed
5. เพิ่ม spatial return metrics: วัดว่า agent กลับมายังโซน seed/fruit เดิมเองหรือถูก food signal พากลับ
6. สำหรับ 200x200 ให้ทดสอบ population scaling แยกจาก density scaling เช่น 50, 100, 200 agents บน density เดิม

## Verdict

Phase 5 ไม่ผ่าน แต่เป็น failure ที่ดี เพราะ control ใหม่ปิดช่องตีความเกินได้สำเร็จ และบอกทิศทางชัดว่าต้องแก้เรื่อง site-quality signal, perception-matched controls, density/population scaling และการแยกแรงดึงอาหารออกจากพฤติกรรม seed placement

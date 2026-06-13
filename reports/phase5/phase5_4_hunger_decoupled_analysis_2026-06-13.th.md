# Analysis: Phase 5.4 Hunger-Decoupled Seed Handling

วันที่: 2026-06-13

ชุดรัน: `data\phase5_4_hunger_decoupled_confirm01_20260613`

รายงานดิบ: `reports\phase5_4_hunger_decoupled_confirm01_2026-06-13.th.md`

## Abstract

Phase 5.4 ทดสอบว่า seed placement signal ที่เห็นใน Phase 5 ถูก hunger/food loop ครอบอยู่หรือไม่ โดยเพิ่มตัวแปร `seed_hunger_drop_bonus` เพื่อปิด bonus การ drop seed ตอนหิว และเพิ่ม context-matched metrics เพื่อแยก drop ที่เกิดใน `hunger`, `food_contact`, และ `balanced_random`

ผลจริง: Phase 5.4 ไม่ผ่าน เป้าหมายการแยก hunger ไม่สำเร็จ เพราะ hunger-neutral condition ยังมี hunger-context fraction สูงกว่า baseline เล็กน้อย (`0.98168` vs `0.97644`) และไม่มี seed ใดผ่าน site-selection gate (`0/5`) ทั้ง baseline, hunger-neutral, และ low-food-signal

ข้อสรุปหลัก: ปัญหาไม่ได้อยู่แค่ `+0.06` hunger drop bonus แต่ดูเหมือน seed handling ทั้งวงจรยังเกิดระหว่าง agent อยู่ใน hunger state เป็นหลัก

## Methods

รัน 3 conditions, condition ละ 5 seeds, seed ละ 90 วินาที:

| condition | key change | runs |
| --- | --- | ---: |
| `baseline_100x100` | ค่า Phase 5 เดิม, `seed_hunger_drop_bonus=0.06` | 5 |
| `hunger_neutral_seed_drop_100x100` | ปิด hunger drop bonus, `seed_hunger_drop_bonus=0.0` | 5 |
| `low_food_signal_100x100` | ลด food signal radius/weight, คง hunger drop bonus | 5 |

Success criteria หลักของ Phase 5.4:

- hunger-neutral activity ไม่ collapse: mean moved drops >= 50
- hunger-neutral hunger fraction ต้องต่ำกว่า baseline
- อย่างน้อย 3/5 seeds ต้องผ่าน site-selection gate
- directional consistency อย่างน้อย 4/5 seeds

## Results

| condition | pass seeds | direction seeds | moved drops | hunger frac | current | nearby | visible | future | high chain | low chain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_100x100` | 0/5 | 0/5 | 79.8 | 0.97644 | 1.00822 | 0.98952 | 0.98706 | 1.16066 | 0.15776 | 0.21370 |
| `hunger_neutral_seed_drop_100x100` | 0/5 | 0/5 | 101.8 | 0.98168 | 0.98850 | 0.97432 | 0.97186 | 1.12170 | 0.11901 | 0.15564 |
| `low_food_signal_100x100` | 0/5 | 0/5 | 74.0 | 0.98244 | 0.99574 | 0.99492 | 0.99348 | 1.09692 | 0.04750 | 0.22141 |

Food-chain activity เกิดจริง:

| condition | total plant food consumed | mean plant food consumed | mean completed moved-seed chains |
| --- | ---: | ---: | ---: |
| `baseline_100x100` | 1187 | 237.4 | 12.8 |
| `hunger_neutral_seed_drop_100x100` | 1717 | 343.4 | 12.6 |
| `low_food_signal_100x100` | 1048 | 209.6 | 9.0 |

Context-matched metrics:

| condition | hunger current | hunger visible | hunger future | hunger chain |
| --- | ---: | ---: | ---: | ---: |
| `baseline_100x100` | 1.00918 | 0.98770 | 1.15986 | 0.15590 |
| `hunger_neutral_seed_drop_100x100` | 0.98972 | 0.97298 | 1.12026 | 0.12884 |
| `low_food_signal_100x100` | 0.99652 | 0.99464 | 1.09650 | 0.12760 |

## Evidence Supporting

- มี seed -> plant -> fruit -> agent chain จริง เพราะ plant food consumed สูงทุก condition และ moved-seed completed chains เฉลี่ยมากกว่า 9 ต่อ run
- Future-path lift สูงทุก condition (`1.09692` ถึง `1.16066`) แปลว่าจุด drop มักดีกว่าจุดที่ agent เดินต่อไปภายหลัง
- Hunger-neutral ไม่ทำให้ activity collapse; moved drops กลับเพิ่มจาก 79.8 เป็น 101.8

## Evidence Against

- Phase 5.4 ไม่ผ่าน: `phase5_4_hunger_decoupling.pass = false`
- Hunger dominance ไม่ลดลงหลังปิด hunger bonus; เพิ่มจาก `0.97644` เป็น `0.98168`
- ไม่มี condition ใดมี passing seed (`0/5` ทั้งหมด)
- Current/nearby/visible controls ไม่ผ่าน threshold:
  - hunger-neutral current = `0.98850`
  - hunger-neutral nearby = `0.97432`
  - hunger-neutral visible = `0.97186`
- High-quality chain rate ไม่ชนะ low-quality chain rate ในค่าเฉลี่ย:
  - baseline: `0.15776 < 0.21370`
  - hunger-neutral: `0.11901 < 0.15564`
  - low-food-signal: `0.04750 < 0.22141`

## Alternative Explanations

1. `seed_hunger_drop_bonus` ไม่ใช่ตัวครอบหลัก ตัวครอบหลักอาจเป็น movement policy ที่ถูก hunger state คุมอยู่แล้ว
2. Agent อาจไม่ได้เลือกจุด drop แต่ drop ระหว่างเดินหาอาหาร ทำให้ future-path lift สูงเพราะทางเดินหลังจากนั้นแย่ลง ไม่ใช่เพราะจุด drop ดีขึ้น
3. Quality score อาจยังไม่ตรงกับ ecological payoff จริงทั้งหมด แม้ตอนนี้แยก moisture/light/nutrient/danger/temperature แล้ว
4. Nutrient score ใกล้ saturation ในหลาย run จึงอาจทำให้ total quality แยกความต่างพื้นที่ไม่คมพอ

## Missing Evidence

- ยังไม่มี ablation ที่แยก hunger state จาก seed action อย่างแท้จริง เช่น seed-drop cooldown หลังหิวจัด หรือ decision window ตอน balanced/safe
- ยังไม่มี memory-disabled / reward-shuffled ablation เพื่อดูว่า reward memory มีผลจริงไหม
- ยังไม่มี control ที่เปรียบเทียบ "ตำแหน่งก่อนถือ seed" กับ "ตำแหน่ง drop" เฉพาะเวลาที่ agent ไม่ได้อยู่ใน hunger state เพราะตัวอย่าง non-hunger น้อยมาก
- ยังไม่ได้รัน 200x200 stress test ใน Phase 5.4 รอบนี้ เพราะเป้าหมายหลักคือแยก hunger coupling บน 100x100 ก่อน

## Confidence Level

Medium-high ต่อข้อสรุปว่า current mechanism ยังไม่ใช่ site selection/farming ที่น่าเชื่อถือ

Medium ต่อข้อสรุปว่า hunger state ครอบ seed handling เพราะ context fraction สูงสม่ำเสมอ แต่ยังต้องมี ablation ที่ตัด hunger state ออกจาก action window โดยตรงเพื่อยืนยันกลไก

## Verdict

Phase 5.4 fail แต่เป็น fail ที่มีค่า: เราพิสูจน์ได้ว่าแค่ปิด hunger drop bonus ไม่พอ และสัญญาณ future-path lift ไม่ควรถูกตีความว่าเป็นการเลือกที่ปลูก

สถานะงานวิจัยตอนนี้:

- ระบบ ecology chain ทำงานแล้ว
- agent สามารถพา seed จนเกิด plant/fruit/food-consumption chain ได้
- ยังไม่มีหลักฐานพอว่า agent เลือก drop seed ในตำแหน่งที่ดีกว่าจุดที่มันถือ seed อยู่ หรือดีกว่าพื้นที่ที่เห็นรอบตัว
- เฟสถัดไปควรแก้โจทย์ "แยก seed behavior ออกจาก hunger state" ไม่ใช่เพิ่มฟิสิกส์หรือเพิ่มอาหารก่อน

## Recommended Next Phase

Phase 5.5 ควรทำ `state-decoupled seed handling`:

1. เพิ่ม metric action-window: แยก seed pickup/drop ตาม instinct state ก่อน/หลังหิว
2. เพิ่ม condition ที่อนุญาตให้ seed drop เกิดเฉพาะตอนไม่ critical hunger เพื่อดูว่า signal หายหรือดีขึ้น
3. เพิ่ม "carry-to-safe-window" control: วัดคุณภาพจุดที่ agent ถือ seed ตอน hunger ลดลงเทียบกับจุด drop
4. เพิ่ม no-reward-memory และ shuffled-reward-memory ablation
5. success gate ยังต้องยึด current_position_control เป็นหลัก และห้ามผ่านด้วย future-path lift อย่างเดียว

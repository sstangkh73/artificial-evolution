# เฟส 0: แผนที่การเข้าถึงข้อมูล (Information-access map)

จัดทำ: 14 ต.ค. 2569

## 1. ระบบเดิม (`agents/agent.py` + `world/environment.py`)

ข้อมูลที่เอเจนต์ในระบบเดิมอ่านจากโลก (นับจำนวนครั้งที่เรียกใน `agents/agent.py`)

| กลุ่ม | ตัวอย่างเมธอด | ประเภท |
|---|---|---|
| การรับรู้เฉพาะที่ | `get_danger_level` (ช่องรอบตัว), `food_signal_at`, `animal_signal_at`, `get_cell_temperature`, `get_cell_moisture`, `food_positions.get((x, y))` (เฉพาะช่องที่ยืนอยู่) | ✅ สังเกตได้จริง |
| **คะแนนประโยชน์ของวัตถุ** | **`score_object_for_action` 3 จุด** (`agent.py:2042`, `2051`, `2063`) | ❌ **oracle**: เอเจนต์อ่านสูตรฟิสิกส์ของโลกโดยตรงเพื่อเลือกวัตถุ |
| การหาเป้าหมายระยะไกล | `find_nearest_safe_area` (ปิดอยู่ ถ้าไม่เปิด `legacy_oracle_perception_enabled`), `find_nearest_large_animal` (จำกัดระยะ `engage_range`) | ⚠️ เดิมเป็น oracle แต่ถูกปิดหรือจำกัดระยะแล้วตาม patch 2026-06-10 |
| ระบบรัง / เตา / บทบาท | `get_nest_materials`, `consume_nest_materials`, `create_experimental_object`, `get_nest_hearth_intensity` | ⚠️ scaffold: การทดลองสร้างวัตถุทำงานเฉพาะเมื่อเปิด `scaffolded_agent_actions_enabled` |

ข้อสรุปของระบบเดิม
1. การเลือกวัตถุใช้ oracle (`_best_available_object` → `score_object_for_action`) ระบบเดิมจึงเท่ากับเงื่อนไข **C3**
2. การเลือกส่วนผสมเป็น if-rule ตามค่า `crafting_skill`, `hunt_drive` และค่าอื่น ๆ (`_choose_experiment_mix`, `agent.py:2698`) ไม่ได้มาจากประสบการณ์
3. การสร้างวัตถุผูกกับรัง เตา บทบาท และคลังอาหาร ซึ่งเป็นตัวแปรกวนของคำถามวิจัย

## 2. สนามทดลองใหม่ (`simulation/tool_discovery.py`)

ใช้ `Environment` เดิมเป็นความจริงของโลกโดยไม่แก้โค้ดโลก ได้แก่ การหาวัสดุ (`forage_materials`), ฟิสิกส์ของวัตถุ (`create_experimental_object`) และผลของการใช้ (`score_object_for_action`)

| ข้อมูล | C0 | C1 / C2 | C4 | C3 |
|---|---|---|---|---|
| บริบทอาหารตรงหน้า (พืช / สัตว์ / ใต้ดิน) | ✅ | ✅ | ✅ | ✅ |
| สมบัติวัตถุที่มองเห็น (มวล ความคม ความแข็ง ความยาว ความยืดหยุ่น ความทนทาน การพกพา) | ✅ | ✅ | ✅ | ✅ |
| รหัสวัตถุ จำนวนครั้งที่ใช้ วัสดุในมือ พลังงานตัวเอง | ✅ | ✅ | ✅ | ✅ |
| ผลจริงหลังการใช้ (อาหาร − แรงที่ใช้) | ไม่จำ | ✅ (C2 ได้ผลที่สลับมา) | ✅ | — |
| สูตรคะแนน, เกณฑ์ (threshold), ผลตอบแทน | ❌ | ❌ | ❌ | ✅ ผ่าน `OracleView` เท่านั้น |
| ชื่อเครื่องมือ / สูตรการสร้าง | ❌ ไม่มีในระบบ | ❌ | ❌ | ❌ |

การกระทำมีเฉพาะการกระทำทางกายภาพพื้นฐาน (`cut`, `pierce`, `hit`, `throw`, `dig`) ไม่มีการกระทำชื่อ "สร้างหอก" หรือ "สร้างมีด"

## 3. หลักฐานอัตโนมัติ (`tests/test_tool_discovery.py`)
- `test_non_oracle_policies_never_read_utility`: ถ้า policy ของ C0/C1/C2/C4 เรียก `score_object_for_action` ระหว่างตัดสินใจ เทสต์จะล้มทันที
- `test_utility_guard_catches_the_oracle`: เทสต์ควบคุม guard ตัวเดียวกันต้องจับ C3 ได้ เพื่อยืนยันว่า guard ทำงานจริง
- `test_non_oracle_policies_hold_no_world_reference`: policy ที่ไม่ใช่ oracle ไม่มีตัวแปรที่อ้างถึงโลก
- `test_observation_contains_no_utility_fields`: observation มีเฉพาะฟิลด์ที่อนุญาต

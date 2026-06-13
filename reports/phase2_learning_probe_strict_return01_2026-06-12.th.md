# รายงาน Phase 2: Reward-Place Learning Probe

วันที่รัน: 2026-06-12
ชุดข้อมูล: `data/phase2_learning_strict_return01_20260612`

## คำตัดสิน

ผ่าน Phase 2 แบบ strict-return: 3/3 seeds ผ่านเกณฑ์

เกณฑ์รอบนี้เข้มกว่า baseline แรก เพราะไม่นับแค่ agent ยังอยู่ใกล้จุดอาหารหลัง delay แต่ต้องเกิดลำดับ:

1. agent กินอาหารจาก `plant_lifecycle`
2. agent ออกจากรัศมีตำแหน่งรางวัล
3. agent กลับเข้ามาใกล้ตำแหน่งเดิมภายหลัง
4. อัตรากลับมาสูงกว่า random-position baseline

## Before / After

ก่อนเพิ่ม Phase 2 telemetry:

- เรารู้ว่า seed -> plant -> fruit -> agent เกิดได้แล้ว
- เรายังแยกไม่ได้ว่า agent เรียนรู้ตำแหน่งแหล่งอาหาร หรือแค่บังเอิญเดินผ่าน/วนค้างใกล้จุดเดิม

หลังเพิ่ม Phase 2 telemetry:

- watcher บันทึก plant-food reward ต่อ agent
- วัด same-agent revisit หลัง delay
- วัด strict left-then-return
- คำนวณ lift เทียบกับ random baseline
- เพิ่ม runner สำหรับรันซ้ำหลาย seed และตัดสิน gate อัตโนมัติ

ไม่มีการเพิ่ม policy หรือ instruction ใหม่ให้ agent ในรอบ strict-return นี้ เพราะ baseline ผ่านด้วย memory/instinct ที่มีอยู่แล้ว

## Experiment Setup

- agents เริ่มต้น: 50
- immortal: true
- world: 100 x 100
- time limit: 60 วินาทีต่อ seed
- seeds: 20260610, 20260611, 20260612
- natural seed rain: 0
- ecology config: ใช้ค่าที่ผ่าน Phase 1 ecology gate
- reward radius: 4 cells
- min delay: 20 ticks
- max reward age: 2000 ticks

## Success Criteria

ต่อ run ต้องผ่านทั้งหมด:

- `plant_matured >= 1`
- `plant_fruited >= 1`
- `plant_lifecycle_food_consumed >= 5`
- `owner_returned_reward_events >= 5`
- `owner_return_agents >= 2`
- `owner_return_lift >= 2.0`

ทั้งชุดต้องผ่านอย่างน้อย 3 runs

## Results

| seed | pass | plant food consumed | returned rewards | return agents | return lift | first return tick |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 20260610 | true | 105 | 82 | 31 | 52.715 | 806 |
| 20260611 | true | 84 | 65 | 24 | 38.694 | 485 |
| 20260612 | true | 131 | 93 | 37 | 33.699 | 754 |

Aggregate:

- mean plant food consumed: 106.6667
- mean owner returned rewards: 80.0
- mean owner return agents: 30.6667
- mean owner return lift: 41.7027

## Interpretation

ผลนี้สนับสนุนว่า Phase 2 ผ่านในความหมายแคบ: agent ที่ได้พลังงานจากผลไม้ของวงจรพืช สามารถออกจากพื้นที่แล้วกลับมาใกล้ตำแหน่งรางวัลเดิมในอัตราที่สูงกว่า random baseline มาก

นี่เป็นสัญญาณ reward-place learning / foraging memory ไม่ใช่หลักฐานว่า agent เข้าใจ farming, seed causality, ภาษา, หรือการวางแผนเพาะปลูก

## Evidence Against / Limitations

- random baseline ตอนนี้เป็น uniform-position baseline ยังไม่ใช่ memory-disabled control
- strict return ลดปัญหา “ยืนค้างใกล้อาหาร” แล้ว แต่ยังอาจมีตัวดึงร่วม เช่น hunger, terrain, social clustering, หรือ food density
- agent เป็นอมตะ จึงยังไม่มี selection pressure จากการตาย
- ยังไม่มีหลักฐานว่า agent รู้ว่า seed ทำให้เกิด plant หรือ plant ทำให้เกิด fruit

## Next Recommended Gate

Phase 3 ควรวัด causal manipulation:

- seed ถูกหยิบ/ย้ายไปไหนบ่อย
- seed ที่ agent เคลื่อนย้ายงอกเป็น plant มากกว่าพื้นที่สุ่มหรือไม่
- plant/fruit cluster เกิดใกล้พื้นที่ที่ agent กลับมาบ่อยหรือไม่
- memory-disabled หรือ shuffled-reward-label control เพื่อตัด alternative explanation

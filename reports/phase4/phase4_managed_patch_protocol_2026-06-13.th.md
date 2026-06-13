# Phase 4 Protocol: Managed Patch / Proto-Farm Gate

วันที่จัดทำ: 2026-06-13
พื้นที่ทดลอง: `C:\artificial-evolution`

## Abstract

Phase 4 ทดสอบว่าหลังจาก Phase 3 พิสูจน์แล้วว่าเมล็ดที่ agent ย้ายสามารถเข้าสู่วงจร `seed -> plant -> fruit -> consumed` ได้จริง agent จะเริ่มทำให้เกิดพื้นที่ผลิตอาหารซ้ำหรือไม่

คำถามหลักไม่ใช่แค่เมล็ดงอก แต่คือ agent ทิ้งเมล็ดซ้ำในบริเวณเดียวกัน แล้วพื้นที่นั้นให้ผลผลิตและถูกกลับมาใช้ซ้ำมากกว่า control หรือไม่

## Research Question

> agent เริ่มสร้างหรือใช้ประโยชน์จาก managed patch / proto-farm ผ่านการย้ายเมล็ดซ้ำ โดยไม่ได้รับคำสั่งหรือความรู้เรื่อง farming หรือไม่

## Hypotheses

- H4-A: agent-moved seeds จะเกิด repeated-drop patch มากกว่าความบังเอิญ
- H4-B: repeated-drop patch จะมี completed seed chains มากกว่า matched control
- H4-C: agent หรือกลุ่ม agent เดิมจะกลับมา patch หลัง drop มากกว่า random/control
- H4-D: ถ้ามี proto-farming substrate จริง ควรเห็น completed chains หลายเส้นใน patch เดียว ไม่ใช่ seed เดียวที่ฟลุคสำเร็จ

## Independent Variables

- random seed ของ simulation
- patch radius
- minimum seed move distance
- ecology parameters ที่ผ่าน Phase 1-3
- run time limit

## Dependent Variables

- repeated-drop patch count
- moved-seed drops per patch
- completed seed chains per patch
- plant/fruit/food-consumed events within patch
- patch return events after first drop
- patch productivity lift vs matched control
- patch return lift vs random baseline

## Control Variables

- world size: `100x100`
- initial population: `50`
- immortal agents: `true`
- natural seed rain: `0`
- ecology config: ใช้ config ที่ผ่าน Phase 1-3
- no farming instruction
- no oracle site selection
- scaffolded managed-food actions must not be used as evidence

## Patch Definition

Phase 4 ใช้ patch แบบ Manhattan radius:

```text
patch center = seed drop cluster center
patch radius = 4 cells
repeated-drop patch = agent-moved seeds >= 3 within radius
```

Patch ที่ผ่าน candidate ต้องมี:

- agent-moved seed drops อย่างน้อย 3 ครั้งในรัศมีเดียวกัน
- completed moved-seed chains อย่างน้อย 1 chain ใน patch
- return หลัง drop อย่างน้อย 1 ครั้ง
- ไม่มี evidence จาก `tend_food_patch` หรือ `food_patch_tended` เป็นตัวทำให้ผ่าน

## Metrics

- `repeated_drop_patch_count`
- `max_patch_moved_seed_drops`
- `max_patch_completed_chains`
- `patch_completed_seed_chains`
- `patch_food_consumed`
- `patch_return_events_after_drop`
- `patch_return_agents`
- `same_agent_patch_food_chains`
- `patch_productivity_lift_vs_matched_control`
- `patch_return_lift_vs_random_control`
- `contamination_events`

## Success Criteria

ต่อ run:

- `repeated_drop_patch_count >= 1`
- `patch_completed_seed_chains >= 3`
- `patch_food_consumed >= 3`
- `patch_return_agents >= 2`
- `patch_productivity_lift_vs_matched_control >= 1.25`
- `patch_return_lift_vs_random_control >= 2.0`
- `contamination_events == 0`

ทั้งชุด confirm:

- อย่างน้อย `3/5 seeds` ผ่าน

## Failure Criteria

ถือว่า Phase 4 ยังไม่ผ่านถ้า:

- ไม่มี repeated-drop patch
- มี seed chains แต่กระจาย ไม่รวมเป็น patch
- patch มีผลผลิตแต่ไม่ได้สูงกว่า matched control
- agent ไม่กลับ patch หลัง drop
- evidence หลักปนกับ scaffolded action เช่น `tend_food_patch`

## Interpretation Rules

ถ้าผ่าน:

> เรียกว่า managed patch / proto-farm evidence ได้ แต่ยังไม่ใช่หลักฐานว่า agent เข้าใจ farming แบบมี concept

ถ้าไม่ผ่าน:

> Phase 3 ยังยืนอยู่ แต่ Phase 4 ชี้ว่า seed causality ยังไม่พัฒนาเป็น repeated area management

## Planned Output

- data: `data/phase4_managed_patch_*`
- run logs: `data/phase4_managed_patch_*/runs`
- summary: `data/phase4_managed_patch_*/summary.json`
- report: `reports/phase4_managed_patch_*_2026-06-13.th.md`

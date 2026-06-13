# รายงานผลสำเร็จ Phase 1-3: Artificial Evolution / World-First AI Learning

วันที่จัดทำ: 2026-06-13
พื้นที่ทดลอง: `C:\artificial-evolution`
ชุดข้อมูลหลัก:

- Phase 1: `data/phase1_5_confirm03_20260612`
- Phase 2: `data/phase2_learning_strict_return01_20260612`
- Phase 3: `data/phase3_seed_causality_confirm01_20260613`

## Abstract

งานทดลองนี้มีเป้าหมายศึกษาว่า ถ้า agent เริ่มต้นในโลกจำลองที่ไม่ได้สอนความหมายของการทำรัง ทำฟาร์ม หรือการใช้เมล็ด agent จะเรียนรู้อะไรได้จากสภาพแวดล้อมจริงของโลกนั้น

ผลถึงปัจจุบันแบ่งเป็น 3 ก้าวสำคัญ:

1. Phase 1 พิสูจน์ว่า ecology substrate เสถียรพอให้เกิดวงจร `seed -> plant -> fruit -> agent`
2. Phase 2 พิสูจน์ว่า agent มี reward-place learning คือกินผลไม้จากวงจรพืชแล้วออกจากพื้นที่ ก่อนกลับมาใกล้ตำแหน่งรางวัลเดิมสูงกว่า random baseline
3. Phase 3 พิสูจน์ว่าเมล็ดที่ agent เคลื่อนย้ายสามารถเข้าสู่วงจร `seed -> plant -> fruit -> consumed` ได้จริง และมี completed-chain rate สูงกว่า control ในทุก seed ที่ยืนยัน

ยังไม่ควรอ้างว่า agent เข้าใจการเพาะปลูก ตั้งใจทำฟาร์ม มีภาษา หรือมีการสื่อสารเชิงสัญลักษณ์ ผลปัจจุบันควรเรียกว่า proto-farming substrate และ early causal participation ในวงจรพืช

## Research Question

คำถามหลัก:

> ถ้า agent ไม่ได้รับความรู้จากโลกจริง ไม่ถูกสอนวิธีปลูกพืชหรือทำฟาร์ม แต่ถูกวางไว้ในโลกที่มีฟิสิกส์และชีววิทยาพื้นฐาน agent จะค้นพบความสัมพันธ์ระหว่างอาหาร ตำแหน่ง เมล็ด และพืชได้หรือไม่

คำถามย่อยตามเฟซ:

- Phase 1: โลกจำลองสร้างวงจรพืชที่เสถียรพอให้ agent ได้กินผลไม้จากพืชได้หรือไม่
- Phase 2: agent กลับไปยังตำแหน่งที่เคยได้อาหารจากพืชมากกว่าความบังเอิญหรือไม่
- Phase 3: เมล็ดที่ agent เคลื่อนย้ายสามารถกลายเป็นพืช ออกผล และถูกกินในภายหลังได้จริงหรือไม่

## Method Summary

ทุกเฟซใช้ world config หลักที่ผ่านการ tune สำหรับโลกขนาด `100x100`:

```text
width=100
height=100
initial_population=50
immortal=true
natural_seed_rain_per_tick=0
max_food=2000
max_plant_seeds=7600
plant_seed_max_age_multiplier=4.0
plant_growth_rate_multiplier=2.0
sprout_biomass_loss_multiplier=0.1
germination_good_ticks_multiplier=0.5
plant_fruiting_interval_multiplier=0.25
plant_fruiting_growth_threshold_multiplier=0.5
plant_fruiting_chance_multiplier=2.0
natural_seed_drop_chance_multiplier=2.0
plant_food_decay_chance=0.0015
```

ข้อสำคัญ:

- ไม่มี natural seed rain ในชุดผ่านหลัก
- agent เป็น immortal เพื่อลดปัญหาตายหมดก่อนเกิดวงจรทดลอง
- ไม่ได้สั่ง agent ว่า seed ใช้ปลูกได้
- ไม่ได้สั่ง agent ให้ทำฟาร์ม
- ไม่ได้ใส่ oracle ว่าพื้นที่ไหนควรปลูก

## Phase 1: Ecology Gate

### เป้าหมาย

พิสูจน์ว่าโลกจำลองสามารถสร้างวงจรพืชพื้นฐานได้เอง:

```text
seed
-> germination
-> mature plant
-> fruit
-> plant-lifecycle food
-> consumed by agent or decayed
```

### เกณฑ์ผ่าน

- โลกขนาด `100x100`
- `natural_seed_rain=0`
- `plant_matured > 0` ในอย่างน้อย 70% ของ seeds
- `plant_fruited > 0` ในอย่างน้อย 70% ของ seeds
- plant-lifecycle food ต้องมี observed fate โดยเฉพาะถูก agent กิน

### ผลลัพธ์

Phase 1 ผ่าน 5/5 seeds

| Metric | Result |
| --- | ---: |
| matured runs | 5/5 |
| fruited runs | 5/5 |
| plant food consumed runs | 5/5 |
| mean seed germinated | 139.0 |
| mean plant matured | 33.6 |
| mean plant fruited | 68.6 |
| mean plant food consumed | 47.8 |
| mean seed-to-germinated rate | 0.5567 |
| mean germinated-to-matured rate | 0.2496 |
| mean matured-to-fruited event rate | 1.9888 |
| mean hunger level | 0.983 |

Per-seed fruit and consumption:

| seed | plant_fruited | plant_lifecycle_food_consumed |
| --- | ---: | ---: |
| 20260610 | 41 | 33 |
| 20260611 | 48 | 33 |
| 20260612 | 67 | 52 |
| 20260613 | 49 | 44 |
| 20260614 | 138 | 77 |

### Interpretation

Phase 1 สำเร็จเพราะโลกมี biological substrate ที่เสถียรพอให้เกิดอาหารจากพืชโดยไม่ต้องใช้ natural seed rain และโดยไม่สอน agent ให้ทำฟาร์ม

นี่ไม่ใช่หลักฐานการเรียนรู้ของ agent แต่เป็นก้าวจำเป็นก่อนทดสอบการเรียนรู้ เพราะถ้าโลกไม่มีวงจรพืชที่เสถียร agent ก็ไม่มี signal ให้เรียนรู้

### จุดเปลี่ยนสำคัญ

ก่อน tune โลกเกิด seed และ sprout ได้ แต่ mature/fruit ยังไม่เสถียร ปัญหาหลักคือ timing gate:

- seed viability สั้นเกินไปในโลกใหญ่
- sprout biomass loss สูงเกินไป
- mature plants ออกผลยากเกินไปภายในเวลารัน

หลังปรับ seed age, growth, sprout loss, germination ticks, fruiting interval, fruiting threshold และ fruiting chance วงจรพืชจึงเสถียร

## Phase 2: Reward-Place Learning

### เป้าหมาย

พิสูจน์ว่า agent ไม่ได้แค่บังเอิญกินผลไม้ แต่สามารถกลับไปใกล้ตำแหน่งที่เคยได้รางวัลจาก plant-lifecycle food หลังจากออกจากพื้นที่แล้ว

ลำดับที่วัด:

```text
agent consumes plant-lifecycle food
-> agent leaves reward radius
-> agent later returns near that rewarded location
-> return rate is higher than random-position baseline
```

### เกณฑ์ผ่าน

ต่อ run ต้องมี:

- `plant_matured >= 1`
- `plant_fruited >= 1`
- `plant_lifecycle_food_consumed >= 5`
- `owner_returned_reward_events >= 5`
- `owner_return_agents >= 2`
- `owner_return_lift >= 2.0`

ทั้งชุดต้องผ่าน 3/3 seeds

### ผลลัพธ์

Phase 2 ผ่าน 3/3 seeds

| seed | consumed | returned rewards | return agents | return lift | first return tick |
| --- | ---: | ---: | ---: | ---: | ---: |
| 20260610 | 105 | 82 | 31 | 52.715 | 806 |
| 20260611 | 84 | 65 | 24 | 38.694 | 485 |
| 20260612 | 131 | 93 | 37 | 33.699 | 754 |

Aggregate:

| Metric | Result |
| --- | ---: |
| mean plant food consumed | 106.6667 |
| mean owner returned rewards | 80.0 |
| mean owner return agents | 30.6667 |
| mean owner return lift | 41.7027 |

### Interpretation

Phase 2 สนับสนุนว่า agent มี reward-place learning หรือ foraging memory

agent ที่กินอาหารจากพืชไม่ได้แค่ยืนค้างอยู่แถวเดิม แต่ใน strict-return metric ต้องออกจากรัศมีก่อน แล้วกลับมาใกล้ตำแหน่งเดิมภายหลัง ผล return lift สูงกว่า random baseline มากในทุก seed

### สิ่งที่ยังอ้างไม่ได้

Phase 2 ยังไม่ใช่ farming เพราะยังไม่ได้พิสูจน์ว่า agent แตะเมล็ด ย้ายเมล็ด หรือสร้างสาเหตุให้พืชเกิดใหม่

สิ่งที่อ้างได้คือ:

- agent จำตำแหน่งรางวัลจากพืชได้
- agent กลับไปยังแหล่งอาหารเดิมมากกว่าความบังเอิญ

สิ่งที่ยังอ้างไม่ได้คือ:

- agent เข้าใจ seed
- agent ตั้งใจปลูก
- agent มีภาษา
- agent สื่อสารเรื่องอาหารหรือพื้นที่

## Phase 3: Seed Causality / Proto-Farming Substrate

### เป้าหมาย

พิสูจน์ว่า agent-displaced seeds สามารถเข้าสู่วงจรพืชจริง:

```text
agent picks seed
-> agent drops seed elsewhere
-> seed germinates
-> plant matures
-> plant fruits
-> plant-lifecycle food is consumed
```

### Baseline ก่อนแก้

ก่อนแก้กลไก seed primitive:

| Metric | Result |
| --- | ---: |
| plant_food_consumed | 191 |
| seed_picked | 0 |
| seed_dropped | 0 |
| agent_moved_seed_count | 0 |
| agent_moved_seed_completed_chains | 0 |

แปลว่าโลกมีวงจรพืชแล้ว แต่ agent ยังไม่เคยเข้าสายเหตุผลของเมล็ด

probe หลังเรียก seed primitive หลัง consume แต่ยังไม่แก้ energy gate:

| Metric | Result |
| --- | ---: |
| plant_food_consumed | 575 |
| seed_picked | 0 |
| seed_dropped | 0 |

ข้อสรุป: agent อยู่ใน hunger pressure สูงมาก ทำให้ seed primitive ถูก energy gate กันออก แม้มีเมล็ดตกที่ตำแหน่งเดียวกับการกินอาหาร

### Change

แก้เฉพาะ substrate-level seed handling:

- หลัง agent กินอาหาร ให้ seed primitive ทำงานด้วย `food_contact=True`
- ถ้าเพิ่งกินอาหาร ให้มีโอกาสหยิบเมล็ดเพิ่มจาก curiosity/gather drive
- ถ้า agent ถือเมล็ดขณะ hunger state ให้มีโอกาสทำตกเพิ่มเล็กน้อย

สิ่งที่ไม่ได้ใส่:

- ไม่สอนว่า seed ใช้ปลูกได้
- ไม่สั่งให้เลือกดินดี
- ไม่สั่งให้กลับมาดู seed
- ไม่สั่งให้ทำฟาร์ม
- ไม่เพิ่ม oracle ว่า seed ไหนจะงอก

### เกณฑ์ผ่าน

ต่อ run ต้องมี:

- `agent_moved_seed_count >= 8`
- `agent_moved_seed_completed_chains >= 3`
- `agent_moved_seed_chain_agents >= 2`
- `agent_moved_vs_control_completed_lift >= 1.0`

ทั้งชุดต้องผ่าน 3/3 seeds

### ผลลัพธ์

Phase 3 ผ่าน 3/3 seeds

| seed | picked | dropped | moved seeds | completed moved-seed chains | chain agents | same-agent chains | moved/control lift |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20260610 | 213 | 213 | 172 | 14 | 12 | 2 | 1.235 |
| 20260611 | 165 | 165 | 137 | 17 | 12 | 6 | 1.600 |
| 20260612 | 212 | 210 | 178 | 18 | 14 | 4 | 1.357 |

Aggregate:

| Metric | Result |
| --- | ---: |
| mean moved seeds | 162.3333 |
| mean completed moved-seed chains | 16.3333 |
| mean moved-seed chain agents | 12.6667 |
| mean same-agent seed-food chains | 4.0 |
| mean moved/control completed-chain lift | 1.3973 |

### Interpretation

Phase 3 สนับสนุนว่า agent-displaced seeds ไม่ได้เป็น event ลอย ๆ แต่สามารถเข้าสู่วงจรชีวภาพจริงจนเกิดอาหารที่ถูกกินได้

นี่คือก้าวสำคัญจาก reward-place learning ไปสู่ proto-farming substrate:

- agent จัดการเมล็ดโดยไม่รู้ความหมาย
- เมล็ดที่ถูกย้ายมี downstream lifecycle
- downstream lifecycle นั้นกลับมาเป็นอาหาร
- completed-chain rate ของเมล็ดที่ agent ย้ายสูงกว่า broad control ในทุก seed

### สิ่งที่ยังอ้างไม่ได้

Phase 3 ยังไม่พิสูจน์ว่า agent ตั้งใจเพาะปลูก

ยังไม่ได้พิสูจน์ว่า:

- agent เลือกพื้นที่จากน้ำ/แสง/ดินดี
- agent ตั้งใจกลับไปดู seed ที่ตัวเองย้าย
- agent มี concept ของ seed
- agent ทำฟาร์มแบบจัดการพื้นที่
- agent สื่อสารข้อมูลเรื่องเมล็ดให้ตัวอื่น

## ก้าวสำคัญของงานวิจัย

### ก้าวที่ 1: โลกเริ่มมี ecology substrate จริง

ก่อน Phase 1 การถามว่า agent เรียนรู้อะไรยังไม่สมเหตุผล เพราะโลกยังไม่ให้ signal ที่เสถียรพอ

หลัง Phase 1 โลกมีวงจรพืชที่ agent กินได้จริง โดยไม่ต้องให้ natural seed rain ช่วยในชุดหลัก

### ก้าวที่ 2: จากอาหารเป็นความจำเชิงตำแหน่ง

Phase 2 เปลี่ยนคำถามจาก “โลกมีผลไม้ไหม” เป็น “agent ใช้ประสบการณ์ผลไม้เปลี่ยนพฤติกรรมตำแหน่งไหม”

ผล strict-return ชี้ว่า agent กลับไปตำแหน่งรางวัลมากกว่าความบังเอิญ

### ก้าวที่ 3: จากความจำตำแหน่งเป็น causal participation

Phase 3 เปลี่ยนจาก “จำแหล่งอาหาร” เป็น “การกระทำของ agent เข้าไปเปลี่ยนอนาคตของ ecology ได้ไหม”

ผลคือ agent ย้ายเมล็ด และเมล็ดเหล่านั้นบางส่วนกลายเป็นพืช ออกผล และถูกกินในภายหลัง

นี่คือครั้งแรกของโปรเจกต์ที่ agent action เชื่อมกับ delayed ecological consequence ได้เป็นสายเหตุผล

### ก้าวที่ 4: เริ่มมี proto-farming substrate

ยังไม่ใช่ farming แต่เริ่มมีองค์ประกอบก่อน farming:

- food reward
- place memory
- seed contact
- seed displacement
- delayed plant lifecycle
- fruit consumption from agent-displaced seeds

องค์ประกอบเหล่านี้เป็นฐานสำหรับ Phase 4 ที่จะถามเรื่อง managed patch โดยตรง

## Evidence Supporting

หลักฐานสนับสนุน:

- Phase 1 ผ่าน 5/5 seeds ทำให้ ecology signal เสถียร
- Phase 2 ผ่าน 3/3 seeds ด้วย strict left-then-return metric
- Phase 3 ผ่าน 3/3 seeds ด้วย seed-id causal ledger
- Phase 3 baseline fail ชี้ว่าก่อนแก้ agent ไม่ได้แตะเมล็ดจริง
- หลังแก้เฉพาะ food-contact seed handling เกิด seed chains จำนวนมากโดยไม่สอน semantics
- moved/control completed-chain lift สูงกว่า 1.0 ทุก seed ใน Phase 3 confirm

## Evidence Against / Alternative Explanations

หลักฐานที่ยังต้านการตีความเกิน:

- sample size ยังเล็ก: Phase 1 ใช้ 5 seeds, Phase 2-3 ใช้ 3 seeds
- world config ถูก tune เพื่อให้ ecology signal เกิดทันเวลา
- agent ยัง immortal จึงยังไม่ใช่ selection pressure แบบธรรมชาติเต็ม
- control ใน Phase 3 ยังเป็น broad control ไม่ใช่ matched micro-site control
- same-agent seed-food chains มี แต่ยังไม่ได้ใช้เป็น gate บังคับ
- high hunger level ยังคุมพฤติกรรม agent หนักมาก
- reward/place memory อาจผสมกับ terrain/food density/social clustering
- ไม่มีหลักฐานภาษา การสื่อสาร หรือ symbolic concept

## Confidence Level

ความมั่นใจแยกตาม claim:

| Claim | Confidence | เหตุผล |
| --- | --- | --- |
| โลกมีวงจร `seed -> plant -> fruit -> consumed` | สูง | ผ่าน 5/5 seeds ใน Phase 1 |
| agent มี reward-place learning | สูงปานกลาง | strict-return lift สูงมากใน 3/3 seeds แต่ baseline ยังเป็น random-position |
| agent-displaced seeds เข้าสู่วงจรพืชได้ | สูงปานกลาง | ผ่าน 3/3 seeds และมี seed-id chain |
| agent ตั้งใจปลูก | ต่ำ | ยังไม่มีหลักฐานเลือกพื้นที่/วางแผน |
| agent ทำฟาร์ม | ต่ำ | ยังไม่มี managed patch หรือ repeated seed placement |
| agent มีภาษา/สื่อสาร | ต่ำมาก | ยังไม่มี telemetry เรื่องสัญญาณ/communication |

## Limitations

1. Immortality

Agent ยังเป็น immortal เพื่อหลีกเลี่ยงการตายหมดก่อนทดลอง แต่ทำให้ยังไม่ใช่ ecological selection แบบเต็ม

2. Tuned ecology

Phase 1 config ถูก tune เพื่อให้วงจรพืชผ่าน gate จึงควรถือเป็น testbed ไม่ใช่โลกจริงสมบูรณ์

3. Control ยังไม่ละเอียดพอ

Phase 3 broad control ยังไม่เท่ากับ matched-site control ที่จับคู่ดิน น้ำ แสง ความชื้น และความหนาแน่นของอาหาร

4. High hunger pressure

Mean hunger level ใน Phase 1 อยู่ที่ 0.983 แปลว่าพฤติกรรมจำนวนมากยังถูก hunger instinct ครอบงำ

5. ยังไม่วัด communication

ยังไม่มีการวัดเสียง สัญญาณ ท่าทาง ภาษา หรือ information transfer ระหว่าง agent

## Phase ต่อไปควรทำอะไร

## Phase 4: Managed Patch / Proto-Farm

คำถาม:

> agent เริ่มทิ้งเมล็ดซ้ำในพื้นที่เดิม และกลับไปใช้พื้นที่นั้นเป็นแหล่งอาหารประจำหรือไม่

Metrics:

- repeated seed drops within patch radius
- agent-moved seed density per patch
- plant/fruit density near repeated-drop patch
- return rate to patch after seed drop
- patch productivity vs matched control cells
- same-agent or same-group patch reuse

Success criteria เบื้องต้น:

- อย่างน้อย 3/5 seeds มี repeated-drop patches
- patch มี plant/fruit density สูงกว่า matched controls
- agent/group กลับไป patch มากกว่า random/control
- มี completed chains หลายรุ่นใน patch เดียว

## Phase 5: Site Selection

คำถาม:

> agent วางเมล็ดในพื้นที่ที่เหมาะกว่าโดยบังเอิญหรือจากประสบการณ์หรือไม่

Metrics:

- water/moisture at drop site
- light at drop site
- nutrients at drop site
- danger at drop site
- germination probability by drop-site quality
- change in drop-site quality over time

Control:

- random carried-seed drop simulation
- matched current-position controls
- shuffled-agent labels

## Phase 6: Remove Immortality / Selection Pressure

คำถาม:

> เมื่อ agent ตายได้จริง พฤติกรรม seed handling/patch use ช่วย survival หรือ reproduction หรือไม่

Metrics:

- survival time
- reproduction count
- offspring maturity
- lineage persistence
- food security near lineage area
- trait shifts across generations

Success criteria:

- lineages with stronger seed/patch behavior survive or reproduce better than controls
- behavior persists across generations without direct instruction

## Phase 7: Social Learning / Information Transfer

คำถาม:

> agent ตัวอื่นใช้ประโยชน์จาก patch หรือ seed behavior ที่ agent หนึ่งสร้างไว้ได้หรือไม่

Metrics:

- non-owner visits to productive patch
- group reuse of seed-drop areas
- child/kin visits to parental food patches
- behavior copying after observation
- shared memory effects

ต้องระวัง:

- แยก social attraction ออกจาก food attraction
- แยก kin clustering ออกจาก true information transfer

## Phase 8: Communication / Proto-Language

คำถาม:

> agent เริ่มสร้างสัญญาณที่มีความสัมพันธ์กับอาหาร พื้นที่ปลอดภัย เมล็ด หรือ patch หรือไม่

เริ่มจากไม่ต้องให้ภาษา:

- ให้ agent มีช่องส่งสัญญาณต้นทุนต่ำ เช่น sound/gesture marker
- signal ไม่มี semantic label ล่วงหน้า
- วัด mutual information ระหว่าง signal กับ world state
- วัดว่า receiver เปลี่ยนพฤติกรรมหลัง signal หรือไม่

Metrics:

- signal entropy
- signal-state mutual information
- receiver movement change
- signal reuse near food/patch/danger
- inter-agent consistency

## Phase 9: Robustness / Paper-Quality Replication

คำถาม:

> ผล Phase 1-4 ยังอยู่ไหมเมื่อเปลี่ยน seed, world size, body plan, ecology parameter และ control ที่เข้มขึ้น

ต้องเพิ่ม:

- 10-20 seeds ต่อ condition
- multiple body plans
- matched micro-site controls
- ablation: no food-contact seed handling
- ablation: memory-disabled agents
- ablation: shuffled reward labels
- confidence intervals
- effect size

## Conclusion

ผลถึง Phase 3 ถือเป็น milestone สำคัญของงานวิจัยนี้

ระบบไม่ได้แค่มีอาหารในโลก แต่เริ่มแสดงลำดับการเรียนรู้เชิงสภาพแวดล้อม:

```text
ecology works
-> agent remembers food places
-> agent actions alter seed futures
-> agent-displaced seeds produce future consumed food
```

คำสรุปที่เหมาะสมที่สุดตอนนี้คือ:

> Agent ยังไม่ได้ทำฟาร์มอย่างตั้งใจ แต่โลกและพฤติกรรม agent มี substrate ที่ทำให้ proto-farming สามารถเกิดขึ้นได้ และมีหลักฐานเชิงข้อมูลว่า agent action เริ่มเชื่อมกับ delayed ecological consequence แล้ว

ก้าวต่อไปจึงไม่ใช่ถามว่า “มีผลไม้ไหม” หรือ “agent กลับมาไหม” อีกแล้ว แต่ต้องถามว่า:

> agent เริ่มจัดการพื้นที่ซ้ำ ๆ จนเกิด patch ที่มีผลผลิตสูงขึ้นหรือไม่

นี่คือโจทย์หลักของ Phase 4

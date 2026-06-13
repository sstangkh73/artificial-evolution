# รายงานสรุป Phase 4: Managed Patch / Proto-Farm Evidence

วันที่สรุป: 2026-06-13
พื้นที่ทดลอง: `C:\artificial-evolution`

ไฟล์อ้างอิง:

- protocol ก่อนทดลอง: `reports/phase4_managed_patch_protocol_2026-06-13.th.md`
- ผล confirm: `data/phase4_managed_patch_confirm01_20260613`
- รายงานอัตโนมัติ: `reports/phase4_managed_patch_confirm01_2026-06-13.th.md`

## Abstract

Phase 4 ผ่านในรอบ confirm 5 seeds: `5/5` runs ผ่านเกณฑ์ managed patch / proto-farm gate

ผลรอบนี้ยกระดับจาก Phase 3 ซึ่งพิสูจน์ว่า agent-displaced seeds เข้าสู่วงจรพืชได้ ไปเป็นหลักฐานว่า seed drops ของ agent สามารถรวมเป็น repeated productive patches ที่มีผลผลิตสูงกว่า control และถูก agent กลับมาใช้พื้นที่ซ้ำ

ยังไม่ควรอ้างว่า agent เข้าใจ farming เชิงสัญลักษณ์หรือมีภาษาการเพาะปลูก คำที่เหมาะสมคือ **managed patch / proto-farming evidence**

## Method

เพิ่ม instrumentation ใน `scripts/run_long_emergence_watch.py` โดยไม่เพิ่ม policy ใหม่ให้ agent:

- ติดตาม seed drop watcher หลัง `seed_dropped` ที่ผ่านเงื่อนไข agent-moved
- จับกลุ่ม agent-moved seed final drop เป็น patch ด้วย Manhattan radius `4`
- วัด completed chain ของ seed ใน patch:

```text
seed_dropped
-> seed_germinated
-> plant_matured
-> plant_fruited
-> plant_lifecycle_food_consumed
```

- วัด agent return หลัง drop เทียบ random-position expectation
- เทียบ productivity กับ control seeds ที่ไม่ได้ถูก agent ย้าย โดยใช้ matched micro-site control เมื่อมีจำนวนพอ
- บันทึก contamination จาก scaffolded farming events:
  - `tend_food_patch`
  - `food_patch_tended`

## Experiment Setup

- seeds: `20260610`, `20260611`, `20260612`, `20260613`, `20260614`
- time limit: `90s` ต่อ seed
- agents เริ่มต้น: `50`
- immortal: `true`
- world size: `100x100`
- natural seed rain: `0`
- ecology config: ใช้ config ที่ผ่าน Phase 1-3
- success gate: อย่างน้อย `3/5` runs ผ่าน

## Results

Phase 4 confirm ผ่าน `5/5` seeds

| seed | pass | moved seeds | moved chains | repeated patches | patch chains | patch food | return agents | max drops | productivity lift | return lift | contamination |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20260610 | true | 111 | 13 | 20 | 18 | 49 | 50 | 22 | 6.052 | 35.245 | 0 |
| 20260611 | true | 116 | 15 | 20 | 28 | 67 | 50 | 21 | 5.363 | 29.313 | 0 |
| 20260612 | true | 141 | 14 | 23 | 21 | 55 | 50 | 22 | 6.315 | 15.390 | 0 |
| 20260613 | true | 234 | 30 | 39 | 46 | 123 | 50 | 24 | 6.445 | 26.091 | 0 |
| 20260614 | true | 142 | 16 | 25 | 32 | 83 | 50 | 15 | 4.933 | 22.857 | 0 |

Aggregate:

- mean repeated-drop patch count: `25.4`
- mean patch completed chains: `29.0`
- mean patch food consumed: `75.4`
- mean patch return agents: `50.0`
- mean max patch moved-seed drops: `20.8`
- mean max patch completed chains: `4.6`
- mean best patch productivity lift vs control: `5.8216`
- mean best patch return lift vs random control: `25.7792`
- total contamination events: `0`

## Key Observation

สิ่งที่เปลี่ยนจาก Phase 3 คือ event ไม่ได้เป็นแค่ seed เดี่ยวที่ agent ย้ายแล้วสำเร็จ แต่เกิดเป็น cluster หลายจุด:

```text
agent-moved seed drops
-> repeated local patches
-> multiple completed plant-food chains inside patches
-> consumed food inside patches
-> agents return to patch areas far above random expectation
```

ตัวอย่าง best patch:

- seed `20260610`: center `[85,18]`, moved-seed drops `22`, completed chains `5`, food consumed `14`, return agents `46`
- seed `20260611`: center `[95,46]`, moved-seed drops `12`, completed chains `5`, food consumed `10`, return agents `45`
- seed `20260614`: center `[57,32]`, moved-seed drops `11`, completed chains `4`, food consumed `8`, return agents `42`

## Evidence Supporting

- ทุก seed ผ่านเกณฑ์ Phase 4
- repeated-drop patches เกิดทุก run
- patch completed chains สูงกว่าเกณฑ์มากทุก run
- patch food consumed สูงกว่าเกณฑ์มากทุก run
- return lift สูงกว่า random baseline ทุก run
- productivity lift สูงกว่า control ทุก run
- control mode เป็น `matched_micro_site` ทุก run
- contamination events เท่ากับ `0`

## Evidence Against / Alternative Explanations

- return agents เท่ากับ 50 ทุก run อาจสะท้อน food attraction, shared foraging corridor หรือ social clustering ไม่ใช่ intentional patch management เพียงอย่างเดียว
- matched control ใช้ cell-quality ณ เวลา summary ยังไม่ใช่ causal counterfactual เต็มรูปแบบ
- agent ยัง immortal ทำให้ยังไม่วัดว่า patch behavior ช่วย survival หรือ reproduction จริงหรือไม่
- ไม่มีหลักฐานว่า agent มี concept ของ seed, farm, ownership หรือ planning
- same-agent chain ยังไม่ใช่ gate หลัก จึงยังแยก owner farming ออกจาก group-level ecological reuse ไม่สมบูรณ์

## Interpretation

ผล Phase 4 สนับสนุน claim ระดับนี้:

> agent behavior plus plant lifecycle substrate now produces repeated productive seed-drop patches that agents revisit and consume from, with productivity and return rates above controls.

คำแปลเชิงวิจัย:

> ระบบเริ่มมี managed patch / proto-farming evidence แล้ว

สิ่งที่ยังไม่ควรพูด:

> agent เข้าใจการทำฟาร์ม

หรือ:

> agent ตั้งใจปลูกพืชแบบมี concept

## Confidence Level

- managed patch exists: สูง
- patch productivity above control: สูงปานกลาง
- patch revisit above random: สูง
- intentional farming: ต่ำ
- symbolic seed knowledge/language: ต่ำมาก

## Next Phase Recommendation

Phase 5 ควรทดสอบ **site selection**:

> agent เลือกวาง seed ในพื้นที่ที่เหมาะกว่าโดยพฤติกรรมเปลี่ยนตามประสบการณ์หรือไม่

ต้องเพิ่ม:

- drop-site moisture/light/nutrient quality over time
- matched current-position controls
- shuffled-agent controls
- memory-disabled or reward-shuffled ablation
- same-agent patch ownership gate
- survival/reproduction linkage ใน Phase 6

## Conclusion

Phase 4 เป็น milestone สำคัญ เพราะเป็นครั้งแรกที่ผลจาก agent seed movement ถูกยกระดับจาก causal chain รายเมล็ด ไปเป็น repeated productive area

สรุปตามหลักฐาน:

```text
Phase 1: ecology signal exists
Phase 2: reward-place learning exists
Phase 3: agent-displaced seed causal chains exist
Phase 4: repeated productive seed-drop patches exist
```

นี่ทำให้โปรเจกต์พร้อมเข้าสู่ Phase 5: ทดสอบว่า patch เหล่านี้เกิดจากการเลือกพื้นที่/การเรียนรู้คุณภาพพื้นที่ หรือยังเป็นผลของตำแหน่งอาหารและการรวมกลุ่มเป็นหลัก

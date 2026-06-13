# รายงาน Phase 3: Seed Causality / Proto-Farming Probe

วันที่รัน: 2026-06-13
ชุดผลลัพธ์หลัก: `data/phase3_seed_causality_confirm01_20260613`

## คำตัดสิน

ผ่าน Phase 3: 3/3 seeds ผ่านเกณฑ์

Phase 3 รอบนี้ไม่ได้วัดแค่ว่า agent จำแหล่งอาหารได้ แต่ตามสายเหตุผลของเมล็ดเป็นราย `seed_id`:

```text
agent picks seed
-> agent drops seed somewhere else
-> seed germinates
-> plant matures
-> plant fruits
-> plant-lifecycle food is consumed
```

## Before

baseline แรกก่อนแก้:

- `plant_food_consumed = 191`
- `seed_picked = 0`
- `seed_dropped = 0`
- `agent_moved_seed_count = 0`
- `agent_moved_seed_completed_chains = 0`

ผลคือ Phase 3 fail เพราะโลกมีวงจรพืชและผลไม้แล้ว แต่ agent ไม่เคยเข้าสายเหตุผลของเมล็ดเลย

probe หลังแก้แค่เรียก seed primitive หลัง consume แต่ยังไม่แก้ energy gate:

- `plant_food_consumed = 575`
- `seed_picked = 0`
- `seed_dropped = 0`

แปลว่าช่องว่างหลักคือ agent อยู่ในภาวะหิววิกฤตเกือบตลอด ทำให้ seed primitive ถูก energy gate กันออก แม้จะเพิ่งกินอาหารและมีเมล็ดตกอยู่ตรงเท้า

## Change

แก้เฉพาะ substrate-level seed handling:

- หลัง agent กินอาหาร ให้ seed primitive ทำงานด้วย `food_contact=True`
- ถ้าเพิ่งกินอาหาร ให้มีโอกาสหยิบเมล็ดเพิ่มจาก curiosity/gather drive
- ถ้า agent ถือเมล็ดขณะอยู่ใน hunger state ให้มีโอกาสทำตกเพิ่มเล็กน้อย

สิ่งที่ไม่ได้ใส่:

- ไม่สอนว่า seed ใช้ปลูกได้
- ไม่สั่งให้เลือกดินดี
- ไม่สั่งให้ทำฟาร์ม
- ไม่เพิ่ม oracle ว่าเมล็ดไหนจะงอก

## Success Criteria

ต่อ run ต้องผ่าน:

- `agent_moved_seed_count >= 8`
- `agent_moved_seed_completed_chains >= 3`
- `agent_moved_seed_chain_agents >= 2`
- `agent_moved_vs_control_completed_lift >= 1.0`

ทั้งชุดต้องผ่าน 3/3 seeds

## Confirm Results

| seed | pass | picked | dropped | moved seeds | completed moved-seed chains | chain agents | same-agent chains | moved/control lift |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20260610 | true | 213 | 213 | 172 | 14 | 12 | 2 | 1.235 |
| 20260611 | true | 165 | 165 | 137 | 17 | 12 | 6 | 1.600 |
| 20260612 | true | 212 | 210 | 178 | 18 | 14 | 4 | 1.357 |

Aggregate:

- mean moved seeds: 162.3333
- mean completed moved-seed chains: 16.3333
- mean moved-seed chain agents: 12.6667
- mean same-agent seed-food chains: 4.0
- mean moved/control completed-chain lift: 1.3973

## Interpretation

ผลนี้สนับสนุนว่า Phase 3 ผ่านในความหมายแคบและสำคัญ:

agent-displaced seeds สามารถเข้าสู่วงจรพืชจริง งอก โต ออกผล และกลายเป็นอาหารที่ถูกกินได้ โดยอัตรา completed chain ของเมล็ดที่ agent ย้ายสูงกว่า control ในทุก seed ที่ยืนยัน

นี่คือ proto-farming substrate ที่เกิดจากการจัดการเมล็ดแบบไม่รู้ความหมาย ไม่ใช่หลักฐานว่า agent เข้าใจการเพาะปลูกหรือมีภาษาเกี่ยวกับเมล็ด

## Evidence Against / Limitations

- ยังไม่ได้พิสูจน์ว่า agent ตั้งใจเลือกพื้นที่ดิน/น้ำ/แสงที่ดีกว่า
- same-agent chains มีแล้ว แต่ยังไม่ใช่เกณฑ์บังคับ
- control ยังเป็น broad control ไม่ใช่ fully matched micro-site control
- agent ยังเป็น immortal จึงยังไม่มีแรงคัดเลือกจากการตาย
- ยังไม่มีหลักฐานภาษา สัญลักษณ์ หรือการสื่อสารเรื่องเมล็ด

## Next Gate

Phase 4 ควรวัด managed patch:

- agent ทิ้งเมล็ดซ้ำในพื้นที่เดิมหรือไม่
- พื้นที่ที่ agent ทิ้งเมล็ดมี plant/fruit density สูงขึ้นหรือไม่
- agent กลับไปพื้นที่นั้นเป็นประจำมากกว่า random/control หรือไม่
- seed placement ดีขึ้นตามเวลาไหม เช่น ดินดี น้ำพอ แสงพอ ความเสี่ยงต่ำ

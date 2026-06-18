# Results: Metabolism v2 — Tier 1 (Fix 1–3) execution

วันที่: 2026-06-18
อ้างอิงแผน: `reports/metabolism_physics_v2_tier1_protocol_2026-06-15.th.md`
commit ที่เพิ่ม: `c6644c8` (Fix 2), `d7adb94` (Fix 3) — base `17bdd6c`
สถานะ: Fix 1–3 ทำครบและ verify แล้ว · พบ blocker เชิงออกแบบ 2 จุดที่ต้องแก้ก่อน Phase 6

---

## สรุปหนึ่งบรรทัด

Tier 1 ทั้ง 3 fix ทำเสร็จและผ่านการ verify (v1 byte-identical, endozoochory ถูกนับถูกหมวด, ecology ไม่พัง, 23/23 tests) **แต่การรันจริงเปิดโปง 2 ข้อเท็จจริงที่แผนไม่รู้:** (1) `args.seed` แทบไม่มีผลต่อผล → "3 seeds" ไม่ใช่ replicate จริง, (2) คอนฟิก gate ไม่มีการเกิดลูกเลยถึง 9000 ticks → heritability ของ Fix 3 ยังไม่มี offspring ให้แสดงผล และ Phase 6 ทำไม่ได้จนกว่าจะแก้

---

## Fix 1 — Fixed-tick gate (v1 vs v2)

method: รัน `.codex-temp/gate_run.py` (reuse คอนฟิก canonical จาก `measure_endo.py`) ล็อก `--ticks 3000`, time-limit 999999, body 37, seeds 20260610/11/12, เทียบ v1 vs v2 ที่ tick เท่ากัน

| metric (tick 3000) | v1 | v2 |
| --- | ---: | ---: |
| seed_germinated | 919 | 903 |
| plant_matured | 247 | 221 |
| plant_fruited | 528 | **487** |
| plant_lifecycle_food_consumed | 284 | **261** |
| harvest_seed_dropped | 350 | 328 |
| seed_picked | 93 | 27 |
| seed_dropped | 93 | 26 |
| gut_seed_ingested / excreted | 0 / 0 | 328 / 326 |
| agent_moved_seed_count | 81 | 337 |

- **gate ผ่าน:** v2 มี `plant_fruited > 0` และ `plant_lifecycle_food_consumed > 0` ครบทั้ง 3 seeds → ecology ไม่พังใต้ energy ใหม่ ไม่ต้อง re-tune `ENERGY_DENSITY`
- v1 ≠ v2 ที่ fixed-tick (ตามที่ควรเป็น) — "เท่ากัน" เดิมเป็น wall-clock artifact จริง
- กลไกเปลี่ยนชัด: v2 ดัน dispersal จาก pickup/drop ที่เขียนมือ (93→26) ไปเป็น gut transit (0→326) = "ฟิสิกส์ตัดสิน" ตาม thesis

> ⚠️ **คำเตือนซื่อสัตย์:** ทั้ง 3 seeds ให้ผล **identical เป๊ะ** (ดู blocker 1) → นี่คือ n=1 ที่ deterministic ไม่ใช่ n=3 ห้ามรายงานเป็น 3 replicates

---

## Fix 2 — Runner parse `gut_seed_*` (committed `c6644c8`)

- เพิ่ม 3 gut events เข้า `SAMPLED_EVENT_KINDS` + branch parse
- `gut_seed_excreted` → `agent_moved=True`, `source_kind="gut_transit"`, ตำแหน่ง = **จุดขับจริง**, ระยะกระจายวัดจากจุดกิน
- `gut_seed_killed` → agent_moved + death (seed-predator: handled แต่ไม่จบ chain)
- เพิ่ม `metabolism_model` + `sample_gut_*` ลง output JSON

**verify (v2, 3000t):** `agent_moved_seed_count` 81→337 (เมล็ดผ่าน gut 326 เม็ดถูกนับเป็น agent dispersal แทนที่จะตกเข้า control); sample = `gut_seed_excreted ... x=80 y=36 acid=0.40 shell=0.60 scarified=1`; v1 ไม่เปลี่ยน (ไม่มี gut event)

---

## Fix 3 — Heritability + `gut_capacity` (committed `d7adb94`)

**แก้ตรรกะ RNG ของแผน:** แผนเขียน "เพิ่มเข้า TRAIT_FIELDS + draw ต่อท้าย" ซึ่งขัดกันเอง — `TRAIT_FIELDS` ถูก draw ในลูปเดียว และทุก draw ที่แทรกใน `inherit_body_plan` จะเลื่อน **stream กลางของ sim** หลัง birth แรก (spawn_child ป้อน rng หลักมาจาก tick loop ที่ [runner.py:2502](simulation/runner.py:2502)) → จะพัง v1

ที่ทำจริง:
- `METABOLISM_TRAIT_FIELDS` แยกจาก `TRAIT_FIELDS` + bounds + steps; `acid_strength ∈ [0.1,0.9]` คร่อม shell 0.6
- `inherit_body_plan(..., draw_metabolism_genes=False)` — draw ยีนใหม่ที่ **tail** เฉพาะเมื่อ flag เปิด
- `spawn_child` ตั้ง flag = `(env.metabolism_model=="v2")` → v1 draw เพิ่ม **ศูนย์** ครั้ง
- `_route_seed_to_gut` บังคับ `gut_capacity` (ท้องเต็ม → เมล็ดคงเป็น harvest_drop บนพื้น)

**verify:**
- **v1 regression:** รัน v1 3000t ก่อน/หลัง → `event_counts` + `seed_causality_metrics` + `births` + `plant_counts` + `first_event_tick` **IDENTICAL** (RNG prefix ไม่ขยับ)
- tests 23/23 (เพิ่ม: v1 ยีนค้าง default, v1 ไม่ draw เพิ่ม, v2 ยีน inherited ใน bounds)

---

## 🔴 Blocker ที่พบจากการรันจริง (สำคัญกว่าตัว fix)

### Blocker 1 — `args.seed` แทบไม่มีผล → ไม่มี replication จริง
[agent.py:909](agents/agent.py:909), [:938](agents/agent.py:938): การเคลื่อนที่ของ agent ใช้ `Random(self.agent_id + self.age)` = RNG seed จาก (agent_id+age) **ไม่ผูกกับ `args.seed`** การเคลื่อนที่คือ driver หลักของพฤติกรรม → 3 seeds ให้ผล identical ทุก metric ทั้งที่ tick 3000 และ 9000
- ผล: Fix 1 design "2 model × 3 seeds" ให้ replicate จริงไม่ได้ (เป็น deterministic n=1)
- ทางแก้: ผูก `args.seed` เข้า movement RNG เช่น `Random(hash((args.seed, agent_id, age)))` หรือสุ่ม initial condition ต่อ replicate **แล้วค่อยเคลม multi-seed**

### Blocker 2 — births = 0 → ไม่มีการสืบพันธุ์
คอนฟิก gate (immortal=True, pop 50) ไม่มี birth เลยถึง 9000 ticks (population คง 50)
- ผล: `inherit_body_plan` ไม่เคยถูกเรียกใน 1 generation → heritability ของ Fix 3 ยัง **ไม่มี offspring ให้แสดงผล**; ยีนทุกตัวคง default → gut_seed_killed=0 ไม่ใช่เพราะ trade-off แต่เพราะยังไม่มีความแปรผัน
- v1 regression จึง byte-identical แบบ **ปลอดภัยโดยโครงสร้าง** (flag gating) แต่ path การสืบพันธุ์ยัง unexercised ในระดับ sim (unit test ครอบไว้แทน)
- ผล: **Phase 6 (selection ข้ามรุ่น) เป็นไปไม่ได้** จนกว่าจะมี births > 0 ต้องหาเงื่อนไข reproduction ที่จุดติด (ทำไม wants_reproduction ไม่เคยจริง) ก่อนเป็นอันดับแรก

---

## Evidence (ตาม hypothesis-testing skill)

- **Supporting:** v1 byte-identical (เลขตรงเป๊ะ); endozoochory ถูกนับเป็น agent_moved 326 เม็ด; ecology gate ผ่านทุก seed; 23/23 tests
- **Against / Alternative:** "3 seeds" ไม่ใช่ replicate (seed inert); births=0 → heritability/Phase 6 ยังพิสูจน์ไม่ได้; gut_killed=0 ยังเป็นเพราะ default ไม่ใช่ trade-off
- **Missing:** การรันที่มี reproduction จริง; seed ที่ผูกกับ movement; control arm + viability gate สำหรับ Phase 6
- **Confidence:** Fix 1–3 ถูกต้องเชิงโค้ด = **สูง**; v2 พร้อมเทียบ v1 ผ่าน phase metrics = **ปานกลาง** (ขึ้นกับแก้ replication); พร้อมเข้า Phase 6 = **ต่ำ** (ติด births=0)

## Next (เรียงตามผลกระทบ)
1. หาเหตุ births=0 (เงื่อนไข `wants_reproduction`) — prerequisite ของทุกอย่างที่เกี่ยวกับ generation
2. ผูก `args.seed` เข้า movement RNG เพื่อให้ multi-seed เป็น replicate จริง
3. แล้วจึงรัน Fix 1 ใหม่แบบมี replicate + เข้า Phase 6 พร้อม control arm

# Protocol: Phase 6 — Selection Pressure on Diet & Seed-Handling

วันที่เขียน: 2026-06-15
สถานะ: pre-implementation (ทำหลัง Tier 1 เสร็จ)
อ้างอิง: `reports/metabolism_physics_v2_tier1_protocol_2026-06-15.th.md` (prerequisite), `reports/phase3/phase1_to_phase3_research_success_report_2026-06-13.th.md` (Phase 6 outline เดิม)

เป้าหมายระยะยาว: เปลี่ยนจาก "endozoochory เกิดได้" (substrate) → "endozoochory/diet ถูกวิวัฒนาการคัดเลือก" (emergent evolution)

---

## คำถามวิจัย

> เมื่อ agent ตายได้จริง (ปิด immortal) และยีน digestion ถ่ายทอด/กลายพันธุ์ได้ —
> 1. trait ด้านการกิน (`acid_strength`, `gape`, `gut_transit_ticks`) เลื่อนข้ามรุ่นตามแรงกดดันของ ecology หรือไม่?
> 2. **diet trade-off** เกิดจริงไหม: lineage `acid < shell` (seed disperser, ได้พลังงานน้อยแต่กระจายเมล็ดต่อวงจรอาหารตัวเอง) vs `acid > shell` (seed predator, ได้พลังงานจากเมล็ดแต่ฆ่ามัน) — ฝั่งไหนรอด/สืบพันธุ์ดีกว่าใน ecology แบบไหน?
> 3. พฤติกรรม seed-handling สืบทอดข้ามรุ่นโดย **ไม่ถูกสอน** หรือไม่?

---

## ⚠️ Prerequisite สำคัญที่สุด: agent ต้องรอดได้ก่อน

ปัจจุบัน mean_hunger = 0.983 (energy ค้างที่ ~1) เพราะ immortal กันตายไว้ **ถ้าปิด immortal ทื่อๆ ประชากรจะตายเกือบหมดทันที** → วัด selection ไม่ได้

ดังนั้น **ก่อน** Phase 6 ต้องมี energy economy ที่ agent อยู่รอดถึงวัยสืบพันธุ์ได้ ตัวเลือก:
- ยก `ENERGY_DENSITY` / `base_food_spawn` จนพลังงานสุทธิเป็นบวกพอให้บางตัวรอด
- หรือเริ่มจาก semi-mortal (เพิ่ม death เป็นขั้น เช่น ตายเฉพาะ energy ≤ 0 นานเกิน N ticks) แล้วค่อยเข้มขึ้น
- gate: ประชากรไม่ collapse < 10 ตัวภายใน 500 ticks แรก และมี births > 0

นี่คือเหตุผลที่ Tier 1 Fix 1 (fixed-tick gate + re-tune energy ถ้าจำเป็น) ต้องเสร็จก่อน

---

## Method

ปิด `--no-immortal` (immortal=False), เปิด heritability (Tier 1 Fix 3), รันยาวพอให้เกิดหลายรุ่น (ประเมิน generation length จาก `ADULT_AGE`/reproduction params — รันจน generation ≥ 5)

### Conditions
| condition | ecology | จุดประสงค์ |
| --- | --- | --- |
| `seed_dependent` | อาหาร ambient น้อย, พึ่งวงจรพืชจากเมล็ดสูง | คาดว่า favor disperser (เมล็ดรอด → อาหารอนาคต) |
| `ambient_rich` | อาหาร ambient เยอะ, ไม่พึ่งเมล็ด | คาดว่า favor predator (กินเมล็ดเอาพลังงานเลย) |
| `neutral_baseline` | สมดุล | baseline |

### Experiment design
- **IV:** ecology regime (3 แบบ); immortal=False
- **DV:** mean `acid_strength` / `gape` / `gut_transit_ticks` ต่อรุ่น; survival time; reproduction count; lineage persistence; `gut_seed_killed : gut_seed_excreted` ratio; completed-chain rate ต่อ lineage; population size
- **Control:**
  - **frozen-genes** (mutation ปิด) — trait เลื่อนเฉพาะตอนมี mutation/selection จริงไหม
  - **shuffled-lineage labels** — แยก selection ออกจาก drift
  - **random-trait reseed** — baseline ของ trait distribution แบบไม่มี selection
- **Success criteria:**
  1. trait shift มีทิศทาง **สัมพันธ์กับ ecology** (disperser↑ ใน seed_dependent, predator↑ ใน ambient_rich) และต่างจาก frozen/shuffled control
  2. lineage ที่ trait เหมาะกับ ecology มี reproduction/persistence สูงกว่า
  3. seed-handling ยังเกิดในรุ่นหลังโดยไม่มีคำสั่ง (≥ 3/5 seeds)
- **Failure / Falsification:**
  - trait ไม่เลื่อน หรือเลื่อนเท่ากันทุก condition → ไม่ใช่ selection (เป็น drift)
  - disperser/predator survive เท่ากันทุก ecology → trade-off ไม่มีผล
  - frozen-genes control ก็เลื่อน → artifact ไม่ใช่ selection

---

## Confounds ที่ต้องคุม (ตาม hypothesis-testing skill)
- **drift vs selection** — ต้องมี frozen-gene control + N seeds พอ + ดู effect size ไม่ใช่แค่ทิศทาง
- **founder effects** — trait เริ่มต้นของ founders มีผลมาก → reseed หลาย founder distribution
- **population crash** — ถ้า collapse selection อ่านไม่ได้ (ดู prerequisite)
- **linked traits** — `acid_strength` อาจ correlate กับยีนอื่นใน archetype → ตรวจว่า shift มาจาก diet pressure จริง ไม่ใช่ hitchhiking
- **gut attribution** — ต้องมี Tier 1 Fix 2 ไม่งั้น completed-chain ของ gut seed อ่านผิด

---

## Metrics output ที่ต้องเพิ่ม
- per-generation trait histogram (acid_strength, gape, gut_transit_ticks)
- lineage tree + survival/reproduction ต่อ lineage
- disperser-fraction vs predator-fraction ข้ามรุ่น
- (ใช้ของเดิม) seed_causality completed-chain ต่อ lineage

---

## Confidence ที่คาดหวังล่วงหน้า
| claim | คาดว่าได้ confidence |
| --- | --- |
| trait ถ่ายทอดข้ามรุ่น (mechanical) | สูง (ถ้า Tier 1 Fix 3 ถูก) |
| trait shift = selection ไม่ใช่ drift | ปานกลาง (ขึ้นกับ control + N) |
| diet trade-off emerge จริง | ต่ำ-ปานกลาง (สมมติฐานเสี่ยง — อาจไม่เกิดถ้า ecology ไม่กดดันพอ) |

> ผลลบก็มีค่า: ถ้า trade-off ไม่ emerge แต่ควบคุมการทดลองดี = บอกได้ว่า ecology ปัจจุบันยังไม่สร้างแรงกดดันพอ ซึ่งเป็น finding ที่ตรงไปตรงมา ไม่ใช่ความล้มเหลว

---

## หลัง Phase 6 (roadmap เดิมต่อ)
- Phase 7: social learning / information transfer (agent อื่นใช้ patch/seed ที่ตัวอื่นสร้าง) — ระวังแยก social attraction ออกจาก food attraction
- Phase 8: proto-communication (signal-state mutual information) — ไม่ให้ภาษาล่วงหน้า
- Phase 9: robustness/replication (10-20 seeds, multiple body plans, matched micro-site controls, ablations, CI, effect size)

(รายละเอียดอยู่ใน `phase1_to_phase3_research_success_report_2026-06-13.th.md` ส่วน "Phase ต่อไป")

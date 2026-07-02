# รายงาน: Toxin Physics v1 — พิษ→ความเสียหาย + การเรียนรู้เลี่ยงอาหาร (ปิดช่องว่าง G11)

**Wiring toxin into damage + the food-value-learning link: does an agent learn to avoid a toxic-but-rich food?**

ผู้จัดทำ: Chisanupong · โครงการ Artificial Evolution (ALife → YSC/ISEF)
วันที่: 2026-07-01
สถานะ: **implemented + tested + demonstrated** (opt-in, byte-identical เมื่อปิด)
ต่อจาก: `aging_physics_v1_implementation_2026-07-01` (G11 คือช่องว่างที่เหลือ) · `metabolism_physics_v2_design` (หลัก no-oracle)

---

## 1. ทำอะไร

ต่อ `toxin` (ที่เดิมเป็น scaffold ใน `world/metabolism.py`) เข้าเส้นทางการกินจริง โดยเพิ่มอาหารมีพิษ **`raw_fruit`** (พลังงานสูง ~10.3 = ~2× raw_plant แต่ toxin สูง) เมื่อ agent กินวัตถุที่ toxin เกิน `toxin_tolerance` (ยีน) จะเกิด **สองผลที่แยกกัน**:

| ผล | กลไก | ผลต่อ ecology |
|---|---|---|
| **เฉียบพลัน (acute)** | หักพลังงานสุทธิของคำนั้น (ป่วย) = `excess × toxin_acute_penalty` | ค่านี้ไหลเข้า `food_value_memory` → **เรียนรู้ที่จะเลี่ยงได้** |
| **เรื้อรัง (chronic)** | เพิ่ม `damage` (ช่อง aging) = `excess × toxin_damage_coeff` | ต้นทุนอายุขัย + selection บน `toxin_tolerance` ("พิษช้า" ที่การเรียนรู้จับไม่ได้) |

**หลัก no-oracle (สำคัญ):** โลก**ไม่เคยบอก**ว่าอาหารมีพิษ — agent รับรู้แค่ "พลังงานสุทธิที่ได้จริง" (ลดเพราะป่วย) และ damage ที่ซ่อนอยู่ การเลี่ยงจึงต้อง **emerge** จากการเรียนรู้/การคัดเลือก ไม่ใช่จากกฎที่เขียนมือ

**จุดเชื่อมที่สวยที่สุด:** เพราะ acute penalty ถูกหักออกจาก `restored_energy` **ก่อน** `_learn_food_value` → ระบบเรียนรู้ค่าอาหารเดิม (study B) เรียนรู้ค่าสุทธิที่ต่ำลงเอง **โดยไม่ต้องเขียนโค้ดเรียนรู้เพิ่มเลย**

---

## 2. ผลลัพธ์: agent เรียนรู้ที่จะไม่กินผลไม้พิษไหม? — **ใช่**

`python scripts/run_toxin_diet_study.py` (controlled: agent อิ่ม เลือกอิสระ plant vs fruit ทุกรอบ ผ่านประตูตัดสินใจจริง):

| เงื่อนไข | learned value (plant / fruit) | fruit ที่กิน (จาก 60 ครั้ง) |
|---|---|---|
| **พิษ OFF** (fruit = อาหารพลังงานสูงล้วน) | 5.0 / **10.0** | **60/60** (กินหมด — fruit ดีสุด) |
| **พิษ ON** (acute penalty 50) | 5.0 / **2.0** | **1/60** (ชิมครั้งเดียวแล้วเลี่ยงตลอด) |

→ เปิดพิษ: agent **ชิม fruit ครั้งเดียว** (บังคับชิมของใหม่เพื่อเรียนรู้) เห็นว่าค่าสุทธิแค่ 2.0 < plant 5.0 แล้ว **เลี่ยงตลอด** = optimal diet ที่ emerge จากการเรียนรู้ล้วน ๆ

---

## 3. ⚠️ ในซิมเต็ม: การเลี่ยงถูกบดบังด้วยคอขวด foraging (ผลที่ต้องซื่อสัตย์)

รันซิมเต็ม (`--value-learning --toxic-food --toxin-acute-penalty ...`) **learned value ยังถูกเป๊ะ** (fruit 30→6 เมื่อเปิดพิษ + food-mult 3) **แต่พฤติกรรมการเลี่ยงแทบไม่เกิด** (fruit% 48→45) เพราะ:

- `mean_energy ≈ 1–2` ทุกการตั้งค่า (แม้เพิ่มพลังงานอาหาร 3× ลด drain 5×) → agent **หิวเรื้อรัง** จาก**คอขวด foraging เชิงพื้นที่** (เข้าไม่ถึงอาหาร ไม่ใช่อาหารพลังงานน้อย)
- ประตู `_food_worth_eating` มี floor "หิวจัด (energy ≤ 6) กินทุกอย่าง" (สมจริง) → เมื่อหิวตลอด floor นี้กลบการเลี่ยง

**นี่คือรากเดียวกับทุกปัญหาในโครงการ:** การเลี่ยงอาหารพิษ (เช่นเดียวกับการวัด heritability/allometry ในประชากรจริง) **จะ emerge ก็ต่อเมื่อแก้ foraging access ก่อน** — Toxin นี้จึงยืนยัน binding constraint เดิมอีกทางหนึ่ง (สอดคล้อง `lifespan_masks_starvation`)

---

## 4. ไฟล์ที่แก้ + knobs + tests

| ไฟล์ | การเปลี่ยนแปลง |
|---|---|
| `world/metabolism.py` | เพิ่ม `raw_fruit` (composition/mass/size) |
| `world/environment.py` | `FOOD_RAW_FRUIT` + FOOD_ENERGY + 3 knobs + `_spawn_toxic_food` |
| `agents/agent.py` | `_apply_toxin` + telemetry (`toxin_ingested_total`, `toxin_damage_total`) + hook ในเส้นทางกิน |
| `simulation/runner.py` | telemetry พิษต่อ agent |
| `scripts/run_toxin_diet_study.py` | **ใหม่** — controlled avoidance study |
| `tests/test_toxin.py` | **ใหม่** — 9 tests |
| `scripts/food_value_study_driver.py`, `run_long_emergence_watch.py` | CLI + env forwarding (ไฟล์ปน WIP — ยังไม่ commit) |

**knobs (default 0 = ปิด → byte-identical):** `toxin_acute_penalty`, `toxin_damage_coeff`, `toxic_food_spawn_per_tick`
**tests:** 9 ใหม่ (off byte-identical, acute ลดพลังงาน, chronic เพิ่ม damage, tolerance gene บรรเทา, learned value สะท้อนพิษ, เลี่ยงเมื่อรู้จักอาหารดีกว่า) · **suite รวม 86/86 ผ่าน**

---

## 5. รันยังไง

```bash
python scripts/run_toxin_diet_study.py          # controlled: เห็นการเลี่ยงชัด (OFF กิน, ON เลี่ยง)
python tests/test_toxin.py                       # unit tests
# ในซิมเต็ม (การเลี่ยงจะเด่นเมื่อแก้ foraging แล้ว):
python scripts/food_value_study_driver.py --model v2 --ticks 800 --value-learning \
  --toxic-food 3 --toxin-acute-penalty 50 --toxin-damage-coeff 5 --aging --mortal ...
```

---

## 6. อนาคต (ตามที่คุยไว้ — trade-off ซ้อนชั้น)

- **immune system:** `parasite → damage` แต่ภูมิคุ้มกัน**กินพลังงานเหมือน maintenance** → trade-off ซ้อน (พลังงาน ↔ ภูมิ ↔ สืบพันธุ์) — โครงเดียวกับ `_apply_toxin`/`_apply_aging` ต่อยอดได้เลย
- **fruit หลายชนิด (A/B/C)** พลังงาน/พิษต่างกัน → optimal diet ที่ซับซ้อนขึ้น + selection บน `toxin_tolerance`
- **ผูก chronic toxin เข้ากับ aging** ให้เห็น lineage ที่กินพิษเยอะอายุสั้น → selection (ต้องมีประชากรเสถียรก่อน)
- **เพิ่ม raw_fruit เข้า diet-metrics telemetry** (ตอนนี้ track แค่ seed/plant) เพื่อวัด skip ของ fruit ในซิมเต็มโดยตรง

**ก่อนอื่น (blocker เดิม):** แก้ foraging access ให้ agent ไม่หิวเรื้อรัง แล้วผลการเลี่ยง + selection จะโผล่ในประชากรจริง

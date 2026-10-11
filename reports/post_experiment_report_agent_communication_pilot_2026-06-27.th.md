# รายงานหลังทดลอง: Agent Communication / Social Transmission Pilot

**วันที่:** 2026-06-27  
**สถานะ:** Post-experiment report  
**Pre-report:** `reports/pre_experiment_plan_agent_communication_pilot_2026-06-27.th.md`  
**Data directory:** `data/agent_communication_pilot_20260627/`  
**เป้าหมาย:** ตรวจว่าการเลี่ยง `raw_seed` ในรอบ food-value learning มีหลักฐานเบื้องต้นของ social transmission หรือยังอธิบายได้ด้วย individual learning

---

## Abstract

รัน pilot 5 seeds โดยใช้ current telemetry ของ `food_value_memory`, `meals_by_type`, `skipped_food_by_type`, และ `agent_diet_summary` เพื่อทดสอบ negative evidence เบื้องต้นต่อ claim เรื่องการสื่อสาร/การบอกต่อระหว่าง agent ผลรวมจาก 60 agents พบว่า 57 agents skip `raw_seed` แต่ **0 agents** skip `raw_seed` ในสถานะ `strict_no_own_taste` ตามนิยามเข้มล่าสุด (`raw_seed_meals == 0`, `plant_meals == 0`, และไม่มี memory ของทั้งสองชนิด) agent ที่ skip ทั้งหมดอยู่ในกลุ่ม `self_tasted_both_then_skipped_seed` คือเคยกินทั้ง seed และ plant แล้วจึงเริ่ม skip seed

ข้อสรุป: pilot นี้สนับสนุน individual learning และยังไม่พบ social-transmission candidate อย่างไรก็ตาม ยังไม่สามารถสรุปเรื่อง communication เต็มรูปแบบ เพราะยังไม่มี `counterfactual_available_foods`, `exposure_events`, ghost teacher, signal shuffle, หรือ receiver-blind control

---

## 1. Introduction

กราฟรวมจาก food-value learning เคยแสดงว่าเมื่อเวลาผ่านไป agent กิน `raw_seed` ลดลงและ skip seed เพิ่มขึ้น แต่กราฟรวมยังตอบไม่ได้ว่า pattern นี้เกิดจาก:

1. agent แต่ละตัวเรียนรู้จาก reward ของตัวเอง
2. agent เลียนแบบ/รับอิทธิพลจาก agent อื่น
3. shared environment หรือ food availability ทำให้ดูเหมือนเรียนพร้อมกัน
4. มี communication signal จริง

การทดลองนี้จึงเป็น pilot เพื่อทดสอบขั้นต่ำก่อน: มี agent ใด skip seed โดยไม่มีประสบการณ์ตรงกับทั้ง target และ comparator หรือไม่

---

## 2. Methods

### 2.1 Configuration

| parameter | value |
| --- | --- |
| seeds | `20260610`-`20260614` |
| runs | 5 |
| ticks | 600 |
| model | v2 |
| body index | 37 |
| population | 12 |
| world | 40x40 |
| low-value food | `raw_seed`, 6 per tick |
| food-value learning | enabled |
| food energy multiplier | 50 |
| metabolic drain multiplier | 0.1 |
| max population | 40 |
| mortality | immortal founders |

Command template:

```powershell
python scripts\food_value_study_driver.py --seed <seed> --model v2 --ticks 600 --output data\agent_communication_pilot_20260627\runs\seed_<seed> --low-value-food 6 --value-learning --food-energy-mult 50 --drain-mult 0.1 --population 12 --world 40 --max-pop 40 --dump data\agent_communication_pilot_20260627\runs\seed_<seed>.json
```

### 2.2 Operational Definition

ใช้ strict no-own-taste:

```text
strict_no_own_taste =
raw_seed_meals == 0
AND plant_meals == 0
AND learned_raw_seed_value is absent
AND learned_raw_plant_value is absent
```

social-transmission candidate ขั้นต่ำ:

```text
strict_no_own_taste_seed_skipper =
raw_seed_skips > 0
AND strict_no_own_taste == true
```

self-learning skipper:

```text
self_tasted_both_then_skipped =
raw_seed_meals > 0
AND plant_meals > 0
AND raw_seed_skips > 0
```

### 2.3 Artifacts

- `data/agent_communication_pilot_20260627/runs/seed_*.json`
- `data/agent_communication_pilot_20260627/aggregate_summary.json`
- `data/agent_communication_pilot_20260627/run_summary.csv`
- `data/agent_communication_pilot_20260627/agent_summary.csv`

---

## 3. Results

### 3.1 Aggregate Results

| metric | value |
| --- | ---: |
| runs | 5 |
| agents observed | 60 |
| agents skipped `raw_seed` | 57 |
| strict no-own-taste seed skippers | **0** |
| mean strict social candidate rate | **0.0** |
| mean self-learning skipper rate | **1.0** |
| agents with learning-speed measurement | 57 |
| mean delta learning ticks | 24.281 |
| min / max delta learning ticks | 1 / 214 |

State totals:

| state | count |
| --- | ---: |
| `self_tasted_both_then_skipped_seed` | 57 |
| `seed_only_no_plant_taste` | 3 |

### 3.2 Per-Seed Summary

| seed | seed skippers | strict no-own-taste skippers | seed meals | plant meals | seed skips | mean delta |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20260610 | 10 | 0 | 108 | 52 | 2163 | 14.1 |
| 20260611 | 12 | 0 | 35 | 55 | 3548 | 18.917 |
| 20260612 | 11 | 0 | 115 | 44 | 2518 | 41.364 |
| 20260613 | 12 | 0 | 19 | 66 | 3192 | 29.833 |
| 20260614 | 12 | 0 | 49 | 71 | 3499 | 16.917 |

### 3.3 Interpretation Of Learning Timing

ทุก agent ที่ skip seed และมี learning-speed field ได้ค่า `first_raw_seed_skip_tick - first_raw_plant_tick` หลังจากเคยมี plant experience แล้ว ความเร็วต่างกันมาก ตั้งแต่ 1 ถึง 214 ticks แปลว่า aggregate curve ที่ดูเหมือน population เปลี่ยนพฤติกรรมพร้อมกัน จริง ๆ เป็น trajectory รายตัวที่ต่างจังหวะ

---

## 4. Hypothesis Testing

### H0: Individual Learning

**Evidence supporting:**

- 57/57 seed skippers เคยมีประสบการณ์ทั้ง `raw_seed` และ `raw_plant`
- strict no-own-taste seed skippers = 0/60
- learned value ข้าม runs คงที่โดยประมาณ: `raw_seed = 50`, `raw_plant = 250`
- agents ที่ยังเป็น `seed_only_no_plant_taste` ไม่ skip seed

**Evidence against:**

- ยังไม่มีหลักฐานเชิงลบต่อ H0 ใน pilot นี้

**Confidence:** กลางถึงสูงสำหรับ claim แคบว่า seed-skip pattern ในเงื่อนไขนี้สอดคล้องกับ individual learning

### H1: Social Transmission Candidate

**Evidence supporting:**

- ไม่พบใน pilot นี้

**Evidence against:**

- strict no-own-taste seed skippers = 0
- strict social candidate rate = 0.0 ทุก seed

**Missing evidence:**

- ยังไม่มี exposure table จึงยังคำนวณ `P(skip | exposure, strict_no_own_taste)` ไม่ได้

**Confidence:** กลางสำหรับ claim ว่า current pilot ยังไม่พบ social-transmission candidate

### H2: Communication

**Evidence supporting:**

- ไม่มี เพราะระบบยังไม่มี explicit communication signal ในการทดลองนี้

**Evidence against:**

- ยังไม่ใช่การทดสอบโดยตรง

**Missing evidence:**

- signal production
- receiver detection
- context dependence
- action-change windows
- fitness horizon
- shuffled signal
- receiver-blind condition

**Confidence:** ต่ำสำหรับ claim เกี่ยวกับ communication เพราะ experiment นี้ยังไม่ instrument signal channel

---

## 5. Discussion

ผลรอบนี้ตอบคำถามเฉพาะได้ค่อนข้างชัด: ใน food-value pilot 5 seeds, การ skip `raw_seed` ยังดูเหมือนมาจากประสบการณ์ตรงของแต่ละ agent มากกว่าการบอกต่อกัน agent ที่ไม่มี plant comparator ยังไม่ skip seed ส่วน agent ที่ skip ล้วนเคยชิมทั้ง seed และ plant แล้ว

แต่ผลนี้ไม่ใช่หลักฐานว่า “ไม่มี social learning ในระบบทั้งหมด” เพราะยังไม่ได้สร้างเงื่อนไข forced exposure, isolation, ghost teacher, หรือ social shuffle ผลที่ควรพูดคือ:

> ในคอนฟิกนำร่องนี้ ยังไม่พบ agent ที่เลี่ยง seed โดยไม่มีประสบการณ์ตรงกับทั้ง seed และ plant; หลักฐานปัจจุบันจึงสนับสนุน individual learning มากกว่า social transmission

---

## 6. Limitations

ข้อจำกัดสำคัญ:

1. ไม่มี `counterfactual_available_foods` จึงยังไม่รู้ว่า ณ decision event agent เห็น seed และ plant พร้อมกันหรือไม่
2. ไม่มี `food_seen`/choice-set event แบบละเอียด
3. ไม่มี `exposure_events` จึงยังแยก `real_teacher`, `ghost_teacher`, `shuffled_teacher`, `no_teacher` ไม่ได้
4. ไม่มี action-change windows 50/100/200 ticks
5. ไม่มี fitness horizon 100/500/1000 ticks
6. ไม่มี communication signal channel
7. ไม่มี parent-child carryover/adoption control
8. เป็น energy-surplus, immortal-founder regime จึงใช้เพื่อ isolate decision learning ไม่ใช่ ecology realism เต็มรูป

---

## 7. Future Work

ขั้นต่อไปที่ควรทำ:

1. เพิ่ม `decision_events.jsonl` ที่มี `visible_foods`, `chosen_food`, `skipped_foods`, `target_available`, `comparator_available`
2. เพิ่ม `exposure_events.jsonl` เพื่อคำนวณ `P(skip | exposure, strict_no_own_taste)`
3. ทำ ghost teacher control แบบ cue-only replay: position/eating/visible action เท่านั้น ไม่มี collision, resource competition, group pull, signal, kinship
4. เพิ่ม action windows: 50, 100, 200 ticks
5. เพิ่ม fitness deltas: 100, 500, 1000 ticks
6. แยก communication จาก cue ด้วย signal shuffle และ receiver-blind condition
7. สำหรับ culture ให้เพิ่ม condition แยก body inheritance จาก memory/social exposure inheritance

---

## 8. Bottom Line

pilot นี้ไม่พบหลักฐานการสื่อสารหรือ social transmission ในข้อมูลที่วัดได้ตอนนี้ ผลที่เห็นสอดคล้องกับ individual learning: agent เลี่ยง seed หลังจากมีประสบการณ์ตรงกับทั้ง seed และ plant แล้ว

claim ที่ปลอดภัย:

> Current multi-seed pilot evidence supports individual food-value learning and provides no strict no-own-taste social-transmission candidates under the tested regime.

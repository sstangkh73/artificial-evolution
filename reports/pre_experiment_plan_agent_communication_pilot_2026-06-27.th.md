# แผนก่อนทดลอง: ตรวจหลักฐานการสื่อสาร/การถ่ายทอดทางสังคมของเอเจนต์แบบ pilot

**วันที่:** 2026-06-27  
**สถานะ:** Pre-experiment report  
**วัตถุประสงค์:** รันชุดทดลองนำร่องเพื่อทดสอบว่า pattern การเลี่ยง `raw_seed` ที่เห็นจากกราฟรวมอธิบายได้ด้วย individual learning หรือมีสัญญาณเบื้องต้นของ social transmission/communication  
**ขอบเขต:** ใช้ telemetry ปัจจุบันของ `food_value_memory`, `meals_by_type`, `skipped_food_by_type`, และ `agent_diet_summary` ยังไม่เพิ่ม explicit signal, ghost teacher, หรือ `counterfactual_available_foods`

---

## 1. Research Question

คำถามหลัก:

> agent ที่เลี่ยง `raw_seed` ทำเช่นนั้นเพราะเรียนรู้จากประสบการณ์ตรงของตัวเอง หรือมีหลักฐานเบื้องต้นว่า agent อื่นมีอิทธิพลต่อพฤติกรรม?

คำถามย่อย:

1. มี agent ที่ skip `raw_seed` โดยยังไม่มีประสบการณ์ตรงกับทั้ง `raw_seed` และ `raw_plant` หรือไม่
2. agent ที่ skip `raw_seed` ส่วนใหญ่เข้ากับ state `self_tasted_both_then_skipped_seed` หรือไม่
3. ผลข้ามหลาย seed สอดคล้องกับรายงาน smoke เดิมหรือไม่

---

## 2. Operational Definitions

### 2.1 Strict No Own Taste

สำหรับ pilot นี้จะคำนวณนิยาม strict จาก summary ราย agent:

```text
strict_no_own_taste =
raw_seed_meals == 0
AND plant_meals == 0
AND learned_raw_seed_value is absent
AND learned_raw_plant_value is absent
```

ถ้า agent เคยกิน `raw_plant` แต่ยังไม่เคยกิน `raw_seed` จะจัดเป็น `partial_experience` ไม่ใช่ naive เต็มรูปแบบ

### 2.2 Knowledgeable

ใน pilot นี้ใช้ proxy จากข้อมูลที่มี:

```text
self_tasted_both_then_skipped_seed =
raw_seed_meals > 0
AND plant_meals > 0
AND raw_seed_skips > 0
```

หมายเหตุ: ยังไม่ได้ใช้ `stable_knowledgeable` แบบ time/event เต็มรูปแบบ เพราะ current output ยังไม่มี event window และ exposure table

---

## 3. Hypotheses

### H0: Individual Learning

agent จะ skip `raw_seed` หลังมีประสบการณ์ตรงกับทั้ง `raw_seed` และ `raw_plant`

หลักฐานสนับสนุน:

- `strict_no_own_taste_seed_skippers = 0`
- state ส่วนใหญ่เป็น `self_tasted_both_then_skipped_seed`
- `delta_learning_ticks` มีค่าหลัง first plant taste

### H1: Social Transmission Candidate

มี agent ที่ skip `raw_seed` โดยไม่มีประสบการณ์ตรงกับทั้ง target และ comparator

หลักฐานสนับสนุน:

- `strict_no_own_taste_seed_skippers > 0`

หมายเหตุ: ถึงพบ H1 candidate ก็ยังเรียกได้แค่ candidate เพราะยังไม่มี exposure/ghost/choice-set control

### H2: Communication

ยังไม่สามารถทดสอบโดยตรงใน pilot นี้ เพราะ current system ยังไม่มี explicit signal channel และยังไม่มี receiver-blind/signal-shuffle condition

---

## 4. Variables

### Independent Variables

- `seed`: 20260610-20260614
- `food_value_learning_enabled`: enabled
- `low_value_food_spawn_per_tick`: 6
- `world`: 40x40
- `population`: 12
- `ticks`: 600
- `body_index`: 37
- `model`: v2
- `food_energy_multiplier`: 50
- `metabolic_drain_multiplier`: 0.1

### Dependent Variables

- number of agents that tasted `raw_seed`
- number of agents that tasted `raw_plant`
- number of agents that skipped `raw_seed`
- number of strict no-own-taste seed skippers
- learning-speed distribution from `first_raw_seed_skip_tick - first_raw_plant_tick`
- state counts in `food_value_learning_state_counts`

### Control Variables

- same world size
- same body type
- same population
- same tick horizon
- same energy-surplus regime
- same low-value-food spawning

---

## 5. Metrics

Primary:

```text
strict_no_own_taste_seed_skippers =
count(agent where raw_seed_skips > 0 AND strict_no_own_taste)
```

```text
strict_social_candidate_rate =
strict_no_own_taste_seed_skippers / agents_observed
```

Secondary:

```text
self_learning_skipper_rate =
agents in self_tasted_both_then_skipped_seed / agents_skipped_raw_seed
```

```text
mean_delta_learning_ticks =
mean(first_raw_seed_skip_tick - first_raw_plant_tick)
```

---

## 6. Success Criteria

สำหรับ pilot นี้ถือว่าสำเร็จถ้า:

1. รันครบ 5 seeds
2. ได้ JSON output ต่อ seed
3. สร้าง aggregate summary ได้
4. ระบุได้ว่า telemetry ปัจจุบันพอหรือไม่พอสำหรับ claim เรื่อง social transmission/communication

---

## 7. Failure Criteria

ถือว่าต้องหยุดหรือปรับ protocol ถ้า:

1. run ไม่ reproducible หรือ fail กลางทาง
2. output ไม่มี `agent_diet_summary`
3. agent ส่วนใหญ่ไม่มี encounter กับทั้ง seed และ plant ทำให้สรุปไม่ได้
4. ผลชี้ social candidate แต่ไม่มี event-level evidence พอจะตีความ

---

## 8. Known Limitations

ข้อจำกัดที่ตั้งใจกำกับไว้ก่อนรัน:

1. ยังไม่มี `counterfactual_available_foods` จึงยังพิสูจน์ไม่ได้ว่า agent เห็น seed และ plant พร้อมกันตอนตัดสินใจ
2. ยังไม่มี `exposure_events` จึงยังคำนวณ `P(skip | exposure, strict_no_own_taste)` ไม่ได้
3. ยังไม่มี ghost teacher control
4. ยังไม่มี explicit communication signal, signal shuffle, หรือ receiver-blind condition
5. ยังไม่มี parent-child adoption/cultural carryover condition

ดังนั้นผลหลังทดลองห้ามสรุปว่า “มี/ไม่มี communication อย่างเด็ดขาด” แต่สรุปได้ว่า current evidence สนับสนุน individual learning หรือมี social-transmission candidate ที่ต้องตามต่อหรือไม่

---

## 9. Planned Commands

รันต่อ seed:

```powershell
python scripts\food_value_study_driver.py --seed <seed> --model v2 --ticks 600 --output data\agent_communication_pilot_20260627\runs\seed_<seed> --low-value-food 6 --value-learning --food-energy-mult 50 --drain-mult 0.1 --population 12 --world 40 --max-pop 40 --dump data\agent_communication_pilot_20260627\runs\seed_<seed>.json
```

หลังจากรันครบ จะสร้าง:

- `data/agent_communication_pilot_20260627/aggregate_summary.json`
- `data/agent_communication_pilot_20260627/agent_summary.csv`
- `reports/post_experiment_report_agent_communication_pilot_2026-06-27.th.md`

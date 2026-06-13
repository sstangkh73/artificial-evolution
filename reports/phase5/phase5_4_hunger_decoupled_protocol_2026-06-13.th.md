# Protocol: Phase 5.4 Hunger-Decoupled Seed Handling

วันที่: 2026-06-13

## Objective

แยกพฤติกรรม seed handling ออกจาก hunger/food loop โดยไม่สอน agent ว่า seed ใช้ปลูก

ผล Phase 5.1-5.3 พบว่า agent-moved seed drops ส่วนใหญ่เกิดใน context `hunger` มากกว่า 94% และแม้ `future_path_lift` จะมากกว่า 1 แต่ `current`, `nearby`, และ `visible` controls ไม่ผ่าน ดังนั้น Phase 5.4 จะทดสอบว่า site-selection signal ยังเหลืออยู่ไหมเมื่อ hunger ไม่ได้เพิ่มโอกาส drop seed โดยตรง

## Research Question

ถ้าลดอิทธิพล hunger ต่อการ drop seed แล้ว agent ยังสามารถสร้าง evidence ของ site selection ได้หรือไม่

## Hypotheses

H5.4a: ถ้า seed site selection เป็นพฤติกรรมจริง ไม่ใช่ผลข้างเคียงจาก hunger, condition ที่ตัด hunger drop bonus ควรยังมี current/nearby/visible lifts ดีขึ้น

H5.4b: ถ้า seed movement ถูก hunger ครอบอยู่จริง, condition ที่ตัด hunger drop bonus จะลด hunger-context fraction แต่ site-selection gate จะยังไม่ผ่าน หรือ activity จะลดลงจนไม่พอ

## Independent Variables

- `seed_hunger_drop_bonus`
  - baseline: `0.06`
  - hunger-neutral: `0.0`
- food signal radius / plant lifecycle food signal
- world size and density
- random seed

## Dependent Variables

- `agent_moved_drop_count`
- `drop_context_fraction_hunger`
- `drop_quality_vs_current_position_lift`
- `drop_quality_vs_nearby_control_lift`
- `drop_quality_vs_visible_control_lift`
- `drop_quality_vs_visible_best_control_lift`
- `drop_quality_vs_future_path_control_lift`
- context-matched lifts by drop context
- high-quality vs low-quality completed chain rate
- late vs early drop quality

## Controls

Primary controls:

1. current-position control
2. nearby control
3. visible average control
4. visible-best diagnostic
5. future-path control

New context controls:

- hunger-only records
- food-contact-only records
- balanced-random-only records

Context-matched metrics must not mix drop contexts when asking whether quality improved.

## Conditions

Core:

1. `baseline_100x100`
2. `hunger_neutral_seed_drop_100x100`
3. `low_food_signal_100x100`

Diagnostics:

4. `large_world_200x200_same_density_long_budget`
5. `large_world_200x200_same_population_long_budget`

## Success Criteria

Phase 5.4 does not require all diagnostics to pass. Core pass requires:

- baseline comparison available
- hunger-neutral activity is not collapsed:
  - `mean_agent_moved_drop_count >= 50`
- hunger-neutral reduces hunger dominance:
  - `mean_drop_context_fraction_hunger < baseline mean`
- at least 3/5 hunger-neutral seeds pass:
  - current lift > 1.10
  - nearby lift > 1.05
  - visible lift > 1.00
  - future-path lift > 1.00
  - high-quality chain rate > low-quality chain rate
  - late/early lift >= 1.05
- directional consistency at least 4/5 seeds

## Failure Criteria

Fail if any of these hold:

- hunger-neutral activity collapses below usable sample size
- hunger-context fraction stays near baseline
- current/nearby/visible controls still remain below threshold
- visible-best diagnostic shows large opportunity gap
- high-quality chain does not beat low-quality chain

## Interpretation Rules

- If future-path lift passes but visible/current/nearby fail, do not claim site selection
- If hunger-neutral reduces drops too much, treat it as evidence that seed behavior is currently coupled to hunger
- If hunger-neutral improves current/visible lifts but chain rates fail, treat it as partial site selection signal, not farming
- If nutrient remains saturated near 1.0, do not overread total quality

## Expected Output

- JSON/CSV run data under `data\phase5_4_hunger_decoupled_*`
- raw markdown run report
- analysis report with Evidence Supporting, Evidence Against, Alternative Explanations, Missing Evidence, and Confidence Level

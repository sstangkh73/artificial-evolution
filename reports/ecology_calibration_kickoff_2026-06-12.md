# Ecology Calibration Kickoff - 2026-06-12

## Objective

เริ่มเฟส calibration ตามแผนล่าสุด เพื่อแยกคำถาม "โลกมี signal ให้เรียนหรือไม่" ออกจากคำถาม "agent เรียนรู้ได้หรือไม่" โดยยังไม่เปลี่ยน policy ของ agent

## Implementation

เพิ่ม runner ใหม่:

`scripts/run_ecology_calibration.py`

หน้าที่:

- sweep map size, food density, spawn rate, bootstrap duration, post-bootstrap multiplier, natural seed rain
- เรียก `scripts/run_long_emergence_watch.py::run_watch` ซ้ำหลาย config
- เก็บผลราย run เป็น JSON + log
- สรุปเป็น `runs.csv`, `aggregate.csv`, `summary.json`
- เพิ่ม metric สำหรับ ecology ignition:
  - `ignition_score`
  - `ticks_per_second`
  - `seed_to_germinated_rate`
  - `germinated_to_matured_rate`
  - `matured_to_fruited_rate`
  - `fruit_to_consumed_rate`
- เพิ่ม plant death reason counter ใน watcher:
  - `plant_died_no_biomass`
  - `plant_died_max_age`
  - `plant_died_low_viability`

## Runs

Smoke sweep:

```powershell
python scripts\run_ecology_calibration.py --output-dir data\ecology_calibration_smoke_20260612 --seeds 20260610 --map-sizes 40,100 --max-food-per-100-cells 20 --base-food-spawn-values 4 --food-spawn-multiplier-values 0.70 --bootstrap-food-spawn-ticks-values 300 --post-bootstrap-multiplier-values 0.10 --natural-seed-rain-values 0 --time-limit-seconds 12 --progress-every-seconds 30 --event-sample-limit 500
```

100x100 targeted probe:

```powershell
python scripts\run_ecology_calibration.py --output-dir data\ecology_calibration_100x100_probe_20260612 --seeds 20260610 --map-sizes 100 --max-food-per-100-cells 20 --base-food-spawn-values 4 --food-spawn-multiplier-values 0.70 --bootstrap-food-spawn-ticks-values 300 --post-bootstrap-multiplier-values 0.10 --natural-seed-rain-values 0 --time-limit-seconds 45 --progress-every-seconds 15 --event-sample-limit 800
```

## Results

Smoke result, `40x40`:

- `tick`: about 1,700 in 12 seconds
- `ticks_per_second`: about 143.56
- `seed_germinated`: 58
- `plant_matured`: 3
- `plant_fruited`: 7
- `natural_seed_dropped`: present
- status: `plant_food_fate_without_consumption`

Smoke result, `100x100`:

- `tick`: about 499 in 12 seconds
- `ticks_per_second`: about 41.62
- `seed_germinated`: 7
- `plant_matured`: 0
- `plant_fruited`: 0
- status: `seed_germinated`

100x100 targeted 45-second result:

- `ticks_per_second`: about 42.8
- `seed_germinated`: 14
- `plant_matured`: 0
- `plant_fruited`: 0
- `plant_died_no_biomass`: 14
- `plant_died_max_age`: 50
- `plant_died_low_viability`: 0
- `mean_hunger_level`: 0.983

## Interpretation

The 40x40 ecology loop ignites quickly under the probe-like food density. The 100x100 world does not ignite under the same per-area food cap within the tested wall-clock budget. It reaches germination, but seedlings fail before maturity and many seeds age out.

This falsifies the simplest hypothesis that full scale only failed because `max_food` was too low. Even with `max_food_per_100_cells=20`, the 100x100 setting remains stuck before maturity. The likely causes are a mix of:

- lower simulation throughput at larger world/resource counts
- seed establishment sites not matching sustained light/water/nutrient growth windows
- hunger lock keeping agents from creating useful disturbance/revisit patterns
- plant growth/maturity timing too strict for sparse full-scale ecology

## Current Status

We now have a repeatable calibration tool. The project is ready to run controlled ecology sweeps before making any claim about agent learning.

Current scientific claim:

> Probe-scale ecology works. Full-scale ecology still fails before mature/fruit stage under the tested settings. Therefore the next blocker is ecology calibration, not agent intelligence evaluation.

## Next Steps

1. Run a real sweep across `70x70` and `100x100` with multiple seeds.
2. Add plant establishment modifiers as experimental knobs instead of hardcoding changes:
   - seed max age multiplier
   - sprout biomass loss rate
   - plant growth rate
   - germination good ticks
3. Test whether `natural_seed_rain=1` can bootstrap ecology without teaching agents.
4. Only after full-scale `plant_fruited > 0` in at least 70% of seeds, run learning metrics:
   - revisit index
   - fruit reward revisit
   - seed contact to later plant/fruit chain
   - agent-level specialization

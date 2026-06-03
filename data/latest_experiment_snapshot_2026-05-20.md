# Latest Experiment Snapshot - 2026-05-20

## Scenario

- branch state: current local exploratory branch
- benchmark body: `body_8`
- population: `50`
- max_ticks: `4000`
- seeds: `8010, 8012, 8014, 8016`

## Per-seed results

| Seed | Final Tick | Extinct | Peak Population | Births | Matured Children | Achieved Survivors | Stored Food Total |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 8010 | 81 | yes | 56 | 6 | 1 | 0 | 0 |
| 8012 | 201 | yes | 56 | 6 | 1 | 1 | 3 |
| 8014 | 201 | yes | 58 | 8 | 2 | 1 | 8 |
| 8016 | 133 | yes | 56 | 6 | 0 | 1 | 0 |

## Aggregate

- mean_final_tick: `154.0`
- mean_peak_population: `56.5`
- mean_total_births: `6.5`
- mean_matured_children: `1.0`
- mean_achieved_survivors: `0.75`
- mean_stored_food_total: `2.75`
- extinctions: `4/4`
- non_extinct_runs: `0/4`

## Interpretation

- ระบบล่าสุดยังไม่ผ่านกำแพง `non-extinction`
- reproduction เกิดขึ้นแล้ว แต่ replacement rate ยังต่ำมาก
- storage เริ่มมีในบาง seed แต่ยังไม่ทบต้นเป็น settlement economy
- benchmark นี้ถูกใช้เป็น `C1` ใน `update_progress_log`

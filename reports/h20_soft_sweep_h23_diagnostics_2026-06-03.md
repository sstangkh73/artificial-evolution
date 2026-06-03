# รายงานอัตโนมัติ H20 Soft Sweep / H23 Temporal Synchronization

- body_index: `14`
- initial_population: `250`
- max_population: `375`
- max_ticks: `800`
- seeds: `7, 8, 11, 13`
- output: `C:\artificial-evolution\data\hypothesis_diagnostics\h20_soft_sweep_h23_2026-06-03`

| Condition | Births | Matured | Gen1 Births | 2nd Wave | Exact Ready | Gen1 Ready | Gen1 Spawn | Final Tick |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 6.0 | 2.0 | 0.0 | 0.00 | 6.0 | 0.0 | 0.0 | 132.0 |
| `h13_parent_child_overlap` | 6.2 | 6.0 | 0.2 | 0.25 | 6.2 | 0.2 | 0.2 | 128.0 |
| `h17_lower_birth_cost` | 9.0 | 2.8 | 0.0 | 0.00 | 9.0 | 0.0 | 0.0 | 157.5 |
| `h20a_litter_cap_only` | 6.0 | 2.0 | 0.0 | 0.00 | 6.0 | 0.0 | 0.0 | 132.0 |
| `h20b_soft_birth_spacing` | 6.0 | 2.0 | 0.0 | 0.00 | 6.0 | 0.0 | 0.0 | 132.0 |
| `h20c_household_buffer_only` | 3.0 | 1.8 | 0.0 | 0.00 | 3.0 | 0.0 | 0.0 | 150.2 |
| `h20d_first_birth_free_repeat_gated` | 6.0 | 2.0 | 0.0 | 0.00 | 6.0 | 0.0 | 0.0 | 132.0 |
| `h20e_temporal_window_matching` | 6.0 | 2.0 | 0.0 | 0.00 | 6.0 | 0.0 | 0.0 | 132.0 |
| `i_h1_h11` | 6.5 | 5.8 | 0.5 | 0.25 | 6.5 | 0.5 | 0.5 | 195.5 |
| `i_h20a_h13` | 6.2 | 6.0 | 0.2 | 0.25 | 6.2 | 0.2 | 0.2 | 128.0 |
| `i_h20b_h13` | 6.2 | 6.0 | 0.2 | 0.25 | 6.2 | 0.2 | 0.2 | 128.0 |
| `i_h20c_h13` | 3.0 | 2.5 | 0.0 | 0.00 | 3.0 | 0.0 | 0.0 | 159.5 |
| `i_h20d_h13` | 6.2 | 6.0 | 0.2 | 0.25 | 6.2 | 0.2 | 0.2 | 128.0 |
| `i_h20d_h13_h21` | 6.2 | 6.0 | 0.2 | 0.25 | 6.2 | 0.2 | 0.2 | 169.2 |
| `i_h20d_h13_h22` | 6.2 | 6.0 | 0.2 | 0.25 | 6.2 | 0.2 | 0.2 | 145.0 |
| `i_h20e_h13` | 6.2 | 6.0 | 0.2 | 0.25 | 6.2 | 0.2 | 0.2 | 128.0 |

## ไฟล์ข้อมูล

- `runs.json`: `C:\artificial-evolution\data\hypothesis_diagnostics\h20_soft_sweep_h23_2026-06-03\runs.json`
- `runs.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h20_soft_sweep_h23_2026-06-03\runs.csv`
- `condition_summary.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h20_soft_sweep_h23_2026-06-03\condition_summary.csv`
- `female_decisions.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h20_soft_sweep_h23_2026-06-03\female_decisions.csv`
- `decision_trace.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h20_soft_sweep_h23_2026-06-03\decision_trace.csv`

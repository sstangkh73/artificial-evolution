# รายงานผลทดลอง H1-H11 Diagnostic Suite

จัดทำอัตโนมัติจาก `scripts/run_hypothesis_diagnostics.py`

## ขอบเขตการทดลอง

- body_index: `14`
- initial_population: `250`
- max_population: `375`
- max_ticks: `800`
- seeds: `7, 8, 11, 13`
- output: `C:\artificial-evolution\data\hypothesis_diagnostics\h1_h11_2026-06-03`

การทดลองนี้เป็น diagnostic sweep เพื่อเทียบผลเชิงกลไก ไม่ใช่ final publication-grade confirmation. ใช้ seed set เดียวกันทุก condition เพื่อดูทิศทางของผลและ interaction ระหว่างสมมุติฐาน.

## ตารางสรุป condition

| Condition | H | Extinct | Final Tick | Final Pop | Births | Matured | Max Gen | Opp/Female | Birth/Female | Matured Female/Female | Stored | Owner Mismatch |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | baseline | 1.00 | 132.0 | 0.0 | 6.0 | 2.0 | 1.0 | 1.01 | 0.048 | 0.010 | 6.0 | 0.000 |
| `h10_delay_technology` | H10 | 1.00 | 132.0 | 0.0 | 6.0 | 2.0 | 1.0 | 1.01 | 0.048 | 0.010 | 6.0 | 0.000 |
| `h11_extend_reproductive_life` | H11 | 1.00 | 115.5 | 0.0 | 6.0 | 5.2 | 1.0 | 1.25 | 0.047 | 0.020 | 11.8 | 0.001 |
| `h1_breeder_tuned` | H1 | 1.00 | 141.0 | 0.0 | 6.0 | 1.8 | 1.0 | 1.03 | 0.048 | 0.008 | 2.2 | 0.001 |
| `h2_canonical_household` | H2 | 1.00 | 181.2 | 0.0 | 6.2 | 1.8 | 1.2 | 0.99 | 0.050 | 0.006 | 19.2 | 0.000 |
| `h3_pipeline_priority` | H3 | 1.00 | 132.0 | 0.0 | 6.0 | 2.0 | 1.0 | 1.01 | 0.048 | 0.010 | 6.0 | 0.000 |
| `h4_mate_rendezvous` | H4 | 1.00 | 119.0 | 0.0 | 6.0 | 1.0 | 1.0 | 0.98 | 0.048 | 0.008 | 84.0 | 0.000 |
| `h5_soft_cooldown` | H5 | 1.00 | 132.0 | 0.0 | 6.0 | 2.0 | 1.0 | 1.01 | 0.048 | 0.010 | 6.0 | 0.000 |
| `h6_earned_nest_support` | H6 | 1.00 | 41.5 | 0.0 | 0.2 | 0.0 | 0.2 | 0.02 | 0.002 | 0.000 | 0.0 | 0.000 |
| `h7_managed_patch_productivity` | H7 | 1.00 | 126.2 | 0.0 | 6.0 | 2.2 | 1.0 | 0.97 | 0.048 | 0.008 | 10.8 | 0.000 |
| `h8_adult_energy_saver` | H8 | 1.00 | 150.0 | 0.0 | 6.0 | 1.5 | 1.0 | 1.20 | 0.048 | 0.008 | 8.0 | 0.000 |
| `h9_disable_mutation` | H9 | 1.00 | 160.0 | 0.0 | 6.2 | 2.2 | 1.2 | 0.98 | 0.049 | 0.010 | 33.0 | 0.001 |
| `i_h1_h11` | Interaction | 1.00 | 195.5 | 0.0 | 6.5 | 5.8 | 1.2 | 1.28 | 0.051 | 0.021 | 167.2 | 0.001 |
| `i_h2_h4_h11` | Interaction | 1.00 | 121.5 | 0.0 | 6.2 | 5.2 | 1.2 | 1.08 | 0.049 | 0.020 | 1.0 | 0.000 |
| `i_h6_h7` | Interaction | 1.00 | 35.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02 | 0.000 | 0.000 | 0.0 | 0.000 |
| `i_reproduction_stack` | Interaction | 1.00 | 156.2 | 0.0 | 6.0 | 5.8 | 1.0 | 1.21 | 0.047 | 0.020 | 54.0 | 0.000 |

## อ่านผลเร็ว

- Baseline มี mean final tick `132.0`, births `6.0`, matured `2.0`, opportunity windows/female `1.01`.
- Share adult females below 2 opportunities ใน baseline = `0.97`.
- เงื่อนไขที่ matured children สูงสุด:
  - `i_h1_h11`: matured `5.8`, births `6.5`, opp/female `1.28`
  - `i_reproduction_stack`: matured `5.8`, births `6.0`, opp/female `1.21`
  - `h11_extend_reproductive_life`: matured `5.2`, births `6.0`, opp/female `1.25`
  - `i_h2_h4_h11`: matured `5.2`, births `6.2`, opp/female `1.08`
  - `h7_managed_patch_productivity`: matured `2.2`, births `6.0`, opp/female `0.97`
- เงื่อนไขที่เพิ่ม opportunity windows สูงสุด:
  - `i_h1_h11`: opp/female `1.28`, matured `5.8`
  - `h11_extend_reproductive_life`: opp/female `1.25`, matured `5.2`
  - `i_reproduction_stack`: opp/female `1.21`, matured `5.8`
  - `h8_adult_energy_saver`: opp/female `1.20`, matured `1.5`
  - `i_h2_h4_h11`: opp/female `1.08`, matured `5.2`
- เงื่อนไขที่ collapse/สูญพันธุ์เด่น:
  - `i_h6_h7`: extinction `1.00`, final tick `35.0`, matured `0.0`
  - `h6_earned_nest_support`: extinction `1.00`, final tick `41.5`, matured `0.0`
  - `h11_extend_reproductive_life`: extinction `1.00`, final tick `115.5`, matured `5.2`
  - `h4_mate_rendezvous`: extinction `1.00`, final tick `119.0`, matured `1.0`
  - `i_h2_h4_h11`: extinction `1.00`, final tick `121.5`, matured `5.2`

## Reproduction Opportunity Bottleneck

ตัวชี้วัดสำคัญใน suite นี้คือ `mean_opportunity_windows`: จำนวนหน้าต่างโอกาส reproduction ต่อ adult female lifetime โดยประมาณ. ถ้าค่านี้ต่ำกว่า 2 และ `matured_female_children_per_adult_female` ต่ำกว่า 1 แปลว่าระบบมี fertility ceiling แม้ stored food จะสูง.

## Interaction Notes

- `i_h1_h11`: delta matured vs baseline `3.8`, delta opportunities `0.27`, extinction `1.00`.
- `i_h2_h4_h11`: delta matured vs baseline `3.2`, delta opportunities `0.08`, extinction `1.00`.
- `i_h6_h7`: delta matured vs baseline `-2.0`, delta opportunities `-0.99`, extinction `1.00`.
- `i_reproduction_stack`: delta matured vs baseline `3.8`, delta opportunities `0.21`, extinction `1.00`.

## ไฟล์ข้อมูลดิบ

- `runs.json`: `C:\artificial-evolution\data\hypothesis_diagnostics\h1_h11_2026-06-03\runs.json`
- `runs.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h1_h11_2026-06-03\runs.csv`
- `condition_summary.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h1_h11_2026-06-03\condition_summary.csv`
- `female_lifetimes.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h1_h11_2026-06-03\female_lifetimes.csv`

## ข้อจำกัด

- เป็น diagnostic intervention ผ่าน monkeypatch ในสคริปต์ ไม่ใช่ patch ถาวรของ simulation core.
- sample seeds มีจำกัดเพื่อให้ทดลองครบ H1-H11 ได้ในเวลาสั้น.
- interaction ที่ดีควรถูกนำไปรันซ้ำแบบ publication-grade batch ก่อนสรุปเป็นข้อค้นพบหลัก.

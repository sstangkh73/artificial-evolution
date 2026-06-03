# รายงานผลทดลอง H12-H18 Reproduction Chain Diagnostic Suite

จัดทำอัตโนมัติจาก `scripts/run_reproduction_chain_diagnostics.py`

## ขอบเขตการทดลอง

- body_index: `14`
- initial_population: `250`
- max_population: `375`
- max_ticks: `800`
- seeds: `7, 8, 11, 13`
- output: `C:\artificial-evolution\data\hypothesis_diagnostics\h12_h18_2026-06-03`

การทดลองนี้เป็น diagnostic sweep เพื่อดู second-wave reproduction, parent-child overlap, food liquidity, energy debt, birth cost, and settlement-trap interactions. ใช้ seed set เดียวกันทุก condition เพื่อดูทิศทางของผล.

## ตารางสรุป condition

| Condition | H | Extinct | Final Tick | Births | Matured | Gen1 Births | 2nd Wave | Max Gen | Gen1 Ready | Parent-Child Overlap | Liquidity Fail | Food Gap | Nest Left |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | baseline | 1.00 | 132.0 | 6.0 | 2.0 | 0.0 | 0.00 | 1.0 | 0.00 | 2.2 | 402.2 | 18.9 | 85.5 |
| `h11_extend_reproductive_life` | H11 | 1.00 | 115.5 | 6.0 | 5.2 | 0.0 | 0.00 | 1.0 | 0.00 | 8.0 | 808.0 | 15.9 | 99.8 |
| `h12_second_wave_support` | H12 | 1.00 | 132.0 | 6.0 | 2.0 | 0.0 | 0.00 | 1.0 | 0.00 | 2.2 | 402.2 | 18.9 | 85.5 |
| `h13_parent_child_overlap` | H13 | 1.00 | 128.0 | 6.2 | 6.0 | 0.2 | 0.25 | 1.2 | 0.08 | 6.0 | 1078.2 | 14.8 | 97.2 |
| `h14_food_liquidity` | H14 | 1.00 | 129.5 | 6.0 | 2.0 | 0.0 | 0.00 | 1.0 | 0.00 | 2.5 | 402.5 | 18.9 | 75.5 |
| `h15_role_protection` | H15 | 1.00 | 123.5 | 6.0 | 2.2 | 0.0 | 0.00 | 1.0 | 0.00 | 0.0 | 335.5 | 18.2 | 115.8 |
| `h16_energy_debt_relief` | H16 | 1.00 | 195.8 | 6.0 | 6.0 | 0.0 | 0.00 | 1.0 | 0.00 | 5.7 | 2082.5 | 14.9 | 219.0 |
| `h17_lower_birth_cost` | H17 | 1.00 | 157.5 | 9.0 | 2.8 | 0.0 | 0.00 | 1.0 | 0.00 | 2.8 | 864.8 | 20.7 | 118.5 |
| `h18_settlement_commute` | H18 | 1.00 | 124.8 | 6.0 | 2.0 | 0.0 | 0.00 | 1.0 | 0.00 | 0.0 | 398.0 | 18.9 | 77.0 |
| `i_h12_h13` | Interaction | 1.00 | 123.8 | 6.2 | 6.0 | 0.2 | 0.25 | 1.2 | 0.08 | 6.0 | 1077.0 | 14.8 | 94.2 |
| `i_h12_h14` | Interaction | 1.00 | 129.5 | 6.0 | 2.0 | 0.0 | 0.00 | 1.0 | 0.00 | 2.5 | 402.5 | 18.9 | 75.5 |
| `i_h13_h17` | Interaction | 1.00 | 150.5 | 9.0 | 8.2 | 0.0 | 0.00 | 1.0 | 0.00 | 1.5 | 1782.2 | 16.3 | 152.8 |
| `i_h14_h15` | Interaction | 1.00 | 123.5 | 6.0 | 2.2 | 0.0 | 0.00 | 1.0 | 0.00 | 0.0 | 335.5 | 18.2 | 115.8 |
| `i_h16_h17` | Interaction | 1.00 | 176.2 | 9.0 | 8.8 | 0.0 | 0.00 | 1.0 | 0.00 | 5.1 | 2907.2 | 16.8 | 176.2 |
| `i_h1_h11` | H1+H11 | 1.00 | 195.5 | 6.5 | 5.8 | 0.5 | 0.25 | 1.2 | 0.17 | 2.1 | 1006.0 | 12.7 | 316.5 |
| `i_h1_h11_h14_h17` | Interaction | 1.00 | 104.0 | 12.0 | 9.8 | 0.0 | 0.00 | 1.0 | 0.00 | 2.5 | 1170.5 | 19.8 | 63.0 |

## อ่านผลเร็ว

- Baseline มี mean final tick `132.0`, births `6.0`, matured `2.0`, opportunity windows/female `1.01`.
- Baseline gen1 births `0.0`, second-wave success rate `0.00`, parent-child adult overlap `2.2`.
- เงื่อนไขที่ matured children สูงสุด:
  - `i_h1_h11_h14_h17`: matured `9.8`, births `12.0`, gen1 births `0.0`
  - `i_h16_h17`: matured `8.8`, births `9.0`, gen1 births `0.0`
  - `i_h13_h17`: matured `8.2`, births `9.0`, gen1 births `0.0`
  - `h13_parent_child_overlap`: matured `6.0`, births `6.2`, gen1 births `0.2`
  - `h16_energy_debt_relief`: matured `6.0`, births `6.0`, gen1 births `0.0`
- เงื่อนไขที่ second wave ดีสุด:
  - `i_h1_h11`: gen1 births `0.5`, success rate `0.25`, max gen `1.2`
  - `h13_parent_child_overlap`: gen1 births `0.2`, success rate `0.25`, max gen `1.2`
  - `i_h12_h13`: gen1 births `0.2`, success rate `0.25`, max gen `1.2`
  - `baseline`: gen1 births `0.0`, success rate `0.00`, max gen `1.0`
  - `h11_extend_reproductive_life`: gen1 births `0.0`, success rate `0.00`, max gen `1.0`
- เงื่อนไขที่ parent-child adult overlap สูงสุด:
  - `h11_extend_reproductive_life`: overlap `8.0`, gen1 births `0.0`, matured `5.2`
  - `h13_parent_child_overlap`: overlap `6.0`, gen1 births `0.2`, matured `6.0`
  - `i_h12_h13`: overlap `6.0`, gen1 births `0.2`, matured `6.0`
  - `h16_energy_debt_relief`: overlap `5.7`, gen1 births `0.0`, matured `6.0`
  - `i_h16_h17`: overlap `5.1`, gen1 births `0.0`, matured `8.8`
- เงื่อนไขที่ collapse/สูญพันธุ์เด่น:
  - `i_h1_h11_h14_h17`: extinction `1.00`, final tick `104.0`, matured `9.8`
  - `h11_extend_reproductive_life`: extinction `1.00`, final tick `115.5`, matured `5.2`
  - `h15_role_protection`: extinction `1.00`, final tick `123.5`, matured `2.2`
  - `i_h14_h15`: extinction `1.00`, final tick `123.5`, matured `2.2`
  - `i_h12_h13`: extinction `1.00`, final tick `123.8`, matured `6.0`

## Second-Wave Diagnostic Notes

ตัวชี้วัดสำคัญใน suite นี้คือ `mean_gen1_births` และ `second_wave_success_rate`. ถ้า H ใดเพิ่ม final tick หรือ stored food แต่ไม่เพิ่ม gen-1 births แปลว่ายังเป็น wealth/survival effect ไม่ใช่ reproduction-chain fix.

## Interaction Notes

- `i_h12_h13`: delta gen1 births vs baseline `0.2`, delta matured `4.0`, extinction `1.00`.
- `i_h12_h14`: delta gen1 births vs baseline `0.0`, delta matured `0.0`, extinction `1.00`.
- `i_h13_h17`: delta gen1 births vs baseline `0.0`, delta matured `6.2`, extinction `1.00`.
- `i_h14_h15`: delta gen1 births vs baseline `0.0`, delta matured `0.2`, extinction `1.00`.
- `i_h16_h17`: delta gen1 births vs baseline `0.0`, delta matured `6.8`, extinction `1.00`.
- `i_h1_h11_h14_h17`: delta gen1 births vs baseline `0.0`, delta matured `7.8`, extinction `1.00`.

## ไฟล์ข้อมูลดิบ

- `runs.json`: `C:\artificial-evolution\data\hypothesis_diagnostics\h12_h18_2026-06-03\runs.json`
- `runs.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h12_h18_2026-06-03\runs.csv`
- `condition_summary.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h12_h18_2026-06-03\condition_summary.csv`
- `female_lifetimes.csv`: `C:\artificial-evolution\data\hypothesis_diagnostics\h12_h18_2026-06-03\female_lifetimes.csv`

## ข้อจำกัด

- เป็น diagnostic intervention ผ่าน monkeypatch ในสคริปต์ ไม่ใช่ patch ถาวรของ simulation core.
- sample seeds มีจำกัดเพื่อให้ทดลองครบ H12-H18 ได้ในเวลาสั้น.
- interaction ที่ดีควรถูกนำไปรันซ้ำแบบ publication-grade batch ก่อนสรุปเป็นข้อค้นพบหลัก.

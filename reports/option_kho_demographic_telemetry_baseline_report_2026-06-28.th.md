# รายงานฉบับเต็ม งาน ข.0-ข.1: telemetry ประชากรและ baseline demographic crash ในโลก access-fixed

**โครงการ:** Artificial Evolution (TURC2026)
**วันที่:** 2026-06-28
**ผู้วิจัย:** Chisanupong
**สถานะ:** ข.0 เสร็จและ verify แล้ว · ข.1 baseline seed เดียวสำเร็จเชิงวินิจฉัย แต่ยังไม่ใช่ multi-seed conclusion
**ต่อจาก:** `reports/PLAN_option_kho_demographic_stabilization_2026-06-28.th.md` และ `reports/option_ga_foraging_access_results_2026-06-28.th.md`
**artifact หลัก:** `data/option_kho_demographic_stabilization_20260628/baseline_sync_seed20260610.json`

---

## บทคัดย่อ

งาน ข มีเป้าหมายแก้คอขวดประชากรหลังงาน ก แก้ foraging access แล้ว: ทำให้ประชากร mortal อยู่รอดข้ามหลาย generation ในโลกที่มีอาหารพืชจริง, depletable carrying capacity, ไม่มี uniform food crutch, และไม่มีการบังคับรอดด้วยการลด drain แบบไม่ซื่อสัตย์

งานรอบนี้ทำ 2 ส่วน:

1. **ข.0: เพิ่ม telemetry วินิจฉัยประชากรที่ขาด** ได้แก่ local food-per-capita, age structure, cohort/death-wave CV, R0-by-density proxy, และ K estimator จาก birth/death balance windows
2. **ข.1: รัน baseline seed เดียวในโลก access-fixed/honest** เพื่อเช็คว่า telemetry อ่านสัญญาณ demographic ที่แผนทำนายได้จริงหรือไม่

ผลหลัก: telemetry ใหม่ทำงานและผ่าน test suite (`67/67`). baseline seed `20260610` สูญพันธุ์ที่ tick `549`, peak population `148`, births `114`, death reasons หลักคือ `lifespan_completed=123`, `starvation=37`, `durability_depleted=4`. ที่สำคัญคือ global food-per-capita สูงขึ้นหลัง crash (`5.20` ที่ tick 200 -> `19.83` ที่ tick 400) แต่ local food-per-capita รอบ cluster เป็น `0.0` ทั้งสองจุด ขณะเดียวกัน death-window CV สูง `0.9322`. นี่สนับสนุนภาพที่งาน ก และแผน ข คาดไว้: access/global food ไม่ใช่คอขวดหลักอีกแล้ว แต่ระบบติด **local depletion + synchronized death wave + delayed demographic crash**

ข้อสรุปแบบ conservative: **ข.0 ผ่าน gate** เพราะ telemetry พร้อมและ default เป็น opt-in. **ข.1 seed เดียว characterize baseline ได้แล้ว** แต่ยังไม่พอประกาศ claim หลาย seed. ขั้นต่อไปคือ ข.2: รัน combination `constant-hazard mortality + density brake` บน K จริง แล้วเทียบกับ baseline นี้

---

## 1. ปัญหาและคำถามวิจัย

### 1.1 ปัญหาหลังงาน ก

งาน ก แก้ foraging access สำเร็จแล้วด้วย plant economy + sensing/continuous vision:

- พืชไม่ดับสนิทอีกต่อไป
- agent เห็นหรือเข้าถึงอาหารพืชได้มากขึ้น
- access-fixed mortal runs ยังสูญพันธุ์ แต่สาเหตุเลื่อนจาก access/energy ไปเป็น spatial-demographic

คอขวดที่เหลือคือ:

- **clustering vs dispersal tension:** home-fidelity ช่วยให้เจอคู่ แต่ทำให้ local food depletion
- **Allee effect:** กระจายออกไปกินอาหารได้ แต่หาคู่ยาก
- **synchronized lifespan death:** founder/cohort death เป็นคลื่นใหญ่
- **R0 knife-edge:** reproduction สูงเกินไปเกิด boom-bust, ต่ำเกินไปเกิด fade

### 1.2 คำถามวิจัยของงาน ข

> ถ้าโลกมี K จริงแล้ว การรวม de-synchronized mortality กับ density-dependent reproduction brake จะทำให้ประชากร converge รอบ K แทนการ boom-bust หรือ fade ได้หรือไม่?

ก่อนตอบคำถามนี้ ต้องมี telemetry ที่วัดให้ตรงจุดก่อน ไม่อย่างนั้นจะตีความผิดระหว่าง global abundance, local depletion, death wave, และ R0-by-density

---

## 2. สมมติฐาน

### H-ข

ถ้าใช้โลกที่งาน ก ทำให้ honest แล้ว คืออาหารพืชจริง, depletable, access แก้แล้ว, ไม่มี uniform crutch:

- ที่ density ต่ำ อาหารต่อหัวสูง -> R0 ควรมากกว่า 1
- เมื่อเข้าใกล้ K อาหารต่อหัวลด -> density brake ควร throttle reproduction
- constant-hazard mortality ควรลบ synchronized death wave
- ถ้า feedback เร็วพอ ประชากรควร converge รอบ K แทน boom-bust

### Null / failure model

แม้มี K จริง ระบบอาจยังสูญพันธุ์ถ้า:

- local depletion แรงกว่า global food signal
- maturation/reproduction lag ยาวเกินไป
- constant hazard ลด fecundity ต่ำกว่า replacement
- mate-finding และ cluster tension เป็น structural

---

## 3. สิ่งที่เพิ่มใน ข.0

### 3.1 Telemetry ใหม่

เพิ่ม opt-in flag ใน `scripts/run_long_emergence_watch.py`:

```bash
--demographic-telemetry
--demographic-local-radius
--demographic-density-bin-size
--demographic-age-bucket-size
```

เมื่อเปิด flag จะเพิ่มข้อมูลดังนี้:

| telemetry | จุดประสงค์ | ตำแหน่ง output |
|---|---|---|
| local food-per-capita | แยก local depletion จาก global abundance | `population_trajectory[*].local_food_per_capita`, `demographic_telemetry.final_local_food_per_capita` |
| age structure | ดู cohort sync และ generation overlap | `population_trajectory[*].age_structure`, `demographic_telemetry.final_age_structure` |
| birth/death windows | วัด boom-bust/death wave เป็น window ไม่ใช่ cumulative | `births_window`, `deaths_window`, `death_window_cv` |
| R0-by-density proxy | ดู matured/female offspring ต่อ mother แยกตาม population bin | `demographic_telemetry.r0_by_density` |
| K estimator | หา windows ที่ births ~= deaths เพื่อประมาณ K | `demographic_telemetry.k_estimate` |

### 3.2 Driver support

เพิ่ม pass-through ใน `scripts/food_value_study_driver.py` เพื่อใช้ telemetry ใหม่กับ harness ที่ใช้รัน sweep อยู่แล้ว และแก้ bug operational ให้ `--dump` สร้าง parent directory ก่อนเขียนไฟล์

### 3.3 ความซื่อสัตย์ของ implementation

telemetry นี้เป็น opt-in และอ่าน state หลัง tick เท่านั้น จึงไม่เปลี่ยน behavior/RNG ของ run เดิมเมื่อไม่เปิด flag. ข้อมูลที่เพิ่มมีไว้เพื่อวินิจฉัย ไม่ได้เป็นกลไกช่วยให้ agent รอด

---

## 4. ระเบียบวิธี baseline ข.1

### 4.1 วัตถุประสงค์ของ baseline

baseline นี้ไม่ใช่การพิสูจน์ ข.2 แต่เป็นการตั้ง control ในโลก access-fixed เพื่อดูว่า telemetry ข.0 อ่านสัญญาณที่แผนคาดไว้หรือไม่:

- มี plant economy จริงหรือไม่
- access ยังดีอยู่หรือไม่
- local depletion ต่างจาก global food หรือไม่
- death wave วัดได้หรือไม่
- K estimator เห็น convergence หรือเห็น crash

### 4.2 Config ที่ใช้

รัน seed เดียว `20260610`, model `v2`, mortal, body `14`, world `100x100`, initial population `50`, max population `600`, ticks target `800`, access-fixed/honest world:

```powershell
$env:PYTHONHASHSEED='0'
python scripts\food_value_study_driver.py `
  --seed 20260610 `
  --model v2 `
  --ticks 800 `
  --mortal `
  --body 14 `
  --world 100 `
  --population 50 `
  --low-value-food 0 `
  --natural-seed-rain 12 `
  --initial-plants 2500 `
  --food-detection-threshold 0.01 `
  --vision-horizon 200 `
  --scaffolded `
  --home-fidelity `
  --continuous-repro `
  --continuous-repro-rate 0.1 `
  --continuous-repro-food-target 0 `
  --starvation-death `
  --starvation-tolerance 15 `
  --repro-max-age 300 `
  --repro-litter-min 2 `
  --drain-mult 0.1 `
  --max-pop 600 `
  --demographic-telemetry `
  --dump data\option_kho_demographic_stabilization_20260628\baseline_sync_seed20260610.json `
  --output data\option_kho_demographic_stabilization_20260628\baseline_sync_seed20260610
```

### 4.3 ตัวแปร

| ประเภท | ค่า |
|---|---|
| Independent variable | ไม่มีใน baseline seed เดียวนี้ เป็น control run |
| Dependent variables | survival, births, death reasons, population trajectory, local/global food-per-capita, age structure, death-window CV, R0-by-density, K estimate |
| Control variables | access fix จากงาน ก, plant-only food, no low-value uniform crutch, home-fidelity ON, continuous reproduction ON, no density brake |
| Success ของ ข.1 | telemetry อ่านสัญญาณ demographic ได้ และ baseline crash ถูก characterize ได้ |
| Failure ของ ข.1 | telemetry ว่าง, plant economy ไม่ทำงาน, หรือผลยังตีความไม่ได้ว่า local/global/death-wave ต่างกันอย่างไร |

---

## 5. ผลลัพธ์

### 5.1 ข.0: telemetry ผ่าน gate

ผล validation:

| รายการ | ผล |
|---|---|
| unit tests เฉพาะ telemetry + density brake | ผ่าน |
| full test suite | `67/67` ผ่าน |
| `py_compile` | ผ่าน |
| CLI smoke `run_long_emergence_watch.py --demographic-telemetry` | ผ่าน |
| driver smoke `food_value_study_driver.py --demographic-telemetry` | ผ่าน |
| `git diff --check` | ผ่าน |

สรุป: ข.0 ผ่าน gate ด้านเครื่องมือแล้ว

### 5.2 ภาพรวม baseline

| metric | ค่า |
|---|---:|
| stop reason | `population_extinct` |
| final tick | `549` |
| final population | `0` |
| peak population | `148` |
| births | `114` |
| plant matured | `1602` |
| plant fruited | `5348` |
| plant lifecycle food consumed | `2598` |
| total plant meals | `2737` |
| birth-window CV | `0.7895` |
| death-window CV | `0.9322` |

### 5.3 Death reasons

| death reason | count |
|---|---:|
| lifespan_completed | 123 |
| starvation | 37 |
| durability_depleted | 4 |

การตายจาก lifespan_completed เป็นสาเหตุหลัก ชี้ว่า baseline นี้ไม่ได้ล้มเพราะอาหารโลกไม่มี แต่ล้มด้วย cohort/demographic timing เป็นหลัก โดยมี starvation เป็นตัวร่วมจาก local depletion

### 5.4 Plant economy และ access ยังทำงาน

หลักฐานว่าโลกยังเป็น access-fixed/honest:

| tick | population | standing food | global food/capita | mean food dist | frac sensing food |
|---:|---:|---:|---:|---:|---:|
| 200 | 148 | 756 | 5.20 | 3.6 | 0.70 |
| 400 | 46 | 895 | 19.83 | 6.9 | 0.78 |

แปลว่า agent ยังเข้าถึงอาหารในระดับ global/vision ได้ดีพอสมควร และอาหารพืชมีอยู่จริง ไม่ใช่โลกว่างแบบก่อนงาน ก

### 5.5 Local depletion: signal ที่แผน ข ต้องการวัด

| tick | population | global food/capita | local food/capita | mean local agents |
|---:|---:|---:|---:|---:|
| 200 | 148 | 5.20 | 0.0 | 56.0 |
| 400 | 46 | 19.83 | 0.0 | 10.0 |

นี่คือผลที่สำคัญที่สุดของ baseline: global food/capita ดูเหมือนดีขึ้นหลัง crash แต่ local food/capita รอบ cluster ยังเป็น `0.0`. ดังนั้น global standing food หลอกตาได้จริงตามที่แผน ข.0 ระบุไว้

ข้อควรระวัง: local radius ที่ใช้คือ `3` ซึ่งตรงกับ home radius ใน config แต่ยังเป็นนิยามแคบ ต้อง sweep radius เช่น `3/6/10/20` ในงานถัดไปเพื่อแยกว่า depletion เกิดเฉพาะ core home area หรือกินพื้นที่กว้างกว่า

### 5.6 Cohort/death-wave signal

| window | births_window | deaths_window | death_window_cv |
|---:|---:|---:|---:|
| tick 200 | 102 | 4 | 0.0 |
| tick 400 | 12 | 114 | 0.9322 |

เกิด boom แล้วตามด้วย death wave ชัดเจน:

- ช่วงแรก births มากกว่า deaths มาก (`102` vs `4`)
- ช่วงถัดมา deaths มากกว่า births มาก (`114` vs `12`)
- death-window CV สูง `0.9322`

นี่คือ baseline ที่ดีสำหรับเทียบ ข.2 เพราะถ้า constant hazard ทำงานจริง death-window CV ควรลดลง

### 5.7 Age structure

| tick | mean age | stage pattern |
|---:|---:|---|
| 200 | 164.69 | old 80, adult 44, juvenile 10, child 14 |
| 400 | 226.46 | old 42, adult 4 |

tick 400 เหลือ adult เพียง 4 ตัว และประชากรส่วนใหญ่เป็น old. แปลว่า reproductive pipeline ไม่เติมทัน death wave

### 5.8 R0-by-density proxy

R0-by-density ใน run นี้ถูกนิยามแบบ conservative เป็น proxy: ลูกที่เกิดใน population bin ใด แล้วรอดถึงวัย adult เทียบกับ mothers ใน bin นั้น

| population bin | mothers | births | matured offspring | matured female offspring | female replacement proxy |
|---|---:|---:|---:|---:|---:|
| 50-59 | 5 | 10 | 10 | 6 | 1.20 |
| 60-69 | 5 | 10 | 10 | 3 | 0.60 |
| 70-79 | 5 | 10 | 10 | 8 | 1.60 |
| 80-89 | 5 | 10 | 10 | 10 | 2.00 |
| 90-99 | 9 | 18 | 18 | 18 | 2.00 |
| 100-109 | 5 | 10 | 10 | 6 | 1.20 |
| 110-119 | 5 | 10 | 10 | 0 | 0.00 |
| 120-129 | 6 | 12 | 12 | 1 | 0.17 |
| 130-139 | 5 | 10 | 10 | 4 | 0.80 |
| 140-149 | 7 | 14 | 14 | 14 | 2.00 |

อ่านแบบระวัง:

- offspring maturation rate เป็น `1.0` ทุก bin เพราะลูกเกิดช่วงต้นและโตทันก่อน crash
- female replacement proxy แกว่งมากเพราะ sample size เล็กและ sex ratio ในแต่ละ bin ไม่เสถียร
- ไม่ควรใช้ตารางนี้ประกาศว่า R0 stable หรือ unstable เชิง population-level ใน seed เดียว
- ใช้ได้ในฐานะ telemetry sanity check ว่าเราสามารถผูก birth density -> offspring maturation ได้แล้ว

### 5.9 K estimator

K estimator หา window ที่ births ~= deaths ไม่เจอ:

| field | ค่า |
|---|---|
| candidate balance windows | 0 |
| nearest balance tick | 400 |
| nearest balance population | 46 |
| standing food | 895 |
| food/capita | 19.83 |
| births_window | 12 |
| deaths_window | 114 |
| balance error | 102 |

สรุป: baseline นี้ไม่ได้ converge รอบ K. มัน boom แล้ว crash ผ่าน K ไปเลย จึงยังไม่มีจุด births ~= deaths ให้ estimate K แบบ logistic ได้

---

## 6. การตีความ

### 6.1 สิ่งที่ข้อมูลสนับสนุน

1. **ข.0 จำเป็นจริง:** global food/capita สูงไม่ได้แปลว่า agent รอบ cluster มีอาหาร
2. **local depletion มีสัญญาณตรง:** local food/capita เป็น 0.0 ขณะที่ standing food ยังเหลือหลายร้อย
3. **death wave มีจริง:** death-window CV สูงและ deaths window กระโดดจาก 4 เป็น 114
4. **access ไม่ใช่คอขวดหลักใน run นี้:** frac_sensing food 0.70-0.78 และ plant meals 2737 แปลว่า agent ยังหาอาหารได้ในระดับหนึ่ง
5. **baseline ไม่ converge:** K estimator ไม่มี balance window

### 6.2 สิ่งที่ข้อมูลยังไม่พิสูจน์

1. ยังไม่ได้พิสูจน์ว่า de-synchronized death + density brake จะรอด
2. ยังไม่ได้พิสูจน์ว่า local depletion เป็นสาเหตุเดียวของ extinction
3. ยังไม่ได้แยก Allee effect จาก local depletion ด้วย home OFF / elastic home / mate-search controls ในรอบนี้
4. ยังไม่ได้ทำ multi-seed จึงไม่ควร claim robustness
5. R0-by-density ยังเป็น proxy ใน seed เดียว ไม่ใช่ estimate สุดท้าย

---

## 7. กรอบ hypothesis-testing

| หมวด | หลักฐาน |
|---|---|
| Evidence supporting H-ข | มี K/plant economy จริง, access ยังดี, death wave วัดได้, local food-per-capita แยกจาก global food ได้แล้ว |
| Evidence against / pressure on H-ข | baseline crash เร็วมาก, ไม่มี balance window, local depletion เป็น 0.0 แม้อาหารโลกเหลือเยอะ |
| Alternative explanations | local radius อาจแคบเกินไป, home-fidelity อาจบังคับ cluster มากเกินธรรมชาติ, sex-ratio variance ใน bin ทำให้ R0 proxy แกว่ง, initial founder cohort ยัง sync |
| Missing evidence | multi-seed baseline, home OFF baseline, radius sweep, constant hazard sweep, density brake sweep, combined hazard+brake run |
| Confidence | ข.0 telemetry works = สูง. ข.1 baseline failure mode = ปานกลางถึงสูงสำหรับ seed นี้. claim population-wide = ยังต่ำจนกว่าจะ multi-seed |

---

## 8. Decision gates

| gate | สถานะ | หลักฐาน |
|---|---|---|
| ข.0 telemetry อ่านได้ | ผ่าน | output มี local food-per-capita, age structure, death CV, R0-by-density, K estimator |
| default/opt-in safety | ผ่าน | flag default off, tests ผ่าน |
| ข.1 baseline characterize ได้ | ผ่านแบบ seed เดียว | extinct tick 549, death-wave CV 0.9322, local/global food contrast ชัด |
| K convergence ใน baseline | ไม่ผ่าน | candidate balance windows = 0 |
| พร้อมเข้า ข.2 | พร้อมเชิงเครื่องมือ | มี baseline metric สำหรับเทียบ hazard+brake |

---

## 9. งานถัดไป: ข.2

ข.2 ควรใช้ baseline เดิมเป็น control แล้วเปิด combination:

- `--stochastic-mortality`
- `--mortality-constant-hazard`
- `--continuous-repro-food-target`
- sweep `continuous-repro-rate`

### 9.1 Sweep ที่แนะนำ

| axis | values เริ่มต้น |
|---|---|
| mortality mode | age-ramp baseline, constant hazard |
| constant hazard | 0.005, 0.01, 0.015, 0.02 |
| food target | 0, 4, 6, 8, 10, 12 |
| repro rate | 0.03, 0.05, 0.07, 0.1 |
| seeds | เริ่ม 3 seeds สำหรับ screen, ขยายเป็น 5+ เมื่อเจอ promising cell |

### 9.2 Metrics ที่ต้องดูใน ข.2

| metric | success direction |
|---|---|
| survival duration | เพิ่มขึ้นชัด เกินหลาย lifespan |
| death-window CV | ลดจาก baseline 0.9322 |
| birth-window CV | ลดจาก baseline 0.7895 |
| K estimator | เริ่มมี balance windows |
| local food-per-capita | ไม่เป็น 0 ตลอดใน cluster |
| R0-by-density | low density > 1, near K -> 1 |
| peak/trough ratio | ลด ไม่ boom-bust |

### 9.3 คำสั่ง template สำหรับ ข.2

```powershell
$env:PYTHONHASHSEED='0'
python scripts\food_value_study_driver.py `
  --seed 20260610 `
  --model v2 `
  --ticks 2000 `
  --mortal `
  --body 14 `
  --world 100 `
  --population 50 `
  --low-value-food 0 `
  --natural-seed-rain 12 `
  --initial-plants 2500 `
  --food-detection-threshold 0.01 `
  --vision-horizon 200 `
  --scaffolded `
  --home-fidelity `
  --continuous-repro `
  --continuous-repro-rate 0.05 `
  --continuous-repro-food-target 8 `
  --starvation-death `
  --starvation-tolerance 15 `
  --stochastic-mortality `
  --mortality-constant-hazard 0.01 `
  --repro-max-age 300 `
  --repro-litter-min 2 `
  --drain-mult 0.1 `
  --max-pop 600 `
  --demographic-telemetry `
  --dump data\option_kho_demographic_stabilization_20260628\h02_seed20260610_rate005_target8_hazard001.json `
  --output data\option_kho_demographic_stabilization_20260628\h02_seed20260610_rate005_target8_hazard001
```

---

## 10. ข้อจำกัด

1. **n=1 baseline:** ใช้เพื่อ validate telemetry และ characterize failure mode เบื้องต้น ไม่ใช่ final claim
2. **sampling interval 200 ticks:** death wave ระหว่าง sample อาจละเอียดกว่านี้ ควรเพิ่ม option sampling interval ถ้าต้องการดู wave shape
3. **local radius = 3:** ตรง home radius แต่แคบ อาจต้อง radius sweep
4. **R0 proxy ยังหยาบ:** matured offspring นับเมื่อรอดถึง adult แต่ยังไม่แยก survival-to-reproductive-success ลึกพอ
5. **K estimator ต้องการ run ที่ไม่ crash เร็ว:** baseline ไม่มี balance window จึง estimate K ไม่ได้
6. **performance:** continuous vision มี cost สูง ควรระวังเมื่อทำ multi-seed/sweep ใหญ่

---

## 11. ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | บทบาท |
|---|---|
| `scripts/run_long_emergence_watch.py` | เพิ่ม demographic telemetry helpers, trajectory fields, final JSON summary |
| `scripts/food_value_study_driver.py` | เพิ่ม CLI pass-through และแก้ dump directory creation |
| `tests/test_demographic_telemetry.py` | unit tests สำหรับ helper metrics |
| `data/option_kho_demographic_stabilization_20260628/baseline_sync_seed20260610.json` | baseline artifact ของ ข.1 |

---

## 12. สรุปสุดท้าย

งานรอบนี้ยังไม่ได้ทำให้ประชากรรอด แต่ทำสิ่งที่จำเป็นก่อนการแก้จริง: **ทำให้ระบบเห็นสาเหตุที่ต้องเห็น**. ก่อนหน้านี้ global food-per-capita อาจทำให้เข้าใจผิดว่าอาหารพอแล้ว แต่ telemetry ใหม่แสดงว่าใน cluster อาหารเป็น 0 ขณะอาหารโลกยังเหลือมาก และ death wave วัดได้ตรงด้วย CV สูง

ดังนั้นข้อสรุปที่ซื่อสัตย์คือ:

> ข.0 ผ่านแล้ว. ข.1 baseline seed แรกยืนยันว่าโลก access-fixed ยัง crash ด้วย local depletion + synchronized death wave และยังไม่ converge รอบ K. งานถัดไปต้องทดสอบ ข.2: constant-hazard mortality + density brake บน telemetry ชุดใหม่นี้

ถ้า ข.2 ลด death-window CV และสร้าง balance windows ได้ จะเป็นหลักฐานแรกว่า demographic stabilization เริ่มเกิดจริง. ถ้ายังสูญพันธุ์ทุก cell จะเป็น honest negative ที่ชี้ว่าคอขวดเป็น structural กว่านั้น เช่น mate-finding, maturation lag, หรือ clustering/dispersal tension ที่ต้องใช้กลไก ข.3

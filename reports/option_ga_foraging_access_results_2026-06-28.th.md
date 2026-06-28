# รายงานผล งาน ก: แก้ foraging access — พืชล้วน + กลิ่น สร้าง access เพียงพอได้จริง (ยังติดคอขวดพลังงาน/ประชากร)

**Option GA results: a seed-rain plant economy + decoupled food-sensing ("smell") restores real foraging access on plant-only food (no uniform crutch); mortal survival is now gated by the energy/demography frontier, not access**

ผู้วิจัย: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-28
สถานะ: ก.1–ก.3 สำเร็จ (วัดตรง, byte-identical, 61/61 tests) · ก.4 (integration mortal) = honest negative — access แก้แล้วแต่ประชากรยังสูญพันธุ์, คอขวดเลื่อนไป spatial-demographic (multi-seed n=3 ยืนยัน)
ต่อจาก: `PLAN_option_ga_foraging_access_fix_2026-06-27` + `SESSION_REPORT_extinction_investigation_2026-06-27`

---

## 0. บทคัดย่อ

แผน ก ตั้งสมมติฐานว่าการสูญพันธุ์มีรากที่ **foraging access** (agent รับรู้อาหารได้แค่รัศมีสายตา ~4 + พืชผลิต standing crop น้อย). งานนี้ทดสอบเป็นเฟสด้วย immortal probe (แยก access ออกจากการตาย) แล้วปิดท้ายด้วย integration mortal.

**ผลสรุปชี้ขาด:** งาน ก **แก้ foraging access ได้สำเร็จจริง** — ด้วย seed rain (ปลุก plant ecology) + sensing radius (กลิ่น) agent กระจายตัวเข้าถึงอาหารพืชล้วนจน **energy เกินดุลมหาศาล (mean energy 200–550 ที่ drain สมเหตุผล)** โดยไม่ใช้ uniform crutch. **แต่ประชากร mortal ยังสูญพันธุ์ทุกชุด** — และเพราะ access แก้แล้ว การสูญพันธุ์จึงไม่ได้มาจากเศรษฐกิจพลังงาน/foraging (รากที่ 5 เส้นทางเดิมชี้) อีกต่อไป แต่**เลื่อนไปคอขวดชั้นใหม่ = spatial-demographic**: ความขัดแย้งระหว่าง **การกระจุก (เพื่อหาคู่) vs การกระจาย (เพื่อหากิน)** — home-fidelity ทำให้เกิด **local food depletion** (อดตายแม้อาหารทั้งโลกเหลือ ~1000) ส่วนการกระจายทำให้หาคู่ไม่ได้ (Allee) บวกกับการตายแบบ synchronized lifespan. **นี่คือความก้าวหน้า: root cause ถูกเลื่อนลึกไปอีกชั้นอย่างมีหลักฐาน** — เป็น honest negative ที่ระบุคอขวดถัดไปได้แม่นยำ

**ผลหลัก:**
1. **Root cause ลึกกว่าที่ diagnosis เดิมระบุ** — plant lifecycle **ดับสนิท** (germinate/mature/fruit = 0 ทั้งรัน) เพราะโลกไม่เคย seed พืช + `natural_seed_rain_per_tick=0` → knob productivity ที่ดุทั้งหมดคูณกับประชากรพืช 0 (= 0). standing food ~2 คือ ambient `_spawn_food` uniform ล้วน
2. **ก.1 (seed rain):** เปิด seed rain → พืช 0 → ~3,000 ต้นโต, 0 → ~6,800 ผล — เศรษฐกิจพืชล้วนกลับมาได้จริง (ไม่ใช่ crutch)
3. **ก.3 (sensing radius = กลิ่น) คือ lever หลัก** — frac_sensing 0.04 → 0.77, meal rate 6.5× บนอาหารพืชล้วน (ไม่มี uniform crutch); **ก.2 (memory-return) เป็น lever รอง** (เปิด/ปิดต่างกัน <15%) — falsify สมมติฐานเดิมที่ว่า memory เป็นตัวหลัก
4. **ก.4:** access fix สร้าง **K จริง** (standing food แปรผกผันกับประชากร ต่างจาก crutch ที่แบน ~3500) และพิสูจน์ว่า access แก้แล้ว (home OFF → energy surplus 200–550) **แต่ประชากรยังสูญพันธุ์** เพราะคอขวด spatial-demographic (clustering⟂dispersal + lifespan sync) — honest negative ที่เลื่อน root cause ไปอีกชั้น

---

## 1. ภูมิหลังและสมมติฐาน
จาก `SESSION_REPORT_extinction_investigation`: 5 เส้นทางอิสระ (fecundity/brake/wave/lifespan/foraging) ลงรากเดียว = เศรษฐกิจพลังงาน/foraging access. ระบบอยู่บน R₀≈1 knife-edge. แผน ก: ทำให้ agent หาอาหารพืชที่คาดเดาได้ → energy เกินดุล → R₀>1 → ประชากรเสถียร โดย**ไม่เพิ่ม crutch**

**สมมติฐานกลาง (H-ก):** foraging access (sensing range << ความเบาบาง + พืชผลิตน้อย) คือคอขวด; แก้ที่ราก → ประชากรรอด

---

## 2. เครื่องมือที่เพิ่ม (opt-in, default = byte-identical, 61/61 tests)
| กลไก/telemetry | ไฟล์ | knob (default) | จุดประสงค์ |
|---|---|---|---|
| **food_sensing_radius** (ก.3) | `world/environment.py`, `agents/agent.py` `_move_toward_food_signal` | `food_sensing_radius=0` (0=ใช้ min(5,vision) เดิม) | แยกการรับรู้อาหาร (กลิ่น) จากสายตา |
| **food_detection_threshold** (ก.3b) | env `food_signal_at`, `agents/agent.py` `_move_toward_food_signal` | `food_detection_threshold=0.0` (0=hard cutoff เดิม) | vision ต่อเนื่อง 1/d² ไม่มี cutoff (ระยะ=ความสว่าง/threshold); `vision_horizon` = เพดานความโค้งโลก |
| **memory_return_enabled** (ก.2 control) | env, `agents/agent.py` `_act_on_hunger_instinct` | `memory_return_enabled=True` (เดิม) | ปิดเพื่อแยกผล memory-return |
| **initial_plant_population** (ก.4) | env `seed_initial_plants`, runner | `initial_plant_population=0` | วางทุ่งหญ้าโตเต็มวัยที่ t=0 → มี K ตั้งแต่ต้น |
| **multi-radius sensing telemetry** | runner trajectory | (auto) | frac_sensing ที่ r=4/8/12/20 — วินิจฉัย "ใกล้แต่เกินสายตา" |

ยืนยัน byte-identical: default ทุกตัวคงพฤติกรรมเดิม; เทียบ rain4/rain12 ก่อน-หลังแก้โค้ด ตัวเลขตรงเป๊ะ (mature 2955/3578, fruited 4883/5739) · `compileall` OK · 61/61 tests

วิธีวัด: immortal probe (drain ปกติ, agent หิวตลอด → forage ตลอด, แยก access จากการตาย), v2, body 14, world 100×100, pop 50, 1200 ticks, `PYTHONHASHSEED=0`. DV ดึงค่าเฉลี่ยช่วงท้าย (tail 1/3 ของ trajectory)

---

## 3. ก.1 — seed rain ปลุก plant ecology (keystone)

**Root cause (ยืนยันด้วย baseline):** rain0 → plants_seed=48 (harvest drop ที่ depth 0) แต่ germinate/mature/fruit = **0/0/0** ทั้งรัน · standing_food=0 · frac_sensing=0 · mean_food_dist=**40.6** · intake 0.004 vs drain 5.0

| natural_seed_rain | mature | fruited | standing plant food | frac_sensing(สายตา) | meal_rate |
|---:|---:|---:|---:|---:|---:|
| 0 (baseline) | **0** | **0** | 0 | 0.00 | 0.0009 |
| 4 | 2955 | 4883 | 322 | 0.085 | 0.024 |
| 12 | 3578 | 5739 | 51 | 0.04 | 0.035 |
| 30 | 3907 | 6806 | 24 | 0.015 | 0.053 |

**สรุป ก.1:** seed rain (กลไกจริง: seed dispersal/seed bank) ปลุก plant ecology จาก 0 → หลายพันต้น — ส่วนแรกของ H-ก เป็นจริง. แต่ frac_sensing(สายตา) ยังต่ำ (≤0.085) → คอขวดเลื่อนไปที่การรับรู้

**Diagnostic multi-radius (rain12, พฤติกรรม default):** frac_sensing ไต่ตามรัศมี r4=0.04 → r8=0.13 → r12=0.34 → **r20=0.54** → **อาหาร "อยู่ใกล้แต่เกินสายตา"** ไม่ใช่ไกลคนละโซน → ก.3 คือ lever ที่ถูก

---

## 4. ก.2 + ก.3 — sensing radius (กลิ่น) คือ lever หลัก, memory เป็นรอง
ฐาน rain12 (พืชล้วน, ไม่มี uniform crutch):

| config | frac_sensing(สายตา) | meal_rate | intake/tick | เทียบ base |
|---|---:|---:|---:|---:|
| base (สายตา ~4) | 0.04 | 0.035 | 0.176 | 1× |
| memory OFF | 0.04 | 0.0349 | 0.174 | =base |
| food_sensing 8 | 0.32 | 0.104 | 0.521 | 3× |
| food_sensing 12 | 0.54 | 0.165 | 0.826 | 4.7× |
| **food_sensing 20** | **0.77** | **0.229** | **1.147** | **6.5×** |
| sensing12 + memory OFF | 0.51 | 0.145 | 0.726 | (vs sensing12: −12%) |

**สรุป ก.2/ก.3:**
- **ก.3 (กลิ่น) คือ lever หลัก** — sensing 20 ยก meal rate 6.5× (≈59% ของ crutch 0.39) บนอาหารพืชล้วน, frac_sensing ทะลุเกณฑ์ 0.5; justify ชีววิทยา (กลิ่น >> สายตาในการหาอาหาร)
- **ก.2 (memory-return) รอง** — เปิด/ปิดต่างกัน <15% (ที่สายตาล้วน ≈0%) → **falsify** สมมติฐานเดิมว่า memory เป็นตัวหลัก (Phase 2 พิสูจน์ memory return ในงานวางเมล็ด แต่ที่ foraging ทั่วไป gradient ของ sensing สำคัญกว่า)

**Gate ก.1–ก.3: ผ่าน** — frac_sensing > 0.5 บนอาหารพืชล้วน ไม่มี uniform crutch (ผ่าน seed rain + sensing radius)

### 4b. ก.3b — โมเดล vision ฟิสิกส์ (ข้อสังเกตผู้ใช้): ต่อเนื่อง ไม่มี hard cutoff
**ข้อสังเกต:** การมองจริงไม่ตัดหายที่รัศมี — ไกลขึ้นแค่เล็ก/จางลง (intensity ~ 1/d²) จนถึง horizon (ความโค้งโลก). โค้ดเดิมมี 1/d² อยู่แล้ว **แต่** ใส่ **hard cutoff** ที่รัศมีสายตา (เกิน = signal 0 ทันที) = ส่วนที่ไม่เป็นฟิสิกส์ และเป็นต้นเหตุ "gradient แบน → เดินสุ่ม". horizon ที่สเกลโลก (ช่อง~1ม.) = √(2Rh) ~1000+ ช่อง » แมพ → ความโค้งไม่ binding; ตัวจำกัดจริงคือ **detection threshold** (ความคมสายตา) ซึ่งทำให้ระยะเห็น**โผล่จากความสว่างของแหล่งเอง**

**ผล (immortal, rain12, พืชล้วน — เทียบ legacy/radius/continuous):**
| โมเดล | meal_rate | intake/tick | frac_r4 | **mean_food_dist** |
|---|---:|---:|---:|---:|
| legacy hard cutoff (สายตา ~4) | 0.035 | 0.176 | 0.04 | **24.0** |
| food_sensing_radius 20 (เลื่อน cutoff) | 0.229 | 1.147 | 0.77 | (สูง) |
| **ต่อเนื่อง threshold 0.025** | 0.210 | 1.048 | 0.84 | **3.1** |
| **ต่อเนื่อง threshold 0.01** | **0.249** | **1.245** | **0.93** | **2.7** |

**จุดชี้ขาด:** `mean_food_dist` ทรุดจาก **24 → ~3** — ลบ hard cutoff → ไม่มีจุดที่ signal = 0 สนิท → agent ที่อยู่ไกลได้ gradient จางๆ ชี้ทางเสมอ → เดินไปยืนติดอาหาร. **ดีกว่า radius knob** (intake 1.245 > 1.147 = 64% ของ crutch) และระยะเห็นเป็น emergent จากความสว่างแหล่ง (กองใหญ่เห็นไกล) — ตรง thesis "ปล่อยฟิสิกส์ตัดสิน". knob: `food_detection_threshold` (0=off byte-identical), `vision_horizon`; perf ช้ากว่า ~2× (O(n_food)/perception). โมเดลนี้เป็น**รูปแบบที่ถูกต้องเชิงฟิสิกส์ของ ก.3** (radius knob เป็น proxy หยาบ)

---

## 5. ก.4 — integration mortal (เกณฑ์ชี้ขาด)
ฐาน mortal = สูตรแคมเปญ extinction (body14, scaffolded, home-fidelity, continuous-repro, starvation-death, stochastic-mortality, repro-max-age 300, litter-min 2) แล้วถอด food crutch → ใส่ access fix

**5.1 Control vs access-fix (drain÷33 = drain crutch เดิมของแคมเปญ):**
| config | survival | standing food vs pop | ตาย |
|---|---|---|---|
| Control (lvf45 crutch) | extinct t2800, boom-bust | **แบน ~3500** (crutch กินไม่หมด → ไม่มี K) | lifespan 1076 |
| Access-fix (lvf0+rain12+sense20) | extinct t600 | **pop↑→food↓** (255/151 → 1/775) = **K จริง** | lifespan 243 |

→ access fix สร้าง carrying capacity จริง (อาหารพร่องเมื่อ pop สูง) ต่างจาก crutch ที่อาหารแบน แต่ overshoot → Allee crash

**5.2 drain frontier (access fix + initial plants 2500 + density brake) — เผย anomaly:**
| drain_mult (drain_total) | peak | extinct | standing food ตอน crash | deaths |
|---:|---:|---:|---:|---|
| 0.03 (0.15) | 135–230 | t400–800 | — | boom-bust |
| 0.1 (0.5) | 118 | t400 | **998 (เหลือเพียบ)** | starvation 88 |
| 0.2 (1.0) | 46 | t400 | **960** | starvation 88 |
| 0.3 (1.5) | 12 | t200 | **893** | starvation 75 |
| 1.0 (5.0) | bootstrap ไม่รอด | t0 | — | starvation |

**Anomaly:** อาหารทั้งโลกเหลือ ~900–1000 แต่ agent **อดตาย** — ทั้งที่ intake ceiling (immortal) = 1.147 > drain 0.5 → ควรเกินดุล → ชี้ว่าปัญหาเป็น **local** ไม่ใช่ global

**5.3 กลไก: 2×2 home-fidelity × repro rate (drain 0.1) — local depletion ยืนยัน:**
| | home ON | home OFF |
|---|---|---|
| repro 0.1 | starvation **88**, energy ตก | starvation **31**, energy 102→**552** |
| repro 0.03 | starvation 7, energy 45→**14** | starvation 2, energy 116→**217** |

- **home OFF → agent กระจาย → เจออาหารพืชเหลือเฟือ → energy surplus 200–550, แทบไม่อดตาย** = foraging access แก้สำเร็จจริง
- **home ON → กระจุก → local food depletion → energy ต่ำ/อดตาย แม้อาหารทั้งโลกเหลือ ~1000**
- ทุกชุดยังสูญพันธุ์: home OFF ตายเพราะ **Allee** (หาคู่ไม่ได้ → births น้อย → fade ตาม lifespan); home ON ตายเพราะ local depletion + boom-bust

**5.4 continuous vision (ก.3b) ใน mortal — access แก้หมดจด, เหลือ demographic ล้วน:**
| config (drain 0.1) | survival | starvation | ตายหลัก | energy |
|---|---|---:|---|---|
| home ON, hard cutoff (5.3) | t400 | 88 | starvation+lifespan | ตก |
| home ON, **continuous** | t600 | **28** | **lifespan 138** | 71→50 |
| home OFF, **continuous** | t400 | **1** | **lifespan 104** | 150→**267** |

continuous vision **ลด starvation ของ home-ON 88→28** (เห็นแหล่งไกล→ออกไปกินได้ ไม่ติดที่ cluster) และ home-OFF เหลือ starvation = 1 (energy 267) → **access แก้หมดจริง**. แต่ยังสูญพันธุ์ และตอนนี้ตายเพราะ **synchronized lifespan death เป็นหลัก ไม่ใช่ starvation** → ยืนยันว่าคอขวดที่เหลือเป็น **demographic ล้วน** (death-wave + Allee, R₀≈1 knife-edge) ในโลกที่ access แก้แล้ว + อาหารจริง depletable

**สรุป ก.4 (decision gate):** ❌ ประชากรยังไม่รอด — **แต่เป็น honest negative ที่ทรงคุณค่า**: access ไม่ใช่คอขวดอีกต่อไป (พิสูจน์ด้วย energy surplus 200–550 บนพืชล้วน) คอขวดเลื่อนไปชั้น **spatial-demographic** = clustering(หาคู่) ⟂ dispersal(หากิน) tension + synchronized lifespan death. body14 brain แพง (drain 5.0) ทำให้ช่วง drain ที่รอดได้แคบ (≤~0.2 หรือต้องลด brain/ใช้ nest-hearth)

---

## 6. กรอบหลักฐาน (hypothesis-testing)
| | |
|---|---|
| **Supporting H-ก** | access เป็นคอขวดจริง: sensing 20 ยก meal 6.5×; seed rain ปลุกพืช 0→6800 ผล; multi-radius พิสูจน์ "ใกล้แต่เกินสายตา" |
| **Against / ปรับ** | memory-return ไม่ใช่ lever หลัก (ต่างจากสมมติฐานแผน); access เพียงพอ**ไม่พอ**ให้ประชากรรอด — มีคอขวดพลังงาน/ประชากรชั้นถัดไป |
| **Alternative** | คอขวดที่เหลือ = (a) energy: body14 brain แพง (drain 5.0) » intake ceiling 1.147; (b) demography: boom-bust จาก repro ที่ drain ถูก |
| **Confidence** | "access แก้ได้ด้วย seed rain + กลิ่น" = **สูง** (วัดตรง, byte-identical, energy surplus 200–550) · "คอขวดเลื่อนไป spatial-demographic (local depletion + Allee)" = **สูง** (2×2 home×repro ชัด) · "ประชากรยังรอดไม่ได้" = **สูง** (ทุก config extinct) |

---

## 7. การทำซ้ำ
knob ใหม่ทั้งหมดเป็น CLI flags ใน `scripts/food_value_study_driver.py` (default-off = byte-identical):
```bash
# ก.1 immortal probe: เปิด seed rain (เทียบ baseline 0)
PYTHONHASHSEED=0 python scripts/food_value_study_driver.py --model v2 --ticks 1200 --body 14 \
  --population 50 --world 100 --low-value-food 0 --natural-seed-rain 12 --dump rain12.json

# ก.3 sensing radius (กลิ่น): meal rate 6.5x
PYTHONHASHSEED=0 python scripts/food_value_study_driver.py --model v2 --ticks 1200 --body 14 \
  --population 50 --world 100 --low-value-food 0 --natural-seed-rain 12 --food-sensing-radius 20 --dump sense20.json
#   ก.2 control: เพิ่ม --no-memory-return

# ก.4 mortal integration (access fix, ไม่มี uniform crutch)
PYTHONHASHSEED=0 python scripts/food_value_study_driver.py --model v2 --ticks 3000 --mortal --body 14 \
  --world 100 --low-value-food 0 --natural-seed-rain 12 --food-sensing-radius 20 --initial-plants 2500 \
  --scaffolded --home-fidelity --continuous-repro --continuous-repro-rate 0.1 --continuous-repro-food-target 8 \
  --starvation-death --stochastic-mortality --mortality-hazard 0.04 --repro-max-age 300 --repro-litter-min 2 \
  --drain-mult 0.1 --max-pop 600 --dump ga4.json
#   2x2 กลไก: สลับ --home-fidelity (ON/OFF) x --continuous-repro-rate (0.1/0.03)
```
harness วิเคราะห์ batch (scratchpad ชั่วคราว): `ga_probe.py`, `ga_batch.py`, `ga4_analyze.py`

**multi-seed confirm (home ON/OFF × 3 seeds, drain 0.1):** ทิศทาง robust ทุก seed (n=3 ต่อ arm) — **home OFF: max mean-energy เฉลี่ย 380, starvation เฉลี่ย 23; home ON: max mean-energy เฉลี่ย 73, starvation เฉลี่ย 66.** home OFF energy สูงกว่า ~5× (กระจาย→เจออาหาร) แต่ทั้งคู่ extinct (สาเหตุ demographic ไม่ใช่ access) — ยืนยัน local depletion จาก clustering

---

## 8. ข้อสรุปและก้าวต่อไป

**สิ่งที่งาน ก พิสูจน์ได้ (สูง):**
1. plant ecology เคยดับสนิทเพราะ seed rain=0 + ไม่ seed โลก — แคมเปญ extinction ทั้งหมดจึงรันในโลกที่อาหารเป็น ambient uniform + crutch ล้วน (ไม่มี plant economy จริง)
2. seed rain + sensing radius (กลิ่น) ทำให้ agent เข้าถึงอาหารพืชล้วนได้จริง → **energy surplus 200–550** (เกินดุลชัด) โดยไม่มี uniform crutch
3. **foraging access ไม่ใช่ binding constraint อีกต่อไป** — ข้อสรุปนี้กลับทิศจาก 5 เส้นทางเดิม เพราะตอนนี้วัด surplus ได้จริง
4. **vision ฟิสิกส์ (ก.3b, ข้อสังเกตผู้ใช้) คือรูปแบบที่ถูกต้อง** — ลบ hard cutoff → mean_food_dist 24→3, ใน mortal ลด starvation 88→28 (home ON) / →1 (home OFF) → access แก้**หมดจด**, residual extinction กลายเป็น **synchronized lifespan death เป็นหลัก** (ไม่ใช่ starvation)

**คอขวดชั้นใหม่ (หลักฐานชัด, = งานถัดไป):**
- **clustering ⟂ dispersal tension:** หาคู่ต้องกระจุก (home-fidelity) แต่กระจุกทำให้ local food depletion → อดตาย; กระจายแก้ depletion แต่ทำให้ Allee (หาคู่ไม่ได้)
- **synchronized lifespan death** (รากเดิมที่ยังค้าง: R₀≈1 knife-edge)
- **body14 brain แพง** (drain 5.0, 60% เป็น brain) → ช่วง drain ที่รอดได้แคบ

**ทิศทางที่แผนรองรับ (จาก §5 ของแผน — local depletion ถูกทำนายไว้):**
1. **local food-per-capita telemetry** — วัด depletion ที่ home cluster โดยตรง (แทน global)
2. คลายความขัดแย้ง clustering⟂dispersal: ให้ home radius ยืดหยุ่นตามอาหาร / foraging trip ออกไปไกลแล้วกลับ home / mating ไม่ต้องกระจุกถาวร
3. ลด brain cost (cheaper body) หรือใช้ nest+hearth drain reduction (กลไกจริงในโค้ด: near_nest+hearth ลด drain ~2-4) เพื่อให้ drain สมจริงรอดได้
4. แก้ synchronized death ควบคู่ K จริง (constant-hazard + food-K พร้อมกัน)

**กลไกที่เก็บเป็นเครื่องมือ (opt-in, byte-identical):** `food_sensing_radius`, `food_detection_threshold` (+`vision_horizon`), `memory_return_enabled`, `initial_plant_population`, multi-radius sensing telemetry — เพิ่มเข้าคลังเดียวกับ home-fidelity/continuous-repro/density-brake/stochastic-mortality

**นัยต่อ TURC2026/ISEF:** access fix + การเลื่อน root cause เป็น honest structural progress (มีคุณค่าวิทยาศาสตร์) ผลหลัก food-value learning + neuroevolution ยังไม่กระทบ ([[ysc-to-isef-roadmap]])

# รายงานสรุปโปรเจกต์ Artificial Evolution

จัดทำ: 2026-06-20  
ผู้วิจัย: Chisanupong  
อ้างอิง: รายงานทุกฉบับในโปรเจกต์ตั้งแต่ต้นจนถึงปัจจุบัน  
โครงการ: TURC2026

---

## 1. โปรเจกต์นี้คืออะไร และถามว่าอะไร

โปรเจกต์นี้ตั้งคำถามว่า

> ถ้าเราวาง agent ไว้ในโลกจำลองที่มีฟิสิกส์และชีววิทยาพื้นฐาน โดยไม่สอนความหมายของการทำฟาร์ม ไม่บอกว่าเมล็ดคืออะไร ไม่ให้ oracle ใด — agent จะค้นพบความสัมพันธ์ระหว่างอาหาร ตำแหน่ง เมล็ด และพืชได้หรือไม่?

เป้าหมายสูงสุดคือให้ evolution เกิดขึ้นจริงในซิม: agent ตายได้จริง ถ่ายทอดยีนให้ลูก และ selection pressure คัดสรรพฤติกรรมที่อยู่รอดได้ดีกว่า โดยไม่มีผู้ออกแบบบอกว่า "ต้องทำแบบนี้"

ระบบที่สร้างขึ้น ณ ปัจจุบัน มีองค์ประกอบครบ:

- โลก 100×100 แบ่ง 4 zone (safe/danger × food-rich/poor), day/night, seasons, large-animal herds
- body plan: sensor, muscle, armor, brain พร้อม trait space ต่อเนื่อง (memory, planning, cooperation, parenting, fear, metabolism ฯลฯ)
- life stages: child, juvenile, adult, old / sexed reproduction / lineage inheritance
- household, food storage, material storage, breeder-priority allocation, social roles
- tools, hearth, World Physics v2
- telemetry ระดับ publication, dashboard, negative results logging

---

## 2. ไทม์ไลน์ Phase — ผ่าน / ไม่ผ่าน / อยู่ระหว่างทำ

### Phase 1 — Ecology Gate ✅ ผ่าน 5/5

**คำถาม:** โลกจำลองสร้างวงจร `seed → plant → fruit → consumed` ได้เองโดยไม่มี natural seed rain และไม่สอน agent หรือไม่?

**วิธีทดลอง:** โลก 100×100, natural_seed_rain=0, immortal=true, 5 seeds  
**เกณฑ์ผ่าน:** plant_matured > 0 และ plant_fruited > 0 ในอย่างน้อย 70% ของ seeds พร้อม plant food ถูก agent กิน

**ผล:**

| Metric | ค่าเฉลี่ย |
|---|---:|
| seeds ที่ผ่าน | 5/5 |
| seed germinated | 139.0 |
| plant matured | 33.6 |
| plant fruited | 68.6 |
| plant food consumed | 47.8 |
| mean hunger level | 0.983 |

**ความหมาย:** โลกมี ecology signal เสถียรพอสำหรับทดสอบการเรียนรู้ โดยไม่ต้องพึ่ง scaffold ภายนอก  
**ข้อจำกัด:** config ถูก tune เพื่อให้วงจรผ่าน gate, agent เป็น immortal, hunger สูงมาก (0.983)

---

### Phase 2 — Reward-Place Learning ✅ ผ่าน 3/3

**คำถาม:** agent กลับไปยังตำแหน่งที่เคยได้อาหารจากพืชมากกว่าความบังเอิญหรือไม่?

**วิธีทดลอง:** วัด strict-return metric: agent ต้องกินอาหารจากพืช → ออกจาก radius → กลับมาใกล้ตำแหน่งเดิมภายหลัง เทียบ lift กับ random-position baseline

**ผล:**

| seed | consumed | return agents | return lift |
|---|---:|---:|---:|
| 20260610 | 105 | 31 | 52.7× |
| 20260611 | 84 | 24 | 38.7× |
| 20260612 | 131 | 37 | 33.7× |
| **เฉลี่ย** | **106.7** | **30.7** | **41.7×** |

**ความหมาย:** agent มี foraging memory / reward-place association จริง กลับตำแหน่งอาหารมากกว่าความบังเอิญมาก  
**สิ่งที่ยังอ้างไม่ได้:** agent เข้าใจ seed, ตั้งใจปลูก, มีภาษา หรือสื่อสารเรื่องอาหาร

---

### Phase 3 — Seed Causality / Proto-Farming Substrate ✅ ผ่าน 3/3

**คำถาม:** เมล็ดที่ agent ย้ายสามารถเข้าสู่วงจรพืชและกลับมาเป็นอาหารได้จริงหรือไม่?

**จุดเปลี่ยน:** baseline ก่อนแก้ — agent ไม่เคยหยิบเมล็ดเลย (seed_picked=0) เพราะ energy gate กัน  
แก้เฉพาะ substrate-level: หลังกินอาหาร seed primitive ทำงานด้วย food_contact=True โดยไม่บอก semantics

**ผล:**

| seed | moved seeds | completed chains | chain agents | moved/control lift |
|---|---:|---:|---:|---:|
| 20260610 | 172 | 14 | 12 | 1.24× |
| 20260611 | 137 | 17 | 12 | 1.60× |
| 20260612 | 178 | 18 | 14 | 1.36× |
| **เฉลี่ย** | **162.3** | **16.3** | **12.7** | **1.40×** |

**ความหมาย:** agent action เชื่อมกับ delayed ecological consequence ได้ครั้งแรก — proto-farming substrate มีอยู่  
**สิ่งที่ยังอ้างไม่ได้:** agent ตั้งใจปลูก, เลือกพื้นที่จากดิน/แสง/น้ำ, มี concept ของ seed

---

### Phase 4 — Managed Patch ⚠️ ผ่านบางส่วน (claim แคบลงหลัง falsification)

**คำถาม:** agent จัดการ patch ซ้ำ ๆ และกลับมาใช้เป็นประจำหรือไม่?

**Phase 4 เดิม:** patches เกิดจริง, return_agents=50 ทุกรัน — ดูเหมือนดี

**Phase 4.1 (Return-Signal Falsification):**

| condition | pass | return agents | dropper return | non-dropper lift |
|---|---:|---:|---:|---:|
| baseline 100×100 | 3/3 | 50.0 | 0.85 | 31.8× |
| low food signal 100×100 | 3/3 | 50.0 | 0.86 | 22.7× |
| large world 200×200 | 0/3 | 20.0 | 0.35 | 13.1× |

**ข้อสรุปปัจจุบัน:**

> ในโลก 100×100 tuned ecology มี repeated productive seed-drop patches ที่ถูก agent จำนวนมากกลับมาใช้ซ้ำ แต่ยังแยกไม่ได้ว่าเป็น agent-specific managed patch หรือ shared food hotspot

claim ที่ต้องปรับจาก "agent เริ่มจัดการ patch" → "มี patch productivity สูงใน 100×100 แต่ non-dropper return ก็สูงพอกัน"

---

### Phase 5 — Site Selection ❌ ยังไม่ผ่าน

**คำถาม:** agent วางเมล็ดในตำแหน่งที่เหมาะกว่าตำแหน่งที่ถืออยู่จากประสบการณ์หรือไม่?

#### Phase 5.4 — Hunger Decoupling (0/5 seeds)

| condition | pass | moved drops | hunger fraction | current lift |
|---|---:|---:|---:|---:|
| baseline | 0/5 | 79.8 | 0.976 | 0.996 |
| hunger_neutral (ปิด bonus) | 0/5 | 101.8 | 0.982 | 0.986 |
| low_food_signal | 0/5 | 74.0 | 0.982 | 0.996 |

ปิด hunger bonus → critical hunger fraction **เพิ่มขึ้น** (0.976 → 0.982) แสดงว่า bonus ไม่ใช่ตัวครอบหลัก

#### Phase 5.5 — State Decoupled (0/5 seeds ทุก condition)

| condition | drops/run | critical hunger fraction | current lift |
|---|---:|---:|---:|
| baseline | 116.4 | 0.979 | 0.996 |
| critical hunger blocked | 14.0 | 0.000 | 0.959 |
| safe-window only | 15.0 | 0.000 | 0.959 |
| memory disabled | 135.2 | 0.974 | 0.995 |
| memory shuffled | 139.2 | 0.969 | 0.995 |

**ข้อสรุปสำคัญ:** เมื่อบล็อก critical hunger drops activity collapse 116 → 14 drops/run แสดงว่า seed handling ทั้งระบบเป็น epiphenomenon ของ foraging instinct ไม่ใช่ behavior อิสระ · memory ablation ไม่เปลี่ยน pattern = memory ไม่ใช่กลไกหลัก

---

### Population Sustainability ❌ ยังไม่สำเร็จ (negative result เชิงโครงสร้าง)

precondition ของ Phase 6: ประชากร mortal ต้องไม่สูญพันธุ์

#### การค้นพบสำคัญ — Energy Economy Investigation (2026-06-19)

สมมติฐานเดิมหลายข้อผิด:

| สมมติฐานเดิม | ความจริงที่พบ |
|---|---|
| "agent ตายจากการอด" | ตายเพราะอายุขัยทั้ง 50 ตัวที่ tick 133 เป๊ะ (FOUNDER_START_AGE=67 + MAX_AGE=200) |
| "อาหารในโลกน้อยเกินไป" | อาหารเหลือเพียบ (คงค้าง 2,654+) คอขวดคือ access: กิน 1 มื้อ/455 ticks |
| "พลังงานเป็น gate เดียว" | มี 3 gates: ① energy ≥ 92, ② durability ≥ 18, ③ social gates |
| "body 37 สืบพันธุ์ได้" | body 37 armor=0 → durability=10 < 18 → สืบพันธุ์ไม่ได้ตายตัวตลอดกาล |

**งบพลังงาน baseline:**

| รายการ | ค่า /agent/tick |
|---|---:|
| drain: base | 1.0 |
| drain: brain | 2.0 |
| drain: movement | 2.0 |
| drain รวม | **4.99** |
| intake (กินได้จริง) | **0.011** |
| อัตราส่วน drain:intake | **453:1** |

**การสืบพันธุ์ครั้งแรก:** body 38 (armor=2, durability=26) ในสภาวะเกินดุล → births 50 ตัว ประชากร 50→100

#### การสอบสวนพลวัตประชากร (2026-06-20)

Reproduction funnel (อิ่มจริง, energy และ durability แก้แล้ว):

| ด่าน | บล็อก |
|---|---:|
| low_safety | 83% |
| short_pair_bond | 76% |
| low_comfort | 72% |
| short_safety_window | 70% |
| no_mate / mate_stressed | ~45% |
| low_energy / low_durability | 8% |
| **ready จริง** | **8%** |

สาเหตุรากของ social gates: ชั้น settlement/social ปิดเป็น default → agent forage กระจาย ไม่เกาะกลุ่ม → social_buffer ≈ 0 → safety ค้าง 0.53 (ใต้เกณฑ์ 0.66)

**dynamics เป็น bistable — ไม่มีจุดกึ่งกลางเสถียร:**

```
repro ต่ำ → R₀ < 1 → fade ช้า ๆ (ถึง gen 6–8 แล้วจาง)
repro สูง → boom ชนทรัพยากร → cohort crash gen 1–3
ไม่มีจุดกึ่งกลาง
```

**ผล 33+ รัน ทุกชุดสูญพันธุ์:**

| เงื่อนไข | max gen | ผล |
|---|---:|---|
| energy+durability แก้แล้ว (กลไกปกติ) | 1–2 | สูญพันธุ์ |
| ผ่อนประตู + litter2 + life300 | 3 | สูญพันธุ์ |
| สูตรรวมดีสุด (carrying cap + ผ่อน + litter2) | 6 | สูญพันธุ์ |
| เปิด scaffolded (รัง+food-share) | 4 | สูญพันธุ์ |
| continuous logistic repro | 1–2 | births น้อย (หาคู่ไม่เจอ) |
| โลกเล็ก 30×30 + continuous | 2 | สูญพันธุ์ |

**R₀ ceiling เชิงโครงสร้าง (~33 รัน, 6 กลไก):**

| เงื่อนไข | peak pop | births | R₀ | ผล |
|---|---:|---:|---:|---|
| drain0.02 + dense40 | 159 | 128 | 0.72 | สูญพันธุ์ |
| drain0.04 + dense40 | 153 | 140 | 0.74 | สูญพันธุ์ |
| ครบ: drain0.03 + dense45 + ทุกกลไก | 217 | 182 | 0.78 | สูญพันธุ์ |

---

### Metabolism Physics v2 — ฟิสิกส์การกินใหม่ 🔄 อยู่ระหว่างทำ

**แรงจูงใจ:** รื้อระบบการกิน/ย่อย/ขับถ่ายให้ฟิสิกส์ตัดสินแทน hard-code — กินได้/ได้พลังงาน/กระจายเมล็ด emerge จากฟิสิกส์ (gape size, enzyme profile, gut transit)

**Tier 1 Fix 1–3 เสร็จแล้ว (commit c6644c8, d7adb94):**

- Fix 1: ecology gate ยังผ่าน 3/3 seeds — v1 byte-identical
- Fix 2: endozoochory ทำงาน: เมล็ดผ่านท้อง 326 เม็ด/รัน (เทียบ pickup/drop เดิม 93 เม็ด)
- Fix 3: heritability genes (acid_strength, shell_resistance, gut_capacity) ถ่ายทอดได้ — แยก RNG ไม่รบกวน v1

**Blockers ที่พบจากการรันจริง:**

1. **Blocker 1 — args.seed ไม่กระทบผล:** movement RNG ใช้ `Random(agent_id + age)` ไม่ผูกกับ args.seed → 3 seeds ให้ผล identical เป๊ะ = n=1 deterministic ไม่ใช่ n=3 replicates
2. **Blocker 2 — births=0 ในคอนฟิก gate:** คอนฟิก immortal=True, pop 50 ไม่มี birth เลยถึง 9000 ticks → heritability ยังไม่มี offspring แสดงผล → Phase 6 ยังทำไม่ได้

---

## 3. สมมติฐานทั้งหมดตั้งแต่ต้นโปรเจกต์

### 3.1 สมมติฐาน Phase — การเรียนรู้และ proto-farming

| # | สมมติฐาน | ผล |
|---|---|---|
| H-P1 | โลกจะสร้างวงจร seed→plant→fruit→consumed ได้เองโดยไม่มี seed rain | ✅ ยืนยัน — ผ่าน 5/5 seeds |
| H-P2 | agent จะกลับไปตำแหน่งที่เคยได้อาหารจากพืชมากกว่าความบังเอิญ | ✅ ยืนยัน — return lift 41.7× เฉลี่ย |
| H-P3 | เมล็ดที่ agent ย้ายจะเข้าสู่วงจรพืชและกลับมาเป็นอาหาร | ✅ ยืนยัน — moved/control lift 1.40× |
| H-P4a | agent จะเริ่มทิ้งเมล็ดซ้ำในพื้นที่เดิมและกลับมาใช้เป็นประจำ | ⚠️ ยืนยันบางส่วน — patch productivity มีจริงแต่ยังแยกไม่ได้ว่า owned หรือ shared |
| H-P4b | return signal เฉพาะเจาะจงกับ agent ที่วางเมล็ด ไม่ใช่ food attraction ทั่วไป | ❌ ไม่ยืนยัน — non-dropper lift ก็สูงพอ ๆ กัน |
| H-P5 | agent จะวางเมล็ดในตำแหน่งที่มีคุณภาพสูงกว่าตำแหน่งที่ถืออยู่ | ❌ ยังไม่ยืนยัน — 0/5 ทุก condition |
| H-P5h | ปิด hunger drop bonus จะลด hunger dominance ใน seed drops | ❌ ไม่ยืนยัน — critical hunger fraction เพิ่มขึ้นแทน |
| H-P5m | reward memory เป็นกลไกหลักของ site selection | ❌ ไม่ยืนยัน — memory ablation ไม่เปลี่ยน pattern |

### 3.2 สมมติฐาน Stability 11 ข้อ (จากรายงาน 2026-06-02)

| # | สมมติฐาน | ผล |
|---|---|---|
| H1 | ปรับ breeder-priority household allocation จะเพิ่ม replacement rate | ✅ ยืนยัน (ดีที่สุดในตอนนั้น) — mean max gen 7.5, matured children 145, non-extinct short 8/10 แต่ long-loop ยังสูญพันธุ์ |
| H2 | household owner resolution ทำให้อาหารติดผิดรัง | ⚠️ ยืนยันบางส่วน — adult withdrawal fix ช่วยบาง seed แต่ผล mixed |
| H3 | juvenile/newly-adult pipeline คือคอขวดจริง | ⚠️ ยืนยันทางอ้อม — funnel analysis ชี้ว่า adult ที่ผ่านประตูสืบพันธุ์มีเพียง 8% แต่ยังไม่ได้ทดสอบ isolated |
| H4 | mate fragmentation ทำให้ adult พร้อมสืบพันธุ์แต่หา mate/nest ไม่เจอ | ✅ ยืนยัน — no_mate ~45%, short_pair_bond 76% เป็น blockers หลัก |
| H5 | cohort synchronization สร้าง wave collapse แต่ hard cooldown แก้แรงเกินไป | ✅ ยืนยันทั้งคู่ — cohort boom-bust เป็นปัญหาจริง + hard cooldown ทำ extinction 10/10 |
| H6 | nest support สร้าง stored-food surplus หลอก ระบบพึ่ง scaffold | ✅ ยืนยัน — active-nest-only filtering ทดลองแล้วทำให้แย่ลง |
| H7 | settlement productivity ตื้นเกินไป ต้องมี food preservation/managed patch | ⏳ ยังไม่ทดสอบตรง — โปรเจกต์หันไปแก้ energy economy ระดับพื้นฐานก่อน |
| H8 | energy/metabolism balance ทำให้ adult breeder หมดพลังเร็วเกินไป | ⚠️ ยืนยันบางส่วน — drain >> intake เป็นปัญหา แต่สาเหตุที่ใหญ่กว่าคือ: ตายเพราะอายุขัย ไม่ใช่อด และ durability เป็น hard block แยก |
| H9 | endogenous mutation ต้องถูกใช้เป็น adaptive loop จริง | ⏳ ยังไม่ทดสอบ — โครงสร้างสร้างแล้ว (Fix 3 v2) แต่ยังไม่มี births ในคอนฟิก gate |
| H10 | technology เกิดเร็วและรบกวน energy economy | ⏳ ไม่ได้ทดสอบ — โปรเจกต์หันไปแก้ metabolic bottleneck ก่อน |
| H11 | reproduction opportunity ต่อ female lifetime < 2 ทำให้ self-sustain ไม่ได้ | ✅ ยืนยัน — funnel ready rate 8%, social gates บล็อก 70–83% ทีละชั้น, R₀ ≤ 0.88 ทุกชุด |

### 3.3 สมมติฐานใหม่ที่ค้นพบระหว่างการทดลอง

สมมติฐานเหล่านี้ไม่ได้ตั้งมาแต่ต้น แต่ถูกเชื่อโดยปริยายและทดสอบแล้วพบว่าผิด

| สมมติฐานเดิม (เชื่อโดยปริยาย) | ผล |
|---|---|
| "agent ตายจากการอดอาหาร (energy_depleted) เป็นสาเหตุหลัก" | ❌ หักล้าง — ตายเพราะอายุขัยทั้ง 50 ตัวที่ tick 133 เป๊ะ; energy ≤ 0 แค่ reset เป็น 1 ไม่เคยฆ่า |
| "อาหารในโลกน้อยเกินไป เป็นสาเหตุที่ agent ไม่สืบพันธุ์" | ❌ หักล้าง — เติมอาหาร 0→30/tick ขาดดุลพลังงานแทบไม่เปลี่ยน; คอขวดคือ access (กิน 1 มื้อ/455 ticks) |
| "พลังงานเป็นตัว gate เดียวที่บล็อกการสืบพันธุ์" | ❌ หักล้าง — มี 3 gates พร้อมกัน: energy ≥ 92, durability ≥ 18, social gates; body 37 พลังงาน 1,256 ก็ births = 0 |
| "body 37 (social_planner) ที่ใช้ใน gate ทุก experiment สามารถสืบพันธุ์ได้" | ❌ หักล้าง — armor=0 → durability=10 < 18 = เป็นไปไม่ได้เชิงโครงสร้างตลอดกาล |
| "การปรับพารามิเตอร์จะแก้ R₀ < 1 ได้ — แค่ต้องหาค่าที่ถูก" | ❌ หักล้าง — 33+ รัน, 6 กลไก, R₀ ติดเพดาน 0.75–0.88 เสมอ; ระบบ bistable ไม่มีจุดกึ่งกลางเสถียร |
| "3 seeds ที่รันให้ผลแตกต่างกัน = replication จริง" | ❌ หักล้าง — movement RNG ใช้ Random(agent_id + age) ไม่ผูกกับ args.seed; 3 seeds ให้ผล identical ทุก metric |
| "ลด food signal radius แล้ว return signal จะแสดง agent memory ชัด" | ❌ ไม่ยืนยัน — non-dropper lift ยังสูง 22× แม้ลด food signal |

---

## 4. สถานะปัจจุบัน (2026-06-20)

### สิ่งที่ยืนยันได้แล้ว (claim ที่แข็งพอ)

- โลกมีวงจรพืช `seed → plant → fruit → consumed` ที่เสถียรบน 100×100 โดยไม่ต้องมี seed rain
- Agent มี reward-place learning: กลับตำแหน่งอาหารมากกว่าความบังเอิญ (41× lift)
- เมล็ดที่ agent ย้ายสามารถเข้าสู่วงจรชีวภาพและกลับมาเป็นอาหารได้จริง (1.40× lift)
- Perf fix: food-signal spatial grid เร็วขึ้น **76×** byte-identical กับ v1
- Metabolism v2: endozoochory ทำงาน (เมล็ดผ่านท้องและขับออกที่ตำแหน่งใหม่ 326 เม็ด/รัน)
- Deaths ในระบบ mortal เกิดจากอายุขัย ไม่ใช่การอดอาหาร
- Durability คือ hard gate แยกจากพลังงาน: body armor=0 สืบพันธุ์ไม่ได้เชิงโครงสร้าง
- การสืบพันธุ์ครั้งแรกของโปรเจกต์เกิดแล้ว: body 38 → births 50 ตัว ประชากร 50→100

### ปัญหาที่กำลังสอบสวน / ยังต้องแก้

- **R₀ ceiling < 1 เชิงโครงสร้าง:** ทุกชุดสูญพันธุ์ · bistable · ไม่มีจุดกึ่งกลางเสถียร
- **Social gates ครอบงำ:** ready rate 8% ต่อ tick หลังพลังงานและ durability แก้แล้ว
- **Agent กระจายตัว ไม่เกาะกลุ่ม:** social clustering ปิดเป็น default → social_buffer ≈ 0 → safety ค้าง
- **Hunger confound ใน seed placement:** 97.8% ของ seed drops เกิดตอน critical hunger
- **Replication ปลอม:** movement RNG ไม่ผูกกับ args.seed → ยังไม่มี true multi-seed replication
- **Phase 6 ยังทำไม่ได้:** precondition (ประชากรยั่งยืน) ยังไม่ผ่าน

---

## 5. สิ่งที่ต้องทำต่อ (เรียงตามลำดับความสำคัญ)

### งาน Prerequisite (ต้องทำก่อนทุกอย่าง)

1. **แก้ clustering ↔ reproduction ↔ mortality ร่วมกัน** — ต้องออกแบบ ไม่ใช่แค่จูน:
   - เปิด home-fidelity + social clustering จริงเพื่อให้ agent เกาะกลุ่มได้ (แก้ Allee effect)
   - continuous logistic reproduction + de-synchronized mortality (แก้ cohort boom-bust)
   - food scaling กับประชากรเพื่อให้มีช่องเสถียรตรงกลาง
   - ทั้ง 4 ต้องทำพร้อมกัน เพราะ couple กัน

2. **ผูก args.seed เข้า movement RNG** — เพื่อให้ multi-seed เป็น replication จริง เช่น `Random(hash((args.seed, agent_id, age)))`

### งาน Phase ต่อไป

3. **Phase 5.6** — เพิ่ม object handling drive ที่ไม่ผูกกับ hunger:
   - carried_object_attention / carry discomfort / object curiosity
   - gate ใหม่: balanced drops ≥ 50/run, critical hunger fraction ≤ 0.30

4. **Metabolism v2 Phase 6** (เมื่อประชากรยั่งยืน) — selection ข้ามรุ่นบน endozoochory traits (acid_strength vs shell_hardness tradeoff)

---

## 6. บทเรียนสำคัญที่ไม่ได้คาดมาแต่ต้น

**1. "อาหารไม่พอ" ไม่ใช่ปัญหาจริง — ปัญหาคือ access**  
ระบบมีอาหารเหลือเพียบ แต่ agent กิน 1 มื้อ/455 ticks เพราะ foraging behavior ขับโดย hunger instinct ที่ครอบงำทุกอย่าง ไม่ใช่โดยตำแหน่งอาหาร

**2. Body selection กำหนดว่าจะสืบพันธุ์ได้เลยหรือไม่**  
gate ทุกตัวในช่วง metabolism ใช้ body 37 (armor=0, durability=10) ซึ่งสืบพันธุ์ไม่ได้เชิงโครงสร้าง ทำให้ births=0 มาตลอดแบบ over-determined โดยไม่รู้ตัว

**3. "3 seeds" ไม่ใช่ replication — movement RNG ไม่ผูกกับ seed**  
ค้นพบว่า args.seed ไม่กระทบ movement ซึ่งเป็น driver หลักของพฤติกรรม ผลทุก seed identical เป๊ะ = n=1 deterministic มาตลอด

**4. ปัญหาประชากรเป็น bistable — ไม่ใช่แค่จูนไม่ดีพอ**  
ลอง 33+ รัน พบว่าระบบมีเพียง 2 attractors: fade (repro ต่ำ) และ boom-crash (repro สูง) ไม่มีจุดกึ่งกลางเสถียรในพื้นที่พารามิเตอร์ที่เข้าถึงได้ ต้องออกแบบ coupling ของ 4 ระบบพร้อมกัน

**5. Seed placement ถูก hijack โดย hunger ทั้งหมด ไม่ใช่แค่ bias เล็กน้อย**  
97.8% ของ seed drops เกิดตอน critical hunger และเมื่อบล็อก critical hunger activity collapse เหลือ 14-15 drops/run จาก ~100+ แปลว่า seed handling ทั้งระบบเป็น epiphenomenon ของ foraging ไม่ใช่ behavior อิสระ

---

## 7. ภาพรวม: อยู่ตรงไหนบน roadmap ยาว

```
Phase 1 (ecology)         ✅ ยืนยัน
Phase 2 (reward-place)    ✅ ยืนยัน
Phase 3 (seed causality)  ✅ ยืนยัน
Phase 4 (managed patch)   ⚠️ claim แคบลง
Phase 5 (site selection)  ❌ ติดขัด — hunger confound
Population stability      ❌ ติดขัด — bistable R₀ < 1
Phase 6 (evolution)       ⏳ รอ — precondition ยังไม่พร้อม
Phase 7 (social learning) ⏳ ยังไม่เริ่ม
Phase 8 (proto-language)  ⏳ ยังไม่เริ่ม
Phase 9 (robustness)      ⏳ ยังไม่เริ่ม
```

> งานวิจัยชิ้นนี้มีคุณค่าวิทยาศาสตร์แม้ยังไม่บรรลุ Phase 6 การพิสูจน์ proto-farming substrate (Phase 1–3) และการค้นพบ structural barriers (R₀ ceiling, bistable dynamics, body-durability gate, replication failure) เป็น honest negative results ที่มีความหมาย เพราะบอกได้ว่า "ปัญหาอยู่ที่ไหนกันแน่" ซึ่งเป็นความก้าวหน้าจริง ไม่ใช่ความล้มเหลว

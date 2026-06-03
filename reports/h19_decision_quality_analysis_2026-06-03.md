# รายงานวิเคราะห์ H19: Reproduction Decision Quality / Gate-to-Action Integrity

วันที่ทดลอง: 2026-06-03  
รายงานก่อนทดลอง: `reports/pre_experiment_plan_h19_decision_quality_2026-06-03.md`  
สคริปต์ทดลอง: `scripts/run_h19_decision_quality_trace.py`  
ผลดิบ: `data/hypothesis_diagnostics/h19_decision_quality_2026-06-03/`

## Abstract

H19 ถูกออกแบบมาเพื่อตรวจว่า Gen1 females ไม่มีลูกเพราะ policy/decision ไม่ยอม reproduce ทั้งที่พร้อมแล้ว หรือเพราะ Gen1 ไม่เคยพร้อมครบทุก gate จริง.

ผลทดลอง 36 runs ชี้ชัดว่าไม่พบ decision/action handoff bug. ทุก tick ที่ `exact_ready=True` กลายเป็น `wants_reproduction=True` และ spawn child สำเร็จทันที. ไม่มี `ready_no_want_ticks` และไม่มี `want_no_spawn_ticks` ในทุก condition.

ดังนั้นคำอธิบายที่แข็งแรงที่สุดตอนนี้คือ:

> Gen1 ไม่มีลูกเพราะแทบไม่เคย exact full-ready ไม่ใช่เพราะพร้อมแล้วไม่ยอมมีลูก

H19a/H19b ถูกหักล้าง. H19d หรือ Gen1 gate alignment bottleneck ได้รับการสนับสนุนแรง.

## Introduction

จาก H12-H18 เราพบว่า first-wave births และ matured children เพิ่มได้ แต่ second-wave reproduction ยังแทบไม่เกิด.

คำถามสำคัญคือ:

> Gen1 โตแล้วทำไมไม่มีลูก

มีความเป็นไปได้สองโลก:

1. Gen1 female พร้อมครบแล้ว แต่ decision policy หรือ runner action handoff ไม่ทำให้เกิด birth
2. Gen1 female มีบาง gate พร้อมบางเวลา แต่ gate ทั้งหมดไม่เคยพร้อมพร้อมกันใน tick เดียว

H19 trace ใช้ตรวจ chain นี้:

`gate ready -> tick returns wants_reproduction -> runner spawn -> child exists`

## Methods

ใช้ conditions ที่มีนัยจาก H12-H18:

| Condition | เหตุผล |
|---|---|
| baseline | control |
| H11 | lifetime opportunity reference |
| H13 | parent-child overlap มี second-wave signal |
| H16 | survival/maturation helper |
| H17 | lower birth cost เพิ่ม first-wave births |
| H13+H17 | matured สูงแต่ gen1 birth 0 |
| H16+H17 | matured สูงและ gen1 opportunity สูงแต่ gen1 birth 0 |
| H1+H11 | best prior second-wave signal |
| H1+H11+H14+H17 | births/matured สูงสุดแต่ gen1 birth 0 |

Control variables:

- body_index: `14`
- initial_population: `250`
- max_population: `375`
- max_ticks: `800`
- seeds: `7, 8, 11, 13`
- total runs: `36`

เพิ่ม output:

- `condition_summary.csv`
- `runs.csv`
- `female_decisions.csv`
- `decision_trace.csv`
- `runs.json`

จำนวน trace rows: `3,255`

## Results

### 1. Gate-to-action chain ไม่ขาด

ผลรวมระดับ condition:

| Condition | Births | Matured | Gen1 Births | Exact Ready | Spawn Events | Ready No Want | Want No Spawn | Gen1 Ready | Gen1 Spawn |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 6.0 | 2.0 | 0.0 | 6.0 | 6.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| H11 | 6.0 | 5.25 | 0.0 | 6.0 | 6.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| H13 | 6.25 | 6.0 | 0.25 | 6.25 | 6.25 | 0.0 | 0.0 | 0.25 | 0.25 |
| H16 | 6.0 | 6.0 | 0.0 | 6.0 | 6.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| H17 | 9.0 | 2.75 | 0.0 | 9.0 | 9.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| H13+H17 | 9.0 | 8.25 | 0.0 | 9.0 | 9.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| H16+H17 | 9.0 | 8.75 | 0.0 | 9.0 | 9.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| H1+H11 | 6.5 | 5.75 | 0.5 | 6.5 | 6.5 | 0.0 | 0.0 | 0.5 | 0.5 |
| H1+H11+H14+H17 | 12.0 | 9.75 | 0.0 | 12.0 | 12.0 | 0.0 | 0.0 | 0.0 | 0.0 |

ข้อค้นพบ:

- `ready_no_want_ticks = 0` ทุก condition
- `want_no_spawn_ticks = 0` ทุก condition
- `ready_to_spawn_conversion = 1.0` ทุก condition
- ไม่มีเคสแบบ "female full_ready หลาย tick แต่ birth = 0"

แปลว่าเมื่อระบบเห็น female พร้อมจริง birth จะเกิดทันที.

### 2. Gen1 exact-ready เกิดน้อยมาก

Gen1 exact-ready เกิดแค่ใน:

- H13 seed 7: 1 tick, spawn 1 child, first gen1 ready/spawn tick `67`
- H1+H11 seed 7: 2 ticks, spawn 2 children, first gen1 ready/spawn tick `100`

นอกนั้น Gen1 exact-ready เป็น 0.

นี่แปลว่า second-wave ที่เกิดขึ้นจริงไม่ใช่เพราะ policy เปลี่ยน แต่เพราะบาง condition ทำให้ gate ของ Gen1 sync กันได้ในบาง seed.

### 3. Gen1 gate rates บอกว่าปัญหาคือ gate alignment

อัตรา gate-ok ของ Gen1 adult female ticks:

| Condition | Samples | Energy OK | Near Nest | Nest Food OK | Mate OK | Cooldown OK | Top Blocks |
|---|---:|---:|---:|---:|---:|---:|---|
| baseline | 148 | 0.068 | 1.000 | 0.736 | 0.115 | 1.000 | low_energy, no_mate, nest_food_low |
| H13 | 253 | 0.004 | 1.000 | 0.261 | 0.166 | 0.929 | low_energy, no_mate, nest_food_low |
| H16 | 446 | 0.314 | 0.996 | 0.590 | 0.157 | 1.000 | no_mate, low_energy, nest_food_low |
| H17 | 270 | 0.259 | 0.630 | 0.522 | 0.052 | 1.000 | no_mate, low_energy, nest_food_low |
| H13+H17 | 549 | 0.104 | 0.820 | 0.368 | 0.091 | 1.000 | no_mate, low_energy, nest_food_low |
| H16+H17 | 613 | 0.163 | 0.863 | 0.365 | 0.215 | 1.000 | low_energy, no_mate, nest_food_low |
| H1+H11 | 205 | 0.156 | 0.966 | 0.556 | 0.327 | 0.824 | low_energy, no_mate, nest_food_low |
| H1+H11+H14+H17 | 293 | 0.000 | 0.997 | 0.379 | 0.352 | 1.000 | low_energy, no_mate, nest_food_low |

ข้อค้นพบ:

- `near_nest` มักไม่ใช่ปัญหาหลักในหลาย condition
- `cooldown` ส่วนใหญ่ไม่ใช่ปัญหาหลัก
- `energy_ok`, `mate_ok`, และ `nest_food_ok` ไม่ sync กัน
- H1+H11+H14+H17 มี `energy_ok=0.000` สำหรับ Gen1 แม้ births/matured สูงมาก

### 4. H17 เพิ่ม birth แต่ทำให้เห็น first-wave trap ชัดขึ้น

H17 ทำให้ births เพิ่มเป็น `9.0`. H1+H11+H14+H17 ทำให้ births เพิ่มเป็น `12.0`. แต่ Gen1 exact-ready ยังเป็น `0.0`.

แปลว่า first-wave birth ที่เพิ่มขึ้นไม่ได้สร้าง second-wave reproduction. ในบางกรณีอาจทำให้ Gen1 energy economics แย่ลงจนไม่มี exact-ready tick เลย.

### 5. H13 ควรถูกให้น้ำหนักมากขึ้น

H13 เป็นหนึ่งในสอง condition ที่ทำให้ Gen1 exact-ready และ Gen1 spawn เกิดจริง.

ถึงค่าเฉลี่ยจะดูเล็ก (`gen1 births = 0.25`) แต่เชิงกลไกมันสำคัญ เพราะมันแสดงว่าเมื่อ parent-child timing ถูกพอ Gen1 สามารถข้ามจาก adult ไป reproduction ได้จริง.

## Hypothesis Testing

### H19a: full_ready=True แต่ wants_reproduction=False

Evidence against:

- `ready_no_want_ticks = 0` ทุก condition

สรุป: หักล้างในชุดทดลองนี้

Confidence: สูง ภายใน current conditions

### H19b: wants_reproduction=True แต่ runner ไม่ spawn child

Evidence against:

- `want_no_spawn_ticks = 0` ทุก condition
- spawn events เท่ากับ exact-ready ticks ทุก condition

สรุป: หักล้างในชุดทดลองนี้

Confidence: สูง ภายใน current conditions

### H19c: measurement lag ทำให้ full-ready เดิมหลอก

Evidence:

- H19 exact trace ไม่พบ mismatch
- ค่า exact-ready สอดคล้องกับ birth/spawn
- previous full-ready metric อาจยังมี lag เล็กน้อยเพราะอ่าน debug ก่อน tick แต่ไม่ได้ทำให้เกิดข้อสรุปผิดหลักในชุดนี้

สรุป: ไม่ใช่ปัญหาหลักตอนนี้

Confidence: กลาง

### H19d: Gen1 gate alignment bottleneck

Evidence supporting:

- Gen1 opportunity/gate บางส่วนมี แต่ exact-ready เกือบทั้งหมดเป็น 0
- Top blocks ของ Gen1 คือ `low_energy`, `no_mate`, `nest_food_low`
- H16+H17 มี Gen1 adult samples สูงถึง `613` แต่ Gen1 exact-ready = 0
- H1+H11+H14+H17 มี Gen1 adult females มาก แต่ `energy_ok=0.000`

สรุป: สนับสนุนแรง

Confidence: สูง

## Discussion

H19 ช่วยปิดประตูหนึ่งที่สำคัญ: ตอนนี้ยังไม่พบว่า AI decision policy ปฏิเสธ reproduction ทั้งที่พร้อมจริง.

เมื่อ female พร้อมจริง ระบบ spawn ลูกทันที. ดังนั้นปัญหา Gen1 ไม่มีลูกอยู่ก่อนจุด decision action. มันอยู่ที่การทำให้ gate ทั้งหมดพร้อมใน tick เดียวกัน.

ประโยคสรุป:

> Gen1 ไม่ได้ไม่ตัดสินใจมีลูก แต่ Gen1 แทบไม่เคยอยู่ในโลกที่มีเงื่อนไขครบพอให้ตัดสินใจได้

ภาพที่ชัดขึ้น:

1. H13 ทำให้ timing ดีขึ้นจน second-wave เกิดบาง seed
2. H17 เพิ่ม birth รุ่นแรก แต่ไม่สร้าง Gen1 readiness
3. H16 ช่วย survival/maturation แต่ไม่ sync mate/food/energy
4. H1+H11 ยังเป็นฐานดีที่สุด เพราะเป็น condition เดียวที่มี Gen1 birth 2 ครั้งใน seed 7
5. H1+H11+H14+H17 เป็น warning ว่าเพิ่ม first-wave birth/matured มากเกินไปอาจทำให้ Gen1 energy พัง

## Limitations

- รัน 4 seeds ต่อ condition เพื่อเทียบกับ H1-H18 ไม่ใช่ publication-grade sample
- H19 เป็น instrumentation ไม่ใช่ fix
- gate rates เป็น aggregate ไม่ใช่ causal proof ว่า gate ใดต้องแก้ก่อน
- ยังไม่ได้ trace household ownership/inheritance ของ Gen1 แบบละเอียด

## Future Work

### H20: First-Wave Throttling / Birth Spacing

ทดสอบว่าการจำกัด first-wave birth ให้ช้าลงจะทำให้ Gen1 energy/food/mate sync ดีขึ้นหรือไม่.

ตัวแปรต้น:

- minimum household buffer before birth
- one-child-until-gen1-ready rule
- longer spacing after founder birth

ตัวแปรตาม:

- Gen1 exact-ready ticks
- Gen1 births
- Gen1 energy_ok rate
- parent-child overlap

### H21: Gen1 Nest Inheritance / Household Identity

ทดสอบว่า Gen1 โตแล้วอยู่ใน household/nest/mate network ถูกต้องหรือไม่.

ตัวแปรที่ต้อง trace:

- Gen1 owner_id
- inherited nest id
- parent nest still active
- Gen1 near inherited nest
- food in inherited nest
- mate in same household radius

### H22: Gen1 Mate Synchronization

เพราะ `mate_ok` ต่ำมากในหลาย condition ควรตรวจว่า Gen1 females และ males โตไม่พร้อมกัน ตายคนละเวลา หรืออยู่คนละ nest.

ตัวแปรที่ต้องวัด:

- Gen1 adult male/female overlap ticks
- same-nest mate availability
- mate distance distribution

## Final Conclusion

H19 หักล้างแนวคิดว่า "female พร้อมแล้วแต่ AI ไม่ยอมมีลูก" ในชุดทดลองนี้.

ปัญหาที่แท้จริงตอนนี้คือ:

> Gen1 full-ready gate alignment ไม่เกิด

ดังนั้นรอบต่อไปไม่ควรแก้ decision policy ก่อน แต่ควรเจาะ:

1. H13 แบบจริงจังกว่าเดิม: 2-generation household overlap
2. H20: first-wave throttling/birth spacing
3. H21: Gen1 nest inheritance
4. H22: Gen1 mate synchronization


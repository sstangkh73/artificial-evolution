# รายงานสรุปรวม: การสูญพันธุ์ของประชากร — โซ่เส้นสุดท้ายที่ขวางความก้าวหน้า

**Population extinction — the final blocker before evolution (consolidated diagnostic report)**

ผู้จัดทำ: Chisanupong · โครงการ Artificial Evolution (TURC2026)
วันที่: 2026-06-27
ขอบเขต: สังเคราะห์จากรายงานทุกฉบับที่เกี่ยวกับการสูญพันธุ์/ความยั่งยืนของประชากร ตั้งแต่ 2026-06-02 ถึง 2026-06-20
สถานะ: **root-cause ครบ · ยังไม่ได้ประชากรเสถียร** (honest negative result เชิงโครงสร้าง)
หมายเหตุการยืนยัน: claim ระดับโค้ดในรายงานนี้ถูกตรวจกับซอร์สจริงในรอบนี้ (ดู §8) ไม่ได้อ้างจากความจำ

---

## บทคัดย่อ (อ่าน 30 วินาที)

เป้าหมายปลายทางคือ **วิวัฒนาการจริง (Phase 6)** ซึ่งมี precondition ข้อเดียวที่ยังไม่ผ่าน: **ประชากร mortal ต้องไม่สูญพันธุ์**. หลังการสอบสวน ~33+ รัน และเพิ่มกลไกโครงสร้าง 6 อย่าง ผลคือ **ทุกชุดสูญพันธุ์เสมอ** — แต่กระบวนการสอบสวนได้ "ย้ายเส้นเขตของปัญหา" ไปไกลมาก:

1. **สิ่งที่แก้/พิสูจน์แล้ว:** พลังงาน (ทำให้เกินดุลได้), durability gate (ต้องใช้ body มีเกราะ), การเกิด birth ครั้งแรกของโปรเจกต์ (50→100), perf (เร็วขึ้น 76×), และที่สำคัญสุด — **fecundity อยู่ที่ระดับทดแทนพอดี (~2.0 ลูก/female) แล้ว**
2. **ตอนนี้ติดที่:** ไม่ใช่ "เกิดน้อย" แต่เป็น **พลวัตประชากรไม่เสถียร** — ระบบเป็น *bistable* มีแค่ 2 จุดดึงดูด (จางช้า ๆ เมื่อสืบพันธุ์ต่ำ / boom→crash เมื่อสืบพันธุ์สูง) **ไม่มีจุดกึ่งกลางเสถียร** ทำให้ R₀ ที่วัดได้ติดเพดานใต้ 1 (0.72–0.88) ทุกการจูน
3. **คาดว่าเพราะ:** **delayed density-dependence** (เบรกประชากรเด้งช้าหลังเกิน K + อายุมาตุรภาพ ~61 ticks หน่วง) → oscillation แบบ delayed-logistic ที่ decay ลงสู่ 0 ไม่ converge สู่ K + couple กับ Allee effect (เบาบาง→หาคู่ไม่เจอ) ต้อง **ออกแบบระบบ clustering↔reproduction↔mortality↔food ร่วมกัน ไม่ใช่จูนพารามิเตอร์ทีละตัว**

> ใจความเดียว: **"ปัญหาเลื่อนจาก fertility ceiling ไปเป็น dynamical-stability ceiling"** — เรารู้แล้วว่าเกิดพอ แต่ประชากรแกว่งจนล้มทุกครั้ง

---

## 1. ทำไมมันคือ "โซ่เส้นสุดท้าย"

roadmap ยาวของโปรเจกต์:

```
Phase 1 (ecology)          ✅ ยืนยัน 5/5
Phase 2 (reward-place)     ✅ ยืนยัน (return lift 41.7×)
Phase 3 (seed causality)   ✅ ยืนยัน (1.40×)
Phase 4 (managed patch)    ⚠️ claim แคบลงหลัง falsification
Phase 5 (site selection)   ❌ ติด hunger confound
── ประชากรยั่งยืน          ❌ ◄◄◄ โซ่เส้นสุดท้ายที่ค้างอยู่ตรงนี้
Phase 6 (evolution)        ⏳ รอ — ทำไม่ได้จนกว่าประชากรจะไม่สูญพันธุ์
Phase 7–9                  ⏳ ยังไม่เริ่ม
```

**เหตุผลเชิงตรรกะ:** วิวัฒนาการ = mortal population + heritable variation + selection over generations. ถ้าประชากรสูญพันธุ์ภายในไม่กี่รุ่น **selection ข้ามรุ่นเกิดไม่ได้** — ไม่มีรุ่นให้คัด. ฉะนั้นแม้กลไก heritability/mutation จะสร้างเสร็จแล้ว (Metabolism v2 Fix 3) ก็ยัง "เดินเครื่องไม่ติด" เพราะไม่มีประชากรต่อเนื่องให้มันทำงาน. **การสูญพันธุ์จึงเป็น gate เดียวที่กั้นระหว่าง "ระบบจำลองชีวิต" กับ "ระบบวิวัฒนาการจริง"**

---

## 2. ไทม์ไลน์การสอบสวน — "แก้อะไรไปแล้ว" ตามลำดับเวลา

| ช่วง | สิ่งที่ทำ / ค้นพบ | ผล | สถานะ |
|---|---|---|---|
| **2026-06-02** | วินิจฉัยแรก: นี่ไม่ใช่ scarcity problem แต่เป็น **conversion problem** (มีอาหาร/เสบียง/รุ่นลึก แต่แปลงเป็น replacement rate ไม่พอ) | long-loop body_14 pop250: **0/10 non-extinct** แม้ไปถึง gen 24–25 และ stored food สูงถึง 42,373 | กรอบปัญหาตั้งต้น |
| 2026-06-02 | **breeder-priority household allocation** (ให้ female พร้อมสืบพันธุ์ดึงอาหารจากรังก่อน) | ดีสุดในรอบนั้น: max gen 5.8→**7.5**, matured children 106→**145**, non-extinct 5/10→**8/10** (ทดสอบสั้น) | คงไว้ (best mechanism ในยุคนั้น) |
| 2026-06-03 | สอบสวนสมมติฐานเชิงระบบ **H1–H23** (hypothesis falsification: diagnostics + reproduction-chain + decision-quality + family-chain) | ยืนยัน H4 (mate fragmentation), H5 (cohort boom-bust + hard cooldown แรงเกิน), H11 (repro opportunity/female < 2) | แคบสาเหตุลง |
| 2026-06-08→12 | งานฝั่ง ecology/learning (immortal discovery, no-oracle breakthrough, ecology calibration) | ยืนยัน Phase 1–3 — แต่ยังเป็น **immortal** (เลี่ยงปัญหาตายไว้ก่อน) | แยกสาย ไม่แตะ mortality |
| **2026-06-18→19** | **Energy-Economy Diagnosis** — วัดงบพลังงานตรง ๆ (telemetry แทนการอนุมาน) | **หักล้างความเชื่อเดิม 3 ข้อ** (ดู §3) + **ปลดล็อก birth ครั้งแรกของโปรเจกต์: 50→100** | จุดพลิกที่ 1 |
| 2026-06-20 | เพิ่มกลไกโครงสร้าง 6 อย่าง: home-fidelity (เกาะกลุ่ม), continuous density-dependent repro, stochastic age-rising mortality, **realistic starvation death** (อาหารคุม K), dense food, tunable repro knobs | กลไกทำงานครบ (peak↑, ไปถึง gen 6–8) **แต่ยังสูญพันธุ์** | สร้างเครื่องมือครบ |
| 2026-06-20 | **perf fix:** `food_signal_at` O(n)→spatial grid | **เร็วขึ้น 76×** (7.38s→0.10s), v1 byte-identical | ✅ สำเร็จจริง |
| 2026-06-20 | **R₀ structural analysis** — กวาด drain/density/rate ครบ ~33 รัน | R₀ ติดเพดาน **0.72–0.88 < 1 ทุกชุด** → bistable, ไม่มี stable middle | จุดพลิกที่ 2 |
| **2026-06-20** | **Per-female fecundity telemetry** — วัดผลผลิตต่อ female ตลอดชีวิต | **fecundity ≈ 2.0 (gen0–3) = ทดแทนพอดี!** ปัญหาไม่ใช่ fertility แต่เป็น **dynamics** | จุดพลิกที่ 3 (พลิกแนวทาง) |
| 2026-06-21→27 | โปรเจกต์เบนไป neuroevolution + communication pilot | งานคู่ขนาน — **ยังไม่ได้กลับมาแก้ extinction ด้วยแนวทางใหม่ (density-brake)** | ค้างไว้ตรงนี้ |

**กลุ่มการแทรกแซงที่ลองแล้ว "ถูกถอนกลับ" (rolled back)** — บันทึกไว้กันทำซ้ำ (จาก `STABILITY_INVESTIGATION_LOG.md`):

| การแทรกแซง | ผลที่ทำให้ถอน |
|---|---|
| direct projected-energy storage fix | แย่ลง (bug จริงแต่เคยบดบัง imbalance ที่ลึกกว่า) |
| aggressive settlement / nest-spacing suppression | collapse หนัก max gen เหลือ 1.0 |
| hard reproduction cooldown (anti-cohort) | births ล่มแรงเกิน extinction 10/10, gen เหลือ 2.5 |
| active-nest-only support filtering (LOOP-008) | ยัง 0/10, long seeds แย่ลง |
| household-linked active nest probe (LOOP-009) | seeds ล่มที่ gen2 (tick ~160–190) |
| naive nest inheritance transfer (LOOP-010) | seeds ล่มที่ gen2 อีก |
| juvenile/young-adult pipeline priority (LOOP-011) | ดีกว่า probe ที่ล้ม แต่ไม่ชนะ breeder-priority baseline |
| founder population เพิ่มอย่างเดียว (สูงสุด ~250) | ช่วยให้ลึกขึ้นแต่ยังตายหมด |

> บทเรียนจากกลุ่มนี้: **การกดทีละจุด (suppress) หรือเติม scaffold ทีละชั้น ไม่เคยแก้ได้** เพราะตัวที่ถูกกดมักเป็น scaffold ที่ระบบยังพึ่งอยู่ → ชน wall ตัวถัดไปเสมอ

---

## 3. ความเชื่อเดิมที่ถูกหักล้าง (หัวใจของ "คาดว่าเพราะอะไร")

นี่คือคุณค่าหลักของการสอบสวน — ความเชื่อโดยปริยายที่ขับงานมานานถูกพิสูจน์ว่า **ผิด** ด้วยการวัดตรง:

| ความเชื่อเดิม (เชื่อโดยปริยาย) | ความจริงที่พบ | หลักฐาน |
|---|---|---|
| "agent **อดตาย** (energy_depleted) เป็นสาเหตุหลักของการล่ม" | **ผิด** — ในโหมด mortal ปกติ `energy ≤ 0` ถูก reset เป็น 1 (ไม่ตาย); การตายจริงคือ **อายุขัย** — founder 50 ตัวเกิดอายุเท่ากัน (67) ตายพร้อมกันที่ tick 133 (MAX_AGE 200) | `agent.py:2586-2590` (reset), `agent.py:256/261` (lifespan_completed) |
| "อาหารในโลก**น้อยเกินไป**" | **ผิด** — เติมอาหาร 0→30/tick (คงค้าง 36→2,654, กิน 14,103 เม็ด) **ขาดดุลแทบไม่ขยับ**; คอขวดคือ **access** (กิน 1 มื้อ/455 ticks) ไม่ใช่ปริมาณ | budget table 06-19 (drain 4.99 vs intake 0.011 = **453:1**) |
| "**พลังงาน**คือ gate เดียวที่บล็อกการสืบพันธุ์" | **ผิด** — มี **3 gates พร้อมกัน:** ① energy ≥ 92, ② durability ≥ 18, ③ social streaks; body 37 พลังงานล้น 1,256 ก็ births = 0 | capstone 06-19 |
| "body 37 (social_planner) ที่ใช้ใน gate ทุก experiment สืบพันธุ์ได้" | **ผิด** — armor=0 → durability=10 < 18 → **สืบพันธุ์ไม่ได้เชิงโครงสร้างตลอดกาล**; births=0 ถูก over-determined โดยไม่รู้ตัว | `body.py:260` (`10+armor*8`), `agent.py:30` (MIN=18) |
| "แค่หาค่าพารามิเตอร์ที่ถูก ก็แก้ R₀ < 1 ได้" | **ผิด** — 33+ รัน, 6 กลไก, R₀ ติดเพดาน 0.72–0.88 เสมอ; ระบบ **bistable** ไม่มีจุดกึ่งกลางเสถียร | R₀ table 06-20 |
| "fecundity (เกิดน้อย) คือคอขวด" | **ผิด (พลิกล่าสุด)** — female ที่อยู่ครบชีวิตมีลูก **~2.0 = ทดแทนพอดี**; ปัญหาคือ **dynamics** (count รุ่น oscillate 25→33→26→5→10 แล้ว decay) | fecundity telemetry 06-20 |
| "3 seeds ที่รัน = replication (n=3)" | **ผิด** — movement RNG ใช้ `Random(agent_id+age)` ไม่ผูก `args.seed` → ทุก seed identical = **n=1 deterministic** | ยืนยันในโค้ด/เอกสาร (ดู §8) |

> **รูปแบบที่ซ้ำ:** เกือบทุกความเชื่อเดิมที่ "ฟังดูสมเหตุผล" (อดตาย/อาหารน้อย/พลังงานพอก็เกิด) **ถูกหักล้างด้วยการวัดตรง**. นี่คือเหตุผลที่ skill บังคับว่า *"ทำงานจากหลักฐานในรีโป ไม่ใช่จากความจำ"*

---

## 4. ตอนนี้ติดตรงไหน (สถานะปัจจุบัน ตรวจกับโค้ดแล้ว)

### 4.1 ภาพพลวัต — ระบบ bistable ไม่มีช่องเสถียร

```
        สืบพันธุ์ต่ำ ──► R₀ < 1 ──► จางช้า ๆ (ถึง gen 6–8 แล้วหาย)   ◄─ Allee
   [ ไม่มีจุดกึ่งกลางเสถียร ]
        สืบพันธุ์สูง ──► boom ชนทรัพยากร/เพดาน ──► cohort crash (gen 1–3) ◄─ boom-bust
```

ระบบถูกบีบจาก 2 ด้านพร้อมกัน:
- **Allee (เบาบาง):** forage ทำให้ agent กระจาย → ไม่เกาะกลุ่ม → `social_buffer ≈ 0` → `safety` ค้างที่ 0.53 (ต่ำกว่าเกณฑ์ 0.66) + หาคู่ไม่เจอ → สืบพันธุ์ ~75–85% ทดแทน → จาง
- **boom-bust (หนาแน่น):** ประตูสืบพันธุ์เปิดพร้อมกัน → cohort รุ่นเดียว → แก่ตายพร้อมกันที่ MAX_AGE → crash

### 4.2 หลักฐานเชิงตัวเลข (สถานะที่ยืนยันแล้ว)

| ตัวชี้วัด | ค่า | ความหมาย |
|---|---|---|
| R₀ ที่วัดได้ (33 รัน, 6 กลไก) | 0.72–0.88 | ต่ำกว่าทดแทนเสมอ |
| fecundity/female ที่อยู่ครบชีวิต (gen0–3) | ≈ 2.0 | **อยู่ที่ระดับทดแทนแล้ว** |
| fecundity เฉลี่ยรวม | 1.838 | ตกเพราะ gen4 = 0.0 (Allee หางการล่ม) |
| reproduction funnel "ready" rate | **8%/tick** | ผ่านทุกประตูพร้อมกันได้น้อย |
| → low_safety บล็อก | 83% | ด่านสังคมหลัก |
| → short_pair_bond บล็อก | 76% | |
| → low_comfort บล็อก | 72% | |
| → energy/durability บล็อก | 8% | **แก้แล้ว — ไม่ใช่คอขวดอีก** |
| count ต่อรุ่น (สูตรดีสุด) | 25→33→26→**5**→10 | oscillation ที่ decay → สูญพันธุ์ |

### 4.3 สิ่งที่ยืนยันแล้วว่า "แก้/พิสูจน์ผ่าน" (ไม่ใช่คอขวดอีกต่อไป)

- ✅ **เศรษฐกิจพลังงาน:** ทำให้เกินดุลได้ (mean E ถึง 3,185, hunger→0)
- ✅ **durability gate:** เข้าใจแล้วว่าต้องใช้ body มีเกราะ (armor ≥ 1, durability ≥ 18) — `body.py:260`
- ✅ **birth ครั้งแรก:** body 38 → 50→100 (พิสูจน์ว่า pipeline การเกิดเดินได้)
- ✅ **fecundity:** อยู่ที่ระดับทดแทน — ไม่ต้องเพิ่มอัตราการเกิดอีก
- ✅ **perf:** 76× (ปลดล็อกการทดลอง density สูง)
- ✅ **กลไกโครงสร้าง 6 อย่าง:** สร้างและทำงานครบ (clustering, continuous birth, spread death, starvation-K)

### 4.4 สิ่งที่ยังติด (คอขวดปัจจุบัน)

- ❌ **R₀ ceiling < 1 เชิงโครงสร้าง** — bistable, ไม่มี stable fixed point ในพื้นที่พารามิเตอร์ที่เอื้อมถึง
- ❌ **dynamical instability** — delayed density-dependence → oscillation decay (สาเหตุที่พลิกล่าสุด)
- ❌ **social gates ครอบงำ** — ready 8% เพราะ agent ไม่เกาะกลุ่ม (safety ค้าง)
- ❌ **replication ปลอม** — n=1 deterministic (movement RNG ไม่ผูก seed) → ยังไม่มีสถิติจริง
- ❌ **Phase 6 ทำไม่ได้** — precondition ยังไม่ผ่าน

---

## 5. คาดว่าเพราะอะไร (สมมติฐานราก + ระดับความเชื่อมั่น)

ตาม hypothesis-testing skill — ระบุหลักฐานหนุน/ค้าน/ทางเลือก/ความเชื่อมั่น:

### H-ราก-1 (ล่าสุด, ความเชื่อมั่น **สูง**): ปัญหาคือ *dynamical instability* ไม่ใช่ fecundity
- **หนุน:** fecundity/female = 2.0 (ทดแทนพอดี) แต่ count รุ่น oscillate (25→33→26→5→10) แล้ว decay; gen4 = 0
- **กลไกคาด:** **delayed density-dependence** — ลูกที่เกิดไปแย่งทรัพยากร *ทีหลัง* + อดตาย *ช้า* (starvation_tolerance 15 ticks) + maturation lag ~61 ticks → ระบบเป็น delayed-logistic ที่ overshoot K แล้ว crash ใต้ K → เข้าโซน Allee → 0
- **ค้าน/ทางเลือก:** funnel ของ continuous mode ไม่น่าเชื่อถือ (reproduction_debug stale) — จึงใช้ fecundity เป็นหลักฐานหลักแทน
- **นัย:** ต้องใส่ **density-dependent reproduction brake แบบ proportional** (อิง food-per-capita) ที่เบรก *ก่อน* overshoot — ไม่ใช่เบรกแบบ all-or-nothing หลังเกิน K แล้ว

### H-ราก-2 (ความเชื่อมั่น **สูง**): การคัปปลิงของ 4 ระบบ ไม่ใช่ค่าพารามิเตอร์ตัวเดียว
```
การเคลื่อนที่ (forage→กระจาย) ⟂ การจับคู่ (ต้องอยู่ใกล้)
        ↓                              ↓
ไม่เกาะกลุ่ม → safety ต่ำ + หาคู่ไม่เจอ → สืบพันธุ์ต่ำ (Allee)
        ↑                              ↓
เกาะกลุ่ม+ประตูเปิดพร้อมกัน → cohort sync → แก่ตายพร้อมกัน (boom-bust)
```
- **หนุน:** ทุก config สูญพันธุ์ (tuning ไม่พอ); continuous mode ยังติด mate-finding ในประชากรเบาบาง
- **นัย:** ต้องออกแบบ **clustering ↔ reproduction ↔ mortality ↔ food** พร้อมกัน เพราะ couple กัน — แก้ทีละตัวจึงชน wall ตัวถัดไปเสมอ (ตรงกับประวัติ rollback ทั้งหมดใน §2)

### H-ราก-3 (ความเชื่อมั่น **สูง**): social/clustering คือชั้นที่ลึกสุด
- **หนุน:** ชั้น settlement/social (`scaffolded_*`) ปิดเป็น default → ไม่เคยถูกเปิด → `social_buffer ≈ 0` → safety 0.53 < 0.66 → low_safety บล็อก 83%
- **ค้าน:** เปิด scaffolded แล้ว births↑ และสร้างรัง 32 ได้ แต่ก็ยังสูญพันธุ์ (gen 4) → clustering จำเป็นแต่ไม่พอเดี่ยว ๆ ต้องคู่กับ density-brake

### สมมติฐานที่ "ตกไปแล้ว" (เคยเชื่อ แต่หักล้าง)
energy-as-sole-gate, food-scarcity, starvation-death-dominant, fecundity-too-low, parameter-tuning-suffices — ดู §3

---

## 6. การยืนยันระดับโค้ดในรอบนี้ (ตรวจจริง ไม่อ้างความจำ)

| claim ในรายงานเก่า | ผลตรวจกับซอร์ส | ตำแหน่ง |
|---|---|---|
| durability = 10 + armor×8 | ✅ ตรง | `agents/body.py:259-260` |
| reproduction ต้อง durability ≥ 18 (hard gate) | ✅ ตรง (`if ... durability < MINIMUM_REPRODUCTION_HEALTH: return`) | `agents/agent.py:30, 289, 365` |
| MAX_AGE=200, REPRODUCTION_THRESHOLD=150, HUNGER_PRIORITY_ENERGY=58 | ✅ ตรงทั้งหมด | `agents/agent.py:25, 27, 49` |
| immortal clamp energy≥1 (บดบังเศรษฐกิจจริง) | ✅ ตรง | `agents/agent.py:2564-2569` |
| โหมด mortal ปกติ: energy≤0 → reset เป็น 1 (อดไม่ฆ่า) | ✅ ตรง | `agents/agent.py:2586-2590` |
| starvation death เป็น opt-in (เปิด 06-20) ฆ่าเมื่ออด > 15 ticks | ✅ ตรง | `agents/agent.py:2571-2583` |
| ไม่มี death_reason `energy_depleted` ในโค้ดปัจจุบัน | ✅ ยืนยัน (มีแค่ lifespan/starvation/durability_depleted/child_isolation) | `agents/agent.py` |
| movement RNG ไม่ผูก args.seed → n=1 | ✅ ยืนยัน (เอกสารในโค้ดระบุเอง); neuroevolution path แก้แล้ว (`Random(args.seed)`) | `scripts/build_advisor_materials_pdf.py:436`, `scripts/run_neuroevolution.py:180` |

**ข้อสังเกตสำคัญจากการตรวจ:** รายงาน 06-02 พูดถึง `energy_depleted` deaths จำนวนมากใน long-loop แต่โค้ดปัจจุบัน**ไม่มี** death_reason นี้แล้ว และโหมด mortal ปกติ reset energy เป็น 1 (อดไม่ฆ่า) — สอดคล้องกับข้อเท็จจริงว่า ณ 06-02 โฟลเดอร์ยัง**ไม่ใช่ git repo** (โค้ดยุคนั้นต่างจากปัจจุบัน) ⇒ ยืนยันว่า "ความเข้าใจเรื่องสาเหตุการตายเปลี่ยนจริงตามเวลา" ไม่ใช่แค่เปลี่ยนคำอธิบาย

**ข้อควรระวังต่อจากนี้:** `agents/agent.py` ถูกแก้ในงาน neuroevolution (06-27) ให้ **"neural network fully owns movement"** (`agent.py:204`) — การสอบสวน extinction ทั้งหมดอยู่บน **rule-based controller**. ถ้าจะกลับมาทำ extinction ต้องระบุชัดว่ารันบน path ไหน เพราะ movement driver เปลี่ยน = พลวัตอาจเปลี่ยน

---

## 7. ทางแก้ที่เสนอ + ลำดับงานต่อไป

> หลักการ: **ออกแบบ ไม่ใช่จูน** — ทำ 4 อย่างพร้อมกันเพราะ couple กัน

### งาน Prerequisite (ก่อนทุกอย่าง)
1. **density-dependent reproduction brake แบบ proportional** (จาก fecundity report — แนวทางที่ยังไม่ได้ลอง): เบรกอัตราสืบพันธุ์ตาม food-per-capita ที่ลดลง *ก่อน* overshoot → damp oscillation → ทดสอบว่า converge สู่ K
2. **ลด lag** ที่สร้าง oscillation: maturation 61 ticks + อดตายช้า — ลดความหน่วงช่วย converge
3. **เปิด clustering/home-fidelity จริง** เพื่อแก้ Allee + safety (social_buffer)
4. **food scale กับประชากร** ยก carrying capacity ให้มีช่องเสถียรตรงกลาง
5. **ผูก `args.seed` เข้า movement RNG** (เช่น `Random(hash((args.seed, agent_id, age)))`) → ได้ multi-seed replication จริง = มีสถิติ (ตรงกับ Phase 1 ของ ISEF roadmap)

### เมื่อประชากรเสถียรแล้ว
6. **Phase 6 (evolution):** เปิด heritability (Fix 3) + variation (seeded RNG) → selection ข้ามรุ่นบน endozoochory traits

### หมายเหตุเชิงกลยุทธ์ (จาก ISEF roadmap 06-27)
โปรเจกต์ได้เบนไป neuroevolution + communication เป็นแกนสำหรับ YSC/ISEF แล้ว — **การแก้ extinction อาจไม่ใช่ critical path ของการแข่ง** (neuroevolution ให้ selection ข้ามรุ่นบน fitness โดยตรง ไม่ต้องรอประชากร self-sustain). แต่ extinction **ยังเป็นเงื่อนไขของ "วิวัฒนาการ emergent ในโลกเปิด"** ซึ่งเป็น original contribution ที่แข็งที่สุด ⇒ **2 ทางเลือก:**
- **(ก) ปิด extinction ให้จบ** เพื่อ claim open-ended evolution (เสี่ยงสูง, ต้อง redesign 4 ระบบ)
- **(ข) วาง extinction เป็น honest negative result เชิงโครงสร้าง** (R₀ ceiling, bistable, fecundity-at-replacement, body-durability gate) แล้วเดินหน้า neuroevolution เป็นผลหลัก — *negative result นี้มีคุณค่าวิทยาศาสตร์จริง เพราะระบุได้ว่า "ปัญหาอยู่ที่ dynamical stability ไม่ใช่ fertility"*

---

## 8. กรอบหลักฐานและความเชื่อมั่น (ตาม hypothesis-testing skill)

| มิติ | สรุป |
|---|---|
| **Supporting** | fecundity 2.0/female = replacement; R₀ 0.72–0.88 ทุกชุด (33 รัน); funnel ready 8%; durability gate ยืนยันในโค้ด; birth ครั้งแรกเกิดจริง; perf 76× byte-identical |
| **Against / Alternative** | continuous-mode funnel ไม่น่าเชื่อ (ใช้ fecundity แทน); regime ใช้คันโยกเทียม (food×50/drain÷20) ยังไม่ ecological-valid; การทดสอบส่วนใหญ่ในกรอบ immortal/body จำกัด (14/38) |
| **Missing evidence** | regime ยั่งยืนแบบ mortal จริง; density-brake แบบ proportional (ยังไม่ลอง); multi-seed replication; สาเหตุเชิงลึกของ "กิน 1 มื้อ/455 ticks"; พลวัตบน neural-movement path |
| **Confidence** | "fecundity ไม่ใช่คอขวด" = **สูง** · "ปัญหาเป็น dynamical instability (bistable, delayed density-dependence)" = **สูง** · "ต้อง redesign 4 ระบบร่วม" = **สูง** · "density-brake จะแก้ได้" = **ปานกลาง** (ยังไม่ทดลอง) |

---

## 9. ภาคผนวก — รายงานต้นทางที่สังเคราะห์ + อ้างอิงโค้ด

**รายงานหลักที่อ่าน (เรียงตามเวลา):**
- `reports/current_problem_summary_2026-06-02.md` — กรอบ conversion problem, breeder-priority, long-loop 0/10
- `reports/scientific_hypotheses_2026-06-02.md` + ชุด `h1_h11` / `h12_h18` / `h19` / `h20_h22` / `h20_soft_sweep_h23` (2026-06-03) — hypothesis falsification H1–H23
- `docs/STABILITY_INVESTIGATION_LOG.md` — บันทึกการแทรกแซง + rollback (LOOP-008 ถึง 011, SUS-001/002/003)
- `reports/energy_economy_diagnosis_2026-06-19.th.md` — หักล้าง 3 ความเชื่อ + birth ครั้งแรก
- `reports/realistic_economy_carrying_capacity_2026-06-20.th.md` — perf 76× + R₀ ceiling
- `reports/population_sustainability_investigation_2026-06-20.th.md` — root-cause funnel + 4-system coupling
- `reports/r0_fecundity_analysis_2026-06-20.th.md` — **พลิกแนวทาง: fecundity = replacement, ปัญหาคือ dynamics**
- `reports/project_status_full_2026-06-20.md` — สรุปภาพรวมทั้งโปรเจกต์
- `reports/ysc_to_isef_roadmap_2026-06-27.th.md` — กรอบกลยุทธ์/ขอบเขตงานแข่ง

**อ้างอิงโค้ด (ยืนยันรอบนี้):**
`agents/body.py:259-260` (durability) · `agents/agent.py:25,27,30,49` (constants) · `agents/agent.py:289,365` (repro durability gate) · `agents/agent.py:2563-2599` (`_resolve_life_state`: immortal clamp / starvation / reset) · `agents/agent.py:204` (neural owns movement) · `scripts/run_neuroevolution.py:180` (seeded RNG)

**commits สำคัญ:** `cef1af4` (energy telemetry) · `6d473d9` (starvation death) · `e5d0253` (home-fidelity) · `87597de` (continuous repro) · `90c3179` (stochastic mortality) · `ea4967c` (food grid 76×) · `2f3308e` (fecundity telemetry) · `ef6245b` (R₀ fecundity analysis)

---

*รายงานนี้เป็นการสังเคราะห์เชิงวินิจฉัย ไม่ได้รันการทดลองใหม่ — ตัวเลขทั้งหมดมาจากรายงานต้นทาง และ claim ระดับโค้ดถูกตรวจกับซอร์สจริงในรอบนี้*

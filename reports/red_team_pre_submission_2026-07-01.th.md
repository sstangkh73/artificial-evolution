# Red-Team ก่อนส่ง — NSRU + ALIFE 2026 (จุดบอดของทั้งโปรเจกต์)

**จัดทำ:** 2026-07-01 · โจมตีงานตัวเองแบบ reviewer ที่โหดที่สุด ก่อนคนอื่นทำ
**สำหรับ:** NSRU (การแข่งไทย) + ALIFE 2026 Late-Breaking (โปสเตอร์, due 2026-07-20)
**ฐาน:** `reports/proposal/alife2026_late_breaking_abstract_v2.en.md` + สถานะ repo จริง

> อ่านด้วยใจนักวิจารณ์ ไม่ใช่เจ้าของงาน จุดแข็งอยู่ท้าย — แต่ต้องรู้จุดบอดก่อน

---

## 0. สรุปทั้งโปรเจกต์ใน 5 บรรทัด (สิ่งที่ "มีจริง")
1. แพลตฟอร์ม ALife 2D: agent + metabolism v2 (กินตามองค์ประกอบ) + สืบพันธุ์ + neuroevolution + food-value learning
2. **ปัญหาค้างใหญ่:** ประชากรสูญพันธุ์จากคอขวด foraging เชิงพื้นที่ → ผลสำคัญ**ทุกอัน**วัดในโหมด "อิ่มเทียม" (controlled) ไม่ใช่ประชากรวิวัฒน์จริง
3. **Aging Physics v1** (session นี้): damage→senescence, validate 4 arm — **แต่เป็น self-consistent (exponent เป็น knob)** · **ถูกตัดออกจาก abstract ALife แล้ว**
4. **Toxin + age-dependent toxicity** (ตัวชูของ ALife): per-kind learner **แพ้** hidden-state toxicity + เจอ "lure effect" (detox ทำอาหารพิษน่ากินขึ้น) → ผลหลักเป็น **negative + counterintuitive**
5. **store-to-detoxify / deferral:** ยัง **ไม่ implement** (ต้อง larder ระดับชิ้น) = เป็น design + predicted เท่านั้น

---

## 1. จุดบอด "ร้ายแรง" (ต้องแก้ก่อนส่ง)

### 🔴 A. n=1 / deterministic — ยังไม่มี multi-seed + CI (แต่บอกว่า "planned")
abstract ยอมรับเองว่า Result 1 เป็น n=1 และ "confirmatory runs planned" — **reviewer จะสับทันที** ส่งงานที่ยัง "planned" ไม่ได้
**แก้:** harness มีอยู่แล้ว วน seed 20–50 ตัว รายงาน mean±CI ของ (blend, %toxic, P(eat)) **ทำได้ในวันเดียว** อย่าส่งโดยไม่มี

### 🔴 B. "นี่มันก็แค่ POMDP / partial observability 101"
reviewer ALife สาย CS จะพูดประโยคนี้แน่ — per-type average แพ้ state-dependent reward เป็นเรื่อง**ที่รู้กันอยู่แล้ว**
**แก้:** (1) นำด้วย **"lure effect" ให้หนักกว่านี้** (detox ทำให้พิษ *น่ากินขึ้น* → แย่กว่าพิษคงที่) — อันนี้ต่างหากที่ *ไม่ obvious* และเป็นของเรา (2) เพิ่ม 1 ประโยค "เรารู้ว่านี่คือ perceptual aliasing ที่รู้จักดี — ของใหม่คือ X" ให้ชัด

### 🔴 C. Related work แทบเป็นศูนย์ (3 refs, 2 generic + 1 placeholder)
ALife คาดหวังการวางตำแหน่งเทียบงานเดิม (evolved foraging/diet, taste aversion, non-stationary bandit/POMDP) — ตอนนี้**ไม่มีเลย** = จุดโดนตีที่ง่ายที่สุด
**แก้:** อ่านจริง 4–6 ชิ้น (มี `siggraph94.pdf` = Sims evolved creatures อยู่แล้ว) ใส่ให้ครบ ห้ามใส่ ref ที่ไม่ได้อ่าน

### 🔴 D. Venue mismatch — **อย่าส่งตัวเดียวกันไป 2 ที่** (ซ้ำรอย TURC)
- **ALife** (CS-expert, EN, ให้ค่า honesty+novelty): negative result + limitations ตรงจริต **เหมาะ**
- **NSRU** (แข่งไทย, กรรมการทั่วไป, ต้องการ impact + ความสมบูรณ์): "มันล้มเหลว + ยังไม่ได้สร้าง" จะอ่านว่า **"งานไม่เสร็จ"** → เสี่ยงแพ้แบบเดียวกับ TURC (memory: "TURC loss = generalist impact-legibility filter")
**แก้:** ทำ **2 เวอร์ชันคนละเฟรม** — NSRU: นำด้วยแพลตฟอร์มที่ทำงานได้ + "agent เรียนเลี่ยงพิษเองได้" + เรื่อง lure ที่ *เซอร์ไพรส์+อธิบายได้* + โยง real-world (ความปลอดภัยอาหาร/AI ในสภาพแวดล้อมที่เปลี่ยน); ลดคำว่า "fail/ยังไม่สร้าง"

---

## 2. จุดบอด "กลาง" (ควรแก้ถ้ามีเวลา)

### 🟠 E. "lure effect" อาจถูกหาว่า cherry-pick พารามิเตอร์
blend 7.9 > staple 5 เกิดเพราะเลือก acute=50, detox fraction, window 3–7 — reviewer จะถามว่า "จริงทุกค่าหรือแค่จุดที่จูนมา?"
**แก้:** sweep เล็ก ๆ (penalty × สัดส่วน-ปลอดภัย) แล้วโชว์ว่า lure เกิดในช่วงกว้าง = ปรากฏการณ์ทั่วไป ไม่ใช่จุดเดียว

### 🟠 F. ทุกผลอยู่ในโหมด "อิ่มเทียม" — เลี่ยง ecology ที่แพลตฟอร์มมีไว้
reviewer: "สร้าง ALife platform ใหญ่ทำไม ถ้าผลหลักรันในสคริปต์ 50 บรรทัดก็ได้?"
**แก้:** (ทางเลือก) โชว์ ≥1 ผลในซิมเต็ม หรือ **argue ให้แข็ง** ว่าการแยก learning ออกจาก foraging confound เป็น *การออกแบบที่ถูกต้อง* (ไม่ใช่แค่ "เลี่ยงปัญหา")

### 🟠 G. Reproducibility รั่ว — CLI experiment ไม่อยู่ใน commit
`food_value_study_driver.py` + `run_long_emergence_watch.py` **ยัง uncommitted** (ปนกับ demographic WIP) → clone repo แล้วรัน `--toxic-food --toxin-detox-ticks` **ไม่ได้** (ส่วน figure scripts committed + self-contained = ดี)
**แก้:** ถ้าจะแนบลิงก์ repo — commit 2 ไฟล์นี้ หรือชี้ reproduce path ไปที่ script ที่ committed เท่านั้น

### 🟠 H. Title/keywords สัญญาเกินของที่โชว์
keywords มี "food processing; deferred consumption" แต่**ยังไม่ได้ทำ** (เป็น predicted) — reviewer กวาด keyword เทียบผลจะสะดุด
**แก้:** ตัด keyword ที่ยังไม่ demonstrate ออก หรือย้ายไป "future"; title "When Detoxification Lures the Learner" **ดีแล้ว** (ตรงผลจริง) เก็บไว้

### 🟠 I. ยังไม่มี "ช่องว่างเทียบ optimal" เป็นตัวเลขพาดหัว
โชว์ว่า learner แพ้ แต่ไม่มีเลขว่าแพ้แค่ไหน (learner ได้กี่ % ของพลังงาน optimal ขณะกินพิษ 60%)
**แก้:** เพิ่ม 1 เลข: "optimal = 0% พิษ / พลังงาน X · learner = 60% พิษ / พลังงาน Y"

---

## 3. จุดบอด "เชิงกลยุทธ์/เล่าเรื่อง"

- 🟡 **สโคปบวม:** 65 reports, aging+toxin+phases+neuroevolution — **claim เดียวคืออะไร?** ALife v2 เลือกโฟกัส toxin ถูกแล้ว แต่ต้องมั่นใจว่า "lure + aliasing breakdown" แข็งพอยืนเดี่ยว (ผมว่า**แข็งพอ** ถ้าเสริม A–C)
- 🟡 **Aging ถูกทิ้ง** = แรงงานเยอะไม่ได้ใช้ (ตัดสินใจถูกสำหรับ 2 หน้า แต่ aging self-consistent เป็น story อ่อนกว่า — เก็บเป็น paper แยกวันหลัง)
- 🟡 **"no oracle / emergent" vs จูน knob เยอะ** — reviewer อาจว่าปรากฏการณ์ถูก "จัดฉาก" ด้วยการเลือกค่า (แก้ด้วย E: sweep)

---

## 4. จุดแข็ง (ของจริง — อย่าทิ้ง)
- ✅ **ความซื่อสัตย์ทางวิทยาศาสตร์** แยก demonstrated/predicted ชัด — **หายากและ ALife ให้ค่า**
- ✅ **วิศวกรรมสะอาด:** opt-in, byte-identical, 93/93 tests, figure จากโค้ดจริง
- ✅ **"lure effect" เป็นผล counterintuitive + quantified ที่แท้จริง** — นี่คือ nugget
- ✅ escalation monotonic→non-monotonic เล่าเป็นเรื่องได้ดี

---

## 5. Checklist ก่อนกดส่ง (เรียงตามคุ้มค่า)
1. [ ] **multi-seed + CI** (แก้ A) — คุ้มสุด ทำวันเดียว
2. [ ] **NSRU เฟรมใหม่แยก** (แก้ D) — กันซ้ำรอย TURC
3. [ ] **related work 4–6 refs ที่อ่านจริง** (แก้ C)
4. [ ] **1 ประโยค "รู้ว่าเป็น POMDP; ของใหม่คือ lure"** (แก้ B)
5. [ ] **sweep พิสูจน์ lure ทั่วไป** (แก้ E)
6. [ ] **commit CLI files หรือชี้ reproduce path ที่ committed** (แก้ G)
7. [ ] **ตัด keyword ที่ยังไม่ทำ + ใส่เลข gap-vs-optimal** (แก้ H, I)
8. [ ] ตรวจ ⚠️ ท้าย abstract v2 (ชื่อผู้เขียน, ห้ามใช้รูป PREDICTED เป็นผล, ห้ามเคลม deferral)

**บรรทัดเดียว:** งานซื่อสัตย์+วิศวกรรมดี, ผลจริง (lure) น่าสนใจ — จุดบอดใหญ่สุด 2 อันคือ **(1) n=1 ยังไม่ทำ multi-seed** และ **(2) จะส่งเฟรมเดียวไป 2 venue ที่ต้องการคนละอย่าง**

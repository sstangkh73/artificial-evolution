# แผนยกระดับรายงาน NSRU ให้ "ว้าวที่สุดเท่าที่ทำได้" (Artificial Evolution)

**วันที่:** 2026-06-29
**ผู้จัดทำ:** ชิษณุพงศ์ อินทร์จันทร์ (ม.4 โรงเรียนดีบุกพังงาวิทยายน)
**เวที:** การแข่งขันวิทยาศาสตร์วิชาการ ครั้งที่ 5 ชิงถ้วยพระราชทานฯ (NSRU)
**เส้นตาย (ต้องยืนยันอีกครั้ง):** ~17 ก.ค. 2569 → เหลือประมาณ 18 วัน
**ไฟล์รายงานปัจจุบัน:** `reports/competition_full_report_artificial_evolution_2026-06-29.th.md` (+ `.docx`)

> เอกสารนี้คือแผนลงมือทุกข้อ เรียงตามผลกระทบ พร้อมคำสั่งรันจริง ผลที่จะได้ นิยาม "เสร็จ" ขอบเขตที่อ้างได้/ห้ามอ้าง ความยาก ความเสี่ยง และทางถอย
> **ปรัชญา:** ว้าวต่อคนนอก + แน่นต่อคนใน + ไม่เคลมเกินหลักฐาน (DNA ของเรา) ความยากไม่ใช่อุปสรรค ถ้าผลตอบแทนยกงานขึ้นอีกระดับ

---

## 0. สรุปผู้บริหาร

จุดแข็งที่มีแล้ว: ผลรายตัว "0 ตัวที่เมิน seed โดยไม่เคยชิม" คือหลักฐานเชิงสาเหตุที่หายากในงานเด็ก จุดอ่อนที่สุด: **n=1 ยังไม่มีสถิติหลายซีด** และผลทั้งหมดมาจาก*กลไกที่เราออกแบบเอง* (food_value_memory + กฎ pickiness) ซึ่งกรรมการเก่ง ๆ จะถามว่า "นี่คุณ hardcode พฤติกรรมเองหรือเปล่า"

แผนนี้แก้สองจุดนั้นตรง ๆ และซ้อน "ของว้าว" ขึ้นไปเป็น 3 ชั้น:

- **Tier A — ล็อกชัยชนะ:** เปลี่ยน n=1 เป็นผลหลายซีดมี CI/effect size + กราฟ legible 3 ตัว + control = งาน "แน่นระดับชาติ" (ความเสี่ยงต่ำ ต้องทำให้ครบ)
- **Tier B — ยกระดับ:** dose-response + ablation = พิสูจน์ว่าเป็นการเรียน "ตามคุณค่าจริง" และทุกองค์ประกอบจำเป็น
- **Tier C — Moonshot:** neuroevolution ที่พฤติกรรมเลี่ยงอาหารแย่ "วิวัฒน์ขึ้นเอง" (ปิดข้อกล่าวหา hardcode) + การสื่อสารเกิดเอง (emergent communication) = ถ้าลงจริงคือผลระดับชาติ/นานาชาติ

**กฎเหล็กของแผน:** Tier A ต้องเสร็จก่อน ~4 ก.ค. (มีของส่งแน่ ๆ) Tier C มี "วันหยุดตาย" (hard stop) ทุกข้อ ถ้าไม่ลงก็รายงานตามจริงและ **core paper ไม่ล้ม**

---

## 1. หลักการ 3 ข้อ (ใช้ตัดสินทุกการตัดสินใจ)

1. **ไม่ claim ก่อนมี control + หลายซีด** — ทุกผลหลักต้องมี baseline/control และทำซ้ำหลายซีดก่อนเขียนเป็นข้อสรุป
2. **ว้าวสองชั้น** — ทุกผลต้องมีทั้ง "ประโยคที่คนทั่วไปรู้สึกได้" และ "ตัวเลข/control ที่คนในวงการเชื่อ"
3. **เขียนขอบเขต claim ไว้ล่วงหน้า** — ก่อนรันแต่ละการทดลอง เขียนไว้เลยว่า "ถ้าผลออกแบบนี้ อ้างได้แค่ไหน" เพื่อกันการตีความเกินตอนตื่นเต้น

---

## 2. TIER A — ล็อกชัยชนะ (ต้องทำทุกข้อ • ความเสี่ยงต่ำ)

### A1. กราฟ "0 ตัวที่เมินโดยไม่ชิม" (ผลเด็ดที่สุด → ทำให้เห็นภาพ)

- **ทำไมว้าว:** เปลี่ยนตัวเลขในตารางเป็นภาพ 2×2 ที่คนนอกเข้าใจใน 3 วินาที: แกน (เคยชิม plant: ใช่/ไม่) × (เมิน seed: ใช่/ไม่) → ทุกตัวอยู่บนเส้นทแยงที่ถูกต้อง ช่อง "เมินทั้งที่ไม่เคยชิม" = ว่างเปล่า (0)
- **ข้อมูล:** มีแล้วใน `.codex-temp/food_tag_smoke.json` (ไม่ต้องรัน sim ใหม่)
- **วิธีทำ:** เขียนสคริปต์เล็ก `scripts/plot_taste_vs_skip_2x2.py` อ่าน per-agent dump → bar/heatmap 2×2 → `reports/figures/fig_taste_vs_skip_2x2.png`
- **ผลที่ได้:** ภาพใหม่ + ประโยค "ไม่มีเอเจนต์สักตัวที่เมินอาหารแย่โดยไม่เคยชิมเอง (0/12)"
- **เสร็จเมื่อ:** ภาพ render ออกถูก ใส่ในบท 4.5
- **อ้างได้:** การเปลี่ยนพฤติกรรมผูกกับประสบการณ์ตรงรายตัว • **ห้ามอ้าง:** เข้าใจความหมาย
- **ความยาก:** ต่ำ • **ความเสี่ยง:** แทบไม่มี

### A2. กราฟค่าที่เรียนรู้ + เส้น threshold (โชว์กลไกตัดสินใจ)

- **ทำไมว้าว:** แท่ง seed=50 / plant=250 + เส้นประ threshold=125 → เห็นชัดว่า "seed ต่ำกว่าเส้นเลยถูกข้าม" ไม่ใช่เพราะป้ายบอกว่าไม่ดี
- **ข้อมูล:** มีแล้ว (4.6) • **วิธีทำ:** สคริปต์เล็ก/เพิ่มใน `make_food_value_figures.py` → `reports/figures/fig_learned_value_threshold.png`
- **เสร็จเมื่อ:** ใส่ในบท 4.6 • **ความยาก:** ต่ำ

### A3. ฮิสโตแกรม learning speed (โชว์ว่าเรียนกันทั้งกลุ่ม)

- **ทำไมว้าว:** กระจาย 2–59 ticks (เฉลี่ย 14.1) → "เรียนไม่พร้อมกันแต่เรียนกันหมด 10/10"
- **ข้อมูล:** มีแล้ว • **วิธีทำ:** สคริปต์เล็ก → `reports/figures/fig_learning_speed_hist.png` • **ความยาก:** ต่ำ

### A4. ⭐ Multi-seed confirmatory + error bar + สถิติ (คันโยกใหญ่สุด)

- **ทำไมว้าว:** เปลี่ยน "n=1 อาจฟลุค" เป็น "ผลทำซ้ำได้ มี 95% CI" — กรรมการให้น้ำหนัก error bar มากที่สุด และตอนนี้ RNG ผูก seed แล้ว (แก้ 26 มิ.ย.) จึงทำ replicate จริงได้
- **วิธีรัน (มี `--seed` + `--dump` อยู่แล้ว → loop):**
  ```powershell
  # 30 ซีด ทั้งกลุ่ม A (control) และ B (learning) เงื่อนไขเดียวกัน
  foreach ($s in 20260610..20260639) {
    python scripts\food_value_study_driver.py --model v2 --ticks 6000 --body 37 --drain-mult 0.05 --food-energy-mult 50 --low-value-food 6 --seed $s --dump data\multiseed\A_$s.json
    python scripts\food_value_study_driver.py --model v2 --ticks 6000 --body 37 --drain-mult 0.05 --food-energy-mult 50 --low-value-food 6 --value-learning --seed $s --dump data\multiseed\B_$s.json
  }
  ```
- **ต้องเขียนเพิ่ม:** `scripts/aggregate_food_value_multiseed.py` → อ่าน dump ทั้งหมด, คำนวณ mean±SD ของ seed-meals ต่อ window, 95% CI, **Mann-Whitney U** (A vs B, เหมาะ n เล็ก/ไม่ปกติ) + **effect size** (rank-biserial / Cliff's delta), แล้ววาดกราฟเส้น A vs B พร้อม **แถบ CI** → `reports/figures/fig_multiseed_seed_consumption_CI.png`
- **ผลที่ได้:** กราฟ error-bar + ตารางสถิติ "n=30, p=..., CI=..., effect=..." → แทนที่/เสริมภาพที่ 1
- **เสร็จเมื่อ:** ทุก claim หลักของบท 4.3 มีตัวเลขสถิติรองรับ + เพิ่มหัวข้อ "การทำซ้ำและสถิติ (Reproducibility & Statistics)" ในบท 3 หรือ 4
- **อ้างได้:** ผลแตกต่างอย่างมีนัยสำคัญและทำซ้ำได้ • **ห้ามอ้าง:** เกินเงื่อนไขทดลอง (energy-surplus)
- **ความยาก:** กลาง • **ความเสี่ยง (สำคัญ):** *moment of truth* — ถ้า effect อ่อนลงเมื่อหลายซีด ต้องรายงานตามจริง (ดูทางถอย §8)

### A5. Memory-disabled control ในชุดรายตัวเดียวกัน

- **ทำไมว้าว:** ปิดคำถามกรรมการ "ชัวร์เหรอว่าเพราะ memory" — รัน config per-agent เดิมแต่ **ไม่เปิด** `--value-learning` แล้วแสดงว่า `agents_skipped_raw_seed = 0`
- **วิธีรัน:**
  ```powershell
  python scripts\food_value_study_driver.py --model v2 --ticks 600 --low-value-food 6 --food-energy-mult 50 --drain-mult 0.1 --population 12 --world 40 --max-pop 40 --seed 20260610 --dump .codex-temp\food_tag_control_nolearn.json
  ```
- **ผลที่ได้:** ตารางเทียบ "เปิด memory: 10 ตัวเมิน / ปิด memory: 0 ตัวเมิน" • **ความยาก:** ต่ำ

**Definition of done ของ Tier A:** ผลหลักทุกอันมี n/CI/p/effect size + กราฟใหม่ 3–4 ตัว + control ครบ → งานขึ้นจาก "ดีระดับโรงเรียน" เป็น "แน่นระดับชาติ"

---

## 3. TIER B — ยกระดับ (คุ้มมาก • ความเสี่ยงกลาง)

### B1. Dose-response บน pickiness (รันได้เลย ไม่ต้องแตะโค้ด)

- **ทำไมว้าว:** มี `--pickiness` อยู่แล้ว กวาด 0.3 / 0.5 / 0.7 × หลายซีด → แสดงว่า "ยิ่ง threshold สูง ยิ่งเมิน seed มาก" อย่างเป็นระบบ = พฤติกรรมตอบสนองต่อพารามิเตอร์อย่างมีเหตุผล ไม่ใช่บังเอิญ
- **วิธีรัน:** loop `--pickiness {0.3,0.5,0.7}` × `--seed` หลายค่า → aggregate → กราฟ pickiness vs seed-skip rate
- **ความยาก:** ต่ำ-กลาง

### B2. ⭐ Dose-response บน "ช่องว่างคุณค่า" (ต้อง patch โค้ด — เด็ดกว่า)

- **ทำไมว้าว:** ถ้าให้ plant:seed = 2x, 3x, 5x, 10x แล้ว "ยิ่งช่องว่างกว้าง ยิ่งเมิน seed เร็ว/แรง" → หลักฐานหนักมากว่ามันเรียน **"คุณค่าเชิงปริมาณ"** ไม่ใช่สวิตช์ on/off นี่คือผลที่ยกระดับจาก "แยกได้/ไม่ได้" เป็น "ไวต่อขนาดของผลตอบแทน"
- **ต้อง patch:** ปัจจุบัน `--low-value-food` = อัตราเกิด ไม่ใช่พลังงาน และ `--food-energy-mult` สเกลทุกอาหารเท่ากัน (ไม่เปลี่ยน ratio) → ต้องเพิ่ม flag เช่น `--low-value-energy-scale` ที่สเกลพลังงาน raw_seed อย่างเดียว (แก้ใน `world/metabolism.py` + ส่งผ่าน driver) พร้อมเขียน test กัน regression
- **วิธีรัน:** loop ค่า gap × seeds → aggregate → กราฟ gap vs avoidance (มี error bar)
- **เสร็จเมื่อ:** มีกราฟ dose-response + ผ่าน unit test เดิมทั้งหมด
- **ความยาก:** กลาง (แตะโค้ด core) • **ความเสี่ยง:** ต้องไม่ทำผล A/B เดิมเพี้ยน → รัน regression หลัง patch

### B3. Ablation study (โชว์ว่าทุกองค์ประกอบจำเป็น)

- **ทำไมว้าว:** ตารางเดียวที่ปิดทีละองค์ประกอบ (ปิด memory / ปิด energy-surplus / ปิด pickiness) แล้วแสดงว่าการเมิน seed หายไป → พิสูจน์ว่าแต่ละชิ้น "จำเป็น" ไม่ใช่ของแถม กรรมการสาย method รักมาก
- **วิธีรัน:** ใช้ flag ที่มี (`--value-learning` on/off, `--drain-mult` สูง=หิว, `--pickiness`) × หลายซีด
- **ความยาก:** กลาง

**Definition of done ของ Tier B:** มีหลักฐาน "เรียนตามคุณค่าจริง (graded)" + ตาราง ablation ที่แต่ละองค์ประกอบจำเป็น

---

## 4. TIER C — MOONSHOT (ว้าวสุด ถ้าลงจริง • ความเสี่ยงสูง • แยกจาก core)

> กฎ: ทุกข้อมี **วันหยุดตาย (hard stop)** ถ้าไม่ลงภายในวันนั้น → เขียนเป็น "งานต่อไป/ผล negative ตามจริง" แล้วเดินหน้าส่งด้วย Tier A+B core paper ไม่ล้มเด็ดขาด

### C1. ⭐ Neuroevolution: พฤติกรรมเลี่ยงอาหารแย่ "วิวัฒน์ขึ้นเอง" (ปิดข้อกล่าวหา hardcode)

- **ทำไมว้าวสุด:** จุดอ่อนใหญ่ของ core paper คือ "พฤติกรรมมาจากกฎ pickiness ที่คุณเขียนเอง" ถ้าโชว์ได้ว่า **สมองนิวรอลที่วิวัฒน์ด้วย neuroevolution ก็เลี่ยงอาหารพลังงานต่ำเองโดยไม่มีกฎ pickiness** = พิสูจน์ว่าการเลือกตามคุณค่า "เกิดได้เอง" ไม่ใช่ของที่เรายัดใส่ → นี่คือ "ว้าว" ที่แท้จริงของ ALife
- **Infra:** มี `scripts/run_neuroevolution.py` (flags: `--generations --pop --ticks --world --seed --eval-seed --eval-seeds --food-spawn --max-food ...`) + `render_neuroevolution_demo.py` + ผลเดิม `data/neuroevolution_best_2026-06-27.json`
- **ต้องทำเพิ่ม:** ใส่อาหาร 2 ค่าพลังงาน (raw_seed/raw_plant) ลงในโลกประเมินของ neuroevolution (ถ้ายังไม่มี) + วัด "อัตราการกิน low-value ของ best genome เทียบ random baseline" ข้ามหลาย `--eval-seeds`
- **วิธีรัน (ตั้งต้น):**
  ```powershell
  python scripts\run_neuroevolution.py --generations 30 --pop 40 --ticks 300 --eval-seeds 5 --seed 1 --dump data\neuro_value\run_seed1.json --save-best data\neuro_value\best_seed1.json
  # ทำซ้ำหลาย --seed เพื่อความเชื่อมั่น
  ```
- **อ้างได้ (ถ้าลง):** การเลือกตามคุณค่าเกิดได้จากการวิวัฒนาการ ไม่ต้องมีกฎกำหนด • **ห้ามอ้าง:** เข้าใจ/วางแผน
- **Hard stop:** ~11 ก.ค. ถ้ายังไม่เห็นสัญญาณ → ย้ายเป็น "งานต่อไป"
- **ความยาก:** สูง • **ความเสี่ยง:** สูง (อาจต้องปรับ eval world)

### C2. ⭐⭐ Emergent communication (signal channel) — ถ้าลง = ระดับนานาชาติ

- **ทำไมว้าวสุด ๆ:** การสื่อสารที่เกิดเองในประชากร AI เป็นหัวข้อแนวหน้าจริง ๆ ของ ALife ถ้าโชว์ได้ว่าเอเจนต์วิวัฒน์มา "ใช้ช่องสัญญาณ" เพื่อบอกข้อมูลที่เป็นประโยชน์ และพิสูจน์ด้วย control = ผลที่กรรมการระดับชาติ/ISEF จำได้
- **Infra ที่มี (จาก 27 มิ.ย.):** signal output head, signal input channel, **receiver-blind hook**, **signal-shuffle hook**, tests — แต่ **ยังไม่มี CLI experiment** ที่รันครบวงจร
- **ต้อง build:** harness ทดลองการสื่อสาร = วิวัฒน์ด้วย neuroevolution ที่เปิด signal channel แล้วเทียบ fitness ระหว่าง 4 เงื่อนไข:
  1. normal (มี signal)
  2. **receiver-blind** (ตัวรับมองไม่เห็น signal)
  3. **signal-shuffle** (สับ signal ให้ไร้ความหมาย)
  4. no-signal (ปิดช่อง)
  - ถ้า fitness ตกเมื่อ receiver-blind/shuffle แต่ไม่ตกเมื่อ control อื่น → **หลักฐานว่า signal ถูกใช้สื่อสารจริง** (ไม่ใช่ noise)
- **multi-seed:** จำเป็น (อย่างน้อย 10 ซีด/เงื่อนไข) + รายงาน effect size เทียบ controls
- **อ้างได้ (ถ้าลง):** เกิดการใช้สัญญาณที่มีฟังก์ชัน โดยพิสูจน์ผ่าน control • **ห้ามอ้าง:** ภาษา/ความหมายเชิงสัญลักษณ์แบบมนุษย์
- **Hard stop:** pilot ต้องเห็นสัญญาณภายใน ~13 ก.ค. ไม่งั้นเป็น "foundation + งานต่อไป"
- **ความยาก:** สูงมาก • **ความเสี่ยง:** สูงมาก — **แต่แม้ผล negative ก็มีค่า** (รายงานตามจริงว่า "ยังไม่เกิดการสื่อสารในเงื่อนไขนี้" = ซื่อสัตย์ + เป็นวิทยาศาสตร์)

### C3. เรื่องเล่า "การเรียนรู้ 2 ระดับเวลา" (งานเขียน — เสี่ยงต่ำ คุ้ม)

- **ทำไมว้าว:** รวม within-life (food-value learning) + across-generation (neuroevolution) เป็นเรื่องเดียวบนแพลตฟอร์มเดียว → contribution ดูใหญ่และเป็นระบบขึ้นมาก โดยเล่าอย่างซื่อสัตย์ว่าเป็น "2 การศึกษาบนโลกเดียวกัน"
- **ต้องทำ:** ส่วนใหญ่เป็นการเขียน (เพิ่มกรอบในบท 1 + บท 5) + ใช้ผล neuroevolution ที่มี
- **ความยาก:** ต่ำ (ถ้า C1 ให้ผล) • **ความเสี่ยง:** ต่ำ

---

## 5. กราฟทั้งหมดในเล่มสุดท้าย (เป้าหมาย)

| ภาพ | มาจาก | สถานะ |
| --- | --- | --- |
| เส้นโค้งการเรียนรู้ A vs B **+ แถบ CI** | A4 | อัปเกรดจากของเดิม |
| 2×2 taste vs skip (0 ตัวไม่ชิม) | A1 | ใหม่ |
| ค่าที่เรียนรู้ + เส้น threshold | A2 | ใหม่ |
| ฮิสโตแกรม learning speed | A3 | ใหม่ |
| trajectory รายตัว | เดิม | มีแล้ว |
| งบพลังงาน | เดิม | มีแล้ว |
| dose-response: value gap vs avoidance | B2 | ใหม่ (ถ้าทำ) |
| neuroevolution: evolved vs random กินอาหารแย่ | C1 | ใหม่ (ถ้าลง) |
| communication: fitness ต่อ 4 controls | C2 | ใหม่ (ถ้าลง) |
| carrying capacity | เดิม | **พิจารณาตัด/ย่อ** (เป็นเรื่อง paper สูญพันธุ์) |

---

## 6. ตารางค่าสถิติที่จะรายงาน (ยกระดับความน่าเชื่อถือ)

| ผล | สถิติที่จะใส่ |
| --- | --- |
| A vs B seed consumption | n (จำนวนซีด), mean±SD ต่อ window, 95% CI, Mann-Whitney U, p, effect size |
| per-agent skip | สัดส่วน 10/12, 0/12 ไม่ชิม (ค่าแน่นอน), mean learning speed 14.1 [2–59] |
| dose-response | slope/แนวโน้ม avoidance ตาม gap + CI |
| neuroevolution | low-value intake: evolved vs random (effect size, หลายซีด) |
| communication | fitness: normal vs receiver-blind vs shuffle vs no-signal (effect size, หลายซีด) |
| reproducibility | seed policy, จำนวนซีด, ยืนยัน same-seed reproducible |

---

## 7. ไทม์ไลน์ ~18 วัน (29 มิ.ย. → 17 ก.ค.)

| ช่วง | งาน | เกต |
| --- | --- | --- |
| 29 มิ.ย.–1 ก.ค. | A1–A3 (กราฟจากข้อมูลเดิม) + เขียน harness multi-seed + A5 control + **kick off A4 รัน 30 ซีด** | กราฟเร็วเสร็จ, รันเดิน |
| 2–4 ก.ค. | A4 aggregate + สถิติ + กราฟ CI + หัวข้อ reproducibility → **rebuild .docx + เช็กหน้า** | ✅ **Tier A เสร็จ = ล็อกชัยชนะ** |
| 5–7 ก.ค. | B1 pickiness sweep + patch B2 value-gap + รัน + B3 ablation | Tier B เสร็จ |
| 8–11 ก.ค. | C1 neuroevolution two-value (hard stop 11 ก.ค.) | C1 ลง/ไม่ลง ตัดสิน |
| 12–13 ก.ค. | C2 communication harness + pilot (hard stop 13 ก.ค.) + C3 เขียนเรื่องเล่า | C2 ลง/ไม่ลง ตัดสิน |
| 14–15 ก.ค. | รวมผลทุก tier เข้าเล่ม + rebuild .docx + เช็ก ≤30 หน้า + ตารางสถิติ | เล่มนิ่ง |
| 16 ก.ค. | buffer + แปลง PDF + ตรวจรอบสุดท้าย | พร้อมส่ง |
| 17 ก.ค. | **ส่ง** | — |

**กฎกันพลาด:** ถ้าวันไหนช้า ให้ตัด Tier C ก่อนเสมอ ห้ามให้ moonshot ทำ Tier A/B หรือการส่งเสีย

---

## 8. ความเสี่ยง + ทางถอย (ทุกอย่างมีแผนสำรอง)

| ความเสี่ยง | ทางถอย (ยังส่งงานดีได้) |
| --- | --- |
| multi-seed ทำ effect อ่อนลง | รายงานตามจริง + ชู per-agent "0 ไม่ชิม" ซึ่งเป็นหลักฐานเชิงกลไก ไม่ไวต่อซีดเท่าค่าเฉลี่ย |
| patch value-gap (B2) ทำผลเดิมเพี้ยน | รัน regression ทันที, ถ้าแก้ไม่ทันใช้ B1 pickiness แทน |
| neuroevolution (C1) ไม่โชว์ value-discrimination | เขียนเป็น "งานต่อไป" + ผล negative ตามจริง core ไม่กระทบ |
| communication (C2) ไม่เกิด | รายงาน honest negative (มีค่าทางวิทยาศาสตร์) + เป็น foundation สำหรับงานหน้า |
| เวลาไม่พอ | Tier A อย่างเดียว = งานแน่นพอส่งและแข่งได้จริง |

---

## 9. นิยาม "ว้าว" แบบซื่อสัตย์ (กันหลงทาง)

**ว้าว = สิ่งเหล่านี้:**
- ความเข้มที่ปฏิเสธไม่ได้: หลายซีด, CI, control, ablation
- ผลที่ "เกิดเอง" และเราพิสูจน์ว่าไม่ได้ hardcode: per-agent causal + neuroevolution
- (ถ้าลง) การสื่อสารเกิดเองที่ผ่าน control

**ไม่ใช่ว้าว (ห้ามแตะ):**
- อ้างว่า AI "เข้าใจ" / รู้คิด / มีจิต
- อ้างทำฟาร์ม / วางแผน / ภาษาแบบมนุษย์
- ขยายผลเกินเงื่อนไขทดลอง

> ความซื่อสัตย์ไม่ใช่ข้อจำกัด มันคือสิ่งที่ทำให้ "ว้าว" ของเราน่าเชื่อ — เด็กที่กล้าเขียน "ยังไม่เกิด" ในที่ที่ควรเขียน คือเด็กที่กรรมการเชื่อเมื่อเขียนว่า "เกิดแล้ว"

---

## 10. เช็กลิสต์รวม (ติ๊กทีละข้อ)

**Tier A (ต้องครบ):**
- [ ] A1 กราฟ 2×2 taste vs skip
- [ ] A2 กราฟ learned value + threshold
- [ ] A3 ฮิสโตแกรม learning speed
- [ ] A4 รัน 30 ซีด A/B + harness aggregate + สถิติ (CI, Mann-Whitney, effect size) + กราฟ CI
- [ ] A4 เพิ่มหัวข้อ Reproducibility & Statistics
- [ ] A5 memory-disabled control
- [ ] rebuild .docx + เช็กหน้า ≤30

**Tier B:**
- [ ] B1 pickiness sweep × ซีด
- [ ] B2 patch `--low-value-energy-scale` + test + รัน value-gap sweep
- [ ] B3 ablation table

**Tier C (moonshot, มี hard stop):**
- [ ] C1 neuroevolution two-value world + วัด evolved vs random (hard stop 11 ก.ค.)
- [ ] C2 communication harness 4 controls + multi-seed (hard stop 13 ก.ค.)
- [ ] C3 เรื่องเล่า 2 ระดับเวลา

**ปิดเล่ม:**
- [ ] รวมผลเข้าบท 4–5 + ตารางสถิติ + ขอบเขต claim ทุกผล
- [ ] rebuild .docx → verify ≤30 หน้า → PDF → ส่ง (≤17 ก.ค.)

---

> **ก้าวแรกที่แนะนำให้ลงมือเลย:** A1–A3 (กราฟจากข้อมูลเดิม ได้ของว้าวเร็ว) + เขียน harness multi-seed แล้ว kick off A4 30 ซีดทันที — เพราะ A4 คือคันโยกที่เปลี่ยนเกมและใช้เวลารันนานสุด ยิ่งเริ่มเร็วยิ่งดี

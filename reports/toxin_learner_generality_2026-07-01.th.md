# "lure" ทั่วไปแค่ไหน? — ทดสอบข้ามกฎการเรียนรู้ (แก้ red-team R2-1)

**Is the "lure" an artifact of our specific gate, or general across learners?**

ผู้วิจัย: ชิษณุพงศ์ อินจันทร์ · 2026-07-01 · ตอบข้อ red-team **R2-1** โดยตรง
สคริปต์: `scripts/run_toxin_learner_comparison.py` · ไม่แตะ core (harness ใช้ net energy จริงจาก `_apply_toxin`)

---

## 1. คำถาม/สมมติฐาน (hypothesis-testing)
red-team รอบ 2 (R2-1) ตั้งข้อสงสัย: คำเคลม "per-type learning แพ้/ถูก lure" อาจเป็นสมบัติของ **gate เฉพาะเรา** (`_food_worth_eating`: ชิมของใหม่ครั้งเดียว → แช่แข็งค่า → เกณฑ์ pickiness) — learner มาตรฐานที่ **sample ต่อ** อาจฟื้นตัวและ lure หายไป

**สมมติฐานที่จะพยายามหักล้าง (H0):** lure หายเมื่อใช้ learner มาตรฐาน
**คำทำนายของเรา (H1):** ตรงข้าม — learner ที่ sample ต่อจะลู่เข้า "ค่าเฉลี่ยจริง (blend)" ซึ่ง > staple → **ถูก lure มากกว่า** (gate เดิมที่แช่แข็งกลับ *ประเมินต่ำ*)

## 2. วิธีการ
เปรียบเทียบ 4 กฎเรียนรู้กับอาหาร two-state (สด=พิษ net 2 / เก่า=ปลอดภัย net 10 — จาก `_apply_toxin` จริง, staple 5) ที่สัดส่วนพิษ 20–60% · 30 seeds × 100 agents · วัด **% agent ที่ถูก lure** (ค่าอาหาร fruit > staple → จัดพิษเป็นอาหารดีสุด):
- **L1 sim gate** — ชิมครั้งเดียว + EMA + เกณฑ์ pickiness (แช่แข็งเมื่อ taste พิษก่อน)
- **L2 ε-greedy** — optimistic init, sample-average, สุ่มสำรวจต่อ (ε=0.1)
- **L3 softmax** — optimistic init, sample-average, เลือกแบบ Boltzmann (τ=2)
- **L4 sample-avg greedy** — optimistic init, sample-average, greedy

## 3. ผล

**% agent ถูก lure (30 seeds, 95% CI):**
| % พิษ | blend | **L1 gate** | **L2 ε-greedy** | **L3 softmax** | **L4 sample-avg** |
|---:|---:|---:|---:|---:|---:|
| 20% | 8.4 | 80 | 98 | **100** | 77 |
| 30% | 7.6 | 63 | 93 | **99** | 62 |
| 40% | 6.8 | 42 | 81 | **94** | 47 |
| 50% | 6.0 | 19 | 58 | **80** | 28 |
| 60% | 5.2 | 6 | 28 | **51** | 11 |

![Learner comparison](figures/toxin_learner_comparison.png)

## 4. ข้อสรุป (แปลงจุดอ่อนเป็นจุดแข็ง)

- **H0 ถูกหักล้าง — lure ไม่หาย:** เกิดกับ **ทุก** learner (ต่ำกว่าขอบเขต analytic p\*=62.5% ที่ blend=staple)
- **lure *แข็งขึ้น* กับ learner ที่สำรวจต่อ:** softmax/ε-greedy ถูก lure **มากกว่า** gate เดิมชัดเจน (softmax ~99% ที่พิษ 30% เทียบ gate 63%) เพราะลู่เข้า blend จริง (>staple) — **gate เดิมของเราประเมิน lure ต่ำเกินไป** (การแช่แข็งบางตัวที่ taste พิษก่อน กด lured% ลง)
- **greedy-family (L1, L4) คล้ายกัน:** greedy ล้วนก็ "ล็อก" ไม่กิน fruit เมื่อค่าตกใต้ staple → lure ต่ำกว่า exploration-family แต่**ยังมี lure**
- **discrimination = 0 สำหรับทุก learner (analytic):** เพราะค่า key ด้วย "ชนิด" = ค่าเดียวต่อชนิด → ตัดสินใจเท่ากันทุกอายุ**โดยโครงสร้าง** ไม่ว่ากฎอะไร — ยืนยัน rule-independent

**คำเคลมที่ตอนนี้อ้างได้ (มีหลักฐาน):**
1. **discrimination = 0 → rule-independent/analytic** (ผลแข็งที่สุด)
2. **lure เป็นทั่วไป ไม่ใช่ artifact ของ gate เรา** — เกิดกับ 4 learner, ถูกจำกัดด้วยขอบเขต analytic p\*, และ **exploration-based learner ถูก lure มากกว่า** (ทิศทางเรียงตามการสำรวจ)
3. *ยังไม่เคลม:* fitness cost ของ lure (โหมดอิ่ม — R2-3)

## 5. ผลต่อเอกสารส่ง
เปลี่ยนคำใน abstract/complete report จาก "*standard-learner comparison is planned*" → **"tested; lure survives and is stronger for exploration-based learners"** = ขยายคำเคลมด้วยหลักฐาน กันข้อโจมตี "artifact ของ gate" ได้แล้ว

## 6. การทำซ้ำ
`python scripts/run_toxin_learner_comparison.py` (self-contained, ขับ `_apply_toxin` จริง) · suite 93/93

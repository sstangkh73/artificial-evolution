# physics-loop progress (รอบ 1: ฟิสิกส์)

ไฟล์นี้คือความจำของลูป ทุกรอบให้เขียนต่อท้าย ห้ามลบของเดิม

## สถานะเริ่มต้น (2026-10-15 เตรียมโดย Claude ในเซสชันกับผู้ใช้)
- **ต้นแบบ 2D แบบลบ element:** อยู่ที่ `prototypes/fracture_poc/` ผลและปัญหาอยู่ใน `docs/physics_world/00_design.md` ข้อ 5–6 (มุมติดกริด, รัศมี nonlocal ที่เลือกเอง, ไวต่อตำแหน่งตี)
- **เป้าตรวจจากเอกสาร:** อยู่ใน `docs/physics_world/01_literature.md` คำนวณ EPA-PD จากข้อมูลแก้วของ Dibble ซ้ำได้ (n = 169) R² = 0.82 ทิศ PD+ EPA+ AOB− และพบว่าวัสดุ 4 ชนิดของ Dibble ให้ ∛มวล/PD ต่างกันไม่เกิน 5%
- **ค่าวัสดุพร้อมแหล่งอ้างอิง:** `physics-loop/spec/materials.json` ค่าที่เป็นสมมติฐานมีป้าย ASSUMPTION กำกับไว้
- **ยังไม่มีแพ็กเกจ `lithics/`:** เริ่มจากขั้น 1 ใน plan.md

## Review log
- **รอบ 1 (ขั้น 1) Codex รีวิวงาน Claude** (log: `physics-loop/.loop/codex/20261015-011758.log`) พบ 10 ข้อ แก้แล้ว 9 ข้อ:
  - `Stone` ไม่ปฏิเสธ phase index ติดลบหรือเกินจำนวน phase และ cell_size/thickness ≤ 0 → เพิ่มการตรวจ
  - 3D ปัดจำนวนชั้นทำให้มวลไม่ตรงกับ `depth_m` → บังคับให้ `depth_m` เป็นจำนวนเต็มของเซลล์
  - `make_core` ไม่ตรวจค่าบวก → เพิ่มการตรวจ, เงื่อนไขฐาน `> 2h` เปลี่ยนเป็น `> 0` และตรวจว่าทุกแถวมีเซลล์แทน
  - `platform_normal` เป็น 2D ใน 3D → แก้ให้ตรงมิติ
  - เทสต์: อ่าน spec จาก path ของเทสต์เอง, ตรวจ `MATERIAL_NAMES` เป็น tuple, ตรวจค่าแร่ทุกฟิลด์และค่า Phase, เพิ่ม EPA 110°, เพิ่มกรณี depth ไม่ลงตัว และกรณี Stone ผิด
  - ไม่แก้: "เทสต์ containment ของ polygon จริง" เพราะเทสต์พื้นที่เทียบสูตรรูปหลายเหลี่ยม (คลาด ≤2%) และเทสต์มุมหน้าแกน (±1°) ครอบคลุมแล้ว
- **รอบ 2 (ขั้น 2 ก) Codex รีวิวงาน Claude** (log: `physics-loop/.loop/codex/20261015-012643.log`) พบ 11 ข้อ แก้ 10 ข้อ:
  - 02: E′ ขึ้นกับโหมด (plane stress ใช้ E′ = E) → เขียนให้ชัด; คำว่า "กำหนดแน่นอน" ของ spsolve → แก้เป็นคาดว่าเท่าเดิมใน environment เดียวกันและจะตรวจจริงใน V10; ขอบรูเป็น polygon → บันทึกเป็นแหล่ง error
  - `fem2d`: ปฏิเสธ quadrature point ที่ r ≤ 0 และปฏิเสธการกำหนด u_r ≠ 0 บนแกน axisymmetric (+ เทสต์)
  - เทสต์: Kirsch extrapolation ดีกรี 2 จาก 3 จุดไม่มีจุดตรวจ → เพิ่มเทสต์โปรไฟล์ σ_yy ที่ r = 1.1a–3a เทียบสูตร Kirsch (<3%); ลบ assertion 1% ที่ซ้ำ; convergence ต้องลดลงทุกระดับ; เพิ่ม patch test บน quad บิดเบี้ยว และแท่งสองวัสดุ (E ต่อ element)
  - ไม่แก้ข้อ 1 (V11 ยังไม่ครบ Hertz/SEN): เป็นขอบเขตที่ตั้งใจแบ่งไว้ ทำในส่วน ข รอบหน้า
- **รอบ 3 (ขั้น 2 ข) Codex รีวิวงาน Claude** (log: `physics-loop/.loop/codex/20261015-013705.log`) ไม่พบเครื่องหมายผิดใน J หรือ active set พบ 10 ข้อ แก้ 8 ข้อ:
  - Hertz oracle ใช้ P จาก FE เอง → เพิ่มเทสต์อิสระ a = √(Rδ) และ P(δ) เทียบ Hertz (1 < P/P_H < 1.03, ลดลงเมื่อวัตถุใหญ่ขึ้น)
  - convergence ตรวจแค่ monotonic → เพิ่มขอบบนสัมบูรณ์ทุกระดับ (Hertz < 3%, < 2%; SEN < 2.5%, < 1%)
  - ตัวเลขใน 02 ไม่ตรงกับที่เทสต์บังคับ → ปรับเทสต์ให้บังคับใกล้ค่าที่รายงาน และแก้ตาราง SEN n = 50 เป็น −1.6% (โดเมนเดียวกับตาราง)
  - projection ไม่ใช่ pressure แบบจุด → เขียนใน docstring และ 02 ว่าเป็น L2 projection และแกว่ง −2.7% p₀ ที่ขอบ
  - ไม่มีหลักฐาน complementarity → `ContactResult` คืน `surface_gap_m` และ `in_contact` พร้อมเทสต์เงื่อนไข Signorini
  - ไม่ใช่ทรงกลม exact → เขียนข้อจำกัดเรื่องพาราโบลา/gap แนว z ใน docstring และ 02
  - Tada ใช้กับแถบยาว → เพิ่มเทสต์ H = 2W เทียบ 3W ต่างกัน < 0.3%
  - SEN ตรวจโดเมนเดียว → บังคับทุกโดเมนคลาด < 1%
  - ไม่แก้: "j_integral ไม่ตรวจทิศรอยร้าว" เพราะ API ระบุไว้ใน docstring ว่ารอยร้าวต้องอยู่ตามแนว −x และไม่มีแรงบนผิวร้าว การตรวจทิศจาก mesh ทำไม่ได้ทั่วไป; ใช้เฉพาะตรวจ V11
  - ไม่แก้: "V11 ยังไม่เชื่อมกับ validate" เพราะ `lithics/validate.py` เป็นงานขั้น 11

## Log

### รอบ 1 — 2026-10-15 (LEAD=claude, Codex รีวิว)
- **ทำ:** ขั้น 1 สร้าง `lithics/__init__.py`, `lithics/materials.py` (`load_material`, `MATERIAL_NAMES`, `Material` พร้อม E′ และ G_c = K_IC²/E′), `lithics/stone.py` (`Stone` dim 2/3, `Phase`, `extract`, `make_core` กำหนด EPA/แท่นตี/ความลึก, mosaic แบบ Voronoi ของแกรนิตที่ต้องระบุ seed) และ `tests/lithics/test_lithics_materials_stone.py`
- **สมมติฐานที่ต้องบันทึกใน 02:** แร่ใน mosaic ใช้ความหนาแน่นและ K_IC ของแกรนิตรวม เพราะ spec ไม่มีค่ารายแร่; จำนวนเมล็ด Voronoi = ปริมาตรกล่อง / grain_size^dim
- **หมายเหตุ:** โฟลเดอร์ `agents/.skills` ว่างเปล่า (ไม่มี SKILL.md ให้อ่าน) จึงทำงานตาม PROMPT.md และ plan.md
- **verify -Quick:** ผ่านข้อ package, คำต้องห้าม, pytest (243), วัสดุ 3 ข้อ; ยังไม่ผ่าน plan เปิด, เอกสาร 02/03, results.json, และ uncommitted (ลูปจะ commit)
- **งานถัดไป:** ขั้น 2 solver ยืดหยุ่น 2D (plane strain + axisymmetric, assembly vectorized) และเทสต์ V11 (แท่ง, Kirsch, Hertz p_max, SEN K_I) อาจแบ่งเป็น 2 รอบ: (ก) solver + แท่ง + Kirsch, (ข) axisymmetric + Hertz + SEN + เขียน 02 ส่วน solver

### รอบ 2 — 2026-10-15 (LEAD=claude, Codex รีวิว)
- **ทำ:** ขั้น 2 ส่วน ก: `lithics/fem2d.py` (Q4 isoparametric, plane strain/plane stress/axisymmetric, assembly vectorized + sparse, `traction_forces`, `boundary_edges`, `quad_mesh` สำหรับ mesh แนบรูปทรง), `tests/lithics/test_lithics_fem2d.py` (15 เทสต์), เขียน `docs/physics_world/02_physics_spec.md` ส่วน 1–2
- **ผล:** แท่ง/ทรงกระบอก/patch แม่นตรงระดับ 1e-8; Lamé u_r < 0.5%; Kirsch SCF 3.005 บน mesh เชิงขั้ว
- **ปัญหาที่เจอ:** รูวงกลมแบบขั้นบันไดบนกริดเซลล์ให้ SCF 2.55 (a = 16h) และ 2.64 (a = 24h) ต่ำไป 12–15% → V11 Kirsch วัดบน mesh แนบรูปทรง (ตรวจ solver) และบันทึกผลขั้นบันไดใน 02 §2.3 ให้รายงานใน 03 และพิจารณาใน V6
- **verify -Quick:** pytest 258 ผ่าน, 02 มีแล้ว; ยังไม่ผ่าน plan เปิด, 03, results.json, uncommitted (ลูป commit)
- **งานถัดไป:** ขั้น 2 ส่วน ข: Hertz p_max (axisymmetric, ทรงกลมแข็ง/ยืดหยุ่นกดผิวเรียบ, เทียบ Johnson 1985) และ SEN K_I (J-integral หรือ displacement extrapolation เทียบ Tada et al. สูตร SEN) แล้วติ๊กขั้น 2

### รอบ 3 — 2026-10-15 (LEAD=claude, Codex รีวิว)
- **ทำ:** ขั้น 2 ส่วน ข: `lithics/contact.py` (สูตร Hertz Johnson 1985 §4.2, `effective_modulus`, `tensor_mesh`, `rigid_sphere_indent` แบบ active set axisymmetric), `fem2d.j_integral` (EDI, Shih–Moran–Nakamura 1986), `tests/lithics/test_lithics_contact_sen.py` (14 เทสต์), 02 ส่วน 2.4–2.5 ติ๊กขั้น 2 แล้ว
- **ผล:** Hertz p₀ คลาด −1.3% (n = 60), P(δ) สูง 1.2–2.3% เพราะวัตถุจำกัด; SEN K_I จาก J คลาด −0.6% (100 เซลล์บนกริด Stone), −0.2% (200)
- **ปัญหาที่เจอ:** displacement extrapolation บน Q4 ธรรมดาคลาด 5–13% จึงใช้ J แทน (บันทึกใน 02 §2.5); projection ความดันแกว่งที่ขอบสัมผัส
- **verify -Quick:** pytest 272 ผ่าน; ยังไม่ผ่าน plan เปิด, 03, results.json, uncommitted (ลูป commit)
- **งานถัดไป:** ขั้น 3 แบบจำลองการแตก phase-field (AT1 หรือ AT2) บน `fem2d` ใช้ `stiffness_scale` เป็น degradation; ℓ จาก E, G_c, σ_t ตามสูตรที่อ้างอิงได้ (เช่น AT1: σ_c = √(3 G_c E′/(8ℓ)) — Tanné et al. 2018 JMPS 110:80) ควรแบ่ง: (ก) solver staggered + เทสต์ร้าวตรงใน SEN/แท่ง, (ข) ร้าวโค้ง/ทิศไม่ติดกริด

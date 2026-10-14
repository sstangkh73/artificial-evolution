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

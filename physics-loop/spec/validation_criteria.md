# เกณฑ์ตรวจความถูกต้องของฟิสิกส์ (ลงทะเบียนล่วงหน้า 2026-10-15)

ผมเขียนไฟล์นี้**ก่อน**เริ่มลูป ลูปห้ามแก้ ถ้าเกณฑ์ข้อใดทำไม่ได้จริง ให้เขียนเหตุผลลงในข้อ deviation ของ `docs/physics_world/03_validation_report.md` แล้วสร้าง `physics-loop/STOP` ห้ามลดเกณฑ์เอง

`physics-loop/tools/verify_physics.py` อ่านผลจาก `data/lithics_validation/results.json` แล้วตัดสินผ่านหรือไม่ผ่านเองด้วยเกณฑ์ในไฟล์นี้ ไม่ใช้ช่อง `pass` ที่ลูปเขียนมา

## หลักการ
1. **เกณฑ์ข้อมูลจริงตรวจแค่ทิศและนัยสำคัญ ไม่ตรวจขนาด** เพราะหินจำลองมีขนาดและมิติต่างจากการทดลองจริง ขนาดของผลให้รายงานไว้ แต่ไม่ใช้ตัดสิน
2. **ห้ามจูนพารามิเตอร์ให้เข้าเป้าตรวจ** พารามิเตอร์ที่ปรับได้มีเพียงตัวที่อยู่ในหัวข้อ `calibration` ของ `spec/materials.json`
3. **ความยาวเชิงตัวเลขทุกตัวต้องคำนวณจากค่าวัสดุตามสูตรที่บันทึกไว้** เช่น ความยาว regularization ของ phase-field หรือรัศมี nonlocal ห้ามเลือกค่าเอง
4. **ค่าสุ่มทุกตัวต้องมาจาก seed ที่ระบุ** ให้ microstructure ใช้ seed 0–29 และการรบกวนตำแหน่งตีใช้ seed 100–129

## รูปแบบของ `results.json`
```json
{
  "lithics_tree": "<git rev-parse HEAD:lithics ตอนรัน>",
  "commit": "<git rev-parse HEAD>",
  "code_dirty": false,
  "suite_minutes": 12.3,
  "criteria": {
    "V1": {"metrics": {...}}, "V2": {...}, ...
  }
}
```
ใน `metrics` ต้องมี key ตามที่ระบุในแต่ละข้อด้านล่างครบทุกตัว จะเพิ่ม key อื่นได้

## เกณฑ์
| ข้อ | สิ่งที่ตรวจ | metrics ที่ต้องมี | ผ่านเมื่อ |
|---|---|---|---|
| **V1** | มุม Hertzian cone ใต้หัวกดทรงกลมบนก้อนแก้วหนา (ใช้ axisymmetric หรือ 3D) ที่ระดับพลังงานตี ≥ 4 ระดับ | `cone_included_angle_deg` (list, 1 ค่าต่อระดับ), `levels` | ทุกค่าอยู่ใน [121, 151] และ max − min ≤ 10 |
| **V2** | แกนหินแก้ว 2D กวาด PD ≥ 4 ค่า × EPA ≥ 3 ค่า × AOB ≥ 3 ค่า แล้ว fit √(พื้นที่สะเก็ด) ~ PD + EPA + AOB ด้วย OLS นับเฉพาะครั้งที่ได้สะเก็ด และใช้นิยาม AOB ตามที่ Dibble ใช้ (บันทึกที่มาใน 03) | `n`, `coef_pd`, `ci_pd`, `coef_epa`, `ci_epa`, `coef_aob`, `ci_aob`, `r2`, `aob_convention_source` | `n` ≥ 60, `ci_pd[0]` > 0, `ci_epa[0]` > 0, `ci_aob[1]` < 0 (ทิศตาม Dibble: AOB มากขึ้น สะเก็ดเล็กลง) |
| **V3** | แรงหรือพลังงานตีขั้นต่ำที่ทำให้ได้สะเก็ด หาด้วย bisection ที่ PD ≥ 8 ค่า | `n`, `spearman_rho`, `p_value` (ความสัมพันธ์ระหว่างมวลหรือพื้นที่สะเก็ดกับพลังงานขั้นต่ำ) | `n` ≥ 8, rho > 0, p < 0.05 |
| **V4** | ความคาดเดาได้ ตีซ้ำ ≥ 30 ครั้งด้วยพารามิเตอร์เดียวกัน รบกวนตำแหน่งตี ±0.5 มม. (seed 100–129) และให้แกรนิตใช้ mosaic ใหม่ทุกครั้ง (seed 0–29) เปรียบเทียบออบซิเดียนกับแกรนิต | `cv_obsidian`, `cv_granite`, `cv_ratio_ci` (bootstrap 95% ของ cv_granite/cv_obsidian), `single_flake_frac_obsidian`, `single_flake_frac_granite` | `cv_ratio_ci[0]` > 1 และ `single_flake_frac_obsidian` > `single_flake_frac_granite` |
| **V5** | วัสดุ 4 ชนิดของ Dibble (แก้ว ออบซิเดียน เชิร์ต บะซอลต์) ภายใต้ชุดการตีเดียวกัน ข้อมูลจริงต่างกันไม่เกิน 5% | `ratio_to_glass` (dict ของ obsidian, chert_flint, basalt คือ ค่าเฉลี่ย √พื้นที่/PD หารด้วยค่าของแก้ว) | ทุกค่าอยู่ใน [0.75, 1.33] |
| **V6** | mesh convergence ของกรณีอ้างอิง 1 กรณี | `rel_dev_area` (dict ความละเอียด → |A−A_ref|/A_ref เทียบกับความละเอียดสูงสุด ≥ 96), `cone_angle_dev_deg` (dict ความละเอียด → ส่วนต่างของมุม) | แต่ละ dict มีความละเอียดที่ต่ำกว่าค่าอ้างอิงอย่างน้อย 2 ค่า (ต้องรวมความละเอียดค่าเริ่มต้นด้วย) ทุกค่าของ `rel_dev_area` ≤ 0.10 และทุกค่าของ `cone_angle_dev_deg` ≤ 5 |
| **V7** | 3D tet ด้วยกรณี PD ≥ 3 × EPA ≥ 2 เทียบทิศกับ 2D | `n_pairs_pd`, `frac_monotone_pd`, `n_pairs_epa`, `frac_monotone_epa`, `bar_rel_error_3d` | `frac_monotone_pd` ≥ 0.8, `frac_monotone_epa` ≥ 0.8, `bar_rel_error_3d` ≤ 0.02 |
| **V8** | ฟิสิกส์การตัด ใช้แบบจำลองจากกลศาสตร์การแตกที่มีแหล่งอ้างอิง และวัสดุเป้าหมายต้องมีค่าคงที่พร้อมแหล่งอ้างอิง | `spearman_force_vs_tip_radius`, `p_value`, `n`, `force_ratio_obsidian_to_granite`, `target_material_sources` | rho > 0, p < 0.05, n ≥ 10, ratio < 1, และ `target_material_sources` ต้องไม่ว่าง |
| **V9** | ความเร็ว | `median_strike_seconds_2d` (ที่ความละเอียดค่าเริ่มต้น), `suite_minutes` | median ≤ 60 และ suite ≤ 240 (แก้ 2026-10-15 ดูหัวข้อการแก้เกณฑ์) |
| **V10** | ความกำหนดแน่นอนและการอนุรักษ์ | `identical_rerun` (bool), `max_mass_conservation_rel_error`, `elements_in_multiple_pieces` | identical = true, error ≤ 1e-9, elements = 0 |
| **V11** | ตรวจเชิงวิเคราะห์ | `bar_rel_error`, `kirsch_scf_rel_error`, `hertz_pmax_rel_error`, `sen_k_rel_error` | ≤ 0.02, ≤ 0.05, ≤ 0.10, ≤ 0.05 ตามลำดับ |

## ข้อกำหนดที่ verify ตรวจเพิ่มเอง (ไม่ได้อ่านจาก results.json)
- `pytest` ต้องผ่านทั้งหมด
- ค่าวัสดุที่ `lithics.materials.load_material(name)` คืนมา ต้องตรงกับ `value` ใน `spec/materials.json` ทุกตัว
- โมดูลฟิสิกส์ `lithics/` ทั้งหมด ยกเว้น `measure*`, `validate*` และ `bench*` ห้าม import โมดูลวัดผล และห้ามมีคำว่า `sharp`, `quality`, `knappab`, `recipe`, `tool_type`
- `results.json` ต้องมาจาก commit ที่ `lithics_tree` ตรงกับ `git rev-parse HEAD:lithics` ปัจจุบัน และ `code_dirty` ต้องเป็น false
- verify จะรัน `python -m lithics.validate --only V10,V11 --out <tmp>` ซ้ำ แล้วเทียบผลกับ results.json ต้องได้ผลเท่าเดิม
- red team ทั้ง Claude และ Codex ต้องให้ `VERDICT: PASS` กับ tree เดียวกัน (ดู `physics-loop/REDTEAM_PROMPT.md`)

## การแก้เกณฑ์หลังลงทะเบียน
### 2026-10-15: V9 (ผู้ใช้อนุมัติ)
- **เดิม:** median ≤ 2.0 วินาทีต่อการตี และ suite ≤ 30 นาที
- **ใหม่:** median ≤ 60 วินาทีต่อการตี 2D และ suite ≤ 240 นาที
- **เหตุผล:** phase-field AT1 ต้องใช้ mesh h ≤ ℓ/4 (แก้ว ℓ = 0.119 มม.) การกดก้อนแก้ว 8 มม. แบบ axisymmetric ใช้ 28 วินาทีที่ h = ℓ/2 และ 129 วินาทีที่ h = ℓ/4 (02 §4.4) เกณฑ์เดิมจึงเป็นไปไม่ได้กับฟิสิกส์ที่ถูกต้อง ความเร็วที่ใช้ในโลกของเอเจนต์จะทำในรอบ 2 (เช่น surrogate ที่ calibrate จาก phase-field)
- **ความซื่อตรง:** แก้ก่อนมีผลของ V1–V8 ใด ๆ และเกณฑ์ V9 ไม่เกี่ยวกับผลทางฟิสิกส์
- **การรัน suite:** รัน `python -m lithics.validate --only <ข้อ>` แยกทีละเกณฑ์ได้ (แต่ละครั้งไม่เกิน 30 นาที เพราะ Bash tool มี timeout 30 นาที) หรือรันหลาย process พร้อมกัน แล้วรวมผลลง `results.json` ได้เฉพาะผลที่มาจาก `lithics_tree` เดียวกันและ `code_dirty: false` ส่วน `suite_minutes` คือผลรวมเวลา CPU-wall ของทุกส่วน

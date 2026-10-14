# สัญญา API ของแพ็กเกจ `lithics` (รอบ 1)

รอบ 2 จะสร้างโลกของเอเจนต์บน API นี้ ลูปรอบ 1 เพิ่มฟังก์ชันได้ แต่ห้ามเปลี่ยนชื่อหรือความหมายของสิ่งที่กำหนดไว้ที่นี่ ถ้าจำเป็นต้องเปลี่ยน ให้บันทึกเป็น deviation

## ที่ verify เรียกใช้โดยตรง
```python
from lithics.materials import load_material, MATERIAL_NAMES
m = load_material("glass_soda_lime")   # dataclass ที่มีฟิลด์ youngs_modulus_pa, poisson_ratio,
                                       # density_kg_m3, fracture_toughness_pa_sqrt_m, tensile_strength_pa,
                                       # microstructure_scale_m  (ค่าตรงกับ spec/materials.json)
```
- `MATERIAL_NAMES` เป็น tuple ของชื่อวัสดุทั้งหมดใน `spec/materials.json`
- `python -m lithics.validate [--only V1,V2,...] --out DIR` เขียน `DIR/results.json` ตามรูปแบบใน `validation_criteria.md`

## API ฟิสิกส์ (รอบ 2 จะใช้)
| ส่วน | สิ่งที่ต้องมี |
|---|---|
| `lithics.stone` | `Stone` คือวัตถุ 2D หรือ 3D ที่ประกอบด้วยเซลล์วัสดุ (รองรับ `dim=2` และ `dim=3` ใน dataclass เดียวกัน) และ `make_core(...)` สำหรับสร้างแกนหินที่มีแท่นตีซึ่งกำหนด EPA และขอบได้ |
| `lithics.impact` | `strike(stone, contact_point_m, direction, hammer_mass_kg, hammer_speed_m_s, hammer_radius_m, support) -> StrikeResult` ใช้พลังงานจลน์ของหินค้อนเป็นอินพุต ไม่ใช่แรงคงที่ `support` รองรับทั้งการถือในมือ (ยึดแบบนุ่ม) และการวางบนหินรอง (passive hammer/bipolar) |
| `StrikeResult` | `pieces` (list ของ `Stone` ใหม่), `fracture_energy_j`, `seconds` และข้อมูลดิบสำหรับวัดผล |
| `lithics.cutting` | `cut(edge_piece, target, ...) -> CutResult` คืนแรงหรือพลังงานที่ต้องใช้ตัด หรือรายงานว่าตัดไม่เข้า ทั้งหมดคำนวณจากรูปทรงขอบจริงของชิ้นหินและค่าวัสดุเป้าหมาย |
| `lithics.measure` | ใช้ฝั่งผู้วิเคราะห์เท่านั้น เช่น มวล พื้นที่ PD EPA มุมขอบ รัศมีปลายขอบ มุมกรวย และจำนวนชิ้น **โลกของเอเจนต์ในรอบ 2 ห้าม import โมดูลนี้** |

## ข้อห้าม
- ห้ามมีตัวแปรหรือฟิลด์ที่บอก "ความคม" "คุณภาพ" หรือ "ความเหมาะกับการกะเทาะ" ในโมดูลฟิสิกส์
- ความต่างระหว่างวัสดุต้องมาจากค่าคงที่ทางกายภาพและ microstructure เท่านั้น

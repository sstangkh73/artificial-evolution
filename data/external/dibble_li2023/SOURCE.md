# ข้อมูลสะเก็ดจากการทดลองควบคุมของ Dibble และคณะ

- **ไฟล์:** `flakes.csv` มี 504 แถว แต่ละแถวคือสะเก็ด 1 ชิ้น ดาวน์โหลดเมื่อ 2026-10-15
- **sha256:** `8bc57deb7d6e68b9d9e11a081e34f3be3fc0159fff81071049720af4666eaf13`
- **แหล่งที่มา:** Supplementary file ESM 3 ของ Li, L., Lin, S. C., McPherron, S. P., Abdolahzadeh, A., Chan, A., Dogandžić, T., Iovita, R., Leader, G. M., Magnani, M., Rezek, Z., & Dibble, H. L. (2023). A Synthesis of the Dibble et al. Controlled Experiments into the Mechanics of Lithic Production. *Journal of Archaeological Method and Theory*, 30, 1284–1325. https://doi.org/10.1007/s10816-022-09586-2
- **URL:** https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs10816-022-09586-2/MediaObjects/10816_2022_9586_MOESM3_ESM.csv

## คอลัมน์ที่ใช้
หน่วยเป็น mm, g และองศา

| คอลัมน์ | ความหมาย |
|---|---|
| `epa` | มุมขอบแท่นตี (exterior platform angle) |
| `platthick` | ความลึกแท่นตี (platform depth, PD) |
| `aob` | มุมของการตี (angle of blow) |
| `fweight` | มวลสะเก็ด |
| `length`, `width`, `thick` | ขนาดสะเก็ด |
| `platwidth` | ความกว้างแท่นตี |
| `termination` | ลักษณะปลายสะเก็ด |
| `coremat` | วัสดุของแกนหิน |
| `coretype` | รูปทรงของแกนหิน |
| `hmat` | วัสดุของค้อน |
| `forceamt` | แรงตี (lbf) |

## การใช้งาน
- ใช้เป็นเป้าตรวจความสมจริงของโลกฟิสิกส์เท่านั้น ดู `docs/physics_world/01_literature.md`
- ห้ามแก้ไฟล์นี้ ถ้าต้องกรองข้อมูล ให้กรองในสคริปต์

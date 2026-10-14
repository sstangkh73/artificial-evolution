# เป้าหมาย: YSC 2027 (29YCSS00443) เฟส 3 — pilot แล้วตรึง protocol ยืนยัน

คำถามวิจัย: เอเจนต์ค้นพบเครื่องมือได้หรือไม่ จากการลองผิดลองถูก โดยไม่มีสูตร ชื่อเครื่องมือ หรือคะแนนประโยชน์ให้ล่วงหน้า
เป้าหมายของเฟสนี้คือเตรียมการทดลองที่ตอบคำถามนี้ได้ด้วยหลักฐานหลายด้าน **ไม่ใช่** การหาผลที่ดูดี

รายการงานและกติกาทั้งหมดอยู่ใน `worklog/2026-10-14-ysc-phase3-loop/plan.md` (ขั้น 1 เสร็จแล้ว เหลือขั้น 2–7)
ข้อมูลประกอบ:
- `worklog/2026-10-14-ysc-review/report.md` — ผลตรวจ 5 ประเด็นที่ต้องแก้
- `docs/ysc2027_tool_discovery/` — แผนเร่ง, information-access map, การออกแบบสนามทดลอง
- โค้ด: `simulation/tool_discovery.py`, `simulation/tool_discovery_metrics.py`, `scripts/run_tool_discovery.py`

ผู้ใช้ตัดสินแล้ว:
- เอเจนต์เป็นอมตะ (`immortal=True`) ใน pilot และรันยืนยัน
- เลือกค่าต่าง ๆ ตามกฎที่เขียนไว้ใน pilot protocol ก่อนรัน
- หยุดเมื่อตรึง protocol ยืนยันแล้ว **ห้ามรัน seeds 5000+**

**เสร็จเมื่อ:** `ysc-loop/verify.ps1` ผ่าน (ดูรายการตรวจทั้งหมดใน `ysc-loop/tools/verify_phase3.py`)

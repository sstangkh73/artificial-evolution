# physics-loop: ลูปสร้างฟิสิกส์การกะเทาะหิน (Claude + Codex)

แบ่งเป็น 2 รอบตามที่ผู้ใช้กำหนด
1. **รอบ 1 (ลูปนี้):** สร้างฟิสิกส์ใน `lithics/` ให้ครบ ผ่านเกณฑ์ V1–V11 แล้วผ่าน red team ทั้งของ Claude และ Codex
2. **รอบ 2:** สร้างโลกของเอเจนต์ ยังไม่ได้เตรียม จะเริ่มหลังผู้ใช้ตรวจผลรอบ 1

## วิธีรัน
```
pwsh -File physics-loop/run-loop.ps1 -MaxIterations 40 -MaxHours 16
```

## ส่วนประกอบ
- **ใครนำ:** แต่ละรอบ `tools/budget.py` เทียบโทเค็นที่เหลือตาม `budget.json` ตัวที่เหลือมากกว่าเป็นคนทำงานหลัก อีกตัวรีวิว
- **ตัวตัดสิน:** `verify.ps1` เรียก `tools/verify_physics.py` ซึ่งตัดสินผ่านหรือไม่ผ่านด้วยเกณฑ์ของตัวเองจาก `spec/validation_criteria.md` ไม่เชื่อช่อง pass ที่ AI เขียนมา และตรวจเพิ่มอีกหลายอย่าง:
  - pytest ทั้ง repo
  - ค่าวัสดุตรงกับ spec
  - คำต้องห้ามในโมดูลฟิสิกส์
  - ผล validate มาจาก tree ที่ commit แล้ว
  - รัน V10 และ V11 ซ้ำแล้วได้ผลเท่าเดิม
- **red team:** เมื่อผ่านทางเทคนิค (verify exit 3) สคริปต์จะเรียก Claude แบบ context ใหม่และ Codex ด้วย `REDTEAM_PROMPT.md` แล้วบันทึกผลที่ `redteam/<key>-<ใคร>.md`
  - key ผูกกับ tree ของ `lithics/`, เทสต์, ผล validate และเอกสาร
  - AI ห้ามแตะโฟลเดอร์นี้ ถ้าแตะลูปจะหยุด
  - ถ้า red team แก้ไฟล์ สคริปต์จะย้อนกลับให้
- **ข้อมูลที่เตรียมไว้:** `spec/materials.json` (ค่าวัสดุ 5 ชนิดพร้อมแหล่งอ้างอิง), `spec/api.md` และ `data/external/dibble_li2023/`
- **commit:** เฉพาะ path ของงานนี้ และไม่ push
- **หยุด:** สร้าง `physics-loop/STOP` หรือกด Ctrl+C
- **ดูความคืบหน้า:** `progress.md`, `worklog/2026-10-15-physics-loop-r1/plan.md`, `.loop/last-verify.txt` และ `redteam/`

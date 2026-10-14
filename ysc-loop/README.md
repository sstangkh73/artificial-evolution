# ysc-loop: ลูปทำงาน YSC เฟส 3 (Claude + Codex)

ดัดแปลงจาก `auto-loop/` ลูปจะทำงานที่ root ของ repo ไปจนกว่า `verify.ps1` จะผ่าน (คือตรึง protocol รันยืนยันได้แล้ว) แล้วหยุด

```
pwsh -File ysc-loop/run-loop.ps1 -MaxIterations 20 -MaxHours 6
```

- **ใครนำ:** แต่ละรอบ `tools/budget.py` เทียบโทเค็นที่เหลือตาม `budget.json` ตัวที่เหลือมากกว่าเป็นคนทำงานหลัก อีกตัวรีวิว
  และใครเจอบั๊กของอีกตัวต้องแก้หรือตีกลับ (บันทึกใน `progress.md` ส่วน Review log)
- **โทเค็น:** `.loop/usage.csv` (Claude นับ input + output + cache-creation, Codex นับจากบรรทัด "tokens used") แก้เพดานได้ที่ `budget.json` ก่อนเริ่ม
- **ตัวตัดสิน:** `tools/verify_phase3.py` ตรวจหลักฐานจริง ได้แก่ เทสต์ผ่าน, ค่าเริ่มต้นยังให้ผล smoke เดิม, pilot ครบและรันจากโค้ดที่ commit แล้ว,
  ใช้แค่ seeds 1000–1099, pilot protocol ถูก commit ก่อนรัน pilot, ไม่มีการใช้ seeds 5000+, และ config รันยืนยันถูกตรึงพร้อม sha256
- **commit:** เฉพาะ path ของงานนี้ (ไม่ใช้ `git add -A` เพราะ repo มีไฟล์ข้อมูลที่ยังไม่ track อยู่มาก) และไม่ push
- **ไฟล์ที่ห้ามแก้:** ไฟล์ตั้งค่าของลูป, `tools/`, `world/`, `agents/`, เทสต์เดิม, ข้อมูล smoke ถ้าถูกแก้ ลูปจะหยุด
- **หยุด:** สร้างไฟล์ `ysc-loop/STOP` หรือกด Ctrl+C (AI จะสร้าง STOP เองถ้าเจอเงื่อนไขหยุดใน plan.md)
- **ดูความคืบหน้า:** `ysc-loop/progress.md`, `worklog/2026-10-14-ysc-phase3-loop/plan.md`, `git log --oneline`, `ysc-loop/.loop/last-verify.txt`

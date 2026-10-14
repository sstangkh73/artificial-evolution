# Report: YSC 2027 — แผนเร่ง + เฟส 0–2 (สนามทดลองค้นพบเครื่องมือ)
Date: 2026-10-14   Status: Done

## Summary
ทำแผนเร่งที่ยังครบทุกเฟสของข้อเสนอ โดยกำหนดส่งรายงานความก้าวหน้าภายใน 25 ธ.ค. (เผื่อ 3 วันก่อนเส้นตาย 28 ธ.ค.)
เฟส 0 (information-access map) และเฟส 1–2 (โลกที่ไม่มีสูตร, learner C0–C4, telemetry) เสร็จแล้ว เทสต์ใหม่ 28 ข้อผ่าน เทสต์ทั้ง repo 196 ข้อผ่าน
รัน smoke 25 รัน (5 seeds × 5 เงื่อนไข) ใช้เวลารวม 18 วินาที แปลว่าการรันยืนยัน 150 รันจะใช้เวลาไม่ถึง 2 นาที

## What was done
- `docs/ysc2027_tool_discovery/00_แผนเร่ง.md` — แผน 7 ช่วงจาก 14 ต.ค. ถึงรอบชิง
- `docs/ysc2027_tool_discovery/01_information_access_map.md` — เฟส 0: ระบบเดิมเท่ากับ C3 เพราะเอเจนต์เรียก `score_object_for_action` 3 จุด
- `docs/ysc2027_tool_discovery/02_สนามทดลอง_เฟส1-2.md` — การออกแบบ ผล smoke และปัญหาที่ pilot ต้องตัดสิน
- `simulation/tool_discovery.py` — สนามทดลอง ใช้ `Environment` เดิมเป็นฟิสิกส์ของโลก **ไม่ได้แก้ `world/` หรือ `agents/`**
- `simulation/tool_discovery_metrics.py` — ตัวชี้วัดระดับรัน, ระดับ A/B, reuse/rebuild, robustness ของ bin width
- `scripts/run_tool_discovery.py` — รัน batch แบบ paired seeds, ไม่เขียนทับ, มี `--resume`, เขียน protocol.json, manifest และ SHA-256
- `tests/test_tool_discovery.py` — เทสต์ 28 ข้อ
- `data/tool_discovery_smoke_20261014/` — ผล smoke (commit เฉพาะ summary/protocol/manifest ส่วน `runs/` ถูก ignore)
- `.gitignore` — เพิ่ม `data/tool_discovery_smoke_*/runs/`

## Verification
- `python -m pytest tests/test_tool_discovery.py -q` → 28 passed
- `python -m pytest tests -q` → 196 passed in 15.49s
- guard เรื่องการรั่วของข้อมูล: C0/C1/C2/C4 ผ่าน และเทสต์ควบคุมยืนยันว่า guard จับ C3 ได้จริง (guard ไม่ได้ผ่านทุกอย่างแบบไร้ผล)
- seed เดียวกันรันซ้ำได้ events และ ledger ตรงกันทุกตัว (เทียบด้วย JSON)
- ป้องกันการเขียนทับ: รันซ้ำไปที่ output เดิมแล้วถูกปฏิเสธพร้อมข้อความ "refusing to overwrite"

## Problems / not done
- ค่าพารามิเตอร์ปัจจุบัน (drain 0.3, เกณฑ์ 12/14/10, ε 0.1, q_init 0) ได้จากการลองแบบหยาบ 3–4 ชุดบน seeds 0–7
  **ดังนั้น seeds 0–7 ถูกใช้ไปแล้ว** และไม่ควรใช้เป็น seeds ยืนยัน แผนจึงเปลี่ยนให้การรันยืนยันใช้ seeds ชุดใหม่ (ดูข้อ Next steps)
- พบปัญหาที่ต้องแก้ใน pilot 3 ข้อ (รายละเอียดใน `02_สนามทดลอง_เฟส1-2.md` หัวข้อ 6):
  survivor bias ในตัวชี้วัดหลัก, ระดับ A หลวมจนผ่านทุกเงื่อนไข, และ learner ใช้เครื่องมือน้อยกว่า oracle มาก
- ยังไม่ได้ทำการวิเคราะห์สถิติ (Wilcoxon, bootstrap, KM) ซึ่งเป็นงานของเฟส 4
- ไฟล์ `agents/.skills/engineering/SKILL.md` ที่ AGENTS.md สั่งให้อ่านไม่มีอยู่แล้ว

## Next steps
1. แก้แผนเรื่อง seed: seeds 0–99 ถูกใช้ใน smoke/calibration แล้ว ให้ pilot ใช้ 1000–1099 และการรันยืนยันใช้ seeds ชุดใหม่ที่ประกาศใน protocol (เช่น 5000–5029)
2. เฟส 3: เขียน pilot protocol (คำถาม 3 ข้อในหัวข้อ 6) แล้วรัน pilot
3. หาวันจัดค่ายและวันรอบชิงภาคใต้

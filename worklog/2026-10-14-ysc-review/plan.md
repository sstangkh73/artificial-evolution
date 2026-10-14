# Plan: ตรวจสอบงาน YSC (commit 18afb12, เฟส 0–2)
Date: 2026-10-14

## Goal
ตรวจแบบ scrutinize ว่าสนามทดลอง tool discovery (เฟส 0–2) ถูกต้อง ไม่รั่วข้อมูล oracle และพร้อมเข้าเฟส 3 (pilot)

## Steps
1. อ่าน docs/ysc2027_tool_discovery/* และเทียบกับข้อเสนอโครงการ
2. อ่านโค้ด simulation/tool_discovery.py, tool_discovery_metrics.py, scripts/run_tool_discovery.py, tests
3. รันเทสต์ + smoke ซ้ำ ตรวจ reproducibility
4. หาบั๊ก/ช่องโหว่ทางวิทยาศาสตร์ (leakage, metric bias, seed hygiene)
5. เขียน report.md

## Notes
- agents/.skills/engineering/SKILL.md ไม่มีอยู่ → ใช้หลัก review ทั่วไป

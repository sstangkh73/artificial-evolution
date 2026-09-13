# บันทึก clean-worktree smoke ก่อนตรึง preregistration

วันที่ตรวจ: 2026-09-14  
สถานะ: **ผ่าน gate ด้านการทำงานของ pipeline; ผลเชิงตัวเลขเป็น exploratory และห้ามใช้เป็นหลักฐานยืนยัน**

## ขอบเขต

- source commit ของรอบ final: `11d69c8` (`Enforce frozen-spec analysis eligibility`)
- detached clean worktree: `C:\artificial-evolution-prereg-smoke-20260914`
- E6 smoke: seed `20260968`, 200 ticks, 15 arms
- T2-RB smoke: seed `20260969`, 200 ticks, 3 arms
- seed ทั้งสองไม่อยู่ในชุด confirmatory
- ไม่ใช้ `--allow-dirty`, `--allow-draft` หรือ `--resume`

## ผล gate

| รายการ | ผล |
|---|---|
| E6 grid | 15/15 runs, 0 failures |
| T2-RB grid | 3/3 runs, 0 failures |
| revision ระหว่าง run | start = end = `11d69c8...`; ไม่เปลี่ยน |
| tracked tree ระหว่าง run | clean ทั้ง start และ end |
| requested horizon | ทุก arm จบที่ tick 200; ไม่มี early stop |
| E6 realized fruit energy | V04=4, V05=5, V06=6, V08=8, V10=10 |
| E6 encounter telemetry | fruit ต่ำสุด 2,906 และ plant ต่ำสุด 1,169 ต่อ arm |
| E6 `type_age` keys | `raw_fruit@0` ถึง `raw_fruit@8` ครบทุกระดับพลังงาน |
| E6 `type_sham` keys | `raw_fruit@0` ถึง `raw_fruit@8` ครบทุกระดับพลังงาน |
| T2-RB encounter telemetry | fruit 1,230–1,330 ต่อ arm |
| batch validator | E6 `VALID` 15/15; T2-RB `VALID` 3/3 |
| full unit tests | 140/140 ผ่าน |

`age` ใน toxin profile และ `type_age` คือ **อายุของชิ้นอาหาร** (`current tick - created_tick`) ไม่ใช่อายุ agent. Smoke ยืนยันว่า B2 เรียนรู้แยกครบ 9 resource-age bins และ B3 มี capacity 9 bins เช่นกันโดย index ไม่ได้มาจากอายุจริง

## การทดสอบ guard ป้องกันการใช้ smoke ผิดประเภท

analyzer อ่าน batch ทั้งสองได้และสร้าง paired contrast ได้ แต่คืนค่า:

- `frozen_confirmatory_spec = false`
- `confirmatory_provenance_eligible = false`

เพราะ embedded spec มีสถานะ `EXPLORATORY_SMOKE_ONLY_NOT_CONFIRMATORY` แทน `PREREGISTERED_CONFIRMATORY_FROZEN` จึงไม่สามารถนำ smoke ไปผ่าน confirmatory pipeline โดยไม่แก้สถานะและ rerun จาก frozen tag

ตัวเลขจาก seed เดียวที่เกิดระหว่างการตรวจ pipeline ได้แก่ E6 slope `1.915345` tick ต่อหน่วยพลังงาน และ T2-RB A2-A3R `-15.64` tick ตัวเลขนี้ไม่มี CI ที่คำนวณได้จากหลาย seed และ **ห้ามใช้เลือกสมมติฐาน เปลี่ยนสเปก หรือเขียนเป็นผลวิจัย**

## ข้อสังเกตที่ไม่ใช่ failure

ใน T2-RB smoke ระยะ 200 ticks แขน A3O และ A3R ให้ outcome เท่ากันใน seed นี้ ความต่าง potency ของสองแขนมีขนาดเล็กและ smoke ไม่ได้ออกแบบมาเพื่อประเมิน effect; ชุด confirmatory 50 seeds ที่ 400 ticks จะคงทั้ง original control และ recalibrated control ตามที่ตรึงไว้

## คำตัดสิน

รอบแรกจาก `8b9233e` ทำให้พบว่า analyzer ยังไม่ได้ตรวจสถานะ preregistration จึงเพิ่ม frozen-status guard และไม่นำรอบนั้นไปเป็น final smoke gate จากนั้นรันใหม่ทั้งหมดจาก `11d69c8` โดยไม่ใช้ผลเดิม ผลรอบ final เหมือนเดิมแบบ deterministic และผ่าน execution, telemetry, realized parameters, analysis routing และ provenance จึงอนุญาตให้เข้าสู่ final preregistration freeze

# รายงานก่อนทำ: Signal Channel Foundation สำหรับเส้นทาง YSC -> ISEF

**วันที่:** 2026-06-27  
**สถานะ:** Before implementation report  
**อ้างอิงแผน:** `reports/ysc_to_isef_roadmap_2026-06-27.th.md`  
**เป้าหมายเฟส:** Phase 2 - เพิ่มฐานการทดลอง communication/signal บน neural + neuroevolution

---

## 1. สรุปก่อนลงมือ

แผน YSC -> ISEF ระบุว่า gap สำคัญหลัง Phase 1 คือการทำ contribution ให้คมขึ้นด้วยกรอบ "การเรียนรู้ 2 ระดับเวลา" และเพิ่มการศึกษาการสื่อสารบน neural agents โดยต้องมี signal output, signal input, และ control เช่น signal-shuffle / receiver-blind

สถานะปัจจุบันของ repo:

- มี neural brain และ neuroevolution แล้ว
- มี pilot เรื่อง social transmission จาก food-value telemetry แล้ว
- pilot พบหลักฐานสนับสนุน individual learning มากกว่า social transmission
- ยังไม่มี explicit signal channel ให้ neural agents ส่ง/รับสัญญาณ

ดังนั้นงานรอบนี้จะไม่พยายาม claim ว่า "เกิด communication แล้ว" แต่จะเพิ่ม infrastructure ที่จำเป็นเพื่อให้ทดลอง communication ได้จริงในรอบถัดไป

---

## 2. Research Question

คำถามเชิงวิศวกรรม:

> จะเพิ่มช่องสัญญาณให้ neural agents ส่ง signal และรับ signal จาก agent รอบข้างได้อย่าง reproducible, opt-in, และไม่กระทบ classic controller เดิมได้หรือไม่

คำถามเชิงวิทยาศาสตร์ที่งานนี้เปิดทางให้ทดสอบภายหลัง:

> ถ้า neural agents มี signal channel แล้ว selection จะทำให้ signal มีผลต่อพฤติกรรม/fitness เกินกว่า cue ทางสิ่งแวดล้อมหรือไม่

---

## 3. Hypotheses

### H0: Infrastructure-only

การเพิ่ม signal channel ยังไม่ควรสร้าง claim เรื่อง communication โดยตัวเอง แต่ควรเพิ่มช่องข้อมูลที่วัดและควบคุมได้

หลักฐานที่ต้องการ:

- neural brain มี signal output head
- agent observation มี signal input channel
- environment เก็บ signal แบบเป็น buffer เพื่อให้ receiver อ่าน signal จาก tick ก่อนหน้า ลด order artifact จากลำดับการ tick
- default classic path ยังไม่เปลี่ยน

### H1: Backward Compatibility Risk

การเพิ่ม output/input ใหม่อาจทำให้ saved genome/spec เดิมพัง

หลักฐานที่ต้องการเพื่อลด risk:

- `spec_from_dict()` อ่าน saved spec เดิมที่ไม่มี `signal_outputs` ได้
- old 3-channel vision spec ยังสร้าง observation ขนาดเดิมได้
- unit tests ตรวจ shape และ legacy round-trip

---

## 4. ขอบเขตการแก้ไข

### ทำในรอบนี้

1. เพิ่ม signal head ใน `agents/neural_brain.py`
2. เพิ่ม signal input channel ใน neural observation ของ `Agent`
3. เพิ่ม signal buffer/methods ใน `Environment`
4. ทำให้ signal อ่านจาก previous tick เพื่อหลีกเลี่ยง receiver เห็นเฉพาะ agent ที่ tick ก่อนหน้าใน tick เดียวกัน
5. เพิ่ม unit tests สำหรับ shape, backward compatibility, signal buffer, และ observation channel
6. อัปเดต roadmap ให้บอกสถานะจริงว่า "foundation พร้อม" แต่ยังไม่ใช่ผล communication

### ยังไม่ทำในรอบนี้

1. ยังไม่รัน neuroevolution communication experiment
2. ยังไม่ทำ signal-shuffle / receiver-blind condition แบบเต็มชุด
3. ยังไม่ทำสถิติ multi-seed ของ communication
4. ยังไม่ claim ว่ามี language, symbol, social learning, หรือ communication emergent แล้ว

---

## 5. Variables สำหรับงาน implementation

### Independent Variables

- `neural_signal_enabled`
- `neural_signal_radius`
- `NeuralBrainSpec.vision_channels`
- `NeuralBrainSpec.signal_outputs`

### Dependent Variables

- genome size
- forward output shape
- decision output shape
- signal visibility in observation
- compatibility with saved legacy specs

### Control Variables

- classic controller path
- old neural spec with 3 vision channels and no signal head
- deterministic seeded neural operations

---

## 6. Success Criteria

ถือว่าสำเร็จถ้า:

1. unit tests ทั้งหมดผ่าน
2. `python -m compileall agents world tests scripts` ผ่าน
3. default classic environment ไม่ต้องเปิด signal และไม่เปลี่ยน behavior path โดยตั้งใจ
4. legacy neural spec เดิมที่ไม่มี `signal_outputs` ยังโหลดได้
5. neural observation มี signal channel เมื่อ spec ขอ `vision_channels >= 4`
6. signal ที่ emit ใน tick หนึ่งถูกอ่านได้จาก previous buffer ใน tick ถัดไป

---

## 7. Failure Criteria

ต้องหยุด/ปรับถ้า:

1. tests เดิมพังโดยไม่มีเหตุผลทาง contract ที่ตั้งใจ
2. saved genome เดิมโหลดไม่ได้
3. signal visibility ขึ้นกับลำดับ agent tick ใน tick เดียวกันโดยตรง
4. classic controller path ต้องจ่าย cost หรือเปลี่ยน RNG stream อย่างมีนัยสำคัญ

---

## 8. ความเสี่ยง

| ความเสี่ยง | ผลกระทบ | แผนลดความเสี่ยง |
| --- | --- | --- |
| genome size เปลี่ยน | saved genome เดิมใช้ไม่ได้ | legacy `spec_from_dict()` default `signal_outputs=0` |
| vision channel mismatch | neural decision fail ด้วย ValueError | observation เติม channel ตาม `spec.vision_channels` |
| order artifact | signal ดูเหมือนมีผลเพราะลำดับ tick | ใช้ previous/current buffer |
| claim เกินหลักฐาน | เสียความน่าเชื่อถือระดับ YSC/ISEF | รายงานหลังทำต้องเขียนข้อจำกัดชัด |

---

## 9. Expected Output

หลังทำควรได้:

- code ที่รองรับ signal channel
- tests ใหม่
- after report ภาษาไทย
- roadmap note ว่า Phase 2 communication ยังอยู่ขั้น foundation ไม่ใช่ผลวิทยาศาสตร์สุดท้าย

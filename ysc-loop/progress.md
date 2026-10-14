# Progress

ความจำของ Claude และ Codex ระหว่างรอบ ให้เขียนต่อท้ายส่วน Log ทุกรอบ

## Log
- รอบ 0 (ตั้งค่า, Claude แบบ interactive 14 ต.ค.): ขั้น 1 โหมดอมตะเสร็จแล้ว (commit febc45b) งานถัดไปคือขั้น 2 แก้ตัวชี้วัด
- รอบ 1 (14 ต.ค., LEAD=claude, Codex รีวิว): ขั้น 2 เสร็จ — ตัวชี้วัดระดับ A แบบอัตรา, `reuse_delta`, `level_b_run`, สคริปต์ระดับ B แบบจับคู่ seed + เทสต์ 6 ข้อ; pytest 204 passed; verify: เทสต์และ smoke ผ่าน ส่วนที่ล้มเป็นขั้น 3–7 ที่ยังไม่ทำ (ตามคาด) ปัญหา: `agents/.skills/engineering/SKILL.md` ไม่มีในเครื่อง (มีแค่ management-talk) จึงทำต่อโดยไม่มี skill นั้น งานถัดไป: ขั้น 3 ความเรียบร้อยของ runner

## Review log
(ใครพบปัญหาอะไรในงานของใคร และแก้อย่างไร)
- รอบ 1, Codex รีวิวงาน Claude (ขั้น 2):
  - ยอมรับ/แก้: `first_discovery_tick=None` แปลว่า "ไม่ค้นพบ" ไม่ใช่ข้อมูลหาย → censored ที่ `ticks` แทนการตัดทิ้ง + เทสต์
  - ยอมรับ/แก้: สคริปต์อาจจับคู่ข้าม grid cell → `load_runs` ปฏิเสธโฟลเดอร์ที่ config ต่างกันหรือ (condition, seed) ซ้ำ + เทสต์
  - เลื่อนไปขั้น 4: ไม่มี primary endpoint/แผน multiple comparisons — เป็นเรื่องของ protocol ไม่ใช่สคริปต์ (สคริปต์เป็นเชิงพรรณนา ระบุใน docstring)
  - เลื่อนไปขั้น 4: `level_b_run` ผ่านได้แม้ `reuse_after_bad=None` — คงไว้เพราะเป็นแค่ตัวคัดกรองรายรัน ระดับ B จริงใช้การเทียบจับคู่
  - ไม่แก้: metric ใช้ `net` จริงและ baseline ทั้งรัน — เป็นการวัดฝั่งผู้วิเคราะห์ เอเจนต์ไม่ได้เห็น จึงไม่ใช่ oracle รั่วเข้าเอเจนต์ จะระบุใน protocol
  - ไม่แก้: ข้อมูล smoke เดิมใช้ key `level_b` — ห้ามแก้ `data/tool_discovery_smoke_20261014/`
  - ไม่ใช่บั๊ก: เทสต์ `tmp_path` error ในฝั่ง Codex เป็นเรื่องสิทธิ์ sandbox ฝั่งเครื่องจริงผ่านครบ

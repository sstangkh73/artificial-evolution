# รายงานหลังทำ: Signal Channel Foundation สำหรับเส้นทาง YSC -> ISEF

**วันที่:** 2026-06-27  
**สถานะ:** After implementation report  
**Before report:** `reports/ysc_to_isef_signal_channel_foundation_2026-06-27.before.th.md`  
**อ้างอิงแผน:** `reports/ysc_to_isef_roadmap_2026-06-27.th.md`

---

## Abstract

เพิ่มฐาน `signal channel` สำหรับ neural/neuroevolution agents แล้ว โดย neural brain รุ่นใหม่มี signal output head เพิ่มจาก move/action head และ agent observation มี signal input channel เมื่อ spec ใช้ `vision_channels >= 4` ส่วน environment เก็บ signal แบบ `current`/`previous` buffer เพื่อให้ receiver อ่าน signal จาก tick ก่อนหน้า ลดปัญหา order artifact จากลำดับการ tick ของ agent ใน tick เดียวกัน

งานนี้เป็น infrastructure สำหรับ Phase 2 ของแผน YSC -> ISEF ยังไม่ใช่ผลทดลองว่าเกิด communication แล้ว แต่ทำให้ขั้นต่อไปสามารถรัน communication experiment พร้อม receiver-blind และ signal-shuffle controls ได้จริง

---

## 1. What Changed

### 1.1 Neural Brain

ไฟล์: `agents/neural_brain.py`

- เพิ่ม `SIGNAL_ACTIONS = (quiet, positive, negative)`
- เพิ่ม `NeuralBrainSpec.signal_outputs`
- เปลี่ยน default `vision_channels` จาก 3 เป็น 4 สำหรับ spec ใหม่
- เพิ่ม signal head ใน genome architecture
- `forward()` คืนค่า `(move_logits, action_logits, signal_logits)`
- `decide()` คืนค่า `(move_index, action_index, signal_index)`
- `spec_to_dict()` บันทึก `signal_outputs`
- `spec_from_dict()` รองรับ saved spec เก่าที่ไม่มี `signal_outputs` โดยตั้งเป็น `0`

ผลสำคัญ:

- neural run ใหม่มีช่องส่ง signal
- saved genome เดิมยังโหลดได้โดยไม่เปลี่ยน genome length

### 1.2 Environment Signal Buffer

ไฟล์: `world/environment.py`

- เพิ่ม opt-in flags:
  - `neural_signal_enabled`
  - `neural_signal_radius`
  - `neural_signal_receiver_blind`
  - `neural_signal_shuffle_enabled`
- เพิ่ม buffer:
  - `neural_signal_current`
  - `neural_signal_previous`
- เพิ่ม `emit_agent_signal()`
- เพิ่ม `agent_signal_at()`
- เพิ่ม deterministic signal shuffle hook โดย rotate signal values ระหว่าง emitters
- rotate buffer ใน `Environment.step()`: current ของ tick ก่อนหน้ากลายเป็น previous ให้ receiver อ่านใน tick ถัดไป

ผลสำคัญ:

- receiver ทุกตัวเห็น signal จาก tick ก่อนหน้าเหมือนกัน
- สามารถปิดการรับ signal ด้วย receiver-blind
- สามารถ shuffle signal values เพื่อ control ความสัมพันธ์ sender-signal-position ได้

### 1.3 Agent Wiring

ไฟล์: `agents/agent.py`

- เพิ่ม `neural_signal_value`
- neural observation เติม signal channel เฉพาะเมื่อ `spec.vision_channels >= 4`
- legacy 3-channel spec ยังสร้าง observation ขนาดเดิม
- neural decision emit signal ตาม signal head หลัง movement
- action head เดิมยังควบคุม `none/eat/pick_seed/drop_seed`

ผลสำคัญ:

- signal output และ signal input ต่อเข้ากับ embodied agent จริงแล้ว
- classic controller path ยังไม่ใช้ signal

### 1.4 Tests

ไฟล์:

- `tests/test_neural_brain.py`
- `tests/test_neural_signal_channel.py`

เพิ่ม/ปรับ tests สำหรับ:

- genome size ใหม่ที่มี signal head
- forward/decide output shape ใหม่
- legacy saved spec ที่ไม่มี `signal_outputs`
- previous-tick signal visibility
- receiver-blind control
- signal-shuffle hook
- agent observation signal channel
- neural decision emit signal head choice

---

## 2. Validation

### Targeted Tests

```text
python -m unittest tests.test_neural_brain
Ran 14 tests in 0.012s
OK
```

```text
python -m unittest tests.test_neural_signal_channel
Ran 6 tests in 0.016s
OK
```

### Full Test Suite

```text
python -m unittest discover -s tests
Ran 54 tests in 0.452s
OK
```

### Compile Check

```text
python -m compileall agents world tests scripts
OK
```

### Integration Smoke

```text
python scripts\run_neuroevolution.py --generations 2 --pop 4 --ticks 10 --world 10 --seed 123 --eval-seeds 1 --max-food 20 --food-spawn 2
```

ผล: run จบโดยไม่ error แต่เป็น smoke ขนาดเล็กมาก จึงไม่ตีความเป็นผลวิทยาศาสตร์

### Legacy Genome Check

โหลด `data/neuroevolution_best_2026-06-27.json` แล้วได้:

```text
vision_channels = 3
signal_outputs = 0
genome_size = 1281
saved_genome_len = 1281
```

ผล: saved genome เดิมยังเข้ากับ spec เดิม ไม่โดนบังคับใช้ signal head ใหม่

---

## 3. Success Criteria Check

| criteria | status | evidence |
| --- | --- | --- |
| unit tests ผ่าน | passed | 54 tests OK |
| compile ผ่าน | passed | compileall OK |
| classic path ไม่ต้องเปิด signal | passed | signal flags default off |
| legacy neural spec โหลดได้ | passed | old genome size 1281 ตรงกัน |
| observation มี signal เมื่อ spec ขอ 4 channels | passed | `test_new_spec_observation_includes_signal_channel` |
| signal อ่านจาก previous tick | passed | `test_signal_is_previous_tick_visible` |
| receiver-blind hook มี | passed | `test_receiver_blind_blocks_signal_input` |
| signal-shuffle hook มี | passed | `test_shuffle_rotates_signal_values_across_emitters` |

---

## 4. Hypothesis Testing

### H0: Infrastructure-only

**Evidence supporting:**

- signal head/input/buffer ถูก implement แล้ว
- tests แยก mechanism ผ่าน
- smoke neuroevolution run ไม่ crash
- ไม่มีการ claim ผล communication

**Evidence against:**

- ยังไม่มี

**Confidence:** สูง ว่า foundation ทำงานตาม contract

### H1: Backward Compatibility Risk

**Evidence supporting risk:**

- genome architecture ใหม่เปลี่ยน default genome size จริง

**Evidence against risk:**

- legacy spec ที่ไม่มี `signal_outputs` โหลดเป็น `signal_outputs=0`
- saved genome เดิม length ตรงกับ genome size
- old 3-channel observation path ยังผ่าน test

**Confidence:** กลางถึงสูง ว่า saved genome เดิมไม่พังใน path ที่ตรวจแล้ว

---

## 5. Scientific Interpretation

สิ่งที่พูดได้ตอนนี้:

> ระบบ neural/neuroevolution มี signal channel foundation ที่ reproducible และมี hooks สำหรับ controls แล้ว

สิ่งที่ยังห้ามพูด:

- ห้ามพูดว่าเกิด communication แล้ว
- ห้ามพูดว่า signal มี semantic meaning แล้ว
- ห้ามพูดว่า social learning ชนะ individual learning แล้ว
- ห้ามพูดว่าเป็น language หรือ symbolic communication

เหตุผล: ยังไม่ได้รัน multi-seed communication experiment และยังไม่มี effect size, CI, receiver-blind comparison, signal-shuffle comparison หรือ fitness-delta analysis

---

## 6. Remaining Work

ขั้นถัดไปเพื่อให้ถึงระดับ YSC/ISEF:

1. เขียน pre-experiment protocol สำหรับ neural communication study
2. เพิ่ม experiment driver ที่รัน conditions อย่างน้อย:
   - normal signal
   - receiver-blind
   - signal-shuffle
   - no-signal legacy/spec control
3. รัน pilot 5 seeds ก่อน แล้วค่อย confirmatory 20-30 seeds
4. เก็บ metrics:
   - signal emission rate
   - receiver action-change after signal exposure
   - food gathered / fitness delta
   - survival or task success
   - effect size เทียบ controls
5. ทำ figure พร้อม CI/error bars
6. เขียน section "Communication Signal Control" ในรายงานภาษาอังกฤษ

---

## 7. Bottom Line

งานนี้ขยับ roadmap จาก "ยังไม่มี signal channel" เป็น "มี signal channel foundation พร้อมทดลอง" แล้ว จุดนี้ช่วยให้ Phase 2 ไม่ค้างอยู่แค่แนวคิด และทำให้คำถาม H2 เรื่อง communication เริ่มกลายเป็นการทดลองที่ falsify ได้จริง

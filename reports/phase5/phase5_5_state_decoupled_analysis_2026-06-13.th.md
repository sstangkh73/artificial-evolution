# รายงานวิเคราะห์หลังทดลอง Phase 5.5: State-Decoupled Seed Handling

วันที่เริ่มรัน: 2026-06-13
วันที่ผลลัพธ์เสร็จ: 2026-06-14 ประมาณ 00:00 Asia/Bangkok
ชุดข้อมูล: `data/phase5_5_state_decoupled_confirm01_20260613`
รายงานอัตโนมัติ: `reports/phase5_5_state_decoupled_confirm01_2026-06-13.th.md`
โปรโตคอลก่อนรัน: `reports/phase5_5_state_decoupled_protocol_2026-06-13.th.md`

## Abstract

Phase 5.5 ทดสอบว่า seed handling ของ agent แยกออกจากภาวะหิววิกฤตได้หรือไม่ โดยไม่สอน agent ว่าเมล็ดคือสิ่งที่ต้องปลูกหรือควรวางที่ไหน ผลจริงคือยังไม่ผ่าน gate: ทุก condition ได้ `phase5_5_passing_runs = 0/5` และ `phase5_5_direction_consistent_runs = 0` อย่างไรก็ตามผลทดลองให้หลักฐานสำคัญว่า bottleneck หลักไม่ใช่ reward memory แต่เป็น action timing ของ seed drop ที่เดิมเกิดตอน `critical_hunger` เกือบทั้งหมด เมื่อบล็อก critical hunger หรือบังคับ safe-window drop แล้ว context สะอาดขึ้นทันที แต่ activity collapse เหลือเฉลี่ย 14-15 drops ต่อ run ทำให้ไม่มี sample พอและไม่มี chain signal

## Research Question

agent เริ่มแสดงการเลือกตำแหน่งวางเมล็ดจาก state ที่ไม่ถูกสัญชาตญาณหิววิกฤตครอบงำแล้วหรือยัง

## Hypotheses

- H1: ถ้า seed handling เริ่มเป็นพฤติกรรมเลือกตำแหน่งจริง จุด drop ควรมีคุณภาพสูงกว่าตำแหน่งปัจจุบันตอนถือเมล็ด (`current_position_control`) และสูงกว่า control ในระยะเห็น
- H2: ถ้าภาวะหิวเป็น confound หลัก การตัด hunger bonus อย่างเดียวควรลด critical-hunger drop ได้
- H3: ถ้า reward memory เป็นตัวช่วยหลัก การปิดหรือ shuffle reward memory ควรลด chain/site-selection signal อย่างชัดเจน

## Methods

รัน 6 conditions, condition ละ 5 seeds (`20260610` ถึง `20260614`), จำกัดเวลา 90 วินาทีต่อ run:

| condition | เป้าหมาย |
| --- | --- |
| `baseline_100x100` | baseline ของ Phase 5 |
| `no_hunger_seed_drop_bonus_100x100` | ตัด bonus ที่เพิ่มโอกาส drop ตอน hunger |
| `critical_hunger_drop_blocked_100x100` | ห้าม drop seed ตอน critical hunger |
| `safe_window_seed_drop_only_100x100` | ให้ drop ได้เฉพาะช่วง balanced/safe-window แบบ permissive |
| `reward_memory_disabled_100x100` | ปิด reward memory |
| `reward_memory_shuffled_100x100` | shuffle ตำแหน่ง reward memory ภายใน radius 16 |

ตัวชี้วัดหลัก:

- `drop_quality_vs_current_position_lift`
- `drop_quality_vs_visible_control_lift`
- `drop_quality_vs_hunger_recovery_position_lift`
- `drop_quality_vs_safe_window_position_lift`
- `high_quality_completed_chain_rate` เทียบกับ `low_quality_completed_chain_rate`
- `late_vs_early_drop_quality_lift`
- `safe_or_balanced_drop_fraction`
- `critical_hunger_drop_fraction`
- `agent_moved_drop_count`

เกณฑ์ Phase 5.5 ต้องการให้มีอย่างน้อย 3/5 seeds ผ่านเงื่อนไขหลัก และมี directional consistency ไม่ใช่ seed เดียวลากค่าเฉลี่ย

## Results

| condition | p5.5 pass | drops/run | safe/balanced | critical hunger | current lift | visible lift | recovery lift | safe-window lift | future lift | high chain | low chain | late/early |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 0/5 | 116.4 | 0.02127 | 0.97873 | 0.99590 | 0.97538 | 0.95070 | 0.99260 | 1.16360 | 0.22086 | 0.15577 | 1.06976 |
| no hunger bonus | 0/5 | 94.2 | 0.02032 | 0.97968 | 0.98644 | 0.97068 | 0.89516 | 0.99260 | 1.11308 | 0.11791 | 0.16318 | 1.10930 |
| critical blocked | 0/5 | 14.0 | 1.00000 | 0.00000 | 0.95932 | 0.93152 | 1.02500 | 0.99260 | 1.15230 | 0.00000 | 0.00000 | 0.98358 |
| safe-window only | 0/5 | 15.0 | 1.00000 | 0.00000 | 0.95892 | 0.92948 | 1.02376 | 1.02314 | 1.16798 | 0.00000 | 0.00000 | 0.99346 |
| memory disabled | 0/5 | 135.2 | 0.02636 | 0.97364 | 0.99542 | 0.97560 | 0.94726 | 0.99260 | 1.16042 | 0.20611 | 0.13416 | 1.05268 |
| memory shuffled | 0/5 | 139.2 | 0.03059 | 0.96941 | 0.99502 | 0.97072 | 0.93622 | 0.99260 | 1.15066 | 0.14038 | 0.14998 | 1.03778 |

Phase 5.5 state-decoupling summary:

- `pass = false`
- baseline safe/balanced fraction = `0.02127`
- `no_hunger_seed_drop_bonus`: activity ok แต่ safe fraction ไม่ดีขึ้น และ p5.5 pass = 0/5
- `critical_hunger_drop_blocked`: safe fraction ดีขึ้นมาก แต่ activity ไม่ผ่าน (`14.0 drops/run`)
- `safe_window_seed_drop_only`: safe fraction ดีขึ้นมาก แต่ activity ไม่ผ่าน (`15.0 drops/run`)

## Evidence Supporting

- plant lifecycle ยังเดินได้: ทุก condition ยังมี `plant_lifecycle_food_consumed` และมี chain seed -> plant -> fruit -> agent อยู่ในระดับหนึ่ง
- baseline มี high-quality chain rate สูงกว่า low-quality chain rate (`0.22086 > 0.15577`) และ memory-disabled ก็ยังคล้ายกัน (`0.20611 > 0.13416`)
- future path lift สูงสม่ำเสมอ (`~1.15-1.17`) แปลว่าจุด drop มักดีกว่าจุดที่ agent เดินต่อไปในอนาคต
- critical-blocked และ safe-window-only ตัด critical-hunger confound ได้จริง (`critical_hunger_drop_fraction = 0`)

## Evidence Against

- ทุก condition ได้ `phase5_5_passing_runs = 0/5` และ directional consistency = 0
- baseline มี `critical_hunger_drop_fraction = 0.97873` แปลว่าเกือบทุก drop เกิดตอนหิววิกฤต
- การตัด hunger bonus อย่างเดียวไม่ช่วย: critical hunger ยัง `0.97968` และ current lift ลดลงเป็น `0.98644`
- เมื่อบล็อก critical hunger activity collapse เหลือ `14-15 drops/run` ต่ำกว่า gate `50 drops/run`
- current-position control ไม่ผ่าน: ทุก condition มี mean current lift ต่ำกว่า 1.0 หรือใกล้ 1.0 มากเกินไป
- visible control ไม่ผ่านชัด: mean visible lift อยู่ประมาณ `0.929-0.976`
- safe-window-only ยังไม่มี chain signal เพราะ high/low chain rate เป็น `0.0/0.0`
- memory disabled/shuffled ไม่เปลี่ยน pattern หลักมากพอ จึงยังไม่มีหลักฐานว่า reward memory เป็นตัวอธิบาย site-selection

## Alternative Explanations

- จุด drop ดูดีเทียบ future path เพราะ agent เดินหนีไปยังพื้นที่แย่กว่า ไม่ใช่เพราะเลือกวางเมล็ดในพื้นที่ดี
- ecology อาจดีขึ้นตามเวลาเอง ทำให้ late/early lift ดีขึ้นบาง condition โดยไม่ใช่การเรียนรู้ของ agent
- critical hunger อาจเกิดเร็วเกินไปขณะถือเมล็ด ทำให้ seed handling ถูก hijack โดย food-seeking instinct ก่อนเกิด exploration
- safe-window-only threshold รอบนี้เป็นแบบ permissive เพื่อให้มี activity จึงตีความว่าเป็น balanced/non-critical window มากกว่า "รู้สึกปลอดภัยจริง" แบบเข้ม
- high-quality chain rate ใน baseline อาจมาจากพื้นที่อาหาร/ทางเดินซ้ำ ไม่ใช่การเลือกจุดปลูก

## Missing Evidence

- ยังไม่มี balanced-state drops มากพอสำหรับวัด chain rate
- ยังไม่มี control ที่แยก "drop เพราะถือมานาน" ออกจาก "drop เพราะเห็นพื้นที่ดี"
- ยังไม่มี causal intervention ที่เพิ่ม object handling โดยไม่บอกวิธีปลูก
- ยังไม่มี evidence ว่า agent เก็บเมล็ดแล้วชะลอการวางจน state ดีขึ้น
- ยังไม่มี large-world confirmation สำหรับพฤติกรรมที่แยกจาก food attraction

## Verdict

Phase 5.5 ยังไม่ผ่านเป้าหมายการเรียนรู้ seed placement

แต่เฟสนี้สำเร็จในเชิงวินิจฉัย: เรารู้แล้วว่า seed drop ปัจจุบันถูกครอบโดย critical hunger เป็นหลัก ไม่ใช่แค่เพราะ hunger bonus หรือ reward memory ถ้าตัด critical hunger ออกแบบแข็ง ๆ พฤติกรรมวางเมล็ดหายไปเกือบหมด ดังนั้นขั้นต่อไปไม่ควรเพิ่มคำสั่งปลูก แต่ควรเพิ่มแรงขับพื้นฐานที่เป็นธรรมชาติกว่า เช่น object handling pressure, curiosity toward carried objects, carry discomfort, หรือ attention ต่อวัตถุที่ถืออยู่ เพื่อให้มี balanced-state seed drops มากพอสำหรับการเรียนรู้จริง

Confidence level: ปานกลางถึงสูงสำหรับข้อสรุปเรื่อง hunger confound, ต่ำถึงปานกลางสำหรับข้อสรุปเรื่อง "ยังไม่มี learning" เพราะ sample balanced drops ยังน้อยมาก

## Before / After

ก่อน Phase 5.5:

- เรารู้ว่า seed -> plant -> fruit -> agent chain เกิดได้
- ยังไม่รู้ว่า seed drop เป็นการเลือกตำแหน่งจริงหรือเกิดจาก hunger/food attraction
- current-position control เป็นช่องโหว่หลักที่ต้องล็อกให้แน่น

หลัง Phase 5.5:

- current-position control ถูกเพิ่มเป็น gate หลักแล้ว
- quality score ถูกแยก component แล้ว
- early/late ใช้ first/last 30% ของ agent-moved drops
- เพิ่ม state controls: hunger recovery และ safe-window
- ยืนยันว่า critical hunger เป็น confound ใหญ่ที่สุด
- ยืนยันว่า memory ablation ไม่ใช่ตัวแก้ปัญหาหลัก
- ได้ blocker ใหม่: เมื่อตัด critical hunger แล้ว balanced seed-drop activity ต่ำเกินไป

## Recommended Next Phase: Phase 5.6

เป้าหมาย Phase 5.6 คือเพิ่ม seed-handling activity โดยไม่สอนการปลูก

ข้อเสนอ:

1. เพิ่ม `carried_object_attention` สำหรับวัตถุที่ถืออยู่
   - ไม่บอกว่า seed ใช้ปลูก
   - เพิ่มโอกาส inspect/move/drop เมื่อถือวัตถุนานขึ้น
   - วัด carry duration, inspect count, balanced drop count

2. เพิ่ม `carry_discomfort` แบบอ่อน
   - ถือเมล็ดนานแล้วเกิดความไม่สะดวกเล็กน้อย
   - drop chance เพิ่มตามเวลาถือ แต่ไม่ผูกกับ hunger
   - gate: balanced drops >= 50/run โดย critical hunger ไม่เกิน 30%

3. เพิ่ม `object novelty / curiosity`
   - agent มีแนวโน้มทดลองกับ object ที่เพิ่งพบ
   - ต้องไม่ใส่คำว่า farm, plant, bury, seed purpose

4. เพิ่ม control ใหม่
   - compare drop site กับตำแหน่งที่ถือเมล็ดครบ 5/10/20 ticks
   - compare drop site กับ random reachable visible cells ในช่วงเดียวกัน
   - แยก drop จาก food-contact, hunger, balanced, curiosity, carry-discomfort

5. Gate ใหม่ก่อนกลับไป Phase 5
   - balanced/non-critical drops >= 50/run อย่างน้อย 3/5 seeds
   - critical hunger drop fraction <= 0.30
   - current lift >= 1.03 เป็น exploratory threshold ก่อนค่อยกลับไป 1.10
   - visible lift >= 1.00
   - high-quality chain rate > low-quality chain rate อย่างน้อย 3/5 seeds

## Files Changed / Produced

- `agents/agent.py`
- `world/environment.py`
- `scripts/run_long_emergence_watch.py`
- `scripts/run_phase5_site_selection_probe.py`
- `reports/phase5_5_state_decoupled_protocol_2026-06-13.th.md`
- `reports/phase5_5_state_decoupled_confirm01_2026-06-13.th.md`
- `reports/phase5_5_state_decoupled_analysis_2026-06-13.th.md`
- `data/phase5_5_state_decoupled_confirm01_20260613/summary.json`
- `data/phase5_5_state_decoupled_confirm01_20260613/runs.csv`

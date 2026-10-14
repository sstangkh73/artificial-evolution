# Plan: YSC 2027 เฟส 3 (pilot) — งานของ /loop
Date: 2026-10-14 · ต่อจาก `worklog/2026-10-14-ysc-review/report.md`

## เป้าหมาย
ตอบคำถามว่า "เอเจนต์ค้นพบเครื่องมือได้หรือไม่" ด้วยหลักฐานหลายด้าน แล้วตรึง protocol สำหรับรันยืนยัน **จากนั้นหยุด** (ห้ามรัน seeds 5000+)

## การตัดสินใจของผู้ใช้ (14 ต.ค.)
- ขอบเขต: จบเฟส 3 แล้วหยุดให้ผู้ใช้ตรวจก่อนรันยืนยัน
- ตัดสินใจเองตามกติกาที่เขียนไว้ใน pilot protocol ก่อนรัน ให้หยุดถามเฉพาะเมื่อ Gate ไม่ผ่าน หรือผลขัดกับข้อเสนอ
- **เอเจนต์เป็นอมตะ**: ตัดเรื่องการตายออก เพื่อให้คำถามอยู่ที่การค้นพบเครื่องมือ (แทนการแก้ survivor bias ด้วย agent-slot)
- loop: ใช้ `ysc-loop/` (ดัดแปลงจาก `auto-loop/`) จำกัด 20 รอบหรือ 6 ชั่วโมง ประหยัดโทเค็น

## กติกาประจำทุกรอบ
- อ่านไฟล์นี้ก่อน ทำ **ขั้นแรกที่ยังไม่ติ๊ก** ให้เสร็จ 1 ขั้น (หรือขั้นย่อยที่จบในตัว) แล้วติ๊ก `[x]` พร้อมบันทึกผลสั้น ๆ ใต้ขั้นนั้น
- ทำงานผ่าน `ysc-loop/` (Claude + Codex ผลัดกันนำตามโทเค็นที่เหลือ อีกตัวรีวิว) ลูปเป็นคน commit ทุกรอบ ห้าม push
- ประหยัดโทเค็น: ใช้ `tail`/`-q` ดูผล อ่านไฟล์เฉพาะช่วงที่ต้องใช้ ห้าม dump events/ledger และสรุปผลลงไฟล์แทนการพิมพ์ยาว
- seeds: 0–99 ใช้แล้ว, pilot ใช้ 1000–1099 เท่านั้น, **ห้ามแตะ 5000+**
- ค่าเริ่มต้นของ config ต้องให้ผลเหมือน smoke เดิมทุกค่า: ฟีเจอร์ใหม่ทั้งหมดต้องเป็น opt-in และตรวจด้วยเทสต์
- เขียนเอกสารเป็นภาษาไทยวิชาการ เรียบง่าย ซื่อตรง ไม่อ้างเกินหลักฐาน

## ขั้นตอน
- [x] 1. **โหมดอมตะ** `ArenaConfig.immortal` (ค่าเริ่มต้น False): ไม่มีการตาย, พลังงานติดลบได้ (เป็นบัญชี), ไม่ใช้ craft_energy_reserve เมื่อเป็นอมตะ, เก็บ `ticks_below_zero` ไว้เป็นตัวชี้วัดรอง + เทสต์ + ยืนยันว่าค่าเริ่มต้นยังให้ผล smoke เดิม
  - เสร็จ 14 ต.ค.: `immortal` เป็น opt-in, มี event `agent_end` (เฉพาะโหมดอมตะ), summary มี `agents_ever_below_zero`, `mean_ticks_below_zero`, `mean_final_energy`; เทสต์ใหม่ 2 ข้อ; ค่าเริ่มต้นได้ผล smoke เดิมทุกค่า; ทั้ง repo 198 passed
  - ดูคร่าว ๆ (seeds 0–4 ซึ่งใช้ไปแล้ว ไม่ใช่ผล): net C0 −1.01, C1 0.35, C2 0.08, C3 0.51, C4 0.31 และ C0 ใช้เครื่องมือ 86% เพราะเมื่อไม่มีเกณฑ์พลังงานสำรอง C0 จะถือวัตถุครบ 2 ชิ้นตลอดและสุ่มเลือกได้ 10 จาก 11 ทาง → pilot ต้องตัดสินว่าจะเก็บต้นทุนการสร้างแบบนี้ไว้หรือไม่ (บันทึกเป็นประเด็นใน protocol)
- [x] 2. **แก้ตัวชี้วัด**: ระดับ A แบบอัตรา (`functional_rate` = functional/crafted, functional ต่อเอเจนต์), เปลี่ยนชื่อเป็น `level_b_run`, เพิ่ม `reuse_delta` (good−bad), เขียนสคริปต์วิเคราะห์ระดับ B ระหว่างเงื่อนไข (C1 เทียบ C0/C2 แบบจับคู่ seed) + เทสต์
  - เสร็จรอบ 1 (Claude นำ, Codex รีวิว): summary มี `functional_rate`, `functional_per_agent`, `reuse_delta`, `level_b_run` (เลิกใช้ `level_b`; ข้อมูล smoke เดิมยังใช้ชื่อเก่า ห้ามแก้); สคริปต์ `scripts/analyze_tool_discovery_level_b.py` จับคู่ seed ในโฟลเดอร์ grid เดียว รายงาน mean diff, SD, dz, นับ t>c/tie/c>t, bootstrap 95% CI, ปฏิเสธโฟลเดอร์ที่ปน config, ไม่ค้นพบ = censored ที่ `ticks`; เทสต์ใหม่ `tests/test_tool_discovery_phase3.py` 6 ข้อ; ทั้ง repo 204 passed; smoke ค่าเดิม
  - ประเด็นที่ต้องเขียนใน protocol (ขั้น 4): ตัวชี้วัด/คู่เทียบหลัก + การจัดการ multiple comparisons; `level_b_run` ผ่านได้แม้ไม่มีคู่ฝั่ง bad (เป็นแค่ตัวคัดกรอง); baseline มือเปล่าคำนวณจากทั้งรัน (ข้อมูลฝั่งผู้วิเคราะห์ ไม่ใช่สิ่งที่เอเจนต์รู้)
- [x] 3. **ความเรียบร้อยของ runner**: ปฏิเสธการรันถ้า code_dirty (ยกเว้นใส่ `--allow-dirty`), `--resume` ต้องตรวจว่า overrides ตรงกับ protocol.json, ค่าเริ่มต้นของ conditions รวม C4 + เทสต์
  - เสร็จรอบ 2 (Claude นำ, Codex รีวิว 2 รอบ): `git_dirty` ตรวจทั้ง `simulation/ world/ scripts/`; ปฏิเสธถ้า dirty เว้นแต่ `--allow-dirty` (บันทึก `code_dirty: true` และ resume ไม่ได้); protocol.json บันทึก `code_tree` (git tree hash ของ 3 โฟลเดอร์ที่ HEAD — ไม่เปลี่ยนเมื่อ commit แค่เอกสาร จึง resume ข้ามรอบลูปได้); `--resume` ต้องตรง conditions/seeds/overrides/code_tree/code_dirty, ปฏิเสธโฟลเดอร์ที่ไม่มี protocol.json และ summary ที่ config ไม่ตรง; รันที่ไฟล์ไม่ครบ 3 ชนิดจะถูกรันใหม่; manifest/summary.csv นับเฉพาะรันที่ protocol ระบุ; ปฏิเสธ seeds ≥5000 เว้นแต่ `--allow-confirmatory-seeds`; ค่าเริ่มต้น conditions = C0–C4; อ่าน git tree ไม่ได้ = หยุด; เทสต์ใหม่ `tests/test_tool_discovery_runner.py` 13 ข้อ; `pytest tests` 217 passed; smoke ค่าเดิม
  - หมายเหตุสำหรับขั้น 5: ต้องรัน pilot ตอน `git status` ของ 3 โฟลเดอร์สะอาด (ตอนนี้ไฟล์ที่เพิ่งแก้จะสะอาดหลังลูป commit)
- [x] 4. **เขียน pilot protocol** `docs/ysc2027_tool_discovery/03_pilot_protocol.md` และ commit ก่อนรัน: คำถาม, grid (ε, softmax τ, q_init แบบ optimistic, จำนวน tick), ตัวชี้วัดหลัก (อาหารสุทธิต่อ agent-tick ช่วงท้าย), หลักฐานการค้นพบ (ระดับ A อัตรา, reuse_delta, rebuild, เวลาถึงการค้นพบ, C1−C2), Gate A/B, **กฎการเลือกค่าที่เขียนไว้ก่อนรัน**, วิธีทำ power analysis จากผลต่าง C1−C2, H5 วัดเฉพาะฝั่งการใช้
  - เสร็จรอบ 3 (Claude นำ, Codex รีวิว 15 ข้อ): seeds แบ่ง S1 1000–1049 (เลือกค่า, 16 เซลล์ = ε {0.05,0.1,0.2,0.3} × q_init {0,10} × ticks {800,1600}, C0–C4) และ S2 1050–1099 (เฉพาะเซลล์ที่เลือก, ใช้ทำ power กัน winner's curse); หลัก = `final_net_per_alive_tick`, คู่หลัก C1−C2; เลือกเซลล์ด้วย C1 สูงสุดในเซลล์ที่ผ่าน Gate + กฎ 1 SE (เสมอ → tick น้อย, ε น้อย, q_init 0); power = safeguard dz (เปอร์เซ็นไทล์ 20 ของ bootstrap) + สูตร Guenther + ตรวจด้วยการจำลอง, ขั้นต่ำ 50, >2000 = หยุด; ตัด softmax (ไม่มีในโค้ด) ตัดสินก่อนรัน; ชื่อโฟลเดอร์ `data/tool_discovery_pilot_s1_e{ε×100:03d}_q{q}_t{ticks}` และ `..._s2_selected`
  - หมายเหตุขั้น 5: ต้องรันในรอบถัดไป (หลัง 03 ถูก commit) ใส่ `--set immortal=true` ทุกเซลล์; ขั้น 6 ต้องเขียนสคริปต์รวมผล 16 เซลล์ + power (ไม่มี scipy ใช้ random/statistics)
- [x] 5. **รัน pilot** ตาม grid บน seeds 1000–1099 (แบ่งเป็นชุด ใช้ `--resume`) จากโค้ดที่ commit แล้ว
  - เสร็จรอบ 4 (Claude นำ, Codex รีวิวตัวรัน): ส่วน S1 ครบ 16 โฟลเดอร์ × 250 รัน, `code_dirty: false`, immortal, seeds 1000–1049 ผ่าน verify ทุกข้อของข้อมูล pilot; C0/C3 เท่ากันข้ามเซลล์ที่ tick เท่ากัน (ตรวจ runner ✓); ตัวรัน `ysc-loop/run_pilot_s1.py` (8 เซลล์พร้อมกัน); ค่าเฉลี่ยเชิงพรรณนาใน `pilot_s1_status.md`
  - ตาม 03 ข้อ 3 ส่วน S2 (seeds 1050–1099) รันได้หลังเลือกเซลล์เท่านั้น → ย้ายไปทำในขั้น 6 (คำสั่งเดียวกัน, `--out data/tool_discovery_pilot_s2_selected`, ใช้เวลาราว 5–10 นาที)
  - ข้อสังเกตเบื้องต้น (ยังไม่ใช่ผลตามกฎ): q_init=10 ทำให้ C1/C2/C4 ติดลบทุกเซลล์; ใน q0 ค่า C1 > C2 ทุกเซลล์และช่องว่างกว้างขึ้นเมื่อ ε สูง
- [x] 6. **วิเคราะห์ pilot**: เลือกค่าตามกฎ, ตรวจ Gate, power analysis เพื่อหาจำนวน seed ที่ต้องใช้ในรันยืนยัน → `docs/ysc2027_tool_discovery/04_ผล_pilot.md`
  - 6a เสร็จรอบ 5 (Claude นำ, Codex รีวิว): สคริปต์ `scripts/analyze_tool_discovery_pilot.py` (`s1` = Gate + กฎเลือก + เงื่อนไขหยุด; `power` = Gate บน S2 + dz_safe + Guenther + จำลอง t-test) ปฏิเสธข้อมูลที่ไม่ครบ 16 เซลล์ × C0–C4 × 50 seeds; เทสต์ใหม่ `tests/test_tool_discovery_pilot_analysis.py` 11 ข้อ; ผล S1 ใน `docs/ysc2027_tool_discovery/pilot_s1_analysis.json`: ผ่าน Gate A/B ทั้ง 16 เซลล์ (B1 = 1.00 ทุกเซลล์ คือ C0 มีวัตถุที่ผ่านระดับ A ทุกรัน → B1 ผ่านง่าย ต้องเขียนใน 04), C1−C2 CI ไม่คร่อม 0 ทุกเซลล์, **เซลล์ที่เลือก: ε = 0.05, q_init = 0, ticks = 1600** (`e005_q0_t1600`, C1 = 0.398, SE 0.005, ไม่มีเซลล์เสมอใน 1 SE)
  - 6b (รอบถัดไป, ต้องให้ `scripts/` สะอาดหลังลูป commit ก่อน): รัน S2 `python scripts/run_tool_discovery.py --out data/tool_discovery_pilot_s2_selected --conditions C0 C1 C2 C3 C4 --seeds 1050-1099 --ticks 1600 --set immortal=true --set epsilon=0.05 --set q_init=0` แล้ว `python scripts/analyze_tool_discovery_pilot.py power data/tool_discovery_pilot_s2_selected --out docs/ysc2027_tool_discovery/pilot_s2_power.json`
  - 6c: เขียน `04_ผล_pilot.md` จาก 2 ไฟล์ JSON
  - 6b+6c เสร็จรอบ 6 (Claude นำ, Codex รีวิว): S2 ครบ 250/250 (commit f1985ef, clean, immortal); Gate A/B ผ่านซ้ำ; C1 − C2 = 0.279 [0.231, 0.331] 50/50 seeds, dz 1.51, dz_safe 1.45, Guenther n = 7 → **n = 50 (seeds 5000–5049)** power 1.00; ไม่มีเงื่อนไขหยุด ไฟล์: `pilot_s2_power.json`, `pilot_s2_secondary.json`, `pilot_s2_secondary_extra.json`, `04_ผล_pilot.md`
  - ข้อควรระวังสำหรับ 05: ผลต่างหลักราว 35% มาจากฝั่งการใช้ (อาหาร − แรง 0.099) อีก 65% มาจาก C1 สร้าง/เก็บน้อยกว่า; C1 ใช้เครื่องมือช่วงท้ายน้อยกว่า C2; ห้ามเพิ่มเกณฑ์ผ่าน/ไม่ผ่านใหม่ (ใช้ 03 ข้อ 8) แต่ตรึงการรายงานองค์ประกอบไว้ใน 05; config ของ 05 = ค่าเดียวกับ `data/tool_discovery_pilot_s2_selected/protocol.json` base_config
- [ ] 7. **ตรึง protocol ยืนยัน**: `docs/ysc2027_tool_discovery/05_confirmatory_protocol.md` + config JSON + SHA-256, commit, เขียน `report.md`, อัปเดต worklog/INDEX.md และ memory แล้ว**หยุด loop**

## เงื่อนไขให้หยุดถามผู้ใช้ (หยุด loop แล้วรายงาน)
- Gate A ไม่ผ่าน (C3 ไม่ดีกว่า C0 ชัดเจน) หรือ Gate B ไม่ผ่าน (C0 เป็นศูนย์หรือง่ายเกินไป)
- ทุกค่าใน grid ให้ C1 ไม่ต่างจาก C2 เลย
- ต้องแก้ `world/` หรือ `agents/`
- เทสต์ล้มแล้วแก้ไม่ได้ภายใน 2 รอบ

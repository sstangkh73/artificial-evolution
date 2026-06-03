# Simulation Architecture

## ภาษาไทย

### โมดูลปัจจุบัน

`main.py`
- จุดเริ่มต้นสำหรับรันการทดลองต้นแบบ

`agents/body.py`
- กฎงบประมาณร่างกาย
- นิยาม `BodyPlan`
- คลัง body เริ่มต้น

`agents/agent.py`
- สถานะของเอเจนต์
- การกระทำพื้นฐานเพื่อเอาชีวิตรอด
- การจัดการพลังงานและการเคลื่อนที่
- การสืบพันธุ์แบบใช้พลังงาน

`world/environment.py`
- ขนาดของโลก
- การเกิดและการกินอาหาร
- วงจรกลางวัน/กลางคืน
- biome และฤดูกาล

`simulation/runner.py`
- ลูปการทดลอง
- การเปรียบเทียบ body
- ตัวชี้วัดสรุปผล
- พลวัตประชากรและการคัดเลือกผู้รอด

### แผนการต่อยอด

#### เฟซ 1
- ขยายจาก body prototype 5 แบบเป็น 50 archetype ที่ถูก generate
- เพิ่มกลยุทธ์ mutation และ body generation

#### เฟซ 2
- เปลี่ยนจากพฤติกรรมแบบเขียนกฎเองง่ายๆ ไปเป็นการเรียนรู้หรือ controller ที่วิวัฒน์ได้
- ติดตามเหตุการณ์สูญพันธุ์และเวลาที่ใช้ในการปรับตัว
- เพิ่มระบบสืบพันธุ์และ generation

#### เฟซ 3
- เพิ่มการสื่อสาร
- เพิ่มความจำ
- เพิ่มระบบสะสมทรัพยากรและก่อสร้าง
- เพิ่มทรัพยากรหลายประเภท
- เพิ่มกลไกทางสังคมและอาณาเขต

### ลำดับการพัฒนาที่แนะนำ

1. ขยายการสร้าง body ให้ได้ 50 แบบที่ valid
2. บันทึกผลการทดลองลง `data/`
3. เพิ่มระบบสืบพันธุ์และ mutation
4. เพิ่ม controller แบบ neural network หรือ policy อย่างง่าย
5. เพิ่ม visualization สำหรับแนวโน้มประชากรและการอยู่รอด

## English

### Current Modules

`main.py`
- Entry point for running prototype experiments

`agents/body.py`
- Body budget rules
- `BodyPlan` definition
- Initial body library

`agents/agent.py`
- Agent state
- Basic survival actions
- Energy and movement handling
- Energy-based reproduction

`world/environment.py`
- World dimensions
- Food spawning and consumption
- Day/night cycle
- Biomes and seasons

`simulation/runner.py`
- Experiment loop
- Body comparison
- Summary metrics
- Population dynamics and survivor selection

### Planned Extensions

#### Phase 1
- Expand from 5 prototype bodies to 50 generated archetypes
- Add mutation and body generation strategies

#### Phase 2
- Replace simple hand-coded behavior with learning or evolved controllers
- Track extinction events and adaptation time
- Add reproduction and generations

#### Phase 3
- Add communication
- Add memory
- Add storage and construction systems
- Add multiple resource types
- Add social and territorial mechanics

### Recommended Next Build Order

1. Expand body generation to 50 valid bodies
2. Save experiment results into `data/`
3. Add reproduction and mutation
4. Introduce a simple neural or policy controller
5. Add visualization for population and survival trends

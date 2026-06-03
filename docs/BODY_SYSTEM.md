# ภาษาไทย

`TOTAL_BODY_COST = 100`

Sensor:
- cost = `10`
- เพิ่มศักยภาพการมองเห็น (`sensor vision`)
- การมองเห็นจริงจะถูกจำกัดโดยความสามารถในการประมวลผลของสมอง

Muscle:
- cost = `15`
- เพิ่มความเร็วในการเคลื่อนที่

Armor:
- cost = `20`
- เพิ่มความทนทานของร่างกาย
- ลดความเร็ว

Brain:
- cost = `25`
- เพิ่มคุณภาพในการตัดสินใจ
- เพิ่มการใช้พลังงานแบบ passive
- เพิ่มขีดจำกัดการประมวลผลการมองเห็น
- เพิ่มความจำระยะสั้น
- ช่วยหลีกเลี่ยงจุดอันตรายที่เคยเจอ
- ช่วยเลือกเส้นทางที่ปลอดภัยและคุ้มค่าพลังงานมากขึ้น
- ถ้าสมองมากพอ จะเริ่มเกิด cooperation ได้
- `brain >= 2` สามารถปรุงอาหารง่ายได้
- `brain >= 3` ทำอาหารแล้วได้โบนัสพลังงานสูงขึ้น
- `brain >= 4` แชร์อาหารให้ลูกหรือสมาชิกกลุ่มได้ดีขึ้น

Cooperation abilities:
- จำเพื่อน
- ส่งสัญญาณ
- ตามฝูง
- แบ่ง role
- วางแผนร่วมกัน

Food Intelligence:
- `raw_plant`: พลังงาน `6`, เก็บง่าย, เด็กโตช้า
- `cooked_plant`: พลังงานเริ่มต้น `14`, ต้องใช้สมอง/เวลา, เด็กโตปานกลาง
- `raw_meat`: พลังงาน `18`, ต้องล่าสัตว์, เด็กโตเร็วแต่เสี่ยง
- `cooked_meat`: พลังงานเริ่มต้น `30`, ต้องล่าและปรุง, เด็กโตเร็วที่สุด
- `brain >= 3` และ `brain >= 4` จะยกระดับค่าพลังงานอาหารปรุงขึ้นอีก

Team Hunting:
- สัตว์ใหญ่ต้องใช้พลังทีมในการล่า
- `group_power = sum(member.speed + member.durability/10 + member.brain)`
- ล่าคนเดียวมีโอกาสพลาด เสียพลังงาน และบาดเจ็บได้
- ล่าเป็นทีมช่วยให้ role อย่าง `planner`, `scout`, `guardian`, และ `forager` มีความหมายมากขึ้น
- สัตว์ใหญ่ใหม่อยู่เป็นฝูง (`herd`) มี `guard`, `grazer`, และ `calf`
- ฝูงสามารถเคลื่อนที่รวมกัน แตกหนีเป็นกลุ่ม และป้องกันลูกได้

Vision Balance:
- `effective_vision = min(sensor_vision, brain_processing_limit)`
- `brain_processing_limit = 2 * (brain + 1)`

ตัวอย่าง:
- Sensor `8`, Brain `0` -> Effective Vision `2`
- Sensor `8`, Brain `1` -> Effective Vision `4`
- Sensor `8`, Brain `2` -> Effective Vision `6`
- Sensor `8`, Brain `3` -> Effective Vision `8`

# English

`TOTAL_BODY_COST = 100`

Sensor:
- cost = `10`
- Increases sensing potential (`sensor vision`)
- Actual vision is limited by brain processing capacity

Muscle:
- cost = `15`
- Increases movement speed

Armor:
- cost = `20`
- Increases durability
- Reduces speed

Brain:
- cost = `25`
- Improves decision quality
- Adds passive energy drain
- Increases vision processing capacity
- Adds short-term memory
- Helps avoid previously dangerous locations
- Improves safe and energy-efficient path selection
- Enables cooperation when brain capacity is high enough
- `brain >= 2` can perform simple cooking
- `brain >= 3` gains stronger cooked-energy bonuses
- `brain >= 4` shares food more effectively with children or group members

Cooperation abilities:
- Remember allies
- Send signals
- Follow the group
- Split roles
- Plan together

Food Intelligence:
- `raw_plant`: `6` energy, easy to gather, slow child growth
- `cooked_plant`: starts at `14` energy, requires brain/tool/time, moderate child growth
- `raw_meat`: `18` energy, requires hunting, fast child growth but risky
- `cooked_meat`: starts at `30` energy, requires hunting plus cooking, fastest child growth
- `brain >= 3` and `brain >= 4` further improve cooked-food output

Team Hunting:
- Large animals require coordinated hunting power
- `group_power = sum(member.speed + member.durability/10 + member.brain)`
- Solo hunts tend to miss, fail to penetrate, drain energy, or trigger counter-damage
- Group hunts make `planner`, `scout`, `guardian`, and `forager` roles immediately meaningful
- Herd animals now have `guard`, `grazer`, and `calf` roles
- Herds move together, scatter under pressure, and defend their young

Vision Balance:
- `effective_vision = min(sensor_vision, brain_processing_limit)`
- `brain_processing_limit = 2 * (brain + 1)`

Examples:
- Sensor `8`, Brain `0` -> Effective Vision `2`
- Sensor `8`, Brain `1` -> Effective Vision `4`
- Sensor `8`, Brain `2` -> Effective Vision `6`
- Sensor `8`, Brain `3` -> Effective Vision `8`

# ภาษาไทย

## Technology Tier 1

เป้าหมายของ tier นี้คือทำให้ `brain` ไม่ได้ช่วยแค่เดินหรือปรุงอาหาร แต่ช่วยเปลี่ยนทรัพยากรธรรมชาติให้กลายเป็นความได้เปรียบระยะยาว

ลูปพื้นฐาน:
- หา resource
- เอากลับไปที่ `nest`
- คราฟต์อุปกรณ์
- ใช้อุปกรณ์เพิ่ม food yield หรือ hunting power
- เกิด surplus

### เงื่อนไขปลดล็อก
- `brain >= 3`
- ต้องอยู่ใกล้ `nest`
- ต้องมีพลังงานพอสำหรับคราฟต์
- ต้องมีวัสดุใน `nest storage`

### วัสดุพื้นฐาน
- `wood`
- `stone`
- `fiber`

### Knife
- สูตร: `stone=1`, `fiber=1`
- ใช้พลังงานคราฟต์: `10`
- ประโยชน์:
- เพิ่มประสิทธิภาพการชำแหละเนื้อ
- เพิ่มพลังงานจากการล่าสำเร็จ
- เหมาะกับสาย parent/caretaker และการป้องกันระยะใกล้

### Spear
- สูตร: `wood=2`, `stone=1`, `fiber=1`
- ใช้พลังงานคราฟต์: `16`
- ประโยชน์:
- เพิ่ม `group_power` ตอนล่าสัตว์ใหญ่
- ลดความเสี่ยงและต้นทุนของการล่า
- เปลี่ยน behavior ให้กล้าล่าเป้าหมายใหญ่ขึ้นและรักษาระยะมากขึ้น

### Sickle
- สูตร: `wood=1`, `stone=1`, `fiber=2`
- ใช้พลังงานคราฟต์: `12`
- ประโยชน์:
- เก็บพืชได้คุ้มขึ้น
- เพิ่มพลังงานจากการ harvest
- ช่วยผลักระบบไปสู่ surplus economy
- เปลี่ยน behavior ให้กลับไปหาแหล่งพืชเดิมและสร้าง gathering route ง่ายขึ้น

## Need-Based Crafting

- `food shortage` -> เอนเอียงไป `sickle`
- `large prey nearby` หรือมีทีม -> เอนเอียงไป `spear`
- `child care / close defense` -> เอนเอียงไป `knife`
- เป้าคือทำให้ tool ไม่ใช่แค่ passive bonus แต่เป็นตัวเปลี่ยนการตัดสินใจ

## Tier ถัดไป

### Bow
- ใช้สำหรับล่าระยะไกล
- ทำให้ `scout/hunter` มีความหมายมากขึ้น

### Storage Upgrade
- เพิ่มความจุอาหารและวัสดุ
- ทำให้ `nest` กลายเป็น settlement จริง

### Farming Tools
- อุปกรณ์สำหรับเพาะปลูก
- ผลักโลกจาก daily foraging ไป seasonal planning

# English

## Technology Tier 1

The goal of this tier is to make `brain` valuable not only for movement and cooking, but also for transforming raw environmental resources into long-term survival advantages.

Core loop:
- gather resources
- return them to the `nest`
- craft tools
- use tools to improve food yield or hunting power
- create surplus

### Unlock Conditions
- `brain >= 3`
- must be near a `nest`
- must have enough energy to craft
- must have the required materials in `nest storage`

### Core Materials
- `wood`
- `stone`
- `fiber`

### Knife
- Recipe: `stone=1`, `fiber=1`
- Craft energy cost: `10`
- Effects:
- improves meat processing
- increases energy gained from successful hunts
- fits parent/caretaker and close-defense behavior

### Spear
- Recipe: `wood=2`, `stone=1`, `fiber=1`
- Craft energy cost: `16`
- Effects:
- increases `group_power` during large-animal hunts
- reduces hunting risk and energy waste
- changes behavior toward larger prey, better engagement range, and stronger group hunting

### Sickle
- Recipe: `wood=1`, `stone=1`, `fiber=2`
- Craft energy cost: `12`
- Effects:
- improves plant harvesting efficiency
- increases energy gained from harvest
- helps push the system toward surplus economy
- changes behavior toward repeated harvest routes and food-source revisits

## Need-Based Crafting

- `food shortage` -> biases toward `sickle`
- `large prey nearby` or active group hunting -> biases toward `spear`
- `child care / close defense` -> biases toward `knife`
- the goal is to make tools alter decisions, not only grant passive bonuses

## Next Tiers

### Bow
- enables ranged hunting
- gives stronger meaning to `scout/hunter` roles

### Storage Upgrade
- increases food and material capacity
- pushes a `nest` toward becoming a true settlement

### Farming Tools
- supports cultivation systems
- shifts the world from daily foraging toward seasonal planning

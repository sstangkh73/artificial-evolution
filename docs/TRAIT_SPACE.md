# TRAIT SPACE / พื้นที่ลักษณะเชิงวิวัฒนาการ

## ภาษาไทย

ระบบร่างกายเวอร์ชันนี้ไม่ได้มอง agent เป็นแค่ `sensor / muscle / armor / brain` อีกต่อไป แต่เพิ่มชั้น trait เพื่อเปิดพื้นที่ให้เกิดความหลากหลายเชิงพฤติกรรมและนิเวศ

### Core Morphology
- `sensor_units`: ระยะรับรู้พื้นฐาน
- `muscle_units`: ศักยภาพการเคลื่อนที่
- `armor_units`: ความทนทาน
- `brain_units`: ศักยภาพการรับรู้และวางแผนขั้นพื้นฐาน

### Continuous Cognition Traits
- `brain_capacity`: ขยายขีดจำกัดการประมวลผล
- `memory_retention`: ความสามารถในการเก็บและใช้แผนที่ความจำ
- `planning_focus`: ความสามารถด้าน route planning, settlement planning, crafting decisions

### Hidden Behavioral Traits
- `cooperation_drive`: แนวโน้มร่วมมือและคงกลุ่ม
- `parenting_instinct`: แนวโน้มดูแลลูกและลงทุนกับ lineage
- `curiosity`: แนวโน้มสำรวจ
- `fear`: แนวโน้มหลบอันตราย
- `aggression`: แนวโน้มเข้าล่า/เข้าปะทะ

### Metabolism And Diet
- `metabolism_rate`: เร็วแต่หิวไว หรือช้าแต่ประหยัด
- `plant_efficiency`: ประสิทธิภาพการใช้พลังงานจากพืช
- `meat_efficiency`: ประสิทธิภาพการใช้พลังงานจากเนื้อ

### Reproduction Strategy
- `reproduction_drive`: แนวโน้มเร่งขยายพันธุ์
- `reproduction_investment`: แนวโน้มลงทุนต่อหนึ่งลูก

### Trait Profiles รุ่นแรก
- `cautious_forager`: เน้นความระวัง หาอาหารพืช และความจำ
- `social_planner`: เน้นการร่วมมือ วางแผน ตั้งหลัก และใช้สมอง
- `fierce_hunter`: เน้นการล่า ความกล้า และ meat specialization
- `nurturing_settler`: เน้นการเลี้ยงลูก ตั้งรกราก และเก็บสะสม

### สิ่งที่เปลี่ยนในระบบ
- body แบบ morphology เดียวกันสามารถมี behavior ต่างกันได้
- memory, heat-use efficiency, danger avoidance และ hunting ถูก bias ด้วย traits
- cooking และ home-building ไม่เกิดจาก trait ตรง ๆ ใน substrate-first runs
- diet specialization เริ่มมีผลต่อ value ของอาหาร
- role identity เริ่มอิง personality + ecology มากกว่า stat ดิบ

### ข้อจำกัดของเวอร์ชันนี้
- ยังเป็น hybrid model ระหว่าง discrete morphology กับ continuous traits
- ยังไม่มี mutation ข้าม trait space แบบต่อเนื่องเต็มรูปแบบ
- reproduction strategy ยังส่งผลบางส่วน ยังไม่ใช่ระบบ lineage เต็ม

## English

This version no longer treats agents as only `sensor / muscle / armor / brain`. It adds trait layers so the simulation can express behavioral and ecological diversity.

### Core Morphology
- `sensor_units`: base sensing range
- `muscle_units`: movement potential
- `armor_units`: durability
- `brain_units`: base cognitive capacity

### Continuous Cognition Traits
- `brain_capacity`: extends processing limits
- `memory_retention`: supports map-like memory retention
- `planning_focus`: biases routing, settlement, and crafting decisions

### Hidden Behavioral Traits
- `cooperation_drive`: tendency to cooperate and maintain groups
- `parenting_instinct`: tendency to invest in offspring and lineage
- `curiosity`: exploration tendency
- `fear`: danger avoidance tendency
- `aggression`: hunting and confrontation tendency

### Metabolism And Diet
- `metabolism_rate`: fast-but-hungry vs slow-but-efficient
- `plant_efficiency`: energy conversion from plants
- `meat_efficiency`: energy conversion from meat

### Reproduction Strategy
- `reproduction_drive`: tendency toward faster breeding
- `reproduction_investment`: tendency toward higher investment per child

### First Trait Profiles
- `cautious_forager`
- `social_planner`
- `fierce_hunter`
- `nurturing_settler`

### What Changes In Practice
- the same morphology can now produce different behaviors
- memory, heat-use efficiency, danger avoidance, and hunting are trait-biased
- cooking and home-building do not come directly from traits in substrate-first runs
- diet specialization starts to shape food value
- role identity is driven more by personality plus ecology than by raw stats alone

### Current Limits
- this is still a hybrid model, not a fully continuous evolutionary genome
- continuous trait mutation is not implemented yet
- reproduction strategy only partially affects lineage outcomes so far

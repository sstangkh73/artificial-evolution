# ภาษาไทย

World size: `100x100`

Energy:
- เอเจนต์เสียพลังงาน `1` หน่วยต่อ tick
- การเคลื่อนที่ใช้พลังงาน
- อาหารช่วยฟื้นฟูพลังงาน

Death:
- ตายเมื่อ `energy <= 0`
- ตายเมื่อ `body durability <= 0`
- เด็กที่โดดเดี่ยวมีโอกาสตายง่ายขึ้น

Life Stages:
- `Child (0-30)`: ช้า มองเห็นน้อย สืบพันธุ์ไม่ได้
- `Juvenile (31-60)`: เริ่มหาอาหารเองได้ แต่ยังอ่อน
- `Adult (61-160)`: ความสามารถเต็ม สืบพันธุ์ได้
- `Old (161-200)`: ความเร็ว การมองเห็น และประสิทธิภาพพลังงานลดลง

Reproduction:
- ต้องมี `age >= adult_age`
- ต้องมี `energy >= reproduction_threshold`
- ต้องมี `durability >= minimum_health`
- ต้องอยู่ใกล้ `nest`

Child Support:
- ถ้า child อยู่ใกล้ parent/group จะเสียพลังงานน้อยลงและรอดง่ายขึ้น
- ถ้า child อยู่คนเดียว จะเสียพลังงานมากขึ้น เคลื่อนไหวแย่ลง และตายง่ายขึ้น
- parent และ caretaker จะพยายามอยู่ใกล้เด็กเพื่อลดการตายจากการโดดเดี่ยว
- ถ้า `child.distance_to(parent) > SAFE_RADIUS` จะเกิด stress สะสม
- ถ้าอยู่ใกล้พ่อแม่ `passive_drain` ของ child จะลดลงมาก

Family Unit:
- เด็กทุกตัวมี `parent_id`
- พ่อแม่จะจำ `children_ids` ของตัวเอง
- มี `bond_strength` ระหว่าง parent-child
- bond เพิ่มเมื่ออยู่ใกล้กัน เดินด้วยกัน หรือให้อาหารกัน
- bond ลดเมื่อพลัดหลง บาดเจ็บ หรือขาดอาหาร
- ถ้าลูกหาย พ่อแม่สามารถ `search_for_child`
- ถ้าลูกอ่อนแอหรือบาดเจ็บ พ่อแม่สามารถ `protect_child`
- ถ้าอาหารน้อย พ่อแม่ที่ฉลาดพอจะพยายาม `share_food_with_child`
- กลุ่มสามารถมี `shared home` อิงจาก nest ของครอบครัวหรือสมาชิกหลัก
- บ้านทำหน้าที่เป็น return point, child area, และจุดรวมของการนอน/พัก/เก็บของ

Nest Construction:
- ถ้า `brain >= 3`, พลังงานสูงพอ, และมี resource รอบตัวพอ เอเจนต์สามารถ `build_nest`
- `nest` สร้าง `safe radius`
- ในเขตบ้าน เด็กโดดเดี่ยวน้อยลง, passive drain ลด, และอันตรายจากโลกต่ำลง
- บ้านกลายเป็นจุดอ้างอิงสำหรับครอบครัวและการสืบพันธุ์
- บ้านสามารถเก็บ `food_storage`
- ถ้ามี surplus เอเจนต์จะเก็บอาหารส่วนเกินไว้ในบ้าน
- เด็กหรือสมาชิกครอบครัวที่พลังงานต่ำสามารถดึงอาหารจากบ้านได้
- นักล่าหรือผู้หาอาหารสามารถ `food redistribution` ให้ลูกหรือกลุ่มได้เมื่อกลับถึงบ้าน

Memory Map:
- `brain >= 2` จะเริ่มจำ `remembered_food_sources`
- `brain >= 2` จะเริ่มจำ `remembered_safe_zones`
- `brain >= 2` จะเริ่มจำ `remembered_nest_locations`
- agent จะพยายามใช้ memory เพื่อลดการเดินมั่ว กลับบ้านได้แม่นขึ้น และใช้พลังงานกับ route ที่คุ้มกว่าเดิม
- brain สูงขึ้นทำให้การเดินตาม memory เสถียรขึ้นและคุ้มพลังงานมากขึ้น

Zones:
- `Safe Low Food`: อาหารน้อย อันตรายต่ำ
- `Safe High Food`: อาหารเยอะ อันตรายต่ำ
- `Danger High Food`: อาหารเยอะ อันตรายสูง
- `Danger Low Food`: อาหารน้อย อันตรายสูง

Food:
- อาหารมีหลายชนิด: `raw_plant`, `cooked_plant`, `raw_meat`, `cooked_meat`
- พืชเกิดแบบสุ่มตามโซน
- สัตว์ใหญ่เกิดเป็นฝูงในโซนที่อาหารสูงและอันตรายสูง
- มีจำนวนจำกัด
- มีวัสดุเทคโนโลยีพื้นฐาน: `wood`, `stone`, `fiber`

Cooking:
- `brain >= 2` เริ่มปรุงอาหารง่ายได้
- `brain >= 3` ได้โบนัสพลังงานจากอาหารปรุงสูงขึ้น
- `brain >= 4` แชร์อาหารให้ลูกหรือกลุ่มได้ดีขึ้น

Hunting:
- สัตว์ใหญ่ต้องใช้ทีมถึงจะล่าได้จริง
- ล่าคนเดียวมีโอกาสพลาด เสียพลังงาน และบาดเจ็บ
- ล่าเป็นทีมมีโอกาสได้เนื้อดิบ/เนื้อปรุงที่พลังงานสูงกว่า
- สัตว์ฝูงมี `guard behavior`, ลูก (`calf`), และการแตกหนีเป็นกลุ่ม

Tools:
- `brain >= 3` สามารถเก็บวัสดุและสร้างเครื่องมือพื้นฐานได้
- เครื่องมือ tier แรกคือ `knife`, `spear`, `sickle`
- `knife` ทำให้การชำแหละเนื้อคุ้มขึ้น
- `spear` ทำให้การล่าเป็นทีมคุ้มขึ้นและปลอดภัยขึ้น
- `sickle` ทำให้การเก็บพืชคุ้มขึ้นและมีโอกาสเกิด surplus มากขึ้น
- เครื่องมือทุกชิ้นมีอายุการใช้งานและพังได้

Child Growth:
- เด็กที่กินพืชดิบจะโตช้ากว่า
- เด็กที่ได้อาหารปรุงหรือเนื้อจะโตเร็วกว่าและรอดง่ายขึ้น

Danger:
- โซนอันตรายมีโอกาสทำให้ร่างกายสึกหรอ
- ตัวเร็ว สมองดี และเกราะสูงมีโอกาสรับมือได้ดีกว่า

Day/Night:
- การมองเห็นลดลงในเวลากลางคืน

# English

World size: `100x100`

Energy:
- Agents lose `1` energy per tick
- Movement costs energy
- Food restores energy

Death:
- Death occurs when `energy <= 0`
- Death occurs when `body durability <= 0`
- Isolated children become much easier to kill

Life Stages:
- `Child (0-30)`: low speed, low vision, cannot reproduce
- `Juvenile (31-60)`: can begin to forage alone, but remains weak
- `Adult (61-160)`: full ability, can reproduce
- `Old (161-200)`: speed, vision, and energy efficiency decline

Reproduction:
- Requires `age >= adult_age`
- Requires `energy >= reproduction_threshold`
- Requires `durability >= minimum_health`
- Requires being near a `nest`

Child Support:
- If a child stays near a parent/group, energy drain is lower and survival improves
- If a child is alone, energy drain rises, movement worsens, and death becomes more likely
- Parents and caretakers try to stay near children to reduce isolation deaths
- If `child.distance_to(parent) > SAFE_RADIUS`, stress accumulates
- If a child stays near a parent, passive drain is reduced significantly

Family Unit:
- Every child has a `parent_id`
- Parents remember their own `children_ids`
- Parent-child pairs maintain `bond_strength`
- Bonds rise when they stay close, travel together, or share food
- Bonds weaken with separation, injury, and starvation pressure
- Missing children can trigger `search_for_child`
- Vulnerable children can trigger `protect_child`
- Smart parents can prioritize `share_food_with_child`

Nest Construction:
- If `brain >= 3`, energy is high enough, and nearby resources meet the requirement, an agent can `build_nest`
- A `nest` creates a local `safe radius`
- Inside the nest radius, child isolation pressure drops, passive drain is reduced, and environmental danger is lower
- Nests become the anchor point for family behavior and reproduction
- Nests can maintain `food_storage`
- When surplus exists, agents can store extra food in the nest
- Low-energy children or family members can withdraw food from the nest

Memory Map:
- `brain >= 2` can remember `remembered_food_sources`
- `brain >= 2` can remember `remembered_safe_zones`
- `brain >= 2` can remember `remembered_nest_locations`
- Agents use memory to reduce random wandering, return to nests more reliably, and spend energy on more efficient routes
- Higher brain values make memory-guided navigation more stable and energy-efficient

Zones:
- `Safe Low Food`: low food, low danger
- `Safe High Food`: high food, low danger
- `Danger High Food`: high food, high danger
- `Danger Low Food`: low food, high danger

Food:
- Food now has multiple forms: `raw_plant`, `cooked_plant`, `raw_meat`, `cooked_meat`
- Wild plant food is now a bootstrap source that declines after early ticks
- Plant-lifecycle food is the intended long-run food source
- Large animals spawn as herds in high-food, high-danger areas
- Food amount is limited
- Basic technology materials exist: `wood`, `stone`, `fiber`

Cooking:
- Brain/cooking traits no longer cook food by themselves
- Food only becomes cooked when the agent is exposed to an external heat source
- Automatic food sharing and group redistribution are disabled in substrate-first runs

Hunting:
- Large animals require team hunting to be reliable
- Solo hunts can miss, waste energy, or cause injuries
- Group hunts can unlock higher-value meat resources
- Herd prey now has guard behavior, calves, and group escape reactions

Tools:
- `brain >= 3` can gather materials and craft basic tools
- First-tier tools are `knife`, `spear`, and `sickle`
- `knife` improves meat processing efficiency
- `spear` improves team hunting value and safety
- `sickle` improves plant harvesting and increases the chance of surplus
- All tools have durability and can break

Persistent Roles:
- บาง agent จะมี `preferred_role` ติดตัว เช่น `hunter`, `gatherer`, `protector`, `caretaker`, `crafter`
- เมื่อเกิดการรวมกลุ่ม role จะไม่รีเซ็ตแบบสุ่มทั้งหมดอีก แต่จะอิงจาก body, brain, และหน้าที่เดิม
- role ที่คงอยู่ช่วยให้ behavior ต่อเนื่องขึ้น เช่น hunter ล่าต่อเนื่อง, gatherer วิ่ง route เดิม, protector เฝ้าบ้าน

Child Growth:
- Raw plants produce the slowest child growth
- Cooked food and meat improve growth and survival

Danger:
- Dangerous zones can damage body durability
- Fast, smart, and armored agents handle danger better

Day/Night:
- Vision is reduced at night

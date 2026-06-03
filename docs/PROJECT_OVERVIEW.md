# Project Overview

## ภาษาไทย

### แนวคิดหลัก

โครงการนี้ศึกษาว่าโครงสร้างร่างกายที่มีประสิทธิภาพ
และพฤติกรรมที่ซับซ้อนมากขึ้น
สามารถเกิดขึ้นเองได้หรือไม่ในเอเจนต์ประดิษฐ์ที่อยู่ในโลกซึ่งมีทรัพยากรจำกัด

การจำลองจะเริ่มจากความหลากหลายของร่างกาย
จากนั้นจึงทดสอบการอยู่รอดภายใต้แรงกดดันของสิ่งแวดล้อม
และต่อยอดไปสู่การศึกษาการเกิดของพฤติกรรมแบบ open-ended ในระยะยาว

### เฟซ 1: สร้างร่างกาย 50 แบบ

เป้าหมาย:
สร้างโครงสร้างร่างกายที่แตกต่างกัน 50 แบบภายใต้งบต้นทุนรวมเท่ากัน

คำถาม:
- องค์ประกอบร่างกายแบบใดที่สามารถใช้งานได้จริง
- มี trade-off อะไรบ้างระหว่างการรับรู้ การเคลื่อนที่ การป้องกัน และการคิด

ผลลัพธ์:
- คลัง body archetype จำนวน 50 แบบ
- ข้อมูลกำกับของแต่ละแบบ เช่น cost, vision, speed, durability และ brain drain

### เฟซ 2: อยู่รอดโดยไม่มีความรู้ล่วงหน้า

เป้าหมาย:
ปล่อย body ทุกแบบลงในโลกโดยให้มีเพียงความสามารถในการกระทำขั้นพื้นฐาน
และไม่มี strategy การเอาชีวิตรอดที่ใส่ไว้ล่วงหน้า

คำถาม:
- ต้องใช้เวลานานแค่ไหนกว่าจะค้นพบพฤติกรรมที่ช่วยให้รอด
- body แบบไหนอยู่รอดได้นานกว่า
- body แบบไหนสูญพันธุ์ และสูญพันธุ์เพราะอะไร

ตัวชี้วัด:
- เวลาในการอยู่รอด
- ปริมาณอาหารที่กินได้
- จำนวนประชากรที่เหลือ
- สาเหตุการตาย
- เวลาที่ใช้ก่อนกินอาหารสำเร็จครั้งแรก

### เฟซ 3: การเกิดของพฤติกรรมระยะยาว

เป้าหมาย:
ปล่อยสายพันธุ์ที่อยู่รอดได้ดีที่สุดให้ดำเนินต่อไป
แล้วสังเกตว่าพฤติกรรมขั้นสูงกว่าจะเกิดขึ้นเองหรือไม่เมื่อเวลาผ่านไป

คำถาม:
- จะเกิดความเชี่ยวชาญเฉพาะด้านหรือไม่
- จะเกิดความร่วมมือหรือความขัดแย้งหรือไม่
- เอเจนต์จะเริ่มสะสมทรัพยากร สร้างอาณาเขต หรือประสานงานกันได้หรือไม่
- ภายใต้เงื่อนไขที่ซับซ้อนขึ้น จะเกิดพฤติกรรมคล้ายอารยธรรมหรือไม่

พฤติกรรมระยะท้ายที่อาจเกิดขึ้น:
- ความร่วมมือ
- การแข่งขัน
- การป้องกันอาณาเขต
- การสะสมทรัพยากร
- การเพาะปลูก
- การก่อสร้าง
- การแลกเปลี่ยน
- สงคราม

### ขอบเขตต้นแบบปัจจุบัน

โค้ดปัจจุบันเป็นซิมเอาชีวิตรอดขั้นต่ำ
ที่ออกแบบมาเพื่อรองรับเฟซ 1
และเวอร์ชันเริ่มต้นของเฟซ 2

สิ่งที่มีแล้วในต้นแบบ:
- โลกขนาดคงที่
- ระบบเกิดอาหาร
- การลดลงของพลังงาน
- ผลกระทบจากกลางวัน/กลางคืนต่อการมองเห็น
- trade-off ของโครงสร้างร่างกาย
- ลูปเปรียบเทียบหลายเอเจนต์

## English

### Core Idea

This project explores whether efficient body structures and increasingly
complex behavior can emerge naturally in artificial agents placed inside a
resource-limited world.

The simulation begins with body diversity, then tests survival under pressure,
and eventually studies long-term open-ended emergence.

### Phase 1: Generate 50 Body Types

Goal:
Create 50 distinct body structures under the same total body budget.

Questions:
- Which body compositions are even viable?
- What trade-offs appear between sensing, movement, defense, and cognition?

Output:
- A library of 50 body archetypes
- Per-body metadata such as cost, vision, speed, durability, and brain drain

### Phase 2: Survival Without Prior Knowledge

Goal:
Drop all body types into the world with only basic action capability and no
preloaded survival strategy.

Questions:
- How long does it take to discover useful survival behavior?
- Which bodies survive longer?
- Which bodies go extinct and why?

Metrics:
- Survival time
- Food consumption
- Population remaining
- Death reason
- Time to first successful food capture

### Phase 3: Long-Term Emergence

Goal:
Continue the simulation with the strongest surviving lineages and observe
whether more advanced behavior emerges over time.

Questions:
- Does specialization appear?
- Do cooperation or conflict emerge?
- Can agents begin storing resources, forming territories, or coordinating?
- Under richer conditions, can proto-civilization behaviors emerge?

Possible Late Behaviors:
- Cooperation
- Competition
- Territory defense
- Resource storage
- Farming
- Construction
- Trade
- War

### Immediate Prototype Scope

The current codebase implements a minimal survival simulation intended to
support Phase 1 and an early version of Phase 2.

Current prototype includes:
- Fixed-size world
- Food spawning
- Energy drain
- Day/night vision penalty
- Body trade-offs
- Multi-agent body comparison loop

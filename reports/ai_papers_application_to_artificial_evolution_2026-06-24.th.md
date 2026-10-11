# รายงาน: การประยุกต์ paper ด้าน AI training, reinforcement learning, agent และ alignment กับโปรเจกต์ Artificial Evolution

วันที่จัดทำ: 2026-06-24  
โครงการ: Artificial Evolution  
แหล่ง paper หลัก: `C:\artificial-evolution\papers`  
แหล่งสถานะโปรเจกต์หลัก: `docs/CURRENT_STATE.md`, `reports/project_status_full_2026-06-20.md`, `reports/agent_food_value_individual_tracking_2026-06-23.th.md`

---

## บทคัดย่อ

รายงานฉบับนี้ประเมินว่า paper ด้านการเทรน AI ตั้งแต่ Transformer, GPT, RLHF, Constitutional AI, DPO, ReAct, Toolformer, Reflexion, Voyager, DQN, AlphaGo Zero, AlphaZero, MuZero และ World Models สามารถนำมาปรับใช้หรือใช้อ้างอิงกับโปรเจกต์ Artificial Evolution ได้อย่างไร โดยพิจารณาจากสถานะจริงของระบบปัจจุบัน ไม่ใช่จากความคล้ายเชิงชื่อเท่านั้น

ข้อสรุปหลักคือ paper กลุ่ม LLM เช่น GPT, InstructGPT, Claude หรือ Llama เหมาะกับการใช้อธิบาย "หลักการเรียนจากข้อมูลและ feedback" และ "การจัด post-training/evaluation" มากกว่าการเอา LLM เข้าไปควบคุม agent โดยตรงในระยะสั้น ส่วน paper ที่เหมาะกับการพัฒนาแกนโปรเจกต์มากที่สุดคือ DQN, AlphaGo Zero/AlphaZero, MuZero, World Models, ReAct, Toolformer, Reflexion และ Voyager เพราะทั้งหมดพูดถึง agent ที่เลือก action จาก state, reward, search, memory, tool use และ environment feedback ซึ่งตรงกับคำถามหลักของโปรเจกต์ว่า agent ในโลกไม่มี label จะเรียนรู้พฤติกรรมที่มีประโยชน์ได้เองหรือไม่

รายงานเสนอ roadmap การนำไปใช้ 7 ขั้น: ตรวจ replication ก่อน, สร้าง action-value controller แบบเล็ก, เพิ่ม encounter-level telemetry, ทดสอบ social transmission, สร้าง world-model สำหรับ seed placement, เพิ่ม skill library สำหรับพฤติกรรมซ้ำได้, และสุดท้ายเชื่อมกับ endogenous mutation-and-selection loop เพื่อยกระดับจาก individual learning ไปสู่ evolution ข้ามรุ่น

---

## 1. คำถามของรายงาน

คำถามหลักของรายงานนี้คือ:

> paper ด้าน AI training และ agent research ที่รวบรวมไว้สามารถนำมาใช้กับโปรเจกต์ Artificial Evolution ส่วนใดได้บ้าง และควรใช้อย่างไรโดยไม่ overclaim?

คำถามย่อย:

1. paper ใดใช้เป็นกรอบทฤษฎีสำหรับอธิบายสิ่งที่โปรเจกต์ทำอยู่แล้ว
2. paper ใดควรแปลงเป็นการทดลองหรือ feature ใหม่
3. paper ใดใช้ได้เฉพาะเป็น citation หรือกรอบระวัง claim
4. paper ใดไม่ควรนำมาใช้ตรง ๆ เพราะจะทำให้เสียโจทย์ "ไม่มี label / ไม่มี oracle / ไม่ scripted"
5. ถ้าจะลงมือทำจริง ควรเริ่มจากขั้นไหนก่อน

---

## 2. สถานะจริงของโปรเจกต์ที่ต้องยึดเป็นฐาน

จาก `docs/CURRENT_STATE.md` ระบบปัจจุบันมีองค์ประกอบสำคัญเหล่านี้แล้ว:

- โลก grid `100x100`
- ecological zones 4 แบบ
- day/night และ seasons
- body plan ที่มี sensor, muscle, armor, brain ภายใต้งบ cost คงที่
- hidden traits เช่น memory, planning, cooperation, parenting, curiosity, fear, metabolism
- life stages: child, juvenile, adult, old
- lineage, parent-child, bond, caretaker/protector behavior
- nest, food storage, material storage
- memory ของ food, danger, safe zone, nest
- food processing, raw/cooked food
- material gathering: wood, stone, fiber
- Tier 1 tools: knife, spear, sickle
- experiment framework และ telemetry

แต่ข้อจำกัดสำคัญคือ:

- ยังไม่มี mutation-and-selection loop ที่เกิดเองเต็มรูปในซิม
- successful variants ยังมาจาก external search มากกว่าการกลายพันธุ์ตอน reproduction
- population sustainability ยังไม่ผ่าน
- social transmission ยังไม่ถูกพิสูจน์
- economy และ production chain ยังตื้น
- movement RNG / true replication เคยเป็น risk สำคัญในรายงานก่อนหน้า

จาก `reports/project_status_full_2026-06-20.md` claim ที่แข็งที่สุดตอนนี้คือ:

- ecology gate ผ่าน
- reward-place learning มี return lift สูง
- seed causality substrate มี delayed ecological consequence
- food-value learning ระดับรายตัวมีหลักฐานดี
- negative results สำคัญมาก: site selection ยังไม่ผ่าน, seed placement ถูก hunger confound, population ยังติด R0/bistability

จาก `reports/agent_food_value_individual_tracking_2026-06-23.th.md` หลักฐานที่แข็งที่สุดของการเรียนรู้คือ:

- agent 12 ตัวถูก track รายตัว
- 10 ตัวเริ่มข้าม `raw_seed`
- ทั้ง 10 ตัวเคยกินทั้ง `raw_seed` และ `raw_plant` ด้วยตัวเองก่อน
- 2 ตัวที่ยังไม่เคยกิน `raw_plant` ยังไม่ข้าม seed
- `agents_skipped_seed_without_recorded_taste = 0`

ดังนั้น current scientific position ที่ควรยึดคือ:

> โปรเจกต์พิสูจน์ individual experience-based learning ได้ในระดับ resource value แต่ยังไม่พิสูจน์ social transmission, intentional farming, stable endogenous evolution หรือ full technology emergence

---

## 3. หลักการจาก paper ที่เกี่ยวข้องกับโปรเจกต์โดยตรง

### 3.1 DQN: agent เลือก action จาก reward ไม่ใช่สคริปต์

Paper: `26_Human_Level_Control_through_Deep_Reinforcement_Learning_DQN.pdf`

DQN ใช้ neural network ประเมิน Q-value ของ action จาก observation แล้วเลือก action ที่คาดว่าจะให้ return สูงที่สุด หลักการสำคัญคือ agent ไม่ได้ถูกเขียน script เฉพาะเกม แต่เรียน policy จาก reward signal และประสบการณ์

สิ่งที่นำมาใช้กับโปรเจกต์ได้:

- ใช้เป็นกรอบอธิบาย "agent เลือกเอง" แบบไม่ overclaim
- แปลง food choice / movement target ให้เป็น action-value problem
- เริ่มจาก Q-table หรือ linear model ก่อน neural network
- ใช้ experience replay แบบเล็กกับเหตุการณ์สำคัญ เช่น food eaten, food skipped, danger hit, successful return

จุดเชื่อมกับโค้ดปัจจุบัน:

- ตอนนี้ food-value learning อยู่ใน `agents/agent.py` ผ่าน `food_value_memory` และ `_food_worth_eating`
- agent เรียนค่าพลังงานของ food kind จากประสบการณ์ตรง
- นี่ใกล้ RL แบบง่าย แต่ยังไม่ใช่ action-value controller เต็ม

ข้อเสนอ:

> สร้าง `QValueFoodPolicy` หรือ `ExperienceValuePolicy` แบบเล็กสำหรับตัดสินใจ eat/skip/move-to-food/store/drop โดยยังไม่ใช้ neural network ก่อน

---

### 3.2 AlphaGo Zero / AlphaZero: self-improvement จาก self-play และ selection

Papers:

- `27_AlphaGo_Zero_Mastering_the_Game_of_Go_without_Human_Knowledge.pdf`
- `28_AlphaZero_Mastering_Chess_and_Shogi_by_Self_Play.pdf`

AlphaGo Zero และ AlphaZero เริ่มจากกฎเกม ไม่ใช้เกมมนุษย์ แล้วให้ระบบเล่นกับตัวเองเพื่อสร้างข้อมูล training รอบต่อไป หลักการที่สำคัญต่อโปรเจกต์ไม่ใช่เกม Go หรือ chess แต่คือวงจร:

```text
policy ปัจจุบัน -> สร้างประสบการณ์ใน environment -> ประเมินผล -> ปรับ policy -> ทำซ้ำ
```

สิ่งที่นำมาใช้กับโปรเจกต์ได้:

- ออกแบบ evolutionary tournament ระหว่าง body/policy variants
- ให้ lineage ที่อยู่รอด/สืบพันธุ์/ใช้ทรัพยากรได้ดีเป็น source ของ mutation รุ่นต่อไป
- ใช้ self-play ในความหมายกว้าง: agent แข่งขันและร่วมมือใน environment เดียวกัน ไม่ใช่เล่นเกมกับตัวเองตามตัวอักษร

ข้อเสนอ:

> ทำ endogenous selection loop โดยเปรียบเทียบ 4 regime: no mutation, trait-only mutation, morphology-only mutation, combined mutation

Metric สำคัญ:

- lineage persistence
- generation depth
- mature offspring per female
- R0
- tool-use event count
- food-value learning transfer
- morphology diversity
- trait diversity

---

### 3.3 MuZero และ World Models: เรียน model ของโลกเพื่อวางแผน

Papers:

- `29_MuZero_Mastering_Atari_Go_Chess_and_Shogi_by_Planning.pdf`
- `1803.10122v4.pdf`

MuZero เรียน model ที่ทำนายสิ่งสำคัญต่อ planning ได้แก่ reward, value และ policy โดยไม่จำเป็นต้องรู้ dynamics จริงทั้งหมด ส่วน World Models แยก representation, memory/dynamics และ controller

ส่วนที่เข้ากับโปรเจกต์มากที่สุดคือ Phase 5 site selection เพราะปัญหาปัจจุบันคือ seed placement ยังถูก hunger pathing ครอบ ไม่ใช่ learned site selection

สิ่งที่นำมาใช้:

- ให้ agent เรียนว่า action บางแบบมี delayed consequence
- สร้าง predictive memory ว่า location/zone/moisture/soil/safety แบบไหนทำให้ seed germinate, mature, fruit
- แยก "จำตำแหน่งอาหาร" ออกจาก "คาดการณ์ผลของการวาง seed"

ข้อเสนอ:

> เพิ่ม `local_outcome_model` ราย agent หรือราย lineage สำหรับทำนาย delayed reward ของ seed placement โดยเริ่มจาก table/EMA ไม่ใช่ neural network

ตัวอย่าง state:

- zone type
- danger level
- moisture/temperature/soil proxy ถ้ามี
- distance to nest
- current hunger state
- prior plant success nearby

ตัวอย่าง prediction:

- probability(seed -> plant)
- expected ticks to food
- expected return value
- risk while returning

---

### 3.4 ReAct: think-act-observe loop

Paper: `16_ReAct_Synergizing_Reasoning_and_Acting_in_Language_Models.pdf`

ReAct ให้ LLM สลับ reasoning กับ action และรับ observation จาก environment กลับมา จุดสำคัญที่ใช้กับโปรเจกต์ได้คือ loop ไม่ใช่ตัว LLM:

```text
state -> internal decision trace -> action -> observation -> update memory
```

ในโปรเจกต์เราไม่ควรใส่ text reasoning ให้ agent โดยตรง เพราะจะเพิ่ม semantics จากภายนอก แต่สามารถใช้ ReAct เป็นกรอบ telemetry ได้:

- agent เห็นอะไร
- internal score/memory คืออะไร
- เลือก action อะไร
- outcome คืออะไร
- memory update อย่างไร

ข้อเสนอ:

> เพิ่ม encounter-level telemetry แบบ ReAct-lite โดยไม่เปลี่ยน behavior ก่อน เพื่อให้แยก "เห็นแล้วไม่กิน", "ไม่เห็น", "เห็นแต่เลือกเดินไปทางอื่น", "ข้ามเพราะ learned value" ได้

---

### 3.5 Toolformer: เรียนว่าจะใช้ tool เมื่อไร

Paper: `17_Toolformer_Language_Models_Can_Teach_Themselves_to_Use_Tools.pdf`

Toolformer ไม่ได้มีประโยชน์เพราะมันเป็น LLM แต่เพราะมันตั้งคำถามว่า model จะเรียนได้ไหมว่าเมื่อไรควรใช้ tool และใช้ tool แล้วผลดีขึ้นหรือไม่

โปรเจกต์มี Tier 1 tools แล้ว:

- knife
- spear
- sickle

สิ่งที่ควรทำ:

- วัด tool-use ROI แยกต่อ tool
- แยกว่า tool ถูกใช้เพราะ scripted role หรือเพราะ experience ทำให้คุ้มขึ้น
- ทำ ablation: no tool, tool exists but no memory, tool durability high/low, tool material scarce/abundant

Metric:

- spear -> hunting success / injury reduction
- sickle -> plant harvest rate / surplus storage
- knife -> meat processing value
- tool breakage cost
- net energy after tool chain

---

### 3.6 Reflexion: เรียนจาก feedback โดยไม่ update weight

Paper: `19_Reflexion_Language_Agents_with_Verbal_Reinforcement_Learning.pdf`

Reflexion ใช้ verbal memory ให้ agent สะท้อนข้อผิดพลาดและทำดีขึ้นในรอบถัดไป สำหรับโปรเจกต์เราไม่ควรใช้ verbal memory ตรง ๆ แต่ใช้แนวคิด "episodic feedback memory" ได้

สิ่งที่นำมาใช้:

- เก็บ failure memory เช่น "กินสิ่งนี้แล้วได้พลังงานต่ำ", "เข้าพื้นที่นี้แล้วบาดเจ็บ", "ล่าคนเดียวแล้วเจ็บ"
- เก็บ success memory เช่น "กลับตำแหน่งนี้แล้วได้อาหาร", "ใช้ spear กับกลุ่มแล้วสำเร็จ"
- ใช้ memory เหล่านี้เปลี่ยน action score

ข้อเสนอ:

> สร้าง `episodic_outcome_memory` ที่บันทึก action-context-outcome เป็น record สั้น ๆ แล้วใช้ influence movement/action policy

ต้องระวัง:

- อย่าใส่ label ว่า "ดี" หรือ "ไม่ดี" โดยตรงจากผู้ทดลอง
- ให้ค่ามาจาก consequence เช่น energy gain, durability loss, child survival, successful return

---

### 3.7 Voyager: skill library และ lifelong learning

Paper: `20_Voyager_Open_Ended_Embodied_Agent_with_LLMs.pdf`

Voyager ใช้ automatic curriculum, skill library และ iterative prompting ใน Minecraft สำหรับโปรเจกต์เราไม่ควรเอา GPT-4 มาควบคุม agent เพราะจะทำลายโจทย์ "ไม่สอน strategy ระดับสูง" แต่ skill library เป็นแนวคิดที่มีประโยชน์มาก

นำมาใช้แบบปลอดภัย:

- skill ไม่ใช่ข้อความภาษา แต่เป็น action sequence หรือ behavior pattern ที่วัดผลได้
- skill เกิดจากการทำสำเร็จซ้ำ ไม่ใช่ผู้วิจัยป้อนชื่อความหมาย
- skill ถูก reuse เมื่อ context คล้ายเดิม

ตัวอย่าง skill substrate:

- `return_to_food_site`
- `avoid_danger_route`
- `store_surplus_at_nest`
- `group_hunt_with_spear`
- `harvest_with_sickle`
- `maintain_hearth_when_fuel_available`

ชื่อข้างบนเป็นชื่อในรายงาน/telemetry ได้ แต่ใน agent ควรเก็บเป็น vector/record ของ context-action-outcome มากกว่าคำ semantic ที่มนุษย์สอน

---

### 3.8 RLHF, DPO, Constitutional AI: ใช้กับ evaluation และ claim discipline

Papers:

- `07_Fine_Tuning_Language_Models_from_Human_Preferences.pdf`
- `08_Learning_to_Summarize_from_Human_Feedback.pdf`
- `10_InstructGPT_Training_LMs_to_Follow_Instructions_with_Human_Feedback.pdf`
- `11_Training_a_Helpful_and_Harmless_Assistant_with_RLHF.pdf`
- `12_Constitutional_AI_Harmlessness_from_AI_Feedback.pdf`
- `14_Direct_Preference_Optimization_DPO.pdf`

กลุ่มนี้ไม่ควรถูกใช้เป็น training signal ให้ agent ในการทดลองหลัก เพราะจะกลายเป็น human preference/oracle แต่ใช้ได้ดีมากในชั้น evaluation หลังรันและการเขียนรายงาน

การประยุกต์ที่เหมาะ:

- ทำ trajectory ranking หลังรันว่า behavior ใดดู technology-like กว่า
- สร้าง rubric แยก evidence level
- ใช้ constitution ของข้ออ้างเพื่อกัน overclaim

ตัวอย่าง claim constitution:

- ห้ามเรียก `intentional farming` ถ้า site-selection control ยังไม่ผ่าน
- ห้ามเรียก `social transmission` ถ้าไม่มี naive-agent evidence
- ห้ามเรียก `endogenous evolution` ถ้ายังไม่มี self-sustaining reproduction และ mutation inheritance
- ห้ามเรียก `language` ถ้ายังไม่มี communication protocol ที่ส่งผลต่อ task
- ห้ามเรียก `planning` ถ้ายังไม่มี evidence ของ delayed outcome prediction หรือ search

---

### 3.9 Scaling Laws และ Chinchilla: ใช้กับ experiment scaling

Papers:

- `06_Scaling_Laws_for_Neural_Language_Models.pdf`
- `09_Training_Compute_Optimal_Large_Language_Models_Chinchilla.pdf`

สำหรับโปรเจกต์เรา บทเรียนไม่ใช่การเพิ่ม parameter ของ LLM แต่คือการจัดสรรงบทดลอง:

- number of seeds
- ticks per run
- population size
- world size
- telemetry frequency
- condition count
- replication quality

Chinchilla สอนว่า "ใหญ่ขึ้นอย่างเดียวไม่พอ ต้อง balance data/compute" โปรเจกต์เราก็เหมือนกัน: รันยาวขึ้นอย่างเดียวไม่พอถ้า seed ไม่ independent หรือ telemetry ไม่ตอบคำถาม

ข้อเสนอ:

> ก่อนรันใหญ่ทุกครั้ง ต้องมี replication audit และ power/variance estimate แบบง่ายจาก pilot run

---

### 3.10 Emergent communication papers: ยังเป็น future work

Papers:

- `1901.08706v2.pdf`
- `2302.14276v1.pdf`
- `2501.00226v2.pdf`

paper กลุ่มนี้เข้ากับเป้าหมายระยะยาวเรื่อง social learning, communication, cultural transmission และ collective world model แต่ยังไม่ควรนำมาเป็น claim ปัจจุบัน

เงื่อนไขก่อนเริ่ม:

- ต้องมี individual learning ที่ยืนยันแบบ multi-seed แล้ว
- ต้องมี encounter/proximity telemetry
- ต้องมี social exposure design
- ต้องแยก naive vs knowledgeable agent ได้
- ต้องมี channel การสื่อสารที่ไม่ hard-code ความหมาย

---

## 4. ตาราง mapping: paper -> ใช้กับโปรเจกต์อย่างไร

| กลุ่ม paper | ใช้กับส่วนใดของโปรเจกต์ | ระดับความพร้อม | ข้อควรระวัง |
| --- | --- | --- | --- |
| DQN | food/action value learning | ใช้ได้เร็ว | เริ่มจาก Q-table ก่อน neural net |
| AlphaGo Zero / AlphaZero | endogenous selection, mutation regimes | ใช้เป็นกรอบทดลอง | self-play ไม่เท่ากับ evolution โดยตรง |
| MuZero / World Models | seed placement, delayed consequence, planning | ควรทำหลัง telemetry พร้อม | ห้ามใส่ oracle ว่า seed ดี/ไม่ดี |
| ReAct | action-observation telemetry | ใช้ได้ทันที | ใช้เป็น logging pattern ไม่ใช่ใส่ text reasoning |
| Toolformer | tool-use ROI | ใช้ได้กับ Tier 1 tools | ต้องแยก tool scripted vs learned |
| Reflexion | episodic outcome memory | ใช้ได้หลัง event schema ชัด | memory ต้องมาจาก consequence |
| Voyager | skill library | ใช้ได้หลัง repeated behavior trace | skill name ไม่ควรเป็น semantic label ใน agent |
| RLHF/DPO | trajectory evaluation/rubric | ใช้หลังรัน | ห้ามป้อน human preference กลับเข้า agent หลัก |
| Constitutional AI | claim-safety constitution | ใช้ได้ทันที | เป็น reporting discipline ไม่ใช่ agent cognition |
| Scaling Laws/Chinchilla | experiment budget, seed/tick/pop scaling | ใช้ได้ทันที | ต้องแก้ replication ก่อน |
| Emergent communication | social learning/proto-language | ยังเป็น future work | ต้องมี naive/exposure controls |
| Sims artificial creatures | morphology-controller coevolution | เหมาะกับ long-term evolution | ต้องมี endogenous mutation loop ก่อน |

---

## 5. Roadmap การนำไปใช้

### Phase A: Replication Gate ก่อนเพิ่ม feature

เหตุผล: รายงานก่อนหน้าพบว่า movement RNG เคยไม่ผูกกับ `args.seed` ทำให้บางผล multi-seed อาจเป็น deterministic n=1

วัตถุประสงค์:

- ยืนยันว่า seed เปลี่ยน trajectory จริง
- ทำให้ multi-seed experiment เป็น replicate จริง

Independent Variables:

- `seed`
- RNG plumbing mode

Dependent Variables:

- initial positions
- movement trajectory hash
- food encounter sequence
- event count distribution

Control Variables:

- world size
- body index
- population
- tick count
- environment config

Metrics:

- trajectory hash uniqueness
- event sequence divergence
- variance across seeds

Success Criteria:

- seeds ต่างกันให้ trajectory/event distribution ต่างกัน
- seed เดิม rerun แล้วได้ผลซ้ำ

Failure Criteria:

- 3 seeds ให้ output identical ใน driver สำคัญ
- seed เดิม rerun แล้ว drift โดยไม่มีเหตุผล

Paper ที่อ้างอิง:

- Scaling Laws / Chinchilla ในเชิง experiment budget

---

### Phase B: DQN-lite / Q-value food policy

วัตถุประสงค์:

- ขยาย food-value learning จาก "จำค่า food kind" ไปเป็น "เลือก action ตาม state"
- ยังไม่ใช้ neural network เพื่อคุมความซับซ้อน

State:

- energy
- hunger
- food kind
- learned food value
- best known food value
- distance to remembered food
- danger level
- distance to nest

Actions:

- eat
- skip
- move toward remembered food
- move toward nest
- explore

Reward/consequence:

- net energy gain
- durability loss
- survival ticks
- successful return to food

Controls:

- current heuristic
- memory disabled
- shuffled food-value memory
- value-blind policy

Metrics:

- low-value meals per 1000 ticks
- seed skip after plant taste
- learning latency
- survival time
- intake per agent tick
- deficit per agent tick

Success Criteria:

- low-value consumption ลดลงเทียบ baseline
- agent ที่ skip ต้องมี experience trace
- memory-disabled ทำให้ effect หายหรือลดลงชัด

Failure Criteria:

- policy skip food โดยไม่มีประสบการณ์
- starvation floor ถูกละเมิดจน agent ตายเพราะไม่กิน
- effect ยังอยู่แม้ shuffle memory

Paper ที่อ้างอิง:

- DQN
- Fine-Tuning from Human Preferences เฉพาะแนวคิด reward from feedback ไม่ใช่ human label

---

### Phase C: Encounter-level telemetry แบบ ReAct-lite

วัตถุประสงค์:

- แยกว่า agent ไม่กินเพราะไม่เห็น, เห็นแต่ข้าม, เห็นแต่เลือกทางอื่น, หรือไม่มีประสบการณ์

Events ที่ควรเพิ่ม:

- `food_seen`
- `food_considered`
- `food_eaten`
- `food_skipped`
- `nearby_agent_eating`
- `tool_seen`
- `tool_used`
- `danger_seen`
- `action_selected`
- `memory_updated`

Metrics:

- seen-to-eaten rate
- seen-to-skipped rate
- skipped without prior taste
- action choice by state bucket
- proximity to knowledgeable agent before first skip

Success Criteria:

- ทุก claim เรื่อง learning มี causal trace ระดับ encounter
- สามารถแยก individual learning กับ social exposure ได้

Failure Criteria:

- เห็นเฉพาะ aggregate count แต่ตอบไม่ได้ว่า decision เกิดจากอะไร

Paper ที่อ้างอิง:

- ReAct
- Reflexion

---

### Phase D: Social transmission experiment

วัตถุประสงค์:

- ทดสอบว่า agent naive เปลี่ยนพฤติกรรมจากการอยู่ใกล้ knowledgeable agent หรือไม่

Independent Variables:

- social exposure: isolated, mixed, forced proximity
- knowledgeable ratio: 0%, 25%, 50%, 75%
- communication channel: none, proximity-only, observable eating, future explicit signal

Dependent Variables:

- naive agent first skip tick
- skipped seed without direct plant taste
- neighbor influence score
- learning latency

Controls:

- isolation control
- shuffled-neighbor control
- memory-disabled control
- no-plant-taste control

Success Criteria:

- naive agent ใน exposure condition เปลี่ยนเร็วกว่า isolation
- effect หายเมื่อปิด social/proximity channel
- มี evidence ว่า agent ยังไม่มี direct taste แต่เปลี่ยนหลัง exposure

Failure Criteria:

- agent ต้องชิมเองเสมอจึงเปลี่ยน
- proximity ไม่มีผล
- social effect ยังอยู่แม้ shuffle exposure

Paper ที่อ้างอิง:

- emergent communication papers
- Reflexion เฉพาะ memory/feedback framing

สถานะปัจจุบัน:

- ยังไม่ควร claim social transmission เพราะรายงานล่าสุดพบ `agents_skipped_seed_without_recorded_taste = 0`

---

### Phase E: World-model seed placement

วัตถุประสงค์:

- แก้ Phase 5 ที่ seed placement ถูก critical hunger ครอบ
- ให้ agent เรียน delayed ecological outcome ของ seed placement

Independent Variables:

- world-model enabled/disabled
- hunger-confound blocked/unblocked
- memory shuffled
- site feature visibility

Dependent Variables:

- balanced drops per run
- critical hunger drop fraction
- moved/control lift
- seed -> plant -> food chain completion
- same-agent return to placed site

Controls:

- current hunger-driven seed drop
- random drop
- carried-position control
- memory disabled
- reward memory shuffled

Success Criteria:

- balanced drops >= 50/run
- critical hunger fraction <= 0.30
- moved/control lift > 1.2 แบบ replicate ได้
- memory disabled ลด effect

Failure Criteria:

- activity collapse เมื่อ block hunger
- lift ใกล้ 1.0
- non-dropper return สูงเท่า dropper โดยไม่มี agent-specific signal

Paper ที่อ้างอิง:

- MuZero
- World Models
- AlphaZero เฉพาะ planning/search/self-improvement framing

---

### Phase F: Tool-use และ skill library

วัตถุประสงค์:

- ทดสอบว่า tool และ action sequence กลายเป็น reusable capability ได้หรือไม่

Independent Variables:

- tool availability
- material scarcity
- skill memory enabled/disabled
- tool durability
- group hunting required/not required

Dependent Variables:

- tool-use event count
- net energy gain after tool chain
- hunt success
- injury rate
- surplus stored
- repeated sequence count

Controls:

- no tool
- tool exists but no memory
- tool effects disabled
- random tool use

Success Criteria:

- tool-use ROI เป็นบวก
- action sequence ที่สำเร็จถูก reuse ใน context คล้ายเดิม
- skill memory disabled ทำให้ reuse ลดลง

Failure Criteria:

- tool ถูกใช้เพราะ role script แต่ไม่มี payoff
- tool เพิ่ม event count แต่ลด survival/reproduction
- sequence ไม่เกิดซ้ำเมื่อเปลี่ยน seed

Paper ที่อ้างอิง:

- Toolformer
- Voyager
- Reflexion

---

### Phase G: Endogenous mutation-and-selection loop

วัตถุประสงค์:

- ย้ายจาก external variant search ไปสู่ evolution ภายใน simulation

Independent Variables:

- mutation mode: none, trait-only, morphology-only, combined
- mutation rate
- inheritance strength
- population density
- reproduction regime

Dependent Variables:

- generation depth
- lineage persistence
- morphology diversity
- trait diversity
- R0
- mature offspring
- technology/skill events per lineage

Controls:

- no mutation
- random replacement
- external search baseline

Success Criteria:

- mutation regime บางแบบเพิ่ม lineage persistence โดยไม่ boom-crash
- trait/morphology distribution เปลี่ยนตาม selection pressure
- learned behavior หรือ tool-use payoff สัมพันธ์กับ reproduction/survival

Failure Criteria:

- ทุก regime สูญพันธุ์เหมือนเดิม
- diversity collapse ทันที
- mutation effect ไม่มีความต่างจาก random drift

Paper ที่อ้างอิง:

- Sims artificial creatures
- AlphaGo Zero/AlphaZero
- DQN
- MuZero

---

## 6. สิ่งที่ควรใช้เป็น citation ในรายงานประกวดหรือ paper

### ใช้อธิบายระบบเรียนรู้จาก feedback

- DQN: agent เลือก action จาก reward และ observation
- AlphaGo Zero/AlphaZero: self-improvement จาก environment rule และ feedback โดยไม่ใช้ human demonstrations
- MuZero: planning ด้วย learned model ของ dynamics
- World Models: internal model ของ environment

### ใช้อธิบาย AI สมัยใหม่ที่ไม่ได้เป็น script

- Transformer
- GPT-2/GPT-3
- InstructGPT
- Constitutional AI
- DPO
- DeepSeek-R1

แต่ในรายงานโปรเจกต์ควรเขียนว่า:

> งานเหล่านี้เป็นแรงบันดาลใจเชิงหลักการเรื่อง learning from data/feedback และ agent decision-making ไม่ได้หมายความว่าโปรเจกต์นี้เทรน LLM ขนาดใหญ่

### ใช้อธิบาย tool-use / agent loop

- ReAct
- Toolformer
- Reflexion
- Voyager

ควรเขียนว่า:

> โปรเจกต์นำแนวคิด action-observation loop, tool-use evaluation และ reusable skill memory มาปรับในโลก artificial life แบบไม่ใช้ LLM เป็น oracle

### ใช้อธิบาย claim discipline

- RLHF
- DPO
- Constitutional AI
- Claude system card

ใช้เพื่อบอกว่า:

> งาน AI สมัยใหม่ให้ความสำคัญกับ evaluation, safety, red teaming และการไม่ overclaim ซึ่งสอดคล้องกับการที่โปรเจกต์นี้แยก claim ที่พิสูจน์แล้วออกจาก future work

---

## 7. สิ่งที่ไม่ควรทำ

### 7.1 ไม่ควรเอา LLM มาเป็นสมอง agent ในตอนนี้

เหตุผล:

- จะทำให้ agent ได้ world knowledge จากภายนอก
- ขัดกับโจทย์ไม่มี label/no oracle
- อธิบายยากว่า behavior เกิดจากโลกจำลองหรือ pretrained knowledge
- ทำให้รายงานแข่งโดนถามหนักเรื่อง external intelligence

ใช้ LLM ได้ในชั้น:

- ช่วยวิเคราะห์ logs
- ช่วยเขียนรายงาน
- ช่วย generate rubric หลังทดลอง
- ไม่ใช่เป็น controller ของ agent ใน experiment หลัก

### 7.2 ไม่ควร claim ว่าเกิด farming แล้ว

สถานะที่ถูกต้อง:

- มี seed causality substrate
- มี plant lifecycle
- มี food-value learning
- site selection ยังไม่ผ่าน
- seed placement ยังถูก hunger confound

คำที่ปลอดภัย:

- proto-farming substrate
- delayed ecological consequence
- seed-to-plant causal chain

คำที่ยังไม่ควรใช้:

- intentional farming
- agriculture
- learned cultivation

### 7.3 ไม่ควร claim social learning จาก food-value run ล่าสุด

ผลล่าสุดสนับสนุน individual learning มากกว่า social transmission เพราะ agent ที่ข้าม seed ล้วนมีประสบการณ์ตรง

คำที่ปลอดภัย:

- individual experience-based food-value learning
- no evidence of social transmission in this run

คำที่ยังไม่ควรใช้:

- agents taught each other
- cultural transmission
- social learning confirmed

### 7.4 ไม่ควร claim open-ended evolution

ยังไม่มี:

- stable self-sustaining population
- in-simulation mutation-selection loop เต็ม
- cross-generation adaptation ที่ replicate ได้

คำที่ปลอดภัย:

- lineage dynamics
- selection pressure
- structural barriers to stable evolution
- future endogenous evolution loop

---

## 8. ข้อเสนอเชิง implementation

### 8.1 เพิ่ม policy abstraction

ตอนนี้ behavior หลายส่วนอยู่ใน `agents/agent.py` โดยตรง ควรค่อย ๆ แยกเป็น policy components:

- `FoodChoicePolicy`
- `MovementTargetPolicy`
- `SeedPlacementPolicy`
- `ToolUsePolicy`
- `SocialExposurePolicy`

เป้าหมายไม่ใช่ refactor ใหญ่ทันที แต่เพื่อให้ ablation ง่าย:

- heuristic policy
- memory policy
- q-value policy
- shuffled-memory policy
- disabled policy

### 8.2 เพิ่ม event schema ที่ชัด

ควรทำให้ event ทุกตัวมี field พื้นฐาน:

- tick
- agent_id
- lineage_id
- generation
- x, y
- state summary
- action
- target
- reason/source
- outcome
- memory before/after ถ้าเกี่ยวข้อง

### 8.3 เพิ่ม experiment manifest

ทุก run ควรบันทึก:

- git commit
- command
- seed
- RNG mode/version
- config hash
- enabled policies
- ablation condition
- expected hypothesis

### 8.4 เพิ่ม claim gate

สร้างไฟล์หรือ section ใน report ที่บอกว่า claim ใดผ่าน gate แล้ว:

| Claim | Evidence required | Status |
| --- | --- | --- |
| Food-value learning | per-agent taste -> value -> skip trace | ผ่าน smoke, รอ multi-seed |
| Social transmission | naive changes after exposure | ยังไม่ผ่าน |
| Site selection | moved/control lift + hunger controlled | ยังไม่ผ่าน |
| Tool-use learning | ROI + ablation | ยังไม่ทดสอบครบ |
| Endogenous evolution | self-sustaining population + inherited variation | ยังไม่ผ่าน |

---

## 9. แผนงาน 4 ช่วง

### ช่วง 1: Scientific hygiene

เป้าหมาย:

- แก้/ยืนยัน RNG replication
- เพิ่ม config/run manifest
- ทำ food-value confirmatory multi-seed

ผลลัพธ์ที่ควรได้:

- ผล food-value learning ที่มี seed variance
- confidence interval หรืออย่างน้อย mean/range
- claim individual learning แข็งขึ้น

### ช่วง 2: Action-value learning

เป้าหมาย:

- สร้าง DQN-lite/Q-value policy สำหรับ food/action
- เพิ่ม encounter telemetry
- ทำ memory-disabled/shuffled controls

ผลลัพธ์ที่ควรได้:

- agent เลือก action จาก learned consequence ชัดขึ้น
- ตอบได้ว่า behavior ไม่ใช่ script หรือ aggregate artifact

### ช่วง 3: Delayed consequence และ skill emergence

เป้าหมาย:

- world-model seed placement
- tool-use ROI
- skill sequence memory

ผลลัพธ์ที่ควรได้:

- เริ่มแยก learned resource management จาก hunger-driven side effect
- มี evidence สำหรับ reusable behavior

### ช่วง 4: Evolution and transmission

เป้าหมาย:

- population stability
- endogenous mutation
- parent-child / social transmission
- communication/proto-language เฉพาะหลัง social learning ผ่าน

ผลลัพธ์ที่ควรได้:

- transition จาก individual learning ไป cross-generation dynamics
- claim evolution มีหลักฐานจริงมากขึ้น

---

## 10. สรุปเชิงยุทธศาสตร์

paper ทั้งหมดไม่ได้บอกให้เรา "ทำ ChatGPT ในซิม" แต่ให้แผนที่ว่า agent ที่ดูเหมือนเลือกเองต้องมีองค์ประกอบอะไร:

1. state/observation
2. action space
3. consequence/reward
4. memory หรือ value estimate
5. policy ที่เปลี่ยนตามประสบการณ์
6. evaluation ที่แยก true learning ออกจาก artifact
7. ablation ที่หักล้างคำอธิบายทางเลือก
8. ถ้าต้องการ evolution ต้องมี reproduction, inheritance, mutation, selection และ population stability

โปรเจกต์ Artificial Evolution มีฐานที่ดีมากแล้ว เพราะมีโลก, resource, energy, memory, tools, family, telemetry และ negative-result discipline สิ่งที่ควรทำต่อไม่ใช่เพิ่มความซับซ้อนทันที แต่คือทำให้ "การเลือกเอง" วัดได้เข้มขึ้น:

- จาก food-value memory ไป action-value policy
- จาก aggregate graph ไป encounter-level causal trace
- จาก seed causality ไป learned site selection
- จาก tool existence ไป tool-use ROI
- จาก lineage tracking ไป endogenous mutation-selection
- จาก social structure ไป social transmission test

หากทำตามลำดับนี้ paper set ที่รวบรวมมาจะกลายเป็น backbone ของงานวิจัยได้จริง ทั้งในรายงานประกวดและในแผนพัฒนาระยะยาว โดยยังรักษาจุดแข็งสำคัญของโปรเจกต์ไว้คือ ไม่สอนความหมายสำเร็จรูป ไม่ใช้ oracle และไม่อ้างเกินหลักฐาน

---

## 11. References และแหล่งอ้างอิงใน repo

### Paper set ใน `papers/`

- `01_Attention_Is_All_You_Need.pdf`
- `05_Language_Models_are_Few_Shot_Learners_GPT3.pdf`
- `07_Fine_Tuning_Language_Models_from_Human_Preferences.pdf`
- `10_InstructGPT_Training_LMs_to_Follow_Instructions_with_Human_Feedback.pdf`
- `12_Constitutional_AI_Harmlessness_from_AI_Feedback.pdf`
- `14_Direct_Preference_Optimization_DPO.pdf`
- `16_ReAct_Synergizing_Reasoning_and_Acting_in_Language_Models.pdf`
- `17_Toolformer_Language_Models_Can_Teach_Themselves_to_Use_Tools.pdf`
- `19_Reflexion_Language_Agents_with_Verbal_Reinforcement_Learning.pdf`
- `20_Voyager_Open_Ended_Embodied_Agent_with_LLMs.pdf`
- `22_OpenAI_o1_System_Card.pdf`
- `24_DeepSeek_R1_Incentivizing_Reasoning_Capability_in_LLMs.pdf`
- `26_Human_Level_Control_through_Deep_Reinforcement_Learning_DQN.pdf`
- `27_AlphaGo_Zero_Mastering_the_Game_of_Go_without_Human_Knowledge.pdf`
- `28_AlphaZero_Mastering_Chess_and_Shogi_by_Self_Play.pdf`
- `29_MuZero_Mastering_Atari_Go_Chess_and_Shogi_by_Planning.pdf`
- `1803.10122v4.pdf`
- `1901.08706v2.pdf`
- `2302.14276v1.pdf`
- `2501.00226v2.pdf`
- `siggraph94.pdf`

### เอกสารในโปรเจกต์

- `docs/CURRENT_STATE.md`
- `docs/PROJECT_OVERVIEW.md`
- `docs/WORLD_RULES.md`
- `reports/project_status_full_2026-06-20.md`
- `reports/agent_food_value_individual_tracking_2026-06-23.th.md`
- `reports/competition_full_report_artificial_evolution_2026-06-24.th.md`
- `papers/00_READING_ORDER.md`
- `papers/sumery.md`

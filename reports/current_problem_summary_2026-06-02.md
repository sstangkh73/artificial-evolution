# รายงานฉบับที่ 1: สรุปปัญหาปัจจุบันของโครงการ Artificial Evolution

จัดทำเมื่อ: 2026-06-02

## 1. ขอบเขตที่อ่านและตรวจสอบ

รายงานฉบับนี้สรุปจากการอ่านงานใน `C:\artificial-evolution` โดยเน้นแหล่งข้อมูลต่อไปนี้

- โค้ดหลัก: `main.py`, `agents/agent.py`, `agents/body.py`, `world/environment.py`, `simulation/runner.py`, `simulation/research_artifacts.py`, `simulation/publication_artifacts.py`, `visualization/dashboard.py`
- เอกสารสถานะและกติกา: `docs/CURRENT_STATE.md`, `docs/STABILITY_INVESTIGATION_LOG.md`, `docs/BUG_IMPACT_LOG.md`, `docs/PHASE2_ROADMAP.md`, `docs/WORLD_RULES.md`, `docs/BODY_SYSTEM.md`, `docs/TRAIT_SPACE.md`, `docs/TECH_TREE.md`, `docs/WORLD_PHYSICS_V2.md`
- รายงานและ paper draft: `reports/paper_draft_2026-05-11/*`, `phase1_report/*`, โดยเฉพาะรายงานที่ปรึกษาและ update progress ล่าสุด
- ผลทดลอง: `data/experiment_history.json`, `data/update_progress_log.*`, `data/latest_experiment_snapshot_2026-05-20.md`, `data/long_loop_iteration_01.*`, `data/long_loop_iteration_02_active_nest_support.*`, `data/founder_opt_250_*`, `data/publication_packages/experiment_047_publication_batch`, `data/publication_packages/experiment_048_robustness_sweep`
- ไฟล์นอกแกน artificial-evolution เช่น `tmp_patch_lifespayback*.py`, `tmp_patch_distortium_save.py`, `utmt_*.csx`, `bodysmith_*` ถูกอ่านแบบจำแนกหมวดแล้ว พบว่าเป็นงาน patch/save-edit หรือ GameMaker/UTMT คนละสายกับปัญหา simulation หลัก จึงไม่นำมาใช้เป็นหลักฐานของคอขวด artificial-evolution

หมายเหตุ: โฟลเดอร์นี้ไม่ใช่ git repository ในสถานะปัจจุบัน (`git status` รายงานว่าไม่มี `.git`) ดังนั้นรายงานนี้ยึดจากไฟล์และ artifact ที่มีใน workspace เป็นหลัก

## 2. สรุปสั้นที่สุด

ปัญหาปัจจุบันไม่ได้อยู่ที่ระบบ "ไม่มีการเกิดลูก" หรือ "ไม่มีอาหารเลย" แต่ติดที่ระบบยังไม่สามารถแปลงอาหาร รัง เสบียง household storage และเด็กที่โตแล้ว ให้กลายเป็น replacement rate ที่พอจะรักษาประชากรไว้ได้ต่อเนื่อง

พูดให้ตรงที่สุดคือ:

> ระบบสร้าง lineage ได้, ไปถึงรุ่นลึกได้บาง seed, มี storage ได้, มี settlement ได้, มีเทคโนโลยีได้ แต่ยังไม่ self-sustain และยังสูญพันธุ์ในที่สุด

คอขวดหลักจึงเป็น conversion problem ระหว่างทรัพยากรกับความต่อเนื่องของประชากร ไม่ใช่ scarcity problem แบบง่าย ๆ

## 3. สถานะของระบบที่ทำได้แล้ว

ระบบปัจจุบันก้าวไกลกว่า README และเอกสาร architecture บางฉบับ โดยมีองค์ประกอบสำคัญแล้วดังนี้

- โลก `100x100` แบ่ง 4 zone: safe/food-rich, safe/food-poor, danger/food-rich, danger/food-poor
- day/night, seasons, food pressure, fertility, large-animal herds
- body budget `TOTAL_BODY_COST = 100` พร้อม morphology: sensor, muscle, armor, brain
- trait space ต่อเนื่อง เช่น memory, planning, cooperation, parenting, fear, aggression, metabolism, diet efficiency, reproduction drive/investment
- life stages: child, juvenile, adult, old
- sexed reproduction, parent id, other parent id, lineage id
- การสืบทอด body plan ผ่าน `inherit_body_plan()` ใน `agents/body.py` และถูกเรียกจริงใน `Agent.spawn_child()` ใน `agents/agent.py`
- household, shared home, nest, food storage, material storage, withdrawal, breeder-priority allocation
- social roles, cooperation, child support, caretaker/protector logic
- tools/materials/hearth/World Physics V2
- research-grade telemetry, dashboard, publication package, negative results, figure source data

จุดสำคัญ: เอกสารบางไฟล์ยังบอกว่า continuous trait mutation หรือ endogenous evolution ยังไม่เกิด แต่โค้ดมีการ mutate/inherit traits แล้วจริง อย่างไรก็ตาม ปัญหายังอยู่ที่ mutation loop ยังไม่ถูกพิสูจน์ว่าเพียงพอสำหรับ open-ended self-sustaining evolution และผลสำเร็จจำนวนมากใน Phase 1 ยังพึ่ง external search/variant expansion

## 4. หลักฐานสำคัญจากผลทดลอง

### 4.1 Phase 1 สำเร็จในระดับ lineage-capable search

รายงาน Phase 1 และ `data/massive_lineage_search.md` ระบุว่า body ที่เด่นคือ:

- `body_8`: `sensor=0, muscle=0, armor=1, brain=3, profile=social_planner`
- `body_14`: `sensor=0, muscle=0, armor=1, brain=3, profile=nurturing_settler`

ผล Phase 1 สำคัญมาก เพราะพิสูจน์ว่าระบบไม่ได้ล้มเหลวตั้งแต่ระดับพื้นฐาน ร่างกายบางกลุ่มสร้าง births และ matured children ได้จำนวนมาก และได้ body types ที่สืบรุ่นได้ครบตามเป้าหมายใน Experiment 31

ข้อจำกัดของผลนี้คือความสำเร็จกระจุกใน morphology corridor แคบมาก: low sensor, low muscle, armor 1, brain 3 แล้วใช้ trait profile แบบ social/planner หรือ nurturing/settler เป็นตัวทำให้รอด

### 4.2 Sexed reproduction ไปถึง gen3 ได้ แต่ยังไม่ robust

จาก paper draft และ publication batch:

- `sexed_gen3_body_8`: ไปถึง generation 3 ได้ `2/6` seeds
- `sexed_gen3_body_14`: ไปถึง generation 3 ได้ `1/6` seeds
- robustness sweep บาง condition ไปถึง gen3 เพียง `1/4` หรือ `0/4`

นี่แปลว่า sexed reproduction chain ไม่ได้เป็นไปไม่ได้ แต่ยังเปราะมาก และเมื่อ food pressure เพิ่มขึ้น ความสำเร็จตกลงทันที

### 4.3 Long-loop ไปได้ลึก แต่ยังสูญพันธุ์ทุก run

`data/long_loop_iteration_01.md` และ `.json` เป็นหลักฐานที่แรงที่สุดของปัญหาปัจจุบัน:

- body: `body_14`
- population: `250`
- seeds: `7-16`
- max ticks: `20000`
- success/non-extinct runs: `0/10`
- บาง seed ไปถึง gen `24-25`
- บาง seed มี stored food สูงมาก เช่น `38050`, `37817`, `42373`
- แต่ final population เป็น `0` ทุก run
- death reason หลักยังเป็น `energy_depleted` จำนวนมาก

นี่คือ paradox สำคัญ: ระบบมี generation depth และ stored food สูง แต่ประชากรยังตายหมด แปลว่าปัญหาไม่ใช่แค่อาหารไม่พอ แต่เป็นอาหาร/เสบียงไม่ถูกใช้เพื่อรักษา breeder throughput และ population continuity ให้พอ

อีกการตีความที่สำคัญคือ ระบบอาจกำลังสร้าง `wealth` แต่ไม่ได้สร้าง `offspring` กล่าวคือ settlement และ storage อาจสะสมทรัพยากรได้จริง แต่ fertility/replacement rate ยังต่ำกว่าเส้นที่ทำให้ประชากรแทนตัวเองได้ เหมือนระบบประชากรจริงที่มีทรัพยากรและความมั่งคั่ง แต่ fertility ต่ำกว่า replacement จนประชากรลดลงในระยะยาว

### 4.4 Best current stability intervention คือ breeder-priority household allocation

จาก `data/founder_opt_250_breeder_priority_comparison.md/json`:

- baseline mean max generation: `6.6`
- household redesign: `5.8`
- adult withdrawal fix: `5.1`
- breeder-priority allocation: `7.5`
- mean matured children เพิ่มเป็น `145.0`
- non-extinct runs ในช่วงทดสอบสั้นเพิ่มเป็น `8/10`

นี่บอกว่า "ใครได้สิทธิ์ดึงอาหารจาก household storage" สำคัญมาก โดยเฉพาะ adult female ที่พร้อมสืบพันธุ์ ไม่ใช่แค่ปริมาณอาหารรวมในระบบ

### 4.5 Branch ล่าสุดถอยลงใน benchmark body_8

`data/latest_experiment_snapshot_2026-05-20.md` ระบุ benchmark ล่าสุด:

- current branch exploratory
- body: `body_8`
- population: `50`
- seeds: `8010, 8012, 8014, 8016`
- extinctions: `4/4`
- mean final tick: `154.0`
- mean births: `6.5`
- mean matured children: `1.0`
- mean stored food total: `2.75`

ตัวเลขนี้ไม่ควรเอาไปเทียบตรง ๆ กับ founder 250 body14 track เพราะคนละ body, คนละ population, คนละ seed, คนละ max_ticks แต่สะท้อนว่า branch ล่าสุดยังไม่ผ่าน non-extinction และ reproduction/storage pipeline ตื้นมากใน benchmark นี้

## 5. คอขวดที่น่าจะติดจริง

### 5.1 Replacement rate หลัง gen1 ต่ำเกินไป

ระบบมักสร้าง gen1 ได้ แต่ gen1/gen2 ไม่กลายเป็น adult breeder ต่อเนื่องพอ หรือมี adult แล้วแต่ไม่พร้อมสืบพันธุ์พร้อมกันทั้งเงื่อนไข energy, mate, nest food, nest proximity, health และ cooldown

ตัวชี้วัดที่ควรดูต่อ:

- adult female count ต่อ generation
- eligible female count ต่อ tick
- ratio: matured children / births
- ratio: births per adult female per generation
- reason distribution จาก `repro_fail`

### 5.2 Reproduction opportunity ต่อ female lifetime อาจต่ำเกินไป

ประเด็นนี้ต่างจากคำถามว่า female พร้อมมีลูกใน tick หนึ่งหรือไม่ เพราะแม้ female จะผ่าน gate ได้บางช่วง แต่ถ้าทั้งชีวิตมี opportunity window จริงเพียง 1 ครั้ง replacement rate ก็อาจไม่มีทางถึง 1

ตัวอย่างเชิงกลไก:

- ช่วง adult ตามทฤษฎีมีหลายสิบ tick
- แต่เวลาจริงถูกกินโดยหาอาหาร เดินกลับรัง หา mate เลี้ยงลูก cooldown/recovery และหลบอันตราย
- สุดท้าย female หนึ่งตัวอาจมีโอกาส reproduction จริงเพียง 1 ครั้ง
- ถ้า litter size, maturation rate และ female offspring ratio ไม่ชดเชย โครงสร้างประชากรจะ decline แม้ stored food จะสูง

metric ที่ควรเพิ่ม:

- `reproduction_opportunities_per_female_lifetime`
- `distinct_opportunity_windows`
- `actual_births_per_opportunity_window`
- `matured_female_offspring_per_adult_female`
- `adult_alive_ticks`, `near_nest_ticks`, `mate_available_ticks`, `cooldown_blocked_ticks`, `full_ready_ticks`

เกณฑ์ที่ควรระวัง:

- ถ้า opportunity windows เฉลี่ยต่ำกว่า `2` ต่อ female lifetime ระบบน่าจะติด fertility ceiling
- ถ้า stored food สูงแต่ opportunity ต่ำ แปลว่าระบบสร้าง wealth แต่ไม่ได้สร้าง offspring
- ถ้า opportunity สูงแต่ births ต่ำ ค่อยกลับไปดู gate เช่น energy, nest food, mate, cooldown หรือ child survival

### 5.3 Energy depletion ยังชนะ stored food

ใน long-loop บางรอบ stored food สูงมาก แต่ยังมี `energy_depleted` deaths จำนวนมาก แปลว่าอาหารอยู่ในระบบแต่ไม่เข้าถึง agent ที่ต้องใช้ในเวลาที่ถูกต้อง

จุดโค้ดที่เกี่ยวข้อง:

- `Agent._store_surplus_food()`
- `Agent._withdraw_nest_food_if_needed()`
- `Agent._nest_owner_id()`
- `Environment.store_food_in_nest()`
- `Environment.withdraw_food_from_nest()`

### 5.4 Household owner / shared home / nest access ยังเป็นกลไกเสี่ยง

เอกสาร bug log ยืนยันว่า household continuity เคยเป็น critical bug และแก้แล้วส่วนหนึ่ง แต่ stability log ยังชี้ว่า adult withdrawal alignment ช่วยบาง seed มากและ breeder-priority allocation ช่วยดีที่สุด จึงยังควรถือว่า household ownership/access เป็นกลไกกลางของปัญหา

ความเสี่ยงคือ agent อาจ:

- reproduce โดยอิง nest หนึ่ง
- store food เข้า nest หนึ่ง
- withdraw emergency food จากอีก owner id หรือไม่มีสิทธิ์ถอน
- โตเป็น adult แล้วหลุดจาก family/shared-home graph

### 5.5 Nest support และ nest seeding อาจกำลังบิดเศรษฐกิจ

ใน `world/environment.py`:

- `build_nest()` ตั้ง `food_storage=18` ให้รังใหม่
- `_support_nests()` เพิ่ม food/material และ spawn food รอบ nest ตาม chance

นี่อาจทำให้ stored food สูงโดยไม่ใช่ productivity จริงของประชากรทั้งหมด แต่การตัด support แบบ active-nest-only กลับทำให้ long-loop แย่ลง จึงสรุปได้ว่า nest support inflation มีจริง แต่อาจเป็น scaffold ที่ระบบยังพึ่งอยู่ การเอาออกตรง ๆ ไม่ใช่คำตอบ

### 5.6 Settlement overshoot แก้แบบแข็งไม่ได้

การกด nest reuse / settlement spacing อย่าง aggressive ทำให้ collapse หนัก:

- mean max generation เหลือ `1.0`
- matured children เฉลี่ยเหลือ `1.4`

แปลว่าปัญหาไม่ได้แก้ด้วยการห้ามสร้างรังใหม่แบบตรง ๆ เพราะรังใหม่อาจเป็นส่วนหนึ่งของ household formation pipeline

### 5.7 Hard reproduction cooldown กดระบบแรงเกินไป

anti-cohort patch ลด cohort boom ได้ แต่กด births ลงมากจน extinction `10/10` และ mean max generation เหลือ `2.5`

สรุปคือ cohort synchronization อาจเป็นปัญหาจริง แต่ไม่ควรแก้ด้วย cooldown แข็ง ควรใช้กลไกนุ่มกว่า เช่น recovery cost, age/fertility window, local child-load cost, pair-bond timing หรือ seasonal fertility

### 5.8 Technology emergence ยังเร็วเกินไป แต่เป็นปัญหารองจาก non-extinction

publication/robustness packages ชี้ว่า technology เกิดได้จริง และ harsh environments ชะลอได้บ้าง แต่ยังเกิดในหลัก tick ต้น ๆ ถึงหลักสิบ ทำให้ยังอ้างไม่ได้ว่าเป็น pressure-driven late innovation

อย่างไรก็ตาม ถ้าเป้าหมายตอนนี้คือ self-sustaining population ปัญหา technology timing เป็นปัญหารอง เว้นแต่ tools/hearth/physics กำลังไปรบกวน energy economy หรือทำให้ branch ล่าสุดถอย

## 6. สิ่งที่ไม่น่าใช่คำตอบหลักในตอนนี้

- เพิ่ม founder population อย่างเดียว เพราะ founder 250 ช่วยให้ลึกขึ้น แต่ long-loop ยังตายหมด
- ลด world difficulty เพราะ goal ชัดเจนว่าต้องไม่ลดความยากของโลก
- hard cooldown เพื่อแก้ cohort boom เพราะเคยทำให้ regression
- aggressive nest reuse/spacing suppression เพราะเคยฆ่า reproduction pipeline
- active-nest-only support filtering แบบตรง ๆ เพราะลด surplus หลอกแต่ไม่สร้าง self-sustain
- naive nest inheritance transfer เพราะ probe collapse แถว gen2
- adult withdrawal alignment แบบ simple fix อย่างเดียว เพราะผล mixed

## 7. จุดที่เอกสารกับโค้ดยังไม่ตรงกัน

- `docs/SIMULATION_ARCHITECTURE.md` ยังเขียนเหมือน reproduction/mutation เป็น future work บางส่วน ทั้งที่โค้ดมี sexed reproduction และ `inherit_body_plan()` แล้ว
- `docs/TRAIT_SPACE.md` บอกว่ายังไม่มี continuous trait mutation แต่ `agents/body.py` มี `TRAIT_MUTATION_STEPS` และ mutation rate ใน `inherit_body_plan()`
- `README.md` ยังสรุปโปรเจกต์ระดับ minimal survival simulation ทั้งที่ระบบจริงมี household, tools, physics, publication package แล้ว
- `docs/REAL_WORLD_ASSUMPTIONS.md` บอกว่ามี terrain ไม่ traversable แต่ `Environment.is_walkable()` ตอนนี้เช็กแค่ขอบเขต map

ข้อเสนอ: ให้ถือ `docs/CURRENT_STATE.md`, `docs/STABILITY_INVESTIGATION_LOG.md`, `docs/BUG_IMPACT_LOG.md`, โค้ดหลัก และ `data/update_progress_log.*` เป็น source of truth ล่าสุด มากกว่า README/architecture รุ่นเก่า

## 8. สรุปปัญหาในรูปประโยควิจัย

คำถามปัจจุบันควรถูกเขียนใหม่เป็น:

> ภายใต้โลกเดิมที่ไม่ลดความยาก ระบบ household economy, breeder allocation, settlement productivity และ spatial/social continuity แบบใดที่จะทำให้ replacement rate มากพอจนประชากร self-sustain ได้เกิน long-horizon โดยไม่พึ่ง external search หรือ resource inflation ที่บิดผล?

## 9. ข้อสรุปสุดท้าย

ผมคิดว่าตอนนี้ติดอยู่ที่ "ประชากรไม่สามารถปิดวงจรชีวิตให้ทบต้นได้" ไม่ใช่ติดที่ "ยังไม่มีระบบวิวัฒนาการเลย" และไม่ใช่ "อาหารไม่มีพอ" อย่างเดียว

กลไกที่ต้องแก้ต่อควรโฟกัส 4 อย่างพร้อมกัน:

1. ใครได้อาหารจาก household storage เมื่อไร
2. female หนึ่งตัวมี reproduction opportunity จริงกี่ครั้งต่อชีวิต
3. เด็ก/juvenile/new adult ถูกส่งต่อไปเป็น breeder ได้ต่อเนื่องแค่ไหน
4. settlement สร้าง productivity จริงหรือแค่สร้าง stored-food artifact
5. spatial/mate/household graph ทำให้ adult ที่พร้อมสืบพันธุ์เจอกันและใช้รังเดียวกันได้หรือไม่

แนวทางที่ควรเดินต่อไม่ใช่ rewrite ใหญ่ แต่เป็น controlled experiments บน baseline เดียวกัน โดยเฉพาะ body_14 founder 250 long-loop seeds 7-16 และ current branch body_8 benchmark เพื่อแยกว่า regression ล่าสุดมาจาก body/population/branch หรือจากกลไกใหม่จริง

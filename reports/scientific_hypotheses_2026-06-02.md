# รายงานฉบับที่ 2: สมมุติฐาน 11 ทางในการแก้ปัญหาแบบวิธีวิทยาศาสตร์

จัดทำเมื่อ: 2026-06-02

## 1. ปัญหาวิจัย

ระบบ Artificial Evolution สามารถสร้าง births, matured children, settlement, storage, lineage depth และ emergent technology ได้แล้ว แต่ยังไม่สามารถทำให้ประชากร self-sustain หรือ non-extinction ได้อย่าง robust โดยไม่ลดความยากของโลก

โจทย์ทดลองหลัก:

> อะไรคือกลไกที่ทำให้ทรัพยากรและ settlement economy แปลงเป็น replacement rate ไม่พอ และ intervention แบบใดทำให้ประชากรรอดต่อเนื่องโดยไม่ลด world difficulty?

## 2. หลักการทดลองร่วม

ให้ใช้ baseline และตัวชี้วัดเดียวกันก่อน แล้วค่อยเปลี่ยนตัวแปรต้นทีละชุด

Baseline แนะนำ:

- Track A: `body_14`, founder population `250`, seeds `7-16`, max_ticks `20000`, no target-survivor early stop
- Track B: `body_8`, population `50`, seeds `8010, 8012, 8014, 8016`, max_ticks `4000` เพื่อเทียบ current branch exploratory
- Track C: publication-style sexed condition `25 male + 25 female`, body `8` และ `14`, seeds อย่างน้อย `12` seeds

ตัวแปรควบคุม:

- world size, zone profiles, day length, season length
- body index และ founder sex composition ภายใน track เดียวกัน
- max_ticks, seed set, spawn strategy
- ไม่ลด world difficulty เช่นไม่เพิ่ม global food แบบตรง ๆ ในการทดสอบหลัก

ตัวแปรตามหลัก:

- `non_extinct_runs`
- `final_population`
- `final_tick`
- `mean_max_generation`
- `total_births`
- `matured_children`
- `matured_children / total_births`
- adult female count ต่อ generation
- eligible female count ต่อ tick
- `energy_depleted` deaths
- reproduction failure reasons: `low_energy`, `nest_food_low`, `no_mate`, `not_near_nest`, `cooldown`, `low_durability`
- reproduction opportunities per female lifetime
- distinct reproduction opportunity windows per adult female
- actual births per opportunity window
- female offspring matured per adult female lifetime
- `stored_food_total` และ stored food per active household
- number of active nests, abandoned nests, nest ownership aliases

เกณฑ์ความสำเร็จเบื้องต้น:

- Long-loop: non-extinct อย่างน้อย `3/10` ที่ max_ticks `20000` โดยไม่ลด world difficulty
- หรือถ้ายังไม่ถึง non-extinction ต้องเพิ่ม mean final tick, mean max generation, matured children และลด energy-depleted deaths แบบมีนัยสำคัญโดยไม่สร้าง stored-food inflation หลอก

## 3. สมมุติฐาน 10 ทาง

### สมมุติฐานที่ 1: ปรับ breeder-priority household allocation จะเพิ่ม replacement rate

ข้อสังเกต:

Breeder-priority household allocation เป็น intervention ที่ดีที่สุดใน stability track ปัจจุบัน เพิ่ม mean max generation เป็น `7.5`, matured children เป็น `145.0`, และ non-extinct runs ระยะสั้นเป็น `8/10`

สมมุติฐาน:

ถ้าปรับค่าคงที่ของ breeder-priority ให้ละเอียดขึ้น เช่น reserve, withdrawal amount, threshold และ timing ระบบจะเพิ่ม adult female throughput และลด `low_energy` reproduction failures โดยไม่ทำให้ child starvation เพิ่มขึ้น

ตัวแปรต้น:

- `BREEDER_NEST_FOOD_RESERVE`
- `GENERAL_NEST_FOOD_RESERVE`
- `CRITICAL_ADULT_WITHDRAW_ENERGY`
- max withdrawal per tick สำหรับ breeder
- personal energy floor ของ adult female ก่อน store surplus

ตัวแปรตาม:

- eligible adult female count
- births per adult female
- `low_energy` reproduction failures
- `energy_depleted` deaths แยก child/adult/female
- non-extinct runs

วิธีทดลอง:

ทำ factorial sweep ขนาดเล็ก เช่น reserve `6/10/14`, withdrawal cap `12/18/24`, adult critical energy `24/28/34` บน seeds เดิม

คำทำนาย:

ค่าที่เหมาะจะเพิ่ม births และ matured children โดยไม่ลด stored-food buffer จนเด็กตาย

เกณฑ์ยืนยัน:

ผ่านถ้า mean matured children เพิ่มมากกว่า baseline S4 อย่างน้อย 15% และ `energy_depleted` adult female ลดลง โดย non-extinct long-loop เพิ่มขึ้น

### สมมุติฐานที่ 2: household owner resolution ยังทำให้อาหารติดผิดรัง

ข้อสังเกต:

เคยมี household continuity bug รุนแรง และ adult withdrawal alignment ช่วยบาง seed มาก แม้ไม่ใช่คำตอบสุดท้าย

สมมุติฐาน:

ถ้า agent resolve household owner แบบ canonical เดียวกันสำหรับ reproduction, store, withdraw, child support และ shared-home update จะลดกรณี stored food สูงแต่ agent ตายจาก energy depletion

ตัวแปรต้น:

- วิธีเลือก owner id ใน `_nest_owner_id()`
- alias resolution ใน `Environment.resolve_nest_owner()`
- shared-home propagation จาก parent/mate/child
- policy ว่า adult child ใช้ parent nest, mate nest หรือ self nest เมื่อใด

ตัวแปรตาม:

- mismatch count: reproduce nest != store nest != withdraw nest
- failed withdrawal despite nearby stored food
- stored food per household owner
- `nest_food_low` และ `low_energy` failures
- final population

วิธีทดลอง:

เพิ่ม telemetry ก่อน: log `repro_owner_id`, `store_owner_id`, `withdraw_owner_id`, `nest_position`, `shared_home_owner_id` ต่อ agent แล้วรัน baseline เดิม จากนั้นทดสอบ canonical owner policy 2-3 แบบ

คำทำนาย:

ถ้าสมมุติฐานถูก ต้องพบ mismatch สูงใน run ที่ collapse และ policy ที่ลด mismatch จะเพิ่ม final tick/eligible breeders

เกณฑ์ยืนยัน:

ผ่านถ้า owner mismatch ลดลงมากกว่า 50% และ `energy_depleted` ใน adult/juvenile ใกล้รังลดลงโดยไม่ลด births

### สมมุติฐานที่ 3: juvenile และ newly-adult pipeline คือคอขวดจริง ไม่ใช่เฉพาะ current breeder

ข้อสังเกต:

juvenile/young-adult priority เคยช่วยบาง deep seeds แต่ยังไม่ outperform best breeder-priority state

สมมุติฐาน:

ถ้าให้ priority แบบนุ่มแก่ juveniles และ newly-adult agents เฉพาะช่วงก่อน/หลัง adult age จะเพิ่ม pool ของ next-generation breeders โดยไม่แย่งอาหารจาก current breeders มากเกินไป

ตัวแปรต้น:

- age window ของ pipeline support เช่น age `45-75`
- energy threshold สำหรับ juvenile/new adult withdrawal
- share ratio ระหว่าง breeder priority กับ pipeline priority
- local child-load multiplier

ตัวแปรตาม:

- juvenile-to-adult survival rate
- adult_generation_counts ต่อ generation
- adult female count gen2+
- births ใน generation ถัดไป
- child/juvenile `energy_depleted` deaths

วิธีทดลอง:

ทดสอบ pipeline support แบบ soft cap: ให้ถอนอาหารได้เฉพาะเมื่อ nest food เหนือ reserve และ energy ต่ำกว่า percentile ที่กำหนด

คำทำนาย:

รุ่นถัดไปควรมี adult breeder มากขึ้น และ late-run collapse ควรถูกเลื่อนออกไป

เกณฑ์ยืนยัน:

ผ่านถ้า adult gen2+ count เพิ่มขึ้นและ mean max generation เพิ่มขึ้นโดย breeder births ไม่ลดลงเกิน 5%

### สมมุติฐานที่ 4: mate fragmentation และ spatial drift ทำให้ adult พร้อมสืบพันธุ์แต่หา mate/nest ไม่เจอ

ข้อสังเกต:

ระบบมีเงื่อนไข mate ต้องเป็น adult male ใกล้ `SAFE_RADIUS` และต้องใกล้ nest ถ้า settlement/lineage กระจายตัวผิดจังหวะ อาจมี adult พร้อมสืบพันธุ์แต่ไม่เจอกัน

สมมุติฐาน:

ถ้าเพิ่ม pair-bond continuity, mate-search behavior หรือ settlement rendezvous สำหรับ adult agents จะลด `no_mate` และ `not_near_nest` failures และเพิ่ม reproduction continuity

ตัวแปรต้น:

- mate search radius
- pair-bond memory duration
- home-return priority ของ adult males/females
- rendezvous interval ใกล้ nest
- local group formation radius

ตัวแปรตาม:

- `no_mate` reproduction failures
- adult male/female distance distribution
- percent adult females near nest with mate
- births per tick/generation
- final tick และ final population

วิธีทดลอง:

ก่อนแก้ให้เก็บ telemetry ระยะห่าง adult female ถึง nearest adult male และ nearest nest ทุก tick จากนั้นทดลองเพิ่ม mate-home rendezvous เฉพาะ adult stage

คำทำนาย:

ถ้า spatial fragmentation เป็นปัญหา ตัวชี้วัด `no_mate`/`not_near_nest` จะลดชัด และ births กระจายสม่ำเสมอขึ้น

เกณฑ์ยืนยัน:

ผ่านถ้า `no_mate` failures ลดลงมากกว่า 30% และ total births/matured children เพิ่มขึ้นโดยไม่เพิ่ม death จาก danger zone

### สมมุติฐานที่ 5: cohort synchronization ทำให้เกิด wave collapse แต่ hard cooldown แก้แรงเกินไป

ข้อสังเกต:

anti-cohort hard cooldown ทำให้ births collapse และ extinction 10/10 แต่ cohort collapse อาจยังเป็นกลไกจริง

สมมุติฐาน:

ถ้าใช้ fertility/recovery แบบต่อเนื่องแทน hard cooldown จะลด population wave collapse โดยไม่กด births จนต่ำเกินไป

ตัวแปรต้น:

- reproduction recovery curve
- fertility window ตาม age
- postpartum energy recovery
- local child-load cost
- seasonal fertility multiplier แบบไม่เพิ่มอาหาร

ตัวแปรตาม:

- births variance ต่อ tick
- cohort age distribution
- population trough depth
- mean births และ matured children
- extinction timing

วิธีทดลอง:

เปรียบเทียบ 3 แบบ: no extra cooldown, hard cooldown เดิม, soft recovery/fertility curve

คำทำนาย:

soft recovery จะลด boom-bust variance แต่ยังรักษา total births ใกล้ S4

เกณฑ์ยืนยัน:

ผ่านถ้า births variance ลดลงและ final tick เพิ่ม โดย total births ไม่ลดลงเกิน 10% จาก S4

### สมมุติฐานที่ 6: nest seeding และ nest support สร้าง surplus หลอก แต่ระบบยังพึ่ง scaffold นี้

ข้อสังเกต:

รังใหม่เริ่มด้วย `food_storage=18` และ `_support_nests()` เติมอาหาร/วัสดุ/food spawn รอบรัง แต่ active-nest-only support filtering ทำให้ผลแย่ลง

สมมุติฐาน:

ถ้าเปลี่ยน nest support จาก "ฟรีตามจำนวนรัง" เป็น "earned support ตาม active labor/managed patch/hearth" แบบค่อยเป็นค่อยไป จะลด stored-food artifact และเพิ่ม productivity จริงโดยไม่ทำให้ scaffold หายทันที

ตัวแปรต้น:

- initial nest food: `0/6/12/18`
- nest support chance
- support condition: active occupancy, caretaker labor, managed patch, material input
- decay rate ของ stored food หรือ abandoned nest

ตัวแปรตาม:

- stored food from nest seeding/support vs gathered/stored by agents
- active vs abandoned nest food
- energy-depleted deaths
- births/matured children
- long-loop non-extinction

วิธีทดลอง:

เริ่มจาก telemetry accounting แยก source ของ stored food จากนั้นทำ gradual support model ไม่ใช่ปิด support ทันที

คำทำนาย:

ถ้า scaffold บิดผลจริง จะเห็น stored food source มาจาก nest support สูง แต่ earned-support model ที่ดีควรรักษา survival ได้พร้อมลด inflation

เกณฑ์ยืนยัน:

ผ่านถ้า stored-food inflation ลดลง แต่ final tick/matured children ไม่ตกเกิน 10% และ energy-depleted deaths ลดใน late run

### สมมุติฐานที่ 7: settlement productivity ยังตื้นเกินไป ต้องมี food preservation/managed patch/storage upgrade

ข้อสังเกต:

ปัจจุบัน settlement มี storage และ hearth แต่ economy ยังไม่ทบต้นพอ เอกสาร phase2 ก็ระบุว่าขาด production chain และ infrastructure upgrades

สมมุติฐาน:

ถ้าเพิ่ม productivity ที่ต้องใช้ labor จริง เช่น food preservation, managed food patch, storage upgrade หรือ better cooking logistics settlement จะเปลี่ยนจาก buffer ชั่วคราวเป็นแหล่ง surplus ที่ค้ำ population ได้

ตัวแปรต้น:

- presence/absence ของ food preservation
- managed patch yield/decay
- storage capacity/upgrade cost
- labor cost ต่อ infrastructure
- spoilage rate

ตัวแปรตาม:

- net food surplus per active nest
- child survival
- breeder energy readiness
- `stored_food_total` ที่มาจาก labor
- non-extinct runs

วิธีทดลอง:

เพิ่ม feature ทีละอย่างแบบ conservative แล้ววัด source accounting ของ food และ labor cost ไม่ให้เป็น free resource

คำทำนาย:

settlement ที่ active ควรสร้าง food security สูงขึ้น ส่วน abandoned settlement ไม่ควรสะสมอาหารฟรี

เกณฑ์ยืนยัน:

ผ่านถ้า active nest productivity เพิ่ม births/matured children และลด extinction โดย stored food ไม่โตจาก abandoned nests

### สมมุติฐานที่ 8: energy/metabolism/lifespan balance ทำให้ adult breeder หมดพลังเร็วเกินไป

ข้อสังเกต:

death reason หลักใน long-loop คือ `energy_depleted` แม้มี stored food สูง และ adult female readiness เป็น control point สำคัญ

สมมุติฐาน:

ถ้าปรับ energy cost เฉพาะช่วง adult breeder ให้สะท้อน reproduction recovery และ role efficiency มากขึ้น จะลด breeder starvation โดยไม่ทำให้โลกง่ายขึ้นแบบเพิ่มอาหารตรง ๆ

ตัวแปรต้น:

- adult base drain modifier
- brain drain modifier สำหรับ high social/settler roles
- movement cost ใกล้ nest
- recovery cost หลัง reproduction
- old-age support burden

ตัวแปรตาม:

- adult female energy distribution
- adult male energy distribution
- breeder death reason
- reproduction readiness windows
- final population/final tick

วิธีทดลอง:

ทำ sensitivity analysis ของ drain/cost เฉพาะ role/stage แทนการเพิ่ม food spawn

คำทำนาย:

ถ้าพลังงาน adult เป็นคอขวดจริง การลด drain เฉพาะ role/stage จะเพิ่ม ready breeders โดยไม่ทำให้ food map overabundant

เกณฑ์ยืนยัน:

ผ่านถ้า adult `energy_depleted` deaths ลดลงและ births เพิ่ม โดย average food eaten ไม่เพิ่มแบบผิดปกติ

### สมมุติฐานที่ 9: endogenous mutation ต้องถูกใช้เป็น adaptive loop จริง ไม่ใช่แค่เกิด mutation แล้วหายไป

ข้อสังเกต:

โค้ดมี `inherit_body_plan()` และ mutation แล้ว แต่ Phase 1 success จำนวนมากยังมาจาก external search/trait variants

สมมุติฐาน:

ถ้าแยกและปรับ mutation regimes ให้ selection ภายในซิมรักษา trait ที่ช่วย household continuity ได้ จะเกิด adaptation ที่เพิ่ม non-extinction หรืออย่างน้อยเพิ่ม generation depth โดยไม่ต้อง external variant search

ตัวแปรต้น:

- trait mutation rate
- major trait mutation rate
- morphology mutation rate
- trait-only vs morphology-only vs combined mutation
- inheritance blending policy

ตัวแปรตาม:

- lineage survival by trait distribution
- mutation spread ใน generation traits
- morphology diversity
- max generation observed
- non-extinct runs

วิธีทดลอง:

รัน controlled mutation regimes บน same seeds และบันทึก `generation_traits.csv`, `lineages.csv`, `agent_outcomes.csv`

คำทำนาย:

trait-only mutation น่าจะช่วยก่อน morphology mutation เพราะ viability corridor แคบ ส่วน morphology mutation มากเกินไปอาจทำให้หลุดจาก corridor และล้ม

เกณฑ์ยืนยัน:

ผ่านถ้า mutation regime ใดเพิ่ม max generation/final tick อย่างสม่ำเสมอ และ trait distributions ของ surviving lineages shift ไปทาง reproduction/parenting/planning ที่เหมาะสม

### สมมุติฐานที่ 10: technology/hearth/material system ยังเกิดเร็วและอาจรบกวน energy economy

ข้อสังเกต:

technology emergence เกิดเร็วมากในหลาย condition และ World Physics V2/hearth อาจเพิ่ม behavior/cost/bonus ใหม่ที่ branch ล่าสุด body_8 ยังรับไม่ไหว

สมมุติฐาน:

ถ้าคุม cost/benefit/timing ของ technology และ hearth ให้เกิดหลัง settlement stability ขั้นต่ำ จะลด early energy distraction และทำให้ tools เป็น productivity booster ระยะกลางแทน noise ระยะต้น

ตัวแปรต้น:

- technology unlock threshold
- experiment_with_objects energy cost
- hearth maintenance cost/fuel benefit
- tool benefit magnitude
- minimum settlement/food buffer ก่อน technology behavior

ตัวแปรตาม:

- first technology tick
- early adult energy
- births before first technology
- tool productivity gain
- final tick/final population
- current branch body8 benchmark metrics

วิธีทดลอง:

ทำ ablation: technology off, hearth off, technology delayed, current settings แล้วเทียบ body8 current benchmark และ body14 long-loop

คำทำนาย:

ถ้าเทคโนโลยีรบกวน early survival การ delayed/unlocked-by-stability version จะเพิ่ม births/matured children ใน early phase และเลื่อน first technology tick ออกไป

เกณฑ์ยืนยัน:

ผ่านถ้า body8 C1 benchmark ดีขึ้นอย่างน้อย 25% ใน mean final tick หรือ matured children และ first technology tick ไม่เกิดเร็วเกินหลักสิบโดยไม่มี productivity base

### สมมุติฐานที่ 11: Reproduction Opportunity Bottleneck หรือโอกาสมีลูกต่อชีวิตต่ำเกินไป

ข้อสังเกต:

stored food สูงมากแต่ final population เป็น `0` เป็นสัญญาณที่น่ากลัว เพราะอาจแปลว่าระบบสร้าง wealth ได้ แต่ไม่ได้สร้าง offspring คล้ายระบบจริงที่มีทรัพยากรแต่ fertility ต่ำกว่า replacement rate จนประชากรหายไปในที่สุด

สมมุติฐานนี้แยกจากคำถามว่า "พร้อมมีลูกไหมใน tick นี้" เพราะปัญหาอาจอยู่ที่ "ทั้งชีวิตมีหน้าต่างให้มีลูกกี่ครั้ง" ถ้า adult female หนึ่งตัวมี reproductive life ตามทฤษฎีหลายสิบ tick แต่เวลาจริงถูกใช้ไปกับหาอาหาร เดินกลับรัง หา mate เลี้ยงลูก cooldown และ recovery จนเหลือ opportunity จริงเพียง 1 ครั้ง replacement rate อาจไม่มีทางถึง 1 แม้อาหารและ storage จะดีขึ้นแล้ว

สมมุติฐาน:

ถ้า `reproduction opportunities per female lifetime` เฉลี่ยต่ำกว่า `2` ระบบจะไม่สามารถ self-sustain ได้อย่าง robust แม้จะลด `low_energy`, `nest_food_low` หรือเพิ่ม stored food สำเร็จ เพราะ lifetime fertility ceiling ต่ำเกินไป

ตัวแปรต้น:

- adult reproductive span: ระยะจาก adult age ถึง old/death age ที่ยังสืบพันธุ์ได้จริง
- travel time ระหว่าง food source, nest และ mate
- child-care duration และ child-load penalty
- reproduction cooldown/recovery
- mate search time
- nest return priority
- litter size และ sex ratio
- fertility window หรือ age-specific fertility policy

ตัวแปรตาม:

- adult female lifetime ticks
- reproductive-age female alive ticks
- opportunity ticks: tick ที่ female adult มีเงื่อนไขพื้นฐานใกล้ครบ เช่น alive, adult, healthy, near nest หรือ reachable nest, mate reachable, cooldown ไม่ล็อกยาว
- full-ready ticks: tick ที่ `can_reproduce()` จะผ่านทุก gate
- distinct opportunity windows: นับช่วงโอกาสเป็น event ไม่ใช่นับทุก tick ติดกันเป็นหลายครั้ง
- actual births per adult female lifetime
- actual births per opportunity window
- matured offspring per adult female lifetime
- matured female offspring per adult female lifetime
- replacement ratio ประมาณ: `female_offspring_matured / adult_female`

วิธีทดลอง:

เพิ่ม telemetry ใน `simulation/runner.py` และ/หรือ `Agent.reproduction_debug` เพื่อบันทึกข้อมูลรายตัวเมียตลอดชีวิต:

- `first_adult_tick`
- `death_tick`
- `adult_alive_ticks`
- `near_nest_ticks`
- `mate_available_ticks`
- `cooldown_blocked_ticks`
- `childcare_high_load_ticks`
- `full_ready_ticks`
- `opportunity_window_count`
- `birth_count`
- `matured_child_count`
- `matured_female_child_count`

นิยาม opportunity window แบบ operational:

- เริ่ม window เมื่อ female เป็น adult, alive, durability ผ่านขั้นต่ำ, มีหรือเข้าถึง nest ได้, และมี mate reachable ภายใน radius/route policy
- window จะถูกนับเป็น 1 ครั้งจนกว่าจะเกิด birth หรือเงื่อนไขหายไปเกิน N ticks
- full-ready tick เป็น metric แยก ไม่ควรใช้แทน opportunity ทั้งหมด เพราะ full-ready ต่ำอาจบอกว่า gate เข้ม แต่ opportunity ต่ำบอกว่า lifespan economics พัง

ทำการวิเคราะห์ก่อนแก้:

1. วัดค่า opportunity windows ต่อ female lifetime ใน long-loop body14 seeds `7-16`
2. วัดค่าเดียวกันใน current branch body8 seeds `8010, 8012, 8014, 8016`
3. แยก female เป็น founder female, gen1 female, gen2+ female
4. เทียบ run ที่มี stored food สูงแต่ extinct กับ run ที่ stored food ต่ำแต่ extinct เร็ว

คำทำนาย:

ถ้าสมมุติฐานถูก ต้องพบว่า adult females จำนวนมากมี opportunity window จริงเฉลี่ยต่ำกว่า `2` หรือมี full-ready windows ต่ำมาก แม้บาง household จะมี stored food สูง และ population จะเคยมี births/matured children มาก่อน

การแก้ที่ควรทดลองหลังวัด:

- ลด travel waste ด้วย home-return/mate-rendezvous ที่ nest
- เพิ่ม pair-bond continuity เพื่อไม่ต้องหา mate ใหม่ทุก reproductive cycle
- ทำ child-care ให้ไม่กินช่วงชีวิต reproductive ทั้งหมด เช่น shared childcare หรือ juvenile caretaker role
- ปรับ cooldown/recovery ให้ไม่กิน lifetime มากเกินไป
- เพิ่ม litter size เฉพาะเมื่อ opportunity count ต่ำและ household buffer ผ่านจริง
- เพิ่ม fertility window ที่ยาวขึ้นหรือลด old-age penalty ต่อ female ที่ยัง healthy

เกณฑ์ยืนยัน:

ผ่านถ้า telemetry แสดงว่า opportunity windows เฉลี่ยต่ำกว่า `2` ใน run ที่ extinct และ intervention ที่เพิ่ม opportunity windows เป็น `>=2` ทำให้ replacement ratio, births per adult female, matured female offspring และ non-extinct runs ดีขึ้น โดยไม่จำเป็นต้องเพิ่ม global food

เกณฑ์หักล้าง:

ถ้า opportunity windows เฉลี่ยสูงกว่า `3-4` อยู่แล้ว แต่ births/matured female offspring ยังต่ำ แปลว่าปัญหาอยู่ที่ gate คุณภาพของแต่ละ opportunity เช่น energy, nest food, child survival หรือ sex ratio ไม่ใช่จำนวน opportunity

## 4. ลำดับการทดสอบที่แนะนำ

1. เพิ่ม telemetry ก่อนแก้ใหญ่: owner mismatch, adult female readiness, mate distance, food source accounting, และ reproduction opportunity windows ต่อ female lifetime
2. ทดสอบสมมุติฐาน 11 ก่อน เพราะถ้า opportunity ต่อชีวิตต่ำกว่า replacement threshold การแก้อาหารหรือ mutation จะอ่านผลผิดได้ง่าย
3. ทดสอบสมมุติฐาน 1 และ 2 เพราะมีหลักฐานแรงจาก breeder-priority และ household continuity
4. ทดสอบสมมุติฐาน 3 และ 4 เพื่อแยกว่า late collapse เกิดจาก pipeline หรือ spatial/mate fragmentation
5. ทดสอบสมมุติฐาน 6 และ 7 เพื่อแยก surplus จริงกับ surplus หลอก
6. ทดสอบสมมุติฐาน 10 บน current branch body8 เพราะ benchmark ล่าสุดถอยแรง
7. ค่อยเปิด mutation regime study ตามสมมุติฐาน 9 หลัง telemetry, lifespan economics และ household economy เสถียรขึ้น

## 5. เกณฑ์ตีความผลแบบระวัง

- ถ้า intervention เพิ่ม stored food แต่ final population ยังตายหมด ให้ถือว่าไม่แก้ conversion problem
- ถ้า intervention เพิ่ม wealth/storage แต่ reproduction opportunities ต่อ female lifetime ยังต่ำกว่า 2 ให้ถือว่ายังไม่แก้ fertility/replacement bottleneck
- ถ้า intervention เพิ่ม births แต่ matured children ลด ให้ถือว่าทำให้ reproduction noisy ไม่ใช่ stable
- ถ้า intervention ลด extinction ด้วยการเพิ่มอาหารโลกตรง ๆ ให้แยกเป็น world-difficulty experiment ไม่ใช่ solution หลัก
- ถ้า intervention ทำให้ seed บางตัวดีขึ้นมากแต่ aggregate แย่ลง ให้เก็บเป็น mechanism clue ไม่ใช่ working fix
- ถ้าผลดีเฉพาะ body14 founder250 แต่ body8 current branch ยังพัง ให้สรุปว่าเป็น body/track-specific solution ต้อง validate ข้าม track

## 6. ข้อเสนอสุดท้าย

สมมุติฐานที่น่าเริ่มที่สุดคือ 11, 1, 2, 3 และ 4 เพราะแตะคอขวดโดยตรง: lifetime reproduction opportunity, household allocation, owner resolution, juvenile-to-breeder pipeline และ mate/nest continuity

สมมุติฐานที่ควรทำแบบระวังคือ 6 และ 7 เพราะเกี่ยวกับ nest support และ settlement productivity ถ้าแก้แรงไปอาจทำให้ scaffold หายแล้ว collapse เหมือน active-nest-only probe

สมมุติฐานที่ควรเลื่อนออกไปก่อนคือ 9 เพราะ endogenous mutation สำคัญต่อเป้าหมายระยะยาว แต่ถ้าโลกยังไม่มี reproductive opportunity มากพอ mutation ที่ดีอาจไม่มีเวลาหรือพลังงานพอจะแสดงผล และจะถูกคัดทิ้งเร็วเกินไปจนอ่านผลยาก

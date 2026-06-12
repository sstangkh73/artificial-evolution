# เฟซแยก: World Discovery Experiment

วันที่จัดทำ: 2026-06-08
สถานะ: runnable exploratory phase + research protocol
CLI mode: `world-discovery`

## 1. เป้าหมาย

โจทย์หลักของเฟซนี้คือ:

> ถ้าโยน AI/agent ลงไปในโลกใหม่โดยไม่ให้คลังข้อมูลโลกเดิม มันจะค้นพบอะไร เรียนรู้อะไร และความรู้นั้นอยู่ในตัวเดียวหรือกลายเป็นความรู้ร่วมของสังคมได้แค่ไหน

เฟซนี้แยกออกจาก Phase 1/2 เดิม เพราะไม่ได้ถามแค่ body ไหนรอด หรือ lineage ไหนสืบพันธุ์ได้ แต่ถามว่า agent สร้าง "แบบจำลองของโลก" จากประสบการณ์ตรงได้หรือไม่

## 2. บทเรียนจาก paper 5 ฉบับ

### 2.1 Ha and Schmidhuber, World Models

แกนสำคัญคือ agent ไม่ควรพึ่ง policy อย่างเดียว แต่ควรมี representation ของโลกที่บีบอัด spatial/temporal experience ได้ แล้วใช้ representation นั้นวางแผนหรือฝึก controller ได้

ผลต่อเฟซนี้:

- ต้องแยก `survival score` ออกจาก `world-knowledge score`
- memory, prediction, route reuse, safe-zone learning และ transfer ไปโลกยากกว่าเป็นตัวชี้วัดสำคัญ
- เฟซอนาคตควรเพิ่ม learned predictive world model จริง ไม่ใช่แค่ rule-based memory

### 2.2 Graesser, Cho, and Kiela, Emergent Linguistic Phenomena in Multi-Agent Communication Games

งานนี้แสดงว่า language/contact phenomena ระดับชุมชนเกิดจาก topology และการปะทะกันของ protocol ได้ แม้ agent จะไม่ได้มี linguistic faculty ซับซ้อนมาก

ผลต่อเฟซนี้:

- ต้องมี condition แบบ individual กับ collective community
- ต้องวัดว่าความรู้กระจายผ่านกลุ่มหรือไม่ ไม่ใช่วัด agent แยกตัวเท่านั้น
- topology, contact frequency, group formation และ mutual exposure เป็นตัวแปรทดลองสำคัญ

### 2.3 Karten et al., Emergent Communication for Social Learning in MARL

บทเรียนคือ communication ที่ดีควรถูกบีบอัดและมี utility ต่อ task ไม่ใช่ส่งข้อมูลเยอะโดยไม่มีความหมาย เฟรมนี้ยังชี้เรื่อง social shadowing: agent เรียนจาก policy/action ของ expert ได้

ผลต่อเฟซนี้:

- ในรอบ runnable ปัจจุบันใช้ `friend_count`, `group_formed`, shared memory และ role persistence เป็น proxy
- เฟซถัดไปควรเพิ่ม message token/bottleneck จริง แล้ววัด compression, utility และ interpretability
- ต้องระวัง false positive แบบสื่อสารเยอะ แต่ survival/technology/reproduction ไม่ดีขึ้น

### 2.4 Taniguchi et al., Generative Emergent Communication

งานนี้แยก Type 1 world model จากประสบการณ์ sensorimotor ของ agent กับ Type 2/collective world model ที่ถูก externalize ในภาษาและสังคม มุมนี้ตรงกับโจทย์ของโครงการมาก

ผลต่อเฟซนี้:

- เฟซนี้ควรแยก 2 คำถาม:
  - agent ตัวเดียวสร้าง Type 1 world model ได้แค่ไหน
  - สังคม agent สร้าง collective world model ได้แค่ไหน
- LLM ที่เทรนจาก text คือการเรียนจาก collective world model ของมนุษย์ แต่โลกจำลองนี้ต้องเริ่มจาก embodied interaction ก่อน
- ถ้ามีภาษา/สัญญะในอนาคต ต้องวัดว่ามัน encode ความรู้โลกจริงหรือเป็นแค่ artifact ของ reward

### 2.5 Sims, Evolving Virtual Creatures

Sims แสดงว่าร่างกายและ controller สามารถ co-evolve ใน physics world แล้วสร้างพฤติกรรมที่คนออกแบบเองยาก

ผลต่อเฟซนี้:

- ต้องให้ morphology/trait/behavior drift เป็นส่วนหนึ่งของการค้นพบโลก
- ห้ามสรุปว่า agent "ฉลาด" ถ้าความสำเร็จมาจาก body corridor แคบหรือ fitness scaffold เพียงอย่างเดียว
- ต้องเทียบ high-cognition body กับ sensory/low-brain control

## 3. Research Question

คำถามหลัก:

> ในโลกใหม่ที่ agent ไม่ได้รับข้อมูลโลกภายนอกล่วงหน้า ความรู้แบบ embodied, social และ material/technology จะเกิดขึ้นเองได้หรือไม่ และความรู้นั้นช่วย survival, reproduction, technology และ transfer ไปโลกใหม่กว่าเดิมหรือไม่

คำถามย่อย:

- Agent สะสมความจำเกี่ยวกับ food, danger, safe zone และ nest ได้มากกว่ากลุ่ม control หรือไม่
- ความรู้จาก agent หลายตัวรวมกันผ่าน social group แล้วเพิ่ม lineage persistence หรือไม่
- scarcity/frontier pressure ทำให้เกิด object experimentation และ technology discovery หรือไม่
- ความรู้ที่เกิดในโลกหนึ่งยังช่วยใน novel scarcity world หรือ collapse เมื่อกฎโลกเปลี่ยน

## 4. Hypotheses

### H24: Embodied World Discovery Hypothesis

ถ้า agent มี cognition/memory/planning สูงพอ มันควรสร้าง Type 1 world knowledge จากการเดิน กิน หลบภัย สร้างรัง และใช้สิ่งแวดล้อม โดยวัดได้จาก memory-site counts, repeated nest/food use, survival และ reproduction

Evidence supporting:

- `mean_agent_memory_sites` สูงกว่า sensory control
- first birth, matured child, settlement, stored food และ peak population สูงกว่า control
- death จาก energy/danger ลดลงเมื่อ memory/social metrics สูงขึ้น

Evidence against:

- memory สูงแต่ survival/reproduction ไม่ดีขึ้น
- sensory control รอดเท่ากันหรือดีกว่า high-cognition body
- ผลเกิดจาก spawn ใน safe-high-food เท่านั้น

### H25: Collective World Model Hypothesis

ถ้า agent อยู่เป็นชุมชน ความรู้โลกควรถูกรวมและถ่ายผ่าน social contact/group memory จนเพิ่ม generation depth หรือ technology emergence ได้มากกว่า individual/default condition

Evidence supporting:

- `social_contact_rate` และ `mean_friend_count` สูง
- collective condition ถึง generation 3 หรือมี lineage persistence สูงกว่า default
- group formation, nest continuity, food sharing, object experimentation เกิดเป็นลำดับที่อธิบายได้

Evidence against:

- social contact สูงแต่ reproduction/generation ไม่ดีขึ้น
- collective condition เพิ่ม population ชั่วคราวแต่ collapse เร็ว
- group memory ไม่แยกจาก founder population effect

### H26: Material Discovery Hypothesis

ถ้าโลกมี resource frontier และ scarcity พอ agent ควรทดลอง object/material จนเกิด technology ที่มี utility มากกว่า decorative artifact

Evidence supporting:

- first technology เกิดใน frontier condition มากกว่า default
- `object_experiment_agent_rate` สูงขึ้นพร้อม survival/reproduction ไม่ collapse
- technology emergence ตามหลัง settlement/material accumulation ไม่ใช่เกิดเร็วแบบไม่มีฐานผลิต

Evidence against:

- technology เกิดเร็วมากแต่ไม่เพิ่ม productivity
- object experimentation ทำให้ energy economy แย่ลง
- first technology เกิดเฉพาะเพราะ scaffold ของ nest/material ไม่ใช่ discovery

### H27: Novel-World Transfer Hypothesis

ถ้า agent สร้าง world knowledge ที่ general ได้จริง strategy บางส่วนควรยังใช้ได้เมื่อ world เปลี่ยนเป็น scarce/variable มากขึ้น

Evidence supporting:

- novel scarcity transfer มี survival/reproduction ดีกว่า sensory control
- memory/social/technology metrics ไม่หายทั้งหมดเมื่อ environment เปลี่ยน
- extinction delay หรือ generation depth ดีขึ้นโดยไม่เพิ่ม global food

Evidence against:

- novel world ทำให้ทุก condition collapse เท่ากัน
- high-cognition body เสียเปรียบเพราะ brain drain โดยไม่มี learning benefit
- success ติดอยู่กับ default quadrant layout มากเกินไป

## 5. Current Runnable Conditions

รันด้วย:

```powershell
python main.py --mode world-discovery --seed 7 --study-seeds 4 --dashboard-ticks 1600 --snapshot-interval 20 --change-note "World discovery exploratory phase"
```

ผลลัพธ์จะอยู่ใน:

- `data/research_runs/...` สำหรับ raw replicate bundles
- `data/publication_packages/experiment_###_world_discovery_phase` สำหรับ aggregate package

| Condition | จุดประสงค์ |
|---|---|
| `embodied_world_model_body_8` | high-cognition default world สำหรับ Type 1 embodied knowledge baseline |
| `frontier_object_discovery_body_8` | scarcity + frontier material เพื่อวัด object/technology discovery |
| `collective_world_model_body_8` | sexed community 50 founders เพื่อวัด collective memory/generation persistence |
| `collective_world_model_body_14` | เปรียบเทียบ body 14 ที่ nurturing/settler กว่า body 8 |
| `sensory_control_body_131` | sensor สูงแต่ brain ต่ำกว่า เพื่อแยก perception จาก world-model/social learning |
| `novel_scarcity_transfer_body_8` | โลก scarcity/season/day pressure สูงกว่า เพื่อวัด transfer/generalization proxy |

## 6. Variables

Independent variables:

- body type: `body_8`, `body_14`, sensory control
- environment: default, frontier-object pressure, novel scarcity
- population topology: 12 alternating founders vs 50 sexed community
- spawn strategy: default vs frontier-safe-high-food

Dependent variables:

- survival: final tick, extinction, peak population
- reproduction: births, matured children, generation-3 adulthood
- embodied knowledge: `mean_agent_memory_sites`, `max_agent_memory_sites`
- social knowledge: `social_contact_rate`, `mean_friend_count`, `group_formed` events
- material discovery: first technology tick/name, `object_experiment_agent_rate`
- lineage adaptation: generation traits, mutation counts, lineage survival

Control variables:

- same seed set within a batch
- same tick horizon per comparable condition
- same world dimensions and base mechanics unless environment condition explicitly changes them
- same output protocol: metadata, tick metrics, events, lineages, agent outcomes, dashboard

## 7. Metrics Added For This Phase

`agent_outcomes.csv` now includes:

- `preferred_role`
- `final_role`
- `friend_count`
- `remembered_food_sources_count`
- `remembered_safe_zones_count`
- `remembered_danger_count`
- `remembered_nest_locations_count`

Publication aggregate outputs now include:

- `mean_agent_memory_sites`
- `max_agent_memory_sites`
- `social_contact_rate`
- `object_experiment_agent_rate`
- `mean_friend_count`

Interpretation:

- memory counts are only a proxy for Type 1 world knowledge
- social contact is only a proxy for collective knowledge exchange
- object experimentation is only a proxy for material discovery
- none of these yet prove language, symbolic reasoning, or neural world-model learning

## 8. Statistical Plan

Exploratory run:

- 4 seeds per condition
- use medians, IQR, full replicate table
- do not make strong confirmatory claims

Confirmatory run:

- at least 12 seeds per condition
- report Wilson intervals for binary outcomes
- compare continuous outcomes with distributions, not only means
- preserve negative results and per-seed dashboards

Bias and limitations to inspect:

- survivorship bias in agent outcomes
- body corridor effect
- spawn-location advantage
- nest support scaffold
- early technology artifact
- founder population effect in collective conditions

## 9. Failure Criteria

Reject or revise a hypothesis if:

- high-cognition conditions do not outperform sensory control on learning proxies or outcomes
- memory/social metrics rise but survival/reproduction/technology do not improve
- technology emergence happens early but decreases reproduction or final tick
- collective conditions improve only because initial population is larger, not because social metrics change
- novel scarcity eliminates all effects and reveals default-world overfitting

## 10. Next Build After This Runnable Phase

This runnable phase is still a proxy study. The next true AI-world-discovery phase should add:

- a learned predictive model over local observations and actions
- explicit action/outcome prediction error
- message tokens with an information bottleneck
- social shadowing from expert to novice agents
- dream rollout or imagined planning inspired by World Models
- topology experiments for language/contact dynamics
- a protocol to test whether learned symbols predict real environmental structure

## 11. Summary

เฟซนี้ทำหน้าที่เป็นสะพานระหว่าง artificial life simulation ปัจจุบันกับโจทย์ใหญ่เรื่อง AI ที่เรียนรู้โลกใหม่จากศูนย์:

- ตอนนี้วัดได้ว่า embodied/social/material discovery proxy เกิดหรือไม่
- ยังไม่ควร claim ว่าเป็น LLM, language, หรือ neural world model
- ถ้าเฟซนี้แสดง signal ชัด ค่อยเพิ่ม learner/communication จริงในเฟซถัดไป

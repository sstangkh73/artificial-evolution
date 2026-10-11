# สรุปไทม์ไลน์การเทรน AI, LLM, Agent และการตัดสินใจเอง

วันที่จัดทำ: 2026-06-24

ไฟล์นี้สรุปจากชุด PDF ใน `C:\artificial-evolution\papers` โดยเน้น 2 คำถามหลัก:

1. AI แบบ ChatGPT, Claude, Llama, DeepSeek ถูกเทรนขึ้นมาอย่างไร
2. การที่ AI "เลือกเอง" ต่างจากการเขียนสคริปต์อย่างไรในเชิงหลักการ

หมายเหตุสำคัญ: คำว่า "เลือกเอง" ในที่นี้ไม่ได้หมายถึงมีเจตจำนงหรือสติแบบมนุษย์ แต่หมายถึงระบบเรียน policy หรือกลยุทธ์การเลือก action จากข้อมูล, reward, preference, environment feedback, memory, search หรือเครื่องมือ ไม่ใช่ลำดับ if-else ที่มนุษย์เขียนตายตัวทั้งหมด

## ภาพรวมสั้นที่สุด

เส้นทางทั้งหมดแบ่งได้เป็น 4 กระแสใหญ่:

1. Reinforcement Learning agent: เริ่มจาก agent ที่รับ observation แล้วเลือก action เพื่อสะสม reward เช่น DQN, AlphaGo Zero, AlphaZero, MuZero นี่คือแกน "เลือก action เอง" ที่ชัดที่สุด
2. Transformer และ language model scaling: Transformer ทำให้เทรนบนข้อมูลขนาดใหญ่ได้ดีขึ้น จาก GPT-1 -> GPT-2 -> GPT-3 -> GPT-4/Llama ทำให้โมเดลเรียน pattern ภาษา ความรู้ และความสามารถแบบ few-shot
3. Alignment และ post-training: โมเดล base ที่ทำนาย token เก่งยังไม่จำเป็นต้องตอบตามเจตนาผู้ใช้ จึงมี SFT, RLHF, RLAIF, Constitutional AI, DPO เพื่อทำให้ตอบ helpful, harmless, honest มากขึ้น
4. Agentic reasoning: LLM เริ่มถูกใช้เป็น policy/controller ที่คิด, เรียก tool, วางแผน, สะท้อนข้อผิดพลาด, เก็บ memory และทดลองใน environment เช่น ReAct, Toolformer, Tree of Thoughts, Reflexion, Voyager, o1, DeepSeek-R1

## แผนที่หลักการ

### 1. Base LLM

เป้าหมายหลักคือเรียนความน่าจะเป็นของ token ถัดไป:

```text
p(next_token | context)
```

โมเดลไม่ได้ถูกสอนทีละกฎว่าเจอคำถามนี้ต้องตอบอะไร แต่ถูกเทรนให้ทำนาย token จากข้อความจำนวนมหาศาล ผลคือมันเรียน grammar, facts, style, reasoning pattern และ task format จาก distribution ของข้อมูล

### 2. Supervised Fine-Tuning หรือ SFT

หลังจาก pretrain แล้ว เอาตัวอย่าง prompt -> answer ที่มนุษย์เขียนดี ๆ มาสอนให้โมเดลตอบในรูปแบบ assistant มากขึ้น จุดนี้ทำให้โมเดลเริ่ม "ตามคำสั่ง" แทนที่จะต่อข้อความแบบ internet text เฉย ๆ

### 3. Reward Model และ RLHF

มนุษย์ไม่ได้เขียนคำตอบที่ถูกเสมอไป แต่ให้ ranking ว่าคำตอบ A ดีกว่า B จากนั้นเทรน reward model ให้ทำนาย preference แล้วใช้ reinforcement learning ปรับ assistant ให้ได้ reward สูง โดยมี KL penalty ไม่ให้ drift ออกจาก base model มากเกินไป

แนวคิด:

```text
prompt -> model สร้างหลายคำตอบ -> human ranking -> reward model -> RL ปรับ policy
```

### 4. RLAIF และ Constitutional AI

แทนที่จะให้มนุษย์ตัดสินทุกคู่คำตอบ ใช้ AI ช่วย critique, revise และเลือกคำตอบโดยอ้างอิงหลักการหรือ constitution เช่น ไม่ช่วยทำอันตราย เคารพความเป็นส่วนตัว ไม่หลอกผู้ใช้ วิธีนี้ลดภาระ human labeling และขยาย alignment ได้มากขึ้น

### 5. DPO

DPO มองว่าไม่จำเป็นต้องแยก reward model แล้วทำ RL ขั้นหนักเสมอไป สามารถใช้คู่ preference เช่น chosen/rejected มาปรับ policy โดยตรงผ่าน objective แบบ classification ที่ผูกกับ reference model ได้ วิธีนี้ง่ายและเสถียรกว่า PPO-style RLHF ในหลายงาน

### 6. Agent ที่เลือก action

LLM ปกติเลือก token แต่ agent ต้องเลือก action:

```text
observation + goal + memory + tools -> action
```

action อาจเป็น:

- ตอบข้อความ
- search
- เรียก calculator
- เขียน code
- คลิกหน้าเว็บ
- เดินในเกม
- เลือก move ใน Go/chess
- เรียก API

ตรงนี้ต่างจากสคริปต์ เพราะมนุษย์ไม่ได้เขียน action sequence ตายตัว แต่กำหนด goal, reward, feedback หรือ tool interface แล้วให้ระบบเลือก action ตาม policy/search/reasoning

## Timeline ว่าเกิดอะไรขึ้น

### 1994 - Artificial creatures และ evolution simulation

ไฟล์: `siggraph94.pdf`

Sims แสดงแนวคิดว่า morphology และ controller ของสิ่งมีชีวิตเสมือนสามารถ evolve ได้ในโลกฟิสิกส์จำลอง ไม่ใช่แค่เขียน animation ด้วยมือ นี่เป็นต้นทางสำคัญของ artificial life: พฤติกรรมเกิดจาก selection pressure, body, controller และ environment ร่วมกัน

ความหมายต่อโจทย์ "AI เลือกเอง": ระบบไม่ได้ถูกสั่งทุก movement แต่ถูก optimize ให้รอดหรือทำ task ได้ใน simulation

### 2015 - DQN: agent เรียนเล่น Atari จากภาพและ reward

ไฟล์: `26_Human_Level_Control_through_Deep_Reinforcement_Learning_DQN.pdf`

DQN รวม deep neural network กับ Q-learning เพื่อให้ agent รับ pixel จากเกม Atari แล้วเลือก action ที่ maximize expected return ใช้ replay memory เพื่อลด correlation ของข้อมูล และ target network เพื่อทำให้ training เสถียรขึ้น

สิ่งที่เกิดขึ้น:

- จากเดิม RL มักทำงานกับ state ที่ออกแบบด้วยมือ
- DQN แสดงว่า neural network เรียน representation จากภาพดิบได้
- agent เลือก action ผ่าน Q-value ไม่ใช่สคริปต์เฉพาะเกม

### 2017 - Transformer: จุดเริ่มฐานสถาปัตยกรรม LLM สมัยใหม่

ไฟล์: `01_Attention_Is_All_You_Need.pdf`

Transformer ตัด recurrent/convolution ออก แล้วใช้ self-attention เป็นแกนหลัก ทำให้ token ทุกตำแหน่งมอง token อื่นใน sequence ได้โดยตรง และ parallelize บน GPU/TPU ได้ดีมาก

หลักการ:

- Self-attention คำนวณว่า token ไหนควรสนใจ token ไหน
- Multi-head attention ให้ model มอง relation หลายแบบพร้อมกัน
- Positional encoding เพิ่มข้อมูลลำดับ
- Feed-forward block + residual + layer norm ทำให้ stack ลึกได้

ผลกระทบ: ถ้าไม่มี Transformer การ scale GPT/Claude/Llama แบบปัจจุบันจะยากมาก

### 2017 - AlphaGo Zero: self-play โดยไม่ใช้เกมมนุษย์

ไฟล์: `27_AlphaGo_Zero_Mastering_the_Game_of_Go_without_Human_Knowledge.pdf`

AlphaGo รุ่นก่อนใช้ข้อมูลเกมมนุษย์ แต่ AlphaGo Zero เริ่มจาก tabula rasa รู้แค่กฎ Go แล้วเล่นกับตัวเอง ใช้ neural network ทำนาย policy และ value แล้วใช้ Monte Carlo Tree Search เลือก move

หลักการ:

- self-play สร้างข้อมูลเอง
- policy network บอก move ที่น่าลอง
- value network ประเมินโอกาสชนะ
- search ปรับปรุงการตัดสินใจ
- เกมที่ดีขึ้นกลายเป็นข้อมูล training รอบถัดไป

นี่เป็นตัวอย่างแรงมากของ "เลือกเอง": มนุษย์ไม่ได้สอน joseki หรือ strategy โดยตรง แต่ระบบค้นพบ strategy จาก reward ชนะ/แพ้

### 2017 - AlphaZero: general self-play สำหรับหลายเกม

ไฟล์: `28_AlphaZero_Mastering_Chess_and_Shogi_by_Self_Play.pdf`

AlphaZero ขยายแนวคิด AlphaGo Zero ไปยัง chess, shogi และ Go โดยใช้ algorithm เดียวกัน รู้แค่กฎเกม ไม่ใช้ handcrafted evaluation function แบบ chess engine รุ่นเก่า

บทเรียน: ถ้า environment มี rule ชัดและ reward ชัด self-play + search + neural network สามารถสร้าง superhuman policy ได้

### 2018 - GPT-1: generative pretraining แล้ว fine-tune

ไฟล์: `02_Improving_Language_Understanding_by_Generative_Pre_Training_GPT1.pdf`

GPT-1 เสนอสูตรที่กลายเป็นรากของ GPT family: pretrain language model บน unlabeled text ขนาดใหญ่ แล้ว fine-tune บน task เฉพาะ

หลักการ:

- ใช้ Transformer decoder
- pretrain ด้วย next-token prediction
- fine-tune ด้วย labeled task
- แปลง input ของหลาย task ให้อยู่ใน format ที่ language model เข้าใจ

ความสำคัญ: เปลี่ยน NLP จากการสร้าง architecture เฉพาะ task ไปสู่ foundation model ที่ transfer ไปหลาย task

### 2018 - BERT: bidirectional encoder pretraining

ไฟล์: `03_BERT_Pretraining_of_Deep_Bidirectional_Transformers.pdf`

BERT ใช้ Transformer encoder และ masked language modeling เพื่อเรียน representation จากบริบทซ้ายและขวาพร้อมกัน เหมาะกับ understanding task เช่น classification, entailment, question answering

ต่างจาก GPT:

- GPT เป็น autoregressive decoder อ่านซ้ายไปขวา เหมาะกับ generation
- BERT เป็น bidirectional encoder เหมาะกับ representation/understanding

บทเรียน: pretraining จาก unlabeled text กลายเป็น standard ของ NLP ทั้งฝั่ง encoder และ decoder

### 2018 - World Models: agent มีโมเดลโลกภายใน

ไฟล์: `1803.10122v4.pdf`

World Models แยก agent ออกเป็น vision model, memory model และ controller โดยให้ระบบเรียน compressed representation และ dynamics ของ environment ก่อน แล้วใช้ controller ตัดสินใจใน latent space

ความสำคัญ:

- agent ไม่จำเป็นต้องตัดสินใจจาก pixel ดิบทุกครั้ง
- การมี model ของโลกช่วยให้วางแผน/คาดการณ์ได้
- เป็นสะพานไปสู่ model-based RL และแนวคิด agent ที่มี internal simulation

### 2019 - GPT-2: zero-shot multitask จาก web-scale text

ไฟล์: `04_Language_Models_are_Unsupervised_Multitask_Learners_GPT2.pdf`

GPT-2 แสดงว่า language model ขนาดใหญ่ที่ pretrain บน WebText สามารถทำ task หลายอย่างแบบ zero-shot ได้เมื่อ prompt มีรูปแบบเหมาะสม เช่น question answering, summarization, translation

สิ่งที่เปลี่ยน:

- task ไม่จำเป็นต้องมี supervised dataset เสมอไป
- prompt กลายเป็น interface สำคัญ
- scale ของ model มีผลต่อ emergent multitask behavior

### 2019 - Fine-Tuning Language Models from Human Preferences

ไฟล์: `07_Fine_Tuning_Language_Models_from_Human_Preferences.pdf`

paper นี้เป็นก้าวต้นของ RLHF สำหรับภาษา: ให้มนุษย์เปรียบเทียบ output แล้วเทรน reward model เพื่อ fine-tune language model ด้วย RL

หลักการ:

- ความดีของคำตอบวัดด้วย human judgment ไม่ใช่ metric อัตโนมัติอย่างเดียว
- reward learning ใช้ preference pair แทน reward ที่เขียนด้วยมือ
- RL สามารถปรับ style หรือ quality ของ generation ได้

ข้อควรระวัง: reward model อาจเรียน shortcut หรือ preference ที่ไม่ลึกจริง เช่น labeler ใช้ heuristic ง่าย ๆ

### 2019 - Emergent communication ใน multi-agent games

ไฟล์: `1901.08706v2.pdf`

paper นี้ดูภาษาหรือสัญญาณที่เกิดในเกม multi-agent communication เมื่อ agent ต้องสื่อสารเพื่อทำ task ร่วมกัน สะท้อนว่า communication อาจ emerge จาก pressure ของ task ไม่จำเป็นต้องออกแบบภาษาด้วยมือทั้งหมด

ความหมายต่อ artificial life/agent:

- cooperation และ communication เป็น emergent behavior ได้
- แต่ภาษาที่ emerge อาจไม่เหมือนภาษามนุษย์
- objective และ environment shape ภาษาที่เกิดขึ้นอย่างแรง

### 2019/2020 - MuZero: วางแผนโดยไม่รู้ dynamics จริง

ไฟล์: `29_MuZero_Mastering_Atari_Go_Chess_and_Shogi_by_Planning.pdf`

MuZero รวม model-based planning กับ learned dynamics โดยไม่ต้องรู้ rule/dynamics ของ environment อย่างสมบูรณ์ มันเรียนเฉพาะสิ่งที่จำเป็นต่อ planning: reward, policy และ value

ต่างจาก AlphaZero:

- AlphaZero ใช้ simulator/rules ของเกมสำหรับ search
- MuZero เรียน model ภายในสำหรับวางแผน

ความสำคัญ: ใกล้โลกจริงมากขึ้น เพราะโลกจริงมักไม่มี simulator ที่สมบูรณ์ให้

### 2020 - Scaling Laws: performance ดีขึ้นตาม power law

ไฟล์: `06_Scaling_Laws_for_Neural_Language_Models.pdf`

paper นี้วัดความสัมพันธ์ระหว่าง loss กับ model size, dataset size และ compute พบว่ามี scaling law ค่อนข้างสม่ำเสมอในช่วงขนาดใหญ่

หลักการ:

- เพิ่ม model, data, compute แล้ว loss ลดแบบ predictable
- architecture detail บางอย่างสำคัญน้อยกว่า scale ในช่วงที่ศึกษา
- larger model มี sample efficiency สูงกว่า

ผลกระทบ: ทำให้บริษัทมั่นใจมากขึ้นว่าการ scale LLM เป็นเส้นทางที่คาดการณ์ได้ ไม่ใช่เดาสุ่ม

### 2020 - GPT-3: few-shot learning จาก scale

ไฟล์: `05_Language_Models_are_Few_Shot_Learners_GPT3.pdf`

GPT-3 มี 175B parameters และแสดงว่า model ใหญ่สามารถทำงานใหม่จาก instruction หรือ examples ใน prompt โดยไม่ต้อง fine-tune ทุก task

หลักการ:

- in-context learning: prompt กลายเป็น mini training context
- few-shot: ตัวอย่างไม่กี่ตัวใน prompt ช่วยให้ทำ task ได้
- autoregressive next-token prediction เมื่อ scale ใหญ่พอ เกิด behavior ที่เหมือนทำ task ได้หลากหลาย

ข้อจำกัด: GPT-3 base ยังไม่ใช่ assistant ที่ aligned ดี อาจ hallucinate, toxic, ไม่ตามเจตนาผู้ใช้

### 2020 - Learning to Summarize from Human Feedback

ไฟล์: `08_Learning_to_Summarize_from_Human_Feedback.pdf`

งานนี้ทำ RLHF กับ summarization อย่างจริงจัง โดยให้มนุษย์เปรียบเทียบ summary แล้วใช้ reward model แทน metric อย่าง ROUGE

บทเรียน:

- human preference สามารถให้สัญญาณคุณภาพที่ metric ดั้งเดิมจับไม่ได้
- RLHF ช่วยให้ model output ถูกใจมนุษย์มากขึ้น
- reward model ต้องระวัง bias และ overoptimization

### 2022 - Chinchilla: compute-optimal training ต้องเพิ่ม data ด้วย

ไฟล์: `09_Training_Compute_Optimal_Large_Language_Models_Chinchilla.pdf`

ก่อน Chinchilla หลายโมเดลเน้นเพิ่ม parameters แต่ train ด้วย token ไม่พอ Chinchilla เสนอว่าเมื่อเพิ่ม model size ควรเพิ่ม training tokens ในสัดส่วนใกล้เคียงกัน

หลักการ:

- undertrained model ใหญ่แพ้ model เล็กกว่าที่เห็นข้อมูลมากพอ
- compute budget เดียวกันควร balance model size และ dataset size
- 70B Chinchilla ที่ train token มากกว่า สามารถชนะ model ใหญ่กว่าอย่าง Gopher/GPT-3 ในหลาย benchmark

ผลกระทบ: recipe ของ LLM รุ่นหลัง ๆ เน้น data quality, data quantity และ compute allocation มากขึ้น

### 2022 - InstructGPT: สูตร public ใกล้ ChatGPT ที่สุด

ไฟล์: `10_InstructGPT_Training_LMs_to_Follow_Instructions_with_Human_Feedback.pdf`

InstructGPT คือจุดเปลี่ยนจาก base LLM ไปเป็น assistant ที่ตามคำสั่งผู้ใช้ โดยใช้ pipeline:

1. Collect demonstrations จาก labeler
2. Supervised fine-tuning
3. Collect rankings ของ model outputs
4. Train reward model
5. Fine-tune ด้วย PPO/RLHF

ผลสำคัญ: InstructGPT 1.3B ถูกมนุษย์ prefer มากกว่า GPT-3 175B ใน prompt distribution ของงานนั้น แปลว่า alignment/post-training อาจสำคัญกว่า parameter count เพียงอย่างเดียว

### 2022 - Anthropic Helpful and Harmless Assistant

ไฟล์: `11_Training_a_Helpful_and_Harmless_Assistant_with_RLHF.pdf`

Anthropic ใช้ preference modeling และ RLHF เพื่อเทรน assistant ให้ helpful และ harmless พร้อมสำรวจ online iteration ที่เก็บ feedback ใหม่เป็นรอบ ๆ

หลักการ:

- alignment ไม่ใช่แค่ทำให้ตอบดี แต่ต้องลดพฤติกรรมอันตราย
- helpfulness และ harmlessness อาจขัดกัน ต้อง tradeoff
- KL divergence จาก model ตั้งต้นเป็นตัวชี้ว่า policy drift แค่ไหน

ความสำคัญ: เป็นรากของ assistant alignment สาย Claude

### 2022 - Constitutional AI: ใช้หลักการให้ AI ช่วย supervise AI

ไฟล์: `12_Constitutional_AI_Harmlessness_from_AI_Feedback.pdf`

Constitutional AI ใช้รายการหลักการหรือ constitution ให้ model critique และ revise output ของตัวเอง จากนั้นใช้ AI feedback เลือกคำตอบที่ harmless กว่า

pipeline:

1. supervised phase: model สร้างคำตอบ -> critique ตาม constitution -> revise
2. RL phase: ใช้ AI preference ทำ reward signal

ความสำคัญ:

- ลด human labels ในเรื่อง harmful output
- ทำให้ alignment scale ได้มากขึ้น
- หลักการกลายเป็น input สำคัญของ training ไม่ใช่แค่ policy ภายนอก

### 2022/2023 - ReAct: reasoning + acting

ไฟล์: `16_ReAct_Synergizing_Reasoning_and_Acting_in_Language_Models.pdf`

ReAct ให้ LLM สลับระหว่าง reasoning trace กับ action เช่น search Wikipedia, observe result, คิดใหม่ แล้วตอบ

หลักการ:

- reasoning ช่วยวางแผนและติดตามสถานะ
- action ช่วยดึงข้อมูลจริงจากโลกภายนอก
- observation จาก tool ลด hallucination

นี่คือรูปแบบ agent สมัยใหม่: model ไม่ได้แค่ตอบทันที แต่ loop ผ่าน think -> act -> observe -> think

### 2023 - GPT-4 Technical Report: frontier multimodal LLM

ไฟล์: `13_GPT4_Technical_Report.pdf`

GPT-4 เป็น multimodal model ที่รับ image/text และ output text รายละเอียด training ไม่เปิดทั้งหมด แต่ report เน้นว่า pretraining เป็น next-token prediction และ post-training alignment ช่วยเรื่อง factuality และ desired behavior

สิ่งที่สำคัญ:

- scale และ infrastructure ทำให้ performance predict ได้จาก model เล็กกว่า
- evaluation กว้างขึ้นไปถึง professional/academic benchmarks
- frontier model ต้องมี safety evaluation และ red teaming

### 2023 - Toolformer: model เรียนใช้ tool เองจากตัวอย่างน้อย

ไฟล์: `17_Toolformer_Language_Models_Can_Teach_Themselves_to_Use_Tools.pdf`

Toolformer สอน language model ให้ตัดสินใจว่าเมื่อไรควรเรียก API, ใช้ argument อะไร และจะ integrate result กลับเข้า text อย่างไร โดยใช้ self-supervised filtering จากตัวอย่าง tool call จำนวนน้อย

เครื่องมือที่ใช้ใน paper:

- calculator
- Q&A system
- search engine
- translation system
- calendar

ความหมายต่อ "เลือกเอง": model ไม่ได้มีสคริปต์ fixed ว่า query ใดต้องเรียก tool แต่เรียน pattern ว่า tool call ไหนช่วยลด loss/เพิ่มคุณภาพ

### 2023 - DPO: preference tuning แบบง่ายกว่า RLHF

ไฟล์: `14_Direct_Preference_Optimization_DPO.pdf`

DPO แปลงปัญหา RLHF ให้เป็น objective ที่ใช้คู่ chosen/rejected โดยตรง ไม่ต้อง train reward model แยกแล้วทำ PPO หลายขั้น

หลักการ:

- ใช้ reference model เป็น anchor
- ปรับให้ log-prob ของ chosen สูงขึ้นเมื่อเทียบกับ rejected
- ได้ alignment จาก preference data โดย training เสถียรกว่า

ผลกระทบ: ทำให้ open-source alignment ทำได้ง่ายขึ้นมาก เพราะไม่ต้องมี RL infrastructure ซับซ้อน

### 2023 - Llama 2: open foundation + chat model recipe

ไฟล์: `15_Llama_2_Open_Foundation_and_Fine_Tuned_Chat_Models.pdf`

Llama 2 เปิดเผยรายละเอียด pretraining และ fine-tuning มากกว่าระบบปิดหลายตัว มี model 7B-70B และ Llama 2-Chat ที่ optimize สำหรับ dialogue

หลักการ:

- pretraining บน corpus ใหญ่
- SFT สำหรับ dialogue
- RLHF สำหรับ helpfulness/safety
- safety data และ red teaming

ความสำคัญ: เป็นหนึ่งใน recipe สาธารณะที่ชัดสำหรับสร้าง chat model แบบ modern

### 2023 - Tree of Thoughts: search over reasoning

ไฟล์: `18_Tree_of_Thoughts_Deliberate_Problem_Solving_with_LLMs.pdf`

Tree of Thoughts ขยาย chain-of-thought จากเส้นเดียวเป็น tree ของ "thoughts" ที่ model สามารถ explore, evaluate, backtrack ได้

หลักการ:

- thought เป็น unit ระดับสูงกว่าหนึ่ง token
- model สร้างหลายเส้นทาง
- self-evaluation หรือ external evaluator เลือกทางที่น่าไปต่อ
- search ช่วยงานที่ต้องวางแผนหลายขั้น

ความหมาย: reasoning ไม่จำเป็นต้องเป็น left-to-right เดียวเสมอไป สามารถใช้ search คล้าย planning algorithm ได้

### 2023 - Reflexion: เรียนจาก feedback ด้วยภาษา ไม่ update weights

ไฟล์: `19_Reflexion_Language_Agents_with_Verbal_Reinforcement_Learning.pdf`

Reflexion ให้ agent สะท้อนความผิดพลาดเป็นข้อความ เก็บไว้ใน episodic memory แล้วใช้ memory นี้ปรับการตัดสินใจรอบถัดไป โดยไม่ต้อง fine-tune weight

หลักการ:

- trial -> feedback -> reflection -> memory -> retry
- feedback อาจเป็น scalar หรือ natural language
- memory ทำหน้าที่เหมือน experience replay แบบภาษา

นี่ทำให้ agent พัฒนาพฤติกรรมได้ใน runtime แม้ model weights คงเดิม

### 2023 - Voyager: lifelong learning agent ใน Minecraft

ไฟล์: `20_Voyager_Open_Ended_Embodied_Agent_with_LLMs.pdf`

Voyager ใช้ GPT-4 เป็น black-box controller ใน Minecraft มี 3 ส่วนหลัก:

1. automatic curriculum เลือกเป้าหมายสำรวจเอง
2. skill library เก็บ code/action ที่ทำสำเร็จ
3. iterative prompting ใช้ environment feedback, execution error และ self-verification เพื่อแก้ code

ความสำคัญ:

- agent ไม่ต้อง fine-tune model weights
- ความสามารถสะสมผ่าน skill library
- behavior ยาวและ compositional มากขึ้น

### 2023 - Emergent communication for social learning

ไฟล์: `2302.14276v1.pdf`

งานนี้ดูบทบาทของ emergent communication ต่อ social learning ใน multi-agent RL เมื่อ agent ใช้ข้อมูล/สัญญาณจาก agent อื่นเพื่อเรียนรู้

ประเด็นสำคัญ:

- communication ช่วย coordination และ learning ได้
- social learning ทำให้ agent ใช้ cue จากผู้เชี่ยวชาญหรือเพื่อนร่วม environment
- protocol ที่ emerge ขึ้นอยู่กับ objective และ reward structure

### 2024 - Llama 3: open model family ที่รองรับ multilingual, coding, reasoning, tool use

ไฟล์: `21_Llama_3_Herd_of_Models.pdf`

Llama 3 ขยายทั้ง scale, data, context length และ post-training มีรุ่นใหญ่ 405B, context สูงสุด 128K และเปิดทั้ง pre-trained/post-trained model

หลักการสำคัญ:

- data pipeline และ quality filtering สำคัญมาก
- post-training ไม่ใช่ขั้นตอนเล็ก แต่เป็นระบบใหญ่ของ SFT, preference, safety, tool use
- model family ต้องมี safety model เช่น Llama Guard

ความหมาย: modern LLM ไม่ใช่แค่ base model แต่เป็น ecosystem ของ model, guard, tool use และ evaluation

### 2024 - OpenAI o1: reasoning model จาก large-scale RL

ไฟล์: `22_OpenAI_o1_System_Card.pdf`

o1 ถูกอธิบายว่า train ด้วย large-scale reinforcement learning เพื่อ reasoning โดยใช้ chain of thought ก่อนตอบ จุดสำคัญคือ test-time reasoning มากขึ้น: model ใช้เวลา/compute ในการคิดก่อน answer

หลักการ:

- RL ฝึกให้ reasoning path นำไปสู่คำตอบดีขึ้น
- deliberative alignment ให้ model reason กับ safety policy ใน context
- reasoning เพิ่ม capability แต่เพิ่ม risk จึงต้อง safety eval หนักขึ้น

นี่คือจุดที่ LLM เริ่มใกล้ "agent คิดก่อนทำ" มากกว่าการ autocomplete ตรง ๆ

### 2024 - Deliberative Alignment: สอนให้ reason ตาม safety specification

ไฟล์: `23_Deliberative_Alignment_Reasoning_Enables_Safer_Language_Models.pdf`

Deliberative Alignment สอน model ให้ recall และ reason over safety specifications ก่อนตอบ โดยไม่ต้องใช้ human-written chain-of-thought หรือคำตอบทุกกรณี

ผลที่ต้องการ:

- ต้าน jailbreak ดีขึ้น
- overrefusal ลดลง
- generalize นอก distribution ดีขึ้น
- alignment โปร่งใสมากขึ้นเพราะ model reason กับ policy ที่ระบุชัด

### 2025 - DeepSeek-R1: reasoning capability จาก RL โดยตรง

ไฟล์: `24_DeepSeek_R1_Incentivizing_Reasoning_Capability_in_LLMs.pdf`

DeepSeek-R1 สำคัญมากเพราะแสดงว่าความสามารถ reasoning บางแบบสามารถ emerge จาก reinforcement learning บน task ที่ verify ได้ เช่น math, coding, STEM โดยไม่จำเป็นต้องมี human-labeled reasoning trajectories เสมอไป

หลักการ:

- RL ให้ reward จากคำตอบที่ตรวจได้
- model ค่อย ๆ เกิด self-reflection, verification, strategy adaptation
- reasoning pattern จาก model ใหญ่สามารถ distill ไป model เล็กได้

R1-Zero ชี้ว่าถ้า reward ชัดพอ model อาจค้นพบรูปแบบ reasoning เอง แต่ R1 เต็มยังใช้ staged training เพื่อให้ภาษาอ่านง่ายและคุณภาพดีขึ้น

### 2025 - Claude Opus 4 / Sonnet 4 System Card

ไฟล์: `25_Claude_Opus_4_and_Sonnet_4_System_Card.pdf`

system card นี้ไม่ใช่ paper สูตร training เต็ม แต่สำคัญเพราะสะท้อนยุคของ hybrid reasoning model, agentic safety evaluation, computer use และ coding capability

ประเด็นสำคัญ:

- model รุ่นใหม่ถูกทดสอบด้าน agentic behavior มากขึ้น
- safety ไม่ใช่แค่ toxic text แต่รวม reward hacking, misalignment, autonomy, tool/computer use
- Claude Opus 4 ถูก deploy ภายใต้ AI Safety Level 3 ส่วน Sonnet 4 ภายใต้ ASL-2 ตามเอกสาร

ความหมาย: เมื่อ model ทำงานยาวและใช้เครื่องมือได้ safety ต้อง evaluate เป็นระบบ agent ไม่ใช่ chatbot อย่างเดียว

### 2025 - Generative Emergent Communication

ไฟล์: `2501.00226v2.pdf`

paper นี้เชื่อม LLM กับ collective/world model และ emergent communication มองว่า language model อาจเป็นกลไกที่รวม distribution ของประสบการณ์/ความรู้จากหลาย agent หรือสังคม

ความสำคัญต่อโปรเจกต์ artificial evolution:

- ภาษาหรือ communication อาจทำหน้าที่เป็น world model แบบ collective
- agent ที่สื่อสารกันอาจเรียนรู้ได้เร็วขึ้นกว่าการลองเองทั้งหมด
- ต้องระวังว่า emergent protocol อาจไม่ตรงกับภาษามนุษย์หรือเป้าหมายที่เราคิด

## สรุปราย paper ตามไฟล์

### 01_Attention_Is_All_You_Need.pdf

คำถามหลัก: จะสร้าง sequence model ที่ train เร็วและจับ dependency ระยะไกลได้ดีกว่า RNN/CNN อย่างไร

หลักการ: ใช้ self-attention ล้วน ๆ พร้อม multi-head attention และ positional encoding

สิ่งที่เปลี่ยน: เปิดทางให้ scale model ขนาดใหญ่มากบน hardware parallel ได้

อ่านเพื่อเข้าใจ: โครงกระดูกของ GPT, Claude, Llama, DeepSeek

### 02_Improving_Language_Understanding_by_Generative_Pre_Training_GPT1.pdf

คำถามหลัก: ใช้ unlabeled text จำนวนมากช่วยงาน NLP ที่มี labeled data น้อยได้ไหม

หลักการ: pretrain autoregressive LM แล้ว fine-tune task downstream

สิ่งที่เปลี่ยน: language model กลายเป็นฐาน transfer learning

อ่านเพื่อเข้าใจ: ทำไม GPT เริ่มจาก next-token prediction

### 03_BERT_Pretraining_of_Deep_Bidirectional_Transformers.pdf

คำถามหลัก: representation ที่อ่านซ้ายและขวาพร้อมกันช่วย understanding task ได้ไหม

หลักการ: masked language modeling + next sentence prediction บน Transformer encoder

สิ่งที่เปลี่ยน: encoder pretraining ครอง NLP understanding benchmarks

อ่านเพื่อเข้าใจ: ความต่าง decoder LLM กับ encoder representation model

### 04_Language_Models_are_Unsupervised_Multitask_Learners_GPT2.pdf

คำถามหลัก: language model จะเรียน task จาก text ธรรมชาติ โดยไม่ fine-tune ได้ไหม

หลักการ: scale autoregressive LM บน WebText และใช้ prompt เป็น task specification

สิ่งที่เปลี่ยน: zero-shot และ prompt-based task transfer เริ่มชัด

อ่านเพื่อเข้าใจ: จุดเริ่มของ prompt engineering

### 05_Language_Models_are_Few_Shot_Learners_GPT3.pdf

คำถามหลัก: ถ้า scale ใหญ่มากพอ model จะทำ task จากตัวอย่างใน prompt ได้ไหม

หลักการ: GPT-3 175B, in-context learning, few-shot prompting

สิ่งที่เปลี่ยน: LLM กลายเป็น general-purpose interface

อ่านเพื่อเข้าใจ: ทำไม model สมัยใหม่เหมือน "เรียนจาก prompt" ได้

### 06_Scaling_Laws_for_Neural_Language_Models.pdf

คำถามหลัก: performance ของ LM คาดการณ์จาก scale ได้แค่ไหน

หลักการ: loss ลดตาม power law กับ parameters, data, compute

สิ่งที่เปลี่ยน: การสร้าง frontier model กลายเป็น engineering ที่วางแผน compute ได้มากขึ้น

อ่านเพื่อเข้าใจ: เหตุผลที่วงการทุ่ม scale

### 07_Fine_Tuning_Language_Models_from_Human_Preferences.pdf

คำถามหลัก: จะสอน preference ที่ metric เขียนยากให้ LM ได้อย่างไร

หลักการ: human comparisons -> reward model -> RL fine-tuning

สิ่งที่เปลี่ยน: RLHF เริ่มเข้าภาษา

อ่านเพื่อเข้าใจ: reward model และ human preference

### 08_Learning_to_Summarize_from_Human_Feedback.pdf

คำถามหลัก: human preference ดีกว่า metric อย่าง ROUGE ใน summarization ไหม

หลักการ: เก็บ pairwise comparisons ของ summaries แล้ว RL optimize reward model

สิ่งที่เปลี่ยน: แสดง RLHF ใช้ปรับคุณภาพ output จริงใน task ภาษาได้

อ่านเพื่อเข้าใจ: ทำไม alignment ใช้มนุษย์ judge output แทน metric ล้วน

### 09_Training_Compute_Optimal_Large_Language_Models_Chinchilla.pdf

คำถามหลัก: compute budget หนึ่งก้อนควรแบ่งระหว่าง model size กับ data อย่างไร

หลักการ: scale parameters และ tokens ไปด้วยกัน

สิ่งที่เปลี่ยน: โมเดลหลัง Chinchilla train tokens มากขึ้น ไม่ใช่เพิ่ม parameters อย่างเดียว

อ่านเพื่อเข้าใจ: ทำไม data quantity/quality สำคัญพอ ๆ กับ model size

### 10_InstructGPT_Training_LMs_to_Follow_Instructions_with_Human_Feedback.pdf

คำถามหลัก: จะทำให้ GPT ตอบตามเจตนาผู้ใช้ได้อย่างไร

หลักการ: SFT + reward model + PPO/RLHF

สิ่งที่เปลี่ยน: base LM กลายเป็น instruction-following assistant

อ่านเพื่อเข้าใจ: recipe public ของ ChatGPT-style alignment

### 11_Training_a_Helpful_and_Harmless_Assistant_with_RLHF.pdf

คำถามหลัก: จะเทรน assistant ให้ทั้ง helpful และ harmless ได้อย่างไร

หลักการ: preference model, RLHF, online iteration, tradeoff ระหว่าง objectives

สิ่งที่เปลี่ยน: alignment ถูกมองเป็น multi-objective problem

อ่านเพื่อเข้าใจ: พื้นฐาน Claude-style assistant training

### 12_Constitutional_AI_Harmlessness_from_AI_Feedback.pdf

คำถามหลัก: ใช้ AI ช่วย supervise AI ได้ไหมโดยมีหลักการกำกับ

หลักการ: constitution -> self-critique -> revision -> AI feedback/RLAIF

สิ่งที่เปลี่ยน: ลด reliance บน human label สำหรับ harmlessness

อ่านเพื่อเข้าใจ: ทำไม Claude พูดถึง constitution และ principles

### 13_GPT4_Technical_Report.pdf

คำถามหลัก: frontier multimodal LLM มี capability และ safety profile อย่างไร

หลักการ: large-scale Transformer, next-token pretraining, post-training alignment, predictable scaling

สิ่งที่เปลี่ยน: LLM เข้าสู่ระดับ professional benchmark และ multimodal use

อ่านเพื่อเข้าใจ: ขอบเขต public ของ GPT-4

### 14_Direct_Preference_Optimization_DPO.pdf

คำถามหลัก: ทำ preference alignment โดยไม่ต้อง RLHF ซับซ้อนได้ไหม

หลักการ: optimize policy จาก chosen/rejected pairs โดยตรงเทียบกับ reference model

สิ่งที่เปลี่ยน: alignment open-source ง่ายขึ้นและเสถียรขึ้น

อ่านเพื่อเข้าใจ: post-training แบบ preference tuning รุ่นใหม่

### 15_Llama_2_Open_Foundation_and_Fine_Tuned_Chat_Models.pdf

คำถามหลัก: จะเปิดเผย recipe ของ foundation/chat model อย่างรับผิดชอบได้อย่างไร

หลักการ: pretraining + SFT + RLHF + safety tuning + evaluation

สิ่งที่เปลี่ยน: ชุมชน open model ได้ blueprint ที่ชัดขึ้น

อ่านเพื่อเข้าใจ: training stack ของ open chat model

### 16_ReAct_Synergizing_Reasoning_and_Acting_in_Language_Models.pdf

คำถามหลัก: LLM จะคิดและลงมือทำสลับกันได้ไหม

หลักการ: interleaved reasoning traces และ actions พร้อม observation จาก environment/tool

สิ่งที่เปลี่ยน: LLM กลายเป็น agent loop ไม่ใช่ generator รอบเดียว

อ่านเพื่อเข้าใจ: think-act-observe pattern

### 17_Toolformer_Language_Models_Can_Teach_Themselves_to_Use_Tools.pdf

คำถามหลัก: model จะเรียนใช้ tool เองจาก demonstration น้อย ๆ ได้ไหม

หลักการ: self-supervised tool call insertion และ filtering ตามผลต่อ language modeling

สิ่งที่เปลี่ยน: tool use กลายเป็นสิ่งที่เรียนได้ ไม่ใช่ hardcoded ทั้งหมด

อ่านเพื่อเข้าใจ: LLM + API/tool integration

### 18_Tree_of_Thoughts_Deliberate_Problem_Solving_with_LLMs.pdf

คำถามหลัก: reasoning ควรเป็นเส้นเดียวหรือ search ได้

หลักการ: generate/evaluate/search over thoughts

สิ่งที่เปลี่ยน: inference-time planning สำคัญขึ้น

อ่านเพื่อเข้าใจ: การเพิ่ม deliberation โดยไม่ต้องเทรน model ใหม่

### 19_Reflexion_Language_Agents_with_Verbal_Reinforcement_Learning.pdf

คำถามหลัก: agent เรียนจาก trial-and-error โดยไม่ update weights ได้ไหม

หลักการ: verbal reflection + episodic memory

สิ่งที่เปลี่ยน: memory และ self-feedback ช่วยให้ agent improve ใน runtime

อ่านเพื่อเข้าใจ: language-based reinforcement signal

### 20_Voyager_Open_Ended_Embodied_Agent_with_LLMs.pdf

คำถามหลัก: LLM agent เรียนรู้ระยะยาวใน environment เปิดได้ไหม

หลักการ: automatic curriculum + skill library + iterative code refinement

สิ่งที่เปลี่ยน: agent สะสม skill และ explore เองใน Minecraft

อ่านเพื่อเข้าใจ: embodied lifelong learning agent

### 21_Llama_3_Herd_of_Models.pdf

คำถามหลัก: modern open foundation model family ควรถูกสร้างและ evaluate อย่างไร

หลักการ: large-scale pretraining, post-training, multilingual/coding/reasoning/tool use, safety models

สิ่งที่เปลี่ยน: open LLM เข้าใกล้ frontier closed models มากขึ้น

อ่านเพื่อเข้าใจ: modern production LLM stack

### 22_OpenAI_o1_System_Card.pdf

คำถามหลัก: reasoning model ที่ถูก train ด้วย RL มี risk และ safety profile อย่างไร

หลักการ: large-scale RL for chain-of-thought reasoning + safety evaluations

สิ่งที่เปลี่ยน: training เริ่มเน้น reasoning process ไม่ใช่แค่ answer style

อ่านเพื่อเข้าใจ: test-time compute และ reasoning RL

### 23_Deliberative_Alignment_Reasoning_Enables_Safer_Language_Models.pdf

คำถามหลัก: ถ้าให้ model reason กับ safety spec โดยตรง จะปลอดภัยขึ้นไหม

หลักการ: teach explicit safety specifications และ train ให้ reason ก่อนตอบ

สิ่งที่เปลี่ยน: safety alignment ใช้ reasoning เป็นกลไกหลัก

อ่านเพื่อเข้าใจ: alignment สำหรับ reasoning models

### 24_DeepSeek_R1_Incentivizing_Reasoning_Capability_in_LLMs.pdf

คำถามหลัก: reasoning emerge จาก RL บน task ที่ verify ได้หรือไม่

หลักการ: pure RL / staged RL บน math, coding, STEM พร้อม distillation

สิ่งที่เปลี่ยน: ยืนยันว่าการให้ reward ที่ตรวจได้สามารถกระตุ้น reasoning pattern ได้

อ่านเพื่อเข้าใจ: RL-driven reasoning และ R1-Zero

### 25_Claude_Opus_4_and_Sonnet_4_System_Card.pdf

คำถามหลัก: hybrid reasoning model รุ่นใหม่ควรประเมิน safety อย่างไร

หลักการ: pre-deployment safety tests, agentic safety, coding/computer use evals, alignment assessment

สิ่งที่เปลี่ยน: safety evaluation ขยายจาก chatbot ไปสู่ autonomous/agentic behavior

อ่านเพื่อเข้าใจ: Claude รุ่นใหม่ในมุม risk และ deployment

### 26_Human_Level_Control_through_Deep_Reinforcement_Learning_DQN.pdf

คำถามหลัก: agent จะเรียน control จาก sensory input ดิบได้ไหม

หลักการ: convolutional Q-network, replay memory, target network

สิ่งที่เปลี่ยน: deep RL เรียน action policy จาก pixels ได้

อ่านเพื่อเข้าใจ: พื้นฐาน "เลือก action เอง" จาก reward

### 27_AlphaGo_Zero_Mastering_the_Game_of_Go_without_Human_Knowledge.pdf

คำถามหลัก: superhuman strategy เกิดจาก self-play โดยไม่ใช้ human data ได้ไหม

หลักการ: policy/value network + MCTS + self-play loop

สิ่งที่เปลี่ยน: agent กลายเป็นครูของตัวเอง

อ่านเพื่อเข้าใจ: self-improvement จาก environment rule และ reward

### 28_AlphaZero_Mastering_Chess_and_Shogi_by_Self_Play.pdf

คำถามหลัก: self-play RL generalize ไปหลายเกมได้ไหม

หลักการ: algorithm เดียวสำหรับ chess, shogi, Go โดยใช้แค่กฎเกม

สิ่งที่เปลี่ยน: ลด dependence ต่อ handcrafted domain knowledge

อ่านเพื่อเข้าใจ: general reinforcement learning algorithm ใน domain rule-based

### 29_MuZero_Mastering_Atari_Go_Chess_and_Shogi_by_Planning.pdf

คำถามหลัก: agent วางแผนได้ไหมโดยไม่รู้ dynamics จริงของโลก

หลักการ: learned model ทำนาย reward, value, policy สำหรับ search

สิ่งที่เปลี่ยน: model-based planning เข้าใกล้ environment จริงมากขึ้น

อ่านเพื่อเข้าใจ: planning with learned world model

## ภาคผนวก: PDF เพิ่มเติมที่พบในโฟลเดอร์

### siggraph94.pdf

หัวข้อ: evolving virtual creatures

ใจความ: ใช้ genetic algorithms สร้าง morphology และ controller ของสิ่งมีชีวิตเสมือนในโลกฟิสิกส์จำลอง เป็นงาน foundational ของ artificial life และ embodied evolution

เกี่ยวกับโจทย์นี้: พฤติกรรมไม่ถูก animate เป็นสคริปต์ แต่ emerge จาก body, neural controller, physics และ selection

### 1803.10122v4.pdf

หัวข้อ: World Models

ใจความ: agent เรียน representation และ dynamics ของ environment ใน latent space แล้วใช้ controller ตัดสินใจ

เกี่ยวกับโจทย์นี้: "เลือกเอง" ดีขึ้นเมื่อ agent มี model ภายในของโลก ไม่ใช่ react จาก observation ดิบอย่างเดียว

### 1901.08706v2.pdf

หัวข้อ: emergent linguistic phenomena in multi-agent communication games

ใจความ: ศึกษาภาษาหรือ protocol ที่เกิดจาก multi-agent learning เมื่อ agent ต้องสื่อสารเพื่อแก้ task

เกี่ยวกับโจทย์นี้: communication สามารถ emerge จาก reward pressure ได้ แต่ไม่ได้รับประกันว่าจะเหมือนภาษามนุษย์

### 2302.14276v1.pdf

หัวข้อ: emergent communication for social learning in multi-agent RL

ใจความ: สื่อสารและเรียนรู้จาก agent อื่นช่วยเพิ่ม social learning และ coordination

เกี่ยวกับโจทย์นี้: ถ้าอยากให้ AI หลายตัวเรียนร่วมกัน ต้องออกแบบ reward/environment ให้ communication มีประโยชน์จริง

### 2501.00226v2.pdf

หัวข้อ: Generative Emergent Communication

ใจความ: มอง LLM ในฐานะ collective world model ที่เกิดจากการสะสม pattern ภาษา/ความรู้/ประสบการณ์ของสังคม

เกี่ยวกับโจทย์นี้: ภาษาช่วย compress และถ่ายทอด world model ระหว่าง agent ได้

## เส้นเชื่อม: จาก token prediction ไปสู่ agent ที่เลือก action

LLM แบบ base model เลือก token ถัดไป ไม่ได้เลือก action ในโลกโดยตรง:

```text
context -> next token
```

แต่เมื่อเราเพิ่ม tool, memory, environment และ goal เข้าไป token บางตัวกลายเป็น action command:

```text
goal + observation + memory -> thought -> action/tool call -> observation ใหม่
```

จากนั้น action loop นี้สามารถถูกปรับด้วย:

- supervised examples: ตัวอย่างวิธีทำงาน
- preference learning: คนหรือ AI เลือก trajectory/answer ที่ดีกว่า
- reward: environment บอกสำเร็จ/ล้มเหลว
- search: ลองหลายทางแล้วเลือกทางที่ดีที่สุด
- memory: จำข้อผิดพลาดและ skill ที่เคยทำสำเร็จ

ดังนั้นระบบอย่าง ChatGPT/Claude ที่ใช้ tool หรือ computer use ไม่ใช่สคริปต์ตายตัว แต่ก็ไม่ใช่อิสระสมบูรณ์ มันคือ learned policy/controller ที่ถูกจำกัดด้วย training, prompt, system policy, tool API, safety layer และ environment feedback

## ถ้าต้องอ่านเพื่อสร้างระบบเอง

อ่านตามเป้าหมาย:

### อยากเข้าใจ LLM training

1. `01_Attention_Is_All_You_Need.pdf`
2. `02_Improving_Language_Understanding_by_Generative_Pre_Training_GPT1.pdf`
3. `05_Language_Models_are_Few_Shot_Learners_GPT3.pdf`
4. `06_Scaling_Laws_for_Neural_Language_Models.pdf`
5. `09_Training_Compute_Optimal_Large_Language_Models_Chinchilla.pdf`

### อยากเข้าใจ ChatGPT/Claude alignment

1. `07_Fine_Tuning_Language_Models_from_Human_Preferences.pdf`
2. `08_Learning_to_Summarize_from_Human_Feedback.pdf`
3. `10_InstructGPT_Training_LMs_to_Follow_Instructions_with_Human_Feedback.pdf`
4. `11_Training_a_Helpful_and_Harmless_Assistant_with_RLHF.pdf`
5. `12_Constitutional_AI_Harmlessness_from_AI_Feedback.pdf`
6. `14_Direct_Preference_Optimization_DPO.pdf`

### อยากเข้าใจ AI เลือก action เอง

1. `26_Human_Level_Control_through_Deep_Reinforcement_Learning_DQN.pdf`
2. `27_AlphaGo_Zero_Mastering_the_Game_of_Go_without_Human_Knowledge.pdf`
3. `28_AlphaZero_Mastering_Chess_and_Shogi_by_Self_Play.pdf`
4. `29_MuZero_Mastering_Atari_Go_Chess_and_Shogi_by_Planning.pdf`
5. `16_ReAct_Synergizing_Reasoning_and_Acting_in_Language_Models.pdf`
6. `20_Voyager_Open_Ended_Embodied_Agent_with_LLMs.pdf`

### อยากเข้าใจ reasoning model ล่าสุด

1. `22_OpenAI_o1_System_Card.pdf`
2. `23_Deliberative_Alignment_Reasoning_Enables_Safer_Language_Models.pdf`
3. `24_DeepSeek_R1_Incentivizing_Reasoning_Capability_in_LLMs.pdf`
4. `25_Claude_Opus_4_and_Sonnet_4_System_Card.pdf`

## สรุปเชิงหลักการสุดท้าย

วิวัฒนาการจาก paper ทั้งหมดคือ:

1. เราเริ่มจาก agent ที่เลือก action ด้วย RL ใน environment ชัดเจน
2. Transformer ทำให้ scale language model ได้
3. GPT/BERT แสดงว่า pretraining จาก text สร้าง general representation/capability
4. Scaling laws ทำให้การเพิ่มขนาดเป็นศาสตร์ที่คาดการณ์ได้
5. RLHF ทำให้ model ที่ทำนาย text เก่งกลายเป็น assistant ที่มนุษย์ prefer
6. Constitutional AI และ DPO ทำให้ alignment scale และ simplify ได้มากขึ้น
7. ReAct/Toolformer/ToT/Reflexion/Voyager เปลี่ยน LLM จาก responder เป็น agent loop
8. o1/DeepSeek-R1 แสดงว่าการเทรนด้วย RL สามารถผลัก reasoning process ได้โดยตรง
9. Claude 4 system card ชี้ว่ายุคต่อไปต้องประเมิน agentic risk ไม่ใช่แค่คุณภาพคำตอบ

แก่นของ "ไม่ใช่สคริปต์" คือระบบไม่ได้ถูกกำหนดคำตอบหรือ action ทุกกรณีไว้ล่วงหน้า แต่เรียนฟังก์ชันการเลือกจากข้อมูลและ feedback:

```text
training data + objective + feedback + architecture + environment -> learned policy
```

แต่แก่นของ "ยังไม่ใช่อิสระจริงแบบสิ่งมีชีวิต" คือ policy นั้นยังอยู่ภายใต้ objective, distribution, tool boundary, safety policy และ reward/preference ที่มนุษย์หรือระบบออกแบบไว้

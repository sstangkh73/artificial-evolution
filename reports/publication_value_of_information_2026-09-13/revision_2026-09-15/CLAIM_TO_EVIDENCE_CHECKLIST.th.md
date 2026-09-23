# Revision claim-to-evidence checklist

อัปเดตสถานะ: 2026-09-17 หลัง reproduce ตัวเลขจาก raw dumps, ตรวจ manuscript/figures และรัน verification รอบสุดท้าย รายการที่ระบุว่า `ผ่าน` มีหลักฐาน authoritative ตามคอลัมน์กลาง; รายการผู้เขียน/คลังข้อมูลยังคงเป็น submission blocker

## Critical claims

| ID | สิ่งที่ต้องตรวจ | หลักฐาน authoritative ที่ต้องสร้าง | สถานะ |
|---|---|---|---|
| C1 | Energy 10 เป็นจุดที่ `0.6 x 10 > 5`, staple acceptance เปลี่ยน regime, mortality ชน senescence ceiling และ slope ไวต่อ endpoint 10 | `mechanism_analysis.json`, `e6_seed_mechanisms.csv`, `e6_paired_contrasts.csv` | ผ่าน—รายงานเป็น regime change/confounding ไม่ใช่กลไกที่แยกได้ |
| C2 | Primary B2-B3 เป็นลบที่พลังงาน 4-8; slope บวกแต่ไม่ผ่าน SESOI 1; B2-B1 เป็นผลรอง | `mechanism_analysis.json`, frozen `E6_analysis.json` | ผ่าน—รายงาน registered test และ post hoc sensitivity แยกกัน |
| C3 | A3/A3O/A3R มี learned net fruit value 6, acceptance 1; realized dose และ A3O-A3R ต่างจริงเพียงใด; B2/B3 แบ่ง key ของ staple | `mechanism_analysis.json`, `t2rb_seed_mechanisms.csv`, `learned_values_by_key.csv` | ผ่าน—A3O/A3R ต่างด้าน toxin damage 2.865% ไม่ใช่ 3.6% ตามคำวิจารณ์เดิม |
| C4 | Intake/dose สัมพันธ์กับ follow-up อย่างไร และ telemetry แยก starvation-override meal ได้หรือไม่ | `mechanism_analysis.json`; limitation audit ใน manuscript | ผ่านแบบมีข้อจำกัด—เพิ่ม rate-based post hoc correlations และเตือน denominator bias; ยังแยก starvation-override meal และ causal path ไม่ได้ |

## Major issues

| ID | สิ่งที่ต้องแก้ | หลักฐาน/ตำแหน่งปลายทาง | สถานะ |
|---|---|---|---|
| M1 | รายงาน secondary outcomes ที่ frozen protocol สัญญาไว้ | supplementary source-data CSV และ Results/Supplement | ผ่าน |
| M2 | คืนถ้อยคำ prediction เดิมและให้ verdict ตรงผล; เปิดเผย deviation | `prediction_audit.csv`, `deviation_audit.csv`, manuscript | ผ่าน |
| M3 | รายงาน systematic age-blind offset ของ D โดยไม่ตั้งชื่อเป็น structural noise floor และไม่ตีความเครื่องหมาย B1/B3 | mechanism JSON และ Discussion | ผ่าน—ระบุว่าต้นเหตุยังไม่ทราบ |
| M4 | ใช้ seed เป็นหน่วยอิสระ, paired CI/effect size; รายงาน observed-SD sensitivity | mechanism JSON, Methods, Results | ผ่าน |
| M5 | เปิดเผย encounter-gate ambiguity และ timing | `deviation_audit.csv`, Methods/Limitations | ผ่าน |
| M6 | ใช้คำว่า internally frozen แทน public preregistration claim | Methods/Provenance | ผ่าน |
| M7 | จัดโครงเรื่อง E2 -> E6 -> T2-RB; E1 เป็น context; ย่อ E3/E4 | manuscript | ผ่าน |
| M8 | ระบุข้อจำกัดของ pickiness, starvation, learning rate, bin/cap และ toxin coefficients | Limitations | ผ่าน |
| M9 | เพิ่มวรรณกรรมเฉพาะเมื่อเปิดตรวจ metadata จากแหล่งต้นฉบับแล้ว | `references.bib`, literature matrix | ผ่าน—ledger ระบุระดับหลักฐานที่ตรวจจริง ไม่อ้าง metadata ว่าเป็น full-text review |

## Figure issues

| รูป | เกณฑ์ผ่าน | สถานะ |
|---|---|---|
| Figure 1 | information-rescue figure ถูกอ้างก่อนและ caption อธิบาย attained-age/follow-up equivalence | ผ่าน visual QA |
| Figure 2 | energy-gradient figure แสดง continuous boundary 8.33 ระหว่างพลังงานที่ทดสอบ 8 และ 10 | ผ่าน visual QA |
| Figure 3 | hidden-toxicity annotation ไม่ทับข้อมูล; caption ระบุ constant payoff/acceptance ของ A3 | ผ่าน visual QA |
| Figure 4 | R-B markers dodge; gray-line legend; SESOI ไม่ทับจุด | ผ่าน visual QA |
| Figure 5 | selection/denominator labels ไม่ถูกตัด | ผ่าน visual QA |

## Round 2 closure (2026-09-17)

| ประเด็น | สถานะ |
|---|---|
| R1-R2: systematic offset และ causal wording | ผ่าน—ไม่เรียก offset ว่า noise floor; ใช้ถ้อยคำว่าไม่พบ detected survival advantage และไม่อ้างว่าแยก interaction เชิงสาเหตุได้ |
| R3: rate-based intake analysis | ผ่าน—เพิ่ม four post hoc correlations พร้อม denominator-bias warning |
| R4: ลำดับรูปตาม first citation | ผ่าน—Figure 1-5 เรียงตามการอ้างครั้งแรก และมี automated audit |
| R5-R7: boundary, annotation, table/math typography | ผ่าน—boundary = 8.33; starvation override ไม่ถูกอ้างเป็นต้นเหตุของ boundary; แก้ annotation และรูปแบบตาราง/สัญลักษณ์ |
| R8-R9: neutral supplement และ Claude disclosure | ผ่าน—เปลี่ยนชื่อ supplement; เอาภาษากระบวนการ review ออกจากเอกสารส่ง; ระบุ Claude Opus 5/model ID/Claude Code และวันที่ใช้งาน |
| R10: journal length check | ผ่านแบบมีเงื่อนไข—แนวทางปัจจุบันระบุบทความโดยทั่วไป 6,000-12,000 คำ และไม่พบ abstract cap แยกต่างหากในหน้าคำแนะนำ; audit ภายในยังจำกัด abstract ที่ 250 คำ |
| R11-R12: Methods promises และ naming/age note | ผ่าน—ชี้ตำแหน่ง probability/key-level data และเพิ่มหมายเหตุ attained age เทียบกับ follow-up |

## Submission blockers that require author or external action

| รายการ | ผู้ยืนยัน | สถานะ |
|---|---|---|
| Funding statement | ผู้เขียน | ยังไม่ยืนยัน |
| Competing interests | ผู้เขียน | ยังไม่ยืนยัน |
| Ethics statement | ผู้เขียน | ยังไม่ยืนยัน |
| CRediT roles | ผู้เขียน | ยังไม่ยืนยัน |
| Final AI disclosure approval | ผู้เขียน | ยังไม่ยืนยัน |
| Public archive DOI and download-back hash | ผู้เขียน/คลังข้อมูล | ยังไม่มี |

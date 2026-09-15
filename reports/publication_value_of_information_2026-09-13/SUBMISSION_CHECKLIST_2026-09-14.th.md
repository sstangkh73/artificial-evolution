# Checklist ก่อนส่ง *Artificial Life*

อ้างอิงข้อกำหนดวารสารที่ตรวจเมื่อ 2026-09-14: `https://direct.mit.edu/artl/pages/submission-guidelines` และนโยบาย AI ของวารสาร `https://direct.mit.edu/artl/article/29/2/141/116359/Editorial-What-Have-Large-Language-Models-and`

## สถานะปัจจุบัน

| รายการ | ข้อกำหนด/เหตุผล | สถานะ | งานถัดไป |
|---|---|---|---|
| ประเภทบทความ | Article โดยทั่วไป 6,000–12,000 คำ | ผ่าน: 6,901 คำตั้งแต่ abstract ถึง declarations โดยไม่รวม references/figure captions; 7,407 คำเมื่อรวม references และข้อมูลหน้าปก | ผู้เขียนตรวจว่าระบบส่งนับคำด้วยหลักเดียวกัน |
| ความเหมาะสมกับวารสาร | ต้องอธิบายใน cover letter | ร่างแล้วและใส่ข้อมูลติดต่อแล้ว | ผู้เขียนตรวจถ้อยคำและเติมวันส่ง |
| initial submission | ส่ง manuscript เป็น PDF ผ่าน ScholarOne | author-review PDF 35 หน้า; source ตรงกับ PDF ไม่มีโน้ตภายใน และแทรกรูป vector ทั้ง 5 ใกล้ Results ที่เกี่ยวข้อง | เติม DOI/คำรับรอง แล้วสร้าง PDF ใหม่และรัน audit จน `pdf.status` เป็น PASS |
| หน้าปก | title, author, affiliation/address/email, corresponding author, abstract, 5–6 keywords | ข้อมูลผู้เขียนทั้ง 5 ช่องยืนยันแล้วเมื่อ 15 กันยายน 2026 และใส่ใน PDF; keywords มี 6 คำ | คัดลอกข้อมูลเดียวกันลงระบบส่งและตรวจ proof |
| ความใหม่/ไม่ส่งซ้ำ | ผู้เขียนรับรองว่าไม่ตีพิมพ์หรืออยู่ระหว่างพิจารณาที่อื่น | รอผู้เขียนรับรอง | ยืนยันใน cover letter/ระบบส่ง |
| เนื้อหาหลัก | ต้นฉบับ Article ฉบับเต็ม | automated scientific audit ผ่าน; source และ PDF เหลือ placeholder 6 รายการใน declarations/archive | author line-by-line verification และปิด placeholder ที่เหลือ |
| รูป | แนะนำ vector สำหรับกราฟ/diagram | พร้อม | ใช้ PDF vector ทั้ง 5 รูปเป็น master; PNG 300 dpi ใช้ preview เท่านั้น |
| figure source data | ต้องตรวจย้อนกลับได้ | พร้อม 8 ตาราง | ตรวจ caption/เลขรูปหลังจัดหน้า |
| supplementary material | ต้องแนบพร้อมบทความหรือให้ URL ที่ไม่กระทบ anonymity | โครงสร้างพร้อม | รวม ODD, parameter/state/version/reproduction files เป็น reviewer package |
| data/code policy | ทำข้อมูลที่รองรับข้อสรุปให้เข้าถึงได้และ cite ในบทความ | 5 ZIP พร้อมในเครื่องและตรวจสมาชิก 696 ไฟล์แล้ว | ผู้เขียนฝาก package ออก DOI ดาวน์โหลดกลับ และตรวจซ้ำ |
| reproducibility | reviewer ต้องรันและตรวจได้ | internal deterministic smoke ผ่าน | ให้บุคคลอื่นทำ protocol และลงชื่อผล; ห้ามเรียก independent ก่อนสำเร็จ |
| citations | APA 7 และทุก claim ต้องอยู่ในขอบเขตหลักฐานที่ตรวจ | 11 แหล่งวิชาการและ 1 รายการเครื่องมือ AI; 6 แหล่งมาจาก *Artificial Life*; แหล่งวิชาการที่อ้างทั้งหมดตรวจฉบับเต็มแล้ว | ผู้เขียนตรวจ metadata/หน้า/DOI/URL รอบสุดท้าย |
| AI disclosure | ทุกการใช้ generative AI ต้องระบุชัดและอ้างแหล่ง/เวอร์ชัน/วันที่ | ร่าง disclosure พร้อมชื่อ รุ่น URL วันที่ งานที่ใช้ และ formal citation แล้ว | ผู้เขียนตรวจ AI log, เติมการใช้ที่อาจตกหล่น และอนุมัติข้อความใน manuscript/cover letter |
| funding | ต้องรายงานตามจริง | ไม่ทราบ | ผู้เขียนเติม “no specific funding” หรือรายละเอียดทุนตามจริง |
| competing interests | ต้องรายงานตามจริง | ไม่ทราบ | ผู้เขียนเติม statement |
| ethics | งานจำลองล้วนคาดว่าไม่ต้อง ethics approval | รอผู้เขียนยืนยัน | ระบุว่าไม่มี human/live-animal subjects หากเป็นจริง |
| third-party permissions | ต้องขอสิทธิ์ถ้ามีภาพ/เนื้อหาภายนอก | รูปปัจจุบันสร้างจากข้อมูลของโครงการ | ผู้เขียนยืนยันว่าไม่มี third-party figure material |
| final accepted package | PDF, Word/LaTeX source, figure แยก, forms | ยังไม่ถึงขั้นนี้ | เตรียมหลังผ่าน review; ไม่ต้องทำ forms ตอน initial submission |

## ไฟล์ที่พร้อมใช้

- `manuscript_v0.en.md` — ต้นฉบับฉบับเต็ม
- `submission/manuscript_initial_submission_draft.pdf` — author-review PDF 35 หน้าแบบ single-column, double-spaced พร้อม Table 1 และรูป vector 5 หน้าที่แทรกใน Results; ยังมี placeholder 6 รายการที่ห้ามส่ง
- `submission/manuscript_submission_audit.json` — ผลตรวจจำนวนคำ abstract keywords รูป citation ตัวเลข confirmatory และ placeholder
- `cover_letter_draft.en.md` — cover letter ที่ใส่ข้อมูลผู้เขียนแล้ว แต่ยังต้องเติมวันส่ง DOI และคำรับรอง
- `ODD_MODEL_DESCRIPTION_DRAFT.en.md` — model description
- `supplement/PARAMETER_TABLES.en.md` และ CSV — parameter provenance
- `supplement/STATE_VARIABLE_CATALOGUE.en.md` — focal state/process catalogue
- `supplement/CODE_VERSION_AUDIT.en.md` — audit ความต่าง 5 run revisions
- `supplement/INDEPENDENT_REPRODUCTION_PROTOCOL.en.md` — ขั้นตอนตรวจโดยบุคคลอื่น
- `supplement/PUBLIC_ARCHIVE_MANIFEST.en.md` พร้อม JSON inventory และ SHA-256 — ขอบเขต release 5 bundles, 696 ไฟล์
- `output/publication_release_2026-09-14/` — ชุดอัปโหลด 5 ZIP พร้อม package-level checksum; ไม่เก็บ ZIP ซ้ำใน Git
- `confirmatory/` — analysis, validators, source data, figures และ checksum manifest
- `AI_USE_LOG.md` — บันทึกการใช้ generative AI

## Gate ที่ต้องผ่านก่อนกดส่ง

1. ผู้เขียนตรวจทุกบรรทัดของต้นฉบับ ตัวเลข ตาราง รูป และ reference โดยเปิดหลักฐานต้นทางประกอบ
2. บุคคลอื่นรัน independent reproduction protocol แล้วได้ `PASS` พร้อมบันทึกชื่อ ระบบ และ hash
3. ฝาก reviewer-safe public archive/DOI ตาม manifest แล้วตรวจ release checksum 696 รายการหลังดาวน์โหลดกลับ (checksum เดิม 616 รายการเป็น core subset)
4. เติม Data and Code Availability และ AI Disclosure ในต้นฉบับด้วย URL/DOI และข้อความที่ผู้เขียนอนุมัติ
5. เติม funding, conflict และ ethics statements
6. จัดหน้า PDF แบบ single-column double-spaced ฝังรูป vector ตรวจทุกหน้า และนับคำครั้งสุดท้าย
7. ตรวจว่า cover letter อธิบาย scope fit รับรองความใหม่ และเปิดเผย AI ตรงกับต้นฉบับ
8. อัปโหลด manuscript, cover letter และ supplement พร้อมกัน แล้วเปิดไฟล์จากระบบส่งเพื่อตรวจอีกครั้งก่อน submit

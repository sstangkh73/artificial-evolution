# Checklist ก่อนส่ง *Artificial Life*

อ้างอิงข้อกำหนดวารสารและนโยบาย MIT Press ที่ตรวจซ้ำเมื่อ 2026-09-16: `https://direct.mit.edu/artl/pages/submission-guidelines`, `https://direct.mit.edu/journals/pages/authors` และนโยบาย AI ของวารสาร `https://direct.mit.edu/artl/article/29/2/141/116359/Editorial-What-Have-Large-Language-Models-and`

## สถานะปัจจุบัน

| รายการ | ข้อกำหนด/เหตุผล | สถานะ | งานถัดไป |
|---|---|---|---|
| ประเภทบทความ | Article โดยทั่วไป 6,000-12,000 คำ | ผ่าน: audit ปัจจุบันนับ 7,868 คำตั้งแต่ abstract ถึง declarations โดยไม่รวม references/figure captions; 8,473 คำเมื่อรวม references; 7,526 คำตั้งแต่ abstract ถึง conclusion; abstract 249 คำ | ผู้เขียนตรวจว่าระบบส่งนับคำด้วยหลักเดียวกัน |
| ความเหมาะสมกับวารสาร | ต้องอธิบายใน cover letter | ร่างแล้วและใส่ข้อมูลติดต่อแล้ว | ผู้เขียนตรวจถ้อยคำและเติมวันส่ง |
| initial submission | ส่ง manuscript เป็น PDF ผ่าน ScholarOne | author-review PDF 37 หน้า; source ตรงกับ PDF ไม่มีโน้ตภายใน และแทรกรูป vector ทั้ง 5 ใกล้ Results ที่เกี่ยวข้อง; `pdf.status` ยัง FAIL เพราะมี placeholder 4 จุด | เติม DOI/คำรับรอง แล้วสร้าง PDF ใหม่และรัน audit จน `pdf.status` เป็น PASS |
| หน้าปก | title, author, affiliation/address/email, corresponding author, abstract, 5–6 keywords | ข้อมูลผู้เขียนทั้ง 5 ช่องยืนยันแล้วเมื่อ 15 กันยายน 2026 และใส่ใน PDF; keywords มี 6 คำ | คัดลอกข้อมูลเดียวกันลงระบบส่งและตรวจ proof |
| ความใหม่/ไม่ส่งซ้ำ | ผู้เขียนรับรองว่าไม่ตีพิมพ์หรืออยู่ระหว่างพิจารณาที่อื่น | รอผู้เขียนรับรอง | ยืนยันใน cover letter/ระบบส่ง |
| เนื้อหาหลัก | ต้นฉบับ Article ฉบับเต็ม | major rewrite ตาม Red Team เสร็จและ automated scientific audit ผ่าน; source/PDF ยังมี placeholder 4 รายการใน declarations/archive | author line-by-line verification และปิด placeholder ที่เหลือ |
| รูป | แนะนำ vector สำหรับกราฟ/diagram | พร้อม | ใช้ PDF vector ทั้ง 5 รูปเป็น master; PNG 300 dpi ใช้ preview เท่านั้น |
| figure source data | ต้องตรวจย้อนกลับได้ | สร้างรูป vector/PNG ใหม่ครบ 5 รูป พร้อม source tables เดิมและ revision CSV/JSON ชุดกลไก | ผู้เขียนตรวจ caption และ interpretation รอบสุดท้าย |
| supplementary material | ต้องแนบพร้อมบทความหรือให้ URL ที่ไม่กระทบ anonymity | โครงสร้างพร้อม | รวม ODD, parameter/state/version/reproduction files เป็น reviewer package |
| data/code policy | ทำข้อมูลที่รองรับข้อสรุปให้เข้าถึงได้และ cite ในบทความ | revision inventory ตรวจ 52 artifacts และ rehash raw 600 ไฟล์ผ่านแล้ว; pre-revision 5 ZIP/696-file inventory ยังไม่ใช่ package ของต้นฉบับรอบนี้ | หลังผู้เขียนปิดข้อความ ให้ rebuild 5 bundles ฝาก DOI ดาวน์โหลดกลับ และตรวจซ้ำ |
| reproducibility | reviewer ต้องรันและตรวจได้ | internal deterministic smoke ผ่าน | ให้บุคคลอื่นทำ protocol และลงชื่อผล; ห้ามเรียก independent ก่อนสำเร็จ |
| citations | APA 7 และทุก claim ต้องอยู่ในขอบเขตหลักฐานที่ตรวจ | 15 แหล่งวิชาการและ 2 รายการเครื่องมือ AI; 6 แหล่งมาจาก *Artificial Life*; แหล่งที่เพิ่มใน revision ตรวจ metadata จาก publisher/repository records แล้ว | ผู้เขียนเปิดตรวจฉบับเต็มและยืนยัน metadata/หน้า/DOI/URL รอบสุดท้าย |
| AI disclosure | ทุกการใช้ generative AI ต้องระบุชัดและอ้างแหล่ง/เวอร์ชัน/วันที่ | อัปเดต disclosure และ AI log ถึง 23 กันยายน 2026 แล้ว; session วันที่ 23 ระบุอย่างโปร่งใสว่า task transcript ไม่แสดง model identifier | ผู้เขียนตรวจ model identifier จาก UI ถ้ามี เติมการใช้ที่อาจตกหล่น และอนุมัติข้อความใน manuscript/cover letter |
| funding | ต้องรายงานตามจริง | ไม่ทราบ | ผู้เขียนเติม “no specific funding” หรือรายละเอียดทุนตามจริง |
| competing interests | ต้องรายงานตามจริง | ไม่ทราบ | ผู้เขียนเติม statement |
| ethics | งานจำลองล้วนและไม่มี human/live-animal subjects ตาม Methods | ใส่ ethics statement ใน manuscript แล้ว | ผู้เขียนตรวจยืนยันก่อนส่ง |
| third-party permissions | ต้องขอสิทธิ์ถ้ามีภาพ/เนื้อหาภายนอก | รูปปัจจุบันสร้างจากข้อมูลของโครงการ | ผู้เขียนยืนยันว่าไม่มี third-party figure material |
| final accepted package | PDF, Word/LaTeX source, figure แยก, forms | ยังไม่ถึงขั้นนี้ | เตรียมหลังผ่าน review; ไม่ต้องทำ forms ตอน initial submission |

## ไฟล์ที่พร้อมใช้

- `manuscript_v0.en.md` — ต้นฉบับฉบับเต็ม
- `submission/manuscript_initial_submission_draft.pdf` — author-review PDF 37 หน้าแบบ single-column, double-spaced รวม figure captions พร้อมตารางหลัก 3 ตารางและรูป vector 5 หน้าที่แทรกใน Results; ยังมี placeholder 4 รายการที่ห้ามส่ง
- `submission/manuscript_submission_audit.json` — ผลตรวจจำนวนคำ abstract keywords รูป citation ตัวเลข confirmatory และ placeholder
- `cover_letter_draft.en.md` — cover letter ที่ใส่ข้อมูลผู้เขียนแล้ว แต่ยังต้องเติมวันส่ง DOI และคำรับรอง
- `ODD_MODEL_DESCRIPTION_DRAFT.en.md` — model description
- `supplement/PARAMETER_TABLES.en.md` และ CSV — parameter provenance
- `supplement/STATE_VARIABLE_CATALOGUE.en.md` — focal state/process catalogue
- `supplement/CODE_VERSION_AUDIT.en.md` — audit ความต่าง 5 run revisions
- `supplement/INDEPENDENT_REPRODUCTION_PROTOCOL.en.md` — ขั้นตอนตรวจโดยบุคคลอื่น
- `supplement/PUBLIC_ARCHIVE_MANIFEST.en.md` — ขอบเขต release 5 bundles; package 696 ไฟล์เดิมเป็น pre-revision baseline
- `output/publication_release_2026-09-14/` — ชุดอัปโหลด 5 ZIP พร้อม package-level checksum; ไม่เก็บ ZIP ซ้ำใน Git
- `confirmatory/` — analysis, validators, source data, figures และ checksum manifest
- `AI_USE_LOG.md` — บันทึกการใช้ generative AI
- `revision_2026-09-15/` — baseline manifest, claim-to-evidence checklist, mechanism report, prediction/deviation audits และ revision source tables
- `revision_2026-09-15/revision_release_inventory.json` และ `revision_release_checksums.sha256` — ตรวจ 52 revision artifacts และยืนยัน raw baseline 600 ไฟล์

## Gate ที่ต้องผ่านก่อนกดส่ง

1. ผู้เขียนตรวจทุกบรรทัดของต้นฉบับ ตัวเลข ตาราง รูป และ reference โดยเปิดหลักฐานต้นทางประกอบ
2. บุคคลอื่นรัน independent reproduction protocol แล้วได้ `PASS` พร้อมบันทึกชื่อ ระบบ และ hash
3. หลังปิด declarations/disclosure แล้ว rebuild 5 release bundles จาก revision inventory ฝาก reviewer-safe public archive/DOI และตรวจ checksum หลังดาวน์โหลดกลับ (pre-revision inventory 696 ไฟล์และ core checksum 616 รายการใช้เป็น baseline เท่านั้น)
4. เติม Data and Code Availability และ AI Disclosure ในต้นฉบับด้วย URL/DOI และข้อความที่ผู้เขียนอนุมัติ
5. ผู้เขียนยืนยัน funding, conflict, ethics และ CRediT statements
6. จัดหน้า PDF แบบ single-column double-spaced ฝังรูป vector ตรวจทุกหน้า และนับคำครั้งสุดท้าย
7. ตรวจว่า cover letter อธิบาย scope fit รับรองความใหม่ และเปิดเผย AI ตรงกับต้นฉบับ
8. อัปโหลด manuscript, cover letter และ supplement พร้อมกัน แล้วเปิดไฟล์จากระบบส่งเพื่อตรวจอีกครั้งก่อน submit

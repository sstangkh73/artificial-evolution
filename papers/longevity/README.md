# papers/longevity — งานวิจัยเรื่องอายุขัยของมนุษย์

โฟลเดอร์นี้รวบรวมงานวิจัยเรื่อง "อายุขัยขึ้นอยู่กับอะไร" เพื่อนำมาออกแบบกลไก aging/lifespan
ในโมเดลจำลอง ALife ของโครงงาน (artificial-evolution → YSC/ISEF)

## ไฟล์ในโฟลเดอร์
| ไฟล์ | คืออะไร |
|------|---------|
| **`human_lifespan_determinants_review.md`** | 📌 **รายงานสรุปหลัก** — สรุปทุกเปเปอร์อย่างละเอียด + ระดับความเชื่อมั่น + วิธีนำไปใช้ในซิม |
| `download_pdfs.ps1` | สคริปต์ดึง PDF (รันบนเครื่องคุณ — ดูด้านล่าง) |
| `README.md` | ไฟล์นี้ |
| `*.pdf` | ตัวเปเปอร์ (ต้องรันสคริปต์/โหลดเองก่อน — ดูด้านล่าง) |

## ⚠️ ทำไมยังไม่มี PDF ในโฟลเดอร์
สภาพแวดล้อม sandbox ที่ Claude รันอยู่ **บล็อกการดาวน์โหลดไฟล์ binary** (endpoint ที่เสิร์ฟ PDF
โดน block/robot-page/404 หมด — ทดสอบแล้วทั้ง PMC, EuropePMC, FTP tarball, bioRxiv) จึง **ไม่สร้าง
ไฟล์ PDF ปลอม** ไว้ให้ ตัวเนื้อหางานวิจัยสรุปครบอยู่ใน `human_lifespan_determinants_review.md` แล้ว

## วิธีได้ PDF จริง (เลือกอย่างใดอย่างหนึ่ง)

### วิธี A — รันสคริปต์ (สะดวก แต่บาง publisher อาจบล็อก)
```powershell
cd C:\artificial-evolution\papers\longevity
./download_pdfs.ps1
```
จะพยายามโหลดฉบับ Open Access/free ให้อัตโนมัติ แล้วสรุปว่าอันไหนสำเร็จ/อันไหนต้องโหลดเอง

### วิธี B — โหลดเองผ่าน browser (การันตีได้ผลเสมอ)
เปิดลิงก์แล้วกดปุ่ม **Download PDF** บนหน้าเว็บ:

**Open Access (โหลดฟรีได้แน่นอน):**
- #2 Stenholm 2016 (lifestyle → disease-free LE): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6937009/
- #6 Yuan 2023 (body size / trade-offs review): https://pmc.ncbi.nlm.nih.gov/articles/PMC10792675/
- #9 Kitazoe 2017 (mitochondria & longevity): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5666079/
- #11 CALERIE 2023 (pace of aging, abstract): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10737863/

**Free-to-read (ฟรีแต่บางทีต้องกดผ่านหน้า publisher):**
- #7 Speakman 2005 (body size, metabolism, lifespan): https://journals.biologists.com/jeb/article/208/9/1717/9377/
- #8 Hulbert 2007 (metabolic rate, membrane, life span): https://journals.physiology.org/doi/full/10.1152/physrev.00047.2006

**Paywall (ต้องมีสิทธิ์เข้าถึงผ่านโรงเรียน/ห้องสมุด — หรืออ่านสรุปในรายงานพอ):**
- #1 Li 2018 (Circulation): https://pmc.ncbi.nlm.nih.gov/articles/PMC6207481/
- #3 Herskind 1996 (Hum Genet): https://pubmed.ncbi.nlm.nih.gov/8786073/
- #4 Heritability 2025 (Science): https://www.science.org/doi/10.1126/science.adz1187
- #5 Kirkwood 1977 (Nature): https://www.nature.com/articles/270301a0
- #10 Ravussin 2015 (CALERIE): https://pmc.ncbi.nlm.nih.gov/articles/PMC4841173/
- #12 López-Otín 2013 (Cell): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3836174/
- #13 López-Otín 2023 (Cell): https://pubmed.ncbi.nlm.nih.gov/36599349/

> เลขที่ (#) ตรงกับตารางอ้างอิงในรายงานหลัก `human_lifespan_determinants_review.md`

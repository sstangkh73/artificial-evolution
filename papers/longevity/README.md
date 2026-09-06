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















(async () => {
  const CONFIG = {
    DRY_RUN: true,          // ตรวจสอบก่อน แล้วเปลี่ยนเป็น false
    MAX_UNFOLLOW: 9999,     // เปลี่ยนเป็น 30–50 หากต้องการทำเป็นรอบ
    DELAY_MIN: 3000,
    DELAY_MAX: 6000,
    MAX_STUCK_ROUNDS: 8
  };

  window.stopTikTokUnfollow = false;

  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const normalize = value => String(value || "").trim().toLowerCase();
  const randomDelay = () =>
    CONFIG.DELAY_MIN +
    Math.random() * (CONFIG.DELAY_MAX - CONFIG.DELAY_MIN);

  const isVisible = element => {
    const rect = element.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };

  const followingLabels = new Set([
    "following",
    "กำลังติดตาม",
    "กำลังติดตามอยู่",
    "ติดตามแล้ว"
  ]);

  const friendLabels = new Set([
    "friends",
    "friend",
    "เพื่อน"
  ]);

  const ariaLabel = button =>
    normalize(button.getAttribute("aria-label"));

  const getFollowingButtons = () =>
    [...document.querySelectorAll("button[aria-label]")]
      .filter(isVisible)
      .filter(button => followingLabels.has(ariaLabel(button)))
      .filter(button => !friendLabels.has(ariaLabel(button)));

  const getFriendButtons = () =>
    [...document.querySelectorAll("button[aria-label]")]
      .filter(isVisible)
      .filter(button => friendLabels.has(ariaLabel(button)));

  const findScrollContainer = element => {
    let current = element?.parentElement;

    while (current && current !== document.body) {
      const style = getComputedStyle(current);

      if (
        current.scrollHeight > current.clientHeight + 20 &&
        ["auto", "scroll"].includes(style.overflowY)
      ) {
        return current;
      }

      current = current.parentElement;
    }

    return document.scrollingElement;
  };

  const initialFollowing = getFollowingButtons();
  const initialFriends = getFriendButtons();

  console.log(`🎯 Following ที่พบตอนนี้: ${initialFollowing.length}`);
  console.log(`🛡️ Friends ที่จะไม่แตะ: ${initialFriends.length}`);

  if (CONFIG.DRY_RUN) {
    console.log(
      "✅ DRY RUN เสร็จแล้ว — ยังไม่มีการกดปุ่ม เปลี่ยน DRY_RUN เป็น false เพื่อเริ่ม"
    );
    return;
  }

  const firstButton =
    initialFollowing[0] ||
    initialFriends[0] ||
    document.querySelector("button[aria-label]");

  const scrollContainer = findScrollContainer(firstButton);

  let total = 0;
  let stuckRounds = 0;

  while (
    total < CONFIG.MAX_UNFOLLOW &&
    stuckRounds < CONFIG.MAX_STUCK_ROUNDS
  ) {
    if (window.stopTikTokUnfollow) {
      console.warn("⛔ หยุดการทำงานแล้ว");
      break;
    }

    const buttons = getFollowingButtons();
    let clickedThisRound = 0;

    for (const button of buttons) {
      if (
        window.stopTikTokUnfollow ||
        total >= CONFIG.MAX_UNFOLLOW
      ) {
        break;
      }

      // ตรวจซ้ำทันที ก่อนกด
      if (!followingLabels.has(ariaLabel(button))) continue;
      if (friendLabels.has(ariaLabel(button))) continue;

      button.scrollIntoView({
        block: "center",
        behavior: "smooth"
      });

      await sleep(500);

      // หากสถานะเปลี่ยนเป็น Friends ระหว่างรอ จะข้ามทันที
      if (!followingLabels.has(ariaLabel(button))) {
        console.log("🛡️ สถานะเปลี่ยน จึงข้ามปุ่มนี้");
        continue;
      }

      button.click();
      total++;
      clickedThisRound++;

      console.log(`❌ Unfollow แล้ว ${total} บัญชี`);

      await sleep(randomDelay());
    }

    const before = scrollContainer.scrollTop;

    scrollContainer.scrollBy({
      top: Math.max(400, scrollContainer.clientHeight * 0.8),
      behavior: "smooth"
    });

    await sleep(1800);

    const after = scrollContainer.scrollTop;
    const remaining = getFollowingButtons().length;

    if (
      clickedThisRound === 0 &&
      remaining === 0 &&
      Math.abs(after - before) < 5
    ) {
      stuckRounds++;
    } else {
      stuckRounds = 0;
    }
  }

  console.log(`✅ จบการทำงาน — unfollow ทั้งหมด ${total} บัญชี`);
  console.log(`🛡️ ปุ่ม Friends ไม่ถูกกด`);
})();
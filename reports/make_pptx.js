const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Chisanupong Injun';
pres.title = 'TURC2026 - Knowledge Emergence in AI Agents';

const C = {
  navy: "1E2761", navyDeep: "131B45", navyMid: "2D3E7A",
  iceBlue: "CADCFC", iceBlueMid: "8FAADC",
  white: "FFFFFF", offWhite: "F5F7FF", cardBg: "EEF2FF",
  text: "1E293B", muted: "64748B",
  green: "16A34A", red: "DC2626", amber: "D97706",
  teal: "0D9488", sky: "38BDF8",
};
const W = 10;
const ms = () => ({ type: "outer", color: "000000", blur: 8, offset: 3, angle: 45, opacity: 0.12 });

function hdr(s, title, sub) {
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.88, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText(title, { x: 0.4, y: 0, w: 9.2, h: 0.88, fontSize: 24, bold: true, color: C.white, fontFace: "Calibri", valign: "middle" });
  if (sub) s.addText(sub, { x: 0.4, y: 0.88, w: 9.2, h: 0.32, fontSize: 11, color: C.muted, fontFace: "Calibri", italic: true });
}

function num(s, n) {
  s.addText(`${n} / 20`, { x: 8.8, y: 5.32, w: 1, h: 0.25, fontSize: 9, color: C.muted, align: "right", fontFace: "Calibri" });
}

function card(s, x, y, w, h, fill, border) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h,
    fill: { color: fill || C.cardBg },
    shadow: ms(), rectRadius: 0.1,
    line: { color: border || C.iceBlue, width: 0.5 }
  });
}

// ── SLIDE 1 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addShape(pres.shapes.OVAL, { x: 7.2, y: -1.2, w: 4.5, h: 4.5, fill: { color: C.iceBlueMid, transparency: 82 }, line: { color: C.iceBlueMid, transparency: 82 } });
  s.addShape(pres.shapes.OVAL, { x: -1.2, y: 3.2, w: 3.5, h: 3.5, fill: { color: C.iceBlue, transparency: 85 }, line: { color: C.iceBlue, transparency: 85 } });
  s.addText("การศึกษาการเกิดขึ้นขององค์ความรู้จากประสบการณ์", { x: 0.6, y: 0.55, w: 8.8, h: 0.75, fontSize: 23, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri" });
  s.addText("ในตัวแทนปัญญาประดิษฐ์ภายใต้สภาพแวดล้อมจำลองที่ไม่มีข้อมูลตั้งต้น", { x: 0.6, y: 1.27, w: 8.8, h: 0.7, fontSize: 21, bold: true, color: C.white, align: "center", fontFace: "Calibri" });
  s.addText("A Study of Experience-Based Knowledge Emergence in Artificial Agents\nwithin an Uninformed Simulated Environment", { x: 0.6, y: 2.1, w: 8.8, h: 0.85, fontSize: 13, italic: true, color: C.iceBlueMid, align: "center", fontFace: "Calibri" });
  s.addShape(pres.shapes.RECTANGLE, { x: 2.8, y: 3.08, w: 4.4, h: 0.04, fill: { color: C.iceBlue }, line: { color: C.iceBlue } });
  s.addText("นายชิษณุพงศ์ อินทร์จันทร์  |  ม.4 โรงเรียนดีบุกพังงาวิทยายน", { x: 0.6, y: 3.22, w: 8.8, h: 0.5, fontSize: 14, bold: true, color: C.white, align: "center", fontFace: "Calibri" });
  s.addText("อาจารย์ที่ปรึกษา: นายบพิธ มังคะลา", { x: 0.6, y: 3.7, w: 8.8, h: 0.42, fontSize: 13, color: C.iceBlueMid, align: "center", fontFace: "Calibri" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.5, y: 4.25, w: 3, h: 0.6, fill: { color: C.iceBlue }, rectRadius: 0.12, line: { color: C.iceBlue } });
  s.addText("TURC 2026  |  สาขาวิทยาศาสตร์ประยุกต์", { x: 3.5, y: 4.27, w: 3, h: 0.56, fontSize: 11, bold: true, color: C.navy, align: "center", fontFace: "Calibri", valign: "middle", margin: 0 });
}

// ── SLIDE 2 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "ปัญหาของ AI แบบมีผู้สอน", "ทำไมเราถึงต้องการแนวทางใหม่?");
  num(s, 2);
  const items = [
    { n: "01", label: "Labeled Data", body: "มนุษย์ต้องป้ายกำกับทุกตัวอย่าง\nใช้เวลาและทรัพยากรมหาศาล" },
    { n: "02", label: "Reward Function", body: "มนุษย์ต้องกำหนดรางวัล\nล่วงหน้าก่อน AI จะเรียนรู้" },
    { n: "03", label: "สภาพแวดล้อมใหม่", body: "พื้นผิวดาว ใต้ทะเล ภัยพิบัติ\nมนุษย์ยังไม่รู้จักพอ" },
  ];
  items.forEach((it, i) => {
    const x = 0.5 + i * 3.15;
    card(s, x, 1.3, 2.9, 2.9, C.offWhite, C.iceBlue);
    s.addText(it.n, { x, y: 1.38, w: 2.9, h: 0.7, fontSize: 40, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri" });
    s.addText(it.label, { x: x+0.1, y: 2.1, w: 2.7, h: 0.5, fontSize: 15, bold: true, color: C.navy, align: "center", fontFace: "Calibri" });
    s.addText(it.body, { x: x+0.1, y: 2.65, w: 2.7, h: 1.3, fontSize: 13, color: C.muted, align: "center", fontFace: "Calibri" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4.42, w: 9, h: 0.75, fill: { color: C.navy }, rectRadius: 0.1, line: { color: C.navy } });
  s.addText("AI เรียนรู้ได้เฉพาะสิ่งที่มนุษย์บอกเท่านั้น — ไม่สามารถส่งไปสำรวจโลกที่ยังไม่รู้จักได้", { x: 0.5, y: 4.44, w: 9, h: 0.71, fontSize: 14, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri", valign: "middle", margin: 0 });
}

// ── SLIDE 3 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  hdr(s, "คำถามวิจัยหลัก");
  num(s, 3);
  card(s, 0.5, 1.32, 9, 2.0, C.white, C.navy);
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.32, w: 0.22, h: 2.0, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText('"  หาก AI อยู่ในโลกที่มีเพียงกฎฟิสิกส์พื้นฐาน โดยไม่บอกว่าวัตถุแต่ละอย่างคืออะไร\nมันจะเรียนรู้จากประสบการณ์จนเกิดพฤติกรรมที่มีความหมายได้หรือไม่?"', { x: 0.87, y: 1.39, w: 8.5, h: 1.87, fontSize: 18, bold: true, color: C.navy, align: "left", fontFace: "Calibri", valign: "middle" });
  const cols = [
    { title: "แรงจูงใจ", body: "ดาวดวงอื่น / ใต้ทะเล / ภัยพิบัติ\n→ ส่ง AI เรียนรู้แทนมนุษย์ก่อน" },
    { title: "ความเชื่อมโยง", body: "Sim-to-Real Transfer\nในหุ่นยนต์สำรวจอวกาศ" },
  ];
  cols.forEach((c, i) => {
    const x = 0.5 + i * 4.75;
    card(s, x, 3.55, 4.3, 1.65, C.cardBg, C.iceBlueMid);
    s.addText(c.title, { x: x+0.15, y: 3.63, w: 4, h: 0.48, fontSize: 15, bold: true, color: C.navy, fontFace: "Calibri" });
    s.addText(c.body, { x: x+0.15, y: 4.12, w: 4, h: 0.98, fontSize: 13, color: C.text, fontFace: "Calibri" });
  });
}

// ── SLIDE 4 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "แนวคิด Artificial Life (ALife)", "แตกต่างจาก Deep Reinforcement Learning ทั่วไปอย่างไร?");
  num(s, 4);
  // Left card: Deep RL
  card(s, 0.4, 1.32, 4.1, 3.7, "FFF5F5", C.red);
  s.addText("Deep RL ทั่วไป", { x: 0.55, y: 1.42, w: 3.8, h: 0.5, fontSize: 17, bold: true, color: C.red, fontFace: "Calibri" });
  ["ต้องการ Reward Function ละเอียด", "มนุษย์กำหนดเป้าหมายล่วงหน้า", "เรียนรู้สิ่งที่ระบุไว้เท่านั้น", "ขึ้นกับ labeled environment"].forEach((t, i) => {
    s.addText([{ text: "✗  ", options: { bold: true, color: C.red } }, { text: t }], { x: 0.6, y: 2.05 + i * 0.6, w: 3.8, h: 0.52, fontSize: 13, color: C.text, fontFace: "Calibri" });
  });
  // Right card: ALife
  card(s, 5.5, 1.32, 4.1, 3.7, "F0FFF4", C.green);
  s.addText("Artificial Life (ALife)", { x: 5.65, y: 1.42, w: 3.8, h: 0.5, fontSize: 17, bold: true, color: C.green, fontFace: "Calibri" });
  ["ให้เพียงสัญญาณการอยู่รอด", "ไม่กำหนดรางวัลล่วงหน้า", "สังเกตพฤติกรรมที่เกิดขึ้นเอง", "โลกมีกฎฟิสิกส์ ไม่มีป้ายกำกับ"].forEach((t, i) => {
    s.addText([{ text: "✓  ", options: { bold: true, color: C.green } }, { text: t }], { x: 5.7, y: 2.05 + i * 0.6, w: 3.8, h: 0.52, fontSize: 13, color: C.text, fontFace: "Calibri" });
  });
  card(s, 4.45, 2.55, 1.1, 1.1, C.navy, C.navy);
  s.addText("VS", { x: 4.45, y: 2.58, w: 1.1, h: 1.04, fontSize: 28, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri", valign: "middle" });
}

// ── SLIDE 5 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "โลกจำลอง 2 มิติ", "สภาพแวดล้อมที่ไม่มีข้อมูลตั้งต้น — วงจรทรัพยากรครบถ้วน");
  num(s, 5);
  // Elements grid (left)
  const els = [
    { label: "เมล็ด (Seed)", col: C.amber },
    { label: "พืช (Plant)", col: C.green },
    { label: "ผล (Fruit)", col: C.teal },
    { label: "อาหาร (Food)", col: C.sky },
    { label: "ความชื้น + แสง + อุณหภูมิ", col: C.iceBlueMid },
    { label: "สารอาหารในดิน", col: C.navyMid },
  ];
  els.forEach((el, i) => {
    const col = Math.floor(i / 3), row = i % 3;
    const x = 0.4 + col * 3.3, y = 1.25 + row * 1.02;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.0, h: 0.82, fill: { color: el.col, transparency: 80 }, line: { color: el.col, width: 1 }, rectRadius: 0.08 });
    s.addText(el.label, { x, y, w: 3.0, h: 0.82, fontSize: 13, bold: true, color: C.navy, align: "center", fontFace: "Calibri", valign: "middle" });
  });
  // Cycle (right)
  s.addText("วงจรชีวภาพ", { x: 7.2, y: 1.2, w: 2.5, h: 0.4, fontSize: 14, bold: true, color: C.navy, align: "center", fontFace: "Calibri" });
  const cs = [["🌱 เมล็ด", C.amber], ["🌿 พืช", C.green], ["🍎 ผล", C.teal], ["🍖 อาหาร", C.sky]];
  cs.forEach(([lbl, col], i) => {
    const y = 1.65 + i * 0.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.2, y, w: 2.5, h: 0.62, fill: { color: col, transparency: 72 }, line: { color: col }, rectRadius: 0.08 });
    s.addText(lbl, { x: 7.2, y, w: 2.5, h: 0.62, fontSize: 14, bold: true, color: C.navy, align: "center", fontFace: "Calibri", valign: "middle" });
    if (i < 3) s.addText("↓", { x: 7.85, y: y + 0.58, w: 0.7, h: 0.3, fontSize: 16, color: C.navy, align: "center" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.4, y: 4.38, w: 6.55, h: 0.82, fill: { color: "FFF8E1", transparency: 0 }, rectRadius: 0.08, line: { color: C.amber } });
  s.addText("⚠  ตัวแทนไม่ได้รับข้อมูลว่าวัตถุแต่ละอย่างคืออะไร — ต้องสำรวจเองทั้งหมด", { x: 0.55, y: 4.42, w: 6.3, h: 0.74, fontSize: 13, bold: true, color: C.amber, fontFace: "Calibri", valign: "middle" });
}

// ── SLIDE 6 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "โครงสร้างตัวแทน AI", "Multi-Input / Multi-Output Neural Network");
  num(s, 6);
  // Input 1
  card(s, 0.3, 1.2, 2.5, 1.4, C.offWhite, C.iceBlue);
  s.addText("Input 1\nภาพกริดรอบตัว", { x: 0.4, y: 1.28, w: 2.3, h: 0.75, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", align: "center" });
  s.addText("ไม่มีป้ายบอกชนิดวัตถุ", { x: 0.4, y: 1.98, w: 2.3, h: 0.48, fontSize: 11, color: C.muted, fontFace: "Calibri", align: "center" });
  // Input 2
  card(s, 0.3, 2.85, 2.5, 1.45, C.offWhite, C.iceBlue);
  s.addText("Input 2\nสถานะภายใน", { x: 0.4, y: 2.93, w: 2.3, h: 0.75, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", align: "center" });
  s.addText("พลังงาน, อุณหภูมิ,\nสิ่งแวดล้อมรอบตัว", { x: 0.4, y: 3.65, w: 2.3, h: 0.55, fontSize: 11, color: C.muted, fontFace: "Calibri", align: "center" });
  // Arrows
  s.addText("→", { x: 2.82, y: 1.78, w: 0.6, h: 0.4, fontSize: 20, color: C.iceBlueMid, align: "center" });
  s.addText("→", { x: 2.82, y: 3.45, w: 0.6, h: 0.4, fontSize: 20, color: C.iceBlueMid, align: "center" });
  // NN box
  card(s, 3.42, 1.9, 3.0, 2.2, C.navy, C.navy);
  s.addText("Neural Network", { x: 3.5, y: 2.0, w: 2.85, h: 0.48, fontSize: 15, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri" });
  for (let r = 0; r < 3; r++) for (let c2 = 0; c2 < 4; c2++) {
    s.addShape(pres.shapes.OVAL, { x: 3.7 + c2 * 0.55, y: 2.62 + r * 0.47, w: 0.26, h: 0.26, fill: { color: C.iceBlueMid, transparency: 30 }, line: { color: C.iceBlue } });
  }
  s.addText("Deep Learning", { x: 3.5, y: 3.78, w: 2.85, h: 0.28, fontSize: 11, italic: true, color: C.iceBlueMid, align: "center", fontFace: "Calibri" });
  // Arrows out
  s.addText("→", { x: 6.45, y: 1.9, w: 0.6, h: 0.4, fontSize: 20, color: C.iceBlueMid, align: "center" });
  s.addText("→", { x: 6.45, y: 3.45, w: 0.6, h: 0.4, fontSize: 20, color: C.iceBlueMid, align: "center" });
  // Output 1
  card(s, 7.05, 1.68, 2.6, 1.35, "F0FFF4", C.green);
  s.addText("Output 1: การเคลื่อนที่", { x: 7.15, y: 1.76, w: 2.4, h: 0.55, fontSize: 13, bold: true, color: C.green, fontFace: "Calibri", align: "center" });
  s.addText("↑ ↓ ← →", { x: 7.15, y: 2.28, w: 2.4, h: 0.65, fontSize: 18, color: C.green, align: "center" });
  // Output 2
  card(s, 7.05, 3.22, 2.6, 1.6, "F0F4FF", C.sky);
  s.addText("Output 2: การกระทำ", { x: 7.15, y: 3.3, w: 2.4, h: 0.55, fontSize: 13, bold: true, color: C.sky, fontFace: "Calibri", align: "center" });
  s.addText("กิน | หยิบ\nปล่อย | เคลื่อนย้ายเมล็ด", { x: 7.15, y: 3.85, w: 2.4, h: 0.82, fontSize: 12, color: C.text, align: "center", fontFace: "Calibri" });
}

// ── SLIDE 7 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "ตัวชี้วัดที่ 1 — Spatial Learning Index (SLI)", "วัดการเรียนรู้ตำแหน่งเชิงพื้นที่");
  num(s, 7);
  s.addText("SLI วัดอะไร?", { x: 0.4, y: 1.28, w: 5.5, h: 0.5, fontSize: 18, bold: true, color: C.navy, fontFace: "Calibri" });
  [
    "อัตราส่วนความถี่กลับสู่พิกัดที่เคยได้รับอาหาร",
    "เทียบกับความถี่ที่คาดจากการเดินสุ่ม (Random Walk)",
    "SLI > 1  →  ตัวแทนจำตำแหน่งได้และกลับมาซ้ำ",
    "SLI = 1  →  ไม่ต่างจากการสุ่ม (ยังไม่เรียนรู้)",
  ].forEach((t, i) => {
    s.addText([{ text: "◆  ", options: { bold: true, color: C.sky } }, { text: t }], { x: 0.4, y: 1.88 + i * 0.62, w: 5.7, h: 0.55, fontSize: 13, color: C.text, fontFace: "Calibri" });
  });
  s.addText("เปรียบเทียบ", { x: 6.5, y: 1.28, w: 3.2, h: 0.45, fontSize: 15, bold: true, color: C.navy, align: "center", fontFace: "Calibri" });
  card(s, 6.5, 1.78, 3.2, 1.45, "FFF5F5", C.red);
  s.addText("Random Agent\nSLI ≈ 1.0", { x: 6.6, y: 1.88, w: 3, h: 1.2, fontSize: 14, bold: true, color: C.red, align: "center", fontFace: "Calibri" });
  s.addText("VS", { x: 7.7, y: 3.3, w: 1, h: 0.45, fontSize: 16, bold: true, color: C.muted, align: "center" });
  card(s, 6.5, 3.78, 3.2, 1.45, "F0FFF4", C.green);
  s.addText("Learning Agent\nSLI >> 1.0  ✓", { x: 6.6, y: 3.88, w: 3, h: 1.2, fontSize: 14, bold: true, color: C.green, align: "center", fontFace: "Calibri" });
}

// ── SLIDE 8 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "ตัวชี้วัดที่ 2 — Seed Causal Chain", "Resource Manipulation Rate — ตัวแทนมีผลต่อวงจรทรัพยากรจริงหรือไม่?");
  num(s, 8);
  const steps = [
    { lbl: "เมล็ด\nธรรมชาติ", col: C.amber },
    { lbl: "ตัวแทน\nหยิบ/ขนย้าย", col: C.sky },
    { lbl: "ปล่อยใน\nพื้นที่ใหม่", col: C.teal },
    { lbl: "เมล็ดงอก\n→ พืช", col: C.green },
    { lbl: "กลายเป็น\nอาหาร ✓", col: C.navy },
  ];
  steps.forEach((st, i) => {
    const x = 0.35 + i * 1.88;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.22, w: 1.65, h: 1.55, fill: { color: st.col, transparency: st.col === C.navy ? 0 : 82 }, line: { color: st.col }, rectRadius: 0.1 });
    s.addText(st.lbl, { x, y: 1.22, w: 1.65, h: 1.55, fontSize: 13, bold: true, color: st.col === C.navy ? C.white : st.col, align: "center", fontFace: "Calibri", valign: "middle" });
    if (i < 4) s.addText("→", { x: x + 1.62, y: 1.88, w: 0.3, h: 0.35, fontSize: 20, color: C.iceBlueMid, align: "center" });
  });
  s.addText("ระบบ Seed ID", { x: 0.4, y: 3.02, w: 9.2, h: 0.48, fontSize: 16, bold: true, color: C.navy, fontFace: "Calibri" });
  [
    "ติดป้ายกำกับ Seed ID ให้เมล็ดทุกเม็ดตั้งแต่แรก",
    "บันทึกประวัติทุกขั้นตอนตลอดวงจรชีวิตของเมล็ด",
    "คำนวณ Resource Manipulation Rate = สัดส่วนเมล็ดที่ตัวแทนขนย้ายแล้วกลายเป็นอาหาร",
  ].forEach((t, i) => {
    s.addText([{ text: "  •  ", options: { color: C.sky } }, { text: t }], { x: 0.4, y: 3.58 + i * 0.56, w: 9.2, h: 0.5, fontSize: 13, color: C.text, fontFace: "Calibri" });
  });
}

// ── SLIDE 9 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "ตัวชี้วัดที่ 3 — Patch Productivity Variance (PPV)", "ตัวแทนเลือกพื้นที่ปล่อยเมล็ดได้ดีกว่าการสุ่มหรือไม่?");
  num(s, 9);
  card(s, 0.4, 1.28, 4.3, 2.5, "F0FFF4", C.green);
  s.addText("Seed Drop Zone", { x: 0.55, y: 1.38, w: 4, h: 0.5, fontSize: 16, bold: true, color: C.green, fontFace: "Calibri" });
  s.addText("(พื้นที่ที่ตัวแทนปล่อยเมล็ดซ้ำ)", { x: 0.55, y: 1.85, w: 4, h: 0.4, fontSize: 12, italic: true, color: C.muted, fontFace: "Calibri" });
  s.addText("ผลผลิตสูง\n(ถ้าตัวแทนเลือกได้จริง)", { x: 0.55, y: 2.28, w: 4, h: 0.8, fontSize: 14, color: C.text, fontFace: "Calibri" });
  s.addText("PPV > 1", { x: 0.55, y: 3.05, w: 2, h: 0.55, fontSize: 26, bold: true, color: C.green, fontFace: "Calibri" });
  s.addText("VS", { x: 4.55, y: 2.25, w: 0.9, h: 0.6, fontSize: 22, bold: true, color: C.navyMid, align: "center" });
  card(s, 5.3, 1.28, 4.3, 2.5, C.offWhite, C.muted);
  s.addText("Control Zone", { x: 5.45, y: 1.38, w: 4, h: 0.5, fontSize: 16, bold: true, color: C.navy, fontFace: "Calibri" });
  s.addText("(พื้นที่ควบคุม ไม่มีตัวแทน)", { x: 5.45, y: 1.85, w: 4, h: 0.4, fontSize: 12, italic: true, color: C.muted, fontFace: "Calibri" });
  s.addText("ผลผลิตเฉลี่ย\nจากธรรมชาติ", { x: 5.45, y: 2.28, w: 4, h: 0.8, fontSize: 14, color: C.text, fontFace: "Calibri" });
  s.addText("PPV = 1", { x: 5.45, y: 3.05, w: 2, h: 0.55, fontSize: 26, bold: true, color: C.navy, fontFace: "Calibri" });
  card(s, 0.4, 4.02, 9.2, 0.88, C.offWhite, C.iceBlueMid);
  s.addText("PPV สูงกว่า 1 อย่างมีนัยสำคัญ → ตัวแทนเลือกพื้นที่ได้จริง (ยืนยันได้ก็ต่อเมื่อผ่านชุดควบคุมทั้งหมด)", { x: 0.55, y: 4.06, w: 9, h: 0.8, fontSize: 13, color: C.navy, fontFace: "Calibri", valign: "middle" });
}

// ── SLIDE 10 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "การป้องกันการตีความเกินจริง", "Scientific Integrity คือจุดแข็งหลักของงานวิจัยนี้");
  num(s, 10);
  const pillars = [
    { n: "1", title: "Random Agent Baseline", body: "แทนที่ด้วยตัวแทนเดินสุ่มในโลกเดียวกัน\n→ ผลที่เกินกว่านี้คือการเรียนรู้จริง" },
    { n: "2", title: "Control Zone", body: "พื้นที่ที่ตัวแทนเข้าไม่ถึง\n→ baseline ผลผลิตธรรมชาติ" },
    { n: "3", title: "ผ่าน 3 ตัวชี้วัดพร้อมกัน", body: "SLI + Causal Chain + PPV\nต้องสอดคล้องกันทั้งหมดก่อนสรุป" },
  ];
  pillars.forEach((p, i) => {
    const x = 0.4 + i * 3.15;
    card(s, x, 1.28, 2.9, 2.95, C.offWhite, C.navy);
    s.addShape(pres.shapes.OVAL, { x: x + 1.1, y: 1.38, w: 0.7, h: 0.7, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText(p.n, { x: x + 1.1, y: 1.4, w: 0.7, h: 0.66, fontSize: 22, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri", valign: "middle" });
    s.addText(p.title, { x: x + 0.1, y: 2.18, w: 2.7, h: 0.65, fontSize: 14, bold: true, color: C.navy, align: "center", fontFace: "Calibri" });
    s.addText(p.body, { x: x + 0.1, y: 2.86, w: 2.7, h: 1.22, fontSize: 12, color: C.text, align: "center", fontFace: "Calibri" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.4, y: 4.42, w: 9.2, h: 0.82, fill: { color: C.navy }, rectRadius: 0.1, line: { color: C.navy } });
  s.addText("ไม่อ้างว่าตัวแทน \"เข้าใจ\" หรือ \"วางแผน\" โดยไม่มีหลักฐานจากข้อมูลที่วัดได้", { x: 0.55, y: 4.45, w: 9, h: 0.76, fontSize: 14, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri", valign: "middle", margin: 0 });
}

// ── SLIDE 11 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "ผลการทดลอง Phase 1 — วงจรนิเวศ ✓", "ยืนยันว่าโลกจำลองทำงานได้ก่อนทดสอบตัวแทน");
  num(s, 11);
  s.addShape(pres.shapes.OVAL, { x: 7.1, y: 1.12, w: 2.5, h: 2.5, fill: { color: C.green }, line: { color: C.green }, shadow: ms() });
  s.addText("✓\nผ่าน", { x: 7.1, y: 1.52, w: 2.5, h: 1.7, fontSize: 36, bold: true, color: C.white, align: "center", fontFace: "Calibri", valign: "middle" });
  s.addText("สรุปผล", { x: 0.4, y: 1.18, w: 6.4, h: 0.5, fontSize: 18, bold: true, color: C.navy, fontFace: "Calibri" });
  [
    "วงจรชีวภาพ เมล็ด → พืช → ผล → อาหาร มีเสถียรภาพตลอดการทดลอง",
    "5/5 เมล็ดในทุก trial เข้าสู่วงจรได้สำเร็จ",
    "ผลสอดคล้องกันข้ามรอบการทดลองที่แตกต่างกัน",
    "โลกจำลองมีสัญญาณที่เรียนรู้ได้จริง — พร้อมทดสอบตัวแทน",
  ].forEach((t, i) => {
    s.addText([{ text: "✓  ", options: { bold: true, color: C.green } }, { text: t }], { x: 0.4, y: 1.82 + i * 0.65, w: 6.4, h: 0.58, fontSize: 13, color: C.text, fontFace: "Calibri" });
  });
  card(s, 0.4, 4.22, 6.4, 0.98, C.offWhite, C.green);
  const cyc = ["🌱 เมล็ด", "🌿 พืช", "🍎 ผล", "🍖 อาหาร"];
  cyc.forEach((c2, i) => {
    s.addText(c2, { x: 0.55 + i * 1.5, y: 4.32, w: 1.38, h: 0.78, fontSize: 13, bold: true, color: C.navy, align: "center", fontFace: "Calibri", valign: "middle" });
    if (i < 3) s.addText("→", { x: 0.55 + i * 1.5 + 1.32, y: 4.52, w: 0.25, h: 0.38, fontSize: 16, color: C.green, align: "center" });
  });
}

// ── SLIDE 12 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "ผลการทดลอง Phase 2 — Spatial Learning ✓", "ตัวแทนจำตำแหน่งอาหารและกลับมาซ้ำได้โดยไม่ได้รับการบอก");
  num(s, 12);
  s.addText("Spatial Learning Index (SLI)", { x: 0.4, y: 1.25, w: 5.5, h: 0.48, fontSize: 16, bold: true, color: C.navy, fontFace: "Calibri" });
  s.addChart(pres.charts.BAR, [{ name: "SLI", labels: ["Trial 1", "Trial 2", "Trial 3", "Random Baseline"], values: [33, 47, 52, 1] }], {
    x: 0.4, y: 1.78, w: 5.5, h: 3.5, barDir: "col",
    chartColors: [C.green, C.green, C.green, C.red],
    chartArea: { fill: { color: C.white }, roundedCorners: false },
    catAxisLabelColor: C.text, valAxisLabelColor: C.muted,
    valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.navy,
    showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 60,
  });
  s.addText("ผลสำคัญ", { x: 6.3, y: 1.25, w: 3.4, h: 0.48, fontSize: 16, bold: true, color: C.navy, fontFace: "Calibri" });
  [{ val: "3/3", lbl: "trials\nผ่านทั้งหมด" }, { val: "33–52×", lbl: "สูงกว่า\nการสุ่ม" }].forEach((f, i) => {
    card(s, 6.3, 1.78 + i * 2.05, 3.4, 1.82, C.offWhite, C.green);
    s.addText(f.val, { x: 6.3, y: 1.9 + i * 2.05, w: 3.4, h: 0.9, fontSize: 42, bold: true, color: C.green, align: "center", fontFace: "Calibri" });
    s.addText(f.lbl, { x: 6.3, y: 2.8 + i * 2.05, w: 3.4, h: 0.65, fontSize: 13, color: C.muted, align: "center", fontFace: "Calibri" });
  });
}

// ── SLIDE 13 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "ผลการทดลอง Phase 3 — Seed Causality ✓", "ตัวแทนมีผลต่อวงจรทรัพยากรของโลกจริง");
  num(s, 13);
  s.addShape(pres.shapes.OVAL, { x: 7.2, y: 1.08, w: 2.5, h: 2.5, fill: { color: C.teal }, line: { color: C.teal }, shadow: ms() });
  s.addText("3/3\nTrials", { x: 7.2, y: 1.45, w: 2.5, h: 1.75, fontSize: 28, bold: true, color: C.white, align: "center", fontFace: "Calibri", valign: "middle" });
  [
    "เมล็ดที่ตัวแทนขนย้ายผ่านวงจรจนกลายเป็นอาหารได้จริงในทุก trial",
    "Seed ID ยืนยัน causal chain ตั้งแต่ตัวแทนหยิบ → ปล่อย → งอก → กิน",
    "Resource Manipulation Rate สูงกว่า control อย่างมีนัยสำคัญ",
    "ยืนยันว่าตัวแทนไม่ใช่ passive observer — มีผลต่อโลกจริง",
  ].forEach((t, i) => {
    s.addText([{ text: "✓  ", options: { bold: true, color: C.teal } }, { text: t }], { x: 0.4, y: 1.25 + i * 0.7, w: 6.5, h: 0.62, fontSize: 13, color: C.text, fontFace: "Calibri" });
  });
  card(s, 0.4, 4.12, 9.2, 1.05, "F0FFF4", C.green);
  s.addText("Phase 1–3 ผ่านแล้ว: โลกเสถียร  |  SLI สูง 33–52×  |  Causal Chain ยืนยันได้", { x: 0.55, y: 4.2, w: 9, h: 0.5, fontSize: 14, bold: true, color: C.green, align: "center", fontFace: "Calibri" });
  s.addText("→ ฐานที่แข็งแกร่งสำหรับการทดสอบ Phase ถัดไป", { x: 0.55, y: 4.68, w: 9, h: 0.38, fontSize: 13, color: C.navy, align: "center", fontFace: "Calibri" });
}

// ── SLIDE 14 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "จุดวิกฤต — ปัญหาที่พบใน Phase 4 & 5", "การค้นพบที่นำไปสู่การออกแบบใหม่ทั้งหมด");
  num(s, 14);
  card(s, 0.4, 1.25, 4.3, 2.15, "FFF5F5", C.red);
  s.addText("Phase 4.1 Falsification", { x: 0.55, y: 1.35, w: 4, h: 0.48, fontSize: 15, bold: true, color: C.red, fontFace: "Calibri" });
  s.addText([{ text: "✗  ", options: { color: C.red, bold: true } }, { text: "200×200 grid — ล้มเหลว 0/3 trials" }], { x: 0.55, y: 1.88, w: 4, h: 0.52, fontSize: 13, color: C.text, fontFace: "Calibri" });
  s.addText([{ text: "✗  ", options: { color: C.red, bold: true } }, { text: "non-dropper return สูง → อ้างความเป็นเจ้าของ patch ไม่ได้" }], { x: 0.55, y: 2.43, w: 4, h: 0.62, fontSize: 13, color: C.text, fontFace: "Calibri" });
  card(s, 5.3, 1.25, 4.3, 2.15, "FFF5F5", C.red);
  s.addText("Phase 5 Site-Selection", { x: 5.45, y: 1.35, w: 4, h: 0.48, fontSize: 15, bold: true, color: C.red, fontFace: "Calibri" });
  s.addText([{ text: "✗  ", options: { color: C.red, bold: true } }, { text: "ไม่ผ่าน — root cause พบในการทดลอง 5.5" }], { x: 5.45, y: 1.88, w: 4, h: 0.52, fontSize: 13, color: C.text, fontFace: "Calibri" });
  s.addText([{ text: "97.8%  ", options: { bold: true, color: C.red } }, { text: "ของการปล่อยเมล็ดเกิดขณะหิวโหยวิกฤต (hunger ≈ 0.983)" }], { x: 5.45, y: 2.43, w: 4, h: 0.62, fontSize: 13, color: C.text, fontFace: "Calibri" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.4, y: 3.62, w: 9.2, h: 1.45, fill: { color: "FFF8E1" }, rectRadius: 0.1, line: { color: C.amber } });
  s.addText("สาเหตุที่แท้จริง", { x: 0.55, y: 3.7, w: 9, h: 0.45, fontSize: 15, bold: true, color: C.amber, fontFace: "Calibri" });
  s.addText("seed_hunger_drop_bonus ใน agent.py เป็น hand-coded bias — ขัดกับหลักการ \"ให้ฟิสิกส์ตัดสิน\" ของโครงงาน\nตัวแทนปล่อยเมล็ดเพราะโค้ดบอก ไม่ใช่เพราะเรียนรู้ → ต้องสร้างระบบย่อยอาหารจากฟิสิกส์ล้วน", { x: 0.55, y: 4.15, w: 9, h: 0.82, fontSize: 13, color: C.text, fontFace: "Calibri" });
}

// ── SLIDE 15 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "การออกแบบใหม่ — Metabolism Physics v2", "สร้างระบบย่อยอาหารจากฟิสิกส์ล้วน ไม่มี hard-coded bias");
  num(s, 15);
  const layers = [
    { n: "1", lbl: "Mouth-Size Gate", body: "กรองวัตถุที่ใหญ่เกินปาก — กรอบปากวิวัฒนาการได้ (heritable gene)" },
    { n: "2", lbl: "Enzyme Digestion", body: "ย่อยตามองค์ประกอบ — เมล็ดย่อยได้บางส่วน ให้พลังงานต่ำกว่าผล" },
    { n: "3", lbl: "Gut Transit + Excretion", body: "เมล็ดในลำไส้เดินทางกับตัวแทน → ขับออกที่ตำแหน่งใหม่ (Endozoochory)" },
    { n: "4", lbl: "Toxicity Filter", body: "ตรวจสอบความเป็นพิษ — สร้าง tradeoff ที่เรียนรู้ได้" },
  ];
  layers.forEach((l, i) => {
    const y = 1.25 + i * 0.97;
    s.addShape(pres.shapes.OVAL, { x: 0.38, y: y + 0.18, w: 0.52, h: 0.52, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText(l.n, { x: 0.38, y: y + 0.2, w: 0.52, h: 0.48, fontSize: 16, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri", valign: "middle" });
    card(s, 1.05, y, 8.55, 0.84, C.offWhite, C.iceBlue);
    s.addText(l.lbl, { x: 1.2, y: y + 0.06, w: 2.9, h: 0.44, fontSize: 15, bold: true, color: C.navy, fontFace: "Calibri" });
    s.addText(l.body, { x: 4.2, y: y + 0.06, w: 5.2, h: 0.72, fontSize: 12, color: C.muted, fontFace: "Calibri" });
    if (i < 3) s.addText("↓", { x: 0.47, y: y + 0.82, w: 0.35, h: 0.2, fontSize: 14, color: C.iceBlueMid, align: "center" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.4, y: 5.12, w: 9.2, h: 0.42, fill: { color: C.navy }, rectRadius: 0.08, line: { color: C.navy } });
  s.addText("ลบ seed_hunger_drop_bonus ออก — การปล่อยเมล็ดเกิดจากฟิสิกส์ล้วน  ✓", { x: 0.55, y: 5.14, w: 9, h: 0.38, fontSize: 13, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri", margin: 0 });
}

// ── SLIDE 16 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "การค้นพบใหม่ — Endozoochory", "การกระจายเมล็ดผ่านลำไส้: พฤติกรรมที่เกิดขึ้นเองจากฟิสิกส์");
  num(s, 16);
  card(s, 6.4, 1.12, 3.3, 3.45, C.navy, C.navy);
  s.addText("ผลที่วัดได้", { x: 6.5, y: 1.2, w: 3.1, h: 0.42, fontSize: 14, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri" });
  s.addText("4.59", { x: 6.5, y: 1.65, w: 3.1, h: 0.95, fontSize: 52, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri" });
  s.addText("Mean Manhattan Distance", { x: 6.5, y: 2.58, w: 3.1, h: 0.5, fontSize: 12, color: C.iceBlueMid, align: "center", fontFace: "Calibri" });
  s.addShape(pres.shapes.RECTANGLE, { x: 7.1, y: 3.12, w: 2.1, h: 0.04, fill: { color: C.iceBlueMid }, line: { color: C.iceBlueMid } });
  s.addText("80% > 0", { x: 6.5, y: 3.2, w: 3.1, h: 0.52, fontSize: 22, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri" });
  s.addText("ของเมล็ดถูกกระจาย\nออกจากตำแหน่งเดิม", { x: 6.5, y: 3.7, w: 3.1, h: 0.72, fontSize: 12, color: C.iceBlueMid, align: "center", fontFace: "Calibri" });
  s.addText("กระบวนการที่เกิดขึ้น", { x: 0.4, y: 1.18, w: 5.8, h: 0.45, fontSize: 16, bold: true, color: C.navy, fontFace: "Calibri" });
  [
    { n: "1", step: "ตัวแทนกินเมล็ดเข้าไป", sub: "ผ่าน mouth-size gate + enzyme digestion บางส่วน" },
    { n: "2", step: "เมล็ดเข้าสู่ระบบย่อย (Gut Transit)", sub: "เดินทางกับตัวแทนตลอดช่วง transit time" },
    { n: "3", step: "ขับออกในตำแหน่งที่ต่างออกไป", sub: "เมล็ดยังมีชีวิต → สามารถงอกในพื้นที่ใหม่" },
  ].forEach((st, i) => {
    s.addShape(pres.shapes.OVAL, { x: 0.38, y: 1.75 + i * 1.02, w: 0.5, h: 0.5, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText(st.n, { x: 0.38, y: 1.77 + i * 1.02, w: 0.5, h: 0.46, fontSize: 16, bold: true, color: C.white, align: "center", fontFace: "Calibri", valign: "middle" });
    s.addText(st.step, { x: 1.05, y: 1.75 + i * 1.02, w: 5.1, h: 0.45, fontSize: 14, bold: true, color: C.navy, fontFace: "Calibri" });
    s.addText(st.sub, { x: 1.05, y: 2.18 + i * 1.02, w: 5.1, h: 0.45, fontSize: 12, color: C.muted, fontFace: "Calibri" });
  });
  card(s, 0.4, 4.2, 5.8, 0.95, "F0FDFA", C.teal);
  s.addText("พฤติกรรมนี้เกิดขึ้นเองจากฟิสิกส์\nเทียบได้กับการกระจายเมล็ดในธรรมชาติโดยสัตว์ — ไม่ได้ถูกโปรแกรมไว้", { x: 0.55, y: 4.24, w: 5.5, h: 0.88, fontSize: 13, bold: true, color: C.teal, fontFace: "Calibri" });
}

// ── SLIDE 17 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "การค้นพบ — อุปสรรคการสืบพันธุ์", "ต้องผ่าน 3 ประตูพร้อมกัน — ไม่ใช่แค่พลังงานอย่างเดียว");
  num(s, 17);
  const gates = [
    { n: "ประตู 1", lbl: "พลังงาน", detail: "Energy ≥ 92\nสะสมในสภาวะ\nperma-starvation ไม่ได้", fix: "แก้ด้วย food/drain multiplier", col: C.amber },
    { n: "ประตู 2", lbl: "Durability", detail: "Durability ≥ 18\nbody 37: durability = 10\n→ สืบพันธุ์ไม่ได้ตลอดกาล\nbody 38: durability = 26 ✓", fix: "แก้โดยเลือก body ที่ถูกต้อง", col: C.red },
    { n: "ประตู 3", lbl: "Social Gates", detail: "mate + pair_bond streak\nsafety streak + comfort\nattachment score", fix: "ยังต้องศึกษาต่อ", col: C.sky },
  ];
  gates.forEach((g, i) => {
    const x = 0.4 + i * 3.15;
    card(s, x, 1.22, 2.9, 3.62, C.white, g.col);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.22, w: 2.9, h: 0.62, fill: { color: g.col }, rectRadius: 0.08, line: { color: g.col } });
    s.addText(g.n, { x, y: 1.24, w: 2.9, h: 0.58, fontSize: 15, bold: true, color: C.white, align: "center", fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addText(g.lbl, { x: x+0.1, y: 1.96, w: 2.7, h: 0.52, fontSize: 18, bold: true, color: g.col, align: "center", fontFace: "Calibri" });
    s.addText(g.detail, { x: x+0.1, y: 2.5, w: 2.7, h: 1.4, fontSize: 12, color: C.text, align: "center", fontFace: "Calibri" });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x+0.15, y: 3.92, w: 2.6, h: 0.72, fill: { color: g.col, transparency: 85 }, rectRadius: 0.08, line: { color: g.col } });
    s.addText(g.fix, { x: x+0.15, y: 3.94, w: 2.6, h: 0.68, fontSize: 12, bold: true, color: g.col, align: "center", fontFace: "Calibri", valign: "middle" });
  });
  card(s, 0.4, 5.0, 9.2, 0.48, C.offWhite, C.navy);
  s.addText("การระบุ root cause ที่แม่นยำ → แก้ปัญหาตรงจุด แทนการ trial-and-error", { x: 0.55, y: 5.02, w: 9, h: 0.44, fontSize: 13, color: C.navy, align: "center", fontFace: "Calibri", valign: "middle" });
}

// ── SLIDE 18 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "ก้าวสำคัญ — การเกิดลูกรุ่นแรก", "19 มิถุนายน 2569 — เปิดทางสู่ Phase 6 Natural Selection");
  num(s, 18);
  const ms2 = [
    { lbl: "Body 37\nDurability = 10", sub: "สืบพันธุ์ไม่ได้\nstructurally blocked", col: C.red, ico: "✗" },
    { lbl: "เปลี่ยน body → 38\nDurability = 26", sub: "ผ่านประตู\nDurability ✓", col: C.amber, ico: "⚙" },
    { lbl: "ปรับ energy\neconomy", sub: "food×50 + drain×0.05\nmean energy 1000s", col: C.teal, ico: "⚡" },
    { lbl: "เกิด 50 ตัว\n50 → 100", sub: "Phase 6\nพร้อมทดสอบ", col: C.green, ico: "✓" },
  ];
  ms2.forEach((m, i) => {
    const x = 0.4 + i * 2.38;
    s.addShape(pres.shapes.OVAL, { x: x + 0.84, y: 1.2, w: 0.7, h: 0.7, fill: { color: m.col }, line: { color: m.col } });
    s.addText(m.ico, { x: x + 0.84, y: 1.22, w: 0.7, h: 0.66, fontSize: 20, bold: true, color: C.white, align: "center", fontFace: "Calibri", valign: "middle" });
    if (i < 3) s.addShape(pres.shapes.RECTANGLE, { x: x + 1.55, y: 1.52, w: 0.85, h: 0.06, fill: { color: C.iceBlueMid }, line: { color: C.iceBlueMid } });
    card(s, x, 2.05, 2.2, 1.8, m.col === C.green ? "F0FFF4" : C.offWhite, m.col);
    s.addText(m.lbl, { x: x+0.05, y: 2.15, w: 2.1, h: 0.85, fontSize: 13, bold: true, color: m.col, align: "center", fontFace: "Calibri" });
    s.addText(m.sub, { x: x+0.05, y: 2.98, w: 2.1, h: 0.75, fontSize: 12, color: C.muted, align: "center", fontFace: "Calibri" });
  });
  card(s, 0.4, 4.05, 9.2, 1.22, "F0FFF4", C.green);
  s.addText("ประชากร  50 → 100  ตัว", { x: 0.55, y: 4.13, w: 9, h: 0.55, fontSize: 26, bold: true, color: C.green, align: "center", fontFace: "Calibri" });
  s.addText("ก้าวสำคัญที่เปิดทางไปสู่ Phase 6 — การคัดเลือกทางธรรมชาติข้ามรุ่น", { x: 0.55, y: 4.67, w: 9, h: 0.48, fontSize: 13, color: C.navy, align: "center", fontFace: "Calibri" });
}

// ── SLIDE 19 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  hdr(s, "แผนงานต่อไปและประโยชน์ที่คาดว่าจะได้รับ");
  num(s, 19);
  s.addText("Phase ถัดไป", { x: 0.4, y: 1.08, w: 4.5, h: 0.48, fontSize: 17, bold: true, color: C.navy, fontFace: "Calibri" });
  [
    { ph: "Phase 6", desc: "Natural Selection — วัดว่า gene ที่ดีกว่า\nถ่ายทอดสู่รุ่นลูกได้จริงหรือไม่" },
    { ph: "Phase 7", desc: "สรุปผลรวม — SLI / PPV / Causal Chain\nด้วย Metabolism Physics v2 เต็มรูปแบบ" },
    { ph: "YSC 2026", desc: "ส่งงานวิจัยฉบับสมบูรณ์\n~สิงหาคม 2569" },
  ].forEach((st, i) => {
    card(s, 0.4, 1.65 + i * 1.18, 4.5, 1.02, C.offWhite, C.navy);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.4, y: 1.65 + i * 1.18, w: 1.15, h: 1.02, fill: { color: C.navy }, rectRadius: 0.08, line: { color: C.navy } });
    s.addText(st.ph, { x: 0.4, y: 1.67 + i * 1.18, w: 1.15, h: 0.98, fontSize: 12, bold: true, color: C.iceBlue, align: "center", fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addText(st.desc, { x: 1.65, y: 1.72 + i * 1.18, w: 3.1, h: 0.88, fontSize: 12, color: C.text, fontFace: "Calibri", valign: "middle" });
  });
  s.addText("ประโยชน์ที่คาดว่าจะได้รับ", { x: 5.3, y: 1.08, w: 4.4, h: 0.48, fontSize: 17, bold: true, color: C.navy, fontFace: "Calibri" });
  [
    "สภาพแวดล้อมจำลองต้นแบบสำหรับวิจัย ALife",
    "ชุดตัวชี้วัด SLI / PPV / Causal Chain ที่ใช้ได้จริง",
    "แนวทางรายงานผลที่ซื่อสัตย์ ไม่ตีความเกิน",
    "ฐานสำหรับ AI สำรวจดาวดวงอื่น / สภาพแวดล้อมใหม่",
    "ประสบการณ์วิจัยครบวงจรในระดับมัธยมศึกษา",
  ].forEach((b, i) => {
    s.addText([{ text: "◆  ", options: { bold: true, color: C.teal } }, { text: b }], { x: 5.3, y: 1.65 + i * 0.7, w: 4.4, h: 0.62, fontSize: 13, color: C.text, fontFace: "Calibri" });
  });
}

// ── SLIDE 20 ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.navyDeep };
  s.addShape(pres.shapes.OVAL, { x: 7.5, y: -0.8, w: 3.8, h: 3.8, fill: { color: C.iceBlueMid, transparency: 82 }, line: { color: C.iceBlueMid, transparency: 82 } });
  s.addText("สรุป", { x: 0.5, y: 0.22, w: 9, h: 0.65, fontSize: 36, bold: true, color: C.iceBlue, fontFace: "Calibri" });
  card(s, 0.5, 1.0, 9, 1.35, C.navyMid, C.iceBlue);
  s.addText("สมมติฐาน:", { x: 0.65, y: 1.08, w: 2.5, h: 0.45, fontSize: 13, bold: true, color: C.iceBlue, fontFace: "Calibri" });
  s.addText("ตัวแทน AI ในสภาพแวดล้อมที่มีวงจรเชิงเหตุผลเสถียร อาจเกิดพฤติกรรมที่มีลักษณะของความรู้เชิงสภาพแวดล้อม แม้ไม่ได้รับข้อมูลใดล่วงหน้า", { x: 0.65, y: 1.5, w: 8.7, h: 0.72, fontSize: 13, italic: true, color: C.iceBlueMid, fontFace: "Calibri" });
  const items = [
    { lbl: "Phase 1–3", st: "ผ่านแล้ว", detail: "นิเวศเสถียร | SLI 33–52× | Causal Chain ยืนยันได้", col: C.green },
    { lbl: "Metabolism v2", st: "สร้างเสร็จ", detail: "Endozoochory verified | Hand-coded bias ถูกลบออก", col: C.teal },
    { lbl: "First Births", st: "สำเร็จ", detail: "ประชากร 50→100 เมื่อ 19 มิ.ย. 2569", col: C.sky },
    { lbl: "Phase 6+", st: "กำลังดำเนินการ", detail: "Natural selection + YSC 2026 สิงหาคมนี้", col: C.amber },
  ];
  items.forEach((it, i) => {
    const y = 2.55 + i * 0.65;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 1.5, h: 0.52, fill: { color: it.col }, rectRadius: 0.08, line: { color: it.col } });
    s.addText(it.lbl, { x: 0.5, y, w: 1.5, h: 0.52, fontSize: 12, bold: true, color: C.white, align: "center", fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addText(it.st, { x: 2.2, y: y + 0.05, w: 1.6, h: 0.42, fontSize: 13, bold: true, color: it.col, fontFace: "Calibri" });
    s.addText(it.detail, { x: 3.82, y: y + 0.05, w: 5.88, h: 0.42, fontSize: 12, color: C.iceBlueMid, fontFace: "Calibri" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 5.1, w: 9, h: 0.4, fill: { color: C.iceBlue }, rectRadius: 0.08, line: { color: C.iceBlue } });
  s.addText("รายงานผลตามหลักฐานที่วัดได้ — ไม่ตีความพฤติกรรมตัวแทนเกินกว่าข้อมูล", { x: 0.5, y: 5.12, w: 9, h: 0.36, fontSize: 14, bold: true, color: C.navy, align: "center", fontFace: "Calibri", margin: 0 });
}

pres.writeFile({ fileName: "C:\\artificial-evolution\\reports\\TURC2026_presentation.pptx" })
  .then(() => console.log("DONE"))
  .catch(err => { console.error(err); process.exit(1); });

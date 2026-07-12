// Build the NSRU food+toxin competition report (.docx) from the markdown source.
// Same formatter as build_nsru_docx.js; only the input/output paths differ.
// Format follows the official spec: A4, one-sided, TH SarabunPSK 16pt,
// margins: top/left 3.18cm (1.5"), bottom/right 2.54cm (1").
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, HeadingLevel,
  PageNumber, Footer, ImageRun,
} = require("docx");

const REPORT_DIR = "C:\\artificial-evolution\\reports";
const MD_PATH = process.argv[2] || path.join(REPORT_DIR, "nsru_report_food_toxin_2026-07-11.th.md");
const OUT_PATH = process.argv[3] || path.join(REPORT_DIR, "nsru_report_food_toxin_2026-07-11.th.docx");

const FONT = "TH SarabunPSK";
const MONO = "Consolas";
const BODY_SIZE = 32; // 16pt (half-points)
const ACCENT = "1F4E79";
const WHITE = "FFFFFF";
const CENTER = AlignmentType.CENTER;
const DXA = WidthType.DXA;
const CLEAR = ShadingType.CLEAR;

// A4 in DXA (1440 DXA = 1 inch)
const PAGE_W = 11906;
const PAGE_H = 16838;
const M_TOP = 2160;    // 1.5"
const M_BOTTOM = 1440; // 1"
const M_LEFT = 2160;   // 1.5"
const M_RIGHT = 1440;  // 1"
const CONTENT_W = PAGE_W - M_LEFT - M_RIGHT; // 8306 DXA

const cellBorder = { style: BorderStyle.SINGLE, size: 4, color: "AAAAAA" };
const borders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };
const cellMargins = { top: 50, bottom: 50, left: 90, right: 90 };

function parseInline(text, opts = {}) {
  const base = { font: FONT, size: BODY_SIZE, bold: !!opts.bold, italics: !!opts.italics, color: opts.color };
  const runs = [];
  const re = /\*\*(.+?)\*\*|`([^`]+?)`/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) runs.push(new TextRun({ ...base, text: text.slice(last, m.index) }));
    if (m[1] !== undefined) runs.push(new TextRun({ ...base, text: m[1], bold: true }));
    else runs.push(new TextRun({ ...base, text: m[2], font: MONO, size: BODY_SIZE - 4 }));
    last = m.index + m[0].length;
  }
  if (last < text.length) runs.push(new TextRun({ ...base, text: text.slice(last) }));
  return runs.length ? runs : [new TextRun({ ...base, text })];
}

function body(text, brk) {
  return new Paragraph({ pageBreakBefore: !!brk, spacing: { after: 60, line: 276 }, children: parseInline(text) });
}

function heading(text, level, brk) {
  const sizes = { 1: 34, 2: 30, 3: 28 };
  const colors = { 1: ACCENT, 2: ACCENT, 3: "333333" };
  const hl = level === 1 ? HeadingLevel.HEADING_1 : level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3;
  return new Paragraph({
    heading: hl,
    pageBreakBefore: !!brk,
    spacing: { before: level === 1 ? 200 : 140, after: 70 },
    children: [new TextRun({ text, font: FONT, size: sizes[level], bold: true, color: colors[level] })],
  });
}

function listItem(marker, text) {
  return new Paragraph({
    indent: { left: 620, hanging: 320 },
    spacing: { after: 40, line: 276 },
    children: [new TextRun({ text: marker + "  ", font: FONT, size: BODY_SIZE }), ...parseInline(text)],
  });
}

function quote(text, brk) {
  return new Paragraph({
    pageBreakBefore: !!brk,
    indent: { left: 480 },
    spacing: { before: 40, after: 80, line: 288 },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 140 } },
    children: parseInline(text, { italics: true }),
  });
}

function coverPara(text, opts = {}) {
  return new Paragraph({
    alignment: CENTER,
    pageBreakBefore: !!opts.brk,
    spacing: { before: opts.before || 0, after: opts.after || 100 },
    children: parseInline(text, { bold: opts.bold, color: opts.color }).map(r => r),
  });
}

function coverTitle(text, brk) {
  return new Paragraph({
    alignment: CENTER,
    pageBreakBefore: !!brk,
    spacing: { before: 120, after: 120 },
    children: [new TextRun({ text, font: FONT, size: 30, bold: true })],
  });
}

function tableCell(text, opts = {}) {
  return new TableCell({
    borders,
    width: { size: opts.width || CONTENT_W, type: DXA },
    shading: opts.header ? { fill: ACCENT, type: CLEAR } : { fill: opts.fill || WHITE, type: CLEAR },
    margins: cellMargins,
    children: [new Paragraph({
      keepNext: true,   // keep rows (and caption) together -> table never orphans a row across a page
      spacing: { after: 0, line: 252 },
      children: parseInline(text, { bold: opts.header, color: opts.header ? WHITE : undefined })
        .map(r => r),
    })],
  });
}

function renderTable(rows) {
  const n = rows[0].length;
  let colWidths;
  if (n === 2) { const c1 = Math.round(CONTENT_W * 0.42); colWidths = [c1, CONTENT_W - c1]; }
  else { const c = Math.floor(CONTENT_W / n); colWidths = Array(n).fill(c); colWidths[n - 1] = CONTENT_W - c * (n - 1); }
  return new Table({
    width: { size: CONTENT_W, type: DXA },
    columnWidths: colWidths,
    rows: rows.map((row, ri) => new TableRow({
      cantSplit: true,   // a single row must not break across a page
      tableHeader: ri === 0,
      children: row.map((cell, ci) => tableCell(cell, {
        width: colWidths[ci], header: ri === 0,
        fill: ri > 0 && ri % 2 === 0 ? "EEF3F8" : WHITE,
      })),
    })),
  });
}

function codeBlock(linesArr) {
  const paras = linesArr.map(l => new Paragraph({
    spacing: { after: 0, line: 240 },
    children: [new TextRun({ text: l.length ? l : " ", font: MONO, size: 21 })],
  }));
  return new Table({
    width: { size: CONTENT_W, type: DXA },
    columnWidths: [CONTENT_W],
    rows: [new TableRow({ children: [new TableCell({
      borders, width: { size: CONTENT_W, type: DXA },
      shading: { fill: "F4F4F4", type: CLEAR },
      margins: { top: 70, bottom: 70, left: 140, right: 140 },
      children: paras,
    })] })],
  });
}

function pngSize(buf) { return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) }; }

function image(relPath, caption, brk) {
  const abs = path.join(REPORT_DIR, relPath);
  const data = fs.readFileSync(abs);
  const { w, h } = pngSize(data);
  const maxW = 500;
  const dispW = Math.min(w, maxW);
  const dispH = Math.round(h * dispW / w);
  const out = [];
  out.push(new Paragraph({
    alignment: CENTER, pageBreakBefore: !!brk, spacing: { before: 100, after: 20 },
    children: [new ImageRun({ type: "png", data, transformation: { width: dispW, height: dispH } })],
  }));
  if (caption) out.push(new Paragraph({
    alignment: CENTER, spacing: { after: 140 },
    children: [new TextRun({ text: caption, font: FONT, size: 26, italics: true, color: "555555" })],
  }));
  return out;
}

const md = fs.readFileSync(MD_PATH, "utf8");
const lines = md.split(/\r?\n/);
const children = [];

let i = 0;
let firstMajor = true;
let pendingBreak = false;
let coverMode = false;

function consumeBreak() { const b = pendingBreak; pendingBreak = false; return b; }
function flushBreakBeforeBlock() {
  if (pendingBreak) { children.push(new Paragraph({ pageBreakBefore: true, spacing: { after: 0 }, children: [] })); pendingBreak = false; }
}

while (i < lines.length) {
  const raw = lines[i];
  const line = raw.trim();

  if (line === "" || line === "---") { i++; continue; }

  if (line.startsWith("# ")) {
    const text = line.slice(2).trim();
    if (!firstMajor) pendingBreak = true;
    firstMajor = false;
    if (text === "ปก" || text === "ปกใน") { coverMode = true; i++; continue; }
    coverMode = false;
    children.push(heading(text, 1, consumeBreak()));
    i++; continue;
  }
  if (line.startsWith("## ")) {
    const text = line.slice(3).trim();
    if (coverMode) { children.push(coverTitle(text, consumeBreak())); i++; continue; }
    children.push(heading(text, 2, consumeBreak()));
    i++; continue;
  }
  if (line.startsWith("### ")) { children.push(heading(line.slice(4).trim(), 3, consumeBreak())); i++; continue; }

  const img = line.match(/^!\[(.*?)\]\((.+?)\)$/);
  if (img) { flushBreakBeforeBlock(); image(img[2].trim(), img[1].trim(), false).forEach(p => children.push(p)); i++; continue; }

  if (line.startsWith("|")) {
    const rows = [];
    while (i < lines.length && lines[i].trim().startsWith("|")) {
      const cells = lines[i].trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(s => s.trim());
      if (!cells.every(c => /^:?-+:?$/.test(c))) rows.push(cells);
      i++;
    }
    flushBreakBeforeBlock();
    children.push(renderTable(rows));
    children.push(new Paragraph({ spacing: { after: 60 }, children: [] }));
    continue;
  }

  if (line.startsWith("```")) {
    i++; const buf = [];
    while (i < lines.length && !lines[i].trim().startsWith("```")) { buf.push(lines[i]); i++; }
    i++;
    flushBreakBeforeBlock();
    children.push(codeBlock(buf));
    children.push(new Paragraph({ spacing: { after: 60 }, children: [] }));
    continue;
  }

  if (line.startsWith("> ")) { children.push(quote(line.slice(2).trim(), consumeBreak())); i++; continue; }

  if (line.startsWith("- ")) {
    if (coverMode) { children.push(coverPara(line.slice(2).trim())); i++; continue; }
    flushBreakBeforeBlock();
    children.push(listItem("•", line.slice(2).trim())); i++; continue;
  }
  const numMatch = line.match(/^(\d+)\.\s+(.*)$/);
  if (numMatch) {
    if (coverMode) { children.push(coverPara(numMatch[2].trim())); i++; continue; }
    flushBreakBeforeBlock();
    children.push(listItem(numMatch[1] + ".", numMatch[2].trim())); i++; continue;
  }

  if (coverMode) { children.push(coverPara(line, { brk: consumeBreak() })); i++; continue; }
  children.push(body(line, consumeBreak()));
  i++;
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: BODY_SIZE } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, font: FONT, color: ACCENT }, paragraph: { spacing: { before: 200, after: 70 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, font: FONT, color: ACCENT }, paragraph: { spacing: { before: 140, after: 70 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: "333333" }, paragraph: { spacing: { before: 120, after: 60 }, outlineLevel: 2 } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: M_TOP, right: M_RIGHT, bottom: M_BOTTOM, left: M_LEFT } } },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: CENTER,
        children: [new TextRun({ text: "หน้า ", font: FONT, size: 22 }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 22 })],
      })] }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT_PATH, buf);
  console.log("Done:", OUT_PATH, "(", buf.length, "bytes )");
});

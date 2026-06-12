from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "รายงาน_Concept_Proposal.pdf"
FLOWCHART = ROOT / "assets" / "population_continuity_flowchart.png"
FONT_DIR = ROOT / "assets" / "fonts"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Sarabun", str(FONT_DIR / "Sarabun-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Sarabun-Bold", str(FONT_DIR / "Sarabun-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Sarabun-Italic", str(FONT_DIR / "Sarabun-Italic.ttf")))


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("\n", "<br/>"), style)


def bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, style), leftIndent=0) for item in items],
        bulletType="bullet",
        start="bulletchar",
        bulletFontName="Sarabun",
        bulletFontSize=16,
        leftIndent=18,
        bulletIndent=0,
        bulletOffsetY=1,
    )


def numbered(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, style), leftIndent=0) for item in items],
        bulletType="1",
        start="1",
        bulletFontName="Sarabun",
        bulletFontSize=16,
        leftIndent=20,
        bulletIndent=0,
    )


def add_page_number(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Sarabun", 12)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawCentredString(A4[0] / 2, 0.65 * cm, f"หน้า {doc.page}")
    canvas.restoreState()


def build() -> None:
    register_fonts()

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=1.55 * cm,
        rightMargin=1.55 * cm,
        topMargin=1.25 * cm,
        bottomMargin=1.20 * cm,
        title="Concept Proposal",
        author="Artificial Evolution Project",
    )

    styles = {
        "title": ParagraphStyle(
            "title",
            fontName="Sarabun-Bold",
            fontSize=21,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=5,
            wordWrap="CJK",
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Sarabun",
            fontSize=15,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334155"),
            spaceAfter=3,
            wordWrap="CJK",
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName="Sarabun-Bold",
            fontSize=18,
            leading=21,
            textColor=colors.HexColor("#1D4ED8"),
            spaceBefore=7,
            spaceAfter=3,
            keepWithNext=True,
            wordWrap="CJK",
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Sarabun-Bold",
            fontSize=16,
            leading=19,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=5,
            spaceAfter=2,
            keepWithNext=True,
            wordWrap="CJK",
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Sarabun",
            fontSize=16,
            leading=19,
            textColor=colors.HexColor("#111827"),
            alignment=TA_LEFT,
            spaceAfter=4,
            wordWrap="CJK",
        ),
        "body_tight": ParagraphStyle(
            "body_tight",
            fontName="Sarabun",
            fontSize=16,
            leading=18,
            textColor=colors.HexColor("#111827"),
            alignment=TA_LEFT,
            spaceAfter=2,
            wordWrap="CJK",
        ),
        "note": ParagraphStyle(
            "note",
            fontName="Sarabun-Italic",
            fontSize=13,
            leading=15,
            textColor=colors.HexColor("#475569"),
            alignment=TA_LEFT,
            spaceAfter=4,
            wordWrap="CJK",
        ),
    }

    story = []
    story.append(p("Concept Proposal", styles["subtitle"]))
    story.append(p("1) ชื่อโครงงาน", styles["h1"]))
    story.append(
        p(
            "การศึกษาปัจจัยที่ส่งผลต่อการอยู่รอดข้ามรุ่นของประชากรในระบบ Artificial Life",
            styles["title"],
        )
    )
    story.append(
        p("Investigating Cross-Generational Survival in Artificial Life Simulations", styles["subtitle"])
    )
    story.append(p("ประเภทโครงงาน: สาขาวิทยาศาสตร์ประยุกต์", styles["body_tight"]))
    story.append(
        p(
            "คำสำคัญ: Artificial Life, Artificial Evolution, Agent-Based Simulation, Population Continuity, Social Emergence, Technology Emergence",
            styles["body_tight"],
        )
    )
    story.append(p("หมายเหตุ: จัดทำตามข้อกำหนด Concept Proposal ไม่เกิน 5 หน้า และใช้ฟอนต์ Sarabun/TH Sarabun ขนาด 16 pt", styles["note"]))

    story.append(p("2) สมาชิก", styles["h1"]))
    members = [
        "หัวหน้าทีม: ชื่อ นายชิษณุพงศ์ นามสกุล อินทร์จันทร์ ระดับชั้น ม.4 โรงเรียนดีบุกพังงาวิทยายน",
        "อาจารย์ที่ปรึกษา: ชื่อ ................................................ นามสกุล ................................................ สังกัด ................................................",
    ]
    for item in members:
        story.append(p(item, styles["body_tight"]))

    story.append(p("3) ความเป็นมาและเหตุผล", styles["h1"]))
    background = [
        "เป้าหมายสูงสุดของโครงงานนี้คือการศึกษาว่า หากสร้างโลกจำลองขึ้นจากศูนย์และปล่อยให้สิ่งมีชีวิตประดิษฐ์ที่มีความสามารถในการเรียนรู้และตัดสินใจดำรงอยู่ภายใต้ข้อจำกัดด้านพลังงาน ทรัพยากร และการสืบพันธุ์ พวกมันจะค่อย ๆ สร้างรูปแบบสังคม เครื่องมือ และเทคโนโลยีแบบใดขึ้นมา และเส้นทางเหล่านั้นจะเหมือนหรือต่างจากเส้นทางของมนุษย์อย่างไร",
        "เพื่อศึกษาคำถามนี้อย่างเป็นระบบ โครงงานใช้แนวทาง Artificial Life หรือการจำลองสิ่งมีชีวิตประดิษฐ์ โดยสร้างโลกจำลองที่มีเอเจนต์อาศัยอยู่ภายใต้ทรัพยากรจำกัด เอเจนต์มีพลังงาน ร่างกาย พฤติกรรมพื้นฐาน การสร้างรัง การเก็บเสบียง การดูแลลูก การสืบพันธุ์ และการใช้วัตถุหรือเครื่องมือพื้นฐาน โลกจำลองลักษณะนี้ช่วยให้ทดลองได้ว่า ภายใต้ข้อจำกัดของสภาพแวดล้อม ประชากรจะอยู่รอด เกิดพฤติกรรมทางสังคม และค่อย ๆ สะสมพฤติกรรมหรือเทคโนโลยีได้หรือไม่",
        "อย่างไรก็ตาม ก่อนจะตอบคำถามใหญ่เรื่องการเกิดสังคมและเทคโนโลยีได้ ต้องแก้คำถามพื้นฐานก่อน คือประชากรในโลกจำลองต้องอยู่รอดข้ามรุ่นได้พอสมควร หากประชากรสูญพันธุ์เร็วเกินไป จะไม่มีเวลามากพอให้เกิดการทดลองซ้ำ การใช้เครื่องมือ การเรียนรู้จากรุ่นก่อน หรือการส่งต่อสิ่งที่ค้นพบไปยังรุ่นถัดไป ดังนั้น ความต่อเนื่องของประชากรจึงเป็นเงื่อนไขสำคัญของการศึกษาการเกิดสังคมและเทคโนโลยีระยะยาว",
        "จากการพัฒนาและทดลองเบื้องต้น ระบบสามารถทำให้เอเจนต์เกิดลูก สร้างรัง เก็บอาหาร และทำให้ลูกบางส่วนเติบโตได้แล้ว แต่ประชากรยังมีแนวโน้มสูญพันธุ์ในระยะยาว แม้บางช่วงจะมีทรัพยากรสะสมอยู่ ปัญหาจึงอาจไม่ได้อยู่ที่การไม่มีอาหารหรือไม่มีการสืบพันธุ์เลย แต่อาจอยู่ที่เงื่อนไขหลายอย่างไม่พร้อมพร้อมกัน เช่น พลังงานไม่พอ อาหารในรังไม่พอ ไม่พบคู่ หรือช่วงวัยของรุ่นพ่อแม่และรุ่นลูกไม่ซ้อนทับกันพอ งานวิจัยนี้จึงมุ่งศึกษาว่าปัจจัยใดทำให้ประชากรในระบบ Artificial Life สามารถต่อรุ่นได้อย่างต่อเนื่องมากขึ้น",
    ]
    for para in background:
        story.append(p(para, styles["body"]))

    story.append(p("คำถามวิจัย", styles["h2"]))
    story.append(
        p(
            "ปัจจัยใดเป็นคอขวดสำคัญที่ทำให้ประชากรในระบบ Artificial Life ไม่สามารถอยู่รอดข้ามรุ่นได้อย่างต่อเนื่อง",
            styles["body"],
        )
    )

    story.append(p("4) วัตถุประสงค์", styles["h1"]))
    story.append(
        numbered(
            [
                "เพื่อพัฒนาและใช้แบบจำลอง Artificial Life สำหรับศึกษาการอยู่รอดข้ามรุ่นของประชากรภายใต้ทรัพยากรจำกัด",
                "เพื่อศึกษาปัจจัยที่เป็นคอขวดของการสืบพันธุ์และการอยู่รอดข้ามรุ่นของเอเจนต์",
                "เพื่อสร้างตัวชี้วัดสำหรับประเมินความต่อเนื่องของประชากร เช่น ระยะเวลาที่อยู่รอด จำนวนการเกิด จำนวนลูกที่เติบโต และอัตราการสูญพันธุ์",
            ],
            styles["body_tight"],
        )
    )
    story.append(p("สมมติฐานการวิจัย", styles["h2"]))
    story.append(
        p(
            "ประชากรในระบบ Artificial Life ไม่ได้สูญพันธุ์เพราะขาดอาหารเพียงอย่างเดียว แต่เกิดจากการที่เงื่อนไขสำคัญของการสืบพันธุ์ เช่น พลังงาน อาหารในรัง การพบคู่ และช่วงวัย ไม่พร้อมกันในช่วงเวลาที่เหมาะสม",
            styles["body"],
        )
    )

    story.append(PageBreak())
    story.append(p("5) กรอบความคิด", styles["h1"]))
    story.append(
        p(
            "แนวคิดของโครงงานคือ การศึกษาการเกิดสังคมและเทคโนโลยีในโลกจำลองต้องเริ่มจากการทำให้ประชากรอยู่รอดข้ามรุ่นได้ก่อน เพราะการเกิด ใช้ซ้ำ สะสม และส่งต่อพฤติกรรมหรือเทคโนโลยีต้องอาศัยเวลาและความต่อเนื่องของประชากร",
            styles["body"],
        )
    )
    img = Image(str(FLOWCHART))
    img.drawWidth = 17.2 * cm
    img.drawHeight = img.drawWidth * 1000 / 1800
    story.append(img)
    story.append(Spacer(1, 3))

    story.append(p("ตัวแปรต้น", styles["h2"]))
    story.append(
        bullets(
            [
                "ปริมาณอาหารและทรัพยากรในโลกจำลอง",
                "พลังงานเริ่มต้นและอัตราการใช้พลังงานของเอเจนต์",
                "เงื่อนไขการสืบพันธุ์ เช่น พลังงานขั้นต่ำ อาหารในรัง การพบคู่ และช่วงวัยที่เหมาะสม",
            ],
            styles["body_tight"],
        )
    )
    story.append(p("ตัวแปรตาม", styles["h2"]))
    story.append(
        bullets(
            [
                "ระยะเวลาที่ประชากรอยู่รอด",
                "จำนวนการเกิดของเอเจนต์ และจำนวนลูกที่เติบโตถึงวัยสืบพันธุ์",
                "การสูญพันธุ์หรือไม่สูญพันธุ์ของประชากร",
                "ช่วงเวลาที่เริ่มเกิดพฤติกรรมทางสังคม การใช้วัตถุ หรือเครื่องมือพื้นฐาน",
            ],
            styles["body_tight"],
        )
    )
    story.append(p("ตัวแปรควบคุม", styles["h2"]))
    story.append(
        bullets(
            [
                "ขนาดโลกจำลอง กฎพื้นฐานของการเกิดอาหารและทรัพยากร",
                "จำนวนประชากรเริ่มต้น ระยะเวลาการทดลอง และ seed ที่ใช้ในการรันซ้ำ",
            ],
            styles["body_tight"],
        )
    )
    story.append(p("วิธีดำเนินงานโดยสรุป", styles["h2"]))
    story.append(
        numbered(
            [
                "สร้างหรือใช้โลกจำลอง Artificial Life ที่มีเอเจนต์ ทรัพยากร พลังงาน รัง และการสืบพันธุ์",
                "กำหนดเงื่อนไขทดลอง เช่น จำนวนประชากรเริ่มต้น ปริมาณอาหาร และเงื่อนไขการสืบพันธุ์",
                "รันการทดลองหลายครั้งโดยควบคุมตัวแปรสำคัญและเปลี่ยนเฉพาะปัจจัยที่ต้องการศึกษา",
                "เก็บข้อมูลผลลัพธ์ เช่น ระยะเวลาที่อยู่รอด จำนวนการเกิด จำนวนลูกที่เติบโต และสาเหตุการสูญพันธุ์",
                "วิเคราะห์ว่าปัจจัยใดสัมพันธ์กับความต่อเนื่องของประชากร และใช้ผลที่ได้เป็นฐานสำหรับศึกษาการเกิดสังคมและการส่งต่อเทคโนโลยีต่อไป",
            ],
            styles["body_tight"],
        )
    )

    story.append(p("6) ประโยชน์ที่คาดว่าจะได้รับ", styles["h1"]))
    story.append(
        numbered(
            [
                "ได้แบบจำลองคอมพิวเตอร์สำหรับศึกษาการอยู่รอดของประชากรในระบบ Artificial Life",
                "ได้ความเข้าใจว่าปัจจัยใดทำให้ประชากรในโลกจำลองสามารถอยู่รอดข้ามรุ่นหรือสูญพันธุ์",
                "ได้ตัวชี้วัดที่ใช้ประเมินความต่อเนื่องของประชากรอย่างเป็นระบบ",
                "ได้พื้นฐานสำหรับต่อยอดไปศึกษาการเกิดรูปแบบสังคม การใช้ซ้ำ การสะสม และการส่งต่อเทคโนโลยีในโลกจำลอง",
                "ได้ฝึกกระบวนการวิจัยเชิงวิทยาศาสตร์ ตั้งแต่การตั้งคำถาม การควบคุมตัวแปร การรันซ้ำ การเก็บข้อมูล และการวิเคราะห์ผล",
            ],
            styles["body_tight"],
        )
    )

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    reader = PdfReader(str(OUT))
    if len(reader.pages) > 5:
        raise SystemExit(f"PDF exceeds requirement: {len(reader.pages)} pages")
    print(f"Wrote {OUT} ({len(reader.pages)} pages)")


if __name__ == "__main__":
    build()

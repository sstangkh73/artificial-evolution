// NSRU presentation deck (10 slides, Thai) built from the video script.
// Figures embedded from reports/figures/. Narration in speaker notes.
const pptxgen = require("pptxgenjs");
const FIG = "C:\\artificial-evolution\\reports\\figures\\";
const OUT = "C:\\artificial-evolution\\reports\\nsru_slides_2026-07-11.pptx";

const DARK="13312C", GREEN="0F6E56", RED="B2352E", AMBER="B7791F",
      INK="22302E", MUTED="6A7B77", TINT="EAF3EF", REDTINT="F7E9E7",
      GOLDTINT="F6EEDD", WHITE="FFFFFF";
const F="Tahoma";
const CW=13.33, CH=7.5, MX=0.6;

const p=new pptxgen();
p.layout="LAYOUT_WIDE";
p.defineSlideMaster({ title:"BASE", background:{color:WHITE} });

const shadow=()=>({type:"outer",color:"9AA6A2",blur:6,offset:2,angle:90,opacity:0.35});

function badge(s,n,x,y,color){
  s.addShape(p.ShapeType.ellipse,{x,y,w:0.62,h:0.62,fill:{color},line:{type:"none"}});
  s.addText(String(n),{x,y,w:0.62,h:0.62,align:"center",valign:"middle",fontFace:F,fontSize:22,bold:true,color:WHITE,margin:0});
}
function heading(s,n,title){
  badge(s,n,MX,0.5,GREEN);
  s.addText(title,{x:MX+0.8,y:0.46,w:CW-MX*2-0.8,h:0.72,fontFace:F,fontSize:30,bold:true,color:INK,align:"left",valign:"middle",margin:0});
}
function stat(s,x,y,w,num,label,color,tint,fs){
  const H=1.72;
  s.addShape(p.ShapeType.roundRect,{x,y,w,h:H,fill:{color:tint},line:{type:"none"},rectRadius:0.1,shadow:shadow()});
  s.addText(num,{x:x+0.05,y:y+0.14,w:w-0.1,h:0.82,align:"center",valign:"middle",fontFace:F,fontSize:fs||30,bold:true,color,margin:0});
  s.addText(label,{x:x+0.1,y:y+0.98,w:w-0.2,h:0.64,align:"center",valign:"top",fontFace:F,fontSize:12,color:INK,margin:0});
}
function img(s,file,x,y,w,h){
  s.addImage({path:FIG+file+".png",x,y,w,h,sizing:{type:"contain",w,h},shadow:shadow()});
}
function bullets(s,items,x,y,w,h,fs){
  s.addText(items.map((t,i)=>({text:t,options:{bullet:{code:"2022",indent:14},breakLine:true,paraSpaceAfter:8,fontFace:F,fontSize:fs||16,color:INK}})),
    {x,y,w,h,valign:"top",align:"left",margin:0});
}

// ---------- Slide 1: title (dark) ----------
let s=p.addSlide();
s.background={color:DARK};
s.addText("กับดักพิษแปรผัน",{x:MX,y:1.2,w:8.6,h:1.0,fontFace:F,fontSize:42,bold:true,color:AMBER,align:"left",valign:"middle",margin:0});
s.addText("การศึกษาพฤติกรรมการเรียนรู้เพื่อหลีกเลี่ยงอันตรายของปัญญาประดิษฐ์ในสภาพแวดล้อมจำลอง",
  {x:MX,y:2.35,w:8.6,h:1.7,fontFace:F,fontSize:20,bold:true,color:WHITE,align:"left",valign:"top",margin:0});
s.addText("บทเรียนความปลอดภัยของ AI ในโลกที่อันตรายเปลี่ยนตามเวลา",
  {x:MX,y:4.15,w:8.3,h:0.5,fontFace:F,fontSize:15,italic:true,color:"AFC6BD",align:"left",margin:0});
s.addText([{text:"นายชิษณุพงศ์ อินทร์จันทร์",options:{bold:true,breakLine:true}},{text:"โรงเรียนดีบุกพังงาวิทยายน",options:{color:"CFE3DA"}}],
  {x:MX,y:5.9,w:7,h:1,fontFace:F,fontSize:16,color:WHITE,align:"left",margin:0});
// right hook circle
s.addShape(p.ShapeType.ellipse,{x:9.6,y:2.0,w:3.1,h:3.1,fill:{color:RED},line:{type:"none"},shadow:shadow()});
s.addText([{text:"63–99%",options:{fontSize:44,bold:true,color:WHITE,breakLine:true}},{text:"AI ถูกหลอกให้จัด\nพิษเป็นอาหารดีที่สุด",options:{fontSize:13,color:"FBE3E0"}}],
  {x:9.6,y:2.0,w:3.1,h:3.1,align:"center",valign:"middle",fontFace:F,margin:0});
s.addNotes("สวัสดีครับ ผมชิษณุพงศ์ จากโรงเรียนดีบุกพังงาวิทยายน โครงงานของผมเริ่มจากคำถามเดียว — ถ้าเราปล่อยปัญญาประดิษฐ์ลงในโลกที่ไม่มีใครบอกอะไรเลย มันจะเรียนรู้เองได้ไหมว่าอะไรกินได้ อะไรเป็นพิษ และผมเจอสิ่งที่ไม่คาดคิด คือ พิษที่หายได้ตามเวลา กลับหลอกให้ AI กินพิษมากขึ้น ไม่ใช่น้อยลง");

// ---------- Slide 2: motivation ----------
s=p.addSlide(); heading(s,1,"ทำไมต้องเรียนเองโดยไม่มีป้าย?");
bullets(s,[
 "AI ที่เก่งที่สุดวันนี้ (เช่น GPT) เก่งเพราะมนุษย์ \"ปักป้าย\" ข้อมูลให้ล่วงหน้า",
 "แต่ในโลกจริงหลายที่ มนุษย์เองก็ปักป้ายให้ไม่ได้ (พื้นที่ภัยพิบัติ ใต้ทะเล ดาวดวงอื่น)",
 "ยิ่งกว่านั้น อันตรายมัก \"เปลี่ยนตามเวลา\" — ผลไม้ดิบมีพิษ พอสุกกินได้ เน่าเป็นพิษ",
 "ใกล้ตัว: เห็ดป่าพิษที่คนไทยเก็บกินแล้วเสียชีวิตแทบทุกปี",
],MX,1.7,6.6,3.8,17);
s.addShape(p.ShapeType.roundRect,{x:7.7,y:2.0,w:5.0,h:3.4,fill:{color:TINT},line:{type:"none"},rectRadius:0.12,shadow:shadow()});
s.addText([{text:"คำถามวิจัย",options:{fontSize:16,bold:true,color:GREEN,breakLine:true,paraSpaceAfter:10}},
  {text:"ถ้าไม่มีป้ายให้ AI จะเรียนรู้เองได้ไหม และ \"ปลอดภัย\" แค่ไหน เมื่ออันตรายเปลี่ยนไปตามเวลา?",options:{fontSize:20,bold:true,color:INK}}],
  {x:8.05,y:2.3,w:4.3,h:2.8,valign:"middle",align:"left",fontFace:F,margin:0});
s.addNotes("AI ที่เก่งที่สุดวันนี้อย่าง GPT เก่งได้เพราะมนุษย์ป้อนข้อมูลที่ปักป้ายกำกับไว้ให้มหาศาล แต่ในโลกจริงหลายที่ มนุษย์เองก็ไม่รู้คำตอบและปักป้ายให้ไม่ได้ เช่น หุ่นยนต์กู้ภัยที่ต้องตัดสินเองว่าสารตรงนั้นอันตรายไหม ยิ่งไปกว่านั้น อันตรายในธรรมชาติมักเปลี่ยนตามเวลา ผลไม้ดิบมีพิษ พอสุกกินได้ เก็บนานก็เน่าเป็นพิษ ใกล้ตัวเราคือเห็ดป่าที่คนไทยเก็บกินแล้วเสียชีวิตแทบทุกปี คำถามคือ AI ที่เรียนรู้เองแบบง่ายจะรับมืออันตรายที่เปลี่ยนตามเวลาได้ไหม");

// ---------- Slide 3: what I built ----------
s=p.addSlide(); heading(s,2,"สิ่งที่สร้าง: โลกจำลองที่ไม่มีป้ายกำกับ");
img(s,"fig_world_overview",6.0,1.55,6.9,4.25);
bullets(s,[
 "โลกจำลองสิ่งมีชีวิต 2 มิติ ที่ AI ต้องหากินเพื่ออยู่รอด",
 "กฎเหล็ก: ไม่มีป้ายบอกว่าอะไรมีค่า/มีพิษ",
 "AI เรียนเองจาก \"พลังงานสุทธิที่ได้รับจริง\"",
 "ผ่านการทดสอบอัตโนมัติ 93/93 และรันซ้ำได้ผลเดิม",
],MX,1.9,5.1,3.6,16);
s.addNotes("ผมสร้างโลกจำลองสิ่งมีชีวิต 2 มิติ ที่ตัวละคร AI ต้องหากินเพื่ออยู่รอด กฎเหล็กคือไม่มีป้ายบอกอะไรเลย โลกไม่บอกว่าอะไรมีค่าหรือมีพิษ AI ต้องเรียนเองจากพลังงานสุทธิที่ได้รับจริง กินคำหนึ่งได้พลังงานเท่าไรก็จดจำค่าไว้ ครั้งต่อไปถึงตัดสินใจว่าจะกินหรือข้าม ระบบนี้ผ่านการทดสอบ 93 จาก 93 รายการ และรันซ้ำได้ค่าเดิม");

// ---------- Slide 4: Act 1 food ----------
s=p.addSlide(); heading(s,3,"องก์ 1 (รากฐาน): AI เรียนเลือกอาหารคุ้มค่าได้เอง");
img(s,"fig_multiseed_seed_consumption_CI",MX,1.7,6.1,3.8);
stat(s,7.0,1.72,1.8,"4.6×","กินค่าต่ำน้อยลง",GREEN,TINT,30);
stat(s,8.95,1.72,1.8,"p<.001","ต่างกันจริง (10 ซีด)",GREEN,TINT,28);
stat(s,10.9,1.72,1.8,"0/12","เมินโดยไม่เคยชิม",RED,REDTINT,30);
s.addShape(p.ShapeType.roundRect,{x:7.0,y:3.75,w:5.7,h:1.95,fill:{color:GOLDTINT},line:{type:"none"},rectRadius:0.1,shadow:shadow()});
s.addText([{text:"หลักฐานเชิงสาเหตุ: ",options:{bold:true,color:AMBER}},
  {text:"ไม่มีเอเจนต์สักตัวที่เมินอาหารค่าต่ำโดยไม่เคยชิมอาหารที่ดีกว่าก่อน → พฤติกรรมมาจากประสบการณ์ตรง ไม่ใช่กฎที่เขียนใส่",options:{color:INK}}],
  {x:7.25,y:3.9,w:5.2,h:1.65,valign:"middle",align:"left",fontFace:F,fontSize:14.5,margin:0});
s.addNotes("ก่อนอื่นต้องพิสูจน์ว่ากลไกเรียนเองทำงานจริง ผมให้ AI อยู่ในโลกที่มีอาหาร 2 แบบ ค่าต่างกัน 5 เท่า โดยไม่บอกว่าอันไหนดีกว่า ผลคือกลุ่มที่เปิดการเรียนรู้กินอาหารค่าต่ำน้อยกว่า 4.6 เท่าเทียบกลุ่มที่ปิด ทดสอบ 10 รอบ ได้ p เท่ากับ 0.0002 และแยกขาดสมบูรณ์ และหลักฐานที่ผมภูมิใจที่สุด จากเอเจนต์ 12 ตัว ไม่มีสักตัวเดียวที่เมินอาหารค่าต่ำโดยไม่เคยชิมของที่ดีกว่าก่อน แปลว่าการเปลี่ยนพฤติกรรมมาจากประสบการณ์ตรงของแต่ละตัว ไม่ใช่กฎที่ผมเขียนใส่");

// ---------- Slide 5: Act 1 constant toxin ----------
s=p.addSlide(); heading(s,4,"องก์ 1 (ต่อ): เลี่ยง \"พิษคงที่\" ได้เอง");
img(s,"toxin_fig3_learning_curve",MX,1.7,7.2,4.4);
bullets(s,[
 "ใส่อาหารที่มีพิษคงที่",
 "AI เริ่มจากลองชิม พอรู้ว่าไม่คุ้ม → เลี่ยงเองตลอด",
 "ความน่าจะเป็นที่เลือกกิน ~100% → ใกล้ 0% ในไม่กี่รอบ",
 "ไม่ได้เขียนกฎให้เลี่ยง — เรียนจากผลจริงล้วน ๆ",
],8.2,1.9,4.5,3.6,16);
s.addNotes("ทีนี้ใส่อาหารที่มีพิษคงที่ AI เริ่มจากลองชิม พอรู้ว่าไม่คุ้มก็เลี่ยงเองตลอด ความน่าจะเป็นที่เลือกกินลดจากเกือบ 100% เหลือใกล้ศูนย์ภายในไม่กี่รอบ โดยที่ผมไม่ได้เขียนกฎให้เลี่ยงเลย มันเรียนจากผลจริงล้วน ๆ สรุปว่ากลไกเรียนรู้ของเราทำงานถูกต้องทั้งเรื่องคุณค่าอาหารและพิษคงที่ นี่คือรากฐาน");

// ---------- Slide 6: Act 2 lure (wow) ----------
s=p.addSlide(); heading(s,5,"องก์ 2 (หมัดเด็ด): \"พิษที่หายได้\" หลอกให้กินพิษมากขึ้น");
img(s,"toxin_multiseed_ci",MX,1.55,8.2,3.35);
stat(s,8.95,1.7,1.85,"63%","ถูกหลอกที่พิษ 30%",RED,REDTINT,32);
stat(s,10.95,1.7,1.75,"99%","กับกฎ softmax",RED,REDTINT,32);
s.addShape(p.ShapeType.roundRect,{x:MX,y:5.15,w:12.1,h:1.75,fill:{color:REDTINT},line:{type:"none"},rectRadius:0.1,shadow:shadow()});
s.addText([{text:"อาหารสด = พิษ / เก็บไว้ = ปลอดภัย  →  AI มองไม่เห็น \"อายุ\" เรียนได้แค่ค่าเฉลี่ยที่สูงกว่าอาหารปลอดภัย  →  ",options:{color:INK}},
  {text:"พลิกจากการ \"เลี่ยง\" เป็นการ \"ไล่ล่า\"",options:{bold:true,color:RED}},
  {text:" (กินพิษจริงราว 30% ของมื้อ)",options:{color:INK}}],
  {x:MX+0.25,y:5.35,w:11.6,h:1.35,valign:"middle",align:"left",fontFace:F,fontSize:17,margin:0});
s.addNotes("แล้วนี่คือสิ่งที่ไม่คาดคิด ผมทำให้พิษเหมือนจริงขึ้น คืออาหารสดมีพิษ แต่เก็บไว้แล้วหายพิษและให้พลังงานสูง ปัญหาคือ AI มองไม่ออกว่าชิ้นไหนสดชิ้นไหนเก่า เห็นแค่ว่าเป็นผลไม้ มันเลยเรียนได้แค่ค่าเฉลี่ยของสองสภาพ ซึ่งดันสูงกว่าอาหารปลอดภัย ผลคือ AI จัดผลไม้พิษเป็นอาหารดีที่สุดแล้วมุ่งเข้าหา แม้พิษจะโผล่ถึง 30% ของครั้ง ก็ยังมี AI ถึง 63% ที่ถูกหลอก และกินพิษจริงราว 30% ของมื้อ พูดง่าย ๆ คือการที่พิษหายได้กลับด้านจากการเลี่ยงเป็นการไล่ล่า ความปลอดภัยแบบมีบางช่วงอันตรายกว่าพิษที่คงที่เสียอีก");

// ---------- Slide 7: generality + window ----------
s=p.addSlide(); heading(s,6,"ไม่ใช่ฟลุก และ AI เล็งช่วงปลอดภัยไม่ได้");
img(s,"toxin_learner_comparison",MX,1.7,6.7,4.3);
stat(s,7.6,1.7,2.4,"×4","กฎการเรียนรู้มาตรฐานที่ทดสอบ — ถูกหลอกทุกแบบ",GREEN,TINT);
stat(s,10.25,1.7,2.45,"0%","แยก \"ช่วงปลอดภัย\" ของพิษไม่โมโนโทนิกไม่ได้เลย",RED,REDTINT);
img(s,"toxin_window_sim_result",7.6,3.55,5.1,2.05);
s.addNotes("เพื่อพิสูจน์ว่าไม่ใช่ข้อบกพร่องเฉพาะระบบผม ผมทดสอบซ้ำด้วยกฎการเรียนรู้มาตรฐาน 4 แบบ เกิด lure กับทุกแบบ และยิ่งกฎฉลาดสำรวจเก่ง ยิ่งถูกหลอกหนักขึ้น softmax ถูกหลอกสูงถึง 99% และเมื่อผมทำพิษให้ซับซ้อนขึ้น มีช่วงปลอดภัยตรงกลาง AI เล็งช่วงปลอดภัยนั้นไม่ได้เลย ความสามารถแยกเท่ากับ 0 เพราะกฎง่าย ๆ ว่าเก่ากว่าปลอดภัยกว่าใช้ไม่ได้อีกต่อไป");

// ---------- Slide 8: why it matters ----------
s=p.addSlide(); heading(s,7,"ทำไมสำคัญ: หลักการความปลอดภัย AI");
s.addShape(p.ShapeType.roundRect,{x:MX,y:1.65,w:12.1,h:1.5,fill:{color:GREEN},line:{type:"none"},rectRadius:0.1,shadow:shadow()});
s.addText([{text:"AI ที่ตัดสินจาก \"ชนิด\" ของสิ่งของ จะพลาดเมื่ออันตรายขึ้นกับ \"สภาพ\" (อายุ/เวลา) ที่มองไม่เห็น",options:{bold:true,color:WHITE}}],
  {x:MX+0.3,y:1.75,w:11.5,h:1.3,valign:"middle",align:"left",fontFace:F,fontSize:20,margin:0});
const cards=[["เห็ดพิษ / อาหารหมักดอง","ระบบเตือนภัยที่เรียนแบบ \"ค่าเฉลี่ย\" อาจตัดสินผิดด้วยกลไก lure เดียวกัน"],
  ["หุ่นยนต์กู้ภัย/สำรวจ","ต้องตัดสินความปลอดภัยเองในที่ที่อันตรายโผล่เป็นช่วง ๆ"],
  ["บทเรียนออกแบบ AI","ต้องให้ AI รับรู้ \"สภาพ/อายุ\" ไม่ใช่แค่ \"ชนิด\""]];
cards.forEach((c,i)=>{
  const x=MX+i*4.05;
  s.addShape(p.ShapeType.roundRect,{x,y:3.5,w:3.8,h:3.1,fill:{color:TINT},line:{type:"none"},rectRadius:0.1,shadow:shadow()});
  s.addShape(p.ShapeType.ellipse,{x:x+0.3,y:3.8,w:0.7,h:0.7,fill:{color:GREEN},line:{type:"none"}});
  s.addText(String(i+1),{x:x+0.3,y:3.8,w:0.7,h:0.7,align:"center",valign:"middle",fontFace:F,fontSize:20,bold:true,color:WHITE,margin:0});
  s.addText([{text:c[0],options:{fontSize:16,bold:true,color:INK,breakLine:true,paraSpaceAfter:8}},{text:c[1],options:{fontSize:14,color:MUTED}}],
    {x:x+0.3,y:4.7,w:3.2,h:1.7,valign:"top",align:"left",fontFace:F,margin:0});
});
s.addNotes("ข้อค้นพบนี้ให้หลักการความปลอดภัย AI ที่ใช้ได้กว้าง AI ที่ตัดสินจากชนิดของสิ่งของจะพลาดเมื่ออันตรายขึ้นกับสภาพอย่างอายุหรือเวลาที่มันมองไม่เห็น และอันตรายที่โผล่เป็นบางช่วงมักถูกประเมินต่ำและอันตรายกว่าอันตรายที่คงที่ เพราะมันดึงค่าเฉลี่ยให้ดูดีแล้วล่อเข้าไป เรื่องนี้สำคัญกับ AI คัดกรองความปลอดภัยของอาหารหรือสิ่งแวดล้อม เช่น ระบบเตือนเห็ดพิษ อาหารหมักดองที่ปลอดภัยเป็นช่วงเวลา หรือหุ่นยนต์ที่ทำงานในที่ที่อันตรายเปลี่ยนไปเรื่อย ๆ");

// ---------- Slide 9: honesty ----------
s=p.addSlide(); heading(s,8,"ความซื่อสัตย์: อ้างได้ vs ยังไม่ควรอ้าง");
s.addShape(p.ShapeType.roundRect,{x:MX,y:1.7,w:6.0,h:4.6,fill:{color:TINT},line:{type:"none"},rectRadius:0.1,shadow:shadow()});
s.addText("✓ อ้างได้ (พิสูจน์แล้ว)",{x:MX+0.3,y:1.9,w:5.4,h:0.5,fontFace:F,fontSize:18,bold:true,color:GREEN,align:"left",margin:0});
bullets(s,[
 "AI เรียนเลือกอาหารคุ้มค่า/เลี่ยงพิษคงที่ได้เอง (หลายซีด + control)",
 "การเรียนต่อชนิดถูกล่อโดยพิษที่หายได้ — ทั่วไปข้ามกฎ 4 แบบ",
 "แยกช่วงปลอดภัย = 0 เป็นผลเชิงโครงสร้าง (ไม่ขึ้นกับกฎ)",
],MX+0.3,2.5,5.4,3.6,15);
s.addShape(p.ShapeType.roundRect,{x:6.9,y:1.7,w:5.8,h:4.6,fill:{color:REDTINT},line:{type:"none"},rectRadius:0.1,shadow:shadow()});
s.addText("✕ ยังไม่ควรอ้าง",{x:7.2,y:1.9,w:5.2,h:0.5,fontFace:F,fontSize:18,bold:true,color:RED,align:"left",margin:0});
bullets(s,[
 "AI \"เข้าใจ\" หรือมีเจตนา/รู้คิด",
 "AI วางแผน/ตั้งใจกินพิษ หรือแปรรูปอาหารได้แล้ว",
 "ต้นทุนการอยู่รอดจริง — ผลนี้วัดจาก \"ค่าที่รับรู้\" ในสภาพควบคุม ยังไม่วัดการตายจริง",
],7.2,2.5,5.2,3.6,15);
s.addNotes("ผมขอพูดตรง ๆ ว่าอะไรพิสูจน์แล้วและอะไรยังไม่ ที่พิสูจน์แล้วคือ AI เรียนเลือกอาหารและเลี่ยงพิษคงที่ได้เอง และการเรียนแบบต่อชนิดถูกหลอกด้วยพิษที่หายได้จริง ส่วนที่ยังไม่อ้างคือ ผมไม่ได้บอกว่า AI เข้าใจหรือมีเจตนา และผลนี้วัดจากค่าที่ AI รับรู้ในสภาพควบคุม ยังไม่ได้วัดการตายจริงในประชากรที่แข่งขัน ความซื่อตรงตรงนี้คือจุดแข็งของงาน");

// ---------- Slide 10: conclusion (dark) ----------
s=p.addSlide(); s.background={color:DARK};
s.addText("สรุป",{x:MX,y:0.7,w:6,h:0.8,fontFace:F,fontSize:30,bold:true,color:AMBER,align:"left",margin:0});
s.addText([
 {text:"ปัญญาประดิษฐ์เรียนรู้เองได้จริงโดยไม่ต้องมีป้าย ",options:{color:WHITE,breakLine:true,paraSpaceAfter:10}},
 {text:"แต่เมื่ออันตรายเปลี่ยนตามเวลา มันถูกหลอกให้ไล่ล่าอันตรายได้ (สูงถึง 99%)",options:{color:"FBE3E0",breakLine:true,paraSpaceAfter:10}},
 {text:"ทางแก้: ให้ AI รับรู้ \"สัญญาณบอกสภาพ\" (เช่น ความสด) ไม่ใช่ปักป้ายทุกอย่าง",options:{color:"CFE3DA"}},
],{x:MX,y:1.7,w:12.1,h:2.6,fontFace:F,fontSize:22,bold:true,align:"left",valign:"top",margin:0});
s.addShape(p.ShapeType.roundRect,{x:MX,y:4.5,w:12.1,h:1.3,fill:{color:"1E4A40"},line:{type:"none"},rectRadius:0.1});
s.addText([{text:"งานต่อไป: ",options:{bold:true,color:AMBER}},{text:"ทดสอบว่า AI จะเรียนที่จะ \"เก็บอาหารไว้ให้หายพิษก่อนกิน\" ได้เองไหม (store-to-detoxify)",options:{color:WHITE}}],
  {x:MX+0.3,y:4.6,w:11.5,h:1.1,valign:"middle",align:"left",fontFace:F,fontSize:17,margin:0});
s.addText("ขอบคุณครับ — นายชิษณุพงศ์ อินทร์จันทร์ · โรงเรียนดีบุกพังงาวิทยายน",
  {x:MX,y:6.4,w:12.1,h:0.6,fontFace:F,fontSize:16,color:"AFC6BD",align:"left",margin:0});
s.addNotes("สรุปคือ ปัญญาประดิษฐ์เรียนรู้เองได้จริงโดยไม่ต้องมีป้าย แต่เมื่ออันตรายเปลี่ยนตามเวลา มันถูกหลอกให้ไล่ล่าอันตรายได้ ทางแก้ไม่ใช่กลับไปปักป้ายทุกอย่าง แต่คือให้ AI รับรู้สัญญาณบอกสภาพ เช่น ความสด งานต่อไปของผมคือทดสอบว่า AI จะเรียนรู้ที่จะเก็บอาหารไว้ให้หายพิษก่อนกินได้เองไหม ขอบคุณครับ");

p.writeFile({fileName:OUT}).then(f=>console.log("wrote",f));

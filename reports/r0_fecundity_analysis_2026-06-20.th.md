# รายงาน: วิเคราะห์ R₀ เชิงโครงสร้าง — fecundity อยู่ที่ระดับทดแทนแล้ว, ปัญหาคือพลวัตไม่เสถียร

ผู้วิจัย: Chisanupong · โครงการ Artificial Evolution (TURC2026) · วันที่: 2026-06-20
commit: `2f3308e` (per-female fecundity telemetry)
สถานะ: วิเคราะห์เสร็จ — **พลิกความเข้าใจของปัญหา**

## บทคัดย่อ
หลังพบ R₀ < 1 ดื้อ (ทุกการจูนสูญพันธุ์) เราเพิ่ม telemetry วัด **ผลผลิตการสืบพันธุ์ต่อ female ตลอดชีวิต** (children_count ตอนตาย แยกตามรุ่น) ผลพลิกความเข้าใจ: **fecundity ≈ 2.0 ลูก/female (= ระดับทดแทนพอดี) ไม่ใช่ปัญหา** — สิ่งที่ทำให้สูญพันธุ์คือ **พลวัตประชากรไม่เสถียร** (boom→crash→Allee→decay)

## ผล (สูตรดีสุด: food×1 + drain0.03 + dense + starvation + stochastic-mort + home-fidelity + continuous, mortal 18000t)
- **MEAN children/dead-adult-female = 1.838** (ต้องการ ~2.0)
- แยกรุ่น: gen0=2.08, gen1=2.0, gen2=2.08, gen3=2.0, **gen4=0.0**
- count/รุ่น: 25 → 33 → 26 → **5** → 10  (โต→crash→ฟื้นบางส่วน)

## การตีความ
- female ที่อยู่ครบชีวิต **มีลูก ~2.0 = ทดแทนพอดี** → **fecundity ไม่ใช่คอขวด**
- overall ตก 1.838 เพราะ gen4 = 0 (10 female โตแต่ไม่ทันสืบพันธุ์ = **Allee ที่หางการล่ม**)
- count รุ่น oscillate (25→33→26→5→10) = boom → overshoot → **crash (g2→g3)** → ฟื้นบางส่วน → decay → สูญพันธุ์
- กลไก: **delayed density-dependence** (ลูกที่เกิดไปแย่งทรัพยากรทีหลัง + อดตายช้า) → oscillation แบบ delayed-logistic ที่ decay ลง ไม่ converge สู่ K

## นัยที่พลิกแนวทาง
การจูน fecundity/อัตราสืบพันธุ์ทั้งหมดที่ผ่านมา (~33 รัน) **โฟกัสผิดจุด** — fecundity ดีอยู่แล้ว ของจริงคือ **เสถียรภาพพลวัต**:
1. **เบรก density ให้เร็ว/แรงขึ้นก่อน overshoot** — ปัจจุบันเบรก (hunger/starvation) เด้งช้าหลังเกิน K แล้ว → crash; ต้องเบรกการสืบพันธุ์แบบ proportional กับ food-per-capita ที่ลดลง *ก่อน* จะ overshoot
2. **ลด lag** — maturation 61 ticks + อดตายช้า = ความหน่วงที่สร้าง oscillation; ลดความหน่วงช่วยให้ converge
3. แก้ Allee ที่หาง — เมื่อไม่ crash ก็ไม่เข้าโซน Allee

## งานต่อไป
- ใส่ **density-dependent reproduction brake ที่อิง food-per-capita/hunger แบบ proportional** (ไม่ใช่ all-or-nothing) เพื่อ damp oscillation → ทดสอบว่าประชากร converge สู่ K เสถียร
- (เครื่องมือพร้อม: fecundity + funnel + population trajectory telemetry, grid เร็ว)

## การทำซ้ำ
```bash
python scripts/food_value_study_driver.py --model v2 --ticks 18000 --mortal --body 14 \
  --scaffolded --home-fidelity --continuous-repro --continuous-repro-rate 0.35 \
  --starvation-death --stochastic-mortality --mortality-hazard 0.04 --drain-mult 0.03 \
  --max-pop 5000 --food-energy-mult 1 --low-value-food 45 --repro-litter-min 2 --repro-max-age 300
# อ่าน female_fecundity ใน dump
```

## หลักฐาน
- **Supporting:** fecundity 2.0/female (gen0-3) = replacement; count รุ่น oscillate→decay
- **Against/Alternative:** funnel ของ continuous mode ไม่น่าเชื่อถือ (reproduction_debug stale) — ใช้ fecundity เป็นหลัก
- **Confidence:** fecundity ไม่ใช่คอขวด = สูง · ปัญหาเป็น dynamical instability (delayed density-dependence) = สูง

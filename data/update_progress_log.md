# Update Progress Log

เอกสารนี้สรุปว่าแต่ละอัปเดตดันระบบไปข้างหน้าหรือถอยหลังใน metric สำคัญอะไรบ้าง

ข้อควรระวัง: เทียบผลแบบตรงไปตรงมาได้เฉพาะภายใน track เดียวกัน

**Track ที่ใช้ในเอกสารนี้**
- `founder_250_body14_stability`: ชุดอัปเดตหลักที่ค่อยๆ ปรับ economy/reproduction/household allocation
- `founder_250_body14_regressions`: อัปเดตที่แก้ปัญหาเฉพาะจุดแต่ทำให้ระบบถอยหลังแรง
- `long_loop_body14_non_extinction`: ชุดทดสอบระยะยาวเพื่อดูว่าสังคมอยู่ต่อเนื่องได้ไหม
- `current_branch_body8_exploratory`: benchmark ล่าสุดของ branch ปัจจุบันที่ยัง exploratory

| Track | Update | Change | Final Tick | Births | Matured | Max Gen | Non-Extinct Runs | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `founder_250_body14_stability` | `S0` | Baseline before bugfix balance | 594.9 | 187.6 | 108.5 | 6.6 | 6 | ใช้เป็น baseline หลักของชุด founder 250 ก่อนการแก้ economy bug และ redesign |
| `founder_250_body14_stability` | `S1` | Direct projected-energy storage fix | 525.2 | 161.9 | 86.6 | 4.2 | 2 | แก้บั๊กตรงๆ แล้วผล aggregate แย่ลง แสดงว่าบั๊กเดิมบัง imbalance เชิง economy อยู่ |
| `founder_250_body14_stability` | `S2` | Household economy redesign | 589.7 | 185.4 | 106.4 | 5.8 | 5 | เปลี่ยนจากแก้บั๊กตรงๆ ไปสู่ redesign เพื่อกัน personal energy floor ก่อนเก็บ household surplus |
| `founder_250_body14_stability` | `S3` | Adult withdrawal alignment | 516.3 | 164.6 | 116.2 | 5.1 | 5 | ทำให้ผู้ใหญ่ดึงอาหารจาก household ได้สอดคล้องขึ้น แม้ final tick ลด แต่ matured children เพิ่มขึ้น |
| `founder_250_body14_stability` | `S4` | Breeder-priority household allocation | 649.6 | 205.5 | 145.0 | 7.5 | 8 | เป็น intervention ที่ดีที่สุดใน stability track ชุด founder 250 ปัจจุบัน |
| `founder_250_body14_stability` | `S5` | Storage accounting before/after check | 525.2 | 161.9 | 86.6 | 4.2 | 2 | ไฟล์นี้เป็น before/after คนละ implementation branch ใช้ดูผลจาก storage accounting fix โดยตรง |
| `founder_250_body14_regressions` | `R1` | Anti-cohort patch regression | 369.4 | 23.9 | 23.2 | 2.5 | 0 | ลด cohort boom ได้ แต่กดระบบลงหนักจน extinction 10/10 และ peak population หดแรง |
| `founder_250_body14_regressions` | `R2` | Settlement overshoot fix regression | 120.2 | 125.0 | 1.4 | 1.0 | 0 | หยุด overshoot ได้จริง แต่ฆ่า reproduction pipeline แทบหมด เหลือ matured children ใกล้ศูนย์ |
| `long_loop_body14_non_extinction` | `L1` | Long loop baseline | 1272.9 | 325.1 | 266.5 | 12.4 | 0 | แม้ไปได้ลึกถึง gen 25 ในบาง seed แต่สุดท้ายสูญพันธุ์ทุก run |
| `long_loop_body14_non_extinction` | `L2` | Active-nest-only support filtering | 1001.3 | 252.6 | 196.0 | 0.0 | 0 | ลด surplus หลอกบางส่วน แต่ยังไม่แก้ non-extinction และ depth โดยรวมลดลง |
| `current_branch_body8_exploratory` | `C1` | Current branch exploratory benchmark | 154.0 | 6.5 | 1.0 | - | 0 | สะท้อนสถานะล่าสุดของ exploratory branch หลังปรับ reproduction/settlement/hearth/patches แล้ว แต่ยังไม่ข้าม non-extinction |
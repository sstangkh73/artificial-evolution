"""รัน pilot ส่วน S1 ครบ 16 เซลล์ตาม 03_pilot_protocol.md ข้อ 4

แต่ละเซลล์คือคำสั่ง runner หนึ่งคำสั่งตาม protocol รันหลายเซลล์พร้อมกัน (ไม่เปลี่ยนผล
เพราะแต่ละรันกำหนดด้วย seed) รันซ้ำได้: โฟลเดอร์ที่มี protocol.json แล้วจะใช้ --resume
เติมเฉพาะรันที่ขาด ผลแต่ละเซลล์ (บรรทัดท้าย) ต่อท้ายใน ysc-loop/.loop/pilot_s1.log
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "ysc-loop" / ".loop" / "pilot_s1.log"
WORKERS = 8
_lock = Lock()


def run_cell(ticks, q, eps):
    out = f"data/tool_discovery_pilot_s1_e{round(eps * 100):03d}_q{q}_t{ticks}"
    cmd = [sys.executable, "scripts/run_tool_discovery.py", "--out", out,
           "--conditions", "C0", "C1", "C2", "C3", "C4", "--seeds", "1000-1049",
           "--ticks", str(ticks), "--set", "immortal=true",
           "--set", f"epsilon={eps}", "--set", f"q_init={q}"]
    if (ROOT / out / "protocol.json").exists():
        cmd.append("--resume")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-2:])
    with _lock, LOG.open("a", encoding="utf-8") as f:
        f.write(f"== {out} rc={r.returncode}\n{tail}\n")
    return r.returncode


cells = [(t, q, e) for t in (1600, 800) for q in (0, 10) for e in (0.05, 0.10, 0.20, 0.30)]
with ThreadPoolExecutor(WORKERS) as pool:
    failed = sum(rc != 0 for rc in pool.map(lambda c: run_cell(*c), cells))
with LOG.open("a", encoding="utf-8") as f:
    f.write(f"ALL DONE failed_cells={failed}\n")
sys.exit(1 if failed else 0)

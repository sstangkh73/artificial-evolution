#!/usr/bin/env bash
# ส่งงานให้ Codex ทำแบบไม่ถามกลับ แล้วพิมพ์ข้อความสรุปสุดท้ายของ Codex
# ใช้: bash tools/codex.sh "คำสั่งงานแบบละเอียด"
set -u

if [ $# -lt 1 ] || [ -z "$1" ]; then
  echo "usage: bash physics-loop/tools/codex.sh \"task\"" >&2
  exit 2
fi

dir="physics-loop/.loop/codex"; mkdir -p "$dir"
ts=$(date +%Y%m%d-%H%M%S)
log="$dir/$ts.log"
last="$dir/$ts.last.md"

codex exec --sandbox "${CODEX_SANDBOX:-workspace-write}" --skip-git-repo-check --output-last-message "$last" "$1" </dev/null >"$log" 2>&1
code=$?

# Log Codex token use so physics-loop/tools/budget.py can pick the lead.
tokens=$(python -c "import re,sys; t=open(sys.argv[1],encoding='utf-8',errors='ignore').read(); m=re.findall(r'tokens used[:\s]*([\d,]+)', t, re.I); print(m[-1].replace(',','') if m else 0)" "$log")
python physics-loop/tools/budget.py add codex "$tokens"

echo "[codex exit=$code | full log: $log]"
if [ -s "$last" ]; then
  cat "$last"
else
  tail -n 80 "$log"
fi
exit $code

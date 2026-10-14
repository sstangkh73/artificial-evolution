# ตัวตัดสินว่างาน YSC เฟส 3 "เสร็จแล้ว": exit 0 = ผ่าน, อย่างอื่น = ยังไม่ผ่าน
# AI ห้ามแก้ไฟล์นี้และ tools/verify_phase3.py (ถ้าถูกแก้ ลูปจะหยุด)
$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location (Split-Path $PSScriptRoot -Parent)
python ysc-loop/tools/verify_phase3.py
exit $LASTEXITCODE

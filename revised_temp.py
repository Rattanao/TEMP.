"""Revised temp: ตัดตัวเลขหลักสุดท้ายของอุณหภูมิตู้เย็นในไฟล์ CLIST ออก 1 หลัก

ตัวอย่าง: S-20C -> S-2C, S-180C -> S-18C, S50C -> S5C
ค่าหลักเดียว (S0C) และช่องที่มีแค่ S ไม่แก้ไข
เติมช่องว่างแทนตัวอักษรที่หายไป ความยาวบรรทัดจึงเท่าเดิม

ใช้งาน:
    python revised_temp.py <ไฟล์ CLIST.txt> [ไฟล์ผลลัพธ์]
ไฟล์ผลลัพธ์ตั้งต้นคือ "Revised temp.txt" ในโฟลเดอร์เดียวกับไฟล์ต้นฉบับ
"""
import re
import sys
from pathlib import Path

COL = 144  # ตำแหน่งเริ่มของช่องอุณหภูมิ (ตัวอักษรที่ 145, นับจาก 0)
TEMP_RE = re.compile(rb"S(-?)(\d*)C?")


def revise(data: bytes):
    changed, skipped, out = [], [], []
    for no, raw in enumerate(data.split(b"\n"), 1):
        cr = raw.endswith(b"\r")
        line = raw[:-1] if cr else raw
        if len(line) <= COL or line[COL:COL + 1] != b"S":
            out.append(raw)
            continue
        m = TEMP_RE.match(line, COL)
        cntr = line[:11].decode("ascii", "replace").strip()
        digits = m.group(2)
        if len(digits) < 2:
            skipped.append((no, cntr, m.group(0).decode()))
            out.append(raw)
            continue
        new = b"S" + m.group(1) + digits[:-1] + b"C"
        line = line[:COL] + new + b" " + line[m.end():]
        changed.append((no, cntr, m.group(0).decode(), new.decode()))
        out.append(line + b"\r" if cr else line)
    return b"\n".join(out), changed, skipped


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name("Revised temp.txt")
    result, changed, skipped = revise(src.read_bytes())
    dst.write_bytes(result)
    for no, cntr, old, new in changed:
        print(f"บรรทัด {no:>3}  {cntr:<11}  {old:<7} -> {new}")
    print(f"\nแก้ไข {len(changed)} บรรทัด, ไม่แก้ไข {len(skipped)} บรรทัด")
    print(f"บันทึกเป็น {dst}")


if __name__ == "__main__":
    main()

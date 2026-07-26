import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent.resolve()
p = HERE / "dictsource" / "hy_extra"
if not p.exists():
    sys.exit(f"{p} not found")

raw = p.read_bytes()
print(f"file: {p}")
print(f"size: {len(raw)} bytes")

if raw.startswith(b"\xef\xbb\xbf"):
    print("\n  !! FILE HAS A BOM - the first entry will be ignored.")
    print("     In VS Code: click 'UTF-8 with BOM' in the status bar,")
    print("     choose 'Save with Encoding' -> 'UTF-8'.")
else:
    print("encoding: UTF-8, no BOM  (good)")

text = raw.decode("utf-8-sig")
entries = []
for i, line in enumerate(text.split("\n"), 1):
    if not line.strip() or line.strip().startswith("//"):
        continue
    parts = line.split(None, 1)
    if len(parts) < 2:
        print(f"\n  !! line {i}: no pronunciation found -> {line!r}")
        continue
    entries.append((i, parts[0], parts[1].strip()))

print(f"\n{len(entries)} entries:\n")

dupes = {w for w, n in Counter(w for _, w, _ in entries).items() if n > 1}


def find_espeak():
    f = shutil.which("espeak-ng")
    if f:
        return f
    for g in [r"C:\Program Files\eSpeak NG\espeak-ng.exe",
              r"C:\Program Files (x86)\eSpeak NG\espeak-ng.exe"]:
        if Path(g).exists():
            return g
    sys.exit("espeak-ng not found")


ESPEAK = find_espeak()
LOCAL = ["--path", str(HERE)] if (HERE / "espeak-ng-data").is_dir() else []
tmp = HERE / "_chk.txt"

for ln, word, phon in entries:
    tmp.write_text(word, encoding="utf-8")
    r = subprocess.run([ESPEAK] + LOCAL + ["-v", "hyw", "-q", "--ipa", "-f", str(tmp)],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    got = (r.stdout or "").strip().replace("\n", " ")
    mark = "  DUPLICATE" if word in dupes else ""
    print(f"  line {ln:3d}  {word:<14} {phon:<12} -> {got}{mark}")

tmp.unlink(missing_ok=True)

if dupes:
    print(f"\n  !! duplicates: {', '.join(dupes)}")
    print("     The LAST one wins. Delete the older lines.")
print("\nIf a line looks right but the output is wrong, run build_dict.py.")
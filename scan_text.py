import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Usage: python scan_text.py yourfile.txt")

infile = Path(sys.argv[1])
if not infile.exists():
    sys.exit(f"No such file: {infile}")


def find_espeak():
    found = shutil.which("espeak-ng")
    if found:
        return found
    for guess in [r"C:\Program Files\eSpeak NG\espeak-ng.exe",
                  r"C:\Program Files (x86)\eSpeak NG\espeak-ng.exe"]:
        if Path(guess).exists():
            return guess
    sys.exit("Could not find espeak-ng.")


ESPEAK = find_espeak()
HERE = Path(__file__).parent.resolve()
LOCAL = ["--path", str(HERE)] if (HERE / "espeak-ng-data").is_dir() else []
print("reading:", "your patched copy" if LOCAL else "system espeak")

text = infile.read_text(encoding="utf-8")

words = re.findall(r"[\u0531-\u0556\u0561-\u0587\u055A]+", text)
counts = Counter(words)
print(f"{len(words)} words, {len(counts)} unique\n")

tmp = HERE / "_scan.txt"


def ipa(w):
    tmp.write_text(w, encoding="utf-8")
    r = subprocess.run(
        [ESPEAK] + LOCAL + ["-v", "hyw", "-q", "--ipa", "-f", str(tmp)],
        capture_output=True, text=True,
        encoding="utf-8", errors="replace")
    return (r.stdout or "").strip().replace("\n", " ")


def risk(word, phon):
    flags = []
    if word.endswith(("ս", "դ")) and len(word) > 2:
        flags.append("final-s/d")
    if word[0] in "ՅյՈոԵե":
        flags.append("initial")
    if "ոյ" in word or "այ" in word:
        flags.append("diphthong")
    if "dictionary file" in phon or "(en)" in phon:
        flags.append("FELL-BACK-TO-ENGLISH")
    if "ə" in phon:
        flags.append("schwa")
    return ",".join(flags)


rows = []
for w, n in counts.most_common():
    p = ipa(w)
    rows.append((n, w, p, risk(w, p)))

tmp.unlink(missing_ok=True)

out = HERE / "scan_results.txt"
with out.open("w", encoding="utf-8") as f:
    f.write("# Mark wrong ones with X at the start of the line.\n")
    f.write("# count | word | phonemes | flags\n\n")
    for n, w, p, fl in rows:
        f.write(f"{n:4d}  {w:<22} {p:<32} {fl}\n")

for n, w, p, fl in rows[:25]:
    print(f"{n:4d}  {w:<20} {p:<30} {fl}")

print(f"\nFull list ({len(rows)} words) written to {out}")
print("Go through it, mark what sounds wrong, add those to dictsource/hy_extra")
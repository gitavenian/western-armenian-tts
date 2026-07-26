import shutil
import subprocess
import sys
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Usage: python word.py <armenian word> [more words...]")


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
tmp = HERE / "_word.txt"


def run(word, args):
    tmp.write_text(word, encoding="utf-8")
    r = subprocess.run([ESPEAK] + args + ["-f", str(tmp)],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return (r.stdout or "").strip()


print()
for w in sys.argv[1:]:
    source = run(w, ["-v", "hy", "-q", "-X"]).split("\n")[-1].strip()
    west = run(w, LOCAL + ["-v", "hyw", "-q", "--ipa"]).replace("\n", " ")

    print(f"  word         {w}")
    print(f"  sounds like  {west}")
    print(f"  paste this   {w}\t{source}")
    print()

tmp.unlink(missing_ok=True)
print("Only add a line to hy_extra if 'sounds like' is wrong.")
print("Edit the pasted phonemes until it sounds right, then rebuild.")
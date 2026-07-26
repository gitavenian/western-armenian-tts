"""
Set up a local, editable copy of espeak's Armenian dictionary, then compile it.

First run:  copies the espeak engine data into this folder, downloads rule files.
Every run:  recompiles dictsource/ -> espeak-ng-data/hy_dict and shows a few tests.

Your system espeak install is never modified.

    python build_dict.py
"""

import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent.resolve()
DATA = HERE / "espeak-ng-data"
SRC = HERE / "dictsource"

RAW = "https://raw.githubusercontent.com/espeak-ng/espeak-ng/master/dictsource/"

MINIMAL = True   # True = Armenian only (~2 MB). False = all languages (~13 MB).


def find_espeak():
    found = shutil.which("espeak-ng")
    if found:
        return Path(found)
    for guess in [
        r"C:\Program Files\eSpeak NG\espeak-ng.exe",
        r"C:\Program Files (x86)\eSpeak NG\espeak-ng.exe",
        "/usr/bin/espeak-ng",
        "/opt/homebrew/bin/espeak-ng",
    ]:
        if Path(guess).exists():
            return Path(guess)
    sys.exit("Could not find espeak-ng.")


ESPEAK = find_espeak()


def find_system_data():
    """Locate the espeak-ng-data folder that came with the install."""
    for c in [
        ESPEAK.parent / "espeak-ng-data",
        Path(r"C:\Program Files\eSpeak NG\espeak-ng-data"),
        Path("/usr/lib/x86_64-linux-gnu/espeak-ng-data"),
        Path("/usr/share/espeak-ng-data"),
        Path("/opt/homebrew/share/espeak-ng-data"),
    ]:
        if c.is_dir():
            return c
    sys.exit("Could not find espeak-ng-data. Where did espeak install?")


# ---------- one-time setup ----------
if not DATA.is_dir():
    system_data = find_system_data()
    print(f"Copying from {system_data}")

    if MINIMAL:
        DATA.mkdir(parents=True)
        for f in ["phondata", "phonindex", "phontab",
                  "intonations", "phondata-manifest"]:
            src = system_data / f
            if src.exists():
                shutil.copy2(src, DATA / f)
        for d in ["lang", "voices"]:
            src = system_data / d
            if src.is_dir():
                shutil.copytree(src, DATA / d)
        shutil.copy2(system_data / "hy_dict", DATA / "hy_dict")
        print("  copied Armenian only (~2 MB)")
    else:
        shutil.copytree(system_data, DATA)
        print("  copied everything (~13 MB)")
    print()

SRC.mkdir(exist_ok=True)
for name in ("hy_rules", "hy_list"):
    target = SRC / name
    if not target.exists():
        print(f"Downloading {name}...")
        urllib.request.urlretrieve(RAW + name, target)
        print(f"  saved to {target}")


# ---------- compile ----------
print("\nCompiling dictionary...")
result = subprocess.run(
    [str(ESPEAK), "--path", str(HERE), "--compile=hy"],
    cwd=str(SRC), capture_output=True, text=True,
    encoding="utf-8", errors="replace",
)
for stream in (result.stdout, result.stderr):
    if stream and stream.strip():
        print("  " + stream.strip().replace("\n", "\n  "))


# ---------- quick check ----------
tmp = SRC / "_in.txt"


def ipa(text, patched=True):
    tmp.write_text(text, encoding="utf-8")
    args = [str(ESPEAK)]
    if patched:
        args += ["--path", str(HERE)]
    args += ["-v", "hyw", "-q", "--ipa", "-f", str(tmp)]
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return (r.stdout or "").strip().replace("\n", " ")


print(f"\n{'word':<16} {'YOUR COPY':<24} {'SYSTEM (untouched)':<24}")
print("-" * 68)
for w in ["Յակոբ", "Յովհաննէս", "Բարի լոյս", "բոլորս", "է", "Պոլիս"]:
    print(f"{w:<16} {ipa(w, True):<24} {ipa(w, False):<24}")

tmp.unlink(missing_ok=True)
print(f"\nEdit files in: {SRC}")
print("Then run this script again.")
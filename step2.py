"""
Step 2: hear the pronunciation rulebook (espeak-ng).

Run:
    python step2.py

Writes wav files into a folder called "espeak_audio" and prints a
comparison of Western vs Eastern pronunciation for each word.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def find_espeak():
    found = shutil.which("espeak-ng")
    if found:
        return found
    for guess in [
        r"C:\Program Files\eSpeak NG\espeak-ng.exe",
        r"C:\Program Files (x86)\eSpeak NG\espeak-ng.exe",
        "/usr/bin/espeak-ng",
        "/opt/homebrew/bin/espeak-ng",
    ]:
        if Path(guess).exists():
            return guess
    sys.exit("Could not find espeak-ng. Is it installed?")


ESPEAK = find_espeak()
print(f"Using: {ESPEAK}\n")

WORDS = [
    ("Բարի լոյս",       "Pari",       "Bari"),
    ("Գիրք",            "Kirk",       "Girk"),
    ("Պոլիս",           "Bolis",      "Polis"),
    ("Տուն",            "Doon",       "Toon"),
    ("Աւետարան",        "Avedaran",   "Avetaran"),
    ("Շնորհակալութիւն", "sh- start",  "sh- start"),
    ("Յովհաննէս",       "Hovhannes",  "Yovhannes"),
    ("լաւ",             "lav",        "lav"),
    ("բոլորս",          "polorus",    "bolors"),
]

tmp = Path("_espeak_input.txt")
out = Path("espeak_audio")
out.mkdir(exist_ok=True)


def espeak(text, voice, wav_path=None):
    """Write text to a UTF-8 file, then let espeak read the file."""
    tmp.write_text(text, encoding="utf-8")
    args = [ESPEAK, "-v", voice, "-f", str(tmp)]
    if wav_path:
        args += ["-w", str(wav_path)]
    else:
        args += ["-q", "--ipa"]
    result = subprocess.run(args, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    return (result.stdout or "").strip().replace("\n", " ")


print(f"{'word':<20} {'WESTERN (hyw)':<22} {'EASTERN (hy)':<22} expected")
print("-" * 90)

for i, (text, want_west, _) in enumerate(WORDS, start=1):
    west = espeak(text, "hyw")
    east = espeak(text, "hy")

    espeak(text, "hyw", out / f"{i:02d}_west.wav")
    espeak(text, "hy",  out / f"{i:02d}_east.wav")

    print(f"{text:<20} {west:<22} {east:<22} {want_west}")

tmp.unlink(missing_ok=True)

print(f"\nWav files written to: {out.resolve()}")
print("Listen to any pair (01_west.wav vs 01_east.wav) to hear the difference.")
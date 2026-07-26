"""
Western Armenian rulebook test suite.

Run:
    python step3_check.py

Checks what espeak's hyw voice gets right and wrong.
PASS/FAIL are checked automatically. "?" means listen and judge yourself.

To add your own test, append a line to TESTS:
    ("category", "your text", "what it should sound like", must_have, must_not)
    - must_have: IPA substring that MUST appear (or None)
    - must_not:  IPA substring that must NOT appear (or None)
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
    ]:
        if Path(guess).exists():
            return guess
    sys.exit("Could not find espeak-ng.")


ESPEAK = find_espeak()

# use the patched local copy if it exists, otherwise the system one
HERE = Path(__file__).parent.resolve()
LOCAL = ["--path", str(HERE)] if (HERE / "espeak-ng-data").is_dir() else []
print("reading:", "your patched copy" if LOCAL else "system espeak")
print(subprocess.run([ESPEAK, "--version"],
                     capture_output=True, text=True).stdout.strip())
print()

tmp = Path("_in.txt")


def ipa(text):
    tmp.write_text(text, encoding="utf-8")
    r = subprocess.run([ESPEAK] + LOCAL + ["-v", "hyw", "-q", "--ipa", "-f", str(tmp)],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return (r.stdout or "").strip().replace("\n", " ")


TESTS = [
    # --- A. consonant shift: these already work, keep as regression check ---
    ("A shift", "Բարի լոյս",  "Pari louys",   "pʰ",  "baɹ"),
    ("A shift", "Գիրք",       "Kirk",         "kʰ",  "ɡir"),
    ("A shift", "Պոլիս",      "Bolis",        "bol", "pol"),
    ("A shift", "Տուն",       "Doon",         "dun", "tun"),
    ("A shift", "Աւետարան",   "Avedaran",     "ved", "vet"),
    ("A shift", "հինգ",       "hink",         "nkʰ", "nɡ"),

    # --- B. word-initial Յ should be h ---
    ("B initial Y", "Յակոբ",      "Hagop",      "h",  "jaɡ"),
    ("B initial Y", "Յովհաննէս",  "Hovhannes",  "h",  "jov"),
    ("B initial Y", "Յոյս",       "Houys",      "h",  "joj"),
    ("B initial Y", "Յուշ",       "Housh",      "h",  "juʃ"),

    # --- C. possessive schwa: needs ը ---
    ("C poss schwa", "մօրս",     "mo-RUS",        "ə",  None),
    ("C poss schwa", "մայրս",    "may-RUS",       "ə",  None),
    ("C poss schwa", "հայրս",    "hay-RUS",       "ə",  None),
    ("C poss schwa", "բոլորս",   "polo-RUS",      "ə",  None),
    ("C poss schwa", "գիրքս",    "kirk-US",       "ə",  None),
    ("C poss schwa", "մայրդ",    "may-RUD",       "ə",  None),

    # --- D. cluster schwa: already works ---
    ("D cluster schwa", "դգալ",   "tuh-KAL",      "ə",  None),
    ("D cluster schwa", "դպրոց",  "tuh-BROTS",    "ə",  None),
    ("D cluster schwa", "գդակ",   "kuh-TAG",      "ə",  None),

    # --- E. copula forms ---
    ("E copula", "լաւ եմ",     "lav EM",     "em",  "jem"),
    ("E copula", "լաւ ես",     "lav ES",     None,   "jes"),
    ("E copula", "լաւ ենք",    "lav ENK",    "enkʰ", None),
    ("E copula", "լաւ էք",     "lav EK",     None,   None),
    ("E copula", "լաւ են",     "lav EN",     "en",  None),
    ("E copula", "Ես լաւ եմ",  "YES lav em", "jes",  None),

    # --- F. the է bug ---
    ("F copula e", "է",         "e",          None,  "(en)"),
    ("F copula e", "ը",         "uh",         None,  "(en)"),
    ("F copula e", "Ան հոս է",  "an hos e",   None,  "(en)"),
    ("F copula e", "Լաւ օր մըն է", "...mun e", None, "(en)"),

    # --- G. rhotics: ր is a tap, ռ is a trill ---
    ("G rhotics", "րոպէ",   "tap r",    "ɾ",  "ɹ"),
    ("G rhotics", "ռումբ",  "trill r",  "r",  None),
    ("G rhotics", "սիրտ",   "tap r",    "ɾ",  "ɹ"),

    # --- H. numbers, already works ---
    ("H numbers", "2026",      "yergu hazar ksanvets", "haz", None),
    ("H numbers", "5 խնձոր",   "hink khndzor",         None,  None),

    # --- I. particles and digraphs ---
    ("I misc", "կը բարեւեմ",     "gu parevem",   "ɡə",  None),
    ("I misc", "կը խօսիմ",       "gu khosim",    "ɡə",  None),
    ("I misc", "վայրկեան",       "vayrgyan",     "ɡj",  None),
    ("I misc", "երկու վայրկեան", "yergu vayrgyan", None, None),
    ("I misc", "եւ",             "yev",          "jev", None),
    ("I misc", "և",              "yev",          "jev", None),
    ("I misc", "Ոսկի",           "VOSgi",        "vos", None),
]

results = {"PASS": 0, "FAIL": 0, "?": 0}
current = None

for cat, text, want, must_have, must_not in TESTS:
    if cat != current:
        print(f"\n--- {cat} ---")
        current = cat

    got = ipa(text)
    flat = got.replace("ˈ", "").replace("ˌ", "")

    if must_have is None and must_not is None:
        verdict = "?"
    elif must_have and must_have not in flat:
        verdict = "FAIL"
    elif must_not and must_not in flat:
        verdict = "FAIL"
    else:
        verdict = "PASS"

    results[verdict] += 1
    mark = {"PASS": "ok  ", "FAIL": "FAIL", "?": "?   "}[verdict]
    print(f"  {mark} {text:<18} {got:<30} want: {want}")

tmp.unlink(missing_ok=True)

print(f"\n{'=' * 70}")
print(f"  {results['PASS']} pass   {results['FAIL']} fail   {results['?']} manual check")
print(f"{'=' * 70}")
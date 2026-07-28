from pathlib import Path

SRC = Path(__file__).parent.resolve() / "dictsource"
rules = SRC / "hy_rules"

if not rules.exists():
    raise SystemExit(f"{rules} not found. Run build_dict.py first.")

s = rules.read_text(encoding="utf-8")
applied, already = [], []


def fix(name, old, new):
    global s
    if new in s:
        already.append(name)
    elif old in s:
        s = s.replace(old, new)
        applied.append(name)
    else:
        print(f"  !! could not find the text for: {name}")


if "\n?1 " in s:
    lines = s.split("\n")
    s = "\n".join("   " + ln[3:] if ln.startswith("?1 ") else ln for ln in lines)
    applied.append("1. enable ?1 Western rules")
else:
    already.append("1. enable ?1 Western rules")

fix("2. possessive schwa (ս)",
    "     _) ս (B     s@",
    "     _) ս (B     s@\n     C) ս (_     @s\n   L02) ս (_     s")

fix("3. possessive schwa (դ)",
    "     _) դ (B     d@",
    "     _) դ (B     d@\n     C) դ (_     @d\n   L02) դ (_     d")

fix("5. ր tap",
    """.group ր
        ր        r""",
    """.group ր
        ր        *""")
for a, b in [("   L02) ր (L02   r", "   L02) ր (L02   *"),
             ("     _) ր (B     r@", "     _) ր (B     *@"),
             ("     C) ր (_     @r", "     C) ր (_     @*"),
             ("   L02) ր (_     r", "   L02) ր (_     *")]:
    if b not in s and a in s:
        s = s.replace(a, b)

fix("7. կ՚ apostrophe",
    "և  եւ",
    "և  եւ\nկ՚ կ\nկ’ կ\nկ' կ")
# 8. medial cluster schwa: 2 consonants before + 1 after -> insert ը
import re as _re
CONS = {'բ':'b','գ':'g','դ':'d','զ':'z','թ':'t#','ժ':'Z','լ':'l','խ':'X',
        'ծ':'ts','կ':'k','հ':'h','ձ':'dz','ղ':'r"','ճ':'tS','մ':'m','ն':'n',
        'շ':'S','չ':'tS#','պ':'p','ջ':'dZ','ռ':'R','ս':'s','վ':'v','տ':'t',
        'ր':'*','ց':'ts#','փ':'p#','ք':'k#','ֆ':'f'}
if "   CC) " not in s:
    out = []
    for line in s.split("\n"):
        out.append(line)
        m = _re.match(r"^\.group (.)$", line)
        if m and m.group(1) in CONS:
            out.append(f"   CC) {m.group(1)} (C     @{CONS[m.group(1)]}")
    s = "\n".join(out)
    applied.append("8. medial cluster schwa")
else:
    already.append("8. medial cluster schwa")

fix("9. schwa before ու→v at word start",
    "        ու (A    v",
    "        ու (A    v\n    _C) ու (A    @v")
fix("10. -ութիւն suffix",
    "        իւ       y",
    "        իւ       y\n    ութ) իւ      ju")

rules.write_text(s, encoding="utf-8")

for a in applied:
    print(f"  applied  {a}")
for a in already:
    print(f"  already  {a}")
print(f"\n{rules} updated. Now run: python build_dict.py")
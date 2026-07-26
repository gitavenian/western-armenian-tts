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

rules.write_text(s, encoding="utf-8")

for a in applied:
    print(f"  applied  {a}")
for a in already:
    print(f"  already  {a}")
print(f"\n{rules} updated. Now run: python build_dict.py")
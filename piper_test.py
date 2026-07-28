import json
import shutil
import sys
from pathlib import Path
import wave

HERE = Path(__file__).parent.resolve()
MODEL = HERE / "hy_AM-gor-medium.onnx"
CONFIG = HERE / "hy_AM-gor-medium.onnx.json"
DATA = HERE / "espeak-ng-data"

for p in (MODEL, CONFIG):
    if not p.exists():
        sys.exit(f"Missing {p.name}\n"
                 f"Run:  python -m piper.download_voices hy_AM-gor-medium")
if not DATA.is_dir():
    sys.exit("No espeak-ng-data here. Run build_dict.py first.")

cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
current = cfg.get("espeak", {}).get("voice")
if current != "hyw":
    shutil.copy2(CONFIG, CONFIG.with_suffix(".json.orig"))
    cfg.setdefault("espeak", {})["voice"] = "hyw"
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"config: espeak voice {current!r} -> 'hyw'  (backup saved)")
else:
    print("config: espeak voice already 'hyw'")

from piper import PiperVoice

print(f"loading {MODEL.name} ...")
voice = PiperVoice.load(MODEL, config_path=CONFIG, espeak_data_dir=DATA)
print(f"sample rate: {voice.config.sample_rate} Hz\n")

SENTENCES = [
    "Բարի լոյս։",
    "Յակոբ եւ Յովհաննէս մեր ընկերներն էին։",
    "Շնորհակալութիւն որ մտիկ ըրիք։",
    "Այս գիրքս ինծի շատ սիրելի է։",
    "Մայրս կ՚ըսէր թէ լեզուն մեր տունն է։",
    "Ազատութիւն եւ անկախութիւն։",
    "Բոլորս միասին ենք։",
    "Դուրս ելանք առաւօտ կանուխ։",
]

out = HERE / "piper_out"
out.mkdir(exist_ok=True)

for i, text in enumerate(SENTENCES, 1):
    phon = voice.phonemize(text)
    flat = " ".join("".join(s) for s in phon)
    path = out / f"{i:02d}.wav"
    with wave.open(str(path), "wb") as f:
        voice.synthesize_wav(text, f)
    print(f"  {i}. {text}")
    print(f"     {flat}")
    print(f"     -> {path.name}\n")

print(f"Listen in: {out}")
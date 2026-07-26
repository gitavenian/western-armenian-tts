import torch
import scipy.io.wavfile
from pathlib import Path
from transformers import VitsModel, AutoTokenizer

MODEL = "facebook/mms-tts-hyw"          # hyw = Western Armenian

SENTENCES = [
    "Բարի լոյս։",
    "Շնորհակալութիւն։",
    "Ինչպէ՞ս ես։",
    "Գիրք",
    "Պոլիս",
    "Տուն",
    "Աւետարան",
    "Յովհաննէս",
    "Այսօր շատ լաւ օր մըն է։",
    "Բարի լոյս։ Այսօր շատ գեղեցիկ օր մըն է։ Մենք բոլորս այստեղ ենք միասին։",
]

print("Loading model (first run downloads ~150MB)...")
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = VitsModel.from_pretrained(MODEL).eval()

out = Path("audio")
out.mkdir(exist_ok=True)

torch.manual_seed(0)

for i, text in enumerate(SENTENCES, start=1):
    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        audio = model(**inputs).waveform[0].float().numpy()

    path = out / f"{i:02d}.wav"
    scipy.io.wavfile.write(path, model.config.sampling_rate, audio)
    print(f"{i:2d}. {text}  ->  {path}")

print(f"\nDone. Open the '{out}' folder and listen.")
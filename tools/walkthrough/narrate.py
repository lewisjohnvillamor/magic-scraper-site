"""Narration for the walkthrough: one WAV per scene, with Kokoro (82M, Apache-2.0),
run offline through kokoro-onnx. Voice af_heart.

  pip install kokoro-onnx soundfile
  # kokoro-v1.0.onnx + voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx releases
  python3 tools/walkthrough/narrate.py MODEL_DIR OUT_DIR [voice] [speed]

Each line is also transcribed back with Whisper by the build, to catch a word
the voice gets wrong before anyone hears it.
"""
import json, sys, os
import soundfile as sf
from kokoro_onnx import Kokoro
mdir, out = sys.argv[1], sys.argv[2]
voice = sys.argv[3] if len(sys.argv) > 3 else 'af_heart'
speed = float(sys.argv[4]) if len(sys.argv) > 4 else 0.98
lines = json.load(open(os.environ.get('LINES') or os.path.join(os.path.dirname(__file__), 'narration.json')))
k = Kokoro(os.path.join(mdir, 'kokoro-v1.0.onnx'), os.path.join(mdir, 'voices-v1.0.bin'))
os.makedirs(out, exist_ok=True)
for key, text in lines.items():
    audio, sr = k.create(text, voice=voice, speed=speed, lang='en-us')
    sf.write(os.path.join(out, key + '.wav'), audio, sr)
    print(f'{key:9s} {len(audio) / sr:6.2f}s')

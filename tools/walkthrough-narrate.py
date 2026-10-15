"""Narration for the YouTube walkthrough: one WAV per scene from
tools/walkthrough-narration.json, with Piper (offline neural TTS, MIT).

Voice: en_US-joe-medium -- its training data is CC0, so the result is free to use
commercially with no credit owed. (Voices trained on CC BY-NC data, such as
ryan or hfc, are not.) Download the .onnx and .onnx.json from
huggingface.co/rhasspy/piper-voices, then:

  pip install piper-tts
  mkdir -p OUT && cp tools/walkthrough-narration.json OUT/lines.json
  python3 tools/walkthrough-narrate.py en_US-joe-medium.onnx OUT 1.05

Lines are phrased for the ear, not the eye: "a CSV file" rather than a bare
"CSV", "magic scraper dot app" as two words. Each was checked by transcribing
the synthesised audio back with Whisper.
"""
import json, sys, wave, subprocess
from piper import PiperVoice
from piper.config import SynthesisConfig
model, outdir = sys.argv[1], sys.argv[2]
voice = PiperVoice.load(model)
cfg = SynthesisConfig(length_scale=float(sys.argv[3]) if len(sys.argv) > 3 else 1.0, noise_scale=0.6, noise_w_scale=0.8)
lines = json.load(open(outdir + '/lines.json'))
for k, text in lines.items():
    p = f'{outdir}/{k}.wav'
    with wave.open(p, 'wb') as w:
        voice.synthesize_wav(text, w, syn_config=cfg)
    with wave.open(p) as w:
        print(f'{k:6s} {w.getnframes() / w.getframerate():5.2f}s')

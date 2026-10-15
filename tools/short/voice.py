"""Voice for the Short: one WAV per line with Kokoro (Apache-2.0, offline), then
every word timed with faster-whisper so the motion graphics land on the words.

  python3 tools/short/voice.py KOKORO_DIR OUT_DIR [voice] [speed]
Writes OUT_DIR/<key>.wav and OUT_DIR/words.json ({key: {dur, words: [[word, start, end]]}}).
"""
import json, os, sys
import soundfile as sf
from kokoro_onnx import Kokoro
from faster_whisper import WhisperModel

mdir, out = sys.argv[1], sys.argv[2]
voice = sys.argv[3] if len(sys.argv) > 3 else 'af_heart'
speed = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
lines = json.load(open(os.path.join(os.path.dirname(__file__), 'lines.json')))
k = Kokoro(os.path.join(mdir, 'kokoro-v1.0.onnx'), os.path.join(mdir, 'voices-v1.0.bin'))
asr = WhisperModel('small.en', device='cpu', compute_type='int8')
os.makedirs(out, exist_ok=True)
timing = {}
for key, text in lines.items():
    audio, sr = k.create(text, voice=voice, speed=speed, lang='en-us')
    path = os.path.join(out, key + '.wav')
    sf.write(path, audio, sr)
    segs, _ = asr.transcribe(path, word_timestamps=True, language='en')
    words = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in segs for w in s.words]
    timing[key] = {'dur': round(len(audio) / sr, 3), 'words': words}
    heard = ' '.join(w[0] for w in words)
    print(f'{key:9s} {len(audio) / sr:5.2f}s  {heard}')
json.dump(timing, open(os.path.join(out, 'words.json'), 'w'), indent=1)

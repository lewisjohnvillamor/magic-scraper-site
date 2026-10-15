# Shorts (motion graphics)

Vertical 1080x1920 Shorts drawn entirely in code: no screen recording. Each one
is hook -> problem -> rehook -> answer -> call to action, sold on the result
for one audience. Short #1 is "Find partners" (businesses turning a directory
into an outreach list). The companies on screen are fictional.

| File | Makes |
|---|---|
| `lines.json` | the script, one line per beat |
| `voice.py` | one WAV per line (Kokoro `af_heart`, offline) and `words.json`, every word timed with faster-whisper; the captions rise in on those times in both cuts |
| `music.py` | the music bed (120 BPM, the cuts sit on bar lines) and the sound effects, generated, so no licence or credit |
| `remotion/` | the film, two compositions: `ShortText` (captions, music, effects) and `ShortVoice` (the same with the voice) |

```
python3 tools/short/voice.py <kokoro model dir> <scratch>/public/vo
cp <scratch>/public/vo/words.json tools/short/remotion/src/
python3 tools/short/music.py <scratch>/public 27.5
# <scratch> holds package.json, tsconfig.json, src/ (copied from remotion/), public/ (fonts, vo, bed.wav, sfx)
npx remotion render src/index.ts ShortText out/short-text.mp4 --concurrency=4
npx remotion render src/index.ts ShortVoice out/short-voice.mp4 --concurrency=4
ffmpeg -i out/short-text.mp4 -c:v copy -af "loudnorm=I=-14.5:TP=-3:LRA=9,alimiter=limit=0.79:level=disabled" -c:a aac -b:a 192k out.mp4
```

The timeline (scene windows, when each line is spoken) is at the top of
`remotion/src/Short.tsx`; change a line, re-run `voice.py`, and adjust `VO`.

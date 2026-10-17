#!/usr/bin/env python3
"""Cut the YouTube walkthrough from raw-walk.webm.

Driven by beats-video.json: the frame times read back off the video's own beat
markers (tools/record-walkthrough.mjs paints them), never by wall-clock times.
The recording's clock drifts by seconds against Date.now(), and a caption timed
from wall clock lands on the wrong scene without anything complaining.

Two stretches are cut: the middle of the drill (a counter going up) and the
two reloads that set up the comparison. Everything else plays as recorded.

Order: node tools/record-walkthrough.mjs, read the beat markers back into
beats-video.json, render tools/cards/w_*.html to PNG, then
python3 tools/walkthrough-music.py bed-walk.wav 100 and
python3 tools/walkthrough-narrate.py (see its header), then:

  python3 tools/edit-walkthrough.py            # needs ffmpeg on PATH or $FFMPEG
"""
import json, os, re, subprocess, sys
from pathlib import Path

S = Path('/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad')
FF = os.environ.get('FFMPEG', 'ffmpeg')
MUSIC = S / 'bed-walk.wav'
VO = S / 'vo' / 'en_US-joe-medium'     # narration, one wav per scene (see tools/walkthrough-narration.json)
OUT = S / 'magic-scraper-walkthrough.mp4'
TITLE, ENDC, XF, XM = 4.0, 9.4, 0.6, 0.45

def run(args):
    r = subprocess.run([FF, '-y', '-hide_banner', '-v', 'error'] + args, capture_output=True, text=True)
    if r.returncode:
        sys.exit('ffmpeg failed:\n' + ' '.join(args[:8]) + '\n' + r.stderr[-2500:])

def dur(p):
    r = subprocess.run([FF, '-hide_banner', '-i', str(p)], capture_output=True, text=True)
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r.stderr).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)

v = json.loads((S / 'beats-video.json').read_text())
b = v['video']; raw = v['duration']
# The first beat is painted before the first frame is drawn and the last one
# as the recording closes, so neither is always read back.
b.setdefault('detected', 0.7)
b.setdefault('changed', min(raw - 0.2, b['changesUp'] + 10.5))
print('beats (video time):', {k: round(t, 2) for k, t in sorted(b.items(), key=lambda kv: kv[1])})

START = b['detected'] + 0.15          # skip the blank frames before the popup paints
END = min(raw - 0.15, b['changesUp'] + 10.6)
keep = [(START, b['drillStart'] + 5.0),
        (b['drillDone'] - 4.0, b['exported'] + 1.0),
        (b['changesUp'] - 1.6, END)]
for (a, z) in keep:
    assert z - a > 2, keep

offs = [0.0]
for (a, z) in keep[:-1]:
    offs.append(offs[-1] + (z - a) - XM)
def cut(t):
    """video time -> time in the cut body"""
    for (a, z), o in zip(keep, offs):
        if a - 1e-6 <= t <= z + 1e-6:
            return o + (t - a)
    for (a, z), o in zip(keep, offs):           # inside a dropped stretch: snap forward
        if t < a:
            return o
    return offs[-1] + (keep[-1][1] - keep[-1][0])
body_len = offs[-1] + keep[-1][1] - keep[-1][0]

caps = [
    ('w_cap1.png', cut(START) + 0.4,            cut(b['tidy']) - 0.2),
    ('w_cap2.png', cut(b['tidy']) + 0.3,        cut(b['crawlTab']) - 0.2),
    ('w_cap3.png', cut(b['crawlTab']) + 0.3,    cut(b['crawlDone']) + 1.3),
    ('w_cap4.png', cut(b['hint']) + 0.2,        cut(b['backToData']) - 0.3),
    ('w_cap5.png', cut(b['backToData']) + 0.3,  cut(b['exported']) + 0.7),
    ('w_cap6.png', cut(b['changesUp']) - 0.2,   body_len - 0.3),
]
LEAD = TITLE - XF
print(f'body {body_len:.2f}s, kept {[(round(a, 2), round(z, 2)) for a, z in keep]}')
for name, a, z in caps:
    print(f'  {name}  body {a:6.2f} -> {z:6.2f} ({z - a:4.1f}s)   final {a + LEAD:6.2f} -> {z + LEAD:6.2f}')
    if z - a < 2.0:
        sys.exit(f'{name} would be up for {z - a:.1f}s, too short to read')
    if not (S / name).exists():
        sys.exit(f'missing {name}: render tools/cards/w_*.html first')

def card(png, seconds, rate, out):
    run(['-loop', '1', '-i', str(S / png), '-frames:v', str(int(seconds * 30)),
         '-vf', f"scale=3840:2160,zoompan=z='min(1+{rate}*on,1.08)':d=1:"
                "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,format=yuv420p",
         '-r', '30', str(S / out)])
card('w_title.png', TITLE, 0.0007, 'w_seg_title.mp4')
card('w_end.png', ENDC, 0.00045, 'w_seg_end.mp4')

# Body: the kept stretches cross-faded, the beat marker covered, captions over.
inputs = ['-i', str(S / 'raw-walk.webm')]
for name, a, z in caps:
    inputs += ['-loop', '1', '-framerate', '30', '-t', f'{z - a + 0.1:.3f}', '-i', str(S / name)]
fc = [f'[0:v]split={len(keep)}' + ''.join(f'[p{i}]' for i in range(len(keep))) + ';']
for i, (a, z) in enumerate(keep):
    fc.append(f'[p{i}]trim={a:.3f}:{z:.3f},setpts=PTS-STARTPTS,fps=30,scale=1920:1080,'
              f'drawbox=x=0:y=0:w=20:h=20:color=0x0f0e15:t=fill[k{i}];')
prev = 'k0'
for i in range(1, len(keep)):
    fc.append(f'[{prev}][k{i}]xfade=transition=fade:duration={XM}:offset={offs[i]:.3f}[j{i}];')
    prev = f'j{i}'
for i, (name, a, z) in enumerate(caps, start=1):
    hold = z - a
    fc.append(f'[{i}:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1,'
              f'fade=t=out:st={hold - 0.4:.3f}:d=0.4:alpha=1,setpts=PTS-STARTPTS+{a:.3f}/TB[c{i}];')
    tail = ',format=yuv420p' if i == len(caps) else ''
    fc.append(f"[{prev}][c{i}]overlay=enable='between(t,{a:.3f},{z:.3f})':eof_action=pass{tail}[o{i}];")
    prev = f'o{i}'
run(inputs + ['-filter_complex', ''.join(fc).rstrip(';'), '-map', f'[{prev}]', '-r', '30',
              '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', str(S / 'w_seg_body.mp4')])

T, B, E = dur(S / 'w_seg_title.mp4'), dur(S / 'w_seg_body.mp4'), dur(S / 'w_seg_end.mp4')
print(f'segments: title {T:.2f}  body {B:.2f}  end {E:.2f}')
O1, O2 = T - XF, T + B - 2 * XF
run(['-i', str(S / 'w_seg_title.mp4'), '-i', str(S / 'w_seg_body.mp4'), '-i', str(S / 'w_seg_end.mp4'),
     '-filter_complex', f'[0:v][1:v]xfade=transition=fade:duration={XF}:offset={O1:.3f}[a];'
                        f'[a][2:v]xfade=transition=fade:duration={XF}:offset={O2:.3f}[v]',
     '-map', '[v]', '-r', '30', '-c:v', 'libx264', '-crf', '16', str(S / 'w_silent.mp4')])
D = dur(S / 'w_silent.mp4')

# Narration: each line starts just after its scene does, in the final timeline.
# A line longer than its scene is an error, not something to discover by ear.
FINAL = lambda body_t: body_t + LEAD
vo_at = {'title': 0.55, 'end': O2 + 0.9}
scene_end = {'title': O1}
for key, (name, a, z) in zip(['s1', 's2', 's3', 's4', 's5', 's6'], caps):
    vo_at[key] = FINAL(a) + 0.15
    scene_end[key] = FINAL(z) + 0.4
scene_end['end'] = D - 0.3
vo_inputs, vo_filters, vo_labels = [], [], []
for i, (key, at) in enumerate(sorted(vo_at.items(), key=lambda kv: kv[1])):
    wav = VO / f'{key}.wav'
    L = dur(wav)
    if at + L > scene_end[key] + 0.05:
        sys.exit(f'narration "{key}" ({L:.1f}s at {at:.1f}) overruns its scene, which ends at {scene_end[key]:.1f}')
    print(f'  vo {key:5s} {at:6.2f} -> {at + L:6.2f}   scene ends {scene_end[key]:6.2f}')
    vo_inputs += ['-i', str(wav)]
    vo_filters.append(f'[{i}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={int(at * 1000)}|{int(at * 1000)}[n{i}];')
    vo_labels.append(f'[n{i}]')
n = len(vo_labels)
run(vo_inputs + ['-filter_complex', ''.join(vo_filters) + ''.join(vo_labels) +
                 f'amix=inputs={n}:normalize=0,apad,atrim=0:{D:.3f},'
                 'highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,'
                 'loudnorm=I=-16:TP=-1.5:LRA=7[vo]',
                 '-map', '[vo]', '-ar', '48000', str(S / 'w_vo.wav')])

# Music under the voice: quieter overall, and ducked further while someone is
# talking, so every word sits on top without the bed vanishing between lines.
run(['-t', f'{D:.3f}', '-i', str(MUSIC), '-i', str(S / 'w_vo.wav'),
     '-filter_complex',
     f'[0:a]aresample=48000,afade=t=in:st=0:d=1.2,afade=t=out:st={D - 3.5:.3f}:d=3.5,volume=0.32[m];'
     '[1:a]asplit=2[v1][v2];'
     '[m][v1]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=450:makeup=1[md];'
     '[md][v2]amix=inputs=2:normalize=0,alimiter=limit=0.89[a]',
     '-map', '[a]', '-ar', '48000', '-ac', '2', '-c:a', 'aac', '-b:a', '192k', str(S / 'w_bed.m4a')])
run(['-i', str(S / 'w_silent.mp4'), '-i', str(S / 'w_bed.m4a'),
     '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
     '-c:a', 'copy', '-shortest', str(OUT)])
print(f'=== {OUT}  {dur(OUT):.2f}s ===')

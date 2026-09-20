#!/usr/bin/env python3
"""Cut the promo from raw.webm, driven by the beats the recorder printed.

Every timing in the old shell version was a literal -- CUT_A=18.6, four caption
offsets, END=42.6 -- measured by hand against one particular recording. Re-record
and every one of them is wrong, silently: the captions drift onto the wrong
scene and nothing complains. So the cut is computed from beats.json instead, and
the only judgement left in the file is how long a caption should stay up.
"""
import json, subprocess, sys
from pathlib import Path

S = Path('/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad')
MUSIC = Path('/root/.claude/uploads/11d9748f-98a9-5e1b-bd66-b55a5ed28106/89921033-Warm_Launch.mp3')
OUT = S / 'magic-scraper-promo.mp4'

TITLE, ENDC, XF = 3.2, 4.0, 0.5      # title card, end card, fades between segments
XM = 0.5                              # cross-fade over the mid-drill join

def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        sys.exit('ffmpeg failed:\n' + ' '.join(args[:6]) + '\n' + r.stderr[-2500:])
    return r.stdout.strip()

def dur(p):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                      '-of', 'csv=p=0', str(p)]))

b = {k: v / 1000 for k, v in json.loads((S / 'beats.json').read_text()).items()}
raw = dur(S / 'raw.webm')
print('raw:', round(raw, 2), 's   beats:', {k: round(v, 2) for k, v in b.items()})

# The drill is the only part that is just a counter going up, so it is the only
# part cut. Keep the start of it and the finish; drop the middle.
CUT_A = b['drillStart'] + 5.5
CUT_B = max(CUT_A + 2.0, b['drillDone'] - 4.5)
END = min(raw, b['changed'] + 1.4)
JOIN = CUT_A - XM
SHIFT = CUT_B - JOIN                  # raw -> cut, for anything after the join

def cut(t):
    return t if t <= CUT_A else t - SHIFT

print(f'cut: keep 0-{CUT_A:.2f}, drop {CUT_A:.2f}-{CUT_B:.2f} '
      f'({CUT_B - CUT_A:.1f}s of counter), keep {CUT_B:.2f}-{END:.2f}')

# Caption windows in the CUT timeline, each pinned to the scene it describes.
body_end = cut(END)
caps = [
    ('cap1.png', 0.40,                    cut(b['crawlStart']) + 0.30),
    ('cap2.png', cut(b['crawlStart']) + 0.40, cut(b['crawlDone']) + 1.40),
    ('cap3.png', cut(b['drillStart']) + 0.30, cut(b['backToData']) - 0.40),
    ('cap4.png', cut(b['backToData']) + 0.30, cut(b['exported']) + 1.20),
    ('cap5.png', cut(b['changesUp']) + 0.20,  body_end - 0.30),
]
# The body is composited after the title card with a cross-fade, so a caption's
# time in the finished file is its body time plus that. Printed, because
# sampling frames at the body times is how a caption gets called missing when
# it is only 2.7 seconds later than the number being checked.
LEAD = TITLE - XF
for name, a, z in caps:
    print(f'  {name}  body {a:6.2f} -> {z:6.2f}  ({z - a:.1f}s)   '
          f'final {a + LEAD:6.2f} -> {z + LEAD:6.2f}')
    if z - a < 1.6:
        sys.exit(f'{name} would be on screen for {z - a:.1f}s, which nobody can read')
    if not (S / name).exists():
        sys.exit(f'missing {name} -- run tools/shoot-cards.mjs first')

def card(png, seconds, rate, out):
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', str(S / png),
         '-frames:v', str(int(seconds * 30)),
         '-vf', f"scale=3840:2160,zoompan=z='min(1+{rate}*on,1.09)':d=1:"
                "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,format=yuv420p",
         '-r', '30', str(S / out)])

card('card_title.png', TITLE, 0.00085, 'seg_title.mp4')
card('card_end.png',   ENDC,  0.00055, 'seg_end.mp4')

# One ffmpeg pass: the two halves of the plate, cross-faded, with five caption
# overlays fading in and out over the join.
inputs = ['-i', str(S / 'raw.webm')]
for name, a, z in caps:
    inputs += ['-loop', '1', '-framerate', '30', '-t', f'{z - a + 0.1:.3f}', '-i', str(S / name)]

fc = [f'[0:v]split=2[p1][p2];',
      f'[p1]trim=0:{CUT_A:.3f},setpts=PTS-STARTPTS,scale=1920:1080,fps=30[va];',
      f'[p2]trim={CUT_B:.3f}:{END:.3f},setpts=PTS-STARTPTS,scale=1920:1080,fps=30[vb];',
      f'[va][vb]xfade=transition=fade:duration={XM}:offset={JOIN:.3f}[v];']
prev = 'v'
for i, (name, a, z) in enumerate(caps, start=1):
    hold = z - a
    fc.append(f'[{i}:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,'
              f'fade=t=out:st={hold - 0.35:.3f}:d=0.35:alpha=1,'
              f'setpts=PTS-STARTPTS+{a:.3f}/TB[c{i}];')
    nxt = f'o{i}'
    tail = ',format=yuv420p' if i == len(caps) else ''
    fc.append(f'[{prev}][c{i}]overlay=enable=\'between(t,{a:.3f},{z:.3f})\':'
              f'eof_action=pass:repeatlast=0{tail}[{nxt}];')
    prev = nxt
filt = ''.join(fc).rstrip(';')

run(['ffmpeg', '-y', '-v', 'error'] + inputs +
    ['-filter_complex', filt, '-map', f'[{prev}]', '-r', '30', str(S / 'seg_body.mp4')])

T, B, E = dur(S / 'seg_title.mp4'), dur(S / 'seg_body.mp4'), dur(S / 'seg_end.mp4')
print(f'segments: title {T:.2f}s  body {B:.2f}s  end {E:.2f}s')

# Offsets from the MEASURED lengths: zoompan does not land exactly on request,
# and using the intended ones once cut six seconds off the end.
O1, O2 = T - XF, T + B - 2 * XF
run(['ffmpeg', '-y', '-v', 'error', '-i', str(S / 'seg_title.mp4'),
     '-i', str(S / 'seg_body.mp4'), '-i', str(S / 'seg_end.mp4'),
     '-filter_complex',
     f'[0:v][1:v]xfade=transition=fade:duration={XF}:offset={O1:.3f}[a];'
     f'[a][2:v]xfade=transition=fade:duration={XF}:offset={O2:.3f}[v]',
     '-map', '[v]', '-r', '30', str(S / 'silent.mp4')])

D = dur(S / 'silent.mp4')
print(f'silent cut: {D:.2f}s')

# The bed is quiet until 0:06 and lands on the beat there; starting at 3.0 puts
# that landing on the cut out of the title card.
run(['ffmpeg', '-y', '-v', 'error', '-ss', '3.0', '-t', f'{D:.3f}', '-i', str(MUSIC),
     '-af', f'afade=t=in:st=0:d=0.6,afade=t=out:st={D - 2.4:.3f}:d=2.4,'
            'loudnorm=I=-16:TP=-1.5:LRA=11',
     '-vn', '-ar', '48000', '-ac', '2', str(S / 'bed.m4a')])

run(['ffmpeg', '-y', '-v', 'error', '-i', str(S / 'silent.mp4'), '-i', str(S / 'bed.m4a'),
     '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p',
     '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(OUT)])

print('=== final ===')
print(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size',
           '-show_entries', 'stream=codec_name,width,height,r_frame_rate',
           '-of', 'default=nw=1', str(OUT)]))

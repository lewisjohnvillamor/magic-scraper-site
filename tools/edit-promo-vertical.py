#!/usr/bin/env python3
"""The 9:16 cut, from the same plate and the same beats as the landscape one.

Same reasoning as tools/edit-promo.py: every timing here used to be a literal
measured against one recording, so a re-record silently slid the captions onto
the wrong scenes. The popup region is cropped out of the 1920x1080 plate and
set on a dark canvas with the caption above it.
"""
import json, subprocess, sys
from pathlib import Path

S = Path('/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad')
MUSIC = Path('/root/.claude/uploads/11d9748f-98a9-5e1b-bd66-b55a5ed28106/89921033-Warm_Launch.mp3')
OUT = S / 'magic-scraper-promo-vertical.mp4'

TITLE, ENDC, XF, XM = 3.2, 4.0, 0.5, 0.5
# The popup sits at x 1157-1809, y 65-1014 in the plate: record-promo.mjs scales
# it 1.42 and pins it 110px from the right edge. Cropped a little wider so a
# strip of the shop still shows down the left -- the point of the shot is that
# this runs on a real page, not in a mockup.
CROP = 'crop=740:958:1085:60'

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

CUT_A = b['drillStart'] + 5.5
CUT_B = max(CUT_A + 2.0, b['drillDone'] - 4.5)
END = min(raw, b['changed'] + 1.4)
JOIN = CUT_A - XM
SHIFT = CUT_B - JOIN
cut = lambda t: t if t <= CUT_A else t - SHIFT
BODY = cut(END)
print(f'raw {raw:.2f}s -> body {BODY:.2f}s  (dropped {CUT_B - CUT_A:.1f}s of drill counter)')

caps = [
    ('v_cap1.png', 0.40,                        cut(b['crawlStart']) + 0.30),
    ('v_cap2.png', cut(b['crawlStart']) + 0.40, cut(b['crawlDone']) + 1.40),
    ('v_cap3.png', cut(b['drillStart']) + 0.30, cut(b['backToData']) - 0.40),
    ('v_cap4.png', cut(b['backToData']) + 0.30, cut(b['exported']) + 1.20),
    ('v_cap5.png', cut(b['changesUp']) + 0.20,  BODY - 0.30),
]
LEAD = TITLE - XF
for name, a, z in caps:
    print(f'  {name}  body {a:6.2f} -> {z:6.2f}   final {a + LEAD:6.2f} -> {z + LEAD:6.2f}')
    if z - a < 1.6:
        sys.exit(f'{name} would be on screen for {z - a:.1f}s, which nobody can read')
    if not (S / name).exists():
        sys.exit(f'missing {name} -- run tools/shoot-cards-vertical.mjs first')

def card(png, seconds, rate, out):
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', str(S / png),
         '-frames:v', str(int(seconds * 30)),
         '-vf', f"scale=2160:3840,zoompan=z='min(1+{rate}*on,1.09)':d=1:"
                "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,format=yuv420p",
         '-r', '30', str(S / out)])

card('v_title.png', TITLE, 0.00085, 'vseg_title.mp4')
card('v_end.png',   ENDC,  0.00055, 'vseg_end.mp4')

inputs = ['-i', str(S / 'raw.webm')]
for name, a, z in caps:
    inputs += ['-loop', '1', '-framerate', '30', '-t', f'{z - a + 0.1:.3f}', '-i', str(S / name)]
foot_i = len(caps) + 1
canvas_i = foot_i + 1
inputs += ['-loop', '1', '-framerate', '30', '-t', f'{BODY:.3f}', '-i', str(S / 'v_foot.png'),
           '-f', 'lavfi', '-t', f'{BODY:.3f}', '-i', 'color=c=0x14121f:s=1080x1920:r=30']

fc = [f'[0:v]split=2[p1][p2];',
      f'[p1]trim=0:{CUT_A:.3f},setpts=PTS-STARTPTS,{CROP},scale=1035:1340,fps=30[va];',
      f'[p2]trim={CUT_B:.3f}:{END:.3f},setpts=PTS-STARTPTS,{CROP},scale=1035:1340,fps=30[vb];',
      f'[va][vb]xfade=transition=fade:duration={XM}:offset={JOIN:.3f}[v];',
      f'[{canvas_i}:v][v]overlay=x=22:y=500[b0];',
      f'[b0][{foot_i}:v]overlay=0:0[b1];']
prev = 'b1'
for i, (name, a, z) in enumerate(caps, start=1):
    hold = z - a
    fc.append(f'[{i}:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,'
              f'fade=t=out:st={hold - 0.35:.3f}:d=0.35:alpha=1,'
              f'setpts=PTS-STARTPTS+{a:.3f}/TB[c{i}];')
    tail = ',format=yuv420p' if i == len(caps) else ''
    fc.append(f"[{prev}][c{i}]overlay=enable='between(t,{a:.3f},{z:.3f})':"
              f'eof_action=pass:repeatlast=0{tail}[o{i}];')
    prev = f'o{i}'

run(['ffmpeg', '-y', '-v', 'error'] + inputs +
    ['-filter_complex', ''.join(fc).rstrip(';'), '-map', f'[{prev}]', '-r', '30',
     str(S / 'vseg_body.mp4')])

T, B, E = dur(S / 'vseg_title.mp4'), dur(S / 'vseg_body.mp4'), dur(S / 'vseg_end.mp4')
print(f'segments: title {T:.2f}s  body {B:.2f}s  end {E:.2f}s')
O1, O2 = T - XF, T + B - 2 * XF
run(['ffmpeg', '-y', '-v', 'error', '-i', str(S / 'vseg_title.mp4'),
     '-i', str(S / 'vseg_body.mp4'), '-i', str(S / 'vseg_end.mp4'),
     '-filter_complex',
     f'[0:v][1:v]xfade=transition=fade:duration={XF}:offset={O1:.3f}[a];'
     f'[a][2:v]xfade=transition=fade:duration={XF}:offset={O2:.3f}[v]',
     '-map', '[v]', '-r', '30', str(S / 'vsilent.mp4')])

D = dur(S / 'vsilent.mp4')
print(f'silent cut: {D:.2f}s')
run(['ffmpeg', '-y', '-v', 'error', '-ss', '3.0', '-t', f'{D:.3f}', '-i', str(MUSIC),
     '-af', f'afade=t=in:st=0:d=0.6,afade=t=out:st={D - 2.4:.3f}:d=2.4,'
            'loudnorm=I=-16:TP=-1.5:LRA=11',
     '-vn', '-ar', '48000', '-ac', '2', str(S / 'vbed.m4a')])
run(['ffmpeg', '-y', '-v', 'error', '-i', str(S / 'vsilent.mp4'), '-i', str(S / 'vbed.m4a'),
     '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
     '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(OUT)])
print('=== final ===')
print(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size',
           '-show_entries', 'stream=codec_name,width,height,r_frame_rate',
           '-of', 'default=nw=1', str(OUT)]))

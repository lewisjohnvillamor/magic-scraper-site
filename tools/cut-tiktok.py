#!/usr/bin/env python3
"""Encode the short-form cut: trim the dead head, add the bed, write the MP4.

Almost nothing to do here on purpose. The landscape promo composites captions,
cross-fades and cards in ffmpeg, which is why its timings went stale every time
the plate was re-recorded. This cut is a page that already knows its own
timeline, so all that is left is a trim, a fade and an audio track.
"""
import json, subprocess, sys
from pathlib import Path

S = Path('/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad')
MUSIC = Path('/root/.claude/uploads/11d9748f-98a9-5e1b-bd66-b55a5ed28106/89921033-Warm_Launch.mp3')
OUT = S / 'magic-scraper-tiktok.mp4'

def run(a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode:
        sys.exit('ffmpeg failed:\n' + ' '.join(a[:8]) + '\n' + r.stderr[-2000:])
    return r.stdout.strip()

def dur(p):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                      '-of', 'csv=p=0', str(p)]))

head = json.loads((S / 'tiktok-head.json').read_text())['head']
raw = dur(S / 'tiktok-raw.webm')
# A breath at the end rather than a hard stop on the end card.
body = raw - head - 0.25
print(f'raw {raw:.2f}s, trimming {head:.2f}s of head -> {body:.2f}s')
if body < 12:
    sys.exit(f'only {body:.1f}s of cut -- the recording did not complete')

run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{head:.3f}', '-t', f'{body:.3f}',
     '-i', str(S / 'tiktok-raw.webm'),
     '-vf', f'fps=30,scale=1080:1920:flags=lanczos,fade=t=out:st={body-0.5:.2f}:d=0.5,format=yuv420p',
     '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
     str(S / 'tiktok-silent.mp4')])

d = dur(S / 'tiktok-silent.mp4')
# The bed lands on its beat at 0:06; starting at 5.6 puts that on the first cut
# out of the hook rather than somewhere in the middle of a caption.
run(['ffmpeg', '-y', '-v', 'error', '-ss', '5.6', '-t', f'{d:.3f}', '-i', str(MUSIC),
     '-af', f'afade=t=in:st=0:d=0.4,afade=t=out:st={d-1.6:.2f}:d=1.6,'
            'loudnorm=I=-14:TP=-1.0:LRA=11',     # -14 LUFS: what the feeds normalise to
     '-vn', '-ar', '48000', '-ac', '2', str(S / 'tiktok-bed.m4a')])

run(['ffmpeg', '-y', '-v', 'error', '-i', str(S / 'tiktok-silent.mp4'),
     '-i', str(S / 'tiktok-bed.m4a'),
     '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
     '-movflags', '+faststart', '-shortest', str(OUT)])

print('=== final ===')
print(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size',
           '-show_entries', 'stream=codec_name,width,height,r_frame_rate',
           '-of', 'default=nw=1', str(OUT)]))

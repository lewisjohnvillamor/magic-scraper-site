#!/usr/bin/env python3
"""Turn the recording into the Remotion timeline (plan.json).

Reads the beat markers off the video frames (record.mjs paints them), finds
the page loads between scenes (the marker is missing while a page loads), and
sizes every scene to whichever is longer: its footage, or its narration plus a
breath. Footage shorter than its narration is held on its last frame rather
than having the voice cut off or run into the next scene.

  python3 plan.py FFMPEG walk2.mp4 walk2-beats.json VO_DIR OUT/plan.json
"""
import json, subprocess, sys, wave

FF, video, beats_json, vo_dir, out = sys.argv[1:6]
FPS = 30
order = json.load(open(beats_json))['order']
raw = subprocess.run([FF, '-v', 'error', '-i', video, '-vf', f'fps={FPS},crop=8:8:4:4,format=gray',
                      '-f', 'rawvideo', '-'], capture_output=True).stdout
n = len(raw) // 64
idx = []
for i in range(n):
    v = sum(raw[i * 64:(i + 1) * 64]) / 64
    k = (v - 30) / 10
    idx.append(round(k) if abs(k - round(k)) < 0.3 and 0 <= round(k) <= len(order) else None)
b = {}
for i, k in enumerate(idx):
    if k and k >= 1 and order[k - 1] not in b:
        b[order[k - 1]] = i / FPS
gaps, start = [], None                      # page loads: no readable marker
for i, k in enumerate(idx):
    t = i / FPS
    if k is None and start is None and t > 1:
        start = t
    elif k is not None and start is not None:
        if t - start > 0.1: gaps.append((round(start, 2), round(t, 2)))
        start = None
print('beats:', {k: round(v, 2) for k, v in b.items()})
print('page loads:', gaps)

def before_load(t):
    """the last moment before the first page load that starts after t"""
    later = [g for g in gaps if g[0] > t + 0.5]
    return later[0][0] - 0.08 if later else None

def vo(key):
    with wave.open(f'{vo_dir}/{key}.wav') as w:
        return w.getnframes() / w.getframerate()

S = [
  dict(key='intro', kind='title'),
  # Held on the shop before the panel opens, so "click the icon" lands on the click.
  dict(key='open', kind='video', page='catalogue', segs=[(b['shop'] + 0.2, b['detected'])], holds=[(-1, 1.3)],
       cam=[(0, 'wide'), (0.45, 'wide'), (0.62, 'icon'), (0.82, 'wide')]),
  dict(key='detected', kind='video', page='catalogue', step='Find the table',
       segs=[(b['detected'], b['tidy'])], cam=[(0, 'wide'), (0.35, 'page'), (0.8, 'panelTop')]),
  dict(key='tidy', kind='video', page='catalogue', step='Tidy the columns',
       segs=[(b['tidy'], before_load(b['tidy']))], cam=[(0, 'panelTable'), (1, 'panelTable')]),
  dict(key='rates', kind='video', page='rates', step='Choose the right table',
       segs=[(b['rates'] - 0.2, before_load(b['rates']))], cam=[(0, 'wide'), (0.4, 'wide'), (1, 'wide')]),
  dict(key='pick', kind='video', page='awkward', step='Point at it yourself',
       segs=[(b['awkward'] - 0.2, before_load(b['picked']))],
       cam=[(0, 'wide'), (0.25, 'pageTable'), (0.7, 'pageTable'), (0.82, 'panelTable'), (1, 'panelTable')]),
  dict(key='crawl', kind='video', page='catalogue', step='Collect every page',
       segs=[(b['crawlTab'] - 1.6, b['crawlDone'] + 0.6)], cam=[(0, 'panelTop'), (1, 'panelTop')]),
  dict(key='drill', kind='video', page='catalogue', step='Open the page behind each row',
       segs=[(b['crawlDone'] + 0.6, b['drillStart'] + 6.0), (b['drillDone'] - 3.5, b['details'] - 0.2)],
       cam=[(0, 'panelTop'), (0.3, 'panelTop'), (1, 'panelMid')]),
  # Held on the new columns while they are described, then the export click.
  dict(key='export', kind='video', page='catalogue', step='Download it',
       segs=[(b['details'] - 0.2, b['details'] + 5.6), (b['details'] + 5.6, b['exported'] + 1.4)], holds=[(0, None)],
       cam=[(0, 'panelTable'), (0.7, 'panelTable'), (0.82, 'panelTop'), (1, 'panelTop')]),
  dict(key='file', kind='file', step='Download it'),
  dict(key='changes', kind='video', page='catalogue', step='See what changed',
       segs=[(b['changes'] - 1.4, b['end'])], cam=[(0, 'panelTop'), (0.3, 'panelTable'), (1, 'panelTable')]),
  dict(key='outro', kind='outro'),
]
LEAD, TAIL = 0.45, 0.9                       # silence before and after each line
t, steps = 0.0, 0
for s in S:
    s['vo'] = round(vo(s['key']), 3)
    foot = sum(z - a for a, z in s.get('segs', [])) if s['kind'] == 'video' else 0
    need = LEAD + s['vo'] + TAIL
    if s['kind'] == 'title': need = max(need, 6)
    if s['kind'] == 'outro': need = need + 2.5
    s['dur'] = round(max(foot, need), 3)
    s['hold'] = round(max(0, s['dur'] - foot), 3) if s['kind'] == 'video' else 0
    s['start'] = round(t, 3); s['voAt'] = round(t + LEAD, 3)
    for a, z in s.get('segs', []):
        assert z and z - a > 0.5, (s['key'], a, z)
    if s.get('step') and (not S.index(s) or S[S.index(s) - 1].get('step') != s['step']):
        steps += 1
    s['stepNo'] = steps if s.get('step') else None
    t += s['dur']
for s in S:
    # pieces: footage played straight, and still frames where the narration
    # needs longer. holds = [(after segment i, seconds or None for the rest)];
    # i = -1 is before the first segment; whatever is left over goes at the end.
    if s['kind'] == 'video':
        segs, left, pieces = s['segs'], s['hold'], []
        plan = dict(s.get('holds', []))
        def freeze(at, sec):
            if sec > 0.04: pieces.append({'freeze': round(at, 3), 'dur': round(sec, 3)})
        if -1 in plan:
            h = min(left, plan[-1] if plan[-1] is not None else left); freeze(segs[0][0], h); left -= h
        for i, (a, z) in enumerate(segs):
            pieces.append({'play': [round(a, 3), round(z, 3)]})
            if i in plan and i != len(segs) - 1:
                h = min(left, plan[i] if plan[i] is not None else left); freeze(z - 0.04, h); left -= h
        freeze(segs[-1][1] - 0.04, left)
        s['pieces'] = pieces
    s['segs'] = [(round(a, 3), round(z, 3)) for a, z in s.get('segs', [])]
    print(f"{s['key']:9s} {s['start']:7.2f}s  dur {s['dur']:6.2f}  vo {s['vo']:5.2f}  hold {s['hold']:5.2f}  {s.get('step') or ''}")
json.dump({'fps': FPS, 'total': round(t, 3), 'steps': steps, 'scenes': S}, open(out, 'w'), indent=1)
print(f'total {t:.1f}s')

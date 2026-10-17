"""Music and sound effects for the Short, generated rather than licensed (no
credit, no terms). 120 BPM, so a bar is 2 s and the cut points of the film sit
on bar lines: a light hook (bar 0), a tense ticking problem (bars 1-4), a riser
into the rehook (bar 5), the drop on "One click" at 12 s (bars 6-9), and a
lighter groove under the call to action that ends on a held chord.

  python3 tools/short/music.py OUT_DIR [length]
Writes OUT_DIR/bed.wav and OUT_DIR/sfx/{whoosh,pop,click,key,impact,ding,tick}.wav.
Deterministic (fixed seed); numpy only."""
import os, sys, wave
import numpy as np

SR = 44100; BEAT = 0.5; BAR = 4 * BEAT
out = sys.argv[1]; LEN = float(sys.argv[2]) if len(sys.argv) > 2 else 27.5
N = int(SR * LEN); rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, cut):
    """One-pole low-pass as a convolution with its (truncated) impulse response."""
    tau = SR / (2 * np.pi * cut); n = max(2, int(tau * 6))
    k = np.exp(-np.arange(n) / tau); k /= k.sum()
    return np.convolve(x, k)[: len(x)]
def hp(x, cut): return x - lp(x, cut)
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))
def saw(f, n, det=(0.0,)):
    t = np.arange(n) / SR
    return sum(2 * ((t * f * 2 ** (d / 12) + rng.random()) % 1.0) - 1 for d in det) / len(det)

# ---- instruments
def kick(g=1.0):
    n = int(0.32 * SR); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t / 0.035); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.12) * g
def clap():
    n = int(0.22 * SR); x = hp(rng.standard_normal(n), 900)
    e = sum(np.roll(env(n, 0.001, 0.012), int(k * 0.011 * SR)) * (k < 3 or 1) for k in range(3))
    return lp(x, 6000) * (e * 0.5 + env(n, 0.001, 0.07)) * 0.35
def hat(open_=False):
    n = int((0.16 if open_ else 0.045) * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.001, 0.05 if open_ else 0.012) * 0.22
def bass(m, dur):
    n = int(dur * SR); s = lp(saw(hz(m), n, (-0.05, 0.05)), 420) + 0.6 * np.sin(2 * np.pi * hz(m) * np.arange(n) / SR)
    return s * env(n, 0.004, dur * 0.7) * 0.55
def pluck(m, dur=0.22):
    n = int(dur * SR); t = np.arange(n) / SR
    sq = np.sign(np.sin(2 * np.pi * hz(m) * t)) * 0.5 + np.sin(2 * np.pi * hz(m) * 2 * t) * 0.3
    return lp(sq, 2600) * env(n, 0.002, 0.07) * 0.22
def pad(notes, dur, cut=1100):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(saw(hz(m), n, (-0.1, 0.0, 0.09)) for m in notes) / len(notes)
    e = np.minimum(1, t / 0.4) * np.clip((dur - t) / 0.5, 0, 1)
    return lp(s, cut) * e * 0.32
def tick():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1850 * t) + 0.4 * np.sin(2 * np.pi * 2900 * t)) * env(n, 0.0005, 0.008) * 0.3

CHORDS = {  # groove: Am - F - C - G
    'Am': ([57, 60, 64, 69], 45), 'F': ([57, 60, 65, 69], 41), 'C': ([55, 60, 64, 67], 48), 'G': ([55, 59, 62, 67], 43)}
PROG = ['Am', 'F', 'C', 'G']

def arp(bar_t, name, density=4, gain=1.0):
    notes, _ = CHORDS[name]; seq = [notes[0], notes[2], notes[1] + 12, notes[3], notes[2] + 12, notes[3], notes[1] + 12, notes[2]]
    for i in range(4 * density):
        add(pluck(seq[i % len(seq)] + 12), bar_t + i * BEAT / density, gain, pan=0.35 if i % 2 else -0.35)

# bar 0: the hook, light and bright
add(pad(CHORDS['Am'][0], BAR + 0.3), 0, 0.8)
arp(0, 'Am', 4, 0.8)
for b in range(4):
    if b % 2 == 0: add(kick(0.7), b * BEAT)
    add(hat(), b * BEAT + BEAT / 2)
# bars 1-4: the problem, tense: a low drone, a clock, a pulse
drone_n = int(4 * BAR * SR); t = np.arange(drone_n) / SR
drone = lp(saw(hz(33), drone_n, (-0.08, 0.08)) + 0.5 * saw(hz(40), drone_n), 260) * np.minimum(1, t / 0.6) * 0.5
add(drone, BAR)
for b in range(16):
    add(tick(), BAR + b * BEAT, 0.9)
    if b % 2 == 0: add(kick(0.35), BAR + b * BEAT)
for b in range(4):  # a dissonant pad, swelling a little each bar
    add(pad([57, 58, 64], BAR + 0.2, 700 + 250 * b), BAR + b * BAR, 0.45 + 0.08 * b)
# bar 5: riser into "There's a faster way"
rs = 5 * BAR; n = int(BAR * SR); t = np.arange(n) / SR
noise = rng.standard_normal(n); grow = (t / BAR) ** 2
riser = (lp(noise, 600) * (1 - grow) + hp(noise, 2500) * grow) * grow * 0.5
sweep = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2.6 * t / BAR)) / SR) * grow * 0.25
cut = int((BAR - 0.09) * SR); riser[cut:] = 0; sweep[cut:] = 0
add(riser + sweep, rs)
for i, at in enumerate(np.concatenate([np.arange(0, 1.0, BEAT / 2), np.arange(1.0, BAR - 0.12, BEAT / 4)])):
    add(clap(), rs + at, 0.25 + 0.5 * at / BAR)
# bars 6-12: the drop on "One click", then the groove under the CTA
for bi in range(6, 13):
    bt = bi * BAR; name = PROG[(bi - 6) % 4]; notes, root = CHORDS[name]
    light = bi >= 10
    add(pad(notes, BAR + 0.3, 1600), bt, 0.7)
    arp(bt, name, 4, 0.7 if light else 0.9)
    for b in range(4):
        add(kick(0.95), bt + b * BEAT)
        if b % 2 == 1: add(clap(), bt + b * BEAT, 0.9)
        add(hat(open_=(b == 3)), bt + b * BEAT + BEAT / 2)
        for e in range(2): add(bass(root + (12 if e else 0), BEAT / 2 * 0.9), bt + b * BEAT + e * BEAT / 2)
# the end: one held chord at 26 s
add(kick(1.0), 13 * BAR); add(pad(CHORDS['Am'][0] + [76], 1.5, 1800), 13 * BAR, 1.0)
for m in CHORDS['Am'][0]: add(pluck(m + 12, 1.2), 13 * BAR, 0.6)

def write(path, l, r=None):
    r = l if r is None else r
    st = np.stack([l, r], 1); st = np.tanh(st / max(1e-9, np.abs(st).max()) * 1.4) / np.tanh(1.4) * 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype('<i2').tobytes())
fade = np.clip((LEN - np.arange(N) / SR) / 1.2, 0, 1)
os.makedirs(os.path.join(out, 'sfx'), exist_ok=True)
write(os.path.join(out, 'bed.wav'), L * fade, R * fade)

# ---- sound effects, one file each
def sfx(name, sig): write(os.path.join(out, 'sfx', name + '.wav'), sig)
n = int(0.5 * SR); t = np.arange(n) / SR; bell = np.sin(np.pi * t / 0.5) ** 2; noise = rng.standard_normal(n)
sfx('whoosh', (lp(noise, 900) * (1 - t / 0.5) + hp(noise, 2200) * (t / 0.5)) * bell)
n = int(0.09 * SR); t = np.arange(n) / SR
sfx('pop', np.sin(2 * np.pi * np.cumsum(520 + 600 * t / 0.09) / SR) * env(n, 0.002, 0.03))
n = int(0.06 * SR); c = np.zeros(n); c[:180] = rng.standard_normal(180); c[1300:1440] = rng.standard_normal(140) * 0.7
sfx('click', hp(c, 1500) * 0.8)
n = int(0.07 * SR); t = np.arange(n) / SR
sfx('key', hp(rng.standard_normal(n), 2000) * env(n, 0.0005, 0.006) + np.sin(2 * np.pi * 190 * t) * env(n, 0.001, 0.018) * 0.8)
n = int(1.2 * SR); t = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(32 + 70 * np.exp(-t / 0.08)) / SR) * np.exp(-t / 0.45)
sfx('impact', boom + lp(rng.standard_normal(n), 1800) * np.exp(-t / 0.09) * 0.6)
n = int(1.0 * SR); t = np.arange(n) / SR
sfx('ding', (np.sin(2 * np.pi * 1318.5 * t) + 0.6 * np.sin(2 * np.pi * 1975.5 * t) + 0.25 * np.sin(2 * np.pi * 2637 * t)) * env(n, 0.002, 0.28))
sfx('tick', tick())
print('bed.wav', LEN, 's and', len(os.listdir(os.path.join(out, 'sfx'))), 'effects')

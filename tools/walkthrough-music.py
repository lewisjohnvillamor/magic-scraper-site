"""Music for the YouTube walkthrough, generated rather than licensed, so it
needs no credit and has no terms. A calm, warm bed for the walkthrough: 92 BPM, Fmaj7 - G6 - Em7 - Am9.
Pad, plucked arpeggio, round bass, soft drums that enter after the intro.
Deterministic (fixed seed). Writes 16-bit stereo WAV."""
import numpy as np, wave, sys
SR = 44100; BPM = 92.0; BEAT = 60 / BPM; BAR = 4 * BEAT
LEN = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
N = int(SR * LEN); rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
CHORDS = [[53, 57, 60, 64], [55, 59, 62, 64], [52, 55, 59, 62], [45, 52, 55, 59, 60]]  # Fmaj7 G6 Em7 Am9
ROOTS = [41, 43, 40, 45]
def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))
def onepole(x, cut):
    a = np.exp(-2 * np.pi * cut / SR); y = np.empty_like(x); acc = 0.0
    for k in range(len(x)): acc = (1 - a) * x[k] + a * acc; y[k] = acc
    return y
def pad(notes, dur):
    t = np.arange(int(dur * SR)) / SR; s = np.zeros_like(t)
    for m in notes:
        for det in (-0.08, 0.0, 0.07):
            f = hz(m + 12) * 2 ** (det / 12)
            s += 2 * ((t * f) % 1.0) - 1
    s = onepole(s / (len(notes) * 3), 900)
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.0).clip(0, 1)
    return s * env
def pluck(m, dur=1.2):
    f = hz(m); n = int(SR / f); buf = rng.uniform(-1, 1, n); out = np.empty(int(dur * SR))
    for k in range(len(out)):
        out[k] = buf[k % n]; buf[k % n] = 0.5 * (buf[k % n] + buf[(k + 1) % n]) * 0.996
    return onepole(out, 3500) * np.exp(-np.arange(len(out)) / SR * 2.2)
def bass(m, dur):
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    s = np.tanh(1.6 * np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t))
    return s * np.minimum(1, t / 0.01) * np.exp(-t * 1.6)
def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 48 + 90 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)
def hat():
    t = np.arange(int(0.06 * SR)) / SR; n = rng.uniform(-1, 1, len(t))
    n = n - onepole(n, 7000); return n * np.exp(-t * 70)
def snap():
    t = np.arange(int(0.18 * SR)) / SR; n = rng.uniform(-1, 1, len(t))
    n = onepole(n - onepole(n, 1200), 6000); return n * np.exp(-t * 26)
cache = {m: pluck(m) for c in CHORDS for m in set(c + [x + 12 for x in c])}
bars = int(LEN / BAR) + 1
for b in range(bars):
    c = b % 4; t0 = b * BAR
    add(pad(CHORDS[c], BAR + 1.0), t0, 0.0, 0.33)
    arp = CHORDS[c] + [CHORDS[c][1] + 12]
    pat = [0, 2, 1, 3, 4, 3, 1, 2]
    for k in range(8):
        m = arp[pat[k] % len(arp)] + 12
        if m not in cache: cache[m] = pluck(m)
        add(cache[m], t0 + k * BEAT / 2, (-0.35 if k % 2 else 0.35), 0.26)
    if b >= 2:
        add(bass(ROOTS[c], BEAT * 1.9), t0, 0, 0.42)
        add(bass(ROOTS[c], BEAT * 1.9), t0 + 2 * BEAT, 0, 0.32)
    if b >= 4:
        for k in (0, 2): add(kick(), t0 + k * BEAT, 0, 0.55)
        for k in range(8): add(hat(), t0 + k * BEAT / 2, 0.25, 0.10 if k % 2 else 0.06)
    if b >= 8:
        for k in (1, 3): add(snap(), t0 + k * BEAT, -0.1, 0.22)
mix = np.stack([L, R], 1)
fade_in = np.minimum(1, np.arange(N) / (SR * 1.5))[:, None]
mix *= fade_in
mix = np.tanh(mix * 1.1)
mix /= np.max(np.abs(mix)) / 0.89
pcm = (mix * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1], f'{LEN:.0f}s at {BPM} BPM, bar {BAR:.3f}s')

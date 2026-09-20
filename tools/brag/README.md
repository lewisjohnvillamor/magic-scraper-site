# Short-form product cuts

Two 20.5s vertical videos, built with [Hyperframes](https://hyperframes.heygen.com/)
from the composition sources in `src/`.

```
tools/brag/build.sh              # both
tools/brag/build.sh drill        # one
CHECK_ONLY=1 tools/brag/build.sh # gate only, no render
```

Output lands in `brag-output/`, which is gitignored. **The sources here are the
artefact**, on the same rule as `tools/tiktok/*.webm`: the thing worth keeping
is what makes the video, not the video. `build.sh` assembles everything else
from files already in this repo or the extension repo beside it, so a fresh
clone rebuilds both cuts without hunting for an asset.

| Cut | Argument | Reveal |
|---|---|---|
| `cut1` → `brag.mp4` | copying by hand, then one click | the crawl finished |
| `drill` → `brag-drill.mp4` | the field is never on the list | the chain builder, ten levels |

The drill cut's payoff is `chain-builder.png`, captured by
`tools/shoot_chain.mjs` in the extension repo. It is the panel where the chain
is *configured*, not the table it eventually produces -- which matters,
because a cut arguing about depth should not resolve into a flat table. The
ten rungs of the animated ladder land on the ten rungs of the real one.

## The beat grids

A grid each, so the two do not sound like one video cut twice. Both beds are
by Sascha Ende (ende.app) under **CC BY 4.0**, which permits commercial use.
The author says attribution is no longer required, but a waiver posted on a
homepage is not a licence amendment and attribution is the licence's one term,
so credit them wherever a cut is posted -- the lines are in
`brag-output/share-copy.txt`.

| Cut | Track | Tempo | Trim | Reveal |
|---|---|---|---|---|
| `cut1` | Business Moves Vol. 1 | 120.19 BPM | 3.02s | 14.00s, beat 28 |
| `drill` | Business Moves Vol. 12 | 109.96 BPM | 8.74s | 14.19s, beat 26 |

The trim is never arbitrary. Each track's beats start a little way in, so
cutting there puts every beat on an exact multiple of video time -- and in
both cases a **strong cue** then lands on the reveal: vol-1's at 17.02s
becomes t=14.00, vol-12's at 22.93s becomes t=14.19. The edits were built
backwards from that, which is why the product arrives on a beat rather than
near one.

Vol. 12 is the slower of the two on purpose. The drill cut is a descent, and
its ten rungs fall one per beat at 0.546s; a 120 BPM pulse made the same
ladder read as a chase.

`build.sh` needs the source mp3s in `brag-output/` (`.music-source.mp3` and
`.music-source-drill.mp3`). They are not committed, because this repo is
public and redistributing someone's track is a different act from using it.

## Sound

`make-sfx.sh` synthesises all six cues with ffmpeg — tick, thud, riser, land,
tap, chime. Made rather than sourced for two reasons. Licensing: the SFX packs
we looked at either stated no terms, or shipped one pre-rendered track welded
to another block's timing. And fit: every cue is shorter than the
beat gap it sits in -- 0.50s on cut1, 0.546s on drill -- so nothing smears
into the next line.

## What is not used, and why

The Hyperframes registry has shader transitions (`flash-through-white`,
`glitch`, `cinematic-zoom` and others). They render fine here — WebGL works
under software GL — but each installs as a **catalog demo**: 1920x1080
landscape, dark themed, with its own branding panel and the prompt text baked
into the frame. They are references, not drop-in components. The act-change
flash in both cuts is eight lines of CSS and GSAP instead, and flashes to the
page colour lifted rather than to white, which would punch a hole in a warm
frame.

## Size

Rendered at **CRF 20**, overriding the default 16. Two things blow the file up
and both are avoidable:

- **Animated grain is ruinous.** Noise that changes every frame defeats
  inter-frame prediction outright. Drifting the grain took this cut from 4.7MB
  to **68MB** -- 26 Mbps -- for a difference nobody would notice. Held still,
  it is nearly free: every frame predicts it perfectly.
- **CRF 16 is near-lossless.** That was invisible while the frames were flat
  paper and expensive the moment a photographic backdrop arrived. Every
  platform re-encodes on upload, so those bits are spent twice and kept never.

## Gotchas that cost a render each

- **An `<audio>` without an `id` renders silent.** Nothing warns at playback;
  `hyperframes check` catches it, and `build.sh` re-checks the finished file
  with `volumedetect` and fails the build under -60 dB.
- **Sub-compositions resolve assets against the project root**, not their own
  directory. `assets/x.png`, never `../assets/x.png`.
- **A flex container makes every inline child its own anonymous item** and
  drops the whitespace between them — `<em>Every</em> row.` renders as
  "Everyrow." Each line wraps its content in one `<span class="t">`.
- **`hyperframes check` passing is not the same as it looking right.** Every
  real defect in these two cuts — the eaten space, a caption behind the
  product, a chain line struck through its own numbers — was found by
  `hyperframes snapshot` and looking at the frames.

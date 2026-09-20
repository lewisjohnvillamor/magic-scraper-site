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
| `drill` → `brag-drill.mp4` | the field is never on the list | merged detail columns |

## The beat grid

Both cuts sit on one grid, which is why they feel like a pair.

The bed is *Happy Beats / Business Moves Vol. 1* by Sascha Ende (ende.app),
**CC BY 4.0** — commercial use is explicitly permitted. The author says
attribution is no longer required, but a waiver posted on a homepage is not a
licence amendment and attribution is the licence's one term, so credit it
wherever a cut is posted. The line is in `brag-output/share-copy.txt`.

It runs at **120.19 BPM** with its beats starting at 3.02s. Trimming there puts
every beat on a clean 0.50s multiple of video time, and the track's strong cue
at 17.02s becomes **t=14.0s** — which is where both cuts reveal the product.
The edits were built backwards from that.

`build.sh` needs the source mp3 at `brag-output/.music-source.mp3` (or
`MUSIC_SRC=`). It is not committed, because this repo is public and
redistributing someone's track is a different act from using it.

## Sound

`make-sfx.sh` synthesises all six cues with ffmpeg — tick, thud, riser, land,
tap, chime. Made rather than sourced for two reasons. Licensing: the SFX packs
we looked at either stated no terms, or shipped one pre-rendered track welded
to another block's timing. And fit: each cue is cut shorter than the 0.50s gap
it sits in, so nothing smears into the next line.

## What is not used, and why

The Hyperframes registry has shader transitions (`flash-through-white`,
`glitch`, `cinematic-zoom` and others). They render fine here — WebGL works
under software GL — but each installs as a **catalog demo**: 1920x1080
landscape, dark themed, with its own branding panel and the prompt text baked
into the frame. They are references, not drop-in components. The act-change
flash in both cuts is eight lines of CSS and GSAP instead, and flashes to the
page colour lifted rather than to white, which would punch a hole in a warm
frame.

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

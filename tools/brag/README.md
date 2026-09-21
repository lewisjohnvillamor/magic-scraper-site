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

| Cut | Length | Argument | Payoff |
|---|---|---|---|
| `cut1` → `brag.mp4` | 20.5s | copying by hand, then one click | the crawl finished |
| `drill` → `brag-drill.mp4` | 20.7s | the field is never on the list | the chain builder, ten levels |
| `long` → `brag-long.mp4` | 44.2s | all three, then what each costs | crawl, chain, Changes, free/Pro |

**20 seconds is not a limit.** It is the `/brag` skill's house rule (15-25s)
and nothing technical -- Hyperframes renders any length. The real constraint is
material: at 20s there is room for one product moment, at 35s for three. The
long cut exists because the Changes tab is the thing nothing else in the
category does, and it could not be reached inside 20s without cutting the
argument that earns it.

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

| Cut | Track | Tempo | Trim | Reveal(s) |
|---|---|---|---|---|
| `cut1` | Business Moves Vol. 1 | 120.19 BPM | 3.02s | 14.00 |
| `drill` | Business Moves Vol. 12 | 109.96 BPM | 8.74s | 14.19 |
| `long` | Business Moves Vol. 11 | 114.84 BPM | 1.60s | 9.998, 17.893, 25.788 |

The long cut runs to 44.2s: its free/Pro card lands on the 30.525 cue and the
outro on 38.42.

The long cut is timed against the track's **detected beat array**, not an
idealised period. The two short cuts could use `n x beat` because their single
reveal happened to fall on one; across 35s the drift makes that wrong, and no
strong cue landed on an exact multiple of the nominal 0.5225s. Its lines sit on
real beats and its three payoffs on real strong cues.

The trim is never arbitrary. Each track's beats start a little way in, so
cutting there puts every beat on an exact multiple of video time -- and in
both cases a **strong cue** then lands on the reveal: vol-1's at 17.02s
becomes t=14.00, vol-12's at 22.93s becomes t=14.19. The edits were built
backwards from that, which is why the product arrives on a beat rather than
near one.

Vol. 12 is the slower of the two on purpose. The drill cut is a descent, and
its ten rungs fall one per beat at 0.546s; a 120 BPM pulse made the same
ladder read as a chase.

`build.sh` needs the source mp3s in `brag-output/`: `.music-source.mp3`,
`.music-source-drill.mp3` and `.music-source-long.mp3`. They are not
committed, because this repo is public and redistributing someone's track is a
different act from using it.

## The free/Pro boundary

Two of the long cut's three payoffs -- the ten-level chain and the Changes tab
-- are **Pro**. Showing them without saying so is how a free install turns
into a refund, so each carries the product's own Pro chip (popup.css
`--accent` #17703f on `--accent-soft` #eef9f2, `#bfe0cd` border -- not an
invented badge), arriving half a second after the product so the feature reads
first and its price second. A free/Pro card then closes the cut.

Every line on it is written against the build, because this boundary has been
got wrong in four separate places:

| Free | Pro |
|---|---|
| Detect, pick and export | Drill-down on **every** row |
| Crawl every page, no cap | Saved setups you can reuse |
| Get a dead run's rows back | Compare a run with the last |
| Drill-down on the first **3 rows** | Run a setup on a schedule |

`maxPages: 0` means Infinity and nothing in the crawl path checks `plan.pro`;
recovery has been free since 1.20.14; and `FREE_ROWS = 3` is a cap on **rows**
-- never on levels, chains, pages or depth. There are exactly four `plan.pro`
gates in the popup and all four are in the right column.

**Free goes first, and complete.** Lead with the paid list and the free tier
reads as a teaser for it, which is the opposite of true and is exactly the
mistake that had the Gumroad page selling a 3-page crawl cap that does not
exist.

## Posting them

Each cut carries a different bed, so **the music credit changes with the
file**. CC BY 4.0 requires attribution and an empty description puts the
upload outside its licence, so this is not optional:

| File | Credit |
|---|---|
| `brag.mp4` | Happy Beats / Business Moves **Vol. 1** |
| `brag-drill.mp4` | Happy Beats / Business Moves **Vol. 12** |
| `brag-long.mp4` | Happy Beats / Business Moves **Vol. 11** |

All by Sascha Ende (https://ende.app), CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/). The tracks carry no Content
ID, so YouTube's copyright check passes clean -- which is not the same as
being licensed, and is not a reason to skip the credit.

**On YouTube**, the long cut went up on 20 September 2026 as a Short, titled
*Scrape any web page to CSV without writing code*. Three things that are easy
to miss in that flow: the **made-for-kids** answer is mandatory and sits above
the fold, custom **thumbnails** must be uploaded or a frame is auto-picked,
and an upload stays **private** until the last step is changed.

Description order matters as much as it does in the cut itself: the first two
lines carry the pitch because YouTube truncates the rest behind "...more", and
**free is listed first and in full** for the same reason it is in the video.
Keep the "does not bypass logins, paywalls, rate limits or bot protection"
line -- it costs nothing and is what keeps the listing clear of the policy a
scraper is most likely to be pulled under.

Pick a thumbnail that is **not** a Pro moment. The frame at ~11.6s of the long
cut -- the crawl finishing -- promises something a free install actually
delivers; the chain builder does not.

**Pin a comment, and do not leave the slot empty.** On a Short the description
is close to invisible -- mobile shows the title and little else -- so the pinned
comment is the only place the free/Pro boundary reaches anyone who has not
tapped through, and the only slot that earns replies. Lead with the question,
carry the disclosure under it:

> What page do you keep copy-pasting out of? Reply with it and I'll tell you
> whether this handles it.
>
> (The ten-level chain and the Changes tab at the end are Pro. Everything
> before them is free -- no account, no time limit.)

**No URL in the pinned comment.** A link is the most common reason a comment is
silently held, and a held comment is worse than none; the description already
carries the link. Confirm it rendered by opening the Short signed out, because
a filtered comment still looks published to the account that wrote it.

**The store links go in a reply to the pinned comment** -- not in the pin, and
not as a second top-level comment. A reply sits under the pin where people
already are, and if the links get it held, the pin survives. A second top-level
comment on a Short with no engagement sinks under *Top* and is read by nobody.

> Chrome (also Brave, Opera, Vivaldi, Arc):
> https://chromewebstore.google.com/detail/magic-scraper/lcdaikobgjpakcgbkdedoapnckeobbck
>
> Edge:
> https://microsoftedge.microsoft.com/addons/detail/magic-scraper/palbdbeiidhladdgdmlolckafkjackfp
>
> Edge is a version behind while this build clears Microsoft's review -- the
> crawl and the drill chain work there today, the Changes tab lands with that
> update.

**The Edge caveat is exactly one feature wide.** Read off the 1.15.3 tree
rather than assumed: the chain builder is all there (`drillAddLevel`,
`drillNextLink`, `drillCost`, `drillDeeper`), so the long cut's ten-level
payoff is honest on Edge today. `tabDiff` is not -- the Changes tab arrived in
**1.20.7** -- so that is the one payoff Edge cannot keep yet, and the one the
caveat names. Guessing "the last two are Pro, so neither is on Edge" would have
been wrong in the direction that talks a working feature out of a sale. Drop
the caveat line when Edge serves 1.20.15.

Strip `utm_source=item-share-cb` if the URL came out of the store's Share
button. It labels the install as arriving from the store's own share widget,
which is the one place it did not; `utm_source=youtube` or nothing at all.

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

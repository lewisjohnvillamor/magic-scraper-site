# YouTube walkthrough

A ~3 minute narrated walkthrough of the real extension, docked as a side panel
beside the practice shop. The sources are kept here; the video is rebuilt from
them, not committed.

| Step | File | Makes |
|---|---|---|
| 1 | `record.mjs` | `walk2.webm` — one page at 1920x1080: the shop, with the extension's own `popup.html#panel` docked on the right, its row highlights on the page and the manual picker clicked on the page. Paints a coded beat marker at each step. |
| 2 | `narrate.py` + `narration.json` | one WAV per scene, Kokoro (Apache-2.0) voice `af_heart`, offline |
| 3 | `../walkthrough-music.py` | the music bed (generated, so no licence or credit) |
| 4 | `plan.py` | `plan.json` — reads the beat markers off the frames (the webm's clock drifts against wall time), finds the page loads between scenes, and sizes each scene to its footage or its narration, whichever is longer, holding a still where the voice needs more time |
| 5 | `remotion/` | the film: a browser window with a toolbar and step labels, camera zooms onto the panel or the page, the exported file opened as a spreadsheet, title and outro, narration over a ducked music bed |

```
python3 -m http.server 80 --bind 127.0.0.1 --directory <this repo>   # the shop, as shop.example.com
node tools/walkthrough/record.mjs
python3 tools/walkthrough/narrate.py <kokoro model dir> <scratch>/rem/public/vo
python3 tools/walkthrough-music.py <scratch>/rem/public/bed.wav 215
ffmpeg -i walk2.webm -c:v libx264 -crf 14 -g 15 -pix_fmt yuv420p -an <scratch>/rem/public/walk2.mp4
python3 tools/walkthrough/plan.py ffmpeg <scratch>/rem/public/walk2.mp4 walk2-beats.json <scratch>/rem/public/vo <scratch>/rem/src/plan.json
cd <scratch>/rem && npx remotion render src/index.ts Walkthrough out/walkthrough.mp4 --concurrency=4
```

The recorder needs the extension repo beside this one; it films the working
tree, so record after the release it shows is built.

Filming this found a real bug, fixed in the extension: a hand pick made from
the side panel never showed its shift-clicked column in the panel's table.

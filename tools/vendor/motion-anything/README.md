# Vendored from motion-anything

Two recipes, copied verbatim at commit `b016900` from
[nexu-io/motion-anything](https://github.com/nexu-io/motion-anything), used for the
kinetic captions in the short-form promo (`tools/record-tiktok.mjs`).

| File | Recipe |
| --- | --- |
| `kinetic-headline.js` / `.css` | `recipes/web/kinetic-headline` — splits a line into words or letters and staggers them in |
| `count-up.js` / `.css` | `recipes/web/count-up` — animates a number up to its value |

**Licence: Apache-2.0** — see `LICENSE`, which is motion-anything's own, copied with the code.

Both recipes are chosen deliberately: motion-anything's `ATTRIBUTION.md` records that 35 of
its `recipes/web/` entries are ports of [react-bits](https://reactbits.dev) effects,
redistributed under a separate permission from that author. These two carry `upstream: null` —
they are motion-anything's own work — so what is vendored here sits under Apache-2.0 alone,
with no second licence to honour in a commercial promo.

Copied rather than depended on: they are four files totalling ~9KB with no imports and no
build step, and the promo has to keep rendering years from now without a package resolving.

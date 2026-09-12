<div align="center">

<img src="docs/banner.png" alt="Magic Scraper — any web list, into a spreadsheet" width="820">

# magic-scraper-site

**The public site for the [Magic Scraper](https://github.com/lewisjohnvillamor/Magic-Data-Scraper-) Chrome extension — and the sandbox people practise scraping on.**

[![Live](https://img.shields.io/badge/live-magicscraper.app-4b3bd0?style=flat-square)](https://magicscraper.app)
[![Deploy](https://img.shields.io/badge/deploy-Cloudflare_Workers-f38020?style=flat-square&logo=cloudflare&logoColor=white)](https://developers.cloudflare.com/workers/static-assets/)
[![Chrome Web Store](https://img.shields.io/badge/Chrome_Web_Store-in_review-b4491f?style=flat-square&logo=googlechrome&logoColor=white)](https://magicscraper.app)
![Build](https://img.shields.io/badge/build_step-none-5d574a?style=flat-square)
![Sandbox](https://img.shields.io/badge/sandbox-141_pages-0f5c4a?style=flat-square)

</div>

---

It lives in its own repository so these pages can be public while the extension source stays
where it is.

| Page | Path |
|---|---|
| Landing | [`/`](https://magicscraper.app) |
| Privacy policy | [`/privacy`](https://magicscraper.app/privacy) |
| Terms | [`/terms`](https://magicscraper.app/terms) |
| Support | [`/support`](https://magicscraper.app/support) |
| After purchase | [`/thanks`](https://magicscraper.app/thanks) |
| Sandbox index | [`/demo/`](https://magicscraper.app/demo/) |

> [!IMPORTANT]
> **Type the URLs without the `.html`.** Cloudflare's asset server strips the extension and
> answers `/privacy.html` with a `307` to `/privacy`. Links inside the pages still use `.html`
> and get redirected, which is fine in a browser — but the Chrome Web Store *validates* its
> privacy-policy field, and a URL that answers with a redirect is an avoidable thing to have
> bounced.

## Publishing

Cloudflare Workers, assets-only. `wrangler.toml` declares `[assets]` with no `main`, which makes
this a static site with no Worker script — all it needs to be. Cloudflare's dashboard now routes
the Git integration through Workers rather than Pages, and `wrangler deploy` refuses to run
without that file.

> [!NOTE]
> GitHub Pages was the original plan and does not work here: it will not publish from a private
> repo on a free plan, and enabling it on this public repo still 404'd for anonymous visitors —
> which is exactly how a store reviewer opens it.

`.assetsignore` keeps `tools/`, `docs/`, `wrangler.toml`, `README.md` and `NOTICE` out of the
upload. They are repo housekeeping, not part of the site.

## The sandbox

<img src="docs/sandbox.png" alt="The four sandbox pages: card grid, plain table, infinite scroll, and a value outside the table" width="820">

`demo/` is a fictional shop, **Northwind Supply**, built to be scraped. Deliberately built like a
real storefront — sticky header, filter rail, rating stars, a footer full of link lists — because
a scraper that only works on a page containing nothing but the table has not been tested on
anything.

| Page | What it exercises |
|---|---|
| [`demo/catalogue.html`](https://magicscraper.app/demo/catalogue) | Card grid, six pages of nine, a Next button |
| [`demo/table.html`](https://magicscraper.app/demo/table) | A plain `<table>` with a header row — the easy case |
| [`demo/scroll.html`](https://magicscraper.app/demo/scroll) | Rows appended as you scroll, five batches then it stops |
| [`demo/awkward.html`](https://magicscraper.app/demo/awkward) | A discount belonging to every row but sitting outside the table |

### Three levels deep, on purpose

<img src="docs/drill.png" alt="Detail columns merged in beside the originals after a drill-down run" width="820">

Behind the catalogue: 120 product pages, each linking to one of eight maker pages, each linking
to a sourcing page. One hop proves nothing about chaining, so there are three.

Every product links to its maker through an identically-labelled **"About the maker →"**, not
through the maker's name. A chain confirmed on one row has to work on all of them, and linking
the name meant it only worked for products by that one maker.

## Keeping it in step

> [!WARNING]
> Two things here duplicate the extension, and **nothing enforces that they agree**.

- `privacy.html` is the same text as `docs/privacy.html` in the extension repository, in this
  site's styling. If the extension changes what it sends or stores, both change together — a
  policy that contradicts the code is worse than no policy, and store reviewers cross-reference
  them.
- The prices and limits quoted on the landing page come from `lib/license.js`.

## tools/

Not published. This is how the artwork is made, kept so it can be remade after a UI change
rather than re-improvised.

| Script | What it does |
|---|---|
| `record-promo.mjs` | Drives the real extension against the sandbox at 1080p and records it |
| `edit-promo.sh` | Cuts the landscape promo: title and end cards, timed captions, music bed |
| `edit-promo-vertical.sh` | The same footage recomposed to 9:16 for Reels and TikTok |
| `shoot-cards.mjs` · `shoot-cards-vertical.mjs` | Render `cards/*.html` to PNG |
| `shoot-readme.mjs` | Rebuilds `docs/sandbox.png` from the live sandbox |

`cards/` holds the title, caption and end cards as HTML.

> [!CAUTION]
> The end cards carry the site URL **in video**. A domain change means re-rendering the cards
> and re-encoding both promos — a find-and-replace across the repo will miss it entirely.

Every frame of `assets/promo.mp4` and `assets/promo-vertical.mp4` is the extension actually
running, and `assets/screenshot.png` is generated the same way. Nothing here is mocked up.

---

<div align="center">
<sub>Copyright 2026 Lewis John Villamor · <a href="https://magicscraper.app/support">support@magicscraper.app</a></sub>
</div>

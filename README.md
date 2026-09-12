# magic-scraper-site

The public site for the **Magic Scraper** Chrome extension, plus the sandbox people practise
scraping on.

Live at **[magicscraper.app](https://magicscraper.app)**.

It lives in its own repository so these pages can be public while the extension source stays
where it is.

| Page | Path |
|---|---|
| Landing | `/` |
| Privacy policy | `/privacy` |
| Terms | `/terms` |
| Support | `/support` |
| After purchase | `/thanks` |
| Sandbox index | `/demo/` |

**Without the `.html`.** Cloudflare's asset server strips the extension and answers
`/privacy.html` with a `307` to `/privacy`. Links inside the pages still use `.html` and are
redirected, which is fine in a browser — but anywhere a bare URL is *typed into a form*, use the
extensionless one. The Chrome Web Store validates its privacy-policy field, and a URL that
answers with a redirect is an avoidable thing to have bounced.

## Publishing

Cloudflare Workers, assets-only. `wrangler.toml` declares `[assets]` with no `main`, which makes
this a static site with no Worker script — all it needs to be. The Cloudflare dashboard now
routes the Git integration through Workers rather than Pages, and `wrangler deploy` refuses to
run without that file.

GitHub Pages was the original plan and does not work here: it will not publish from a private
repo on a free plan, and enabling it on this public repo still 404'd for anonymous visitors —
which is exactly how a store reviewer opens it.

`.assetsignore` keeps `tools/`, `wrangler.toml`, `README.md` and `NOTICE` out of the upload.
They are repo housekeeping, not part of the site.

## The sandbox

`demo/` is a fictional shop, **Northwind Supply**, built to be scraped. Deliberately built like a
real storefront — sticky header, filter rail, rating stars, a footer full of link lists — because
a scraper that only works on a page containing nothing but the table has not been tested on
anything.

| Page | What it exercises |
|---|---|
| `demo/catalogue.html` | Card grid, six pages of nine, a Next button |
| `demo/table.html` | A plain `<table>` with a header row — the easy case |
| `demo/scroll.html` | Rows appended as you scroll, five batches then it stops |
| `demo/awkward.html` | A discount belonging to every row but sitting outside the table |

Behind the catalogue: 120 product pages, each linking to one of eight maker pages, each linking
to a sourcing page. That is a **three-level drill chain**, and it is three levels on purpose —
one hop proves nothing about chaining.

Every product links to its maker through an identically-labelled *"About the maker →"*, not
through the maker's name. A chain confirmed on one row has to work on all of them, and linking
the name meant it only worked for products by that one maker.

## Keeping it in step

`privacy.html` is the same text as `docs/privacy.html` in the extension repository, in this
site's styling. **If the extension changes what it sends or stores, both change together.** A
policy that contradicts the code is worse than no policy, and store reviewers cross-reference
them.

The same goes for prices and limits quoted on the landing page: they are duplicated from
`lib/license.js`, and nothing enforces that they agree.

## tools/

Not published — this is how the artwork is made, kept so it can be remade after a UI change
rather than re-improvised.

- `record-promo.mjs` — drives the real extension against the sandbox at 1080p and records it.
  Every frame in the promos is the extension actually running.
- `edit-promo.sh` / `edit-promo-vertical.sh` — cut the landscape and 9:16 versions from that
  footage: title and end cards, timed caption overlays, and the music bed.
- `shoot-cards.mjs` / `shoot-cards-vertical.mjs` — render `cards/*.html` to PNG.
- `cards/` — the title, caption and end cards as HTML. The end cards carry the site URL, so a
  domain change means re-rendering and re-encoding, not just a find-and-replace.

`assets/screenshot.png` and the promos are generated this way, not mocked up.

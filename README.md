# magic-scraper-site

The public site for the **Magic Scraper** Chrome extension: landing page, privacy policy
and terms.

It lives in its own repository so the pages can be public — which GitHub Pages requires on a
free plan — while the extension source stays where it is.

| Page | URL |
|---|---|
| Landing | `https://lewisjohnvillamor.github.io/magic-scraper-site/` |
| Privacy policy | `https://lewisjohnvillamor.github.io/magic-scraper-site/privacy.html` |
| Terms | `https://lewisjohnvillamor.github.io/magic-scraper-site/terms.html` |

The privacy policy URL is the one the Chrome Web Store listing needs.

## Publishing

Settings → Pages → Source: **Deploy from a branch** → branch `main`, folder `/ (root)`.

## Keeping it in step

`privacy.html` is a copy of `docs/privacy.html` in the extension repository. If the extension
changes what it sends or stores, both files change together — a policy that contradicts the
code is worse than no policy, and store reviewers cross-reference them.

`assets/demo.webm` and `assets/screenshot.png` are generated from the extension's own test
harness, not mocked up.

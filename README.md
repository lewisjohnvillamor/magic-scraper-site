<div align="center">

<img src="docs/banner.png" alt="Magic Scraper — any web list, into a spreadsheet" width="820">

# Magic Scraper — site &amp; scrape sandbox

**[magicscraper.app](https://magicscraper.app)** — the home page for the Magic Scraper Chrome
extension, and a practice site anyone is welcome to scrape.

[![Live](https://img.shields.io/badge/live-magicscraper.app-4b3bd0?style=flat-square)](https://magicscraper.app)
[![Chrome Web Store](https://img.shields.io/badge/Chrome_Web_Store-in_review-b4491f?style=flat-square&logo=googlechrome&logoColor=white)](https://magicscraper.app)
[![Sandbox](https://img.shields.io/badge/sandbox-open_to_all-0f5c4a?style=flat-square)](https://magicscraper.app/demo/)
![Static](https://img.shields.io/badge/static_site-no_build_step-5d574a?style=flat-square)

</div>

---

## The extension

Magic Scraper finds the table or list on the page you are looking at and exports it to CSV, XLSX
or JSON. Detection, the manual picker and multi-page crawling are free; drill-down — opening the
page behind each row and merging its fields back in as extra columns — is the paid feature.

Everything runs in your browser. There is no server, no account, and nothing about the pages you
scrape is transmitted anywhere.

📄 [Privacy policy](https://magicscraper.app/privacy) · [Terms](https://magicscraper.app/terms) ·
[Support](https://magicscraper.app/support)

## The sandbox — please do scrape it

<img src="docs/sandbox.png" alt="The four sandbox pages: card grid, plain table, infinite scroll, and a value outside the table" width="820">

**[magicscraper.app/demo](https://magicscraper.app/demo/)** is a fictional shop, *Northwind
Supply*, built to be practised on. Nothing on it is real and nothing is rate-limited, so hammer
it as hard as you like — with this extension or any other.

It is deliberately built like a real storefront: sticky header, filter rail, rating stars, a
footer full of link lists. A scraper that only works on a page containing nothing but the table
has not been tested on anything.

| Page | What it exercises |
|---|---|
| [Catalogue](https://magicscraper.app/demo/catalogue) | Card grid, six pages of nine, a Next button |
| [Trade list](https://magicscraper.app/demo/table) | A plain `<table>` with a header row — the easy case |
| [New arrivals](https://magicscraper.app/demo/scroll) | Rows appended as you scroll, five batches then it stops |
| [Clearance](https://magicscraper.app/demo/awkward) | A discount belonging to every row but sitting outside the table |

### Three levels deep, on purpose

<img src="docs/drill.png" alt="Detail columns merged in beside the originals after a drill-down run" width="820">

Behind the catalogue: 120 product pages, each linking to one of eight maker pages, each linking
to a sourcing page. One hop proves nothing about chaining, so there are three.

Every product links to its maker through an identically-labelled **"About the maker →"** rather
than the maker's name — which is how real shops label such links, and what makes a chain
confirmed on one row work on all of them.

## Running it locally

No build step, no dependencies. Serve the folder:

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000>. Fonts are self-hosted, so it works offline too — a site whose
whole claim is *nothing leaves your machine* should not make your browser phone a third party to
render a headline.

Deployment is Cloudflare Workers, static assets only, on push to `main`.

---

<div align="center">
<sub>Copyright 2026 Lewis John Villamor · <a href="mailto:support@magicscraper.app">support@magicscraper.app</a></sub>
</div>

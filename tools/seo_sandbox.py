#!/usr/bin/env python3
"""Retitle the sandbox pages for search, and give them link previews.

Two problems this fixes.

The titles read "Shop the look - Northwind Supply". Northwind Supply does not
exist, so the strongest on-page signal each page has was spent on a brand
nobody can search for, while the terms these pages should rank for -- shadow
DOM, iframes, Load more, ARIA grids -- sat only in the description. The page
keeps its shop identity where that matters (the <h1>, the header, the markup
being scraped); the <title> is not visible on the page, and the black SANDBOX
banner across the top already tells a visitor what they are looking at.

And none of them carried Open Graph tags, so a link pasted into Reddit, Hacker
News or Discord -- which is exactly how a practice site travels -- rendered as
a bare URL.
"""

import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "demo")
SITE = "https://magicscraper.app"
OG_IMAGE = SITE + "/assets/screenshot.png"

# slug -> title. One shape across all of them: what the page tests, then the
# head term. Every one is under 60 characters, which is roughly where Google
# truncates.
TITLES = {
    "catalogue": "Paginated card grid &mdash; web scraping practice",
    "table":     "HTML table with a header row &mdash; web scraping practice",
    "scroll":    "Infinite scroll &mdash; web scraping practice",
    "awkward":   "A value outside the table &mdash; web scraping practice",
    "shadow":    "Shadow DOM &mdash; web scraping practice",
    "iframe":    "Table inside an iframe &mdash; web scraping practice",
    "feed":      "JSON-LD and microdata &mdash; web scraping practice",
    "reviews":   "Load more button &mdash; web scraping practice",
    "stock":     "ARIA data grid, no table &mdash; web scraping practice",
    "returns":   "Messy data to clean up &mdash; web scraping practice",
    "rates":     "Two tables on one page &mdash; web scraping practice",
    "bulk":      "2,000 rows across 40 pages &mdash; web scraping practice",
    "live":      "A page that changes every minute &mdash; web scraping practice",
}

# The catalogue's other five pages are noindex, so their titles are only ever
# read in a tab. They still get to say which page they are.
PAGED = {"page%d" % n: TITLES["catalogue"] + ", page %d" % n for n in range(2, 7)}
PAGED.update({"bulk%d" % n: TITLES["bulk"] + ", page %d" % n for n in range(2, 41)})


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def read(slug):
    with open(os.path.join(DEMO, slug + ".html"), encoding="utf-8") as fh:
        return fh.read()


def write(slug, src):
    with open(os.path.join(DEMO, slug + ".html"), "w", encoding="utf-8") as fh:
        fh.write(src)


def set_title(src, slug, title):
    out, n = re.subn(r"<title>.*?</title>", lambda m: "<title>%s</title>" % title,
                     src, count=1, flags=re.S)
    if not n:
        raise SystemExit("%s: no <title>" % slug)
    return out


def add_og(src, slug, title):
    if "og:title" in src:
        return src                      # already has one; leave it alone
    m = re.search(r'<meta name="description" content="(.*?)">', src, re.S)
    if not m:
        raise SystemExit("%s: no meta description to build a card from" % slug)
    desc = m.group(1)
    block = (
        '\n<meta property="og:type" content="website">'
        '\n<meta property="og:site_name" content="Magic Scraper">'
        '\n<meta property="og:url" content="%s/demo/%s">'
        '\n<meta property="og:title" content="%s">'
        '\n<meta property="og:description" content="%s">'
        '\n<meta property="og:image" content="%s">'
        '\n<meta name="twitter:card" content="summary_large_image">'
        % (SITE, slug, title, desc, OG_IMAGE)
    )
    out, n = re.subn(r"</head>", lambda m2: block + "</head>", src, count=1)
    if not n:
        raise SystemExit("%s: no </head>" % slug)
    return out


def main():
    for slug, title in sorted(TITLES.items()):
        src = add_og(set_title(read(slug), slug, title), slug, title)
        write(slug, src)
        print("%-10s %2d  %s" % (slug, len(plain(title)), plain(title)))

    for slug, title in sorted(PAGED.items()):
        # Titles only: these are noindex and carry no description to build a
        # card from, and nobody shares page 4 of a fictional catalogue.
        write(slug, set_title(read(slug), slug, title))
        print("%-10s %2d  %s  (title only, noindex)" % (slug, len(plain(title)), plain(title)))

    # The sandbox index already has its card; give it the site name the rest
    # now carry.
    src = read("index")
    if "og:site_name" not in src:
        src = src.replace('<meta property="og:type" content="website" />',
                          '<meta property="og:type" content="website" />\n'
                          '<meta property="og:site_name" content="Magic Scraper" />', 1)
        write("index", src)
        print("index      og:site_name added")


if __name__ == "__main__":
    main()

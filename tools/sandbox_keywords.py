#!/usr/bin/env python3
"""Lead every sandbox page with the search it should be found by.

People learning to scrape search for the job, not the technique: "warehouse
stock scraping", "price list table scraping". So each main page's <title>,
og:title and <h1> say that, and say what it practises. The header's fictional
shop name gives way to "Magic Scraper Sandbox", linking home, and the banner's
link to the extension says what it is: get it, free. The shop's products, makers
and prices stay as they are -- they are what is being scraped.

Run after make_sandbox_pages.py and seo_sandbox.py (which reads TITLES below).
Safe to run again.
"""
import glob, os, re

DEMO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'demo')

# slug -> (h1, title). Titles under 60 characters.
PAGES = {
    'catalogue': ('Product catalogue scraping', 'Product catalogue scraping: paginated cards to practise'),
    'table':     ('Price list table scraping', 'Price list table scraping: an HTML table to practise on'),
    'scroll':    ('Infinite scroll scraping', 'Infinite scroll scraping: new arrivals to practise on'),
    'awkward':   ('Clearance list scraping', 'Clearance list scraping: a value outside the table'),
    'shadow':    ('Shadow DOM scraping', 'Shadow DOM scraping: products inside a web component'),
    'iframe':    ('Iframe table scraping', 'Iframe table scraping: stock levels inside a frame'),
    'feed':      ('Product data scraping', 'Product data scraping: JSON-LD and microdata to practise'),
    'reviews':   ('Customer review scraping', 'Customer review scraping: a Load more button to practise'),
    'stock':     ('Warehouse stock scraping', 'Warehouse stock scraping: an ARIA data grid, no table'),
    'returns':   ('Returns log scraping', 'Returns log scraping: messy data to clean up'),
    'rates':     ('Delivery rates scraping', 'Delivery rates scraping: two tables on one page'),
    'bulk':      ('Bulk list scraping', 'Bulk list scraping: 2,000 rows across 40 pages'),
    'live':      ('Live price board scraping', 'Live price board scraping: data that changes every minute'),
}
TITLES = {k: v[1] for k, v in PAGES.items()}

BRAND_OLD = re.compile(r'<a class="brand" href="[^"]*">North<b>wind</b> <span>Supply</span></a>')
BRAND_NEW = '<a class="brand" href="../" title="Magic Scraper home">Magic <b>Scraper</b> <span>Sandbox</span></a>'
CTA_OLD = '<a href="../index.html">About the extension</a>'
CTA_NEW = '<a href="../index.html"><b>Get Magic Scraper free</b></a>'


def main():
    for path in glob.glob(os.path.join(DEMO, '*.html')):
        slug = os.path.basename(path)[:-5]
        s = open(path, encoding='utf-8').read()
        o = s
        s = BRAND_OLD.sub(BRAND_NEW, s)
        s = s.replace(CTA_OLD, CTA_NEW)
        if slug in PAGES:
            h1, title = PAGES[slug]
            s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, s, count=1, flags=re.S)
            s = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + title, s, count=1)
            s = re.sub(r'<h1>.*?</h1>', '<h1>%s</h1>' % h1, s, count=1, flags=re.S)
        if s != o:
            open(path, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    main()

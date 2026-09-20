#!/usr/bin/env python3
"""Generate the bulk trade list: 2,000 rows across 40 pages of 50.

Every other sandbox page tops out at 54 rows, so nothing there exercises the
things that only appear at scale -- the 500-row preview cap, the free tier's
5,000-row auto-save, a pager with a window rather than every page number, or
simply what a long crawl feels like. The extension's drill store is tested to
40,000 rows, but those rows are injected straight into the service worker;
until now no page produced them.

Rows are variants of the 120 real product pages -- a size or a finish, with its
own SKU and its own price -- so every row has a unique key for the comparison
feature to match on, and the product name still links to a detail page that
exists.

    python3 tools/make_bulk_pages.py
"""

import html
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DEMO = os.path.join(HERE, "..", "demo")

import make_sandbox_pages as S       # read_items, banner, header, FOOTER, money, stars

PER_PAGE = 50
PAGES = 40
TOTAL = PER_PAGE * PAGES

VARIANTS = [
    ("Small", 0.78), ("Medium", 1.0), ("Large", 1.35), ("Extra large", 1.7),
    ("Natural", 1.0), ("Charcoal", 1.06), ("Ecru", 1.03), ("Fern", 1.08),
    ("Ink", 1.11), ("Clay", 1.04), ("Sage", 1.07), ("Bone", 1.02),
    ("Rust", 1.09), ("Oat", 1.01), ("Slate", 1.12), ("Pair", 1.85),
    ("Set of four", 3.4), ("Set of six", 4.9), ("Trade pack", 8.2),
    ("Sample", 0.35),
]
STOCK = ["In stock", "In stock", "In stock", "Low stock", "Made to order", "Sold out"]
LEAD = ["ships today", "2–3 days", "1 week", "2 weeks", "4–6 weeks"]


def build_rows(items, rnd):
    rows = []
    for n in range(TOTAL):
        base = items[n % len(items)]
        vname, mult = VARIANTS[(n // len(items) + n) % len(VARIANTS)]
        price = round(max(4.0, base["price"] * mult) + rnd.uniform(-3, 3), 2)
        was = round(price * rnd.uniform(1.06, 1.42), 2) if rnd.random() < 0.34 else None
        rows.append({
            "sku": "NWT-%05d" % (10000 + n),
            "name": "%s — %s" % (base["name"], vname),
            "url": base["url"],
            "maker": base["maker"],
            "category": base["category"],
            "price": price,
            "was": was,
            "stock": STOCK[rnd.randrange(len(STOCK))],
            "lead": LEAD[rnd.randrange(len(LEAD))],
            "rating": round(rnd.uniform(3.1, 5.0), 1),
            "reviews": rnd.randrange(0, 420),
            "pack": rnd.choice([1, 1, 1, 2, 4, 6, 12]),
        })
    return rows


def pager(n):
    """A window, not forty numbers. Real shops do this, and it keeps the Next
    control the only reliable way through -- which is the thing being tested."""
    def href(k):
        return "bulk.html" if k == 1 else "bulk%d.html" % k
    out = ['<div class="pager">']
    if n > 1:
        out.append('<a class="prev" href="%s">&lsaquo; Prev</a>' % href(n - 1))
    lo, hi = max(1, n - 2), min(PAGES, n + 2)
    if lo > 1:
        out.append('<a href="%s">1</a>' % href(1))
        if lo > 2:
            out.append('<span class="gap">&hellip;</span>')
    for k in range(lo, hi + 1):
        out.append('<span class="on">%d</span>' % k if k == n
                   else '<a href="%s">%d</a>' % (href(k), k))
    if hi < PAGES:
        if hi < PAGES - 1:
            out.append('<span class="gap">&hellip;</span>')
        out.append('<a href="%s">%d</a>' % (href(PAGES), PAGES))
    if n < PAGES:
        out.append('<a class="next" id="next" href="%s">Next &rsaquo;</a>' % href(n + 1))
    out.append('</div>')
    return "".join(out)


def table(rows):
    head = ("<thead><tr><th>SKU</th><th>Product</th><th>Maker</th><th>Category</th>"
            "<th>Pack</th><th>Price</th><th>Was</th><th>Stock</th><th>Lead time</th>"
            "<th>Rating</th><th>Reviews</th></tr></thead>")
    body = []
    for r in rows:
        body.append(
            '<tr><td class="sku">%s</td>'
            '<td><a href="%s">%s</a></td>'
            '<td>%s</td><td>%s</td><td>%d</td>'
            '<td class="price">%s</td><td class="was">%s</td>'
            '<td>%s</td><td>%s</td>'
            '<td><span class="stars">%s</span> %s</td><td>%d</td></tr>'
            % (r["sku"], r["url"], html.escape(r["name"]),
               html.escape(r["maker"]), html.escape(r["category"]), r["pack"],
               S.money(r["price"]), S.money(r["was"]) if r["was"] else "",
               r["stock"], r["lead"], S.stars(r["rating"]), r["rating"], r["reviews"]))
    return ('<div class="tablewrap"><table class="data">' + head +
            "<tbody>" + "".join(body) + "</tbody></table></div>")


def main():
    rnd = random.Random(20260920)
    items = S.read_items()
    if len(items) < 120:
        raise SystemExit("expected 120 product pages, found %d" % len(items))
    rows = build_rows(items, rnd)

    skus = {r["sku"] for r in rows}
    if len(skus) != TOTAL:
        raise SystemExit("SKUs are not unique: %d rows, %d keys -- the comparison "
                         "feature needs one column that identifies a row" % (TOTAL, len(skus)))

    for n in range(1, PAGES + 1):
        chunk = rows[(n - 1) * PER_PAGE: n * PER_PAGE]
        fname = "bulk.html" if n == 1 else "bulk%d.html" % n
        first, last = (n - 1) * PER_PAGE + 1, n * PER_PAGE
        S.page(
            fname,
            "Bulk trade list" + ("" if n == 1 else ", page %d" % n),
            "Sandbox bulk list: %s rows across %d pages of %d. For testing a long "
            "crawl, the preview cap and auto-save." % (format(TOTAL, ","), PAGES, PER_PAGE),
            "A long one: <b>%s rows across %d pages</b>. Crawl it to see the preview cap "
            "and the auto-save." % (format(TOTAL, ","), PAGES),
            '<a href="catalogue.html">Home</a> / Bulk trade list',
            "Bulk trade list",
            "Showing %s&ndash;%s of %s variants." % (
                format(first, ","), format(last, ","), format(TOTAL, ",")),
            table(chunk) + pager(n),
            noindex=(n > 1),
        )

    print("\n%s rows across %d pages of %d, %d unique SKUs"
          % (format(TOTAL, ","), PAGES, PER_PAGE, len(skus)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fill in the six missing clearance product pages, and make the ten clearance
prices agree with the page behind them.

The clearance table links to item111 through item120. Only 111 to 114 were ever
generated, so six of its ten rows led to a 404 -- on a practice site whose whole
promise is that drill-down works. These six are built from the same skeleton as
the others, and the prices on all ten are reconciled with the -35% the clearance
callout advertises.
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "demo")

NEW = [
    (115, "Wool Bowl, Charcoal", "Tabletop", "Wool", 258.00,
     "Tessa Ruiz Studio", "tessa-ruiz-studio", "Portugal", "1.8 kg", "2–3 days", "1 year",
     4.2, 37, "In stock"),
    (116, "Linen Tray", "Tabletop", "Linen", 198.00,
     "Hallam & Co.", "hallam-co", "Portugal", "0.9 kg", "In stock, ships today", "1 year",
     3.8, 21, "In stock"),
    (117, "Cast Iron Jug, Charcoal", "Kitchen", "Cast Iron", 238.00,
     "Brock Forge", "brock-forge", "India", "3.6 kg", "1 week", "5 years",
     4.6, 64, "Low stock"),
    (118, "Oak Skillet, Fern", "Kitchen", "Oak", 526.00,
     "Oakleaf Mill", "oakleaf-mill", "Japan", "2.7 kg", "Made to order", "2 years",
     4.4, 12, "Made to order"),
    (119, "Smoked Glass Tray, Ecru", "Tabletop", "Smoked Glass", 457.00,
     "Mirren Ceramics", "mirren-ceramics", "Italy", "2.2 kg", "2 weeks", "1 year",
     3.6, 48, "In stock"),
    (120, "Ceramic Coaster Set, Natural", "Tabletop", "Ceramic", 321.00,
     "Aoyama Works", "aoyama-works", "Japan", "1.1 kg", "2–3 days", "1 year",
     4.9, 9, "In stock"),
]

# Clearance "Was" figures, straight off the clearance table.
WAS = {111: 429.00, 112: 488.00, 113: 434.00, 114: 526.00,
       115: 258.00, 116: 198.00, 117: 238.00, 118: 526.00, 119: 457.00, 120: 321.00}

DISCOUNT = 0.35


def stars(r):
    n = int(round(r))
    return "★" * n + "☆" * (5 - n)


def money(v):
    return "$%s" % format(v, ",.2f")


def read(n):
    with open(os.path.join(DEMO, "item%d.html" % n), encoding="utf-8") as fh:
        return fh.read()


def write(n, src):
    with open(os.path.join(DEMO, "item%d.html" % n), "w", encoding="utf-8") as fh:
        fh.write(src)


def related_block(category):
    """Borrow a finished 'More in <category>' block from a page that has one."""
    for n in range(1, 115):
        src = read(n)
        m = re.search(r'<div class="related"><h2>More in %s</h2>.*?</div></div>'
                      % re.escape(category), src, re.S)
        if m:
            return m.group(0)
    raise SystemExit("no related block found for %s" % category)


def build(spec):
    (n, name, cat, material, was, maker, maker_slug,
     origin, weight, lead, warranty, rating, reviews, avail) = spec
    now = round(was * (1 - DISCOUNT), 2)
    src = read(114)

    def sub(pattern, repl, flags=0):
        out, count = re.subn(pattern, lambda m: repl, src, count=1, flags=flags)
        if not count:
            raise SystemExit("item%d: pattern did not match: %s" % (n, pattern))
        return out

    src = sub(r"<title>.*?</title>", "<title>%s \u2014 Northwind Supply</title>" % name)
    src = sub(r'<a href="#">Tabletop</a> / Ash Coaster Set, Ink',
              '<a href="#">%s</a> / %s' % (cat, name))
    src = sub(r"<h1>Ash Coaster Set, Ink</h1>", "<h1>%s</h1>" % name)
    src = sub(r'<p class="maker">Mirren Ceramics &middot; Tabletop</p>',
              '<p class="maker">%s &middot; %s</p>' % (maker, cat))
    src = sub(r'<div class="pricing">.*?</div>',
              '<div class="pricing"><span class="now">%s</span>'
              '<span class="was">%s</span></div>' % (money(now), money(was)), re.S)
    src = sub(r'<span class="stars" style="color:var\(--gold\)">.*?</span> '
              r'[\d.]+ out of 5 &middot; \d+ reviews',
              '<span class="stars" style="color:var(--gold)">%s</span> '
              '%.1f out of 5 &middot; %d reviews' % (stars(rating), rating, reviews))
    src = sub(r'<p class="avail">In stock &middot; dispatch Made to order</p>',
              '<p class="avail">%s &middot; dispatch %s</p>' % (avail, lead))
    src = sub(r"<tr><th>SKU</th>.*?<th>Warranty</th><td>.*?</td></tr>",
              "<tr><th>SKU</th><td>NW-%d</td></tr><tr><th>Price</th><td>%s</td></tr>"
              "<tr><th>Availability</th><td>%s</td></tr>"
              "<tr><th>Material</th><td>%s</td></tr><tr><th>Made in</th><td>%s</td></tr>"
              "<tr><th>Weight</th><td>%s</td></tr>"
              "<tr><th>Lead time</th><td>%s</td></tr>"
              "<tr><th>Warranty</th><td>%s</td></tr>"
              % (1000 + n, money(now), avail, material, origin, weight, lead, warranty),
              re.S)
    src = sub(r'href="maker-mirren-ceramics\.html"', 'href="maker-%s.html"' % maker_slug)
    src = sub(r'<div class="related">.*?</div></div>', related_block(cat), re.S)

    # The gallery gradient ids are page-local, but keeping them distinct per
    # page makes the generated set easier to diff and debug.
    src = re.sub(r'id="g(\d+)"', lambda m: 'id="g%d_%s"' % (n, m.group(1)), src)
    src = re.sub(r'url\(#g(\d+)\)', lambda m: 'url(#g%d_%s)' % (n, m.group(1)), src)

    write(n, src)
    print("wrote demo/item%d.html  %s  %s (was %s)" % (n, name, money(now), money(was)))


def reconcile(n):
    """Make an existing clearance page's price match the clearance table."""
    src = read(n)
    was = WAS[n]
    now = round(was * (1 - DISCOUNT), 2)
    src = re.sub(r'<div class="pricing">.*?</div>',
                 '<div class="pricing"><span class="now">%s</span>'
                 '<span class="was">%s</span></div>' % (money(now), money(was)),
                 src, count=1, flags=re.S)
    src = re.sub(r'(<tr><th>Price</th><td>)\$[\d,.]+(</td></tr>)',
                 lambda m: m.group(1) + money(now) + m.group(2), src, count=1)
    write(n, src)
    print("reconciled demo/item%d.html to %s (was %s)" % (n, money(now), money(was)))


def main():
    for spec in NEW:
        build(spec)
    for n in (111, 112, 113, 114):
        reconcile(n)


if __name__ == "__main__":
    main()

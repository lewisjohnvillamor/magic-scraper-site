#!/usr/bin/env python3
"""Generate the seven harder sandbox pages for the Northwind Supply shop.

The original four (catalogue, table, scroll, awkward) cover the problems most
scrapers hit first. These cover the ones the extension's store listings claim
to handle and the ones a real shop actually ships: an open shadow root, a
same-origin iframe, schema.org markup, a Load-more button, an ARIA grid built
from divs, a table full of dirty data, and two tables on one page.

Product facts are read back out of the existing item pages rather than invented
again, so a row here matches the page it links to.
"""

import html
import json
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "demo")

# ---------------------------------------------------------------- source data

def read_items():
    """Pull the catalogue back out of the generated product pages."""
    items = []
    for i in range(1, 121):
        path = os.path.join(DEMO, "item%d.html" % i)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            src = fh.read()

        def spec(label):
            m = re.search(r"<th>%s</th><td>(.*?)</td>" % label, src)
            return html.unescape(m.group(1)) if m else ""

        title = re.search(r"<title>(.*?)</title>", src).group(1)
        name = html.unescape(re.split(r"\s+(?:\u2014|&mdash;)\s+", title)[0])
        mk = re.search(r'<p class="maker">(.*?) &middot; (.*?)</p>', src)
        rating = re.search(r"([\d.]+) out of 5 &middot; (\d+) reviews", src)
        items.append({
            "i": i,
            "url": "item%d.html" % i,
            "name": name,
            "maker": html.unescape(mk.group(1)) if mk else "",
            "category": mk.group(2) if mk else "",
            "price": float(spec("Price").replace("$", "").replace(",", "") or 0),
            "sku": spec("SKU"),
            "material": spec("Material"),
            "origin": spec("Made in"),
            "weight": spec("Weight"),
            "lead": spec("Lead time"),
            "warranty": spec("Warranty"),
            "avail": spec("Availability"),
            "rating": float(rating.group(1)) if rating else 4.0,
            "reviews": int(rating.group(2)) if rating else 0,
        })
    return items


# ------------------------------------------------------------- shared chrome

STRIP = ('<div class="strip">Free shipping on trade orders over <b>$400</b> '
         '&middot; Samples dispatched same day</div>')


def banner(hint):
    return ('<div class="sandbox"><div class="shell"><span class="tag">Sandbox</span>'
            '<b>Practice site for Magic Scraper.</b> ' + hint +
            ' <a href="index.html">All sandbox pages</a> &middot; '
            '<a href="../index.html">About the extension</a> &middot; '
            '<a href="../privacy.html">Privacy</a></div></div>')


def header():
    return ('<header class="site"><div class="shell bar">'
            '<a class="brand" href="catalogue.html">North<b>wind</b> <span>Supply</span></a>'
            '<nav><a href="catalogue.html">Catalogue</a><a href="table.html">Trade list</a>'
            '<a href="scroll.html">New arrivals</a><a href="awkward.html">Clearance</a></nav>'
            '<div class="tools"><input class="search" type="search" '
            'placeholder="Search 54 products" aria-label="Search">'
            '<a class="cart" href="#">Basket<b>0</b></a></div></div></header>')


FOOTER = ('<footer class="site"><div class="shell"><div class="cols">'
          '<div><h5>Northwind Supply</h5><p style="color:var(--ink-2);font-size:14px;margin:0">'
          'Household goods for people who keep things. Trade accounts welcome.</p>'
          '<div class="signup"><input type="email" placeholder="Email address" '
          'aria-label="Email address"><button type="button">Join</button></div></div>'
          '<div><h5>Shop</h5><ul>'
          '<li><a href="catalogue.html">Catalogue</a></li>'
          '<li><a href="table.html">Trade list</a></li>'
          '<li><a href="scroll.html">New arrivals</a></li>'
          '<li><a href="awkward.html">Clearance</a></li>'
          '<li><a href="shadow.html">Shop the look</a></li>'
          '<li><a href="#">Gift cards</a></li></ul></div>'
          '<div><h5>Help</h5><ul>'
          '<li><a href="rates.html">Delivery rates</a></li>'
          '<li><a href="iframe.html">Stock &amp; delivery</a></li>'
          '<li><a href="reviews.html">Customer reviews</a></li>'
          '<li><a href="returns.html">Returns log</a></li>'
          '<li><a href="#">Contact</a></li></ul></div>'
          '<div><h5>About</h5><ul>'
          '<li><a href="#">Our makers</a></li>'
          '<li><a href="stock.html">Warehouse stock</a></li>'
          '<li><a href="feed.html">Product data</a></li>'
          '<li><a href="#">Journal</a></li></ul></div></div>'
          '<div class="fine"><span>&copy; 2026 Northwind Supply</span>'
          '<a href="../terms.html">Terms</a><a href="../privacy.html">Privacy</a>'
          '<span class="sep">A fictional shop. Nothing here is for sale.</span>'
          '</div></div></footer>')


def page(fname, title, desc, hint, crumbs, h1, sub, body,
         slug=None, noindex=False, scripts="", head_extra=""):
    slug = slug or fname[:-5]
    robots = '<meta name="robots" content="noindex,follow">' if noindex else ""
    canon = "" if noindex else ('<link rel="canonical" href="https://magicscraper.app/demo/%s">' % slug)
    out = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>' + title + ' &mdash; Northwind Supply</title>'
        '<meta name="description" content="' + desc + '">'
        + robots + canon +
        '<link rel="icon" href="../assets/icon.png">\n'
        '<link rel="stylesheet" href="store.css">' + head_extra + '</head><body>'
        + banner(hint) + STRIP + header() +
        '<div class="shell"><p class="crumbs">' + crumbs + '</p>'
        '<div class="head"><h1>' + h1 + '</h1><p>' + sub + '</p></div>'
        + body + '</div>' + FOOTER + scripts + '</body></html>'
    )
    with open(os.path.join(DEMO, fname), "w", encoding="utf-8") as fh:
        fh.write(out)
    print("wrote demo/%s" % fname)


def stars(r):
    full = int(round(r))
    return "★" * full + "☆" * (5 - full)


def money(v):
    return "$%s" % format(v, ",.2f")


# ------------------------------------------------------- 1. open shadow root

def build_shadow(items, rnd):
    picks = rnd.sample(items, 12)
    data = [{"name": p["name"], "maker": p["maker"], "price": p["price"],
             "sku": p["sku"], "rating": p["rating"], "url": p["url"],
             "category": p["category"],
             "hue": (p["i"] * 37) % 360, "shape": p["i"] % 4} for p in picks]

    body = (
        '<div style="padding-bottom:70px">'
        '<p class="lede">The gallery below is a web component. Its markup lives in an open '
        'shadow root rather than in the page, so <code>document.querySelector</code> will not '
        'find a single product in it &mdash; and neither will a scraper that stops at the '
        'light DOM.</p>'
        '<nw-showcase></nw-showcase>'
        '<p class="aside-note">Nothing is hidden from you here: open DevTools and you will see '
        '<code>#shadow-root (open)</code> under <code>&lt;nw-showcase&gt;</code>. A closed root '
        'would be a different matter, and neither this extension nor any other can read one.</p>'
        '</div>'
    )

    scripts = (
        '<script id="showcase-data" type="application/json">' + json.dumps(data) + '</script>'
        '<script>\n'
        '(function () {\n'
        '  var CSS = ".g{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:26px 22px}"\n'
        '    + "@media(max-width:820px){.g{grid-template-columns:repeat(3,minmax(0,1fr))}}"\n'
        '    + "@media(max-width:640px){.g{grid-template-columns:repeat(2,minmax(0,1fr))}}"\n'
        '    + "article{font:inherit}"\n'
        '    + ".shot{display:block;aspect-ratio:4/3;border-radius:10px;overflow:hidden;"\n'
        '    + "background:#f6f7f9;margin-bottom:12px}"\n'
        '    + ".shot svg{width:100%;height:100%;display:block}"\n'
        '    + "h3{margin:0 0 3px;font-size:15px;font-weight:600}"\n'
        '    + "h3 a{color:inherit;text-decoration:none}h3 a:hover{text-decoration:underline}"\n'
        '    + ".maker{color:#8d93a1;font-size:13px;margin:0 0 6px}"\n'
        '    + ".row{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}"\n'
        '    + ".price{font-weight:700}.stars{color:#d8a33a;font-size:12px}"\n'
        '    + ".stars em{color:#8d93a1;font-style:normal;margin-left:4px}"\n'
        '    + ".sku{font-size:12px;color:#8d93a1;margin:2px 0 0}";\n'
        '\n'
        '  function star(r) {\n'
        '    var n = Math.round(r), s = "";\n'
        '    for (var i = 0; i < 5; i++) s += i < n ? "\\u2605" : "\\u2606";\n'
        '    return s;\n'
        '  }\n'
        '\n'
        '  var SHAPES = [\n'
        '    \'<circle cx="200" cy="150" r="74" fill="H" opacity=".26"/>\',\n'
        '    \'<rect x="132" y="82" width="136" height="136" rx="10" fill="H" opacity=".26"/>\',\n'
        '    \'<path d="M158 96h84l-12 104a30 30 0 0 1-30 26h0a30 30 0 0 1-30-26z" fill="H" opacity=".26"/>\',\n'
        '    \'<path d="M126 226V150a74 74 0 0 1 148 0v76z" fill="H" opacity=".26"/>\'\n'
        '  ];\n'
        '\n'
        '  function shot(p) {\n'
        '    var solid = "hsl(" + p.hue + " 30% 38%)";\n'
        '    return \'<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" \'\n'
        '      + \'role="img" aria-label="Product photograph">\'\n'
        '      + \'<defs><linearGradient id="s\' + p.sku + \'" x1="0" y1="0" x2="1" y2="1">\'\n'
        '      + \'<stop offset="0" stop-color="hsl(\' + p.hue + \' 36% 92%)"/>\'\n'
        '      + \'<stop offset="1" stop-color="hsl(\' + ((p.hue + 28) % 360) + \' 30% 83%)"/>\'\n'
        '      + \'</linearGradient></defs>\'\n'
        '      + \'<rect width="400" height="300" fill="url(#s\' + p.sku + \')"/>\'\n'
        '      + SHAPES[p.shape].split("H").join(solid)\n'
        '      + "</svg>";\n'
        '  }\n'
        '\n'
        '  function card(p) {\n'
        '    return "<article>"\n'
        '      + \'<a class="shot" href="\' + p.url + \'" aria-hidden="true" tabindex="-1">\'\n'
        '      + shot(p) + "</a>"\n'
        '      + "<h3><a href=\\"" + p.url + "\\">" + p.name + "</a></h3>"\n'
        '      + \'<p class="maker">\' + p.maker + " \\u00b7 " + p.category + "</p>"\n'
        '      + \'<div class="row"><span class="price">$\' + p.price.toFixed(2) + "</span>"\n'
        '      + \'<span class="stars">\' + star(p.rating) + "<em>" + p.rating.toFixed(1) + "</em></span></div>"\n'
        '      + \'<p class="sku">\' + p.sku + "</p></article>";\n'
        '  }\n'
        '\n'
        '  // An open shadow root: readable by anything that walks into it on purpose,\n'
        '  // invisible to anything that only queries the light DOM.\n'
        '  class Showcase extends HTMLElement {\n'
        '    connectedCallback() {\n'
        '      if (this.shadowRoot) return;\n'
        '      const root = this.attachShadow({ mode: "open" });\n'
        '      const rows = JSON.parse(document.getElementById("showcase-data").textContent);\n'
        '      root.innerHTML = "<style>" + CSS + "</style>"\n'
        '        + \'<div class="g">\' + rows.map(card).join("") + "</div>";\n'
        '    }\n'
        '  }\n'
        '  customElements.define("nw-showcase", Showcase);\n'
        '})();\n'
        '</script>'
    )

    page("shadow.html", "Shop the look",
         "Sandbox page whose products live inside an open shadow root, so a scraper that only "
         "queries the light DOM finds nothing. Twelve products, free to scrape.",
         "The twelve products below are inside an <b>open shadow root</b>, not the page. "
         "Detection should still find them.",
         '<a href="catalogue.html">Home</a> / Shop the look',
         "Shop the look",
         "Twelve pieces our buyers picked this month.",
         body, scripts=scripts)
    return len(data)


# ------------------------------------------------------ 2. same-origin iframe

def build_iframe(items, rnd):
    picks = rnd.sample(items, 24)
    rows = []
    for p in picks:
        rows.append(
            '<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td>'
            '<td class="num">%d</td><td class="num">%d</td><td>%s</td></tr>' % (
                p["url"], html.escape(p["name"]), p["sku"], html.escape(p["maker"]),
                rnd.randint(0, 240), rnd.randint(0, 80), p["lead"] or "2\u20133 days"))

    frame_body = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Live stock levels</title>'
        '<meta name="robots" content="noindex,nofollow">'
        '<link rel="stylesheet" href="store.css"></head>'
        '<body style="padding:18px">'
        '<p style="margin:0 0 14px;font-size:13px;color:var(--ink-3)">'
        'Warehouse feed &middot; refreshed 06:00 daily. This document is the contents of the '
        'frame on <a href="iframe.html">Stock &amp; delivery</a>.</p>'
        '<div class="table-scroll"><table class="data"><thead><tr><th>Product</th><th>SKU</th>'
        '<th>Maker</th><th class="num">Wigan</th><th class="num">Rotterdam</th>'
        '<th>Next dispatch</th></tr></thead><tbody>\n' + "\n".join(rows) +
        '\n</tbody></table></div></body></html>'
    )
    with open(os.path.join(DEMO, "iframe-stock.html"), "w", encoding="utf-8") as fh:
        fh.write(frame_body)
    print("wrote demo/iframe-stock.html")

    body = (
        '<div style="padding-bottom:70px">'
        '<p class="lede">Stock is held in two warehouses and the numbers below come straight '
        'from the warehouse system, which serves its own page. We embed it rather than copy '
        'it, so what you see is what the system says.</p>'
        '<iframe class="frame" src="iframe-stock.html" title="Live stock levels" '
        'loading="lazy"></iframe>'
        '<p class="aside-note">The table is in a <b>same-origin iframe</b>. It is a separate '
        'document with its own DOM: nothing in it is reachable from this page\'s '
        '<code>document</code>, and a scraper pointed at this URL alone will report that there '
        'is no table here. Same origin is the condition &mdash; a frame served from another '
        'domain is closed to every extension, by the browser, not by choice.</p>'
        '<h2 class="sub">Delivery once it leaves us</h2>'
        '<p class="lede">Wigan ships next working day within the UK. Rotterdam covers the EU '
        'and ships in two. Full prices are on <a href="rates.html">delivery rates</a>.</p>'
        '</div>'
    )
    page("iframe.html", "Stock &amp; delivery",
         "Sandbox page with its stock table inside a same-origin iframe &mdash; a separate "
         "document a page-level scraper will miss. 24 rows, free to scrape.",
         "The stock table is inside a <b>same-origin iframe</b>. Detection has to step into "
         "the frame to find it.",
         '<a href="catalogue.html">Home</a> / Help / Stock &amp; delivery',
         "Stock &amp; delivery",
         "Live warehouse levels, refreshed every morning at 06:00.",
         body)
    return len(rows)


# ------------------------------------------- 3. schema.org JSON-LD + microdata

def build_feed(items, rnd):
    picks = sorted(rnd.sample(items, 20), key=lambda p: p["sku"])

    cards, ld = [], []
    for p in picks:
        avail = ("https://schema.org/InStock" if p["avail"].lower().startswith("in stock")
                 else "https://schema.org/PreOrder")
        cards.append(
            '<div class="feedrow" itemscope itemtype="https://schema.org/Product">'
            '<h3 itemprop="name">%s</h3>'
            '<dl>'
            '<dt>SKU</dt><dd itemprop="sku">%s</dd>'
            '<dt>Brand</dt><dd itemprop="brand" itemscope itemtype="https://schema.org/Brand">'
            '<span itemprop="name">%s</span></dd>'
            '<dt>Category</dt><dd itemprop="category">%s</dd>'
            '<dt>Material</dt><dd itemprop="material">%s</dd>'
            '<dt>Weight</dt><dd>%s</dd>'
            '<dt>Price</dt>'
            '<dd itemprop="offers" itemscope itemtype="https://schema.org/Offer">'
            '<span itemprop="priceCurrency" content="USD">$</span>'
            '<span itemprop="price" content="%.2f">%s</span>'
            '<link itemprop="availability" href="%s">'
            '<meta itemprop="url" content="https://magicscraper.app/demo/%s">'
            '</dd>'
            '<dt>Rating</dt>'
            '<dd itemprop="aggregateRating" itemscope itemtype="https://schema.org/AggregateRating">'
            '<span itemprop="ratingValue">%.1f</span> from '
            '<span itemprop="reviewCount">%d</span> reviews</dd>'
            '</dl>'
            '<p class="go"><a itemprop="url" href="%s">Product page &rarr;</a></p>'
            '</div>' % (
                html.escape(p["name"]), p["sku"], html.escape(p["maker"]), p["category"],
                p["material"], p["weight"], p["price"], format(p["price"], ",.2f"),
                avail, p["url"][:-5], p["rating"], p["reviews"], p["url"]))

        ld.append({
            "@type": "Product",
            "name": p["name"],
            "sku": p["sku"],
            "category": p["category"],
            "material": p["material"],
            "brand": {"@type": "Brand", "name": p["maker"]},
            "url": "https://magicscraper.app/demo/" + p["url"][:-5],
            "offers": {"@type": "Offer", "price": "%.2f" % p["price"],
                       "priceCurrency": "USD", "availability": avail},
            "aggregateRating": {"@type": "AggregateRating",
                                "ratingValue": "%.1f" % p["rating"],
                                "reviewCount": p["reviews"]},
        })

    feed = {"@context": "https://schema.org", "@type": "ItemList",
            "name": "Northwind Supply partner feed (sample)",
            "numberOfItems": len(ld),
            "itemListElement": [{"@type": "ListItem", "position": n + 1, "item": it}
                                for n, it in enumerate(ld)]}

    body = (
        '<div style="padding-bottom:70px">'
        '<p class="lede">Stockists and price-comparison partners take this feed rather than '
        'scraping the catalogue. Every product below is marked up twice: once as '
        '<b>microdata</b> in the HTML, and once as <b>JSON-LD</b> in the page head. Same twenty '
        'products, two ways of reading them.</p>'
        '<div class="feed">' + "".join(cards) + '</div>'
        '<p class="aside-note">If your scraper reads structured data, it should get all twenty '
        'without touching a selector &mdash; and it should notice that the JSON-LD and the '
        'microdata agree. If it reads the rendered text instead, the <code>content</code> '
        'attributes are where the machine-readable price hides: <code>399.00</code>, not '
        '<code>$399.00</code>.</p>'
        '</div>'
    )

    head_extra = ('<script type="application/ld+json">' +
                  json.dumps(feed, indent=None, ensure_ascii=False) + '</script>')

    # noindex on purpose: this is fictional stock with prices and availability
    # on it. Marked up that thoroughly and left indexable, it is exactly the
    # shape of a structured-data spam signal, and the practice value does not
    # depend on being in anyone's index.
    page("feed.html", "Product data",
         "Sandbox page with twenty products marked up in both schema.org JSON-LD and microdata, "
         "for testing structured-data extraction.",
         "Twenty products marked up as <b>JSON-LD and microdata</b> at the same time.",
         '<a href="catalogue.html">Home</a> / About / Product data',
         "Product data",
         "The sample feed we hand to stockists. Twenty lines, updated nightly.",
         body, noindex=True, head_extra=head_extra)
    return len(picks)


# --------------------------------------------------------- 4. Load more button

FIRST = ["Priya", "Tom", "Marguerite", "Daniel", "Aoife", "Ravi", "Hannah", "Joachim",
         "Lena", "Samuel", "Bea", "Oliver", "Nadia", "Callum", "Ines", "Piotr",
         "Grace", "Tobias", "Mei", "Fergus", "Rosa", "Evan", "Saskia", "Léon"]
LAST = list("ABCDEFGHJKLMNPRSTVWY")
GOOD = [
    "Arrived a day early and better finished than the photographs suggest.",
    "Third one of these I have bought. They do not warp.",
    "Handsome, heavy, and the colour is closer to the second photo than the first.",
    "Bought for a rental flat and it has survived two tenancies.",
    "Ordered on a Thursday, here Monday. No notes.",
    "Replaced a supermarket one and the difference is not subtle.",
    "Good weight in the hand. The seam is neater than I expected at this price.",
    "Second one, for the other end of the table. Worth it.",
    "Exactly what was described, which is rarer than it should be.",
    "My mother asked where it came from, which is the only review that counts.",
]
FAIR = [
    "Does the job. Slightly smaller than I pictured from the dimensions.",
    "Packaging was excessive but nothing was broken, so I will not complain.",
    "It is fine. I would buy it again but I would not write home about it.",
    "Lovely object. Wish it came in the darker finish as standard.",
    "Good, though the lead time was a week longer than quoted.",
    "No complaints about the item. The courier was another matter.",
    "Solid enough. The photographs flatter the finish a little.",
]
POOR = [
    "The finish marks easily if you are careless with it, and I was careless with it.",
    "Arrived chipped. Replaced without argument, but it should not have shipped like that.",
    "Smaller and lighter than the listing led me to expect. Sent it back.",
    "Two weeks late and nobody told me until I asked.",
    "Handsome, but it has not survived ordinary use.",
]


def build_reviews(items, rnd):
    picks = [rnd.choice(items) for _ in range(48)]
    pools = {"good": list(GOOD), "fair": list(FAIR), "poor": list(POOR)}
    for v in pools.values():
        rnd.shuffle(v)
    cursor = {"good": 0, "fair": 0, "poor": 0}

    def body_for(r):
        key = "good" if r >= 4 else "fair" if r == 3 else "poor"
        pool = pools[key]
        out = pool[cursor[key] % len(pool)]
        cursor[key] += 1
        return out

    # Newest first, because that is what the page says and what the sort control
    # is set to. Working backwards from the most recent one keeps it honest.
    MONTHS = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September"]
    day, month = 12, 8          # 12 September 2026

    entries = []
    for n, p in enumerate(picks):
        r = rnd.choice([3, 4, 4, 4, 5, 5, 5, 2])
        entries.append({
            "who": "%s %s." % (rnd.choice(FIRST), rnd.choice(LAST)),
            "stars": stars(r), "rating": r,
            "when": "%d %s 2026" % (day, MONTHS[month]),
            "item": p["name"], "url": p["url"],
            "verified": rnd.random() < 0.72,
            "body": body_for(r),
        })
        day -= rnd.choice([1, 2, 2, 3, 4, 5])
        while day < 1:
            month -= 1
            day += 28 if month == 1 else 30

    def render(e):
        return ('<article class="rev"><div class="top">'
                '<span class="who">%s</span>'
                '<span class="stars" title="%d out of 5">%s</span>'
                '<span class="when">%s</span>'
                '<span class="item">on <a href="%s">%s</a></span>%s</div>'
                '<p>%s</p></article>' % (
                    html.escape(e["who"]), e["rating"], e["stars"], e["when"],
                    e["url"], html.escape(e["item"]),
                    '<span class="ok">Verified purchase</span>' if e["verified"] else "",
                    e["body"]))

    first = "".join(render(e) for e in entries[:12])
    rest = [entries[i:i + 12] for i in range(12, 48, 12)]

    avg = sum(e["rating"] for e in entries) / float(len(entries))
    body = (
        '<div style="padding-bottom:70px">'
        '<div class="toolbar"><span>%d reviews &middot; %.1f average</span>' % (len(entries), avg) +
        '<span class="right">Sort <select><option>Most recent</option>'
        '<option>Highest rated</option></select></span></div>'
        '<div id="reviews">' + first + '</div>'
        '<button class="more" id="more" type="button">Load more reviews</button>'
        '<p id="done" class="aside-note" hidden></p>'
        '</div>'
    )

    payload = [[render(e) for e in batch] for batch in rest]
    scripts = (
        '<script id="review-batches" type="application/json">' +
        json.dumps(payload) + '</script>'
        '<script>\n'
        '(function () {\n'
        '  var batches = JSON.parse(document.getElementById("review-batches").textContent);\n'
        '  var list = document.getElementById("reviews");\n'
        '  var btn = document.getElementById("more");\n'
        '  var done = document.getElementById("done");\n'
        '  var n = 0;\n'
        '  btn.addEventListener("click", function () {\n'
        '    // A short delay, because a real endpoint is never instant and a scraper\n'
        '    // that clicks without waiting is the bug this page is here to catch.\n'
        '    btn.disabled = true;\n'
        '    btn.textContent = "Loading\\u2026";\n'
        '    setTimeout(function () {\n'
        '      list.insertAdjacentHTML("beforeend", batches[n].join(""));\n'
        '      n++;\n'
        '      if (n >= batches.length) {\n'
        '        btn.remove();\n'
        '        done.textContent = "That is all 48 reviews.";\n'
        '        done.hidden = false;\n'
        '        return;\n'
        '      }\n'
        '      btn.disabled = false;\n'
        '      btn.textContent = "Load more reviews";\n'
        '    }, 450);\n'
        '  });\n'
        '})();\n'
        '</script>'
    )

    page("reviews.html", "Customer reviews",
         "Sandbox page with a Load more button rather than pagination or infinite scroll: "
         "12 reviews on load, 48 after three clicks.",
         "Twelve on load, then a <b>Load more</b> button &mdash; three clicks to reach all 48. "
         "Not pagination, and not infinite scroll.",
         '<a href="catalogue.html">Home</a> / Help / Customer reviews',
         "Customer reviews",
         "What people said, newest first. Verified purchases are marked.",
         body, scripts=scripts)
    return 12, len(entries)


# ------------------------------------------- 5. ARIA grid built out of divs

def build_stock(items, rnd):
    picks = rnd.sample(items, 30)
    cols = ["Product", "SKU", "Bin", "Wigan", "Rotterdam", "Status"]
    rows = []
    for p in picks:
        wigan = rnd.randint(0, 260)
        rott = rnd.randint(0, 90)
        total = wigan + rott
        status = ("Out of stock" if total == 0 else
                  "Reorder" if total < 25 else "Healthy")
        rows.append(
            '<div role="row">'
            '<span role="cell"><a href="%s">%s</a></span>'
            '<span role="cell">%s</span>'
            '<span role="cell">%s-%02d-%s</span>'
            '<span role="cell" class="num">%d</span>'
            '<span role="cell" class="num">%d</span>'
            '<span role="cell">%s</span>'
            '</div>' % (p["url"], html.escape(p["name"]), p["sku"],
                        rnd.choice("ABCDEF"), rnd.randint(1, 40), rnd.choice("LR"),
                        wigan, rott, status))

    head = "".join('<span role="columnheader"%s>%s</span>'
                   % (' class="num"' if c in ("Wigan", "Rotterdam") else "", c)
                   for c in cols)

    body = (
        '<div style="padding-bottom:70px">'
        '<div class="toolbar"><span>30 lines &middot; bin locations as of 06:00</span>'
        '<span class="right">View <select><option>Grid</option><option>List</option>'
        '</select></span></div>'
        '<div class="table-scroll"><div class="agrid" role="table" '
        'aria-label="Warehouse stock by bin">'
        '<div role="rowgroup"><div role="row">' + head + '</div></div>'
        '<div role="rowgroup">' + "".join(rows) + '</div>'
        '</div></div>'
        '<p class="aside-note">There is no <code>&lt;table&gt;</code> on this page. It is '
        '<code>&lt;div&gt;</code> elements carrying <code>role="table"</code>, '
        '<code>role="row"</code> and <code>role="cell"</code> &mdash; which is how most '
        'JavaScript data grids render, and why a scraper that looks for '
        '<code>table tr td</code> comes back with nothing on half the web apps you will '
        'point it at.</p>'
        '</div>'
    )
    page("stock.html", "Warehouse stock",
         "Sandbox data grid built from divs with ARIA roles instead of a table element. "
         "Thirty rows, six columns, no &lt;table&gt; on the page.",
         "No <code>&lt;table&gt;</code> here: 30 rows of <code>role=\"row\"</code> divs, the "
         "way a JavaScript data grid renders.",
         '<a href="catalogue.html">Home</a> / About / Warehouse stock',
         "Warehouse stock",
         "Bin-level counts across both warehouses. Internal view, published for trade accounts.",
         body)
    return len(rows), len(cols)


# ------------------------------------------------------------ 6. messy data

def build_returns(items, rnd):
    picks = rnd.sample(items, 22)
    reasons = ["Damaged in transit", "Wrong item sent", "Changed mind",
               "Faulty &mdash; hairline crack", "Ordered 2, wanted 1",
               "Colour not as shown", "", "Arrived late &amp; refused",
               "Duplicate order", "N/A", "&mdash;"]
    statuses = ["Refunded", "refunded", "REFUNDED", "Pending", "pending",
                "Credit note", "Rejected", ""]

    MONTHS_IN = [3, 7, 1, 9, 4, 6, 2, 8, 5, 7, 3, 9, 1, 5, 8, 2, 6, 4, 9, 3, 7, 1, 4, 8]

    def a_date(n):
        d = 1 + (n * 5) % 27
        m = MONTHS_IN[n % len(MONTHS_IN)]
        if n % 3 == 0:
            return "2026-%02d-%02d" % (m, d)
        if n % 3 == 1:
            return "%02d/%02d/2026" % (d, m)
        return "%d %s 2026" % (d, ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                   "Jul", "Aug", "Sep"][m - 1])

    def a_refund(n, price):
        if n % 7 == 3:
            return ""
        if n % 7 == 5:
            return "&mdash;"
        if n % 5 == 0:
            return "USD %d" % int(price)
        if n % 4 == 0:
            return "%s" % format(price, ",.2f")
        return "$%s" % format(price, ",.2f")

    rows, refs = [], []
    for n, p in enumerate(picks):
        ref = "RT-2026-%04d" % (1180 + n * 3)
        refs.append(ref)
        rows.append({
            "ref": ref,
            "date": a_date(n),
            "name": html.escape(p["name"]) + ("&nbsp;" if n % 6 == 2 else ""),
            "sku": "" if n % 9 == 4 else p["sku"],
            "reason": reasons[n % len(reasons)],
            "qty": "" if n % 11 == 7 else str(rnd.randint(1, 4)),
            "refund": a_refund(n, p["price"]),
            "status": statuses[n % len(statuses)],
        })

    # Two rows filed twice, which is what happens when a warehouse hand and the
    # returns desk both log the same parcel. Identical, not merely similar.
    dupes = [dict(rows[4]), dict(rows[13])]
    rows.insert(9, dupes[0])
    rows.append(dupes[1])

    tr = []
    for r in rows:
        tr.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                  '<td class="num">%s</td><td class="num">%s</td><td>%s</td></tr>' % (
                      r["ref"], r["date"], r["name"], r["sku"], r["reason"],
                      r["qty"], r["refund"], r["status"]))

    empties = sum(1 for r in rows for k in ("sku", "reason", "qty", "refund", "status")
                  if r[k] == "")
    blank_marks = sum(1 for r in rows if r["reason"] in ("N/A", "&mdash;"))

    body = (
        '<div style="padding-bottom:70px">'
        '<div class="toolbar"><span>%d lines &middot; September to date</span>'
        '<span class="right">Export <select><option>CSV</option><option>XLSX</option>'
        '</select></span></div>'
        '<div class="table-scroll"><table class="data"><thead><tr><th>Reference</th>'
        '<th>Received</th><th>Product</th><th>SKU</th><th>Reason</th><th class="num">Qty</th>'
        '<th class="num">Refund</th><th>Status</th></tr></thead><tbody>\n%s\n'
        '</tbody></table></div>'
        '<p class="aside-note">This is a real returns log, in the sense that it is as untidy as '
        'a real one. Dates are written three different ways. Refunds appear as '
        '<code>$1,240.00</code>, <code>USD 85</code> and bare <code>85.00</code>. %d cells are '
        'empty, %d more say <code>N/A</code> or an em dash instead, and two parcels were logged '
        'twice by two different people, so two rows repeat exactly. Getting it out is the easy '
        'part; the point of this page is what you do with it afterwards.</p>'
        '</div>' % (len(rows), "\n".join(tr), empties, blank_marks)
    )
    page("returns.html", "Returns log",
         "Sandbox table of deliberately dirty data: empty cells, three date formats, three "
         "currency formats, duplicate rows and HTML entities.",
         "Deliberately dirty data &mdash; empty cells, three date formats, duplicate rows. "
         "Export it, then see what your cleanup does with it.",
         '<a href="catalogue.html">Home</a> / Help / Returns log',
         "Returns log",
         "Every parcel back through the door this month, exactly as it was keyed in.",
         body)
    return len(rows), empties


# ------------------------------------------------------ 7. two tables, one page

def build_rates(rnd):
    dom = [("Zone 1", "Greater Manchester", "Next working day", "$6.50", "Free"),
           ("Zone 2", "North West &amp; North Wales", "Next working day", "$8.00", "Free"),
           ("Zone 3", "Midlands, Yorkshire", "1&ndash;2 working days", "$9.50", "Free"),
           ("Zone 4", "South East, South West", "2 working days", "$11.00", "$4.00"),
           ("Zone 5", "Scotland (mainland)", "2&ndash;3 working days", "$13.50", "$6.00"),
           ("Zone 6", "Scottish Highlands", "3&ndash;4 working days", "$18.00", "$9.00"),
           ("Zone 7", "Northern Ireland", "3 working days", "$16.00", "$8.00"),
           ("Zone 8", "Isle of Man, Channel Islands", "4&ndash;5 working days", "$21.00", "$12.00")]

    intl = [("Ireland", "IE", "2&ndash;3 days", "$14.00", "$180", "DDP"),
            ("Netherlands", "NL", "2&ndash;3 days", "$15.00", "$180", "DDP"),
            ("Belgium", "BE", "2&ndash;3 days", "$15.00", "$180", "DDP"),
            ("Germany", "DE", "3&ndash;4 days", "$16.50", "$200", "DDP"),
            ("France", "FR", "3&ndash;4 days", "$16.50", "$200", "DDP"),
            ("Denmark", "DK", "3&ndash;4 days", "$18.00", "$200", "DDP"),
            ("Spain", "ES", "4&ndash;5 days", "$19.00", "$220", "DDP"),
            ("Italy", "IT", "4&ndash;5 days", "$19.00", "$220", "DDP"),
            ("Sweden", "SE", "4&ndash;5 days", "$21.00", "$240", "DDP"),
            ("Norway", "NO", "5&ndash;6 days", "$26.00", "&mdash;", "DAP"),
            ("Switzerland", "CH", "5&ndash;6 days", "$26.00", "&mdash;", "DAP"),
            ("United States", "US", "6&ndash;9 days", "$34.00", "&mdash;", "DAP"),
            ("Canada", "CA", "7&ndash;10 days", "$36.00", "&mdash;", "DAP"),
            ("Japan", "JP", "7&ndash;10 days", "$39.00", "&mdash;", "DAP")]

    t1 = "\n".join('<tr><td>%s</td><td>%s</td><td>%s</td><td class="num">%s</td>'
                   '<td class="num">%s</td></tr>' % r for r in dom)
    t2 = "\n".join('<tr><td>%s</td><td>%s</td><td>%s</td><td class="num">%s</td>'
                   '<td class="num">%s</td><td>%s</td></tr>' % r for r in intl)

    body = (
        '<div style="padding-bottom:70px">'
        '<h2 class="sub" id="domestic">Domestic</h2>'
        '<p class="lede">Eight zones, priced by postcode. Trade orders over $400 ship free '
        'everywhere on this table.</p>'
        '<div class="table-scroll"><table class="data"><thead><tr><th>Zone</th><th>Covers</th>'
        '<th>Transit</th><th class="num">Standard</th><th class="num">Trade</th></tr></thead>'
        '<tbody>\n' + t1 + '\n</tbody></table></div>'
        '<h2 class="sub" id="international">International</h2>'
        '<p class="lede">Duties are paid by us where the last column says DDP. Where it says '
        'DAP they are collected on delivery, and we cannot quote them in advance.</p>'
        '<div class="table-scroll"><table class="data"><thead><tr><th>Country</th><th>Code</th>'
        '<th>Transit</th><th class="num">Flat rate</th><th class="num">Free over</th>'
        '<th>Duties</th></tr></thead><tbody>\n' + t2 + '\n</tbody></table></div>'
        '<p class="aside-note">Two tables, one page, different column counts. Automatic '
        'detection picks the bigger one &mdash; the ' + str(len(intl)) + '-row international '
        'table &mdash; so if you want the ' + str(len(dom)) + '-row domestic one you have to '
        'ask for it. That is what the <b>Another table</b> control is for.</p>'
        '</div>'
    )
    page("rates.html", "Delivery rates",
         "Sandbox page with two tables of different widths on one page, for testing table "
         "selection: 8 domestic zones and 14 international destinations.",
         "<b>Two tables on one page.</b> Detection takes the bigger one; use "
         "<b>Another table</b> for the other.",
         '<a href="catalogue.html">Home</a> / Help / Delivery rates',
         "Delivery rates",
         "Effective 1 September 2026. Prices exclude VAT where applicable.",
         body)
    return len(dom), len(intl)


# ---------------------------------------------------------------------- main

def main():
    rnd = random.Random(20260915)
    items = read_items()
    if len(items) < 120:
        raise SystemExit("expected 120 product pages, found %d" % len(items))

    counts = {}
    counts["shadow"] = build_shadow(items, rnd)
    counts["iframe"] = build_iframe(items, rnd)
    counts["feed"] = build_feed(items, rnd)
    counts["reviews"] = build_reviews(items, rnd)
    counts["stock"] = build_stock(items, rnd)
    counts["returns"] = build_returns(items, rnd)
    counts["rates"] = build_rates(rnd)

    print("\nexpected results, for the sandbox index:")
    for k, v in counts.items():
        print("  %-8s %s" % (k, v))


if __name__ == "__main__":
    main()

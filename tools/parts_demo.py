#!/usr/bin/env python3
"""A trade parts catalogue: a category sidebar, a brand filter, a featured
carousel, a paged parts table and a recently-viewed strip -- the shape of most
wholesale and parts sites, with every list a scraper could mistake for the data.

    python3 tools/parts_demo.py

Six categories of different lengths, ten parts to a page:
  Fasteners 26 (3 pages)  Hinges 8 (1)  Brackets 14 (2)
  Handles 5 (1)  Castors 12 (2)  Shelf supports 9 (1)   = 74 parts

demo/parts.html is Fasteners, page 1, and the page for search; every other
category page and page number is noindex. The practice:
- open on the table, not the sidebar, the carousel or the footer;
- page the table by its own pager, not the carousel's Next arrow;
- go through every category, every page of each: 74 rows with the category.
Everything is invented.
"""
import html, os, random
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'demo')
rnd = random.Random(1162026)
PER = 10
CATS = [('fasteners', 'Fasteners', 26, 'FX'), ('hinges', 'Hinges', 8, 'HG'), ('brackets', 'Brackets', 14, 'BR'),
        ('handles', 'Handles', 5, 'HD'), ('castors', 'Castors', 12, 'CS'), ('shelf-supports', 'Shelf supports', 9, 'SS')]
WORDS = {
 'fasteners': (['Wood screw', 'Machine screw', 'Coach bolt', 'Hex nut', 'Washer', 'Wall plug', 'Threaded insert', 'Rivet'], ['4 x 30 mm', '5 x 50 mm', 'M6', 'M8', 'M10', '6 mm', '8 mm']),
 'hinges': (['Butt hinge', 'Concealed hinge', 'Piano hinge', 'Tee hinge'], ['75 mm', '100 mm', '35 mm cup', '1.8 m']),
 'brackets': (['Shelf bracket', 'Angle bracket', 'Corner brace', 'Mending plate', 'Joist hanger'], ['100 mm', '150 mm', '200 mm', '250 mm']),
 'handles': (['Bar handle', 'Cup handle', 'Knob', 'D handle', 'Edge pull'], ['128 mm', '96 mm', '32 mm', '160 mm']),
 'castors': (['Swivel castor', 'Fixed castor', 'Braked castor', 'Ball castor'], ['50 mm', '75 mm', '100 mm']),
 'shelf-supports': (['Shelf stud', 'Shelf pin', 'Track upright', 'Glass clip'], ['5 mm', '6 mm', '1 m', '8 mm']),
}
MATERIALS = ['Zinc plated steel', 'Stainless steel', 'Brass', 'Black steel', 'Nylon', 'Oiled bronze']
BRANDS = ['Brock Forge', 'Northwind Hardware', 'Hallam & Co.', 'Aoyama Works', 'Fieldhouse', 'Kestrel Fixings', 'Millbrook', 'Thornbury']
PARTS = {}
for slug, name, n, pre in CATS:
    kinds, sizes = WORDS[slug]
    PARTS[slug] = [(f'{pre}-{1001 + i}', f'{kinds[i % len(kinds)]}, {sizes[(i * 3) % len(sizes)]}', MATERIALS[(i + len(slug)) % len(MATERIALS)],
                    str(rnd.choice([1, 10, 25, 50, 100, 200])), '${:,.2f}'.format(rnd.randint(40, 4800) / 100),
                    rnd.choice(['In stock', 'In stock', 'Low stock', 'Back order'])) for i in range(n)]
FEATURED = [('Soft-close concealed hinge', '$4.80'), ('Heavy-duty braked castor, 100 mm', '$12.40'), ('Brass cup handle', '$6.95'), ('Stainless coach bolt, M10', '$0.62'),
            ('Glass shelf clip', '$1.10'), ('Oiled bronze bar handle', '$9.30')]
RECENT = [('Mending plate, 150 mm', 'brackets'), ('Shelf stud, 5 mm', 'shelf-supports'), ('Swivel castor, 50 mm', 'castors')]

def addr(slug, p):
    if slug == 'fasteners' and p == 1: return 'parts.html'
    return f'parts-{slug}.html' if p == 1 else f'parts-{slug}-{p}.html'

CSS = '''
.parts{display:grid;grid-template-columns:220px 1fr;gap:34px;margin:6px 0 40px}@media(max-width:860px){.parts{grid-template-columns:1fr}}
.side h4{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#6b6556;margin:0 0 8px}.side ul{list-style:none;margin:0 0 24px;padding:0}
.side li{padding:5px 0;border-bottom:1px dashed #e7e2d8;font-size:15px}.side li a{text-decoration:none}.side li a[aria-current]{font-weight:700}.side .count{color:#8d8677;font-size:13px;margin-left:4px}
.featured{border:1px solid #e0dbd0;border-radius:12px;padding:14px 16px;margin:0 0 22px;background:#fffefb}.featured h2{font-size:17px;margin:0 0 10px;display:flex;justify-content:space-between;align-items:center}
.carousel{display:flex;gap:14px;overflow:hidden}.carousel .card{flex:0 0 calc(25% - 11px);border:1px solid #ece7dc;border-radius:10px;padding:10px 12px;background:#fff}
.carousel .card h3{font-size:14px;margin:0 0 4px}.carousel .card p{margin:0;font-size:14px;font-weight:700}
.arrows button{font:inherit;border:1px solid #e0dbd0;background:#fff;border-radius:50%;width:30px;height:30px;cursor:pointer;margin-left:6px}
table.partlist{border-collapse:collapse;width:100%;font-size:14.5px}table.partlist th{text-align:left;padding:8px 10px;border-bottom:2px solid #17150f;white-space:nowrap}
table.partlist td{padding:8px 10px;border-bottom:1px solid #ece7dc}table.partlist td.num,table.partlist th.num{text-align:right}
.showing{color:#6b6556;font-size:14px;margin:0 0 8px}.parts .pager{margin:12px 0}
.recent{margin-top:26px}.recent h2{font-size:17px;margin:0 0 8px}.recent ul{list-style:none;padding:0;margin:0;display:flex;gap:18px;flex-wrap:wrap}
.recent li{border:1px solid #ece7dc;border-radius:8px;padding:8px 12px;font-size:14px}
footer.cols{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;border-top:1px solid #e0dbd0;padding:26px 0 40px;font-size:14px}
footer.cols ul{list-style:none;padding:0;margin:0}footer.cols li{padding:3px 0}footer.cols h5{margin:0 0 8px;font-size:13px}
'''
JS = r'''
(function () {
  var track = document.querySelector('.carousel'), cards = track ? track.children : [], at = 0;
  function show() { for (var i = 0; i < cards.length; i++) cards[i].style.display = (i >= at && i < at + 4) ? '' : 'none'; }
  var n = document.querySelector('.carousel-next'), p = document.querySelector('.carousel-prev');
  if (n) n.addEventListener('click', function () { at = Math.min(at + 1, cards.length - 4); show(); });
  if (p) p.addEventListener('click', function () { at = Math.max(at - 1, 0); show(); });
  show();
})();
'''
BRAND = '<a class="brand" href="../" title="Magic Scraper home">Magic <b>Scraper</b> <span>Sandbox</span></a>'

def page(slug, p):
    name = dict((s, nm) for s, nm, _, _ in CATS)[slug]
    rows = PARTS[slug]; pages = (len(rows) + PER - 1) // PER
    show = rows[(p - 1) * PER: p * PER]
    side = '<aside class="side"><h4>Categories</h4><ul class="categories">' + ''.join(
        f'<li><a href="{addr(s, 1)}"' + (' aria-current="page"' if s == slug else '') + f'>{nm}</a><span class="count">({c})</span></li>'
        for s, nm, c, _ in CATS) + '</ul><h4>Brand</h4><ul class="brands">' + ''.join(
        f'<li><a href="#">{html.escape(b)}</a></li>' for b in BRANDS) + '</ul></aside>'
    feat = ('<div class="featured"><h2>Featured this month<span class="arrows"><button type="button" class="carousel-prev" aria-label="Previous">&lsaquo;</button>'
            '<button type="button" class="carousel-next" aria-label="Next">&rsaquo;</button></span></h2><div class="carousel">' + ''.join(
            f'<div class="card"><h3>{html.escape(t)}</h3><p>{pr}</p></div>' for t, pr in FEATURED) + '</div></div>')
    head = '<tr><th>Part no.</th><th>Description</th><th>Material</th><th class="num">Pack</th><th class="num">Price</th><th>Stock</th></tr>'
    body = ''.join('<tr>' + ''.join(f'<td class="num">{html.escape(c)}</td>' if k in (3, 4) else f'<td>{html.escape(c)}</td>' for k, c in enumerate(r)) + '</tr>' for r in show)
    pager = ''
    if pages > 1:
        pager = '<div class="pager">' + (f'<a class="prev" href="{addr(slug, p - 1)}">&lsaquo; Prev</a>' if p > 1 else '') + ''.join(
            f'<span class="on">{k}</span>' if k == p else f'<a href="{addr(slug, k)}">{k}</a>' for k in range(1, pages + 1)) + \
            (f'<a class="next" href="{addr(slug, p + 1)}">Next &rsaquo;</a>' if p < pages else '') + '</div>'
    first = (p - 1) * PER + 1
    main = (f'<div>{feat}<h2 style="font-size:22px;margin:0 0 4px">{name}</h2><p class="showing">Showing {first}&ndash;{first + len(show) - 1} of {len(rows)} parts</p>'
            f'<table class="partlist"><thead>{head}</thead><tbody>{body}</tbody></table>{pager}'
            '<div class="recent"><h2>Recently viewed</h2><ul>' + ''.join(f'<li><a href="{addr(s, 1)}">{html.escape(t)}</a></li>' for t, s in RECENT) + '</ul></div></div>')
    foot = ('<footer class="cols"><div><h5>Shop</h5><ul><li><a href="catalogue.html">Catalogue</a></li><li><a href="wholesale-prices.html">Wholesale</a></li><li><a href="stockists.html">Stockists</a></li></ul></div>'
            '<div><h5>Account</h5><ul><li><a href="account.html">Trade account</a></li><li><a href="#">Orders</a></li><li><a href="#">Invoices</a></li></ul></div>'
            '<div><h5>Help</h5><ul><li><a href="rates.html">Delivery</a></li><li><a href="returns.html">Returns</a></li><li><a href="#">Contact</a></li></ul></div>'
            '<div><h5>Sandbox</h5><ul><li><a href="index.html">All practice pages</a></li><li><a href="../">Magic Scraper</a></li></ul></div></footer>')
    return (f'<p class="crumbs"><a href="index.html">Sandbox</a> / Parts / {name}</p>'
            '<div class="head"><h1>Category and table scraping</h1><p>Trade parts catalogue &middot; 6 categories &middot; 74 parts</p></div>'
            f'<div class="parts">{side}{main}</div>{foot}<script>{JS}</script>')

def shell(title, desc, body, canonical='', noindex=False):
    meta = f'<meta name="description" content="{desc}">' + ('<meta name="robots" content="noindex, follow">' if noindex else '') + \
           (f'<link rel="canonical" href="https://magicscraper.app/demo/{canonical}">' if canonical else '')
    og = '' if noindex else (f'<meta property="og:type" content="website"><meta property="og:site_name" content="Magic Scraper"><meta property="og:url" content="https://magicscraper.app/demo/{canonical}">'
                             f'<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="https://magicscraper.app/assets/screenshot.png">'
                             '<meta name="twitter:card" content="summary_large_image">')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>{meta}{og}
<link rel="icon" href="../assets/icon.png"><link rel="stylesheet" href="store.css"><style>{CSS}</style></head><body><div class="sandbox"><div class="shell"><span class="tag">Sandbox</span><b>Practice site for Magic Scraper.</b> A category sidebar, a carousel and a paged table. The jobs: this table, every page of it &mdash; then every category&rsquo;s. <a href="index.html">All sandbox pages</a> &middot; <a href="../index.html"><b>Get Magic Scraper free</b></a></div></div>
<header class="site"><div class="shell bar">{BRAND}<nav><a href="catalogue.html">Catalogue</a><a href="parts.html" aria-current="page">Parts</a><a href="wholesale-prices.html">Wholesale</a><a href="account.html">Account</a></nav></div></header>
<div class="shell">{body}</div></body></html>'''

TITLE = 'Category and table scraping: a parts catalogue to practise on'
DESC = ('Practise scraping a parts table beside a category sidebar, a brand filter and a featured carousel: '
        '26 fasteners over 3 pages, then all 74 parts from six categories with the category on each row.')
n = 0
for slug, name, count, _ in CATS:
    pages = (count + PER - 1) // PER
    for p in range(1, pages + 1):
        a = addr(slug, p)
        main = a == 'parts.html'
        t = TITLE if main else f'{name}' + (f', page {p}' if p > 1 else '') + ' — category and table scraping practice'
        open(os.path.join(ROOT, a), 'w', encoding='utf-8').write(shell(t, DESC, page(slug, p), canonical='parts' if main else '', noindex=not main))
        n += 1
print(n, 'pages written; parts per category:', {s: len(PARTS[s]) for s in PARTS}, 'total', sum(len(v) for v in PARTS.values()))

"""Three sandbox pages for what the extension learned in 2.0 and 2.1.

    python3 tools/more_demos.py

- demo/stockists.html: a store locator split under A-Z headings, which comes
  out as one table with a Section column.
- demo/wholesale-prices.html: four products whose own pages hold a spec table
  and a volume-price table; drill-down gives one row per price tier.
- demo/directory.html (+ -2, -3): a local business directory over three pages,
  each listing with a profile page of label/value details -- the lead-list case.

Profile and product pages carry noindex, like the sandbox's other generated
detail pages. Everything is invented.
"""
import html, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'demo')
BRAND = '<a class="brand" href="../" title="Magic Scraper home">Magic <b>Scraper</b> <span>Sandbox</span></a>'
CSS = '''
.letters{display:flex;gap:6px;margin:6px 0 22px}.letters a{display:inline-block;width:30px;height:30px;line-height:30px;text-align:center;border:1px solid #e0dbd0;border-radius:6px;text-decoration:none;font-weight:600}
section.town{margin:0 0 22px}section.town h2{font-size:22px;margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid #e0dbd0}
ul.stockists{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:8px 22px}
ul.stockists li{padding:8px 0;border-bottom:1px dashed #e7e2d8}ul.stockists b{display:block}ul.stockists span{color:#6b6556;font-size:14px;margin-right:12px}
.biz{border:1px solid #e0dbd0;border-radius:10px;padding:14px 16px;background:#fffefb;margin:0 0 12px}.biz h3{margin:0 0 4px;font-size:18px}.biz p{margin:2px 0;color:#5d574a;font-size:14px}
table.specs,table.tiers{border-collapse:collapse;font-size:16px;width:100%}table.specs th,table.specs td,table.tiers td{text-align:left;padding:8px 12px;border-bottom:1px solid #e0dbd0}
table.tiers th{text-align:left;padding:8px 12px;border-bottom:2px solid #17150f}dl.profile{display:grid;grid-template-columns:160px 1fr;gap:8px 16px}dl.profile dt{color:#6b6556}dl.profile dd{margin:0}
'''

def shell(title, banner, body, desc='', noindex=False, canonical=''):
    meta = (f'<meta name="description" content="{desc}">' if desc else '') + ('<meta name="robots" content="noindex, follow">' if noindex else '') + \
           (f'<link rel="canonical" href="https://magicscraper.app/demo/{canonical}">' if canonical else '')
    og = (f'<meta property="og:type" content="website"><meta property="og:site_name" content="Magic Scraper"><meta property="og:title" content="{title}">'
          f'<meta property="og:description" content="{desc}"><meta property="og:image" content="https://magicscraper.app/assets/screenshot.png">') if desc and not noindex else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>{meta}{og}
<link rel="stylesheet" href="store.css"><style>{CSS}</style></head><body><div class="sandbox"><div class="shell"><span class="tag">Sandbox</span><b>Practice site for Magic Scraper.</b> {banner} <a href="index.html">All sandbox pages</a> &middot; <a href="../index.html"><b>Get Magic Scraper free</b></a></div></div>
<header class="site"><div class="shell bar">{BRAND}<nav><a href="catalogue.html">Catalogue</a><a href="directory.html">Directory</a><a href="wholesale-prices.html">Wholesale</a><a href="stockists.html">Stockists</a></nav></div></header>
<div class="shell">{body}</div></body></html>'''

def write(name, text):
    open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(text)

# ---- 1. store locator, A-Z
TOWNS = {
  'A': [('Ashby Home & Hearth', 'Ashby', '01530 555 014'), ('Avonmore Interiors', 'Avonmore', '0161 555 0192'), ('Alder & Rye', 'Alnwick', '01665 555 027')],
  'B': [('Bramble Kitchen Co.', 'Bath', '01225 555 031'), ('Burnside Living', 'Bristol', '0117 555 0148'), ('Bell Lane Goods', 'Beverley', '01482 555 063'), ('Blackthorn Studio', 'Buxton', '01298 555 070')],
  'C': [('Copper & Clay', 'Cardiff', '029 5550 0112'), ('Crane Street Store', 'Chester', '01244 555 089')],
  'D': [('Dovecote Home', 'Durham', '0191 555 0134'), ('Driftwood & Co.', 'Dartmouth', '01803 555 046'), ('Dunmore Supply', 'Dundee', '01382 555 018')],
  'E': [('Elm Row Living', 'Edinburgh', '0131 555 0176'), ('Ember Kitchenware', 'Exeter', '01392 555 052')],
}
n = sum(len(v) for v in TOWNS.values())
body = ('<p class="crumbs"><a href="index.html">Sandbox</a> / Store locator</p><div class="head"><h1>Store locator scraping</h1><p>Our stockists, A to Z</p></div>'
        '<p class="letters">' + ''.join(f'<a href="#{L}">{L}</a>' for L in TOWNS) + '</p>' +
        ''.join(f'<section class="town" id="{L}"><h2>{L}</h2><ul class="stockists">' + ''.join(
            f'<li><b class="shop-name">{html.escape(nm)}</b><span class="town-name">{t}</span><span class="tel">{p}</span></li>' for nm, t, p in rows) + '</ul></section>'
            for L, rows in TOWNS.items()))
write('stockists.html', shell('Store locator scraping: stockists listed A to Z',
    f'A store locator split under letter headings: {n} shops in five sections.', body,
    desc=f'Practise scraping a store locator split under A-Z headings: {n} stockists in five sections, which should come out as one table with the letter as a column.', canonical='stockists'))

# ---- 2. wholesale prices with tier tables
HW = [('Steel hinge, 100 mm', 'HG-100', 'Brushed steel', '2 days', [('1–9', '$2.40', '—'), ('10–49', '$2.10', '12%'), ('50+', '$1.80', '25%')]),
      ('Brass cabinet handle', 'BH-220', 'Polished brass', '3 days', [('1–24', '$6.00', '—'), ('25+', '$5.10', '15%')]),
      ('Oak shelf, 90 cm', 'OS-900', 'Oiled oak', '5 days', [('1–4', '$38.00', '—'), ('5–9', '$35.00', '8%'), ('10–19', '$32.00', '16%'), ('20+', '$29.00', '24%')]),
      ('Iron shelf bracket', 'SB-150', 'Matte black', '2 days', [('1–19', '$4.20', '—'), ('20–99', '$3.70', '12%'), ('100+', '$3.20', '24%')])]
tiers = sum(len(h[4]) for h in HW)
cards = ''
for i, (nm, sku, fin, ship, tr) in enumerate(HW):
    hue = (i * 71 + 20) % 360
    cards += (f'<article class="product"><a class="shot" href="wholesale-{i + 1}.html"><svg viewBox="0 0 400 300" role="img" aria-label="Product photograph"><rect width="400" height="300" fill="hsl({hue} 30% 90%)"/>'
              f'<rect x="130" y="90" width="140" height="120" rx="14" fill="hsl({hue} 28% 40%)" opacity=".25"/></svg></a><h3><a href="wholesale-{i + 1}.html">{html.escape(nm)}</a></h3>'
              f'<p class="maker">Northwind Hardware</p><div class="row"><span class="price">from {tr[-1][1]}</span></div><p class="sku">{sku}</p></article>')
    detail = (f'<p class="crumbs"><a href="wholesale-prices.html">Wholesale prices</a> / {html.escape(nm)}</p><div class="head"><h1>{html.escape(nm)}</h1><p>Northwind Hardware</p></div>'
              '<div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin:10px 0 40px"><div><h2 style="font-size:20px">Specifications</h2><table class="specs">' +
              ''.join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k, v in (('SKU', sku), ('Finish', fin), ('Ships in', ship))) +
              '</table></div><div><h2 style="font-size:20px">Volume pricing</h2><table class="tiers"><thead><tr><th>Quantity</th><th>Unit price</th><th>Discount</th></tr></thead><tbody>' +
              ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in tr) + '</tbody></table></div></div>')
    write(f'wholesale-{i + 1}.html', shell(f'{nm} — wholesale price scraping practice', 'A product page with a spec table and a volume-price table.', detail, noindex=True))
body = ('<p class="crumbs"><a href="index.html">Sandbox</a> / Wholesale prices</p><div class="head"><h1>Wholesale price scraping</h1>'
        '<p>Trade pricing: the more you order, the less each costs. Each product&rsquo;s own page has its price breaks.</p></div>'
        f'<div class="grid">{cards}</div>')
write('wholesale-prices.html', shell('Wholesale price scraping: volume pricing on product pages',
    f'Four products; each one&rsquo;s page holds a volume-price table. Expected with drill-down, one row per price tier: {tiers} rows.', body,
    desc=f'Practise scraping wholesale and volume pricing: four products whose own pages hold a spec table and a price-break table. One row per tier gives {tiers} rows.', canonical='wholesale-prices'))

# ---- 3. business directory over three pages, with profiles
TRADES = ['Plumber', 'Electrician', 'Roofer', 'Joiner', 'Plasterer', 'Locksmith', 'Glazier', 'Painter']
FIRST = ['Harbour', 'Kestrel', 'Millbrook', 'Oakfield', 'Riverside', 'Stonegate', 'Thornbury', 'Westcliff', 'Ashgrove', 'Brookside', 'Cedar', 'Fernhill']
STREETS = ['High Street', 'Station Road', 'Mill Lane', 'Church Street', 'Park Avenue', 'Queen Street']
BIZ = []
for i in range(24):
    trade = TRADES[i % 8]
    name = f'{FIRST[i % 12]} {trade}s' if i % 3 else f'{FIRST[i % 12]} {trade} & Sons'
    slug = f'biz-{i + 1}'
    BIZ.append(dict(name=name, trade=trade, slug=slug, town='Lakeside', phone=f'01632 555 {100 + i * 7:03d}',
                    email=f'hello@{FIRST[i % 12].lower()}{trade.lower()}.example', site=f'https://{FIRST[i % 12].lower()}{trade.lower()}.example',
                    addr=f'{3 + i * 4} {STREETS[i % 6]}, Lakeside LK{1 + i % 9} {2 + i % 7}QA', hours='Mon–Fri 8:00–17:30' if i % 4 else 'Mon–Sat 7:30–18:00',
                    since=1978 + (i * 3) % 44))
for p in (1, 2, 3):
    rows = BIZ[(p - 1) * 8: p * 8]
    cards = ''.join(f'<article class="biz"><h3><a href="{b["slug"]}.html">{html.escape(b["name"])}</a></h3><p class="trade">{b["trade"]} &middot; {b["town"]}</p><p class="phone">{b["phone"]}</p></article>' for b in rows)
    pager = '<div class="pager">' + (f'<a href="{"directory" if p == 2 else "directory-" + str(p - 1)}.html">&lsaquo; Previous</a>' if p > 1 else '') + \
            ''.join(f'<span class="on">{k}</span>' if k == p else f'<a href="{"directory" if k == 1 else "directory-" + str(k)}.html">{k}</a>' for k in (1, 2, 3)) + \
            (f'<a class="next" href="directory-{p + 1}.html">Next &rsaquo;</a>' if p < 3 else '') + '</div>'
    body = (f'<p class="crumbs"><a href="index.html">Sandbox</a> / Business directory</p><div class="head"><h1>Business directory scraping</h1>'
            f'<p>Trades in Lakeside &middot; 24 listings &middot; page {p} of 3</p></div>{cards}{pager}')
    name = 'directory.html' if p == 1 else f'directory-{p}.html'
    write(name, shell('Business directory scraping: a lead list with profile pages' + ('' if p == 1 else f', page {p}'),
        'A local business directory: 24 listings over three pages, each with a profile page.', body,
        desc='Practise building a lead list from a business directory: 24 listings over three pages, each with a profile page of address, phone, email, website and hours.' if p == 1 else '',
        noindex=p > 1, canonical='directory' if p == 1 else ''))
for b in BIZ:
    body = (f'<p class="crumbs"><a href="directory.html">Business directory</a> / {html.escape(b["name"])}</p><div class="head"><h1>{html.escape(b["name"])}</h1><p>{b["trade"]} in {b["town"]}</p></div>'
            '<dl class="profile">' + ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in (
                ('Address', html.escape(b['addr'])), ('Phone', f'<a href="tel:{b["phone"].replace(" ", "")}">{b["phone"]}</a>'),
                ('Email', f'<a href="mailto:{b["email"]}">{b["email"]}</a>'), ('Website', f'<a href="{b["site"]}">{b["site"].replace("https://", "")}</a>'),
                ('Opening hours', b['hours']), ('Established', str(b['since'])))) + '</dl>')
    write(f'{b["slug"]}.html', shell(f'{b["name"]} — business directory scraping practice', 'A business profile page: label and value pairs.', body, noindex=True))
print('written: stockists, wholesale-prices (+4), directory (+2 pages, 24 profiles)')

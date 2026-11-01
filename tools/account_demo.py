#!/usr/bin/env python3
"""A supplier account dashboard: five tables on one page, each paged its own way.

    python3 tools/account_demo.py

The practice is choosing one table out of several and paging *that* table:
- Open orders  18 rows, 3 pages of 6, each page its own address (account-orders-N)
- Invoices     40 rows, 4 pages of 10, each page its own address (account-invoices-N)
- Shipments    15 rows, 3 pages of 5, a JavaScript pager with no address
- Returns      12 rows, 6 on load and a "Show more returns" button
- Messages      5 rows, no pager

The orders and invoices pagers are worded and classed identically, and the
orders one comes first, so a scraper that takes the first Next on the page
pages the wrong table. Each address changes one table and shows the others at
their first page, as a server would.

account.html is the page for search; the paged addresses are noindex.
Everything is invented.
"""
import html, json, os, random
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'demo')
rnd = random.Random(20261101)

CUSTOMERS = ['Ashby Home & Hearth', 'Bramble Kitchen Co.', 'Copper & Clay', 'Dovecote Home', 'Elm Row Living', 'Alder & Rye',
             'Burnside Living', 'Crane Street Store', 'Driftwood & Co.', 'Ember Kitchenware']
PRODUCTS = ['Walnut Tray', 'Oak Runner, Ecru', 'Stoneware Carafe', 'Copper Coaster Set', 'Linen Throw', 'Slate Planter', 'Enamel Bowl', 'Cedar Mirror']
CARRIERS = ['DPD', 'Royal Mail', 'DHL Express', 'UPS', 'Parcelforce']
CITIES = ['Bath', 'Bristol', 'Cardiff', 'Chester', 'Durham', 'Edinburgh', 'Exeter', 'Leeds', 'York', 'Rotterdam']

def money(v): return '${:,.2f}'.format(v)

ORDERS = [(f'SO-{48120 + i}', f'{2 + i // 2} Oct 2026', str(rnd.randint(2, 40)), money(rnd.randint(180, 4200) + rnd.choice([0, .5, .25])),
           rnd.choice(['Awaiting stock', 'Picking', 'Packed', 'Part shipped'])) for i in range(18)]
INVOICES = [(f'INV-{2026}-{1301 + i}', f'{1 + (i * 3) % 28} {["Jul", "Aug", "Sep", "Oct"][i // 10]} 2026',
             f'{1 + (i * 3) % 28} {["Aug", "Sep", "Oct", "Nov"][i // 10]} 2026', money(rnd.randint(90, 6800) + rnd.choice([0, .4, .75])),
             rnd.choice(['Paid', 'Paid', 'Paid', 'Due', 'Overdue'])) for i in range(40)]
SHIPMENTS = [(f'{rnd.choice(["JD", "RM", "DH", "1Z", "PF"])}{rnd.randint(10**9, 10**10 - 1)}', rnd.choice(CARRIERS), f'{10 + i} Oct 2026',
              rnd.choice(CITIES), rnd.choice(['In transit', 'Delivered', 'Out for delivery', 'Delivered'])) for i in range(15)]
RETURNS = [(f'RMA-{7700 + i * 3}', rnd.choice(PRODUCTS), rnd.choice(['Damaged in transit', 'Wrong item', 'Faulty', 'Not as described']),
            money(rnd.randint(12, 380))) for i in range(12)]
MESSAGES = [('Accounts team', 'Statement for October is ready', '31 Oct 2026'), ('Warehouse', 'Order SO-48124 is part shipped', '30 Oct 2026'),
            ('Your account manager', 'New trade price list from 1 November', '28 Oct 2026'), ('Accounts team', 'Invoice INV-2026-1337 is overdue', '27 Oct 2026'),
            ('Returns desk', 'RMA-7703 credited to your account', '24 Oct 2026')]
assert len({r[0] for r in ORDERS}) == 18 and len({r[0] for r in INVOICES}) == 40

CSS = '''
.dash{display:grid;gap:26px;margin:8px 0 40px}.panel{border:1px solid #e0dbd0;border-radius:12px;background:#fffefb;padding:16px 18px 12px}
.panel h2{font-size:19px;margin:0 0 2px}.panel .sub{color:#6b6556;font-size:13.5px;margin:0 0 10px}
.panel table{border-collapse:collapse;width:100%;font-size:14.5px}.panel th{text-align:left;font-weight:600;padding:7px 10px;border-bottom:2px solid #17150f;white-space:nowrap}
.panel td{padding:7px 10px;border-bottom:1px solid #ece7dc;white-space:nowrap}.panel td.num,.panel th.num{text-align:right}
.panel .pager{margin:10px 0 2px;display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.panel .pager a,.panel .pager span,.panel .pager button{display:inline-block;min-width:30px;padding:4px 9px;border:1px solid #e0dbd0;border-radius:6px;text-align:center;font:inherit;font-size:14px;background:#fff;color:inherit;text-decoration:none;cursor:pointer}
.panel .pager .on{background:#17150f;color:#fff;border-color:#17150f}.panel .pager button[disabled]{opacity:.4;cursor:default}
.panel .more{margin-top:10px;font:inherit;font-size:14px;padding:6px 14px;border:1px solid #17150f;border-radius:8px;background:#fff;cursor:pointer}
.twocol{display:grid;grid-template-columns:1fr 1fr;gap:26px}@media(max-width:900px){.twocol{grid-template-columns:1fr}}
'''
BRAND = '<a class="brand" href="../" title="Magic Scraper home">Magic <b>Scraper</b> <span>Sandbox</span></a>'

def table(cls, heads, rows, nums=()):
    th = ''.join(f'<th class="num">{h}</th>' if i in nums else f'<th>{h}</th>' for i, h in enumerate(heads))
    body = ''.join('<tr>' + ''.join(f'<td class="num">{html.escape(c)}</td>' if i in nums else f'<td>{html.escape(c)}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'

def addr(kind, n):
    return 'account.html' if n == 1 else f'account-{kind}-{n}.html'

def pager(kind, n, pages, label):
    out = f'<div class="pager" aria-label="{label} pages">'
    if n > 1: out += f'<a class="prev" href="{addr(kind, n - 1)}">&lsaquo; Previous</a>'
    for k in range(1, pages + 1):
        out += f'<span class="on">{k}</span>' if k == n else f'<a href="{addr(kind, k)}">{k}</a>'
    if n < pages: out += f'<a class="next" href="{addr(kind, n + 1)}">Next &rsaquo;</a>'
    return out + '</div>'

def page(orders_p=1, invoices_p=1):
    o = ORDERS[(orders_p - 1) * 6: orders_p * 6]
    iv = INVOICES[(invoices_p - 1) * 10: invoices_p * 10]
    body = (
        '<p class="crumbs"><a href="index.html">Sandbox</a> / Trade account</p>'
        '<div class="head"><h1>Multiple tables scraping</h1><p>Trade account &middot; Northwind Supply &middot; five tables, each paged its own way</p></div>'
        '<div class="dash">'
        '<section class="panel" id="orders"><h2>Open orders</h2><p class="sub">18 orders not yet delivered</p>'
        + table('orders', ['Order', 'Placed', 'Items', 'Total', 'Status'], o, nums=(2, 3)) + pager('orders', orders_p, 3, 'Orders') + '</section>'
        '<section class="panel" id="invoices"><h2>Invoices</h2><p class="sub">Last four months &middot; 40 invoices</p>'
        + table('invoices', ['Invoice', 'Issued', 'Due', 'Amount', 'Status'], iv, nums=(3,)) + pager('invoices', invoices_p, 4, 'Invoices') + '</section>'
        '<div class="twocol">'
        '<section class="panel" id="shipments"><h2>Shipments</h2><p class="sub">This month &middot; 15 parcels</p>'
        + table('shipments', ['Tracking', 'Carrier', 'Shipped', 'To', 'Status'], SHIPMENTS[:5]) +
        '<div class="pager" aria-label="Shipments pages"><button type="button" id="ship-prev" disabled>&lsaquo; Previous</button>'
        '<span class="on" id="ship-at">1 / 3</span><button type="button" id="ship-next">Next &rsaquo;</button></div></section>'
        '<section class="panel" id="returns"><h2>Returns</h2><p class="sub">Open and credited &middot; 12</p>'
        + table('returns', ['RMA', 'Product', 'Reason', 'Credit'], RETURNS[:6], nums=(3,)) +
        '<button type="button" class="more" id="returns-more">Show more returns</button></section>'
        '</div>'
        '<section class="panel" id="messages"><h2>Messages</h2><p class="sub">Latest five</p>'
        + table('messages', ['From', 'Subject', 'Received'], MESSAGES) + '</section>'
        '</div>'
        '<script type="application/json" id="ship-data">' + json.dumps(SHIPMENTS) + '</script>'
        '<script type="application/json" id="returns-data">' + json.dumps(RETURNS[6:]) + '</script>'
        '<script>' + JS + '</script>')
    return body

JS = r'''
(function () {
  var esc = function (s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); };
  // Shipments: pages drawn in place, no address. A short wait, as a real one has.
  var ship = JSON.parse(document.getElementById('ship-data').textContent), at = 1, per = 5, pages = Math.ceil(ship.length / per);
  var tb = document.querySelector('table.shipments tbody'), prev = document.getElementById('ship-prev'), next = document.getElementById('ship-next');
  function draw() {
    tb.innerHTML = ship.slice((at - 1) * per, at * per).map(function (r) {
      return '<tr>' + r.map(function (c) { return '<td>' + esc(c) + '</td>'; }).join('') + '</tr>';
    }).join('');
    document.getElementById('ship-at').textContent = at + ' / ' + pages;
    prev.disabled = at === 1; next.disabled = at === pages;
  }
  function go(d) { prev.disabled = next.disabled = true; setTimeout(function () { at += d; draw(); }, 350); }
  next.addEventListener('click', function () { if (at < pages) go(1); });
  prev.addEventListener('click', function () { if (at > 1) go(-1); });
  // Returns: one more batch, then the button goes.
  var more = document.getElementById('returns-more');
  more.addEventListener('click', function () {
    more.disabled = true; more.textContent = 'Loading…';
    setTimeout(function () {
      var rows = JSON.parse(document.getElementById('returns-data').textContent);
      document.querySelector('table.returns tbody').insertAdjacentHTML('beforeend', rows.map(function (r) {
        return '<tr>' + r.map(function (c, i) { return '<td' + (i === 3 ? ' class="num"' : '') + '>' + esc(c) + '</td>'; }).join('') + '</tr>';
      }).join(''));
      more.remove();
    }, 400);
  });
})();
'''

def shell(title, desc, body, canonical='', noindex=False):
    meta = f'<meta name="description" content="{desc}">' + ('<meta name="robots" content="noindex, follow">' if noindex else '') + \
           (f'<link rel="canonical" href="https://magicscraper.app/demo/{canonical}">' if canonical else '')
    og = '' if noindex else (f'<meta property="og:type" content="website"><meta property="og:site_name" content="Magic Scraper"><meta property="og:url" content="https://magicscraper.app/demo/{canonical}">'
                             f'<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="https://magicscraper.app/assets/screenshot.png">'
                             '<meta name="twitter:card" content="summary_large_image">')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>{meta}{og}
<link rel="icon" href="../assets/icon.png"><link rel="stylesheet" href="store.css"><style>{CSS}</style></head><body><div class="sandbox"><div class="shell"><span class="tag">Sandbox</span><b>Practice site for Magic Scraper.</b> Five tables, each paged its own way. The job: all 40 invoices, and nothing from the other tables. <a href="index.html">All sandbox pages</a> &middot; <a href="../index.html"><b>Get Magic Scraper free</b></a></div></div>
<header class="site"><div class="shell bar">{BRAND}<nav><a href="catalogue.html">Catalogue</a><a href="directory.html">Directory</a><a href="wholesale-prices.html">Wholesale</a><a href="account.html" aria-current="page">Account</a></nav></div></header>
<div class="shell">{body}</div></body></html>'''

def write(name, text):
    open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(text)

TITLE = 'Multiple tables scraping: five paged tables on one page'
DESC = ('Practise scraping one table out of several on the same page, each with its own pager: 40 invoices over 4 pages '
        'beside paged orders, a JavaScript-paged shipments table, a Show more button and a table with no pager.')
write('account.html', shell(TITLE, DESC, page(), canonical='account'))
for n in (2, 3):
    write(f'account-orders-{n}.html', shell(f'Open orders, page {n} — multiple tables scraping practice', DESC, page(orders_p=n), noindex=True))
for n in (2, 3, 4):
    write(f'account-invoices-{n}.html', shell(f'Invoices, page {n} — multiple tables scraping practice', DESC, page(invoices_p=n), noindex=True))
print('written: account.html, account-orders-2..3, account-invoices-2..4')
print('first invoice', INVOICES[0], 'last', INVOICES[-1])

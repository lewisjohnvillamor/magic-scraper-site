"""The sandbox's pagination practice pages: one list, seven kinds of Next.

    python3 tools/pagers.py      (writes demo/pagers.html and demo/pager-*.html)

Each style is the same shop's 30 products over three pages of ten, so the only
thing that changes between them is how the page says "there is more". The
first page of each is linked from demo/pagers.html; the rest carry noindex,
like the sandbox's other generated pages, so they can be followed without
filling an index with fictional stock.
"""
import html, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'demo')

NAMES = ['Cast Iron Mug Set', 'Wool Skillet', 'Walnut Side Table', 'Wool Bowl', 'Slate Vase', 'Oak Jug',
         'Stoneware Desk Lamp', 'Smoked Glass Coaster Set', 'Oak Coaster Set', 'Linen Cushion', 'Brass Lamp',
         'Oak Chopping Board', 'Indigo Tea Towel', 'Bamboo Tray', 'Hand-blown Glass', 'Copper Kettle',
         'Stone Coasters', 'Ceramic Planter', 'Felt Placemats', 'Rattan Basket', 'Pine Shelf', 'Enamel Colander',
         'Clay Teapot', 'Woven Throw', 'Marble Board', 'Steel Hinge', 'Brass Handle', 'Iron Bracket',
         'Cork Trivet', 'Glass Carafe']
FINISH = ['Oat', 'Ink', 'Clay', 'Moss', 'Bone', 'Rust']
MAKERS = ['Fieldhouse', 'Aoyama Works', 'Tessa Ruiz Studio', 'Brock Forge', 'Mirren Ceramics', 'Northwind Own']
JA = ['鋳鉄マグセット', 'ウールのブランケット', 'くるみのサイドテーブル', '陶器の花瓶', 'リネンのクッション', '真鍮のランプ',
      'オークのまな板', '藍染めの布巾', '竹のトレイ', '手吹きグラス']
DE = ['Gusseisen-Becher', 'Wolldecke', 'Nussbaum-Beistelltisch', 'Steingutvase', 'Leinenkissen', 'Messinglampe',
      'Eichen-Schneidebrett', 'Geschirrtuch Indigo', 'Bambustablett', 'Mundgeblasenes Glas']

def product(n, lang='en'):
    i = n - 1
    name = (JA[i % 10] + f' No.{n}') if lang == 'ja' else (DE[i % 10] + f' Nr. {n}') if lang == 'de' else f'{NAMES[i]}, {FINISH[i % 6]}'
    price = f'{(n * 37) % 260 + 18}.00'
    cur = '¥' + f'{int(float(price) * 150):,}' if lang == 'ja' else (price.replace('.', ',') + ' €') if lang == 'de' else '$' + price
    hue = (n * 41) % 360
    return (f'<article class="product"><a class="shot" href="item{n}.html"><svg viewBox="0 0 400 300" role="img" aria-label="Product photograph">'
            f'<rect width="400" height="300" fill="hsl({hue} 30% 90%)"/><circle cx="200" cy="160" r="70" fill="hsl({hue} 30% 40%)" opacity=".22"/></svg></a>'
            f'<h3><a href="item{n}.html">{html.escape(name)}</a></h3><p class="maker">{MAKERS[i % 6]}</p>'
            f'<div class="row"><span class="price">{cur}</span></div><p class="sku">NW-{2000 + n}</p></article>')

def post(n):
    return (f'<article class="post"><h3><a href="item{n}.html">Notes from the workshop, no. {31 - n}</a></h3>'
            f'<p class="meta"><time datetime="2026-10-{(31 - n):02d}">{31 - n} October 2026</time> &middot; {MAKERS[(n - 1) % 6]}</p>'
            f'<p>How the {NAMES[n - 1].lower()} is made, start to finish, and what we changed this season.</p></article>')

def shell(title, body, lang='en', noindex=False, head_extra=''):
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ''
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>{robots}{head_extra}
<link rel="stylesheet" href="store.css"><style>
.post{{border-bottom:1px solid #e0dbd0;padding:14px 0}}.post h3{{margin:0 0 4px;font-size:18px}}.post .meta{{color:#6b6556;font-size:13px;margin:0 0 6px}}
.pg-arrow{{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border:1px solid #e0dbd0;border-radius:50%}}
.older-newer{{display:flex;justify-content:space-between;margin:26px 0 40px;font-size:15px}}
.pagination__next{{display:inline-block;width:40px;height:40px;border-radius:8px;background:#17150f;position:relative}}
.pagination__next::after{{content:"";position:absolute;left:14px;top:13px;width:10px;height:10px;border-top:2px solid #fff;border-right:2px solid #fff;transform:rotate(45deg)}}
.pageinfo{{margin:26px 0 40px;color:#6b6556}}
</style></head><body><div class="sandbox"><div class="shell"><span class="tag">Sandbox</span><b>Practice site for Magic Scraper.</b> Seven kinds of Next button. <a href="pagers.html">All of them</a> &middot; <a href="index.html">All sandbox pages</a></div></div>
<header class="site"><div class="shell bar"><a class="brand" href="catalogue.html">North<b>wind</b> <span>Supply</span></a><nav><a href="catalogue.html">Catalogue</a><a href="table.html">Trade list</a><a href="scroll.html">New arrivals</a></nav></div></header>
<div class="shell">{body}</div></body></html>'''

CHEVRON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>'
STYLES = [
  ('arrow', 'An arrow with no word', 'The Next control is an icon: a chevron in a circle with an <code>aria-label</code> and no visible text. Tests whether your scraper reads labels, not just link text.', 'en'),
  ('numbers', 'Page numbers only', 'A row of page numbers with the current one marked, and no Next or arrow at all. Tests whether your scraper can work out which number comes next.', 'en'),
  ('older', 'A blog&rsquo;s &ldquo;Older posts&rdquo;', 'A journal of posts, newest first, paged by <i>Older posts &rarr;</i> and <i>&larr; Newer posts</i>. Tests whether &ldquo;next&rdquo; is understood as &ldquo;older&rdquo; here.', 'en'),
  ('de', 'Next in German', 'The same list in German: <i>Weiter &rsaquo;</i> and <i>&lsaquo; Zur&uuml;ck</i>, prices written <i>39,00 &euro;</i>. Tests a scraper that only knows English.', 'de'),
  ('ja', 'Next in Japanese', 'The same list in Japanese, paged by <i>次へ</i> and <i>前へ</i>, with prices in yen. Tests a scraper that only knows the Latin alphabet.', 'ja'),
  ('class', 'A class name and nothing else', 'An empty, styled button whose only clue is <code>class="pagination__next"</code> &mdash; no text, no label, the arrow drawn in CSS. Tests whether your scraper reads the markup&rsquo;s own names.', 'en'),
  ('js', 'A button, and no address', 'One page. <i>Next page</i> is a <code>&lt;button&gt;</code> that swaps the products in with JavaScript; the address never changes. Tests whether your scraper can click as well as follow links.', 'en'),
]

def pager(style, p):
    nxt, prv = f'pager-{style}-{p + 1}.html', f'pager-{style}-{p - 1}.html'
    if style == 'arrow':
        return '<div class="pager">' + (f'<a class="pg-arrow" href="{prv}" aria-label="Previous page"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></a>' if p > 1 else '') + (f'<a class="pg-arrow" href="{nxt}" aria-label="Next page">{CHEVRON}</a>' if p < 3 else '') + '</div>'
    if style == 'numbers':
        return '<div class="pager">' + ''.join(f'<span class="on">{k}</span>' if k == p else f'<a href="pager-numbers-{k}.html">{k}</a>' for k in (1, 2, 3)) + '</div>'
    if style == 'older':
        return '<nav class="older-newer">' + (f'<a href="{prv}">&larr; Newer posts</a>' if p > 1 else '<span></span>') + (f'<a href="{nxt}">Older posts &rarr;</a>' if p < 3 else '') + '</nav>'
    if style == 'de':
        return '<div class="pager">' + (f'<a href="{prv}">&lsaquo; Zur&uuml;ck</a>' if p > 1 else '') + f'<span class="on">Seite {p} von 3</span>' + (f'<a href="{nxt}">Weiter &rsaquo;</a>' if p < 3 else '') + '</div>'
    if style == 'ja':
        return '<div class="pager">' + (f'<a href="{prv}">&lsaquo; 前へ</a>' if p > 1 else '') + f'<span class="on">{p} / 3</span>' + (f'<a href="{nxt}">次へ &rsaquo;</a>' if p < 3 else '') + '</div>'
    if style == 'class':
        return f'<div class="pageinfo">Page {p} of 3 ' + (f'<a class="pagination__next" href="{nxt}"></a>' if p < 3 else '') + '</div>'

def write(name, text):
    open(os.path.join(ROOT, name), 'w').write(text)

H1 = {'de': 'Haushaltswaren', 'ja': '商品一覧', 'en': 'Household goods'}
for style, title, _, lang in STYLES:
    if style == 'js':
        items = [product(n) for n in range(1, 31)]
        body = (f'<p class="crumbs"><a href="pagers.html">Pagination practice</a> / A button, and no address</p><div class="head"><h1>{H1["en"]}</h1><p>30 products, 10 at a time</p></div>'
                '<div class="grid" id="list"></div><div class="pager"><button type="button" id="prev" class="more" disabled>Previous page</button> '
                '<span id="where" class="on">1 / 3</span> <button type="button" id="next" class="more">Next page</button></div>'
                '<script>const ITEMS=' + str(items).replace('</', '<\\/') + ';let p=0;'
                'function show(){document.getElementById("list").innerHTML=ITEMS.slice(p*10,p*10+10).join("");'
                'document.getElementById("where").textContent=(p+1)+" / 3";document.getElementById("prev").disabled=p===0;document.getElementById("next").disabled=p===2;}'
                'document.getElementById("next").onclick=()=>{if(p<2){p++;show();window.scrollTo(0,0);}};document.getElementById("prev").onclick=()=>{if(p>0){p--;show();}};show();</script>')
        write('pager-js.html', shell('A button, and no address &mdash; pagination practice', body))
        continue
    for p in (1, 2, 3):
        if style == 'older':
            items = ''.join(post(n) for n in range((p - 1) * 10 + 1, p * 10 + 1))
            listing = f'<div class="posts">{items}</div>'
            heading = '<div class="head"><h1>Journal</h1><p>From the workshop</p></div>'
        else:
            items = ''.join(product(n, lang) for n in range((p - 1) * 10 + 1, p * 10 + 1))
            listing = f'<div class="grid">{items}</div>'
            heading = f'<div class="head"><h1>{H1.get(lang, H1["en"])}</h1><p>30 / {p}</p></div>' if lang != 'en' else f'<div class="head"><h1>{H1["en"]}</h1><p>Page {p} of 3</p></div>'
        crumbs = f'<p class="crumbs"><a href="pagers.html">Pagination practice</a> / {title}</p>'
        write(f'pager-{style}-{p}.html', shell(f'{title} (page {p}) &mdash; pagination practice', crumbs + heading + listing + pager(style, p), lang=lang, noindex=p > 1))

# ---- the hub
cards = ''.join(f'''      <div class="step">
        <span class="n">{i + 1:02d}</span>
        <h3><a href="{'pager-js.html' if s == 'js' else f'pager-{s}-1.html'}">{t}</a></h3>
        <p>{d}</p>
        <p class="expect">Expected: 30 {'posts' if s == 'older' else 'products'} {'from 3 clicks' if s == 'js' else 'across 3 pages'}.</p>
      </div>
''' for i, (s, t, d, _) in enumerate(STYLES))
src = open(os.path.join(ROOT, 'index.html')).read()
head_end = src.index('<body')
TITLE = 'Pagination practice: 7 kinds of Next button to scrape'
DESC = 'Seven practice lists, each paged a different way: an icon arrow, page numbers only, Older posts, German and Japanese, a class name only and a JavaScript button. Test any scraper.'
head = src[:head_end]
import re
head = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', head, flags=re.S)
head = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + DESC, head)
head = re.sub(r'(<link rel="canonical" href=")[^"]*', r'\g<1>https://magicscraper.app/demo/pagers', head)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + TITLE, head)
head = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + DESC, head)
head = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>https://magicscraper.app/demo/pagers', head)
head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
body_start = src.index('<main')
header = src[head_end:body_start]
footer = src[src.index('</main>'):]
main = f'''<main id="main">
<div class="wrap">
  <div class="hero">
    <p class="eyebrow">Sandbox &middot; pagination</p>
    <h1>Seven kinds of <i>Next</i> button, to practise on.</h1>
    <p class="standfirst">Most scrapers stop at page one because they look for a link that says
      &ldquo;Next&rdquo;. Real sites say it with an arrow, a page number, &ldquo;Older posts&rdquo;,
      another language, a class name, or a button with no address at all. Here is the same list of
      thirty products paged each of those ways, so you can see which ones your tool follows.</p>
  </div>
</div>
<div class="wrap">
  <section id="styles">
    <h2>The seven</h2>
    <p class="deck">Each list is 30 items over three pages of ten. Start on the first page and crawl;
      anything short of 30 means the Next was missed.</p>
    <div class="steps">
{cards}    </div>
  </section>
  <section id="more">
    <h2>And the ones the rest of the sandbox covers</h2>
    <div class="claim">
      <p>A plain <a href="catalogue.html">Next button over six pages</a>, <a href="scroll.html">infinite
        scroll</a>, a <a href="stock.html">Load more button</a> and a <a href="bulk.html">2,000-row list over
        40 pages</a>. Magic Scraper follows all of them, and every one above, from the Crawl tab&rsquo;s
        <b>Start crawling</b>; when it can&rsquo;t tell which control is Next, point at it once and it uses
        that for the rest.</p>
    </div>
  </section>
</div>

'''
open(os.path.join(ROOT, 'pagers.html'), 'w').write(head + header + main + footer)
print('written: pagers.html and', sum(1 for f in os.listdir(ROOT) if f.startswith('pager-')), 'pager pages')

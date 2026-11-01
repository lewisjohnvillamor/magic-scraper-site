#!/usr/bin/env python3
"""Notes under each sandbox page: what it is, why it is awkward, how to get it.

Written page by page, by hand -- each page has its own real-world twin, its own
trap and its own way out, and the notes say those, not a template. They go
below the data in a <section class="practice-notes">, as prose under headings
(no lists, no tables), so the page's own data stays the only list on it and a
scraper practising on the page is not handed a second one.

    python3 tools/practice_notes.py

Run after make_sandbox_pages.py, more_demos.py and sandbox_keywords.py. Safe to
run again: the section between the markers is replaced.
"""
import os, re
DEMO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'demo')
START, END = '<!-- practice-notes -->', '<!-- /practice-notes -->'
CSS = ('<style>.practice-notes{max-width:780px;margin:44px 0 56px;padding:24px 28px;background:#fffefb;border:1px solid #e0dbd0;'
       'border-radius:12px;color:#2a2720;font-size:15.5px;line-height:1.6}.practice-notes .kicker{font:600 11px/1 ui-monospace,monospace;'
       'letter-spacing:.12em;text-transform:uppercase;color:#b4491f;margin:0 0 10px}.practice-notes h2{font-size:21px;margin:22px 0 6px}'
       '.practice-notes h2:first-of-type{margin-top:4px}.practice-notes p{margin:0 0 10px}.practice-notes pre{background:#17150f;color:#f3efe6;'
       'padding:12px 14px;border-radius:8px;overflow:auto;font-size:13px;line-height:1.5}.practice-notes code{font-size:.92em}'
       '.practice-notes .cta{margin-top:16px;font-weight:600}</style>')

NOTES = {}

NOTES['stock'] = '''
<p class="kicker">About this practice page</p>
<h2>A stock screen from inside a warehouse system</h2>
<p>This is the kind of page you get from a warehouse management or ERP tool: one line per product,
the bin it lives in, a count for each site and a status. Suppliers publish screens like it for their
trade customers, and operations teams read them every morning. Nobody exports them, because the
system that draws them was never built to.</p>
<h2>Why most scrapers come back empty</h2>
<p>There is no <code>&lt;table&gt;</code> here. The grid is built from <code>&lt;div&gt;</code>
elements with <code>role="row"</code>, <code>role="columnheader"</code> and <code>role="cell"</code>,
which is how JavaScript data-grid components render. Anything that looks for
<code>table tr td</code> &mdash; Excel&rsquo;s <i>From Web</i>, Google Sheets&rsquo;
<code>IMPORTHTML</code>, most copy-and-paste &mdash; finds nothing, or one long column of text.</p>
<h2>Reading it</h2>
<p>Magic Scraper reads the ARIA roles as a table: open the extension and the 30 lines are there with
the six headers as column names, plus the product link it keeps as a column of its own. If you are
writing your own, the roles are the hook &mdash; in the browser console:</p>
<pre><code>[...document.querySelectorAll('[role="row"]')]
  .map(r =&gt; [...r.querySelectorAll('[role="cell"]')].map(c =&gt; c.textContent.trim()))
  .filter(cells =&gt; cells.length)</code></pre>
<p>On a real system there is usually one more catch: big grids only draw the rows on screen and
reuse them as you scroll. That is the moment to scroll the grid itself, not the page &mdash; the
extension does, inside the panel the grid sits in.</p>
<h2>What right looks like</h2>
<p>30 rows and 7 columns, with Wigan and Rotterdam as numbers you can sum. Wrong answers to watch
for: the header row repeated as data, or the toolbar line &ldquo;30 lines &middot; bin locations as of
06:00&rdquo; turning up as a row. If you track a page like this over time, the counts falling and the
status changing are the story &mdash; see <a href="../track-website-price-changes">tracking changes on a
schedule</a>.</p>
'''

NOTES['catalogue'] = '''
<p class="kicker">About this practice page</p>
<h2>An ordinary shop category, which is the point</h2>
<p>Product cards in a grid, filters down the side, a sort menu and a pager at the bottom: this is
what a Shopify, WooCommerce or Magento category page looks like, and it is the page most people
want first &mdash; for watching a competitor&rsquo;s prices, moving a catalogue between systems, or
simply getting a supplier&rsquo;s range into a spreadsheet you can sort.</p>
<h2>Where it goes wrong</h2>
<p>Three small things, each enough to spoil a sheet. The cards are not all the same: on this first page six
carry a <i>Sale</i> badge and a crossed-out price, two say <i>Low stock</i>, the rest say neither, so a scraper
that reads fields by position slides every column one place to the left on the cards without them.
The filter lists in the sidebar are repeated items too, and a careless detector picks
&ldquo;Textiles (19)&rdquo; as the data. And there are six pages, so stopping at page one gets you
nine rows of fifty-four.</p>
<h2>Getting all fifty-four</h2>
<p>In Magic Scraper: open it, check the nine cards are outlined (not the sidebar), then <b>Start
crawling</b> on the Crawl tab. Every card behind every page has its own product page as well, and
<a href="../drill-down">drill-down</a> reads it &mdash; the maker, and behind the maker a chain ten
levels deep, if you want to practise that. In Python, read fields by class rather than position and
follow the Next link until there isn&rsquo;t one:</p>
<pre><code>import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

url, rows = "https://magicscraper.app/demo/catalogue", []
while url:
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    for card in soup.select("article.product"):
        was = card.select_one(".was")
        rows.append({"name": card.h3.get_text(strip=True),
                     "price": card.select_one(".price").get_text(strip=True),
                     "was": was.get_text(strip=True) if was else ""})
    nxt = soup.select_one("a.next")
    url = urljoin(url, nxt["href"]) if nxt else None
print(len(rows))   # 54</code></pre>
<h2>A correct result</h2>
<p>54 rows across 6 pages. 25 of them are on sale; the <i>was</i> price is empty on the other
29, not filled with the next field along; the rating comes out as a number (4.1), separate from the
stars.</p>
'''

NOTES['table'] = '''
<p class="kicker">About this practice page</p>
<h2>A supplier&rsquo;s trade price list</h2>
<p>Wholesalers and distributors publish price lists exactly like this one: a plain table of
products with a retail price, a trade price and what is on hand. It is the easiest page in the
sandbox, and it is here for that reason &mdash; it is where to start, and the yardstick for every
harder page.</p>
<h2>The page where the built-in tools work too</h2>
<p>Because this is a real <code>&lt;table&gt;</code> with a <code>&lt;thead&gt;</code>, delivered with
the page rather than drawn by a script, the tools that fail elsewhere work here. Excel&rsquo;s
<b>Data &rarr; From Web</b> imports it; in Google Sheets, <code>=IMPORTHTML("https://magicscraper.app/demo/table",
"table", 1)</code> does too; in Python, one line:</p>
<pre><code>import pandas as pd
df = pd.read_html("https://magicscraper.app/demo/table")[0]
df.shape   # (50, 7)</code></pre>
<p>Notice the seven: each product name is a link to its own page, and all three of those tools keep
the text and drop the link. Magic Scraper keeps the link as an eighth column &mdash; which matters the
moment you want to open each product&rsquo;s page for more, as <a href="../drill-down">drill-down</a>
does.</p>
<h2>Small things to get right</h2>
<p>The prices come through as written, with the dollar sign, so a spreadsheet treats them as
text until you take it off: in Excel, Find and Replace <code>$</code> with nothing, or
<code>=VALUE(SUBSTITUTE(E2,"$",""))</code> in a spare column. The <i>On hand</i> column is a plain
count and arrives as numbers. The expected result is 50 rows and 8 columns.</p>
<h2>Where to go next</h2>
<p>The same products appear on the <a href="stock.html">warehouse stock</a> page drawn without a
table at all, and on the <a href="catalogue.html">catalogue</a> as cards over six pages. Doing all
three is a quick way to see which kinds of page your tool really handles.</p>
'''

NOTES['directory'] = '''
<p class="kicker">About this practice page</p>
<h2>A local directory, and the lead list behind it</h2>
<p>Trade directories, chamber of commerce member lists and &ldquo;find a tradesperson&rdquo; sites all
look like this: a short card per business in the list, and the useful details &mdash; email, website,
address, opening hours &mdash; one click away on its own profile page. If you are building a list of
businesses to contact, this is the job, and it has two halves.</p>
<h2>The first half: every listing</h2>
<p>The list shows a name, a trade and a phone number, eight to a page, over three pages. Collect
all three pages and you have 24 businesses with a phone each &mdash; in Magic Scraper, open it on this
page and press <b>Start crawling</b>.</p>
<h2>The second half: what is on each profile</h2>
<p>Each profile lays its details out as label and value pairs (<i>Address</i>, <i>Phone</i>,
<i>Email</i>, <i>Website</i>, <i>Opening hours</i>, <i>Established</i>). Turn on
<a href="../drill-down">drill-down</a>, preview the first profile, and those become columns on every
row. The free version reads the first three profiles so you can see the result; Pro reads all of
them. Writing it yourself, it is a loop over the profile links, reading the pairs into a dictionary:</p>
<pre><code>for link in soup.select("article.biz h3 a"):
    page = BeautifulSoup(requests.get(urljoin(url, link["href"])).text, "html.parser")
    labels = [dt.get_text(strip=True) for dt in page.select("dl.profile dt")]
    values = [dd.get_text(strip=True) for dd in page.select("dl.profile dd")]
    record = dict(zip(labels, values))</code></pre>
<h2>Checking the result, and using it well</h2>
<p>24 rows; with the profiles read, six more columns. The phone number appears twice, once from
the list and once from the profile &mdash; keep one. On a real directory, keep to business details,
check the site&rsquo;s terms, and mind the rules on contacting people where you are:
<a href="../is-it-legal-to-scrape-a-business-directory">is it legal to scrape a business directory?</a>
For the whole workflow, from finding the directory to keeping only the leads you don&rsquo;t have, see
<a href="../lead-generation">building a B2B lead list</a>.</p>
'''

def main():
    for slug, body in NOTES.items():
        path = os.path.join(DEMO, slug + '.html')
        s = open(path, encoding='utf-8').read()
        s = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', s, flags=re.S)
        # the old one-paragraph note under the stock grid is folded into these notes
        if slug == 'stock':
            s = re.sub(r'<p class="aside">There is no &lt;table&gt; on this page\..*?</p>', '', s, flags=re.S)
        block = (START + CSS + '<section class="practice-notes" id="practice-notes">' + body.strip() +
                 '<p class="cta">Try it yourself: <a href="../">get Magic Scraper free</a> and open it on this page.</p>'
                 '</section>' + END)
        if '<footer class="site">' in s:
            s = s.replace('<footer class="site">', block + '<footer class="site">', 1)
        else:
            i = s.rindex('</div></body>')
            s = s[:i] + block + s[i:]
        open(path, 'w', encoding='utf-8').write(s)
        print('notes:', slug, len(re.sub(r'<[^>]+>', ' ', body).split()), 'words')


if __name__ == '__main__':
    main()

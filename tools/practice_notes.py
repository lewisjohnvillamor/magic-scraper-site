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

NOTES['scroll'] = '''
<p class="kicker">About this practice page</p>
<h2>A &ldquo;new arrivals&rdquo; feed with no page two</h2>
<p>Fashion shops, marketplaces, job boards and social feeds have mostly given up on numbered pages.
They show a first handful and add more as you near the bottom. It is pleasant to browse and awkward
to collect, because nothing tells you how many there are or when you have reached the end. This
page behaves like those: eight products on load, eight more each time you scroll close to the
bottom, five times, and then the line &ldquo;No more items.&rdquo;</p>
<h2>Why a single grab gets eight</h2>
<p>When the page first appears only the first batch exists. Read it then and you have eight rows,
and nothing looks wrong &mdash; there is no pager to remind you of what you missed. Fetch the address
with a plain HTTP request and it is worse: the cards are drawn by a script, so the HTML holds no
cards at all.</p>
<h2>Collecting all forty</h2>
<p>In Magic Scraper, turn on <b>Infinite scroll</b> on the Crawl tab and start crawling. It scrolls,
waits for the new cards, adds them, and stops when two scrolls in a row bring nothing new. In the
browser console the same idea is a short loop:</p>
<pre><code>for (let i = 0; i &lt; 10; i++) {
  window.scrollTo(0, document.body.scrollHeight);
  await new Promise(r =&gt; setTimeout(r, 400));
}
document.querySelectorAll('#feed article.product').length   // 40</code></pre>
<p>Before you scroll anything, look at the page source. Feeds like this often ship their whole list
as JSON for the script to draw from, and here it is: an <code>ITEMS</code> array with all forty.
When that is there, it beats scrolling:</p>
<pre><code>import re, json, requests
html = requests.get("https://magicscraper.app/demo/scroll").text
items = json.loads(re.search(r"var ITEMS=(\\[.*?\\]);", html, re.S).group(1))
len(items)   # 40</code></pre>
<p>On real sites the list usually comes from a separate request instead &mdash; the Network tab in
DevTools, filtered to Fetch/XHR, shows it as you scroll.</p>
<h2>A correct result</h2>
<p>40 rows, no repeats, each with name, maker, a price like $192.00, the rating as a number, a stock
line and an SKU. If you have 8, the scroll never happened; 16 or 24 means the waits were too short
for the feed to keep up.</p>
'''

NOTES['reviews'] = '''
<p class="kicker">About this practice page</p>
<h2>Product reviews behind a &ldquo;Load more&rdquo; button</h2>
<p>Reviews are some of the most useful text on the web: what buyers like, what breaks, what they
compare you with. Shops, app stores and review sites rarely put them on numbered pages. They show a
dozen and a <b>Load more</b> button. This page has 48 reviews, 12 on load, and the button adds 12 at
a time until it disappears and the page says &ldquo;That is all 48 reviews.&rdquo;</p>
<h2>The two ways it goes wrong</h2>
<p>The first is not clicking at all and stopping at 12. The second is subtler: clicking too fast.
Each click here takes about half a second to answer, as a real server would, and during that time
the button says &ldquo;Loading&hellip;&rdquo; and is disabled. A scraper that clicks and immediately
reads gets the same twelve again, or clicks a disabled button and decides it is finished.</p>
<h2>Getting all 48</h2>
<p>Magic Scraper spots the button as the way to the next batch, so <b>Start crawling</b> clicks it,
waits for the new reviews, and stops when the button is gone. In the console, click only when the
button is ready and wait between clicks:</p>
<pre><code>let b;
while ((b = document.getElementById('more'))) {
  if (!b.disabled) b.click();
  await new Promise(r =&gt; setTimeout(r, 600));
}
document.querySelectorAll('#reviews article.rev').length   // 48</code></pre>
<p>Each review has a reviewer, a star rating, a date, the product it is about and the text. The
stars are characters (&#9733;&#9733;&#9733;&#9734;&#9734;), which are no use in a spreadsheet; the number is
in the element&rsquo;s title, &ldquo;3 out of 5&rdquo;, and that is what to keep.</p>
<h2>Checking the result</h2>
<p>48 rows. 31 are marked <i>Verified purchase</i> and 17 are not, so that column should be blank
on 17 rows, not shifted along. The ratings should average 3.9, matching the figure above the list.
Dates run from 12 September 2026 back to 30 April 2026 and come through as written; for sorting,
convert them in your spreadsheet. Once they are in a sheet, sorting by rating and reading the
one- and two-star reviews together is the quickest way to find what keeps going wrong.</p>
'''

NOTES['shadow'] = '''
<p class="kicker">About this practice page</p>
<h2>Products inside a web component</h2>
<p>More and more sites are assembled from web components: a <code>&lt;product-grid&gt;</code> or
<code>&lt;store-locator&gt;</code> tag that draws its own contents in a <i>shadow root</i>, a private
document fragment attached to the element. Design systems and embeddable widgets use them because
their styles cannot leak. Scrapers meet them as a page that plainly shows twelve products and
contains, as far as <code>document.querySelectorAll</code> is concerned, none.</p>
<h2>What is happening</h2>
<p>The twelve cards are inside <code>&lt;nw-showcase&gt;</code>. Open DevTools and you will see
<code>#shadow-root (open)</code> beneath it, with the cards inside. Queries on the page stop at that
boundary. So do most point-and-click tools, and so does a plain HTTP request, because the
component builds its cards with JavaScript after the page loads.</p>
<h2>Reading it</h2>
<p>Magic Scraper looks inside open shadow roots as it searches the page, so it finds the twelve
cards with no setting to change. Writing your own, step through the root on purpose:</p>
<pre><code>[...document.querySelector('nw-showcase').shadowRoot.querySelectorAll('article')]
  .map(a =&gt; ({ name: a.querySelector('h3').textContent,
               price: a.querySelector('.price').textContent }))</code></pre>
<p>In Python without a browser, look for where the component gets its data. Here it reads a JSON
block in the page, <code>&lt;script id="showcase-data"&gt;</code>, which <code>json.loads</code> turns
into twelve records. Real components more often fetch it, and the request shows up in the Network
tab.</p>
<h2>The limit worth knowing</h2>
<p>A shadow root can also be created <i>closed</i>, and then the page&rsquo;s own scripts keep the
only reference to it. Nothing outside &mdash; no extension, no console snippet &mdash; can read a closed
root. That is rare on content people want to read, but if a tool cannot see a component that DevTools
shows as <code>#shadow-root (closed)</code>, that is why, and the data source is the way in.</p>
<h2>A correct result</h2>
<p>12 rows with name, maker and category, a price ($243.00 for the first), a rating as a number and
an SKU. Zero rows means the tool never stepped into the root.</p>
'''

NOTES['iframe'] = '''
<p class="kicker">About this practice page</p>
<h2>A table that lives in another page</h2>
<p>Stock levels from a warehouse system, a booking calendar, a results table from a sports
federation, a price list from a supplier&rsquo;s portal: sites often show these by embedding another
page in an <code>&lt;iframe&gt;</code> rather than copying the data in. To the eye it is one page. To
anything reading the page it is two documents, and the table is in the one you did not ask for.</p>
<h2>What a page-level tool sees</h2>
<p>Ask for this address and you get the frame, not its contents. In Python,
<code>pd.read_html("https://magicscraper.app/demo/iframe")</code> fails with &ldquo;No tables
found&rdquo;; Excel&rsquo;s From Web and Google Sheets&rsquo; <code>IMPORTHTML</code> come back the same.
In the browser, <code>document.querySelector('table')</code> returns nothing, because the table belongs
to the frame&rsquo;s own <code>document</code>.</p>
<h2>Getting the 24 rows</h2>
<p>The frame here is served from the same site, which is the case that can be read. Magic Scraper
steps into same-origin frames while it looks for data, so it finds the table directly. In the console,
go through the frame:</p>
<pre><code>document.querySelector('iframe').contentDocument.querySelectorAll('tbody tr').length   // 24</code></pre>
<p>The more general route works for any frame: find its address in the <code>src</code> attribute
(here <a href="iframe-stock.html">iframe-stock.html</a>) and open it on its own. Then it is an
ordinary page with an ordinary table, and <code>pd.read_html</code> on it returns 24 rows by 6
columns.</p>
<h2>When the frame is from another site</h2>
<p>If the embedded page comes from a different domain, the browser keeps the two apart: no script on
the outer page, and no extension working in it, can read inside. Opening the frame&rsquo;s address in
its own tab is then the only route, and usually an easy one. From version 2.1, Magic Scraper notices
a large frame from another site and offers to open it in its own tab for you.</p>
<h2>A correct result</h2>
<p>24 rows: product, SKU, maker, the counts at Wigan and Rotterdam, and next dispatch. The Wigan
column should add up to 2,830 and Rotterdam to 837 &mdash; a quick check that every row came through
as a number.</p>
'''

NOTES['awkward'] = '''
<p class="kicker">About this practice page</p>
<h2>A clearance list where the important number is outside the list</h2>
<p>End-of-line pages, outlet sections and trade promotions often work like this one: a table of
products at their old price, and a banner above it that changes everything &mdash; here,
&ldquo;&minus;35% applies to every line below&rdquo;. If you are comparing prices or deciding what to
buy, the price you would pay is the one you want, and the page never writes it down.</p>
<h2>What a scraper can and can&rsquo;t know</h2>
<p>Any good tool gets the table: ten lines with Product, SKU, Category, Was and Left, plus the
product link. None of them can know that the banner applies to the rows. That is not a detection
problem a better tool solves; it is a sentence written for people, and the connection between it and
the rows exists only in the reader&rsquo;s head. A scraper that silently invents a &ldquo;Now&rdquo;
column would be worse than one that leaves it out.</p>
<h2>Adding the missing column yourself</h2>
<p>Collect the ten rows with Magic Scraper and export them, then add the discount as one formula.
With <i>Was</i> in column D, put this in a spare column and fill down:</p>
<pre><code>=VALUE(SUBSTITUTE(D2,"$",""))*(1-35%)</code></pre>
<p>In pandas it is one line once the table is read:</p>
<pre><code>import pandas as pd
df = pd.read_html("https://magicscraper.app/demo/awkward")[0]
df["Now"] = (df["Was"].str.lstrip("$").astype(float) * 0.65).round(2)</code></pre>
<p>Write the rule down next to the data &mdash; &ldquo;&minus;35% from the banner, ends Sunday&rdquo; &mdash;
because in a week the sheet will be the only record of it. If you scrape the page on a
<a href="../track-website-price-changes">schedule</a>, a change to the banner will not show up as a
change to any row, so check it by eye.</p>
<h2>A correct result</h2>
<p>10 rows. Walnut Tray was $429.00, so it is $278.85 after the discount; Jute Tray, Bone goes from
$488.00 to $317.20. The <i>Left</i> column is a count, from 1 to 18, and arrives as numbers.</p>
'''

NOTES['returns'] = '''
<p class="kicker">About this practice page</p>
<h2>A returns log typed in by several people</h2>
<p>Back-office pages &mdash; returns, orders, tickets, timesheets &mdash; are where data gets messy,
because people key them in by hand, on different days, with different habits. This log is 24 lines
of exactly that. Getting it off the page is one click. Getting it into a state where you can total
the refunds or count returns by reason is the real work, and this page is for practising it.</p>
<h2>What is wrong with it</h2>
<p>Dates are written three ways: <code>2026-03-01</code>, <code>06/07/2026</code> and
<code>11 Jan 2026</code>. The slashed ones are ambiguous &mdash; 06/07 is June to an American and July
to a Brit &mdash; and nothing on the page says which. Refunds come as <code>$420.00</code>,
<code>USD 227</code> and a bare <code>341.90</code>. Status is <i>Refunded</i>, <i>refunded</i> and
<i>REFUNDED</i>. Thirteen cells are empty, seven more say <code>N/A</code> or an em dash, some product
names end in a non-breaking space you cannot see, and two returns were logged twice.</p>
<h2>Cleaning it</h2>
<p>Magic Scraper exports the cells as they are written, which is what you want: cleaning belongs
after the export, where you can see what you changed. In pandas, the steps are short but each one
is a decision:</p>
<pre><code>import pandas as pd
df = pd.read_html("https://magicscraper.app/demo/returns")[0]
df = df.drop_duplicates()                                   # 24 -&gt; 22
df["Status"] = df["Status"].str.strip().str.capitalize()
df["Refund"] = pd.to_numeric(df["Refund"].str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
df["Product"] = df["Product"].str.strip()</code></pre>
<p>Two things to know. <code>read_html</code> quietly turns <code>N/A</code> into a missing value,
which is usually right but means the count of blanks goes up. And dates should be parsed per
format, not with one guess: decide what <code>06/07/2026</code> means for your source and say so
in the sheet.</p>
<h2>A correct result</h2>
<p>24 rows and 8 columns before cleaning, 22 after the two exact repeats are dropped. If your tool
gives 22 straight away, it has deduplicated for you; Magic Scraper keeps both, because two identical
lines in a log may be a real double return and only you can tell.</p>
'''

NOTES['rates'] = '''
<p class="kicker">About this practice page</p>
<h2>Shipping rates in two tables</h2>
<p>Carriers, couriers and shops publish delivery charges like this: one table for home, one for
abroad, and they are never the same shape. If you are comparing carriers or building a shipping
calculator, you usually need both &mdash; and a scraper that takes &ldquo;the table on the
page&rdquo; gives you one.</p>
<h2>Which table do you get?</h2>
<p>The domestic table has 8 zones and 5 columns (Zone, Covers, Transit, Standard, Trade). The
international one has 14 countries and 6 (Country, Code, Transit, Flat rate, Free over, Duties).
Automatic detection picks the bigger one, the international table, because it has more rows. That is
the right guess more often than not, and wrong whenever you came for the other.</p>
<h2>Getting each one</h2>
<p>In Magic Scraper, open it and you have the 14 international rows. For the domestic zones, open
<b>Wrong list?</b> and choose <b>Another table</b>; it moves to the next candidate on the page and
outlines it, so you can see which you have before exporting. In Python both come back at once, in
page order:</p>
<pre><code>import pandas as pd
domestic, international = pd.read_html("https://magicscraper.app/demo/rates")
domestic.shape, international.shape   # (8, 5) (14, 6)</code></pre>
<p>Do not try to stack them into one sheet: the columns mean different things. Keep two tabs, or add
a <i>Region</i> column to each before joining.</p>
<h2>Reading the values</h2>
<p>Several cells are words, not numbers: <i>Free</i> in the trade column for zones 1 to 3, and an
em dash under <i>Free over</i> for the countries where there is no free threshold. Decide what they
mean before summing &mdash; Free is 0; the dash is &ldquo;never&rdquo;, which is not 0. The Duties
column is a code: DDP means duties are paid by the sender, DAP that they are collected on delivery.</p>
<h2>A correct result</h2>
<p>8 rows by 5 columns, or 14 rows by 6. Zone 1, Greater Manchester, is $6.50 standard; Japan is
the most expensive at $39.00 flat.</p>
'''

NOTES['bulk'] = '''
<p class="kicker">About this practice page</p>
<h2>A big trade list: 2,000 variants over 40 pages</h2>
<p>A full supplier range, every size and finish as its own line, fifty to a page: this is what
exporting a whole wholesale catalogue or a marketplace category looks like. Small pages hide the
problems that only show up at size, and this one is long enough to show them.</p>
<h2>What changes when it is long</h2>
<p>The pager shows <code>1 2 3 &hellip; 40 Next &rsaquo;</code>: a window, not every number, so
following page numbers gets you to page 3 and the last page and nothing between. The Next link is
the only reliable way through. Forty requests also take long enough that things go wrong: a laptop
sleeps, a tab is closed, the connection drops at page 27.</p>
<h2>Running it in Magic Scraper</h2>
<p>Open it on page 1 and press <b>Start crawling</b>. The counter climbs past fifty a page while
the preview stops at the first 100 rows, so it stays quick &mdash; the export holds every row. The
pace setting waits between pages, which costs nothing here and matters on a real shop that notices
a burst of requests. If the run dies part-way &mdash; a closed tab, a crash &mdash; reopen the
extension on the site and it offers to <b>Recover</b> the rows it had collected, so a failure at page
27 does not cost you the first 26. Crawling has no row limit on the free version.</p>
<h2>In Python</h2>
<p>Follow Next until it is gone and join the pages at the end:</p>
<pre><code>import io, requests, pandas as pd
from urllib.parse import urljoin
from bs4 import BeautifulSoup

url, pages = "https://magicscraper.app/demo/bulk", []
while url:
    html = requests.get(url).text
    pages.append(pd.read_html(io.StringIO(html))[0])
    nxt = BeautifulSoup(html, "html.parser").select_one("a.next")
    url = urljoin(url, nxt["href"]) if nxt else None
df = pd.concat(pages, ignore_index=True)
df.shape   # (2000, 11)</code></pre>
<p>On a real site, add a pause between requests (<code>time.sleep(1)</code>) and write each page to
disk as you go, for the same reason.</p>
<h2>A correct result</h2>
<p>2,000 rows, 11 columns, every SKU unique from NWT-10000 up. 671 rows have a <i>Was</i> price.
Stock splits into 1,002 In stock, 356 Sold out, 329 Made to order and 313 Low stock &mdash; a quick
way to check nothing was skipped or doubled.</p>
'''

NOTES['live'] = '''
<p class="kicker">About this practice page</p>
<h2>A price board that moves while you watch</h2>
<p>Most of the reason to scrape a competitor&rsquo;s prices, a supplier&rsquo;s stock or a list of
open jobs is to see what changed since last time. That cannot be practised on a page that never
changes, so this one changes every minute, on a fixed rule worked out from the clock: a couple of
lines are repriced, one sells out, one leaves the board and the one that left last minute comes back.
Everything else holds still, including each row&rsquo;s <i>Updated</i> time, which is when that row
last moved.</p>
<h2>Why comparing is harder than collecting</h2>
<p>Two snapshots are easy. Knowing which differences are real is not. Rows move position when one
drops off, so comparing line 7 with line 7 reports changes that are not there. The fix is to match
rows by something that identifies them &mdash; here the SKU &mdash; and then the differences are
only the real ones: a few changed lines, one row gone and one row back.</p>
<h2>Doing it in Magic Scraper</h2>
<p>Open it on this page and export, or simply leave it. When the countdown passes zero, open it again:
the <b>Changes</b> tab compares this run with your last run of the same list. Set <i>Match rows on</i>
to SKU, and it lists what was added, removed and changed, which you can export on their own. Below the
board, the page prints what moved this minute, so you can check the answer instead of trusting it. Run
it on a <a href="../track-website-price-changes">schedule</a> and the comparison happens without you.</p>
<h2>In code</h2>
<p>The board is drawn by a script, so the HTML holds an empty table; read it in a browser, or with a
headless one. Once you have two snapshots, an outer merge on SKU does the comparison:</p>
<pre><code>m = before.merge(after, on="SKU", how="outer", suffixes=("_before", "_after"), indicator=True)
added   = m[m["_merge"] == "right_only"]
removed = m[m["_merge"] == "left_only"]
changed = m[(m["_merge"] == "both") &amp; (m["Price_before"] != m["Price_after"])]</code></pre>
<h2>A correct result</h2>
<p>Each snapshot has 25 rows and 6 columns (SKU, Product, Maker, Price, Stock, Updated). Between
two neighbouring minutes the comparison should find one row gone, one row new and three or four
changed &mdash; usually two new prices and two stock changes, one line selling out and another coming
back &mdash; with the other twenty-odd untouched. The line under the board gives the same counts for
the minute you are looking at.</p>
'''

NOTES['feed'] = '''
<p class="kicker">About this practice page</p>
<h2>Product data written for machines</h2>
<p>Most shops describe their products twice: once for people, in the page, and once for search
engines and price-comparison sites, as schema.org structured data. That second copy is usually the
cleanest data on the page &mdash; prices without currency symbols, availability as a fixed code,
ratings as numbers. This page carries twenty products both ways, as JSON-LD in the head and as
microdata in the HTML.</p>
<h2>Reading the JSON-LD</h2>
<p>The JSON-LD is a <code>&lt;script type="application/ld+json"&gt;</code> block holding an
<code>ItemList</code> of twenty <code>Product</code>s. It needs no selectors at all:</p>
<pre><code>import json, requests
from bs4 import BeautifulSoup
soup = BeautifulSoup(requests.get("https://magicscraper.app/demo/feed").text, "html.parser")
data = json.loads(soup.select_one('script[type="application/ld+json"]').string)
products = [e["item"] for e in data["itemListElement"]]
products[0]["offers"]   # {'price': '55.00', 'priceCurrency': 'USD', 'availability': '.../PreOrder', ...}</code></pre>
<h2>Reading the microdata</h2>
<p>The same facts sit in <code>itemprop</code> attributes on the visible elements. The thing to
notice is where the machine-readable value is: the price shown is &ldquo;55.00&rdquo; beside a $
sign, but the attribute <code>content="55.00"</code> is the value to keep, and availability is a
<code>&lt;link&gt;</code> to a schema.org code with no visible text at all.</p>
<h2>In Magic Scraper</h2>
<p>Open it here and it says <i>Found JSON-LD Product &times;20</i>: it prefers the structured copy
when a page has one, and gives you 20 rows and 11 columns &mdash; name, SKU, category, material, brand,
link, price, currency, availability, rating and review count &mdash; with the price as the plain number
from the data, not the text beside the $ sign. If you would rather have what the page shows, the
visible cards are one of the other lists under <b>Wrong list?</b></p>
<h2>Check one against the other</h2>
<p>The two copies agree exactly on this page: same twenty SKUs, same prices. On real sites they
often drift &mdash; the JSON-LD is cached, or describes only the first variant &mdash; so if the
numbers matter, compare them. A mismatch is a finding, not a bug in your scraper.</p>
<p>This page is not offered to search engines: its structured data describes products that are not
for sale, and that is not what structured data is for.</p>
'''

NOTES['pagers'] = '''
<p class="kicker">About these practice lists</p>
<h2>Why &ldquo;it only scraped the first page&rdquo; is the commonest complaint</h2>
<p>A scraper that pages through a list has to find the control that goes forward, and most of them
look for a link that says <i>Next</i>. Real sites rarely make it that easy. A theme draws an arrow
icon. A blog says <i>Older posts</i>. A shop in Munich says <i>Weiter</i>, one in Osaka <i>次へ</i>. A
forum shows only page numbers. A framework renders an empty element whose only clue is its class
name, or a button that runs JavaScript and has no address at all. Each of the seven lists above is
paged one of those ways, with the same thirty products, so you can see exactly which ones a tool
follows.</p>
<h2>What each one asks of a scraper</h2>
<p>The arrow needs the link&rsquo;s <code>aria-label</code> (&ldquo;Next page&rdquo;) read, because
there is no text. Page numbers need the current number found and the link to the one after it
chosen &mdash; without being fooled by a row of star ratings that also reads 1 2 3 4 5. <i>Older
posts</i> needs the direction understood: on a blog, older is forward and <i>Newer</i> is back. The
German and Japanese lists need words in other languages. The class-only link needs the markup&rsquo;s
own names read. The JavaScript button needs clicking in a real page, then waiting for the list to
change, because there is no URL to fetch.</p>
<h2>In Magic Scraper</h2>
<p>It finds all seven on its own: open it on the first page of any list and press <b>Start
crawling</b>. To see which control it chose before you start, press <b>Auto-detect
&ldquo;Next&rdquo;</b> on the Crawl tab. If a site has one it misses, <b>Pick &ldquo;Next&rdquo;
manually</b> lets you click the control yourself.</p>
<h2>A Next finder in Python</h2>
<p>The six link-based lists can be walked with one function that tries the same clues in order:
<code>rel="next"</code>, a label or word that means forward, a class with <i>next</i> in it, and
finally the number after the current page.</p>
<pre><code>import re, requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

WORDS = re.compile(r"^(next|older|weiter|次へ|suivant|siguiente)\\b|^[›»→]$", re.I)

def next_link(soup):
    for a in soup.select("a[href]"):
        label = (a.get("aria-label") or a.get_text(" ", strip=True)).strip()
        if a.get("rel") == ["next"] or WORDS.search(label) or "next" in " ".join(a.get("class", [])):
            return a["href"]
    on = soup.select_one(".pager .on")                 # page numbers only
    if on and on.get_text(strip=True).isdigit():
        a = on.find_next_sibling("a", string=str(int(on.get_text(strip=True)) + 1))
        return a["href"] if a else None

url, rows = "https://magicscraper.app/demo/pager-ja-1", 0
while url:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    rows += len(soup.select("article"))
    href = next_link(soup)
    url = urljoin(url, href) if href else None
print(rows)   # 30</code></pre>
<p>Pass <code>.content</code>, not <code>.text</code>, to BeautifulSoup: it then reads the page&rsquo;s
own charset, and the Japanese list does not turn into mojibake on a server that leaves the charset
out of its headers. The seventh list, the JavaScript button, cannot be done this way at all; it needs a
browser, or the extension.</p>
<h2>A correct result</h2>
<p>30 items over 3 pages from every list. Ten means the Next was missed; twenty usually means a
crawler went forward and then back.</p>
'''

NOTES['stockists'] = '''
<p class="kicker">About this practice page</p>
<h2>A store locator split under letters</h2>
<p>&ldquo;Where to buy&rdquo; pages, dealer lists, member directories and lists of branches are often
grouped like this: a heading for each letter, region or county, and a short list under each. It
reads well. For a spreadsheet it is awkward, because the heading is information too &mdash; the region
a dealer is in, the county a branch serves &mdash; and it is written once above its group rather than
on every line.</p>
<h2>What goes wrong</h2>
<p>There are five separate lists here, one under each letter, with three, four, two, three and two
shops. A scraper that takes &ldquo;the biggest list&rdquo; gets the four under B and stops. One that
gathers every shop without its heading gets fourteen rows and loses the grouping, which on a real
locator is usually the region you wanted to filter by.</p>
<h2>In Magic Scraper</h2>
<p>It sees that the five lists are the same kind of thing, joins them into one table and adds the
heading each shop sat under as a <i>Section</i> column: 14 rows with Section, Shop Name, Town Name and
Tel. Nothing to set.</p>
<h2>In Python</h2>
<p>Walk the groups and carry each heading down to its rows:</p>
<pre><code>soup = BeautifulSoup(requests.get("https://magicscraper.app/demo/stockists").content, "html.parser")
rows = [{"section": sec.h2.get_text(strip=True),
         "name": li.select_one(".shop-name").get_text(strip=True),
         "town": li.select_one(".town-name").get_text(strip=True),
         "tel":  li.select_one(".tel").get_text(strip=True)}
        for sec in soup.select("section.town") for li in sec.select("li")]
len(rows)   # 14</code></pre>
<h2>Using a list like this</h2>
<p>Phone numbers come through as written, with their spaces, so a spreadsheet treats them as text and
keeps the leading zero &mdash; which is what you want. On a real locator, the shop&rsquo;s own page often
has the address and opening hours; <a href="../drill-down">drill-down</a> adds those as columns, the
same way the <a href="directory.html">business directory</a> practice page does.</p>
<h2>A correct result</h2>
<p>14 rows in four columns, the first being Section A, Ashby Home &amp; Hearth, Ashby, 01530 555 014,
and the last Section E, Ember Kitchenware, Exeter.</p>
'''

NOTES['wholesale-prices'] = '''
<p class="kicker">About this practice page</p>
<h2>Volume pricing that lives on each product&rsquo;s page</h2>
<p>Trade and wholesale shops, print shops, packaging and hardware suppliers all price by quantity:
one price for one to nine, a lower one for ten to forty-nine, lower again for fifty or more. The list
page shows only &ldquo;from $1.80&rdquo;. The breaks themselves are in a small table on each
product&rsquo;s own page, next to its specifications. If you are comparing suppliers, those breaks are
the whole point.</p>
<h2>Why this is two jobs</h2>
<p>First, every product link has to be opened. Second, each product has several price breaks, so
one product is not one row. Put the breaks side by side as columns and you get &ldquo;Quantity 1,
Unit price 1, Quantity 2&hellip;&rdquo;, which cannot be sorted or compared. What you want is one row
per product per break, with the product&rsquo;s details repeated on each.</p>
<h2>In Magic Scraper</h2>
<p>Turn on <a href="../drill-down">drill-down</a> and preview the first product. It shows the
specifications (SKU, Finish, Ships in) and notices the price-break table. Tick <b>Every row of its table &mdash; one row
each</b> and run it: the four products become 12 rows, each with the product, its specifications, and
one Quantity, Unit price and Discount. Reading every product page is a Pro feature; the free version
reads the first three so you can see the result.</p>
<h2>In Python</h2>
<pre><code>url = "https://magicscraper.app/demo/wholesale-prices"
soup = BeautifulSoup(requests.get(url).content, "html.parser")
rows = []
for link in soup.select("article.product h3 a"):
    page = BeautifulSoup(requests.get(urljoin(url, link["href"])).content, "html.parser")
    specs = {tr.th.get_text(strip=True): tr.td.get_text(strip=True) for tr in page.select("table.specs tr")}
    for tr in page.select("table.tiers tbody tr"):
        qty, price, off = [td.get_text(strip=True) for td in tr.select("td")]
        rows.append({"product": link.get_text(strip=True), **specs,
                     "quantity": qty, "unit_price": price, "discount": off})
len(rows)   # 12</code></pre>
<h2>A correct result</h2>
<p>12 rows: three breaks for each of four products. The steel hinge runs from $2.40 for 1&ndash;9 to
$1.80 for 50 or more; the first break of each product has an em dash for its discount, which means
none, not missing. To compare at a given order size, filter on the quantity range that contains it.</p>
'''

# A real screenshot of the extension's result on each page (tools: shots in the
# scratchpad, composed to demo/img/<slug>-result.webp, og copy as .jpg). The
# caption says what the result is, so it reads as part of the notes.
FIGURES = {
 'stock': ("Magic Scraper beside the warehouse stock grid, showing 30 rows and 7 columns",
           "Opened on this page: 30 rows and 7 columns, read from the grid&rsquo;s ARIA roles &mdash; Product, its link, SKU, Bin, Wigan, Rotterdam and Status."),
 'catalogue': ("Magic Scraper after crawling the catalogue: 54 rows from 6 pages",
           "After <b>Start crawling</b>: 54 rows from all six pages, with the sale flag, the was price, the rating and the stock line in columns of their own."),
 'table': ("Magic Scraper beside the trade price list, showing 50 rows and 8 columns",
           "50 rows and 8 columns &mdash; the seven in the table, plus each product&rsquo;s link."),
 'directory': ("Magic Scraper after crawling the directory and reading every profile",
           "24 businesses from three pages, with Address, Phone, Email, Website, Opening hours and Established added from each profile by drill-down."),
 'stockists': ("Magic Scraper showing the 14 stockists as one table with a Section column",
           "Five lists joined into one table of 14 shops, with the letter each sat under as the <i>Section</i> column."),
 'wholesale-prices': ("Magic Scraper after drill-down, one row per price break",
           "Drill-down with one row per table row: four products become 12 rows, each with one Quantity, Unit price and Discount beside the product&rsquo;s specifications."),
 'scroll': ("Magic Scraper after an infinite-scroll crawl: 40 rows",
           "With <b>Infinite scroll</b> on: 40 rows collected as the feed loaded, and the crawl stopped on its own at the end."),
 'reviews': ("Magic Scraper after clicking Load more to the end: 48 reviews",
           "All 48 reviews, after the crawl clicked <b>Load more</b> until the button was gone."),
 'shadow': ("Magic Scraper reading 12 products from inside a shadow root",
           "12 products and 7 columns, read from inside the open shadow root."),
 'iframe': ("Magic Scraper reading the stock table inside the iframe",
           "24 rows read from inside the same-origin frame: product, link, SKU, maker, Wigan, Rotterdam and next dispatch."),
 'awkward': ("Magic Scraper showing the 10 clearance rows",
           "The 10 clearance rows. The &minus;35% in the banner is not in any row, so it is not a column &mdash; add it after the export."),
 'returns': ("Magic Scraper showing the returns log as 24 rows and 8 columns",
           "24 rows and 8 columns, kept exactly as typed &mdash; the mixed dates, refunds and statuses, and both duplicate lines."),
 'rates': ("Magic Scraper choosing the 14-row international rates table",
           "Detection takes the bigger table, the 14 international rates; <b>Another table</b> under <b>Wrong list?</b> switches to the eight domestic zones."),
 'bulk': ("Magic Scraper after crawling all 40 pages: 2,000 rows",
           "2,000 rows from 40 pages. The preview shows the first 100 to stay quick; the export holds every row."),
 'live': ("Magic Scraper reading the live price board: 25 rows",
           "25 rows from the board this minute. Open it again once the minute turns, and the <b>Changes</b> tab compares the two."),
 'feed': ("Magic Scraper reading 20 products from the page's JSON-LD",
           "Read from the JSON-LD: 20 products in 11 columns, with the price as a plain number and availability as its own column."),
 'pagers': ("Magic Scraper after following page numbers to the end: 30 products",
           "The page-numbers list, crawled: 30 products from three pages, with no Next link anywhere on them."),
}
VIDEOS = {
 'directory': ('lnpNfYghYbQ', 'Turn any business directory into a lead list in 1 click'),
 'table': ('FAcp6XF582E', 'Scrape any web table to Excel'),
 'catalogue': ('3oCmoj57Pxs', 'Scrape every page, every row, straight to CSV'),
}
FIG_CSS = ('<style>.practice-notes figure{margin:18px 0 20px}.practice-notes figure img{display:block;width:100%;height:auto;'
           'border:1px solid #e0dbd0;border-radius:10px;background:#f6f3ec}.practice-notes figcaption{font-size:13.5px;color:#5d574a;'
           'margin-top:8px;line-height:1.5}.practice-notes .watch{display:flex;gap:14px;align-items:center;margin:14px 0 6px;'
           'text-decoration:none;color:inherit}.practice-notes .watch img{width:168px;height:auto;border-radius:8px;flex:none}'
           '.practice-notes .watch span{font-weight:600}</style>')

def figure(slug):
    out = ''
    if slug in FIGURES and os.path.exists(os.path.join(DEMO, 'img', slug + '-result.webp')):
        alt, cap = FIGURES[slug]
        out += ('<figure><img src="img/%s-result.webp" width="1400" height="672" loading="lazy" decoding="async" alt="%s">'
                '<figcaption>%s</figcaption></figure>' % (slug, alt, cap))
    if slug in VIDEOS:
        vid, title = VIDEOS[slug]
        out += ('<a class="watch" href="https://www.youtube.com/watch?v=%s" rel="noopener">'
                '<img src="../assets/video/%s.webp" width="168" height="94" loading="lazy" alt="">'
                '<span>Watch it done on this page: &ldquo;%s&rdquo; (YouTube)</span></a>' % (vid, vid, title))
    return out

def main():
    for slug, body in NOTES.items():
        path = os.path.join(DEMO, slug + '.html')
        s = open(path, encoding='utf-8').read()
        s = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', s, flags=re.S)
        # the old one-paragraph note under the stock grid is folded into these notes
        if slug == 'stock':
            s = re.sub(r'<p class="aside">There is no &lt;table&gt; on this page\..*?</p>', '', s, flags=re.S)
        fig = figure(slug)
        b = body.strip()
        if fig:   # after the first section: what the page is, then what the result looks like
            i = b.index('</p>', b.index('<h2>')) + 4
            b = b[:i] + fig + b[i:]
        block = (START + CSS + FIG_CSS + '<section class="practice-notes" id="practice-notes">' + b +
                 '<p class="cta">Try it yourself: <a href="../">get Magic Scraper free</a> and open it on this page.</p>'
                 '</section>' + END)
        if '<footer class="site">' in s:
            s = s.replace('<footer class="site">', block + '<footer class="site">', 1)
        elif '</main>' in s:
            # the hub-style pages: content in <main>, each part in a .wrap
            i = s.rindex('</main>')
            s = s[:i] + START + '<div class="wrap">' + block[len(START):-len(END)] + '</div>' + END + '\n' + s[i:]
        else:
            i = s.rindex('</div></body>')
            s = s[:i] + block + s[i:]
        # its own picture when shared, not the site's generic one
        if os.path.exists(os.path.join(DEMO, 'img', slug + '-result.jpg')):
            s = re.sub(r'<meta property="og:image" content="[^"]*"',
                       '<meta property="og:image" content="https://magicscraper.app/demo/img/%s-result.jpg"' % slug, s, count=1)
        open(path, 'w', encoding='utf-8').write(s)
        print('notes:', slug, len(re.sub(r'<[^>]+>', ' ', body).split()), 'words')


if __name__ == '__main__':
    main()

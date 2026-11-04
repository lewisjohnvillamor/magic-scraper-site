#!/usr/bin/env python3
"""Notes under each sandbox page: what it is, why it is tricky, how to do it.

Written page by page, by hand, for people using Magic Scraper -- not for
programmers: no code, and every page framed as what it stands for, what makes
it hard for most tools, how Magic Scraper handles it, and what a correct
result looks like. They go below the data in an <aside class="practice-notes">
(an aside, not a <section>: a sixth <section> beside a page's own five made
them a list), as prose under headings, so the page's own data stays the only
list on it.

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
<p>This is the kind of screen a warehouse or ERP system shows: one line per product, the bin it
lives in, a count for each site and a status. Suppliers give trade customers screens like it, and
operations teams check them every morning &mdash; but there is rarely an export button.</p>
<h2>Why it is tricky</h2>
<p>There is no ordinary table here. The grid is built the way modern web apps build them, from
blocks marked as rows and cells, so Excel&rsquo;s <i>From Web</i>, Google Sheets&rsquo; import
functions and plain copy and paste come back empty or as one long column of text. Magic Scraper
reads those row and cell markings as a table, so none of that matters.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page. The 30 lines appear straight away, with the screen&rsquo;s own
headings as column names and each product&rsquo;s link kept as a column of its own. Export to
Excel or CSV, or open it in Google Sheets. On a real system with thousands of lines, where only the
rows on screen are drawn, turn on <b>Infinite scroll</b> on the Crawl tab: it scrolls the grid
itself and collects every line.</p>
<h2>What you should get</h2>
<p>30 rows and 7 columns, with the Wigan and Rotterdam counts as numbers you can add up &mdash; and no
stray header row or toolbar line among them. Tracking a screen like this over time? See
<a href="../track-website-price-changes">tracking changes on a schedule</a>.</p>
'''

NOTES['catalogue'] = '''
<p class="kicker">About this practice page</p>
<h2>An ordinary shop category, which is the point</h2>
<p>Product cards in a grid, filters down the side, a sort menu and page numbers at the bottom: this
is what most online shop categories look like, and it is the page most people want first &mdash; to
watch a competitor&rsquo;s prices, move a catalogue to another system, or get a supplier&rsquo;s
range into a spreadsheet you can sort.</p>
<h2>Why it is tricky</h2>
<p>Three things trip up simpler tools. The cards differ: some have a <i>Sale</i> badge and a
crossed-out price, a few say <i>Low stock</i>, so a tool that reads fields by position shifts
columns on the cards without them. The filter lists in the sidebar repeat too, and are easy to grab
by mistake. And the products run over six pages. Magic Scraper keeps each field in its own column
whether a card has it or not, picks the cards over the sidebar, and follows the pages for you.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper and check that the nine cards are outlined. Then press <b>Start crawling</b>
on the Crawl tab: it goes through all six pages and says when it has reached the end. Every product
also has its own page; <a href="../drill-down">drill-down</a> can add what is on it &mdash; and behind
each maker there is a chain ten levels deep, if you want to see how far that goes.</p>
<h2>What you should get</h2>
<p>54 rows from 6 pages. 25 products are on sale; on the other 29 the <i>was</i> price is simply
empty, and the rating comes out as a number (4.1), separate from the stars.</p>
'''

NOTES['table'] = '''
<p class="kicker">About this practice page</p>
<h2>A supplier&rsquo;s trade price list</h2>
<p>Wholesalers and distributors publish price lists exactly like this: a plain table of products with
a retail price, a trade price and what is in stock. It is the simplest page in the sandbox, and it is
here for that reason &mdash; it is where to start.</p>
<h2>The one thing most tools lose</h2>
<p>A plain table like this is the one case where Excel&rsquo;s <i>From Web</i> and Google
Sheets&rsquo; import work too. What they drop is the link behind each product name. Magic Scraper
keeps it as a column of its own, which matters as soon as you want each product&rsquo;s own page as
well &mdash; that is what <a href="../drill-down">drill-down</a> uses.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page and press <b>Export CSV</b>, or the arrow beside it for Excel. The
prices come through as written, with the dollar sign, so a spreadsheet treats them as text: to make
them numbers, use Find and Replace to replace <code>$</code> with nothing.</p>
<h2>What you should get</h2>
<p>50 rows and 8 columns: the seven in the table, plus each product&rsquo;s link. The same products
appear on the <a href="stock.html">warehouse stock</a> page drawn without a table at all, and on the
<a href="catalogue.html">catalogue</a> as cards over six pages &mdash; a quick way to see which kinds
of page a tool really handles.</p>
'''

NOTES['directory'] = '''
<p class="kicker">About this practice page</p>
<h2>A local directory, and the lead list behind it</h2>
<p>Trade directories, chamber of commerce member lists and &ldquo;find a tradesperson&rdquo; sites all
look like this: a short card per business, and the useful details &mdash; email, website, address,
opening hours &mdash; one click away on each business&rsquo;s own profile. If you are building a list
of businesses to contact, this is the job.</p>
<h2>Why it is two steps</h2>
<p>The list itself only has a name, a trade and a phone number, over three pages. Everything else
is on the profiles, one page per business. Magic Scraper does both in one run: it collects every
listing, then opens each profile and adds its details as columns.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page and press <b>Start crawling</b> to collect all three pages. Then,
on the Crawl tab, turn on <a href="../drill-down">drill-down</a>, preview the first profile and press
<b>Use this for all rows</b>. The free version reads the first three profiles so you can see the
result; Pro reads all of them. With Pro, <b>Compare with a file</b> takes your CRM export and marks
the businesses you do not have yet.</p>
<h2>What you should get</h2>
<p>24 businesses, and with the profiles read, six more columns: Address, Phone, Email, Website,
Opening hours and Established. Keep to business details and check the site&rsquo;s terms:
<a href="../is-it-legal-to-scrape-a-business-directory">is it legal to scrape a business directory?</a>
The whole workflow is in <a href="../lead-generation">building a B2B lead list</a>.</p>
'''

NOTES['scroll'] = '''
<p class="kicker">About this practice page</p>
<h2>A &ldquo;new arrivals&rdquo; feed with no page two</h2>
<p>Fashion shops, marketplaces, job boards and social feeds have mostly dropped numbered pages. They
show a first handful and add more as you scroll down. This page works the same way: eight products
to start, eight more each time you near the bottom, five times, and then &ldquo;No more items.&rdquo;</p>
<h2>Why it is tricky</h2>
<p>When the page opens, only the first eight exist, and nothing on the page says how many more are
coming. A tool that reads the page once gets eight rows and looks finished. Magic Scraper scrolls,
waits for the new products, adds them, and stops on its own when scrolling brings nothing new.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page, go to the Crawl tab, tick <b>Infinite scroll</b> and press
<b>Start crawling</b>. Watch the count climb; it stops by itself at the end.</p>
<h2>What you should get</h2>
<p>40 rows with no repeats, each with name, maker, a price like $192.00, the rating as a number, the
stock line and the SKU. Eight rows means the scrolling never started; 16 or 24 means it stopped
before the feed caught up.</p>
'''

NOTES['reviews'] = '''
<p class="kicker">About this practice page</p>
<h2>Product reviews behind a &ldquo;Load more&rdquo; button</h2>
<p>Reviews are some of the most useful text on the web: what buyers like, what breaks, what they
compare you with. Shops, app stores and review sites usually show a dozen and a <b>Load more</b>
button. This page has 48 reviews: 12 to start, 12 more per click, until the button disappears.</p>
<h2>Why it is tricky</h2>
<p>There are no pages to follow &mdash; the button is the only way to the rest. And each click takes
a moment to answer, as a real site does, so a tool that clicks and reads straight away gets the same
twelve again. Magic Scraper recognises the button, clicks it, waits for the new reviews to arrive,
and stops when the button is gone.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page and press <b>Start crawling</b> on the Crawl tab. Once it is
done, sorting the sheet by rating and reading the one- and two-star reviews together is the quickest
way to find what keeps going wrong.</p>
<h2>What you should get</h2>
<p>48 rows, each with the reviewer, the stars, the date, the product and the text. 31 are marked
<i>Verified purchase</i> and 17 are not, so that column is blank on 17 rows rather than shifted
along. Dates run from 12 September 2026 back to 30 April 2026.</p>
'''

NOTES['shadow'] = '''
<p class="kicker">About this practice page</p>
<h2>Products inside a web component</h2>
<p>More and more sites are built from reusable components &mdash; a product gallery, a store locator, a
widget from another company &mdash; that draw their contents in a private part of the page called a
<i>shadow root</i>. On screen it looks like any other page. To many tools, the products are simply
not there.</p>
<h2>Why it is tricky</h2>
<p>Most point-and-click tools, and the simple ways of copying a page, only look at the page&rsquo;s
main content and stop at the component&rsquo;s edge, so they find nothing. Magic Scraper looks inside
these components as it searches the page, with nothing to switch on.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page. The twelve products are found as usual; export them like any
other table.</p>
<h2>What you should get</h2>
<p>12 rows with name, maker, price, rating and SKU, plus each product&rsquo;s link. One limit worth
knowing: a component can also be made fully <i>closed</i>, and then no extension can read inside it.
That is rare on pages people want to collect from.</p>
'''

NOTES['iframe'] = '''
<p class="kicker">About this practice page</p>
<h2>A table that lives in another page</h2>
<p>Stock levels from a warehouse system, a booking calendar, a results table, a supplier&rsquo;s price
list: sites often show these by embedding another page in a frame rather than copying the data in.
To you it is one page. To most tools, the table is in a page they were never asked to read.</p>
<h2>Why it is tricky</h2>
<p>Excel&rsquo;s <i>From Web</i> and Google Sheets&rsquo; import read the outer page and report that
there is no table. When the embedded page comes from the same site, as here, Magic Scraper steps
into the frame and reads it directly.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page &mdash; the 24 rows are found inside the frame. If a frame comes
from a different site, the browser keeps every extension out of it; open the frame&rsquo;s own address
in a tab and it reads like any other page. From version 2.1, Magic Scraper notices a large frame from
another site and offers to open it for you.</p>
<h2>What you should get</h2>
<p>24 rows: product, link, SKU, maker, the counts at Wigan and Rotterdam, and next dispatch. The
Wigan column adds up to 2,830 and Rotterdam to 837 &mdash; a quick check that every row came through
as a number.</p>
'''

NOTES['awkward'] = '''
<p class="kicker">About this practice page</p>
<h2>A clearance list where the key number is outside the list</h2>
<p>Outlet sections and trade promotions often look like this: a table of products at their old
price, and a banner above it that changes everything &mdash; here, &ldquo;&minus;35% applies to every
line below&rdquo;. The price you would actually pay is never written down.</p>
<h2>Why it is tricky</h2>
<p>Any good tool finds the ten lines of the table. No tool can know on its own that the banner
applies to them &mdash; that connection is written for people. So Magic Scraper lets you point at it.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper, then <b>Wrong list?</b> &rarr; <b>Pick manually</b>. Click one of the rows,
shift-click the &minus;35% in the banner, and press <b>Use selection</b>: the ten rows come back with
the discount as a column of its own. To turn it into a price in your sheet, with <i>Was</i> in column
D, put <code>=VALUE(SUBSTITUTE(D2,"$",""))*(1-35%)</code> in a spare column and fill down. Tracking the
page on a <a href="../track-website-price-changes">schedule</a>? Keep the picked discount in the saved
setup, and a new banner shows up as a change on every row.</p>
<h2>What you should get</h2>
<p>10 rows with the discount on each. Walnut Tray was $429.00, so it is $278.85 after the discount;
Jute Tray, Bone goes from $488.00 to $317.20.</p>
'''

NOTES['returns'] = '''
<p class="kicker">About this practice page</p>
<h2>A returns log typed in by several people</h2>
<p>Back-office pages &mdash; returns, orders, tickets, timesheets &mdash; are where data gets messy,
because people type them in by hand, with different habits. This log is 24 lines of exactly that.
Getting it off the page takes one click; getting it into shape is the work.</p>
<h2>What is messy about it</h2>
<p>Dates are written three ways (2026-03-01, 06/07/2026, 11 Jan 2026). Refunds appear as $420.00,
USD 227 and a bare 341.90. Status is <i>Refunded</i>, <i>refunded</i> and <i>REFUNDED</i>. Thirteen
cells are empty, seven say N/A or a dash, some names end in an invisible space, and two returns were
logged twice. Magic Scraper exports every cell exactly as written &mdash; on purpose, so the
cleaning happens in your sheet, where you can see what changed.</p>
<h2>How to tidy it in a spreadsheet</h2>
<p>Export to Excel or Google Sheets, then: remove the two repeated lines with <b>Remove
duplicates</b> (Excel: Data tab; Google Sheets: Data &rarr; Data cleanup); make the status column
consistent with Find and Replace; take the extra spaces off names with <code>=TRIM(C2)</code>; and
decide what 06/07/2026 means for your source before converting dates, because June and July both fit.</p>
<h2>What you should get</h2>
<p>24 rows and 8 columns straight from the page &mdash; both repeated lines included, because two
identical lines in a log can be a real double return and only you can tell &mdash; and 22 once the
duplicates are removed.</p>
'''

NOTES['rates'] = '''
<p class="kicker">About this practice page</p>
<h2>Shipping rates in two tables</h2>
<p>Couriers and shops publish delivery charges like this: one table for home, one for abroad, never
the same shape. If you are comparing carriers or working out shipping costs, you usually need both.</p>
<h2>Why it is tricky</h2>
<p>A tool that takes &ldquo;the table on the page&rdquo; gives you one and leaves you wondering where
the other went. Magic Scraper opens on the bigger one &mdash; the international rates &mdash; and keeps
the other one a click away.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper: the 14 international rates are there. For the 8 domestic zones, open
<b>Wrong list?</b> and press <b>Another table</b>; the outline moves so you can see which one you have
before exporting. Keep the two in separate tabs of your sheet &mdash; their columns mean different
things.</p>
<h2>What you should get</h2>
<p>14 rows by 6 columns (Country, Code, Transit, Flat rate, Free over, Duties), or 8 rows by 5 (Zone,
Covers, Transit, Standard, Trade). Some cells are words: <i>Free</i> means 0, while a dash under
<i>Free over</i> means there is no free threshold at all. DDP means duties are paid by the sender, DAP
that they are collected on delivery.</p>
'''

NOTES['bulk'] = '''
<p class="kicker">About this practice page</p>
<h2>A big trade list: 2,000 lines over 40 pages</h2>
<p>A full supplier range, every size and finish as its own line, fifty to a page: this is what
exporting a whole wholesale catalogue or marketplace category looks like. Small pages hide what only
shows up at this size.</p>
<h2>Why it is tricky</h2>
<p>The page numbers show only a few pages at a time (1 2 3 &hellip; 40), so the <b>Next</b> link is the
only reliable way through. Forty pages also take long enough for things to go wrong: a laptop sleeps,
a tab gets closed. Magic Scraper follows Next to the end, and keeps what it collected if the run is
cut short.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on page 1 and press <b>Start crawling</b>. The count climbs page by page; the
preview shows the first 100 rows to stay quick, and the export holds every row. If the tab dies,
open the extension on the site again and it offers to <b>Recover</b> the rows. Crawling has no row
limit on the free version.</p>
<h2>What you should get</h2>
<p>2,000 rows and 11 columns, every SKU different. 671 lines have a <i>Was</i> price, and the stock
column splits into 1,002 In stock, 356 Sold out, 329 Made to order and 313 Low stock &mdash; an easy
way to check nothing was skipped or doubled.</p>
'''

NOTES['live'] = '''
<p class="kicker">About this practice page</p>
<h2>A price board that moves while you watch</h2>
<p>Most of the reason to collect a competitor&rsquo;s prices or a supplier&rsquo;s stock is to see what
changed since last time. This board changes every minute on a fixed rule: a couple of lines are
repriced, one sells out, one disappears and the one that disappeared a minute ago comes back.</p>
<h2>Why comparing is the hard part</h2>
<p>Two snapshots are easy; telling the real changes apart is not. When one line disappears the rest
move up, so comparing line 7 with line 7 reports changes that never happened. Magic Scraper matches
the rows by something that stays the same &mdash; here the SKU &mdash; and shows only what really
changed.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page. When the countdown passes zero, open it again: with Pro, the
<b>Changes</b> tab compares this run with your last one. Set <b>Match rows on</b> to SKU and it lists
what was added, removed and changed, which you can export on its own. Put it on a
<a href="../track-website-price-changes">schedule</a> and the comparison happens without you.</p>
<h2>What you should get</h2>
<p>25 rows and 6 columns each time. Between two neighbouring minutes: one line gone, one line new, and
three or four changed. The line under the board shows the same counts for the minute you are looking
at, so you can check the answer.</p>
'''

NOTES['feed'] = '''
<p class="kicker">About this practice page</p>
<h2>Product data written for machines</h2>
<p>Most shops describe their products twice: once for people, in the page, and once for search
engines and comparison sites, in a hidden structured format. That hidden copy is often the cleanest
data on the page &mdash; prices without currency signs, availability as a fixed value, ratings as
numbers. This page carries twenty products both ways.</p>
<h2>How Magic Scraper uses it</h2>
<p>When a page has that structured copy, Magic Scraper prefers it: the panel says <i>Found JSON-LD
Product &times;20</i>, and the columns come straight from the data rather than from how the page
happens to be laid out.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page and export. If you would rather have what the page shows on
screen, the visible cards are one of the other lists under <b>Wrong list?</b></p>
<h2>What you should get</h2>
<p>20 rows and 11 columns &mdash; name, SKU, category, material, brand, link, price, currency,
availability, rating and review count &mdash; with the price as a plain number (55.00, not $55.00).</p>
<p>This page is kept out of search results: its structured data describes products that are not for
sale, and that is not what structured data is for.</p>
'''

NOTES['pagers'] = '''
<p class="kicker">About these practice lists</p>
<h2>Why &ldquo;it only got the first page&rdquo; is the commonest complaint</h2>
<p>To go through a list, a scraper has to find the way to the next page, and most look for a link
that says <i>Next</i>. Real sites rarely make it that easy: an arrow icon, &ldquo;Older posts&rdquo;,
<i>Weiter</i> or <i>次へ</i>, page numbers only, a button whose only clue is its style, or a button
that loads the next page without changing the address. Each of the seven lists above is paged one
of those ways, with the same thirty products.</p>
<h2>How Magic Scraper handles them</h2>
<p>It finds all seven on its own. It reads an arrow&rsquo;s label, works out which number comes after
the current page, understands that <i>Older</i> means forward on a blog, knows the word for
&ldquo;next&rdquo; in more than 80 languages, and clicks buttons that have no address, waiting for the
list to change each time.</p>
<h2>How to do it</h2>
<p>Open any of the seven lists on its first page and press <b>Start crawling</b>. To see which control
it chose before you start, press <b>Auto-detect &ldquo;Next&rdquo;</b> on the Crawl tab. If a site ever
has one it misses, <b>Pick &ldquo;Next&rdquo; manually</b> lets you click it yourself.</p>
<h2>What you should get</h2>
<p>30 items over 3 pages from every list. Ten means the way forward was missed; twenty usually means a
crawler went forward and then back. More on this in
<a href="../scraper-only-scrapes-first-page">when a scraper only scrapes the first page</a>.</p>
'''

NOTES['stockists'] = '''
<p class="kicker">About this practice page</p>
<h2>A store locator split under letters</h2>
<p>&ldquo;Where to buy&rdquo; pages, dealer lists, member directories and branch lists are often grouped
like this: a heading for each letter, region or county, and a short list under each. The heading is
information too &mdash; usually the region you wanted to filter by &mdash; but it is written once, above
its group.</p>
<h2>Why it is tricky</h2>
<p>There are five separate small lists here, one per letter. A tool that takes the biggest list gets
the four shops under B; one that gathers every shop loses the letter. Since version 2.1, Magic
Scraper sees that the five lists belong together, joins them into one table and keeps the heading
each shop sat under as a <i>Section</i> column.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page &mdash; there is nothing to set. Phone numbers come through as
written, with their spaces, so a spreadsheet keeps the leading zero. On a real locator, each
shop&rsquo;s own page often has its address and hours; <a href="../drill-down">drill-down</a> adds
those as columns, as on the <a href="directory.html">business directory</a> page.</p>
<h2>What you should get</h2>
<p>14 rows in four columns, from Section A, Ashby Home &amp; Hearth, Ashby, 01530 555 014, to
Section E, Ember Kitchenware, Exeter.</p>
'''

NOTES['wholesale-prices'] = '''
<p class="kicker">About this practice page</p>
<h2>Volume pricing on each product&rsquo;s own page</h2>
<p>Trade and wholesale shops price by quantity: one price for one to nine, less for ten to forty-nine,
less again for fifty or more. The list shows only &ldquo;from $1.80&rdquo;; the real price breaks are
in a small table on each product&rsquo;s page. If you are comparing suppliers, those breaks are the
whole point.</p>
<h2>Why it is tricky</h2>
<p>Every product page has to be opened, and each product has several price breaks, so one product is
not one row. Side by side as columns (&ldquo;Quantity 1, Price 1, Quantity 2&hellip;&rdquo;) they cannot
be sorted or compared. What you want is one row per price break, with the product&rsquo;s details on
each &mdash; and that is what Magic Scraper gives you.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper on this page. On the Crawl tab, turn on <a href="../drill-down">drill-down</a>
and preview the first product: it shows the specifications and finds the price-break table. Tick
<b>Every row of its table &mdash; one row each</b> and run it. The free version reads the first three
products so you can see the result; Pro reads them all.</p>
<h2>What you should get</h2>
<p>12 rows &mdash; three breaks for each of four products &mdash; each with the SKU, finish, delivery
time, quantity, unit price and discount. The steel hinge runs from $2.40 for 1&ndash;9 to $1.80 for
50 or more; a dash in the first break&rsquo;s discount means none.</p>
'''

NOTES['account'] = '''
<p class="kicker">About this practice page</p>
<h2>One table out of five, every page of it</h2>
<p>Customer portals, supplier accounts and admin dashboards put several tables on one screen &mdash;
orders, invoices, shipments, messages &mdash; each with its own page numbers. The job is almost always
one of them: every invoice for the accountant, every shipment for a claim. The task here: all 40
invoices across their four pages, and not one row from the other tables.</p>
<h2>Why it is tricky</h2>
<p>The orders table above the invoices has a <i>Next</i> button that looks exactly like the
invoices&rsquo; one, and it comes first. A tool that takes &ldquo;the Next button on the page&rdquo;
pages the orders and ends up with ten invoices. The other tables add their own twists: shipments page
with a button that has no address, returns with <i>Show more</i>, and messages have no pages at all.
Since version 2.1, Magic Scraper uses the Next button that belongs to the table you chose.</p>
<h2>How to do it</h2>
<p>Magic Scraper opens on the invoices, the biggest table. For another one, use <b>Wrong list?</b>
&rarr; <b>Another table</b> until it is outlined, or <b>Pick manually</b>. Then press <b>Start
crawling</b>. To collect all five tables, do them one after another and export each.</p>
<h2>What you should get</h2>
<p>Invoices: 40 rows, INV-2026-1301 to INV-2026-1340, all different, no order numbers among them.
Orders: 18. Shipments: 15. Returns: 12. Messages: 5.</p>
'''

NOTES['parts'] = '''
<p class="kicker">About this practice page</p>
<h2>The page most wholesale sites are built on</h2>
<p>Parts suppliers, trade counters and most catalogue sites share one layout: categories down the left
with a count beside each, a filter under them, a featured strip across the top, the products as a
table with page numbers underneath, and a footer full of links. The two jobs people actually have:
this category&rsquo;s table, every page of it &mdash; and then every category&rsquo;s, in one sheet.</p>
<h2>Why it is tricky</h2>
<p>Each of those blocks is a list a tool can grab by mistake. The featured strip has its own
<i>Next</i> arrow, which a careless tool clicks instead of paging the table. And going through the
categories, each one has its own pages: reading only the first page of each gets 52 parts out of 74
and looks finished.</p>
<h2>How to do it</h2>
<p>Open Magic Scraper: it picks the parts table, and <b>Start crawling</b> pages it by its own page
numbers &mdash; 26 fasteners from three pages. For every category: <b>Wrong list?</b> &rarr; <b>Another
table</b> until the category list is outlined, then on the Crawl tab turn on
<a href="../drill-down">drill-down</a>, preview the first category, tick <b>Every row of its table
&mdash; one row each</b> and run it. Each category&rsquo;s parts come back one row per part, every page
of them (from version 2.1), with the category on each row. The free version reads the first three
categories; Pro reads them all.</p>
<h2>What you should get</h2>
<p>This category: 26 rows, FX-1001 to FX-1026. Every category: 74 rows &mdash; 26 Fasteners, 8 Hinges,
14 Brackets, 5 Handles, 12 Castors and 9 Shelf supports &mdash; every part number different.</p>
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
           "The 10 clearance rows as detection finds them. The &minus;35% in the banner is in no row; <b>Pick manually</b> and a shift-click on it adds it as a column."),
 'returns': ("Magic Scraper showing the returns log as 24 rows and 8 columns",
           "24 rows and 8 columns, kept exactly as typed &mdash; the mixed dates, refunds and statuses, and both duplicate lines."),
 'rates': ("Magic Scraper choosing the 14-row international rates table",
           "Detection takes the bigger table, the 14 international rates; <b>Another table</b> under <b>Wrong list?</b> switches to the eight domestic zones."),
 'bulk': ("Magic Scraper after crawling all 40 pages: 2,000 rows",
           "2,000 rows from 40 pages. The preview shows the first 100 to stay quick; the export holds every row."),
 'live': ("Magic Scraper reading the live price board: 25 rows",
           "25 rows from the board this minute. Open it again once the minute turns, and with Pro the <b>Changes</b> tab compares the two."),
 'feed': ("Magic Scraper reading 20 products from the page's JSON-LD",
           "Read from the JSON-LD: 20 products in 11 columns, with the price as a plain number and availability as its own column."),
 'account': ("Magic Scraper after crawling the invoices table: 40 rows from four pages",
           "Invoices chosen and crawled: 40 rows from four pages, and none from the orders table whose pager comes first."),
 'parts': ("Magic Scraper after drill-down over the six categories: 74 parts",
           "From the category list, drill-down with one row per table row: every page of every category, 74 parts, each with its category."),
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
        s = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', s, flags=re.S)
        # the old one-paragraph note under the stock grid is folded into these notes
        if slug == 'stock':
            s = re.sub(r'<p class="aside">There is no &lt;table&gt; on this page\..*?</p>', '', s, flags=re.S)
        fig = figure(slug)
        b = body.strip()
        if fig:   # after the first section: what the page is, then what the result looks like
            i = b.index('</p>', b.index('<h2>')) + 4
            b = b[:i] + fig + b[i:]
        block = (START + CSS + FIG_CSS + '<aside class="practice-notes" id="practice-notes" aria-label="About this practice page">' + b +
                 '<p class="cta">Try it yourself: <a href="../">get Magic Scraper free</a> and open it on this page.</p>'
                 '</aside>' + END)
        if '<footer class="site">' in s:
            # The store-style pages close their .shell before the footer, so the
            # guide goes in a .shell of its own: without one it sat flush to the
            # left edge of the window, with no padding.
            wrapped = START + '<div class="shell">' + block[len(START):-len(END)] + '</div>' + END
            s = s.replace('<footer class="site">', wrapped + '<footer class="site">', 1)
        elif '<footer class="cols">' in s:
            s = s.replace('<footer class="cols">', block + '<footer class="cols">', 1)
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

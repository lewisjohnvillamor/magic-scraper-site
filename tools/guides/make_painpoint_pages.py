#!/usr/bin/env python3
"""Build the pain-point guide pages for magicscraper.app from PAGES below.

Each page follows the site's guide template (copy-table-from-website-to-excel.html):
HowTo + FAQPage + BreadcrumbList JSON-LD, hero, sections, an FAQ, the shared
header/footer. Run from the repo root: python3 tools/guides/make_painpoint_pages.py .
"""
import html, json, re, sys

ROOT = sys.argv[1]
CWS = "https://chromewebstore.google.com/detail/magic-scraper/lcdaikobgjpakcgbkdedoapnckeobbck"
EDGE = "https://microsoftedge.microsoft.com/addons/detail/magic-scraper/palbdbeiidhladdgdmlolckafkjackfp"

def plain(s):
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)

def page(p):
    url = "https://magicscraper.app/" + p["slug"]
    ld = []
    if p.get("howto"):
        ld.append({
            "@context": "https://schema.org", "@type": "HowTo",
            "name": p["howto"]["name"], "description": p["howto"]["description"],
            "totalTime": p["howto"].get("time", "PT5M"),
            "tool": [{"@type": "HowToTool", "name": "Magic Scraper browser extension"}],
            "step": [{"@type": "HowToStep", "name": plain(n), "text": plain(t),
                      "url": url + "#" + p["howto"]["anchor"]} for n, t in p["howto"]["steps"]],
        })
    ld.append({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": plain(q),
                        "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in p["faq"]],
    })
    ld.append({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Magic Scraper", "item": "https://magicscraper.app/"},
            *([{"@type": "ListItem", "position": 2, "name": "Guides", "item": "https://magicscraper.app/guides"}]
              if p.get("eyebrow", "Guide") == "Guide" else []),
            {"@type": "ListItem", "position": 3 if p.get("eyebrow", "Guide") == "Guide" else 2,
             "name": p["crumb"], "item": url},
        ],
    })
    ldhtml = "\n".join('<script type="application/ld+json">\n%s\n</script>' % json.dumps(x, indent=2, ensure_ascii=False) for x in ld)
    e = lambda s: html.escape(s, quote=True)
    secs = "\n".join(p["sections"])
    faq = "\n".join("""      <details>
        <summary>%s</summary>
        <p>%s</p>
      </details>""" % (q, a) for q, a in p["faq"])
    assert len(plain(p["title"])) <= 65, (p["slug"], len(plain(p["title"])))
    assert len(plain(p["desc"])) <= 160, (p["slug"], len(plain(p["desc"])))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{p['title']}</title>
<meta name="description" content="{e(plain(p['desc']))}" />
<link rel="canonical" href="{url}" />
<link rel="icon" href="assets/icon.png" />
<link rel="preload" as="font" type="font/woff2" href="assets/fonts/fraunces-var.woff2" crossorigin />
<link rel="preload" as="font" type="font/woff2" href="assets/fonts/archivo-var.woff2" crossorigin />
<link rel="stylesheet" href="style.css" />
<script>document.documentElement.classList.add('js');</script>
<meta property="og:type" content="article" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{e(plain(p['title']))}" />
<meta property="og:description" content="{e(plain(p.get('og', p['desc'])))}" />
<meta property="og:image" content="https://magicscraper.app/assets/og.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
{ldhtml}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="wrap">
  <div class="masthead">
    <a class="logo" href="/">
      <span class="glyph" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="var(--paper)"
             stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 20 L14 10" /><path d="M18 3 v5 M15.5 5.5 h5" />
        </svg>
      </span>
      <span class="wordmark">Magic Scraper</span>
    </a>
    <button class="burger" type="button" aria-label="Menu"
            aria-expanded="false" aria-controls="site-nav"><span class="bars"></span></button>
    <nav id="site-nav">
      <a href="/guides">Guides</a>
      <a href="/desktop">Desktop</a>
      <a href="/#price">Pricing</a>
      <a href="/demo/">Sandbox</a>
      <a href="/services">Services</a>
      <a href="/support">Support</a>
    </nav>
  </div>
</header>

<main id="main">
<div class="wrap">
  <div class="hero">
    <p class="eyebrow">{p.get('eyebrow', 'Guide')}</p>
    <h1>{p['h1']}</h1>
    <p class="standfirst">{p['standfirst']}</p>
    <div class="actions">
      <a class="btn" href="{CWS}" target="_blank" rel="noopener">Install for Chrome &mdash; free</a>
      <a class="btn btn-quiet" href="{EDGE}" target="_blank" rel="noopener">Install for Edge</a>
      <span class="aside">{p['aside']}</span>
    </div>
  </div>
</div>

<div class="wrap">

{secs}
  <section id="faq">
    <h2>Reasonable questions</h2>
    <div class="qa">
{faq}
    </div>
  </section>

</div>

</main>

<div class="wrap">
  <footer>
    <span>Magic Scraper</span>
    <a href="/">Home</a>
    <a href="/guides">Guides</a>
    <a href="/desktop">Desktop</a>
    <a href="/privacy">Privacy</a>
    <a class="sep" href="/support">Support</a>
  </footer>
</div>

<script src="nav.js" defer></script>
</body>
</html>
"""

def sec(id_, h2, body, deck=None):
    d = f'\n    <p class="deck">{deck}</p>' if deck else ""
    return f"""  <section id="{id_}">
    <h2>{h2}</h2>{d}
{body}
  </section>
"""

def claim(*paras):
    return '    <div class="claim">\n' + "\n".join(f"      <p>{x}</p>" for x in paras) + "\n    </div>"

def steps(items):
    out = ['    <div class="steps">']
    for i, (h, t) in enumerate(items, 1):
        out.append(f"""      <div class="step">
        <span class="n">{i:02d}</span>
        <h3>{h}</h3>
        <p>{t}</p>
      </div>""")
    out.append("    </div>")
    return "\n".join(out)

def table(head, rows):
    out = ['    <table class="compare">',
           "      <thead><tr><td></td>" + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead>",
           "      <tbody>"]
    for r in rows:
        out.append("        <tr><td>%s</td>%s</tr>" % (r[0], "".join(f'<td class="{c}">{t}</td>' for c, t in r[1:])))
    out += ["      </tbody>", "    </table>"]
    return "\n".join(out)

PAGES = []

# ---------------------------------------------------------------- 1. no subscription
PAGES.append(dict(
    slug="web-scraper-no-subscription",
    crumb="No subscription",
    title="A web scraper with no subscription, credits or free trial",
    desc="A Chrome web scraper with no credits, no account and no trial that turns into a charge. Pay $25 once, or never: nothing renews and nothing to cancel.",
    og="No credits, no trial that renews, no account. What is free, what the one-time Pro licence adds, and the questions to ask any scraper before you pay.",
    h1="A web scraper with no <i>meter</i> running.",
    standfirst="Credits that run out halfway through a list. A free trial that becomes a charge on day one. A cancel button you can't find. Those are the most common complaints in scraper reviews, and none of them is about scraping. Here is how Magic Scraper is priced instead, and what to ask any tool before you pay.",
    aside="Free with no time limit. Pro is $25, once.",
    sections=[
        sec("free", "What you get without paying", "\n".join([
            claim("Install it and it works: no account, no email, no card. The free version has no clock "
                  "on it and no monthly allowance. It finds tables, lists and card grids, lets you pick "
                  "rows by hand, crawls <b>every page</b> of a paginated list, and exports CSV, Excel or "
                  "JSON as often as you like. Nothing is counted, so nothing runs out."),
            table(["Free", "Pro, $25 once"], [
                ["Find tables and lists, pick by hand", ("y", "Yes"), ("y", "Yes")],
                ["Crawl every page: Next, page numbers, infinite scroll, Load more", ("y", "Unlimited"), ("y", "Unlimited")],
                ["Export CSV, XLSX, JSON or copy", ("y", "Unlimited"), ("y", "Unlimited")],
                ["Recover a run whose tab closed", ("y", "Yes"), ("y", "Yes")],
                ["<a href=\"/drill-down\">Open the page behind each row</a>", ("q", "First 3 rows of a run"), ("y", "Every row, up to 10 levels")],
                ["One setup over a list of addresses", ("q", "First 2 addresses"), ("y", "Every address")],
                ["Named setups, compare runs, compare with a file, schedules", ("n", "No"), ("y", "Yes")],
                ["Account, credits or monthly fee", ("y", "None"), ("y", "None")],
            ]),
            claim("The two limits on the free side are stated here, and on the drill-down and "
                  "list controls in the extension before a run starts, so nobody finds them at the "
                  "end of a job."),
        ])),
        sec("credits", "Why credits feel like a trap", claim(
            "Credit-based scrapers charge per page loaded, per row returned or per AI action. That can be "
            "fair, but it makes the cost of a job unknowable until it's done. Reviewers keep describing "
            "the same three surprises: credits spent on a run that failed, credits spent on pages they "
            "didn't select, and a feature that costs thousands of credits on a plan that comes with a "
            "hundred.",
            "Magic Scraper runs in your browser, on your computer, so there is no server time to bill "
            "for. A failed run costs nothing but the minute you spent on it, and a 10,000-row list costs "
            "the same as a 10-row one.")),
        sec("once", "What \"pay once\" means here", claim(
            "Pro is a licence key from Gumroad: <b>$25, one time</b> ($19 for the first 100 buyers). It "
            "never renews, so there is nothing to cancel. Every update since carries across, so there is "
            "no second purchase for a new version. If it isn't what you needed, ask for a refund within "
            "seven days.",
            "Try before paying: drill-down runs on the first three rows of any run for free, so you see "
            "exactly which fields come back from the site you care about before you spend anything.")),
        sec("checklist", "Five questions to ask any scraper before you pay", steps([
            ("Does the trial turn into a charge?", "If a card is needed for a free trial, find out the date and amount it bills, and whether it's monthly or a year up front."),
            ("What counts as a credit?", "A page, a row, a subpage, an AI call? Is a failed or blocked page charged?"),
            ("Where do I cancel?", "Look for the cancel button before you subscribe, not after. In-app cancellation is the sign of a fair plan."),
            ("What is the refund policy?", "\"Non-refundable\" is common. A stated refund window is worth more than a long trial."),
            ("What happens to my data?", "Is it scraped on their servers, stored in their cloud, sent to an AI model? See <a href=\"/web-scraper-extension-privacy\">how to check</a>."),
        ])),
    ],
    faq=[
        ("Is there a web scraper with no subscription?", "Yes. Magic Scraper's free version has no time limit and no account, and its Pro licence is a one-time $25 payment that never renews. There are no credits on either."),
        ("Is the free version a trial?", "No. It has no clock and no monthly allowance. Detection, unlimited pagination and export stay free. Pro adds drill-down on every row, lists of addresses beyond two, saved setups, comparisons and schedules."),
        ("Do I need a credit card or an account?", "No. Install it from the Chrome Web Store or Edge Add-ons and use it. A card is only involved if you choose to buy Pro on Gumroad."),
        ("What happens if a run fails?", "Nothing is charged, because nothing is metered. If the tab closes during a crawl, the rows collected so far can be brought back the next time you open the extension on that site, free."),
        ("Can I get a refund?", "Yes, within seven days of buying Pro, with no questions asked."),
        ("Does Pro include future updates?", "Yes. Updates arrive through the Chrome Web Store or Edge Add-ons, and a Pro licence keeps working across them."),
    ],
))

# ---------------------------------------------------------------- 2. first page only
PAGES.append(dict(
    slug="scraper-only-scrapes-first-page",
    crumb="Stops at page 1",
    title="Web scraper only scraping the first page? Here's why",
    desc="Why a scraper stops at page 1: JavaScript Next buttons, Load more, infinite scroll and rate limits. How to scrape every page into one sheet, free.",
    og="JavaScript Next buttons, Load more, infinite scroll and rate limits: why scrapers stop at page 1, and how to get every page into one sheet.",
    h1="Stuck on <i>page one</i>? It's usually one of five things.",
    standfirst="The run says it finished, the sheet has 20 rows, and the site has 2,000. Stopping at the first page is the complaint people post most about scrapers. The cause is nearly always one of five page patterns, and each has a fix.",
    aside="Crawling every page is free, with no page limit.",
    sections=[
        sec("why", "Five reasons a scraper stops at page 1", steps([
            ("The Next button isn't a link", "Many sites draw Next as a button that runs JavaScript, with no address behind it. A tool that only follows links sees nothing to follow."),
            ("It's a Load more button", "\"Load more\" and \"Show more results\" add rows to the same page without changing the address, so a tool waiting for a new page waits forever."),
            ("It's infinite scroll", "New rows appear only when the page is scrolled to the bottom. Nothing scrolls, nothing loads."),
            ("The tool clicked the wrong control", "A pager has Next, numbers and Last. Pick Last by mistake and you get page 1 and the final page, and nothing between."),
            ("The site pushed back", "Ask for pages too fast and a site answers with \"too many requests\" or a check page. Many tools stop silently and call it finished."),
        ])),
        sec("how", "Getting every page", "\n".join([
            steps([
                ("Open the first page", "Open the list or search results and let it finish loading. Click the Magic Scraper icon: the rows are found and shown with named columns."),
                ("Press Auto-detect \"Next\"", "On the <b>Crawl</b> tab. It looks for the page's own <code>rel=\"next\"</code> link first, then scores the buttons on the page by their words and position, and handles Load more buttons and infinite scroll as well as page links."),
                ("Wrong control? Pick it yourself", "Press <b>Pick &ldquo;Next&rdquo; manually</b> and click the real Next or Load more button once."),
                ("Start crawling", "Every page is added to the same table, with a pause between pages. When it ends it says why: no further Next link, the last page, Load more gone, or you stopped it."),
            ]),
            claim("Crawling is free and has no page limit. A <b>Max pages</b> box is there if you only want "
                  "the first few."),
        ]), deck="With the extension, on any paginated list."),
        sec("slow", "When a site says \"too many requests\"", claim(
            "A site that limits requests answers a fast scraper with a 429 error or a \"slow down\" page. "
            "Magic Scraper waits and retries, and tells you if it had to stop. If a site keeps pushing "
            "back, choose <b>Gentle</b> pacing: slower, and the least likely to be blocked. <b>Fast</b> is "
            "there only for sites you own or that allow it.",
            "If the site shows a \"verify you're human\" check, the run stops and hands you the tab. It "
            "never tries to get past the check: you can answer it yourself and carry on, or leave the "
            "site alone.")),
        sec("practice", "Practise on pages built to break scrapers", claim(
            "The <a href=\"/demo/\">sandbox</a> has a catalogue with numbered pages, a Load more list "
            "and an infinite-scroll feed, all fictional and none rate-limited, so you can see each "
            "pattern work before you try a real site.")),
    ],
    howto=dict(name="Scrape every page of a paginated list", description="Collect every page of a paginated list, Load more list or infinite scroll into one table.",
               anchor="how", steps=[
                   ("Open the first page", "Open the list and click the Magic Scraper icon."),
                   ("Find Next", "On the Crawl tab press Auto-detect Next, or Pick Next manually and click the button."),
                   ("Start crawling", "Press Start crawling. Every page joins the same table until there are no more."),
                   ("Export", "Press CSV or XLSX."),
               ]),
    faq=[
        ("Why does my web scraper only scrape the first page?", "Usually because the Next button runs JavaScript instead of linking to a page, the list uses Load more or infinite scroll, the tool picked the wrong pager control, or the site rate-limited it. A scraper that clicks buttons, scrolls and waits on 429 errors gets past all four."),
        ("How do I scrape a page with a Load more button?", "Open the page, click the Magic Scraper icon, and on the Crawl tab press Auto-detect Next, or Pick Next manually and click Load more once. Start crawling clicks it until it disappears."),
        ("How do I scrape infinite scroll?", "The same way: Start crawling scrolls the page and collects new rows as they load, until the page stops adding them."),
        ("Is there a page limit?", "No. Crawling is free with no page limit. Set Max pages if you want fewer."),
        ("Why did the crawl stop early?", "The extension says why when it ends: no further Next link, the last page, Load more disappeared, the site asked it to slow down, a human check, or you pressed Stop. Rows collected so far are kept."),
        ("What if it finds the wrong Next button?", "It finds Next differently: it prefers the page's rel=next link and scores buttons by their words and position, and you can pick the control by hand if it guesses wrong."),
    ],
))

# ---------------------------------------------------------------- 3. doesn't support this site
PAGES.append(dict(
    slug="scraper-not-working-on-this-site",
    crumb="Not working on a site",
    title="Scraper says it doesn't support this site? What to try",
    desc="When a scraper finds nothing, the wrong table or an empty sheet: why it happens, what to try in a minute, and which sites no honest tool should promise.",
    og="Nothing found, the wrong table, an empty sheet: why scrapers fail on some sites, what to try, and which sites no honest tool should promise.",
    h1="When a scraper finds <i>nothing</i>.",
    standfirst="It worked on the demo, then on the site you actually need it says it doesn't support it, or exports an empty sheet. Here is why that happens, what to try in the next minute, and which sites no honest tool should promise you.",
    aside="Free: detection, picking by hand and export.",
    sections=[
        sec("try", "Try these first", steps([
            ("Let it finish loading", "Many pages draw their rows a second or two after the page appears, or only as you scroll. Wait, scroll down once, then click the icon again."),
            ("Press Another table", "A page often has several lists: menus, filters, related items. If the outline is on the wrong one, cycle to the next."),
            ("Pick it by hand", "Click one row of what you want. The extension finds the rest that look the same. Then shift-click any extra field, such as a price that sits outside the row, and it joins as a column."),
            ("Open the page behind each row", "If the list only shows names, the details may live on each item's own page. <a href=\"/drill-down\">Drill-down</a> opens them and adds their fields, free for 3 rows."),
        ])),
        sec("why", "Why some pages come back empty", claim(
            "<b>The rows aren't there yet.</b> Pages that load as you scroll hold only what has been "
            "shown. Scroll first, or crawl it as <a href=\"/scraper-only-scrapes-first-page\">infinite "
            "scroll</a>.",
            "<b>The data is in a frame from another site.</b> Maps, booking widgets and embedded "
            "tables often come from a different address inside the page. Open that address in its own "
            "tab and scrape it there.",
            "<b>It isn't text.</b> Prices drawn as images, charts drawn on a canvas and tables inside a "
            "PDF have no text for any scraper to read.",
            "<b>You're not signed in, or the session expired.</b> Magic Scraper runs in your own browser, "
            "so it sees pages you are signed into, the same as you do. It never signs in for you. Check "
            "the site's terms before collecting from pages behind a login.",
            "<b>The page is a check, not the content.</b> \"Just a moment\", \"verify you're human\" or "
            "\"access denied\" pages have nothing to scrape. Magic Scraper stops and hands you the tab "
            "rather than trying to get past them.")),
        sec("honest", "Sites no honest tool should promise", claim(
            "Some of the most requested sites, LinkedIn and Facebook among them, forbid automated "
            "collection in their terms and actively detect scraping extensions. A tool that promises "
            "them is promising to break those rules on your account. Magic Scraper doesn't, and won't "
            "get past captchas or bot checks.",
            "For business lists, the same companies are usually in public directories that are made "
            "to be read: see <a href=\"/list-of-businesses-in-an-area\">where local business lists "
            "live</a> and <a href=\"/business-directory-scraper\">scraping a business directory</a>.")),
        sec("tell", "Tell us which site", claim(
            "If a public page should work and doesn't, send the address from <a href=\"/support\">"
            "support</a>, or copy a diagnostic report from the extension's menu: it holds errors only, "
            "with web addresses removed. Sites that fail for many people are fixed in the next update.")),
    ],
    faq=[
        ("Why does my scraper say it doesn't support this site?", "Usually the rows haven't loaded yet, the data sits in a frame from another site, it's an image or PDF rather than text, the page needs a sign-in, or it's a bot check page. Wait and scroll, try another table, or pick the rows by hand."),
        ("How do I scrape a page where automatic detection fails?", "Click one row of what you want and the extension selects the rest that look the same. Shift-click extra fields to add them as columns."),
        ("Can it scrape pages I'm logged into?", "It reads what your browser shows, including pages you're signed into, and never signs in for you. Whether you may collect from those pages depends on the site's terms."),
        ("Does it work on LinkedIn?", "No, and it doesn't try. LinkedIn's terms forbid automated collection and it detects scraping extensions."),
        ("Can it get past captchas?", "No. When a site shows a human check, the run stops and hands you the tab."),
        ("Why does my scraper return an empty CSV?", "The page was read before its rows appeared, or the wrong list was selected. Check the preview before exporting: if it shows the right rows, the file will too."),
    ],
))

# ---------------------------------------------------------------- 4. missing data
PAGES.append(dict(
    slug="scraper-missing-data",
    crumb="Missing rows or columns",
    title="Scraper missing rows, columns or phone numbers? Why",
    desc="Why scraped data has missing rows, blank columns or lost phone numbers, and how to stop Excel dropping leading zeros or garbling UTF-8 characters.",
    og="Missing rows, blank columns, phone numbers gone, garbled characters in Excel: what causes each and how to fix it.",
    h1="Rows missing, columns blank, <i>phone numbers</i> gone.",
    standfirst="A sheet that looks complete but is 20% short is worse than an error. Here is what causes missing rows, blank or wrong columns and mangled phone numbers, and how to check the result before you rely on it.",
    aside="Free: detection, crawling and export to Excel, CSV or JSON.",
    sections=[
        sec("rows", "Missing rows", claim(
            "<b>They hadn't loaded.</b> On scrolling pages only the rows already shown exist. Crawl the "
            "page as infinite scroll so new rows are collected as they appear.",
            "<b>The crawl ended early.</b> Check the end-of-crawl message and the pages counter: the "
            "extension says why it stopped. If a site asked it to slow down, use Gentle pacing and run "
            "it again.",
            "<b>Duplicates were dropped.</b> When a site shows the same rows again on a later page, "
            "they are collected once. That is a smaller sheet, not a lost one.",
            "<b>The tab closed mid-run.</b> Open the extension on that site again: it offers back the "
            "rows collected so far, free.")),
        sec("cols", "Blank or wrong columns", claim(
            "<b>The field isn't on the list.</b> Lists often show a name and a town, and keep the phone, "
            "website and email on each item's own page. <a href=\"/drill-down\">Drill-down</a> opens "
            "those pages and adds their fields as columns.",
            "<b>The field is outside the row.</b> A price or badge drawn beside the row rather than in "
            "it isn't picked up automatically. Shift-click it once and it joins as a column.",
            "<b>The value appears only on click.</b> Some directories hide the phone number behind a "
            "\"show number\" button. It isn't in the page until someone clicks, so no scraper reads it "
            "from the list.",
            "<b>Badly named columns.</b> Double-click a header to rename it, click it to leave it out. "
            "Your choices are remembered for that site.")),
        sec("excel", "When Excel mangles the export", "\n".join([
            claim("<b>Phone numbers lose their leading zero</b> or turn into 4.47E+11 when a CSV is opened in "
                  "Excel, because Excel guesses they are numbers. Export <b>XLSX</b> instead: every cell is "
                  "written as text, so 0207&hellip; stays 0207&hellip;.",
                  "<b>Accents and symbols turn into &Atilde;&copy;</b> when a file has no marker saying it is "
                  "UTF-8. Magic Scraper's CSV includes that marker, so Excel reads caf&eacute; as caf&eacute;.",
                  "<b>A cell that starts with = runs as a formula</b> when the file opens, which a hostile "
                  "page can abuse. CSV exports defuse those cells; XLSX cells are never evaluated."),
        ])),
        sec("maps", "A word on Google Maps", claim(
            "Lead lists from Google Maps are the single most common source of \"no phone numbers\" "
            "complaints about scrapers: the list shows names, and the phone and website sit in each "
            "place's panel. Magic Scraper isn't built or tested for Google Maps, and Google's terms "
            "restrict automated collection. For local business lists, public directories are the "
            "better source: see <a href=\"/list-of-businesses-in-an-area\">a list of businesses in "
            "any area</a>.")),
    ],
    faq=[
        ("Why is my scraper missing rows?", "The rows hadn't loaded when the page was read, the crawl stopped early, or repeated rows were collected once. Crawl scrolling pages as infinite scroll, check why the crawl ended, and use Gentle pacing on sites that push back."),
        ("Why are phone numbers missing from my scraped data?", "Often the list doesn't hold them: they're on each listing's own page, or behind a show-number button. Drill-down adds fields from each listing's page; numbers hidden until a click aren't in the page at all."),
        ("How do I stop Excel removing leading zeros from phone numbers?", "Export XLSX instead of CSV. Every cell is written as text, so leading zeros and long numbers stay as they are."),
        ("Why does my CSV show strange characters in Excel?", "Excel needs a marker to read a CSV as UTF-8. Magic Scraper's CSV includes it, so accented letters and symbols open correctly."),
        ("How do I add a column the scraper missed?", "Hold Shift and click the missing field on the page. It's added as a column for every row."),
        ("Does it scrape Google Maps?", "It isn't built or tested for Google Maps, and Google restricts automated collection. Public business directories are the better source for local lead lists."),
    ],
))

# ---------------------------------------------------------------- 5. privacy
PAGES.append(dict(
    slug="web-scraper-extension-privacy",
    crumb="Scraper extension privacy",
    title="Is your web scraper extension safe? Check what it sends",
    desc="Is a scraper extension safe? Check what it can see and send: its permissions, privacy disclosures, network requests and current owner, in ten minutes.",
    og="Permissions, privacy disclosures, network requests and ownership: a ten-minute check for any scraper extension, and Magic Scraper's own answers.",
    h1="Is your scraper extension <i>safe</i>? Check what it sends.",
    standfirst="A scraper extension sees every page you point it at, and often every page you visit. Extensions change hands, and a new owner can change what one collects. You don't need to trust anyone's word: here is a ten-minute check you can run on any of them, Magic Scraper included.",
    aside="Magic Scraper: your scraped data never leaves your browser.",
    sections=[
        sec("check", "A ten-minute check for any extension", steps([
            ("Read the permissions", "In Chrome, open <code>chrome://extensions</code>, press <b>Details</b>. \"Read and change all your data on all websites\" means it can see every page you open, not just the one you scrape."),
            ("Read the privacy disclosures", "On the store listing, open <b>Privacy practices</b>. Look for \"Web history\", \"Personally identifiable information\" or \"Website content\" being collected."),
            ("Watch its traffic", "Open the page, press <b>F12</b>, choose <b>Network</b>, then scrape. Requests to a domain that isn't the site you're on are the extension talking to someone."),
            ("Check who owns it now", "Look at the publisher on the listing and the developer's website. When a popular extension is sold, the name stays the same and the owner changes."),
            ("Look for consent screens", "A screen asking you to \"accept all\" before the tool works is asking for something. Read what."),
        ])),
        sec("ours", "Magic Scraper's answers", "\n".join([
            claim("<b>Your data:</b> what you scrape stays in your browser until you save a file. Finding a "
                  "table, picking one by hand and exporting it make no network requests at all. There is "
                  "no account and no server of ours for anything to go to."),
            table(["When", "What is requested"], [
                ["Crawling or drill-down", ("y", "Further pages of the site you're on, after you press Start")],
                ["Activating Pro", ("y", "Your licence key to Gumroad, once, to confirm the purchase")],
                ["Install and uninstall", ("y", "A welcome page opens, and a page asking why on removal")],
                ["Anything else", ("y", "Nothing: no analytics, no tracking, no AI service")],
            ]),
            claim("<b>Permissions:</b> it asks for access to the tab you click it on, to save downloads and to "
                  "open the side panel. Wider access, such as reading other tabs for a crawl or keeping a "
                  "schedule, is optional and asked for only when you use the feature that needs it. Each "
                  "one is explained on the <a href=\"/privacy\">privacy page</a>.",
                  "Run the check above on it. If you ever see a request that isn't in this table, tell us."),
        ])),
        sec("why", "Why it matters for scraping", claim(
            "Scraping work is often confidential: a prospect list, a competitor's prices, research "
            "nobody has published yet. A tool that sends the pages you visit, or your results, to its "
            "own servers or an AI model is sharing that work, whatever its terms say about it.",
            "For how the ownership of one popular scraper changed, see <a href=\"/instant-data-scraper-alternative#who\">"
            "who makes Instant Data Scraper now</a>.")),
    ],
    faq=[
        ("Are web scraper extensions safe?", "Some are and some collect more than you'd expect. Check the permissions, the store's privacy disclosures and the network requests while you scrape, and look at who owns the extension now."),
        ("Does Magic Scraper send my data anywhere?", "No. Scraped data stays in your browser until you save a file. Detection and export make no network requests. The only requests are further pages of the site you're crawling, and a one-time licence check with Gumroad if you buy Pro."),
        ("Why does a scraper extension need access to all websites?", "To work on whatever site you open, and to crawl pages in the background. In Magic Scraper that wider access is optional and requested only when a feature needs it."),
        ("How do I see what an extension sends?", "Open DevTools with F12, choose the Network tab, and use the extension. Any request to a domain other than the site you're on came from somewhere else, often the extension."),
        ("Does Magic Scraper use AI or send pages to a server?", "No. Detection runs in your browser with no AI service and no server of ours."),
        ("What happens when an extension is sold?", "The listing usually keeps its name and users, and the new owner can change what it collects in an update. Check the publisher name and the privacy disclosures after a big update."),
    ],
))

# ---------------------------------------------------------------- 6. changelog
def release(id_, ver, when, badge, items):
    when = f"<b>{badge}.</b> {when}" if badge else when
    lis = "\n".join(f"        <li>{x}</li>" for x in items)
    return f"""  <section id="{id_}">
    <h2>{ver}</h2>
    <p class="deck">{when}</p>
    <ul class="ticks">
{lis}
    </ul>
  </section>
"""

PAGES.append(dict(
    slug="changelog",
    eyebrow="Changelog",
    crumb="Changelog",
    title="Magic Scraper changelog: every update, in plain words",
    desc="What changed in each Magic Scraper update: new features, fixes and anything removed or moved to Pro. The version in the Chrome and Edge stores now is 1.22.2.",
    og="Every Magic Scraper update in plain words, including what was removed or moved to Pro.",
    h1="What changed, <i>update</i> by update.",
    standfirst="Updates arrive by themselves through the Chrome Web Store and Edge Add-ons, once each one clears store review. This page lists what each one changed, in plain words, including anything that was removed or moved to Pro, so an update never surprises you.",
    aside="In the stores now: v1.22.2.",
    sections=[
        release("v1-22-3", "v1.22.3", "Built 17 October 2026, tested, not in the stores yet.", "Next update", [
            "<b>Business directories get named columns</b>: Name, Phone, City, State, Postcode, Website and Map Link, instead of generic labels, on chamber of commerce and Yellow Pages-style directories.",
            "<b><a href=\"/drill-down\">Drill-down</a> reads a member's profile page</b>: address, phone, fax, email, website and social pages, leaving out the directory's own header, footer and links.",
            "<b>Research paper pages</b> (arXiv, PubMed, journals): drill-down reads the title, authors, date, journal, DOI, PDF and abstract.",
            "Links on pages that set a different base address now point to the right pages.",
            "A table that a page fills in later is no longer offered as rows with nothing in them.",
            "Larger buttons and clearer text in the popup.",
        ]),
        release("v1-22-2", "v1.22.2", "15 October 2026.", "In the Chrome and Edge stores now", [
            "A pick made by hand from the side panel shows its columns there straight away.",
            "Includes 1.22.1, which never went out on its own: when the rows on screen each link to a page of their own, the Data tab says so, and <b>Show me</b> takes you to drill-down.",
            "A first install opens a page showing where the icon went (new extensions hide in the puzzle-piece menu). Removing the extension opens one optional question on our website.",
        ]),
        release("v1-22-0", "v1.22.0", "1 October 2026.", None, [
            "<b>Keep it open beside the page</b> in the browser's side panel: it stays while you click and follows the tab you're on.",
            "<b>Reddit, Amazon search, Hacker News, PubMed and arXiv</b> read into named columns. <a href=\"/supported-sites\">What each gives</a>.",
            "Wikipedia-style tables get their real headers, two-row headers included. Cards laid out three to a row come back as one list. Lists built from web components are found.",
            "Image columns hold the whole address of the original image, not a resized copy. Columns are no longer named after styling classes.",
            "Fixes from two read-throughs of the code (1.21.8 and 1.21.9): a Next button drawn as an icon no longer ends the crawl at page 2, a Next link that loops back no longer crawls forever, columns with the same header keep all their cells, and comparing with a file catches numbers that differ only in the last digit.",
        ]),
        release("v1-21", "v1.21", "22 to 25 September 2026.", None, [
            "<b>One setup over a list of pages</b>: paste the addresses, and the page you're on is crawled first, then each address in a tab of its own with the same setup, drill-down included. All of it comes back as one sheet with a List column.",
            "<b>Changed</b>: a list of pages is free for the first two addresses; Pro runs them all.",
            "A queued run's rows survive the popup closing. Drilled rows whose page showed nothing are kept instead of thrown away. An empty pick no longer fails the run.",
        ]),
        release("v1-20", "v1.20.14 to 1.20.20", "20 to 22 September 2026.", None, [
            "<b>Recovering a run whose tab closed is free</b>, no longer Pro.",
            "<b>Removed</b>: the CSV auto-save during long runs. It could stop on a file chooser every few thousand rows; recovery keeps those rows without interrupting you.",
            "<b>A &ldquo;verify you're human&rdquo; check stops the run</b> and hands you the tab, instead of retrying into it.",
            "Stop responds at once, instead of finishing the pause it was pressed during. A schedule that had lapsed no longer shows as active.",
            "Detection: menus of links, page layouts and font-size classes no longer win over the real list, or name its columns.",
        ]),
        sec("earlier", "Earlier", claim(
            "<b>1.17</b> compared a run with the last one of the same list. <b>1.16.1</b> added named "
            "setups you can reuse and export. <b>1.16.0</b> brought back runs whose tab closed. Each "
            "of those has grown since; the entries above say how.")),
        sec("promise", "How updates work", claim(
            "Each update is checked by Chrome and Microsoft before it reaches you, then installs by "
            "itself. A Pro licence keeps working across every update: there is no paid upgrade.",
            "When an update removes something, or moves it between Free and Pro, it is listed here "
            "under that version, in words, as the entries above show. If something you relied on "
            "changed and isn't listed, <a href=\"/support\">tell us</a>.")),
    ],
    faq=[
        ("Which version of Magic Scraper is in the stores?", "Version 1.22.2, on both the Chrome Web Store and Edge Add-ons. Version 1.22.3 is built and tested and goes to the stores next."),
        ("How do Magic Scraper updates arrive?", "Automatically, through the Chrome Web Store or Edge Add-ons, once each update has cleared store review. You don't need to reinstall."),
        ("Do I have to pay for updates?", "No. A Pro licence is paid once and keeps working across every update."),
        ("Will an update remove a feature I use?", "Anything removed, or moved between Free and Pro, is listed on this page under the version that changed it."),
    ],
))

for p in PAGES:
    path = f"{ROOT}/{p['slug']}.html"
    open(path, "w", encoding="utf-8").write(page(p))
    print("wrote", path, len(plain(p["title"])), len(plain(p["desc"])))

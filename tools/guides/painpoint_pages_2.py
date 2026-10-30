"""Four more pain-point guides, from what people report about scrapers in
forums and reviews: a crawl that stops partway, columns named x193iq5w or
[object Object], being blocked or shown a captcha, and a popup that closes
the moment the page is clicked.

Anything that ships in the next update is marked with a "next update" tag, as
the language pages are, until the stores serve it.
"""


def painpoint_pages_2(sec, claim, steps, table):
    soon = ''   # 2.1.0 is in the stores: nothing here is waiting any more
    pages = []

    # ------------------------------------------------------------ stops partway
    pages.append(dict(
        slug="scraper-stops-after-a-few-pages",
        crumb="Stops partway",
        title="Web scraper stops after a few pages? Why, and how to finish",
        desc="Why a crawl stops at page 10 or 20, skips rows or closes without a word, and how to carry on from where it stopped instead of starting over.",
        og="Why a crawl stops at page 10 or 20, skips rows or closes without a word, and how to carry on from where it stopped.",
        h1="It got to <i>page twelve</i>, then stopped. Now what?",
        standfirst="Not the first page: the run got going, collected a few hundred rows, and then stopped, or closed with no message, or came back with gaps. In forum threads about every scraper this comes up again and again. There are a handful of causes, and a crawl that says which one it hit is most of the fix.",
        aside="Crawling is free, with no page limit. A stopped crawl keeps its rows.",
        sections=[
            sec("why", "Why a crawl stops partway", steps([
                ("The site asked it to slow down", "A 429 \"too many requests\" or 503 answer means the site is rate-limiting you. Retrying straight away makes it worse; waiting, for as long as the site asks, usually works."),
                ("A \"verify you are human\" page appeared", "A check page in place of page 13 has no rows on it. A tool that reads it as data stops with \"nothing found\", or worse, carries on and saves the check page's text as a row."),
                ("The pages started repeating", "Some sites send page one again, or the same last page, once you go past the end. A crawl that cannot tell keeps going for ever, or adds the same rows twice."),
                ("The tab closed, crashed or navigated away", "The rows of most extension crawls live in the page. Close the tab at row 4,000 and they are gone."),
                ("You pressed Stop, then Start", "Many tools start again from page one, find nothing new on the pages they already have, and decide the list is finished."),
            ])),
            sec("how", "What Magic Scraper does about each", "\n".join([
                steps([
                    ("It says why it stopped", "Every crawl ends with its reason on screen: no further Next link, the last page, Load more gone, the site stopped answering, a human check, or Stop. A run that stopped short never says it finished."),
                    ("It waits when a site pushes back", "On a 429 or 503 it waits and retries, honouring the site's own Retry-After up to four minutes, and says so while it waits. Choose <b>Gentle</b> pacing for sites that keep pushing back."),
                    ("It hands you a human check", "The run stops and the page with the check is opened in front of you. It never tries to get past it. Clear it yourself and press Start: the crawl carries on from the page it never read."),
                    ("It notices repeats", "Two pages in a row that add no new rows end the crawl, with that reason, instead of looping."),
                    ("It keeps the rows if the tab dies", "Rows are kept as the crawl goes. Open the extension on the same site again and it offers to recover the run, on the page it reached."),
                    ("Start after Stop carries on" + soon, "Stop, then Start, picks up at the page after the last one read, and so does Start after the max-pages limit you set."),
                ]),
                claim("Rows collected before a stop are kept either way. Nothing is charged per page or per row, "
                      "so a run that stopped costs nothing to finish."),
            ]), deck="And what you can do."),
            sec("gaps", "Rows missing from the middle", claim(
                "When a sheet has the first pages and the last ones but gaps between, the usual cause is a "
                "page that loaded slowly: the tool read it before its new rows had appeared. Magic Scraper "
                "waits for new rows after each click or scroll before reading them, and a page that fails "
                "to load is retried, never silently skipped.",
                "If rows are still missing, compare the row count with what the site says it has. The "
                "<a href=\"/scraper-missing-data\">missing data guide</a> covers the other causes.")),
        ],
        howto=dict(name="Finish a crawl that stopped partway", description="Carry on a web scraping crawl from the page it stopped on.",
                   anchor="how", steps=[
                       ("Read why it stopped", "The status line says why the crawl ended."),
                       ("Fix the cause", "Clear a human check in the tab that opened, choose Gentle pacing for a site that rate-limits, or raise Max pages."),
                       ("Press Start again", "The crawl carries on from the first page it has not read."),
                       ("Export", "Press CSV or XLSX: every page is in one table."),
                   ]),
        faq=[
            ("Why does my scraper stop after a few pages?", "Most often the site started rate-limiting it, showed a human check, began repeating pages past the end, or the tab closed. A scraper that says why it stopped tells you which, and Magic Scraper does on every run."),
            ("Can I continue a crawl instead of starting over?", "Yes. After a human check or the max-pages limit, pressing Start carries on from the page it never read. The same goes for Stop and for a site that stopped answering."),
            ("I closed the tab during a crawl. Are the rows gone?", "No. They are kept as the crawl goes. Open Magic Scraper on the same site and it offers to recover the run."),
            ("Will it get past a captcha for me?", "No, and no honest tool should. It stops, puts the page in front of you, and carries on once you have answered it yourself."),
            ("Is there a limit on pages or rows?", "No. Crawling is free, with no page or row limit."),
        ],
    ))

    # ------------------------------------------------------------ messy columns
    pages.append(dict(
        slug="scraper-column-names-object-object",
        crumb="Messy column names",
        title="Scraper columns named x193iq5w or [object Object]? Why",
        desc="Why scraped columns come out as CSS class names like x193iq5w, or cells read [object Object], and how to get columns named Price, Date and Link instead.",
        og="Why scraped columns come out named x193iq5w, or cells read [object Object], and how to get columns named Price, Date and Link.",
        h1="Columns called <i>x193iq5w</i> are not your data's fault.",
        standfirst="You export a list and the headers read x193iq5w, x1i10hfl href, css-1x2y3z. Some cells say [object Object]. Half the columns are empty, and tags are spread over Tag 2 to Tag 14. It is a common sight with one-click scrapers, and it comes from how they name what they find.",
        aside="Named columns, rename and drop: all free.",
        sections=[
            sec("why", "Where names like x193iq5w come from", steps([
                ("The column is named after a CSS class", "A scraper that does not know what a value is names its column after the element's class. Modern sites generate those classes when they are built: x193iq5w, css-1x2y3z, sc-bdVaJa. They mean nothing to a person and change whenever the site is rebuilt."),
                ("[object Object] is a value that was never turned into text", "A tool that copies a structure where it should copy its text writes the programming language's placeholder into the cell. The data was there; the tool did not read it out."),
                ("Tags become Tag 2 to Tag 14", "A record with a varying number of the same thing &mdash; tags, categories, thumbnails &mdash; comes out as one column per position, each mostly empty."),
                ("The same link appears five times", "A card wrapped in a link, with the title, picture and button all linking to the same page, gives the same address in several columns."),
            ])),
            sec("how", "How Magic Scraper names its columns", "\n".join([
                steps([
                    ("From the page's own headers and labels first", "A table's header row, two-row headers included; a definition list's terms; \"Phone:\" and \"Address:\" labels beside their values; the page's structured data."),
                    ("Then from what the values are", "A column of prices is <b>Price</b>, dates are <b>Date</b>, addresses <b>Link</b>, pictures <b>Image</b>, and a class name is used only when it is a real word like <code>product-title</code>, never a build hash."),
                    ("Values are always text", "Every cell is the text you see, the address a link goes to, or the picture's address. There is no [object Object]."),
                    ("Repeats are tidied", "A column identical to another is dropped, an image's alt text that repeats the name is folded in, and tags of varying number are merged into one Tag column" + soon + "."),
                ]),
                claim("Still not right? Click a column header to drop it, double-click it to rename it, and "
                      "the names you choose are remembered for that site and used in every export."),
            ]), deck="Readable names, without setting anything up."),
            sec("compare", "Side by side", table(["Some one-click scrapers", "Magic Scraper"], [
                ("Column names", ("no", "CSS classes: x193iq5w, x1i10hfl href"), ("yes", "Price, Date, Link, Image, the page's own headers")),
                ("Objects in cells", ("no", "[object Object]"), ("yes", "Always the visible text, or the link or image address")),
                ("Tags and categories", ("no", "Tag 2 &hellip; Tag 14, mostly empty"), ("yes", "One Tag column" + soon)),
                ("Rename and drop", ("partial", "Varies"), ("yes", "Click to drop, double-click to rename, remembered per site")),
            ])),
        ],
        faq=[
            ("Why are my scraped column names random letters?", "They are the page's CSS class names, which modern sites generate automatically. A scraper that falls back on them gives you names like x193iq5w. Magic Scraper names columns from the page's headers and labels, or from the values, instead."),
            ("What does [object Object] mean in a scraped spreadsheet?", "The tool copied a programming structure where it should have copied its text. The value was on the page but never read out. Magic Scraper writes the text you see, or the link or image address."),
            ("Can I rename columns?", "Yes. Double-click a column header in the preview to rename it, click it to drop it. Your choices are remembered for that site."),
            ("Why do I get Tag 2, Tag 3 ... Tag 14?", "Each record has a different number of tags and the tool made a column per position. Magic Scraper merges them into one Tag column, the tags separated by commas."),
        ],
    ))

    # ------------------------------------------------------------ blocked
    pages.append(dict(
        slug="web-scraper-blocked-captcha",
        crumb="Blocked or captcha",
        title="Scraper blocked, rate-limited or shown a captcha? What to do",
        desc="Why sites block scrapers with 429 errors, access denied pages and captchas, and how to collect a list politely without being blocked.",
        og="Why sites block scrapers with 429 errors, access denied pages and captchas, and how to collect a list politely.",
        h1="Blocked? The site is telling you <i>something</i>.",
        standfirst="\"Too many requests\". \"Access denied\". \"Just a moment...\". A captcha in place of page eight. Being blocked is one of the most common scraping complaints, and most of the time it is the site saying the requests came too fast, or from somewhere it does not trust.",
        aside="It never solves captchas and uses no proxies. It slows down.",
        sections=[
            sec("why", "Why sites block scrapers", steps([
                ("Too fast", "Dozens of pages a minute, at even intervals, look like a machine because they are one. Rate limits answer with 429 \"too many requests\"."),
                ("From a server, not a person", "Cloud scrapers run from data-centre addresses that many sites refuse outright, or meet with a check page on every visit."),
                ("Without your session", "A server-side tool is not signed in and has none of your cookies, so the site treats it as a stranger."),
                ("On a site that forbids it", "Some sites do not allow automated collection at all, whatever the speed."),
            ])),
            sec("how", "How Magic Scraper avoids it", "\n".join([
                steps([
                    ("It runs in your own browser", "Pages are read in your browser, from your connection, with your session, the way you would read them by hand. There is no server of ours in between and no data-centre address."),
                    ("It paces itself", "A random pause between pages, longer for detail pages. <b>Gentle</b> is the slowest and the least likely to be blocked, <b>Normal</b> suits most sites, and <b>Fast</b> is for sites you own."),
                    ("It backs off", "A 429 or 503 answer makes it wait, as long as the site's Retry-After asks, up to four minutes, and try again, saying so on screen."),
                    ("It stops at a human check", "A \"verify you are human\" page stops the run and is put in front of you. It never tries to get past one."),
                ]),
                claim("It uses no proxies, rotates nothing and solves no captchas. If a site keeps refusing, "
                      "the honest answer is that it does not want to be collected this way."),
            ]), deck="By not looking like a robot hammering the site."),
            sec("when", "If you are still blocked", claim(
                "Choose Gentle pacing, crawl fewer pages at a time, and avoid running the same list over and "
                "over. Check the site's terms: many offer an export, an API or a data feed that is quicker "
                "and allowed.",
                "Some sites, LinkedIn among them, do not allow automated collection, and no tool you can "
                "trust should promise to get round that. The <a href=\"/scraper-not-working-on-this-site\">guide "
                "to sites that don't work</a> has more.")),
        ],
        faq=[
            ("Why does my scraper get a 429 too many requests error?", "The site limits how fast it answers one visitor, and the scraper went over. Slowing down, and waiting as long as the site's Retry-After asks before trying again, fixes most of them. Magic Scraper does both."),
            ("Will Magic Scraper solve captchas?", "No. It stops at a human check and shows you the page; you can answer it yourself and carry on, or leave the site alone."),
            ("Does it use proxies or rotate IP addresses?", "No. It runs in your own browser from your own connection, which is also why sites block it far less than server-based scrapers."),
            ("Which pacing should I choose?", "Normal for most sites, Gentle for any site that has pushed back, and Fast only for sites you own or that allow it."),
            ("Is scraping a site that blocks me legal?", "It depends on the site's terms and your country's law. If a site keeps blocking automated access, treat that as an answer. The guide to scraping business directories goes into more detail."),
        ],
    ))

    # ------------------------------------------------------------ popup closes
    pages.append(dict(
        slug="scraper-popup-keeps-closing",
        crumb="Popup keeps closing",
        title="Scraper popup closes when you click the page? Keep it open",
        desc="Why an extension's popup closes the moment you click the page, and two ways to keep a scraper open while you work: the side panel and its own window.",
        og="Why an extension's popup closes when you click the page, and two ways to keep a scraper open: the side panel and its own window.",
        h1="The popup closed <i>again</i>. It doesn't have to.",
        standfirst="You open the scraper, click the page to pick a field, and the popup is gone, taking the table with it. Every browser extension popup does this: the browser closes it the moment focus leaves it, and nothing an extension does can change that. What it can do is not live in a popup.",
        aside="Both ways are free.",
        sections=[
            sec("why", "Why the popup closes", claim(
                "A toolbar popup belongs to the browser, not to the page. Chrome, Edge and Firefox close it "
                "whenever you click anywhere else, switch tabs or press Escape. That is fine for a quick "
                "export and frustrating for anything longer: picking fields by hand, watching a crawl, "
                "copying rows across.",
                "Magic Scraper's rows live in the page, not in the popup, so closing it loses nothing; open "
                "it again and the table is still there. But not having to reopen it is better.")),
            sec("how", "Two ways to keep it open", "\n".join([
                steps([
                    ("Beside the page: the side panel", "Open the &#9881; menu and choose <b>Keep open beside the page</b>. Magic Scraper moves into the browser's side panel (the sidebar in Firefox), stays there while you click, scroll and pick, and follows the tab in front."),
                    ("A window of its own", "Open the &#9881; menu and choose <b>Open in its own window</b>. Magic Scraper opens as a window with its own place in the taskbar: move it, resize it, put it on another screen, pin it. It reads the tab it was opened from."),
                ]),
                claim("In either, picking by hand works without anything closing: click the block your rows "
                      "come from, shift-click extra fields, and the table updates as you go."),
            ]), deck="Pick the one that suits your screen."),
            sec("which", "Side panel or window?", table(["Side panel", "Own window"], [
                ("Where", ("yes", "Beside the page, in the same window"), ("yes", "Anywhere, its own window")),
                ("Which tab it reads", ("yes", "Whichever tab is in front"), ("yes", "The tab it was opened from")),
                ("Taskbar", ("partial", "Part of the browser window"), ("yes", "Its own entry, can be pinned")),
                ("Best for", ("yes", "Working through several tabs"), ("yes", "A big table on a second screen")),
            ])),
        ],
        faq=[
            ("Why does my scraper extension close when I click the page?", "Browsers close an extension's toolbar popup whenever focus leaves it. No extension can stop that, but Magic Scraper can move into the side panel, or open in its own window, which stay open."),
            ("Do I lose my data when the popup closes?", "No. The rows are kept in the page; open the popup again and the table is still there."),
            ("How do I open Magic Scraper in its own window?", "Open the \u2699 menu and choose Open in its own window. It opens as a separate window that you can move, resize and pin to the taskbar."),
            ("Does the side panel work in Firefox?", "Yes: Firefox calls it the sidebar, and the same menu item opens it."),
        ],
    ))

    # ------------------------------------------------------------ duplicates
    pages.append(dict(
        slug="scraper-duplicate-rows",
        crumb="Duplicate rows",
        title="Scraped data full of duplicate rows? Why, and how to stop it",
        desc="Why a scrape of 261 links comes back with 16,000 rows, why the export does not match the preview, and how to get each row once.",
        og="Why a scrape of 261 links comes back with 16,000 rows, why the export differs from the preview, and how to get each row once.",
        h1="Asked for 261 rows, got <i>16,000</i>?",
        standfirst="One user on a scraper forum asked for 261 links and got more than 16,000 rows, the same links over and over. Others find the export has rows the preview did not, or is missing ones it did. Duplicates are rarely the site's doing: they come from how the tool walks the pages.",
        aside="Every row once, and the export is the table you see. Free.",
        sections=[
            sec("why", "Where duplicates come from", steps([
                ("The last page is read again and again", "Past the end of a list, many sites send the last page, or page one, again. A tool that only stops when Next disappears reads it until something gives."),
                ("Infinite scroll is read whole each time", "A scrolling list keeps every row on the page, so each pass reads the earlier rows again. Unless the tool remembers what it has, they are added every time."),
                ("A selector matches more than one thing", "Each record holds several elements that match, so each record turns into several rows."),
                ("One row opens many pages", "Following every link on a detail page multiplies rows on purpose. A tool that repeats the parent row when it runs out of pages makes copies that look like data."),
            ])),
            sec("how", "How Magic Scraper keeps each row once", "\n".join([
                steps([
                    ("Rows already collected are not added again", "Each new page's rows are checked against the ones already held, column by column, so a page read twice, or the top of a scrolling list read again, adds nothing."),
                    ("Repeating pages end the crawl", "Two pages in a row with nothing new, or a Next link that leads back to a page already read, end it, and it says so."),
                    ("A record is one row", "Rows are found as repeated blocks on the page, the way you see them, and each block is read once, whatever it holds."),
                    ("Drill-down out of pages says so once" + soon, "When a row\u2019s page budget runs out, one row says it stopped, instead of a copy of the parent for every link left over."),
                ]),
                claim("Drop a row you do not want with the &times; beside it. Rows that are identical in every "
                      "column are kept as they are, and the &times; removes just the one you clicked."),
            ]), deck="Without setting anything up."),
            sec("export", "When the export does not match the preview", claim(
                "The preview draws the first 100 rows of a large run, and says so: &ldquo;Showing the first "
                "100 of 2,000 rows. Exports include all of them.&rdquo; Every export, CSV, Excel, JSON or "
                "copy, writes the same table you see, with your dropped columns, renamed columns and "
                "filter applied, and the status line says how many rows went into the file.",
                "If the page behind the popup has been closed or reloaded, it no longer holds the rows. The "
                "extension refuses to export the 100-row preview as if it were the run, and "
                "the rows of a crawl that stopped can be brought back with Recover run.")),
        ],
        faq=[
            ("Why does my scraper export duplicate rows?", "Usually because it read the last page, or the top of an infinite-scroll list, again and again without remembering what it already had. Magic Scraper checks each page's rows against the ones it holds and adds only new ones."),
            ("Why is my export different from the preview?", "Large runs show only the first 100 rows in the preview; the export has all of them. Magic Scraper says this under the table, and the export applies exactly the columns, renames and filter you see."),
            ("Can I remove duplicates in Excel instead?", "Yes: Data, Remove Duplicates. But it is better not to collect them, because a crawl reading the same page again is also a crawl that has stopped making progress."),
            ("Does it remove rows that only look alike?", "No. Only rows identical in every column are treated as the same. Two products with the same name and different prices stay two rows."),
        ],
    ))

    return pages

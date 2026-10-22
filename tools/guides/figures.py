"""Figures for the pain-point guides: real screenshots, inline SVG diagrams
(coloured from the site's tokens, so they follow dark mode) and click-to-play
YouTube boxes. Imported by make_painpoint_pages.py."""
import html as _h

def shot(src, alt, caption, w=1280, h=800):
    return f"""    <figure class="fig">
      <img src="{src}" alt="{_h.escape(alt, quote=True)}" width="{w}" height="{h}" loading="lazy" />
      <figcaption>{caption}</figcaption>
    </figure>"""

def video(vid, title, short=False):
    w, h = (540, 960) if short else (960, 540)
    t = _h.escape(title, quote=True)
    return f"""    <div class="yt{' short' if short else ''}" data-id="{vid}" data-title="{t}">
      <a href="https://www.youtube.com/watch?v={vid}" aria-label="Play video: {t} (YouTube)"><img src="assets/video/{vid}.webp" alt="" width="{w}" height="{h}" loading="lazy" /></a>
    </div>
    <p class="yt-cap">Video: {_h.escape(title)}. It plays from YouTube when you press play.</p>"""

def diagram(svg, label, caption):
    return f"""    <figure class="fig">
      {svg.strip().replace('<svg ', f'<svg role="img" aria-label="{_h.escape(label, quote=True)}" class="dg" ', 1)}
      <figcaption>{caption}</figcaption>
    </figure>"""

# --- five kinds of "more results" --------------------------------------------
def _row(y, control, title, sub):
    return f"""<rect class="b-card" x="1" y="{y}" width="638" height="96" rx="10"/>
{control}
<text x="262" y="{y+42}" font-size="26" font-weight="600">{title}</text>
<text x="262" y="{y+74}" font-size="22" class="t-mute">{sub}</text>"""

PAGER_SVG = '<svg viewBox="0 0 640 540" xmlns="http://www.w3.org/2000/svg">' + "".join([
    _row(2, '<text x="40" y="60" font-size="26" class="t-acc" text-decoration="underline">Next ›</text>',
         "A Next link", "Has an address: most tools follow it."),
    _row(110, '<rect class="b-acc" x="30" y="138" width="130" height="44" rx="8"/><text x="95" y="168" font-size="22" text-anchor="middle" class="t-acc">Next ›</text>',
         "A Next button", "Runs a script, with no address."),
    _row(218, '<rect class="b-fill-acc" x="30" y="246" width="190" height="44" rx="22"/><text x="125" y="276" font-size="22" text-anchor="middle" style="fill:var(--paper)">Load more</text>',
         "Load more", "Same page, more rows added."),
    _row(326, '<line class="rule" x1="34" y1="350" x2="200" y2="350"/><line class="rule" x1="34" y1="368" x2="180" y2="368"/><line class="rule" x1="34" y1="386" x2="196" y2="386"/><path class="l-acc" d="M224 346 v40 m-12 -12 l12 12 l12 -12"/>',
         "Infinite scroll", "Rows appear as you scroll down."),
    _row(434, '<text x="30" y="492" font-size="22" class="t-mute">‹ 1 2 3 …</text><text x="138" y="492" font-size="22" class="t-warm" text-decoration="line-through">Last</text><text x="196" y="492" font-size="22" class="t-acc">›</text>',
         "Numbers, Next and Last", "Click Next, not Last."),
]) + '</svg>'

# --- Excel leading zeros ------------------------------------------------------
def _sheet(x, head, rows, cls):
    out = [f'<rect class="b-card" x="{x}" y="60" width="296" height="196" rx="10"/>',
           f'<text x="{x+20}" y="44" font-size="22" font-weight="600">{head}</text>',
           f'<text x="{x+20}" y="98" font-size="20" class="t-mute">Phone</text>',
           f'<line class="rule" x1="{x}" y1="114" x2="{x+296}" y2="114"/>']
    for i, v in enumerate(rows):
        y = 160 + i * 62
        out.append(f'<text x="{x+20}" y="{y}" font-size="24" class="t-mono {cls}">{v}</text>')
        if i == 0: out.append(f'<line class="rule" x1="{x}" y1="{y+22}" x2="{x+296}" y2="{y+22}"/>')
    return "".join(out)

ZEROS_SVG = ('<svg viewBox="0 0 640 270" xmlns="http://www.w3.org/2000/svg">'
             + _sheet(1, "CSV opened in Excel", ["2079460123", "4.47911E+11"], "t-warm")
             + _sheet(343, "XLSX export", ["02079460123", "447911123456"], "t-acc")
             + '</svg>')

# --- what leaves the browser ----------------------------------------------------
def _box(x, y, w, h, lines, cls="b-card", tcls=""):
    t = "".join(f'<text x="{x+w/2}" y="{y+ (h/2) - (len(lines)-1)*14 + 8 + i*28}" font-size="21" text-anchor="middle" class="{tcls}">{l}</text>' for i, l in enumerate(lines))
    return f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>{t}'

PRIVACY_SVG = ('<svg viewBox="0 0 640 470" xmlns="http://www.w3.org/2000/svg">'
    + _box(1, 10, 180, 96, ["The page", "you're on"])
    + _box(230, 10, 180, 96, ["Magic Scraper,", "in your browser"], "b-acc", "")
    + _box(459, 10, 180, 96, ["Your CSV or", "Excel file"])
    + '<path class="l-acc" d="M184 58 h40 m-10 -9 l10 9 l-10 9"/><path class="l-acc" d="M413 58 h40 m-10 -9 l10 9 l-10 9"/>'
    + '<text x="1" y="160" font-size="21" class="t-mute">The only other requests, each one started by you:</text>'
    + _box(1, 180, 200, 100, ["More pages of", "the same site,", "when you crawl"])
    + _box(220, 180, 200, 100, ["Gumroad, once,", "to check a", "Pro licence"])
    + _box(439, 180, 200, 100, ["Your own Google", "Sheet, if you", "send to it (Pro)"])
    + '<text x="1" y="320" font-size="21" class="t-mute">Never:</text>'
    + _box(1, 344, 200, 92, ["A server of ours", "(there isn't one)"], tcls="t-mute")
    + _box(220, 344, 200, 92, ["Analytics or", "tracking"], tcls="t-mute")
    + _box(439, 344, 200, 92, ["An AI service"], tcls="t-mute")
    + ''.join(f'<circle cx="{x}" cy="352" r="15" style="fill:var(--warm)"/><path d="M{x-6} 346 l12 12 m0 -12 l-12 12" style="stroke:var(--paper);stroke-width:3"/>' for x in (186, 405, 624))
    + '</svg>')

# --- credits vs pay once (illustration) ------------------------------------------
CREDITS_SVG = ('<svg viewBox="0 0 640 330" xmlns="http://www.w3.org/2000/svg">'
    + '<path class="l-ink" d="M60 20 V270 H630"/>'
    + '<text x="345" y="314" font-size="22" text-anchor="middle" class="t-mute">Rows scraped</text>'
    + '<text x="24" y="150" font-size="22" text-anchor="middle" class="t-mute" transform="rotate(-90 24 150)">What you pay</text>'
    + '<path class="l-warm" d="M60 250 H160 V214 H260 V170 H360 V120 H460 V74 H560 V30 H620"/>'
    + '<text x="80" y="50" font-size="22" class="t-warm">Credits: grows with every row</text>'
    + '<path class="l-acc" d="M60 226 H620"/>'
    + '<text x="380" y="216" font-size="22" class="t-acc">Pro: $25, once</text>'
    + '<path class="l-dash" d="M60 266 H620"/>'
    + '<text x="380" y="256" font-size="22" class="t-mute">Free: $0</text>'
    + '</svg>')

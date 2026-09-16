#!/usr/bin/env python3
"""Extend the sandbox's drill-down chain from three levels to ten.

The chain ran catalogue -> product -> maker -> sourcing and stopped. The
listings say drill-down can be "chained as many levels deep as needed", and
there was nowhere to check that past three. Northwind now traces a material all
the way to the standard its auditor worked to, which is what a real
traceability record looks like and gives ten levels of genuinely different
fields.

  L1  product        item*.html          (existing)
  L2  maker          maker-*.html        (existing)
  L3  sourcing       sourcing-*.html     (existing, gains a link onward)
  L4  material lot   lot-*.html
  L5  supplier       supplier-*.html
  L6  origin site    origin-*.html
  L7  certificate    cert-*.html
  L8  certifying body auditor-*.html
  L9  audit report   report-*.html
  L10 standard       method-*.html

Deeper levels are shared between branches, the way they are in a real supply
chain: several lots come from one supplier, several certificates cite one
standard.
"""

import glob
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "demo")

STRIP = ('<div class="strip">Free shipping on trade orders over <b>$400</b> '
         '&middot; Samples dispatched same day</div>')

HEADER = ('<header class="site"><div class="shell bar">'
          '<a class="brand" href="catalogue.html">North<b>wind</b> <span>Supply</span></a>'
          '<nav><a href="catalogue.html">Catalogue</a><a href="table.html">Trade list</a>'
          '<a href="scroll.html">New arrivals</a><a href="awkward.html">Clearance</a></nav>'
          '<div class="tools"><input class="search" type="search" '
          'placeholder="Search 54 products" aria-label="Search">'
          '<a class="cart" href="#">Basket<b>0</b></a></div></div></header>')

FOOTER = ('<footer class="site"><div class="shell"><div class="fine">'
          '<span>&copy; 2026 Northwind Supply</span>'
          '<a href="../terms.html">Terms</a><a href="../privacy.html">Privacy</a>'
          '<span class="sep">A fictional shop. Nothing here is for sale.</span>'
          '</div></div></footer>')

LINK = ('<p style="margin-top:22px"><a href="%s" '
        'style="color:var(--brand);font-variation-settings:\'wght\' 600">%s &rarr;</a></p>')


def page(fname, title, level, hint, crumbs, h1, sub, specs, onward=None):
    rows = "".join("<tr><th>%s</th><td>%s</td></tr>" % kv for kv in specs)
    out = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>' + title + '</title>'
        '<meta name="robots" content="noindex,follow">'
        '<link rel="icon" href="../assets/icon.png">\n'
        '<link rel="stylesheet" href="store.css"></head><body>'
        '<div class="sandbox"><div class="shell"><span class="tag">Sandbox</span>'
        '<b>Practice site for Magic Scraper.</b> ' + hint +
        ' <a href="index.html">All sandbox pages</a> &middot; '
        '<a href="../index.html">About the extension</a> &middot; '
        '<a href="../privacy.html">Privacy</a></div></div>'
        + STRIP + HEADER +
        '<div class="shell"><p class="crumbs">' + crumbs + '</p>'
        '<div class="head"><h1>' + h1 + '</h1><p>' + sub + '</p></div>'
        '<div style="padding-bottom:60px;max-width:760px">'
        '<table class="specs" style="width:100%">' + rows + '</table>'
        + (LINK % onward if onward else "") +
        '</div></div>' + FOOTER + '</body></html>'
    )
    with open(os.path.join(DEMO, fname), "w", encoding="utf-8") as fh:
        fh.write(out)
    return fname


def lvl(n, what):
    return ('%s &mdash; level <b>%d</b> of the ten-level chain. '
            'Fields here appear on no level above it.' % (what, n))


# ------------------------------------------------------------------- the data

MAKERS = ["aoyama-works", "brock-forge", "fieldhouse", "hallam-co",
          "mirren-ceramics", "northwind-own", "oakleaf-mill", "tessa-ruiz-studio"]

LOTS = [
    ("lot-nw4471", "NW-4471", "Flax tow, combed", "Northern Ireland", "2026-01-14",
     "1,240 kg", "supplier-ardglass"),
    ("lot-nw4488", "NW-4488", "Merino fleece, grade A", "Otago, New Zealand", "2025-11-03",
     "860 kg", "supplier-tarn-valley"),
    ("lot-nw4502", "NW-4502", "White oak, quarter-sawn", "Jura, France", "2025-09-28",
     "14.2 m3", "supplier-combe-timber"),
    ("lot-nw4519", "NW-4519", "Ball clay, refined", "Devon, England", "2026-02-09",
     "3,100 kg", "supplier-teign-minerals"),
    ("lot-nw4530", "NW-4530", "Copper sheet, 1.2mm", "Falun, Sweden", "2025-12-17",
     "2,050 kg", "supplier-falu-metall"),
    ("lot-nw4547", "NW-4547", "Cork bark, virgin", "Alentejo, Portugal", "2025-08-21",
     "710 kg", "supplier-ardglass"),
    ("lot-nw4558", "NW-4558", "Cast iron, recycled", "Sheffield, England", "2026-03-02",
     "5,400 kg", "supplier-falu-metall"),
    ("lot-nw4566", "NW-4566", "Jute yarn, 4-ply", "Khulna, Bangladesh", "2025-10-11",
     "1,880 kg", "supplier-tarn-valley"),
]

SUPPLIERS = [
    ("supplier-ardglass", "Ardglass Fibre Co.", "1974", "Ardglass, County Down",
     "Flax, hemp and cork", "42", "origin-mourne"),
    ("supplier-tarn-valley", "Tarn Valley Fibres", "1988", "Alexandra, Otago",
     "Wool and jute", "17", "origin-clutha"),
    ("supplier-combe-timber", "Combe Timber", "1951", "Champagnole, Jura",
     "Hardwood, quarter-sawn", "63", "origin-joux"),
    ("supplier-teign-minerals", "Teign Minerals", "1903", "Newton Abbot, Devon",
     "Ball clay and kaolin", "88", "origin-bovey"),
    ("supplier-falu-metall", "Falu Metall AB", "1866", "Falun, Dalarna",
     "Copper and recycled iron", "121", "origin-falun"),
]

ORIGINS = [
    ("origin-mourne", "Mourne Flax Fields", "54.24 N, 5.89 W", "Rain-fed, no irrigation",
     "Retting ponds, on site", "Spring sown, August pulled", "cert-fsc-100"),
    ("origin-clutha", "Clutha Station", "45.25 S, 169.38 E", "High country, 620 m",
     "Shorn once yearly, October", "Non-mulesed flock", "cert-rws-2024"),
    ("origin-joux", "Forêt de la Joux", "46.71 N, 5.96 E", "Managed rotation, 180 years",
     "Winter felling only", "Single-stem selection", "cert-fsc-100"),
    ("origin-bovey", "Bovey Basin Pit 4", "50.58 N, 3.66 W", "Open pit, 31 m",
     "Restored in rotation", "Water table monitored monthly", "cert-iso-14001"),
    ("origin-falun", "Falun Recycling Yard", "60.61 N, 15.63 E", "Post-industrial feed",
     "No primary ore", "Scrap traced to source works", "cert-scrap-9"),
]

CERTS = [
    ("cert-fsc-100", "FSC 100%", "FSC-C014231", "2024-06-01", "2029-05-31",
     "Forest Stewardship Council", "auditor-nordkap"),
    ("cert-rws-2024", "Responsible Wool Standard", "RWS-2024-0881", "2024-02-15",
     "2027-02-14", "Textile Exchange", "auditor-southlands"),
    ("cert-iso-14001", "ISO 14001:2015", "EMS-551204", "2025-01-09", "2028-01-08",
     "ISO", "auditor-nordkap"),
    ("cert-scrap-9", "EN 13920-9 scrap grade", "SCR-9-2211", "2025-04-22", "2028-04-21",
     "CEN", "auditor-vasterby"),
]

AUDITORS = [
    ("auditor-nordkap", "Nordkap Assurance", "Trondheim, Norway", "NA-2291",
     "Forestry, environmental management", "report-2026-114"),
    ("auditor-southlands", "Southlands Verification", "Dunedin, New Zealand", "SV-0442",
     "Animal fibre, welfare", "report-2025-903"),
    ("auditor-vasterby", "Västerby Kontroll", "Gothenburg, Sweden", "VK-7718",
     "Metals, scrap grading", "report-2026-058"),
]

REPORTS = [
    ("report-2026-114", "2026-114", "2026-03-11", "Nordkap Assurance", "Passed",
     "2 minor, both closed", "method-iaf-md1"),
    ("report-2025-903", "2025-903", "2025-11-27", "Southlands Verification", "Passed",
     "None raised", "method-te-am"),
    ("report-2026-058", "2026-058", "2026-02-04", "Västerby Kontroll", "Passed",
     "1 minor, closed 2026-02-19", "method-iaf-md1"),
]

METHODS = [
    ("method-iaf-md1", "IAF MD 1:2023", "International Accreditation Forum",
     "Multi-site sampling", "Square root of sites, minimum 3",
     "Annual surveillance, 3-year cycle"),
    ("method-te-am", "Textile Exchange Assurance Manual 4.0", "Textile Exchange",
     "Chain of custody, physical", "Every site in scope",
     "Annual, unannounced for 10%"),
]


# --------------------------------------------------------------- the builders

def build_lots():
    for slug, ref, material, region, dated, qty, supplier in LOTS:
        name = dict((s[0], s[1]) for s in SUPPLIERS)[supplier]
        page(slug + ".html", "Material lot %s &mdash; Northwind Supply" % ref, 4,
             lvl(4, "A material lot"),
             '<a href="catalogue.html">Home</a> / Traceability / Lot %s' % ref,
             "Material lot %s" % ref, material,
             [("Lot reference", ref), ("Material", material),
              ("Region of origin", region), ("Received", dated),
              ("Quantity", qty), ("Supplier", name),
              ("Storage", "Bay 4, ambient"), ("Blended", "No")],
             onward=(supplier + ".html", "Supplier"))


def build_suppliers():
    for slug, name, founded, based, supplies, staff, origin in SUPPLIERS:
        page(slug + ".html", "%s &mdash; Northwind Supply" % name, 5,
             lvl(5, "A supplier"),
             '<a href="catalogue.html">Home</a> / Traceability / %s' % name,
             name, supplies,
             [("Supplier", name), ("Founded", founded), ("Based in", based),
              ("Supplies", supplies), ("People", staff),
              ("Contract since", "2019"), ("Payment terms", "30 days")],
             onward=(origin + ".html", "Origin site"))


def build_origins():
    for slug, name, coords, land, practice, season, cert in ORIGINS:
        page(slug + ".html", "%s &mdash; Northwind Supply" % name, 6,
             lvl(6, "An origin site"),
             '<a href="catalogue.html">Home</a> / Traceability / %s' % name,
             name, "Origin site",
             [("Site", name), ("Coordinates", coords), ("Land", land),
              ("Practice", practice), ("Season", season),
              ("Visited by us", "Twice yearly")],
             onward=(cert + ".html", "Certificate"))


def build_certs():
    for slug, name, number, issued, expires, scheme, auditor in CERTS:
        page(slug + ".html", "%s &mdash; Northwind Supply" % name, 7,
             lvl(7, "A certificate"),
             '<a href="catalogue.html">Home</a> / Traceability / %s' % name,
             name, "Certificate %s" % number,
             [("Certificate", name), ("Number", number), ("Scheme owner", scheme),
              ("Issued", issued), ("Expires", expires), ("Scope", "Raw material")],
             onward=(auditor + ".html", "Certifying body"))


def build_auditors():
    for slug, name, based, accred, scope, report in AUDITORS:
        page(slug + ".html", "%s &mdash; Northwind Supply" % name, 8,
             lvl(8, "A certifying body"),
             '<a href="catalogue.html">Home</a> / Traceability / %s' % name,
             name, "Certifying body",
             [("Body", name), ("Based in", based), ("Accreditation", accred),
              ("Scope", scope), ("Accredited since", "2011")],
             onward=(report + ".html", "Audit report"))


def build_reports():
    for slug, ref, dated, by, outcome, findings, method in REPORTS:
        page(slug + ".html", "Audit report %s &mdash; Northwind Supply" % ref, 9,
             lvl(9, "An audit report"),
             '<a href="catalogue.html">Home</a> / Traceability / Report %s' % ref,
             "Audit report %s" % ref, outcome,
             [("Report", ref), ("Audit date", dated), ("Carried out by", by),
              ("Outcome", outcome), ("Findings", findings),
              ("Next audit due", "12 months")],
             onward=(method + ".html", "Standard used"))


def build_methods():
    for slug, name, owner, kind, sampling, cycle in METHODS:
        page(slug + ".html", "%s &mdash; Northwind Supply" % name, 10,
             lvl(10, "The standard an audit worked to") +
             " This is the end of the chain &mdash; nothing links onward from here.",
             '<a href="catalogue.html">Home</a> / Traceability / %s' % name,
             name, owner,
             [("Standard", name), ("Owner", owner), ("Audit type", kind),
              ("Sampling rule", sampling), ("Cycle", cycle),
              ("Published", "2023")])


def link_sourcing():
    """Level 3 gains the link that starts levels 4 to 10."""
    rnd = random.Random(20260916)
    lots = [l[0] for l in LOTS]
    for n, slug in enumerate(MAKERS):
        f = os.path.join(DEMO, "sourcing-%s.html" % slug)
        src = open(f, encoding="utf-8").read()
        if 'Material lot &rarr;' in src:
            continue
        lot = lots[n % len(lots)]
        src = src.replace("</table></div>",
                          "</table>" + (LINK % (lot + ".html", "Material lot")) + "</div>", 1)
        # The banner still says the chain stops at three.
        src = src.replace("Sourcing detail &mdash; the <b>third</b> level. "
                          "A chain can go this deep.",
                          "Sourcing detail &mdash; level <b>3</b> of ten. "
                          "Keep going: the material traces back to the standard its auditor used.")
        open(f, "w", encoding="utf-8").write(src)
        print("linked sourcing-%s.html -> %s.html" % (slug, lot))


def main():
    for fn in (build_lots, build_suppliers, build_origins,
               build_certs, build_auditors, build_reports, build_methods):
        fn()
        print("built %s" % fn.__name__.replace("build_", ""))
    link_sourcing()
    made = sum(len(x) for x in (LOTS, SUPPLIERS, ORIGINS, CERTS, AUDITORS, REPORTS, METHODS))
    print("\n%d new pages, levels 4 to 10" % made)


if __name__ == "__main__":
    main()

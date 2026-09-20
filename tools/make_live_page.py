#!/usr/bin/env python3
"""Generate /demo/live: a listing that changes on its own, once a minute.

Comparing a run with the last one is the hardest feature to demonstrate,
because every other sandbox page is static -- the only way to show a diff was
to edit the DOM by hand from a script, which proves nothing to anyone watching.

This page derives its own contents from the clock. The minute number seeds a
small deterministic PRNG, so every visitor sees the same board in the same
minute and a different one the next: a few prices move, one line sells out, one
is discontinued, one arrives. Scrape it, wait for the clock, scrape it again,
and the Changes tab has something real to show.

Deterministic on purpose. A page of random noise would produce a diff, but not
one anybody could check -- and "it said 5 changed, was that right?" is the
question a demo has to be able to answer.

    python3 tools/make_live_page.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DEMO = os.path.join(HERE, "..", "demo")

import make_sandbox_pages as S

POOL = 26          # rows in the pool; ~20 shown at a time


def main():
    items = S.read_items()
    if len(items) < 120:
        raise SystemExit("expected 120 product pages, found %d" % len(items))
    pool = [{
        "sku": it["sku"],
        "name": it["name"],
        "url": it["url"],
        "maker": it["maker"],
        "base": it["price"],
    } for it in items[:POOL]]

    body = (
        '<div class="liveband">'
        '<span class="dot" aria-hidden="true"></span>'
        '<b>The board changes every minute.</b> '
        '<span>Reading for <time id="stamp"></time> &middot; next in '
        '<b id="countdown">--</b>s. Scrape it, wait for the clock to turn, '
        'scrape it again &mdash; the Changes tab compares the two.</span>'
        '</div>'
        '<div class="tablewrap"><table class="data" id="board">'
        '<thead><tr><th>SKU</th><th>Product</th><th>Maker</th><th>Price</th>'
        '<th>Stock</th><th>Updated</th></tr></thead><tbody></tbody></table></div>'
        '<p class="hint" id="movednote"></p>'
    )

    script = (
        '<script>\n'
        '/* The board is a pure function of the minute, so two people looking at\n'
        '   it in the same minute see the same thing and the difference between\n'
        '   one minute and the next is something you can check rather than take\n'
        '   on trust.\n\n'
        '   Most lines hold completely still. The first draft re-rolled every\n'
        '   row every minute, which does produce a diff -- a diff in which all\n'
        '   twenty rows changed, which demonstrates nothing. Three lines are\n'
        '   repriced, one sells out, one comes back, one drops off and the one\n'
        '   that dropped off last minute returns. Everything else is identical,\n'
        '   including the Updated column, which holds the minute that row last\n'
        '   moved rather than the current time -- a clock in every row would\n'
        '   make every row a change. */\n'
        'var POOL = ' + json.dumps(pool) + ';\n'
        'var N = POOL.length;\n'
        'var STOCK = ["In stock", "In stock", "Low stock", "Made to order"];\n'
        'function mod(a, b) { return ((a % b) + b) % b; }\n'
        'function rng(seed) {                 // mulberry32\n'
        '  return function () {\n'
        '    seed |= 0; seed = seed + 0x6D2B79F5 | 0;\n'
        '    var t = Math.imul(seed ^ seed >>> 15, 1 | seed);\n'
        '    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;\n'
        '    return ((t ^ t >>> 14) >>> 0) / 4294967296;\n'
        '  };\n'
        '}\n'
        '// Three lines are repriced each minute, rotating through the pool.\n'
        'function lastReprice(i, m) {\n'
        '  var best = -Infinity;\n'
        '  for (var d = 0; d < 3; d++) best = Math.max(best, m - mod(m - (i - d), N));\n'
        '  return best;\n'
        '}\n'
        '// A repriced line keeps its new price until its next turn, the way a\n'
        '// shop does -- not bouncing back a minute later.\n'
        'function priceAt(i, m) {\n'
        '  var at = lastReprice(i, m);\n'
        '  var r = rng(i * 7919 + at);\n'
        '  return Math.round(Math.max(4, POOL[i].base * (1 + (r() - 0.5) * 0.24)) * 100) / 100;\n'
        '}\n'
        'function rowAt(i, m) {\n'
        '  if (mod(m, N) === i) return null;                       // off the board\n'
        '  return { price: priceAt(i, m),\n'
        '           stock: mod(m * 11 + 3, N) === i ? "Sold out" : STOCK[i % STOCK.length] };\n'
        '}\n'
        'function lastMoved(i, m) {\n'
        '  var cur = rowAt(i, m);\n'
        '  for (var k = 1; k <= N; k++) {\n'
        '    var prev = rowAt(i, m - k);\n'
        '    if (!prev || prev.price !== cur.price || prev.stock !== cur.stock) return m - k + 1;\n'
        '  }\n'
        '  return m - N;\n'
        '}\n'
        'function boardFor(m) {\n'
        '  var rows = [];\n'
        '  for (var i = 0; i < N; i++) {\n'
        '    var r = rowAt(i, m);\n'
        '    if (!r) continue;\n'
        '    rows.push({ sku: POOL[i].sku, name: POOL[i].name, url: POOL[i].url,\n'
        '                maker: POOL[i].maker, price: r.price, stock: r.stock,\n'
        '                moved: lastMoved(i, m) });\n'
        '  }\n'
        '  return rows;\n'
        '}\n'
        'function hhmm(minute) {\n'
        '  var d = new Date(minute * 60000);\n'
        '  return String(d.getHours()).padStart(2, "0") + ":" +\n'
        '         String(d.getMinutes()).padStart(2, "0");\n'
        '}\n'
        'var shownMinute = null;\n'
        'function draw() {\n'
        '  var now = new Date();\n'
        '  var minute = Math.floor(now.getTime() / 60000);\n'
        '  document.getElementById("countdown").textContent = 60 - now.getSeconds();\n'
        '  if (minute === shownMinute) return;\n'
        '  shownMinute = minute;\n'
        '  var rows = boardFor(minute), prev = boardFor(minute - 1);\n'
        '  document.getElementById("stamp").textContent = hhmm(minute);\n'
        '  document.getElementById("stamp").setAttribute("datetime", now.toISOString());\n'
        '  var out = "";\n'
        '  for (var i = 0; i < rows.length; i++) {\n'
        '    var x = rows[i];\n'
        '    out += \'<tr><td class="sku">\' + x.sku + \'</td>\' +\n'
        '      \'<td><a href="\' + x.url + \'">\' + x.name + "</a></td>" +\n'
        '      "<td>" + x.maker + "</td>" +\n'
        '      \'<td class="price">$\' + x.price.toFixed(2) + "</td>" +\n'
        '      "<td>" + x.stock + "</td>" +\n'
        '      "<td>" + hhmm(x.moved) + "</td></tr>";\n'
        '  }\n'
        '  document.querySelector("#board tbody").innerHTML = out;\n'
        '  // Printed here so the extension\'s answer can be checked against the\n'
        '  // page rather than believed.\n'
        '  var was = {}; prev.forEach(function (p) { was[p.sku] = p; });\n'
        '  var now2 = {}; rows.forEach(function (p) { now2[p.sku] = p; });\n'
        '  var changed = 0, added = 0, gone = 0;\n'
        '  rows.forEach(function (p) {\n'
        '    var b = was[p.sku];\n'
        '    if (!b) { added++; return; }\n'
        '    if (b.price !== p.price || b.stock !== p.stock) changed++;\n'
        '  });\n'
        '  prev.forEach(function (p) { if (!now2[p.sku]) gone++; });\n'
        '  document.getElementById("movednote").textContent =\n'
        '    rows.length + " lines. Since the minute before: " + changed + " changed, " +\n'
        '    gone + " gone, " + added + " new \u2014 the rest are untouched.";\n'
        '}\n'
        'draw(); setInterval(draw, 1000);\n'
        '</script>'
    )

    S.page(
        "live.html",
        "A board that changes every minute",
        "Sandbox live page: prices, stock and the line-up change once a minute, "
        "deterministically from the clock. For testing run-to-run comparison.",
        "This one <b>changes every minute</b>. Scrape it, wait for the clock to turn, "
        "scrape it again, and compare the two runs.",
        '<a href="catalogue.html">Home</a> / Live board',
        "Live trade board",
        "Prices and availability as of this minute. It moves on its own.",
        body,
        scripts=script,
    )
    print("\n%d lines in the pool; roughly 20-24 on the board in any minute" % POOL)


if __name__ == "__main__":
    main()

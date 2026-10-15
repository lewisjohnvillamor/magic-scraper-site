/* Film the YouTube walkthrough: the practice shop with the real extension
   docked beside it as a side panel, the way 1.22 is meant to be used.

   One page is recorded at 1920x1080. The extension's own popup.html#panel is
   mounted in that page as a right-hand panel (the recording copy of the
   extension lists it as web-accessible), so the page reflows beside it like
   Chrome's side panel, the extension's blue row highlights are drawn on the
   page, and the manual picker is clicked on the page itself. Everything on
   screen is the extension working; nothing is mocked except the shop changing
   its prices before the Changes tab, which is the page edited in place.

   A coded beat marker is painted in the top-left corner at every step, because
   the webm's clock drifts seconds against Date.now(); the editor reads the
   markers back off the frames.

   Serve the site first:  python3 -m http.server 80 --bind 127.0.0.1 --directory <site>
   Output (scratchpad): walk2.webm, walk2-beats.json, walk2-file.json */
import { chromium } from 'playwright';
import { mkdtempSync, cpSync, rmSync, readFileSync, writeFileSync, renameSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

const S = process.env.OUT || '/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad';
const EXT = join(S, 'ext-walk2'), VID = join(S, 'vid-walk2');
const SHOP = 'http://shop.example.com/demo/';
rmSync(EXT, { recursive: true, force: true }); rmSync(VID, { recursive: true, force: true });
cpSync(process.env.EXT_SRC || '/home/user/Magic-Data-Scraper-', EXT,
  { recursive: true, filter: (p) => !/node_modules|\.git($|\/)/.test(p) });
const mf = JSON.parse(readFileSync(join(EXT, 'manifest.json'), 'utf8'));
mf.permissions = ['activeTab', 'scripting', 'downloads', 'tabs', 'storage', 'sidePanel'];
mf.host_permissions = ['<all_urls>'];
delete mf.optional_permissions; delete mf.optional_host_permissions;
// Recording copy only: lets the shop page frame the panel.
mf.web_accessible_resources = [{ resources: ['*'], matches: ['<all_urls>'] }];
writeFileSync(join(EXT, 'manifest.json'), JSON.stringify(mf, null, 2));

const ctx = await chromium.launchPersistentContext(mkdtempSync(join(tmpdir(), 'mdsw2-')), {
  headless: true,
  executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  viewport: { width: 1920, height: 1080 },
  recordVideo: { dir: VID, size: { width: 1920, height: 1080 } },
  args: [`--disable-extensions-except=${EXT}`, `--load-extension=${EXT}`, '--no-sandbox',
         '--disable-dev-shm-usage', '--host-resolver-rules=MAP shop.example.com 127.0.0.1',
         '--proxy-bypass-list=*'],
});
let sw = null;
for (let i = 0; i < 40 && !sw; i++) {
  for (const w of ctx.serviceWorkers()) {
    if (await w.evaluate(() => !!(self.chrome && chrome.storage && chrome.tabs)).catch(() => false)) sw = w;
  }
  if (!sw) await new Promise((r) => setTimeout(r, 500));
}
if (!sw) throw new Error('extension worker never started');
const extId = new URL(sw.url()).host;
await sw.evaluate(() => chrome.storage.local.set({ mds_license: { pro: true, at: Date.now() } }));
for (const p of ctx.pages()) await p.close().catch(() => {});

const page = await ctx.newPage();
const PANEL_W = 460, K = 1.25;                       // panel CSS width, and its on-screen scale
const PANEL_PX = Math.round(PANEL_W * K);            // 575px of the 1920 frame

// ---- the stage: beat marker, a visible pointer, and the docked panel ----
let beatIndex = 0;
async function stage({ panel = true, slide = false } = {}) {
  await page.evaluate(({ id, W, K, PX, panel, slide, bi }) => {
    const d = document;
    if (!d.getElementById('__w_style')) {
      const st = d.createElement('style'); st.id = '__w_style';
      st.textContent = `
        html.__w_docked { padding-right:${PX}px !important; box-sizing:border-box; }
        #__w_panel { position:fixed; top:0; right:0; width:${W}px; height:${Math.round(1080 / K)}px;
          transform:scale(${K}); transform-origin:top right; border:0; z-index:2147483600;
          background:#fff; box-shadow:-1px 0 0 #d9d6e3, -18px 0 40px -24px rgba(20,18,31,.35);
          transition:transform .55s cubic-bezier(.2,.8,.2,1); }
        #__w_panel.__w_off { transform:translateX(${PX + 40}px) scale(${K}); }
        #__w_cursor { position:fixed; z-index:2147483647; left:0; top:0; width:26px; height:26px;
          pointer-events:none; transition:transform .5s cubic-bezier(.3,.7,.2,1); }
        #__w_cursor svg { filter:drop-shadow(0 2px 3px rgba(0,0,0,.35)); }
        #__w_cursor .__w_ring { position:absolute; left:-14px; top:-14px; width:28px; height:28px;
          border-radius:50%; border:3px solid #7c6cf0; opacity:0; transform:scale(.4); }
        #__w_cursor.__w_tap .__w_ring { animation:__w_tap .45s ease-out; }
        @keyframes __w_tap { 0%{opacity:.9;transform:scale(.4)} 100%{opacity:0;transform:scale(1.6)} }
        #__w_beat { position:fixed; left:0; top:0; width:16px; height:16px; z-index:2147483647; pointer-events:none; }`;
      d.documentElement.appendChild(st);
    }
    if (!d.getElementById('__w_beat')) {
      const mk = d.createElement('div'); mk.id = '__w_beat'; d.documentElement.appendChild(mk);
    }
    const g = 30 + bi * 10;
    d.getElementById('__w_beat').style.background = `rgb(${g},${g},${g})`;
    if (!d.getElementById('__w_cursor')) {
      const c = d.createElement('div'); c.id = '__w_cursor';
      c.innerHTML = '<span class="__w_ring"></span><svg width="26" height="26" viewBox="0 0 24 24">' +
        '<path d="M4 2 L4 19 L8.5 14.8 L11.6 21.5 L14.4 20.2 L11.3 13.6 L17.5 13.4 Z" fill="#fff" stroke="#14121f" stroke-width="1.4" stroke-linejoin="round"/></svg>';
      c.style.transform = window.__wCur || 'translate(760px,620px)';
      d.documentElement.appendChild(c);
    }
    if (panel && !d.getElementById('__w_panel')) {
      d.documentElement.classList.add('__w_docked');
      const f = d.createElement('iframe'); f.id = '__w_panel';
      f.src = `chrome-extension://${id}/popup.html#panel`;
      if (slide) f.classList.add('__w_off');
      d.documentElement.appendChild(f);
      if (slide) requestAnimationFrame(() => requestAnimationFrame(() => f.classList.remove('__w_off')));
    }
  }, { id: extId, W: PANEL_W, K, PX: PANEL_PX, panel, slide, bi: beatIndex });
}
const panelFrame = async () => {
  for (let i = 0; i < 60; i++) {
    const f = page.frames().find((fr) => fr.url().includes('popup.html'));
    if (f) { await f.waitForLoadState('load').catch(() => {}); return f; }
    await page.waitForTimeout(100);
  }
  throw new Error('panel frame never loaded');
};
let P = null;                                         // the panel's frame

// Move the pointer to a spot in the page (x, y in page px), optionally tap.
async function moveTo(x, y, { tap = false, wait = 600 } = {}) {
  await page.evaluate(([x, y]) => {
    const c = document.getElementById('__w_cursor'); if (!c) return;
    window.__wCur = `translate(${x}px,${y}px)`; c.style.transform = window.__wCur;
  }, [x, y]);
  await page.waitForTimeout(wait);
  if (tap) {
    await page.evaluate(() => {
      const c = document.getElementById('__w_cursor'); c.classList.remove('__w_tap');
      void c.offsetWidth; c.classList.add('__w_tap');
    });
    await page.waitForTimeout(160);
  }
}
// Point at something in the panel (scaled, docked right) or on the page.
async function pointPanel(sel, opts) {
  const r = await P.evaluate((s) => { const e = document.querySelector(s); if (!e) return null;
    const b = e.getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + b.height / 2 }; }, sel);
  if (!r) throw new Error('nothing in the panel matches ' + sel);
  await moveTo(1920 - PANEL_PX + r.x * K, r.y * K, opts);
}
async function pointPage(sel, opts) {
  const r = await page.evaluate((s) => { const e = document.querySelector(s); if (!e) return null;
    e.scrollIntoView({ block: 'nearest' });
    const b = e.getBoundingClientRect(); return { x: b.left + Math.min(b.width / 2, 60), y: b.top + b.height / 2 }; }, sel);
  if (!r) throw new Error('nothing on the page matches ' + sel);
  await moveTo(r.x, r.y, opts);
}
// Playwright places clicks wrongly inside a transformed iframe, so the panel
// is driven with the element's own click() after the pointer has moved there.
const click = async (sel, opts = {}) => {
  await pointPanel(sel, { tap: true, ...opts });
  await P.evaluate((s) => document.querySelector(s).click(), sel);
};

const mark = {}, order = [];
const t0 = Date.now();
async function beat(n) {
  beatIndex++; order.push(n);
  await page.evaluate((g) => { const m = document.getElementById('__w_beat'); if (m) m.style.background = `rgb(${g},${g},${g})`; },
    30 + beatIndex * 10).catch(() => {});
  mark[n] = Date.now() - t0;
  console.log(n.padEnd(14), '@', (mark[n] / 1000).toFixed(2) + 's');
}
async function go(path, { slide = false } = {}) {
  await page.goto(SHOP + path, { waitUntil: 'load' });
  await page.waitForTimeout(300);
  await stage({ panel: true, slide });
  P = await panelFrame();
  await P.waitForFunction(() => +document.getElementById('statRows').textContent > 0, null, { timeout: 15000 });
}
const rows = () => P.evaluate(() => +document.getElementById('statRows').textContent);
const status = () => P.evaluate(() => document.getElementById('status').textContent.replace(/\s+/g, ' ').trim());

/* ---------------- the walkthrough ---------------- */

// 0. the shop, no extension yet
await page.goto(SHOP + 'catalogue.html', { waitUntil: 'load' });
await stage({ panel: false });
await beat('shop');
await page.waitForTimeout(1200);
await moveTo(1500, 230, { wait: 1400 });
await moveTo(1860, 24, { tap: true, wait: 1100 });      // where the toolbar icon is drawn
await beat('openPanel');
await stage({ panel: true, slide: true });
P = await panelFrame();
await P.waitForFunction(() => +document.getElementById('statRows').textContent > 0, null, { timeout: 15000 });
await page.waitForTimeout(900);
await beat('detected');
console.log('  catalogue:', await rows(), 'rows ·', await status());
await moveTo(700, 520, { wait: 800 });
await page.waitForTimeout(6500);

// 1. tidy
await beat('tidy');
const cols = await P.evaluate(() => [...document.querySelectorAll('#previewWrap th[data-idx]')].map((t) => t.textContent.trim()));
// The first column is a "Sale" flag that is blank on half the rows: the one a
// person would drop, and it is on screen.
let drop = cols.findIndex((c) => /flag/i.test(c));
if (drop < 0) drop = 0;
await click(`#previewWrap th[data-idx="${drop}"]`);
await page.waitForTimeout(1600);
const nm = cols.findIndex((c) => /link text|name|title/i.test(c));
await pointPanel(`#previewWrap th[data-idx="${nm}"]`, { tap: true });
await P.evaluate((s) => document.querySelector(s).dispatchEvent(new MouseEvent('dblclick', { bubbles: true })),
  `#previewWrap th[data-idx="${nm}"]`);
await page.waitForTimeout(500);
await page.keyboard.press('ControlOrMeta+A');
await page.keyboard.type('Product', { delay: 120 });
await page.keyboard.press('Enter');
await page.waitForTimeout(1500);
await pointPanel('#filter', { tap: true });
await P.type('#filter', 'oak', { delay: 170 });
await page.waitForTimeout(2600);
await P.fill('#filter', ''); await P.dispatchEvent('#filter', 'input');
await page.waitForTimeout(1400);

// 2. two tables on one page. The tidy choices above are saved for the whole
// site; forget them so this page opens as a first visit would.
await sw.evaluate((k) => chrome.storage.local.remove(k), 'mds_settings');
await go('rates.html');
await beat('rates');
console.log('  rates first pick:', await rows(), 'rows ·', await status());
await page.waitForTimeout(5200);
await click('#tryAnother');
await page.waitForTimeout(1600);
await beat('another');
console.log('  rates after Another table:', await rows(), 'rows');
await page.waitForTimeout(4200);

// 3. pick it by hand
await go('awkward.html');
await beat('awkward');
await page.waitForTimeout(2600);
await click('#pickArea');
await page.waitForTimeout(1200);
await beat('picking');
await pointPage('table.data tbody tr:nth-child(3) td:nth-child(2)', { tap: true, wait: 900 });
await page.click('table.data tbody tr:nth-child(3) td:nth-child(2)');
await page.waitForTimeout(1800);
await pointPage('#discount', { tap: true, wait: 900 });
await page.click('#discount', { modifiers: ['Shift'] });
await page.waitForTimeout(1800);
await pointPage('#__mds_pk_done', { tap: true, wait: 900 });
await page.click('#__mds_pk_done');
await page.waitForTimeout(2200);
await beat('picked');
await page.waitForTimeout(1200);
// The picked column is added at the right-hand end; bring it into view.
await P.evaluate(() => {
  const w = document.getElementById('previewWrap'); const to = w.scrollWidth - w.clientWidth;
  let x = w.scrollLeft; const id = setInterval(() => { x = Math.min(to, x + 16); w.scrollLeft = x; if (x >= to) clearInterval(id); }, 24);
});
const pickedCols = await P.evaluate(() => [...document.querySelectorAll('#previewWrap th[data-idx]')].map((t) => t.textContent.trim()));
console.log('  picked:', await rows(), 'rows ·', pickedCols.join(' | '));
await page.waitForTimeout(3600);

// 4. every page
await go('catalogue.html');
await page.waitForTimeout(800);
await click('.tab[data-tab="crawl"]');
await page.waitForTimeout(1400);
await beat('crawlTab');
if (await P.isVisible('#autoNext')) { await click('#autoNext'); await page.waitForTimeout(1500); }
await P.evaluate(() => { minDelay.value = '1.0'; maxDelay.value = '1.3'; });
await page.waitForTimeout(2400);
await click('#startCrawl');
await beat('crawlStart');
await P.waitForFunction(() => /Done\./.test(document.getElementById('status').textContent), null, { timeout: 90000 });
await page.waitForTimeout(2600);
await beat('crawlDone');
console.log('  crawled:', await rows(), 'rows ·', await status());

// 5. drill-down
await click('.tab[data-tab="data"]');
await page.waitForTimeout(1000);
if (!(await P.isVisible('#drillHint'))) throw new Error('drill-down hint did not appear');
await beat('hint');
await pointPanel('#drillHint', { wait: 900 });
await page.waitForTimeout(3800);
await click('#drillHintGo');
await page.waitForTimeout(1600);
await click('#drillEnable');
await P.waitForFunction(() => !document.getElementById('drillControls').hidden, null, { timeout: 8000 });
await page.waitForTimeout(2200);
await beat('drillStart');
const items = await P.evaluate(async () => {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const r = await new Promise((res) => chrome.tabs.sendMessage(tabs[0].id, { type: 'MDS_FULL_DATA' }, res));
  const col = Object.keys(r.rows[0]).find((k) => /^link$/i.test(k));
  return r.rows.map((row, i) => ({ index: i, url: row[col] })).filter((x) => x.url);
});
await P.evaluate((its) => chrome.runtime.sendMessage({ type: 'MDS_DRILL_START', items: its,
  opts: { minDelay: 0.05, maxDelay: 0.1, area: -1, openOnError: false, maxRows: 0 } }), items);
for (let i = 0; i < 400; i++) {
  const st = await sw.evaluate(async () => (await chrome.storage.local.get('mds_drill_status')).mds_drill_status || null);
  if (st && st.running === false) break;
  await page.waitForTimeout(400);
}
await page.waitForTimeout(1600);
await beat('drillDone');

// 6. the columns that came back, and the file
await click('.tab[data-tab="data"]');
await page.waitForTimeout(1200);
await beat('details');
await P.evaluate(() => {
  const w = document.getElementById('previewWrap');
  const th = [...w.querySelectorAll('th[data-idx]')].find((t) => /detail:SKU/.test(t.textContent));
  const to = th ? th.offsetLeft - 8 : 700;
  let x = 0; const id = setInterval(() => { x += 18; w.scrollLeft = x; if (x >= to) clearInterval(id); }, 24);
});
await page.waitForTimeout(5200);
await click('#exportXlsx');
await page.waitForTimeout(1800);
await beat('exported');
// What the file holds, for the editor's spreadsheet view: the same rows the
// export just wrote, read back from the page, with the popup's own column
// choices (renames, exclusions) applied.
const fileView = await P.evaluate(async () => {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const r = await new Promise((res) => chrome.tabs.sendMessage(tabs[0].id, { type: 'MDS_FULL_DATA' }, res));
  const heads = [...document.querySelectorAll('#previewWrap th[data-idx]')]
    .filter((t) => !t.classList.contains('excluded')).map((t) => t.textContent.replace(/^✓/, '').trim());
  return { columns: heads, total: r.rows.length };
});
const preview = await P.evaluate(() => {
  const ths = [...document.querySelectorAll('#previewWrap thead th[data-idx]')];
  const keep = ths.map((t, i) => [t, i]).filter(([t]) => !t.classList.contains('excluded'));
  const heads = keep.map(([t]) => t.textContent.replace(/^✓/, '').trim());
  const body = [...document.querySelectorAll('#previewWrap tbody tr')].slice(0, 18).map((tr) => {
    const tds = [...tr.querySelectorAll('td')].slice(1);
    return keep.map(([, i]) => (tds[i] ? tds[i].textContent.trim() : ''));
  });
  return { heads, body };
});
writeFileSync(join(S, 'walk2-file.json'), JSON.stringify({ ...fileView, ...preview }, null, 1));
await page.waitForTimeout(1600);

// 7. what changed since last time
await P.evaluate(async () => {
  const [t] = await chrome.tabs.query({ active: true, currentWindow: true });
  await new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_RESET' }, r));
  await new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_DETECT' }, r));
  return new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_SNAPSHOT_SAVE' }, r));
});
await beat('changesSetup');
const moved = await page.evaluate(() => {
  const cards = [...document.querySelectorAll('article.product')];
  const out = { repriced: 0, soldOut: 0, removed: 0, added: 0 };
  cards.slice(1, 4).forEach((c) => { const p = c.querySelector('.price'); if (!p) return;
    p.textContent = p.textContent.replace(/([\d.]+)/, (m0) => (Number(m0) + 15).toFixed(2)); out.repriced++; });
  cards.slice(4, 6).forEach((c) => { const st = c.querySelector('.stock'); if (st) { st.textContent = 'Sold out'; out.soldOut++; } });
  if (cards[7]) { cards[7].remove(); out.removed++; }
  if (cards[0]) { const clone = cards[0].cloneNode(true);
    const sku = clone.querySelector('.sku'); const name = clone.querySelector('h3 a') || clone.querySelector('h3');
    if (sku) sku.textContent = 'NW-1042'; if (name) name.textContent = 'Ash Serving Board, Small';
    cards[0].parentNode.insertBefore(clone, cards[0]); out.added++; }
  return out;
});
console.log('  the shop moved on:', JSON.stringify(moved));
await P.evaluate(async () => {
  const [t] = await chrome.tabs.query({ active: true, currentWindow: true });
  return new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_DETECT' }, r));
});
// The panel re-reads the page when it is reopened, as it would be next time.
await page.evaluate(() => { const f = document.getElementById('__w_panel'); f.src = f.src; });
P = await panelFrame();
await P.waitForFunction(() => +document.getElementById('statRows').textContent > 0, null, { timeout: 15000 });
await page.waitForTimeout(1500);
await click('.tab[data-tab="diff"]');
await page.waitForTimeout(1200);
await beat('changes');
const diff = await P.evaluate(() => ({ ready: !document.getElementById('diffReady').hidden,
  summary: document.getElementById('diffText').textContent.replace(/\s+/g, ' ').trim(),
  rows: document.querySelectorAll('#diffWrap tbody tr').length }));
console.log('  changes:', JSON.stringify(diff).slice(0, 170));
if (!diff.ready || !diff.rows) throw new Error('no comparison to film');
await page.waitForTimeout(11000);
await beat('end');
await page.waitForTimeout(800);

const path = await page.video().path();
await ctx.close();
renameSync(path, join(S, 'walk2.webm'));
writeFileSync(join(S, 'walk2-beats.json'), JSON.stringify({ wall: mark, order }, null, 2));
console.log('\nwalk2.webm written');

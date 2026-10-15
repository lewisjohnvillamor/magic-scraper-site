/* Record the YouTube walkthrough: the real extension, at 1080p, on the practice
   shop, one capability after another at a pace someone can follow.

   Same stage as record-promo.mjs -- the popup scaled up over a dimmed shot of
   the page -- but slower, and covering the everyday features the promo skips:
   tidying columns, the drill-down hint on the Data tab, and the export. Every
   row and number on screen is the extension's own; nothing is mocked except
   the shop "moving on" before the Changes tab, which is the page being edited
   in place exactly as a real shop would change.

   Needs the site served on port 80 (shop.example.com is mapped to 127.0.0.1):
     sudo python3 -m http.server 80 --directory /home/user/magic-scraper-site
   Writes raw-walk.webm and beats-walk.json to the scratchpad, which
   tools/edit-walkthrough.py turns into the finished video. */
import { chromium } from 'playwright';
import { mkdtempSync, cpSync, rmSync, readFileSync, writeFileSync, renameSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

const S = '/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad';
const EXT = join(S, 'extwalk'), VID = join(S, 'vidwalk');
rmSync(EXT, { recursive: true, force: true }); rmSync(VID, { recursive: true, force: true });
cpSync('/home/user/Magic-Data-Scraper-', EXT, { recursive: true,
  filter: (p) => !/node_modules|\.git($|\/)/.test(p) });
const m = JSON.parse(readFileSync(join(EXT, 'manifest.json'), 'utf8'));
m.permissions = ['activeTab', 'scripting', 'downloads', 'tabs', 'storage'];
m.host_permissions = ['<all_urls>'];
delete m.optional_permissions; delete m.optional_host_permissions;
writeFileSync(join(EXT, 'manifest.json'), JSON.stringify(m, null, 2));

const ctx = await chromium.launchPersistentContext(mkdtempSync(join(tmpdir(), 'mdswk-')), {
  headless: true,
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  viewport: { width: 1920, height: 1080 },
  recordVideo: { dir: VID, size: { width: 1920, height: 1080 } },
  args: [`--disable-extensions-except=${EXT}`, `--load-extension=${EXT}`, '--no-sandbox',
         '--disable-dev-shm-usage', '--host-resolver-rules=MAP shop.example.com 127.0.0.1',
         '--proxy-bypass-list=*'],
});
// The first worker reported can be one that has not finished starting, with
// chrome.storage not yet on it; wait for the one that is ready.
let sw = null;
for (let i = 0; i < 40 && !sw; i++) {
  for (const w of ctx.serviceWorkers()) {
    if (await w.evaluate(() => !!(self.chrome && chrome.storage && chrome.tabs)).catch(() => false)) sw = w;
  }
  if (!sw) await new Promise((r) => setTimeout(r, 500));
}
if (!sw) throw new Error('the extension\'s worker never started');
const extId = new URL(sw.url()).host;
// Pro, so the drill runs every row on camera. The caption says which parts are Pro.
await sw.evaluate(() => chrome.storage.local.set({ mds_license: { pro: true, at: Date.now() } }));

const site = await ctx.newPage();
await site.goto('http://shop.example.com/demo/catalogue.html', { waitUntil: 'load' });
await site.waitForTimeout(700);
const shot = (await site.screenshot()).toString('base64');
const tab = await sw.evaluate(async () => (await chrome.tabs.query({}))
  .filter((t) => t.url && t.url.includes('/demo/')).map((t) => t.id)[0]);

const pop = await ctx.newPage();
await sw.evaluate((id) => chrome.tabs.update(id, { active: true }), tab);
await pop.goto(`chrome-extension://${extId}/popup.html`, { waitUntil: 'load' });
// Re-applied after every reload: addStyleTag does not survive one.
const STAGE = `
  html { background:#0e0d14; }
  html::before { content:""; position:fixed; inset:0; z-index:-2;
    background-image:url("data:image/png;base64,${shot}");
    background-size:1920px auto; background-position:center top; background-repeat:no-repeat; }
  html::after { content:""; position:fixed; inset:0; z-index:-1;
    background:linear-gradient(90deg,rgba(14,13,20,.90) 0%,rgba(14,13,20,.82) 38%,
               rgba(14,13,20,.46) 62%,rgba(14,13,20,.30) 100%); }
  body { position:absolute; right:110px; top:50%;
         transform:translateY(-50%) scale(1.42); transform-origin:right center;
         border-radius:14px; overflow:hidden;
         box-shadow:0 50px 110px -24px rgba(0,0,0,.9), 0 0 0 1px rgba(255,255,255,.12); }
  /* a visible pointer, so a viewer can follow what is being clicked */
  #mds-cursor { position:fixed; z-index:99999; width:22px; height:22px; margin:-11px 0 0 -11px;
    border-radius:50%; background:rgba(167,139,250,.35); border:2px solid #a78bfa;
    pointer-events:none; transition:left .45s ease, top .45s ease, transform .15s; }
  #mds-cursor.down { transform:scale(.7); background:rgba(167,139,250,.7); }
`;
/* Beat markers. The webm's clock drifts against Date.now() -- by seconds
   across the two reloads before the Changes tab -- so a beat's wall time is
   not its time in the video. Each beat therefore also paints a 16px square in
   the top-left corner whose grey level encodes the beat's index; the editor
   reads the square back frame by frame and covers it. */
let beatIndex = 0;
const paintMarker = () => pop.evaluate((i) => {
  let mk = document.getElementById('mds-beat');
  if (!mk) {
    mk = document.createElement('div'); mk.id = 'mds-beat';
    mk.style.cssText = 'position:fixed;left:0;top:0;width:16px;height:16px;z-index:100000;pointer-events:none';
    document.documentElement.appendChild(mk);
  }
  const g = 30 + i * 10;
  mk.style.background = `rgb(${g},${g},${g})`;
}, beatIndex).catch(() => {});
const dress = async () => {
  await pop.addStyleTag({ content: STAGE });
  await pop.evaluate(() => {
    if (document.getElementById('mds-cursor')) return;
    const c = document.createElement('div'); c.id = 'mds-cursor';
    c.style.left = '50%'; c.style.top = '50%'; document.body.appendChild(c);
  });
  await paintMarker();
};
await dress();

// Move the visible pointer onto an element, press it, then do the real action.
// The pointer lives inside the scaled body, so it is positioned in the body's
// own (untransformed) coordinates.
async function point(sel, { press = true, pause = 650 } = {}) {
  await pop.evaluate((s) => {
    const el = document.querySelector(s), c = document.getElementById('mds-cursor');
    if (!el || !c) return;
    const b = document.body.getBoundingClientRect(), r = el.getBoundingClientRect();
    const k = b.width / document.body.offsetWidth || 1;
    c.style.left = ((r.left + r.width / 2 - b.left) / k) + 'px';
    c.style.top = ((r.top + r.height / 2 - b.top) / k) + 'px';
    c.style.position = 'absolute';
  }, sel);
  await pop.waitForTimeout(pause);
  if (press) {
    await pop.evaluate(() => document.getElementById('mds-cursor').classList.add('down'));
    await pop.waitForTimeout(140);
    await pop.evaluate(() => document.getElementById('mds-cursor').classList.remove('down'));
  }
}

const mark = {};
const t0 = Date.now();
const order = [];
const beat = async (n) => {
  beatIndex++; order.push(n);
  await paintMarker();
  mark[n] = Date.now() - t0;
  console.log(n.padEnd(14), '@', (mark[n] / 1000).toFixed(2) + 's', ' marker', 30 + beatIndex * 10);
};

/* 1 -- it finds the table */
await pop.waitForFunction(() => +document.getElementById('statRows').textContent > 0, null, { timeout: 15000 });
await beat('detected');
console.log('  rows:', await pop.evaluate(() => document.getElementById('statRows').textContent),
  ' status:', await pop.evaluate(() => document.getElementById('status').textContent.trim()));
// Long enough for the narration over this scene (about 7s).
await pop.waitForTimeout(8600);

/* 2 -- tidy it: drop a column, rename one, filter */
await beat('tidy');
const cols = await pop.evaluate(() => [...document.querySelectorAll('#previewWrap th[data-idx]')].map((t) => t.textContent.trim()));
console.log('  columns:', cols.join(' | '));
// The second rating column repeats the first: the natural one to drop on camera.
let dropIdx = cols.findIndex((c) => /rating 2/i.test(c));
if (dropIdx < 0) dropIdx = cols.findIndex((c) => /image|img|flag/i.test(c));
if (dropIdx >= 0) {
  await point(`#previewWrap th[data-idx="${dropIdx}"]`);
  await pop.click(`#previewWrap th[data-idx="${dropIdx}"]`);
  await pop.waitForTimeout(1400);
}
const nameIdx = cols.findIndex((c) => /name|title|link text/i.test(c));
if (nameIdx >= 0) {
  await point(`#previewWrap th[data-idx="${nameIdx}"]`);
  await pop.dblclick(`#previewWrap th[data-idx="${nameIdx}"]`);
  await pop.waitForTimeout(500);
  await pop.keyboard.press('ControlOrMeta+A');
  await pop.keyboard.type('Product', { delay: 110 });
  await pop.waitForTimeout(400);
  await pop.keyboard.press('Enter');
  await pop.waitForTimeout(1300);
}
await point('#filter');
await pop.click('#filter');
await pop.keyboard.type('oak', { delay: 160 });
await pop.waitForTimeout(2400);
await pop.fill('#filter', '');
await pop.dispatchEvent('#filter', 'input');
await pop.waitForTimeout(1200);

/* 3 -- every page */
await point('.tab[data-tab="crawl"]');
await pop.click('.tab[data-tab="crawl"]');
await pop.waitForTimeout(1200);
await beat('crawlTab');
// The Next button is usually found the moment the popup opens, and step 1 is
// then collapsed to its summary. Only press Auto-detect when it is showing.
if (await pop.isVisible('#autoNext')) {
  await point('#autoNext');
  await pop.click('#autoNext');
}
await pop.waitForTimeout(2200);
await pop.evaluate(() => { minDelay.value = '0.9'; maxDelay.value = '1.1'; });
await point('#startCrawl');
await beat('crawlStart');
await pop.click('#startCrawl');
await pop.waitForFunction(() => /Done\./.test(document.getElementById('status').textContent),
  null, { timeout: 90000 }).catch(() => {});
await pop.waitForTimeout(2800); await beat('crawlDone');
console.log('  crawled:', await pop.evaluate(() =>
  document.getElementById('statRows').textContent + ' rows / ' + document.getElementById('statPages').textContent + ' pages'));

/* 4 -- the drill-down hint on the Data tab, then the drill */
await point('.tab[data-tab="data"]');
await pop.click('.tab[data-tab="data"]');
await pop.waitForTimeout(900);
const hint = await pop.evaluate(() => !document.getElementById('drillHint').hidden &&
  document.getElementById('drillHintText').textContent.trim());
console.log('  hint:', hint);
if (!hint) throw new Error('the drill-down hint did not show after the crawl');
await beat('hint');
await pop.waitForTimeout(3200);
await point('#drillHintGo');
await pop.click('#drillHintGo');
await pop.waitForTimeout(2000); await beat('showMe');
await point('#drillEnable');
await pop.check('#drillEnable');
await pop.waitForTimeout(1800); await beat('drillReady');

const items = await pop.evaluate(async () => {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const r = await new Promise((res) => chrome.tabs.sendMessage(tabs[0].id, { type: 'MDS_FULL_DATA' }, res));
  const col = Object.keys(r.rows[0]).find((k) => /^link$/i.test(k));
  return r.rows.map((row, i) => ({ index: i, url: row[col] })).filter((x) => x.url);
});
await beat('drillStart');
await pop.evaluate((its) => chrome.runtime.sendMessage({
  type: 'MDS_DRILL_START', items: its,
  opts: { minDelay: 0.05, maxDelay: 0.1, area: -1, openOnError: false, maxRows: 0 }
}), items);
for (let i = 0; i < 400; i++) {
  const st = await sw.evaluate(async () => (await chrome.storage.local.get('mds_drill_status')).mds_drill_status || null);
  if (st && st.running === false) break;
  await pop.waitForTimeout(400);
}
await pop.waitForTimeout(1800); await beat('drillDone');

/* 5 -- the detail columns, and the file */
await pop.click('.tab[data-tab="data"]');
await pop.waitForTimeout(1400); await beat('backToData');
await pop.evaluate(() => {
  const w = document.getElementById('previewWrap');
  const th = [...w.querySelectorAll('th[data-idx]')].find((t) => /detail:SKU/.test(t.textContent));
  const to = th ? th.offsetLeft - 8 : 700;
  let x = 0; const id = setInterval(() => { x += 22; w.scrollLeft = x; if (x >= to) clearInterval(id); }, 24);
});
await pop.waitForTimeout(3600); await beat('scrolled');
await point('#exportXlsx');
await pop.click('#exportXlsx');
await pop.waitForTimeout(1600);
await point('#exportCsv');
await pop.click('#exportCsv');
await pop.waitForTimeout(2400); await beat('exported');

/* 6 -- what changed since last time (Pro) */
await pop.evaluate(async () => {
  const [t] = await chrome.tabs.query({ active: true, currentWindow: true });
  await new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_RESET' }, r));
  await new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_DETECT' }, r));
  return new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_SNAPSHOT_SAVE' }, r));
});
await pop.reload({ waitUntil: 'load' }); await dress();
await pop.waitForTimeout(1600); await beat('keptFirst');
const moved = await site.evaluate(() => {
  const cards = [...document.querySelectorAll('article.product')];
  const out = { repriced: 0, soldOut: 0, removed: 0, added: 0 };
  cards.slice(1, 4).forEach((c) => {
    const p = c.querySelector('.price'); if (!p) return;
    p.textContent = p.textContent.replace(/([\d.]+)/, (m0) => (Number(m0) + 15).toFixed(2)); out.repriced++;
  });
  cards.slice(4, 6).forEach((c) => { const st = c.querySelector('.stock'); if (st) { st.textContent = 'Sold out'; out.soldOut++; } });
  if (cards[7]) { cards[7].remove(); out.removed++; }
  if (cards[0]) {
    const clone = cards[0].cloneNode(true);
    const sku = clone.querySelector('.sku'); const name = clone.querySelector('h3 a') || clone.querySelector('h3');
    if (sku) sku.textContent = 'NW-1042'; if (name) name.textContent = 'Ash Serving Board, Small';
    cards[0].parentNode.insertBefore(clone, cards[0]); out.added++;
  }
  return out;
});
console.log('  the shop moved on:', JSON.stringify(moved));
await pop.evaluate(async () => {
  const [t] = await chrome.tabs.query({ active: true, currentWindow: true });
  return new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_DETECT' }, r));
});
await pop.reload({ waitUntil: 'load' }); await dress();
await pop.waitForTimeout(2000);
await point('.tab[data-tab="diff"]');
await pop.click('.tab[data-tab="diff"]');
await pop.waitForTimeout(1100); await beat('changesUp');
const diff = await pop.evaluate(() => ({
  ready: !document.getElementById('diffReady').hidden,
  summary: document.getElementById('diffText').textContent.replace(/\s+/g, ' ').trim(),
  rows: document.querySelectorAll('#diffWrap tbody tr').length,
}));
console.log('  changes:', JSON.stringify(diff).slice(0, 160));
if (!diff.ready || !diff.rows) throw new Error('no comparison to film: ' + JSON.stringify(diff));
await pop.waitForTimeout(10500); await beat('changed');

const path = await pop.video().path();
await ctx.close();
renameSync(path, join(S, 'raw-walk.webm'));
writeFileSync(join(S, 'beats-walk.json'), JSON.stringify({ wall: mark, order }, null, 2));
console.log('\nraw-walk.webm written; beats:', JSON.stringify(mark));

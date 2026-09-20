/* Record the real extension against the new storefront, at 1080p, with the
   popup scaled up so it reads at video size. Everything on screen is real. */
import { chromium } from 'playwright';
import { mkdtempSync, cpSync, rmSync, readFileSync, writeFileSync, renameSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

const S = '/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad';
const EXT = join(S, 'extpromo'), VID = join(S, 'vid');
rmSync(EXT, { recursive: true, force: true }); rmSync(VID, { recursive: true, force: true });
cpSync('/home/user/Magic-Data-Scraper-', EXT, { recursive: true });
rmSync(join(EXT, '.git'), { recursive: true, force: true });
const m = JSON.parse(readFileSync(join(EXT, 'manifest.json'), 'utf8'));
m.permissions = ['activeTab', 'scripting', 'downloads', 'tabs', 'storage'];
m.host_permissions = ['<all_urls>'];
delete m.optional_permissions; delete m.optional_host_permissions;
writeFileSync(join(EXT, 'manifest.json'), JSON.stringify(m, null, 2));

const ctx = await chromium.launchPersistentContext(mkdtempSync(join(tmpdir(), 'mdspr-')), {
  headless: true,
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  viewport: { width: 1920, height: 1080 },
  recordVideo: { dir: VID, size: { width: 1920, height: 1080 } },
  args: [`--disable-extensions-except=${EXT}`, `--load-extension=${EXT}`, '--no-sandbox',
         '--disable-dev-shm-usage', '--host-resolver-rules=MAP shop.example.com 127.0.0.1',
         '--proxy-bypass-list=*'],
});
const sw = ctx.serviceWorkers()[0] || await ctx.waitForEvent('serviceworker', { timeout: 15000 });
const extId = new URL(sw.url()).host;
await sw.evaluate(() => chrome.storage.local.set({ mds_license: { pro: true, at: Date.now() } }));

const site = await ctx.newPage();
await site.setViewportSize({ width: 1920, height: 1080 });
await site.goto('http://shop.example.com/demo/catalogue.html', { waitUntil: 'load' });
await site.waitForTimeout(700);
const shot = (await site.screenshot()).toString('base64');
const tab = await sw.evaluate(async () => (await chrome.tabs.query({}))
  .filter((t) => t.url && t.url.includes('/demo/')).map((t) => t.id)[0]);

const pop = await ctx.newPage();
await sw.evaluate((id) => chrome.tabs.update(id, { active: true }), tab);
await pop.goto(`chrome-extension://${extId}/popup.html`, { waitUntil: 'load' });
/* Re-applied after every reload. addStyleTag does not survive one, and a
   reload part-way through cost the last nine seconds of the video its
   backdrop and its scale -- the popup rendered plain in the top-left corner
   on white, under a caption about the feature it was supposed to be showing. */
const STAGE = `
  html { background:#0e0d14; }
  html::before { content:""; position:fixed; inset:0; z-index:-2;
    background-image:url("data:image/png;base64,${shot}");
    background-size:1920px auto; background-position:center top; background-repeat:no-repeat; }
  html::after { content:""; position:fixed; inset:0; z-index:-1;
    background:linear-gradient(90deg,rgba(14,13,20,.90) 0%,rgba(14,13,20,.82) 38%,
               rgba(14,13,20,.46) 62%,rgba(14,13,20,.30) 100%); }
  /* 1.42, not 1.5: with the drill step open and its progress line running the
     popup is about 720 CSS px tall, and 1.5 pushed the header off the top of
     the 1080 frame -- the row/page chips are the one thing that must stay in
     shot. The recorder logs the composed height so this stays honest. */
  body { position:absolute; right:110px; top:50%;
         transform:translateY(-50%) scale(1.42); transform-origin:right center;
         border-radius:14px; overflow:hidden;
         box-shadow:0 50px 110px -24px rgba(0,0,0,.9), 0 0 0 1px rgba(255,255,255,.12); }
`;
const dress = () => pop.addStyleTag({ content: STAGE });
await dress();

const mark = {};
const beat = (n) => { mark[n] = Date.now() - t0; console.log(n, '@', (mark[n]/1000).toFixed(2) + 's'); };
const t0 = Date.now();

await pop.waitForTimeout(3400);  beat('detected');
console.log('  rows:', await pop.evaluate(() => document.getElementById('statRows').textContent));

await pop.click('.tab[data-tab="crawl"]');
await pop.waitForTimeout(1200);
await pop.evaluate(() => { minDelay.value = '0.85'; maxDelay.value = '1.0'; });
beat('crawlStart');
await pop.click('#startCrawl');
await pop.waitForFunction(() => /Done\./.test(document.getElementById('status').textContent),
  null, { timeout: 90000 }).catch(() => {});
await pop.waitForTimeout(1200); beat('crawlDone');
console.log('  crawled:', await pop.evaluate(() =>
  document.getElementById('statRows').textContent + ' rows / ' + document.getElementById('statPages').textContent + ' pages'));

// Stay on the Crawl tab and open the drill step: the drill's own progress line
// ("Drilling 31 / 54...") lives there, so the run has something to watch. The
// Data tab during a drill is a still table plus the quality banner warning that
// the detail columns are still empty, which is true but not a promo.
await pop.click('.step[data-step="3"] .step-head');
await pop.waitForTimeout(900);
await pop.check('#drillEnable');
await pop.waitForTimeout(1100); beat('drillReady');

// drill every row of the crawl so nothing is blank on camera
const items = await pop.evaluate(async () => {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const r = await new Promise((res) => chrome.tabs.sendMessage(tabs[0].id, { type: 'MDS_FULL_DATA' }, res));
  const col = Object.keys(r.rows[0]).find((k) => /^link$/i.test(k));
  // Every row, not the first nine. Drilling a subset leaves the other rows'
  // detail columns blank, and the popup correctly says so -- "11 of 22 columns
  // are mostly empty" is not a caption you want in a promo, and the fix is to
  // do the thing the video claims rather than to hide the warning.
  return r.rows.map((row, i) => ({ index: i, url: row[col] })).filter((x) => x.url);
});
beat('drillStart');
await pop.evaluate((its) => chrome.runtime.sendMessage({
  type: 'MDS_DRILL_START', items: its,
  opts: { minDelay: 0.05, maxDelay: 0.1, area: -1, openOnError: false, maxRows: 0 }
}), items);
for (let i = 0; i < 400; i++) {
  const st = await sw.evaluate(async () => (await chrome.storage.local.get('mds_drill_status')).mds_drill_status || null);
  if (st && st.running === false) break;
  await pop.waitForTimeout(400);
}
await pop.waitForTimeout(1600); beat('drillDone');
console.log('  popup height on camera:',
  Math.round(await pop.evaluate(() => document.body.getBoundingClientRect().height)), 'px of 1080');

await pop.click('.tab[data-tab="data"]');
await pop.waitForTimeout(1400); beat('backToData');

// slide across to the columns that came from the detail pages
await pop.evaluate(() => {
  const w = document.getElementById('previewWrap');
  const th = [...w.querySelectorAll('th[data-idx]')].find((t) => /detail:SKU/.test(t.textContent));
  const to = th ? th.offsetLeft - 8 : 700;
  let x = 0; const id = setInterval(() => { x += 26; w.scrollLeft = x; if (x >= to) clearInterval(id); }, 24);
});
await pop.waitForTimeout(2600); beat('scrolled');

await pop.click('#exportCsv');
await pop.waitForTimeout(2200); beat('exported');

/* ---- and what changed since last time ----
 *
 * A real comparison rather than a mocked one. Page one on its own, not the
 * 54-row crawl: two six-page crawls would add forty seconds of counter to a
 * forty-second video, and the feature is the same either way. Everything here
 * is a message the popup itself sends -- reset, detect, keep -- so what ends
 * up on camera is the extension diffing two readings it genuinely took.
 */
const reset = await pop.evaluate(async () => {
  const [t] = await chrome.tabs.query({ active: true, currentWindow: true });
  await new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_RESET' }, r));
  await new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_DETECT' }, r));
  return new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_SNAPSHOT_SAVE' }, r));
});
console.log('  kept page one:', JSON.stringify(reset).slice(0, 80));
await pop.reload({ waitUntil: 'load' }); await dress();
await pop.waitForTimeout(1800); beat('keptFirst');

// the shop moves on, in the page that is on camera behind the popup
const moved = await site.evaluate(() => {
  const cards = [...document.querySelectorAll('article.product')];
  const out = { repriced: 0, soldOut: 0, removed: 0, added: 0 };
  cards.slice(1, 4).forEach((c) => {
    const p = c.querySelector('.price');
    if (!p) return;
    p.textContent = p.textContent.replace(/([\d.]+)/, (m0) => (Number(m0) + 15).toFixed(2));
    out.repriced++;
  });
  cards.slice(4, 6).forEach((c) => {
    const st = c.querySelector('.stock');
    if (st) { st.textContent = 'Sold out'; out.soldOut++; }
  });
  if (cards[7]) { cards[7].remove(); out.removed++; }
  if (cards[0]) {
    const clone = cards[0].cloneNode(true);
    const sku = clone.querySelector('.sku');
    const name = clone.querySelector('h3 a') || clone.querySelector('h3');
    if (sku) sku.textContent = 'NW-1042';
    if (name) name.textContent = 'Ash Serving Board, Small';
    cards[0].parentNode.insertBefore(clone, cards[0]);
    out.added++;
  }
  return out;
});
console.log('  the shop moved on:', JSON.stringify(moved));
await pop.evaluate(async () => {
  const [t] = await chrome.tabs.query({ active: true, currentWindow: true });
  return new Promise((r) => chrome.tabs.sendMessage(t.id, { type: 'MDS_DETECT' }, r));
});
await pop.reload({ waitUntil: 'load' }); await dress();
await pop.waitForTimeout(2200);
await pop.click('.tab[data-tab="diff"]');
await pop.waitForTimeout(1100); beat('changesUp');
const diff = await pop.evaluate(() => ({
  ready: !document.getElementById('diffReady').hidden,
  summary: document.getElementById('diffText').textContent.replace(/\s+/g, ' ').trim(),
  rows: document.querySelectorAll('#diffWrap tbody tr').length,
}));
console.log('  changes:', JSON.stringify(diff).slice(0, 160));
if (!diff.ready || !diff.rows) throw new Error('no comparison to film: ' + JSON.stringify(diff));
// slide across to the cells that moved. getBoundingClientRect reports
// transformed pixels and the stage scales the popup by 1.42, while
// scrollLeft is untransformed -- so every correction measured off a rect has
// to be divided back down or it overshoots by 42%. That is why three passes
// of the same snap that works in the screenshot tool never converged here.
await pop.evaluate(() => {
  const wrap = document.getElementById('diffWrap');
  const cell = wrap.querySelector('td.moved');
  if (!cell) return;
  const ths = [...wrap.querySelectorAll('thead th')];
  const i = Math.max(1, cell.cellIndex - 1);
  const scale = wrap.getBoundingClientRect().width / wrap.offsetWidth || 1;
  const target = wrap.scrollLeft +
    (ths[i].getBoundingClientRect().left - ths[0].getBoundingClientRect().right) / scale;
  let x = wrap.scrollLeft;
  const id = setInterval(() => {
    x = Math.min(x + 26, target);
    wrap.scrollLeft = x;
    if (x >= target) clearInterval(id);
  }, 24);
});
await pop.waitForTimeout(1600);
// ...then settle exactly on a column edge, in a call of its own once the
// animation has stopped.
const landed = await pop.evaluate(() => {
  const wrap = document.getElementById('diffWrap');
  const ths = [...wrap.querySelectorAll('thead th')];
  const cell = wrap.querySelector('td.moved');
  const i = Math.max(1, cell.cellIndex - 1);
  const scale = wrap.getBoundingClientRect().width / wrap.offsetWidth || 1;
  const gap = () => (ths[i].getBoundingClientRect().left - ths[0].getBoundingClientRect().right) / scale;
  const before = gap();
  const steps = [];
  for (let p = 0; p < 6; p++) {
    wrap.scrollLeft += gap();
    steps.push(Math.round(gap() * 10) / 10);
  }
  return { startsAt: ths[i].textContent.trim(), i, cellIndex: cell.cellIndex,
           scale: Math.round(scale * 100) / 100,
           before: Math.round(before), steps,
           scrollLeft: Math.round(wrap.scrollLeft),
           maxScroll: Math.round(wrap.scrollWidth - wrap.clientWidth),
           residual: Math.round(gap() * 10) / 10 };
});
console.log('  settled on:', JSON.stringify(landed));
// The column it aimed at has to actually be at the sticky column's edge.
// Checking only for a straddling cell passed happily while the scroll sat a
// whole column short, leaving the tail of the one before on camera.
if (Math.abs(landed.residual) > 2) {
  throw new Error('the scroll did not land on a column edge: ' + JSON.stringify(landed));
}
await pop.waitForTimeout(4200); beat('changed');

const path = await pop.video().path();
await ctx.close();
renameSync(path, join(S, 'raw.webm'));
writeFileSync(join(S, 'beats.json'), JSON.stringify(mark, null, 2));
console.log('\nraw.webm written; beats:', JSON.stringify(mark));

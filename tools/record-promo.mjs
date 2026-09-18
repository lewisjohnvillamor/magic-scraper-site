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
await pop.addStyleTag({ content: `
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
` });

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

const path = await pop.video().path();
await ctx.close();
renameSync(path, join(S, 'raw.webm'));
writeFileSync(join(S, 'beats.json'), JSON.stringify(mark, null, 2));
console.log('\nraw.webm written; beats:', JSON.stringify(mark));

/* A second plate, for the short-form cut: the popup over the 2,000-row list,
   scaled up so it reads at phone size, crawling all forty pages.
 *
 * The landscape promo's plate tops out at "54 rows · 6 pages", which is the
 * truth about a six-page catalogue and a weak first second on a feed where the
 * first second is the whole job. This one's counter runs to four figures.
 *
 * Recorded in full and cut afterwards, the same as the drill in the landscape
 * cut: every frame is the real thing, only the waiting is shortened.
 */
import { chromium } from 'playwright';
import { mkdtempSync, cpSync, rmSync, readFileSync, writeFileSync, renameSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

const S = '/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad';
const EXT = join(S, 'extbulkplate'), VID = join(S, 'vidbulk');
rmSync(EXT, { recursive: true, force: true }); rmSync(VID, { recursive: true, force: true });
cpSync('/home/user/Magic-Data-Scraper-', EXT, { recursive: true });
rmSync(join(EXT, '.git'), { recursive: true, force: true });
const m = JSON.parse(readFileSync(join(EXT, 'manifest.json'), 'utf8'));
m.permissions = ['activeTab', 'scripting', 'downloads', 'tabs', 'storage'];
m.host_permissions = ['<all_urls>'];
delete m.optional_permissions; delete m.optional_host_permissions;
writeFileSync(join(EXT, 'manifest.json'), JSON.stringify(m, null, 2));

const ctx = await chromium.launchPersistentContext(mkdtempSync(join(tmpdir(), 'mdsbp-')), {
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
await site.goto('http://shop.example.com/demo/bulk.html', { waitUntil: 'load' });
await site.waitForTimeout(700);
const shot = (await site.screenshot()).toString('base64');
const tab = await sw.evaluate(async () => (await chrome.tabs.query({}))
  .filter((t) => t.url && t.url.includes('/demo/bulk')).map((t) => t.id)[0]);

const pop = await ctx.newPage();
await sw.evaluate((id) => chrome.tabs.update(id, { active: true }), tab);
await pop.goto(`chrome-extension://${extId}/popup.html`, { waitUntil: 'load' });
// Centred rather than pinned right: the vertical crop takes a column out of
// the middle of the frame, so the popup has to be in it.
const STAGE = `
  html { background:#0b0a10; }
  html::before { content:""; position:fixed; inset:0; z-index:-2;
    background-image:url("data:image/png;base64,${shot}");
    background-size:1920px auto; background-position:center top; background-repeat:no-repeat; }
  html::after { content:""; position:fixed; inset:0; z-index:-1;
    background:linear-gradient(180deg,rgba(11,10,16,.82) 0%,rgba(11,10,16,.62) 50%,rgba(11,10,16,.86) 100%); }
  body { position:absolute; left:50%; top:50%;
         transform:translate(-50%,-50%) scale(1.5); transform-origin:center center;
         border-radius:16px; overflow:hidden;
         box-shadow:0 60px 120px -30px rgba(0,0,0,.95), 0 0 0 1px rgba(255,255,255,.14); }
`;
const dress = () => pop.addStyleTag({ content: STAGE });
await dress();

const mark = {};
const t0 = Date.now();
const beat = (n) => { mark[n] = Date.now() - t0; console.log(n, '@', (mark[n] / 1000).toFixed(2) + 's'); };

await pop.waitForTimeout(3200); beat('detected');
console.log('  rows:', await pop.evaluate(() => document.getElementById('statRows').textContent));

await pop.click('.tab[data-tab="crawl"]');
await pop.waitForTimeout(900);
await pop.evaluate(() => {
  const h = document.querySelector('.step[data-step="1"] .step-head');
  if (h.getAttribute('aria-expanded') !== 'true') h.click();
});
await pop.waitForTimeout(400);
await pop.click('#autoNext'); await pop.waitForTimeout(700);
await pop.evaluate(() => { document.getElementById('minDelay').value = '0';
                           document.getElementById('maxDelay').value = '0'; });
beat('crawlStart');
await pop.click('#startCrawl');
// Mark the moment each round number goes by, so the cut can land on them.
const seen = {};
for (let i = 0; i < 600; i++) {
  const n = await pop.evaluate(() => Number(document.getElementById('statRows').textContent));
  [250, 500, 1000, 1500].forEach((k) => { if (!seen[k] && n >= k) { seen[k] = true; beat('rows' + k); } });
  const busy = await pop.evaluate(() => !document.getElementById('busy').hidden);
  if (!busy && i > 6) break;
  await pop.waitForTimeout(500);
}
await pop.waitForTimeout(1600); beat('crawlDone');
console.log('  crawled:', await pop.evaluate(() =>
  document.getElementById('statRows').textContent + ' rows / ' +
  document.getElementById('statPages').textContent + ' pages'));

await pop.click('.tab[data-tab="data"]');
await pop.waitForTimeout(1800); beat('data');
await pop.click('#exportCsv');
await pop.waitForTimeout(2000); beat('exported');

const path = await pop.video().path();
await ctx.close();
renameSync(path, join(S, 'bulk-plate.webm'));
writeFileSync(join(S, 'bulk-beats.json'), JSON.stringify(mark, null, 2));
console.log('\nbulk-plate.webm written; beats:', JSON.stringify(mark));

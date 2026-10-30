// Run from tools/guides with the site served on 127.0.0.1:80 (python3 -m http.server 80).
/* Real screenshots of the extension on the sandbox, for the pain-point guides.
   Each shot is the sandbox page with the popup open beside it, 1280x800, saved
   as WebP (encoded by Chromium's canvas, so no image tools are needed).
   Usage: node shoot.mjs [only-this-shot] */
import { chromium } from 'playwright';
import { cpSync, rmSync, readFileSync, writeFileSync, mkdtempSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

const OUT = '/home/user/magic-scraper-site/assets/guides';
const BASE = 'http://magicscraper.app/demo/';
const only = process.argv[2];
const EXT = mkdtempSync(join(tmpdir(), 'mds-shot-ext-'));
cpSync('/home/user/Magic-Data-Scraper-', EXT, { recursive: true, filter: (p) => !/node_modules|\.git($|\/)|dist/.test(p) });
const m = JSON.parse(readFileSync(join(EXT, 'manifest.json'), 'utf8'));
m.permissions = ['activeTab', 'scripting', 'downloads', 'tabs', 'storage', 'sidePanel', 'identity'];
m.host_permissions = ['<all_urls>'];
delete m.optional_permissions; delete m.optional_host_permissions;
writeFileSync(join(EXT, 'manifest.json'), JSON.stringify(m, null, 2));

const ctx = await chromium.launchPersistentContext(mkdtempSync(join(tmpdir(), 'mds-shot-')), {
  headless: true, executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1,
  args: [`--disable-extensions-except=${EXT}`, `--load-extension=${EXT}`, '--no-sandbox', '--disable-dev-shm-usage', '--host-resolver-rules=MAP magicscraper.app 127.0.0.1', '--proxy-bypass-list=*', '--proxy-server=direct://'],
});
let sw = null;
for (let i = 0; i < 40 && !sw; i++) {
  for (const w of ctx.serviceWorkers())
    if (await w.evaluate(() => !!(self.chrome && chrome.storage && chrome.tabs)).catch(() => false)) sw = w;
  if (!sw) await new Promise((r) => setTimeout(r, 500));
}
if (!sw) throw new Error('worker never started');
const extId = new URL(sw.url()).host;
// Close the welcome tab a first install opens, so it never becomes the "active" tab.
await new Promise((r) => setTimeout(r, 1500));
for (const p of ctx.pages()) if (/welcome/.test(p.url())) await p.close();

const STAGE = (shot) => `
  html { background:#ece8df; }
  html::before { content:""; position:fixed; inset:0; z-index:-2;
    background-image:url("data:image/png;base64,${shot}"); background-size:1280px auto;
    background-position:left top; background-repeat:no-repeat; }
  html::after { content:""; position:fixed; inset:0; z-index:-1; background:rgba(20,18,28,.30); }
  body { position:absolute; right:28px; top:22px; transform:scale(1.0); transform-origin:right top;
    border-radius:12px; overflow:hidden; max-height:756px;
    box-shadow:0 30px 70px -18px rgba(0,0,0,.55), 0 0 0 1px rgba(0,0,0,.10); }
  #ver { visibility:hidden; }
`;

async function openSite(file) {
  const site = await ctx.newPage();
  await site.goto(BASE + file, { waitUntil: 'load' });
  await site.waitForTimeout(800);
  const tab = await sw.evaluate(async (f) => (await chrome.tabs.query({}))
    .filter((t) => t.url && t.url.includes('/demo/' + f)).map((t) => t.id)[0], file);
  return { site, tab };
}
async function openPopup(site, tab) {
  const shot = (await site.screenshot()).toString('base64');
  const pop = await ctx.newPage();
  await sw.evaluate((id) => chrome.tabs.update(id, { active: true }), tab);
  await pop.goto(`chrome-extension://${extId}/popup.html`, { waitUntil: 'load' });
  await pop.waitForTimeout(1500);
  return { pop, dress: () => pop.addStyleTag({ content: STAGE(shot) }) };
}
async function save(page, name) {
  const png = (await page.screenshot()).toString('base64');
  const enc = await ctx.newPage();
  await enc.setContent('<canvas></canvas>');
  const webp = await enc.evaluate(async (b64) => {
    const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
    const c = document.querySelector('canvas'); c.width = img.width; c.height = img.height;
    c.getContext('2d').drawImage(img, 0, 0);
    return c.toDataURL('image/webp', 0.86).split(',')[1];
  }, png);
  await enc.close();
  writeFileSync(join(OUT, name + '.webp'), Buffer.from(webp, 'base64'));
  writeFileSync(join(process.env.PREVIEW_DIR || tmpdir(), name + '.preview.png'), Buffer.from(png, 'base64'));
  console.log('saved', name);
}
const send = (tab, msg) => sw.evaluate(([i, x]) => chrome.tabs.sendMessage(i, x), [tab, msg]);

// 1. Load more, crawled to the end: the Crawl tab says why it stopped.
if (!only || only === 'loadmore') {
  const { site, tab } = await openSite('reviews.html');
  const { pop, dress } = await openPopup(site, tab);
  await pop.click('.tab[data-tab="crawl"]');
  await pop.waitForTimeout(400);
  await pop.selectOption('select:has(option[value="fast"])', 'fast').catch(() => {});
  if (await pop.isVisible('#autoNext')) await pop.click('#autoNext');
  for (let i = 0; i < 10; i++) {
    await pop.waitForTimeout(1000);
    const st = (await pop.textContent('#status').catch(() => '')) || '';
    console.log('  after autoNext', i, '|', st.trim().slice(0, 160));
    if (/found|Next|Load more|error|Could not/i.test(st) && i > 1) break;
  }
  await pop.click('#startCrawl');
  for (let i = 0; i < 40; i++) {
    const st = (await pop.textContent('#status').catch(() => '')) || '';
    const cw = (await pop.textContent('#crawlWhere').catch(() => '')) || '';
    console.log('  t', i * 3, '|', st.trim().slice(0, 140), '|', cw.trim().slice(0, 80));
    if (/Done|Stopped because|Finished/i.test(st)) break;
    await pop.waitForTimeout(3000);
  }
  await pop.waitForTimeout(800);
  // Shoot the page as it now is (48 reviews loaded) behind the popup.
  const shot = (await site.screenshot()).toString('base64');
  await pop.addStyleTag({ content: STAGE(shot) });
  await pop.waitForTimeout(500);
  await save(pop, 'crawl-load-more');
  console.log('  status:', await pop.textContent('#status'));
  await pop.close(); await site.close();
}

// 2. Picked by hand on the awkward page, with the discount shift-clicked in as a column.
if (!only || only === 'pick') {
  const { site, tab } = await openSite('awkward.html');
  await sw.evaluate((i) => chrome.scripting.executeScript({ target: { tabId: i }, files: ['content.js'] }), tab);
  await send(tab, { type: 'MDS_DETECT' });
  await send(tab, { type: 'MDS_PICK_AREA' });
  await site.click('table.data tbody tr:nth-child(2) td:nth-child(1)');
  await site.click('#discount', { modifiers: ['Shift'] });
  await site.keyboard.press('Enter');
  await site.waitForTimeout(800);
  const { pop, dress } = await openPopup(site, tab);
  await pop.evaluate(() => { const x = document.getElementById('drillHintX'); if (x && x.offsetParent) x.click(); });
  await pop.waitForTimeout(300);
  console.log('  columns:', await pop.evaluate(() => [...document.querySelectorAll('table th')].map((t) => t.textContent.trim()).join(' | ')));
  await pop.evaluate(() => {
    const t = document.querySelector('table'); let w = t && t.parentElement;
    while (w && w.scrollWidth <= w.clientWidth + 2) w = w.parentElement;
    if (w) w.scrollLeft = w.scrollWidth;
  });
  await dress(); await pop.waitForTimeout(500);
  await save(pop, 'pick-manually');
  await pop.close(); await site.close();
}

// 3. The free drill-down limit, stated on the control before a run.
if (!only || only === 'drillfree') {
  const { site, tab } = await openSite('catalogue.html');
  const { pop, dress } = await openPopup(site, tab);
  await pop.click('.tab[data-tab="crawl"]');
  await pop.waitForTimeout(500);
  await pop.click('.step[data-step="3"] .step-head');
  await pop.waitForTimeout(600);
  await pop.evaluate(() => { const n = document.getElementById('drillFreeNote'); if (n) n.scrollIntoView({ block: 'center' }); });
  await dress(); await pop.waitForTimeout(500);
  await save(pop, 'drill-free-rows');
  console.log('  note:', await pop.textContent('#drillFreeNote').catch(() => ''));
  await pop.close(); await site.close();
}

await ctx.close();
rmSync(EXT, { recursive: true, force: true });

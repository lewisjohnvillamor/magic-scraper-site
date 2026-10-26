import { chromium } from 'playwright';
import { readFileSync, writeFileSync } from 'fs';
const S = process.env.PREVIEW_DIR || '/tmp';
const SITE = '/home/user/magic-scraper-site';
const font = readFileSync(SITE + '/assets/fonts/archivo-var.woff2').toString('base64');
const b64 = (p) => readFileSync(p).toString('base64');
const BG = {
  crawl: 'data:image/webp;base64,' + b64(SITE + '/assets/guides/crawl-load-more.webp'),
  pick: 'data:image/webp;base64,' + b64(SITE + '/assets/guides/pick-manually.webp'),
  drill: 'data:image/webp;base64,' + b64(SITE + '/assets/guides/drill-free-rows.webp'),
  dir: 'data:image/webp;base64,' + b64(SITE + '/assets/directory.webp'),
  hook: 'data:image/webp;base64,' + b64(SITE + '/assets/guides/webhook-frame.webp'),
};
const cards = [
  ['scraper-only-scrapes-first-page', 'crawl', 'Stuck on page one?', 'Get every page.', 'Why scrapers stop at page 1, and the fix for Next buttons, Load more and infinite scroll.', ['Free', 'No page limit', 'Says why it stopped']],
  ['scraper-not-working-on-this-site', 'pick', 'Scraper found nothing?', 'Point at it yourself.', 'What to try when a scraper says it doesn\'t support the site, and which sites no tool should promise.', ['Pick by hand', 'Shift-click extra fields', 'Free']],
  ['scraper-missing-data', 'dir', 'Rows missing?', 'Phones gone?', 'Why a scraped sheet comes back short, and why Excel drops leading zeros.', ['XLSX keeps zeros', 'UTF-8 safe CSV', 'Free']],
  ['web-scraper-no-subscription', 'drill', 'No credits. No trial.', 'Pay once, or never.', 'What the free version does, what $25 once adds, and five questions to ask any scraper first.', ['No account', 'Nothing renews', '7-day refund']],
  ['web-scraper-extension-privacy', 'crawl', 'Is your scraper safe?', 'Check what it sends.', 'A ten-minute check for any extension: permissions, disclosures, network requests, owner.', ['No analytics', 'No AI service', 'Data stays local']],
  ['changelog', 'drill', 'Every update,', 'in plain words.', 'What each Magic Scraper release changed, including anything removed or moved to Pro.', ['v1.23 in the stores', 'Updates included']],
  ['scraped-data-webhook-node-php', 'hook', 'Scraped rows,', 'to your server.', 'Webhook receivers in Node.js and PHP, about 40 lines each, and the safe way to hand rows to a shell script.', ['Node.js', 'PHP', 'No packages']],
];
const fraunces = readFileSync(SITE + '/assets/fonts/fraunces-var.woff2').toString('base64');
// The default share picture for every page without its own card.
cards.push(['og', 'crawl', 'Any web list,', 'into a spreadsheet.', 'Find the table, follow every page, open the page behind each row, and export it. No account, no tracking, no server of ours.', ['Free', 'Chrome & Edge', 'Runs in your browser']]);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
for (const [slug, bg, l1, l2, sub, pills] of cards) {
  // The website's identity: warm paper, ink, the second line in rust italic,
  // and the screenshot as a framed card, as the site shows them.
  await pg.setContent(`<!doctype html><style>
  @font-face { font-family: Archivo; src: url(data:font/woff2;base64,${font}) format('woff2'); font-weight: 100 900; }
  @font-face { font-family: Fraunces; src: url(data:font/woff2;base64,${fraunces}) format('woff2'); font-weight: 100 900; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { width:1200px; height:630px; overflow:hidden; font-family: Archivo, sans-serif; color:#17150f; background:#faf8f4; position:relative; }
  .shot { position:absolute; left:700px; top:58px; width:620px; height:514px; border:1px solid #17150f; background:#fff url(${BG[bg]}) ${bg === 'dir' ? 'right -110px top' : 'right top'} / ${bg === 'hook' ? '900px' : '1080px'} auto no-repeat;
          box-shadow: 22px 22px 0 -10px rgba(23,21,15,.08); }
  .t { position:absolute; left:56px; top:0; bottom:0; width:600px; display:flex; flex-direction:column; justify-content:center; }
  .brand { display:flex; align-items:center; gap:12px; margin-bottom:30px; font-family:Fraunces, serif; font-weight:600; font-size:24px; letter-spacing:-.3px; }
  .g { width:36px; height:36px; border-radius:9px; background:#17150f; display:grid; place-items:center; }
  h1 { font-family:Fraunces, serif; font-size:60px; line-height:1.03; font-weight:600; letter-spacing:-1.2px; font-variation-settings:'SOFT' 0,'WONK' 1,'opsz' 100; }
  h1 span { color:#b4491f; font-style:italic; display:block; }
  p { margin-top:20px; font-size:23px; line-height:1.42; color:#5d574a; max-width:580px; }
  .pills { margin-top:26px; display:flex; gap:10px; flex-wrap:wrap; }
  .pills b { font-weight:500; font-size:18px; padding:7px 14px; border-radius:999px; background:#fffefb; border:1px solid #e0dbd0; }
  </style><body><div class="shot"></div><div class="t">
  <div class="brand"><span class="g"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#faf8f4" stroke-width="2.4" stroke-linecap="round"><path d="M4 20 L14 10"/><path d="M18 3 v5 M15.5 5.5 h5"/></svg></span>Magic Scraper</div>
  <h1>${l1}<span>${l2}</span></h1><p>${sub}</p>
  <div class="pills">${pills.map((x) => `<b>${x}</b>`).join('')}</div></div></body>`);
  await pg.evaluate(() => document.fonts.ready);
  await pg.waitForTimeout(300);
  const jpg = await pg.screenshot({ type: 'jpeg', quality: 86 });
  writeFileSync(slug === 'og' ? `${SITE}/assets/og.jpg` : `${SITE}/assets/og/${slug}.jpg`, jpg);
  writeFileSync(`${S}/og-${slug}.png`, await pg.screenshot());
  console.log('og', slug, jpg.length);
}
await b.close();

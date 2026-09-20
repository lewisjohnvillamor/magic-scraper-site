/* The short-form cut: 1080x1920, ~23s, recorded in one pass.
 *
 * Unlike the landscape promo there is no ffmpeg compositing here. The whole
 * thing is a page -- tools/tiktok/stage.html -- that plays the two recorded
 * plates behind kinetic captions and walks its own timeline. Playwright records
 * that page. What you get in a browser is what lands in the file, which is the
 * only way a cut this fast stays editable: change a beat, reload, look.
 *
 * Captions use motion-anything's kinetic-headline and count-up recipes,
 * vendored under tools/vendor/motion-anything/ (Apache-2.0, see its README for
 * why those two and not the others).
 *
 *   node tools/record-bulk-plate.mjs     # the 40-page plate, if it is stale
 *   node tools/record-promo.mjs          # the landscape plate, for drill + changes
 *   node tools/record-tiktok.mjs
 */
import { chromium } from 'playwright';
import { readFileSync, writeFileSync, existsSync, renameSync, rmSync, copyFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const HERE = dirname(fileURLToPath(import.meta.url));
const S = '/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad';
const VID = join(S, 'vidtiktok');
rmSync(VID, { recursive: true, force: true });

for (const f of ['bulk-plate.webm', 'bulk-beats.json', 'raw.webm', 'beats.json']) {
  if (!existsSync(join(S, f))) {
    throw new Error('missing ' + f + ' -- record the plates first (see the header)');
  }
}
const bulkBeats = JSON.parse(readFileSync(join(S, 'bulk-beats.json'), 'utf8'));
const mainBeats = JSON.parse(readFileSync(join(S, 'beats.json'), 'utf8'));
console.log('bulk plate beats:', JSON.stringify(bulkBeats));
console.log('main plate beats:', JSON.stringify(mainBeats));

// Where in each plate the cut looks, taken from what the recorders measured
// rather than from numbers typed here.
const marks = {
  chaseFrom: bulkBeats.crawlStart / 1000 + 0.35,   // the counter starting to run
  tail: bulkBeats.data / 1000 + 0.35,              // sitting on the finished total
  drill: mainBeats.drillStart / 1000 + 7.0,        // mid-drill, its counter moving
  changes: mainBeats.changesUp / 1000 + 3.2,       // the Changes table, scrolled to the diff
};
console.log('marks:', JSON.stringify(marks));

// The plates have to be same-origin with the page, so serve everything from
// one directory the page can reach.
copyFileSync(join(S, 'bulk-plate.webm'), join(HERE, 'tiktok', 'bulk-plate.webm'));
copyFileSync(join(S, 'raw.webm'), join(HERE, 'tiktok', 'main-plate.webm'));

const browser = await chromium.launch({
  headless: true,
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--autoplay-policy=no-user-gesture-required'],
});
const ctx = await browser.newContext({
  viewport: { width: 1080, height: 1920 },
  recordVideo: { dir: VID, size: { width: 1080, height: 1920 } },
});
const filmingFrom = Date.now();          // recording starts with the context
const page = await ctx.newPage();
page.on('console', (c) => { if (c.type() === 'error') console.log('  page error:', c.text()); });
page.on('pageerror', (e) => console.log('  pageerror:', e.message));
await page.goto('file://' + join(HERE, 'tiktok', 'stage.html'), { waitUntil: 'load' });
await page.waitForTimeout(1200);          // fonts

const started = Date.now();
await page.evaluate(([m]) => window.__maStart(
  { bulk: 'bulk-plate.webm', main: 'main-plate.webm' }, m), [marks]);
await page.waitForFunction(() => window.__maDone === true, null, { timeout: 90000 });
await page.waitForTimeout(400);
console.log('timeline ran for', ((Date.now() - started) / 1000).toFixed(1) + 's');

const firstBeat = await page.evaluate(() => window.__maFirstBeat || 0);
const head = Math.max(0, (firstBeat - filmingFrom) / 1000);
const path = await page.video().path();
await ctx.close();
await browser.close();
renameSync(path, join(S, 'tiktok-raw.webm'));
writeFileSync(join(S, 'tiktok-head.json'), JSON.stringify({ head: Number(head.toFixed(3)) }, null, 2));
console.log('wrote tiktok-raw.webm; dead head before the first beat: ' + head.toFixed(2) + 's');

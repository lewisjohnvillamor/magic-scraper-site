/* Four sandbox pages, shot at the same size, composed into one 2x2 grid so the
   README carries a single image instead of four that wrap differently. */
import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
const pages = [
  ['catalogue.html', 'Card grid · six pages'],
  ['table.html',     'Plain HTML table'],
  ['scroll.html',    'Infinite scroll'],
  ['awkward.html',   'Value outside the table'],
];
for (const [f] of pages) {
  const p = await b.newPage({ viewport: { width: 1200, height: 780 }, deviceScaleFactor: 1 });
  await p.goto('http://127.0.0.1/demo/' + f, { waitUntil: 'load' });
  await p.waitForTimeout(800);
  await p.screenshot({ path: 'rm_' + f.replace('.html', '') + '.png' });
  await p.close();
}
// compose
const grid = await b.newPage({ viewport: { width: 1240, height: 880 }, deviceScaleFactor: 1 });
const cells = pages.map(([f, label]) =>
  `<figure><img src="rm_${f.replace('.html','')}.png"><figcaption>${label}</figcaption></figure>`).join('');
// setContent resolves relative src against about:blank, so the four shots came
// out as empty boxes. Write the page to disk and load it from there instead.
const html = `<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{width:1240px;height:880px;background:#faf8f4;padding:20px;
       font-family:"Liberation Sans",Arial,sans-serif;
       display:grid;grid-template-columns:1fr 1fr;gap:20px}
  figure{background:#fff;border:1px solid #e0dbd0;border-radius:10px;overflow:hidden;
         display:flex;flex-direction:column}
  img{width:100%;flex:1;object-fit:cover;object-position:top left;display:block;min-height:0}
  figcaption{padding:9px 13px;font-size:15px;color:#5d574a;border-top:1px solid #e0dbd0;background:#fffefb}
</style>${cells}`;
const { writeFileSync } = await import('fs');
writeFileSync('rm_grid.html', html);
await grid.goto('file:///tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad/rm_grid.html',
  { waitUntil: 'load' });
await grid.waitForTimeout(900);
await grid.screenshot({ path: 'readme_sandbox.png' });
await b.close();
console.log('ok');

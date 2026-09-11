import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
const S = '/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad/';
for (const [f, alpha] of [['v_title',0],['v_end',0],['v_cap1',1],['v_cap2',1],['v_cap3',1],['v_cap4',1],['v_foot',1]]) {
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + S + f + '.html', { waitUntil: 'load' });
  await p.waitForTimeout(500);
  await p.screenshot({ path: S + f + '.png', omitBackground: !!alpha });
  await p.close();
}
await b.close(); console.log('ok');

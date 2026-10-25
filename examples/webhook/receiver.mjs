// Receive rows from Magic Scraper's "Send to webhook" and append them to
// rows.jsonl, one JSON object per line. Node 18 or later, no packages.
//
//   MS_SECRET=your-secret node receiver.mjs
//   ON_ROWS=./on-rows.sh MS_SECRET=your-secret node receiver.mjs   (optional script)
import { createServer } from 'node:http';
import { appendFileSync } from 'node:fs';
import { timingSafeEqual } from 'node:crypto';
import { spawn } from 'node:child_process';

const PORT = Number(process.env.PORT) || 8787;
const SECRET = process.env.MS_SECRET || '';  // the Secret typed in Magic Scraper, if any
const ON_ROWS = process.env.ON_ROWS || '';   // a script to run with the new rows on stdin
const FILE = process.env.MS_FILE || 'rows.jsonl';

function secretOk(got) {
  if (!SECRET) return true;
  const a = Buffer.from(String(got || '')), b = Buffer.from(SECRET);
  return a.length === b.length && timingSafeEqual(a, b);
}

createServer((req, res) => {
  if (req.method !== 'POST' || req.url !== '/hook') return res.writeHead(404).end();
  if (!secretOk(req.headers['x-magic-scraper-secret'])) return res.writeHead(401).end();
  const chunks = [];
  let size = 0;
  req.on('data', (c) => { size += c.length; if (size > 25e6) req.destroy(); else chunks.push(c); });
  req.on('end', () => {
    let msg;
    try { msg = JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { return res.writeHead(400).end(); }
    // "Batches of rows" (the default) sends an object; "One item per row" a bare list.
    const rows = Array.isArray(msg) ? msg : msg.rows || [];
    if (!Array.isArray(msg) && msg.event === 'test') {
      console.log('Test row from Magic Scraper', msg.version, '- saved settings work.');
      return res.writeHead(200, { 'content-type': 'application/json' }).end('{"ok":true}');
    }
    const lines = rows.map((r) => JSON.stringify(r)).join('\n') + '\n';
    appendFileSync(FILE, lines);
    const where = Array.isArray(msg) ? '' : ` from ${msg.page.url} (batch ${msg.batch.index}/${msg.batch.count})`;
    console.log(`${rows.length} rows${where}`);
    res.writeHead(200, { 'content-type': 'application/json' }).end(JSON.stringify({ ok: true, rows: rows.length }));
    // The rows go to the script on stdin, never on its command line: scraped
    // text is written by whoever made the page, and a shell would run it.
    if (ON_ROWS && rows.length) {
      const p = spawn(ON_ROWS, [], { stdio: ['pipe', 'inherit', 'inherit'] });
      p.on('error', (e) => console.error('ON_ROWS failed:', e.message));
      p.stdin.end(lines);
    }
  });
}).listen(PORT, () => console.log(`Waiting for Magic Scraper on http://localhost:${PORT}/hook`));

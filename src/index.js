/*
 * The site's small API: the feature request board, the home page's
 * "I'd use this" votes, and the goodbye page's one question.
 *
 * Everything that is not /api/... is served from the assets binding, so the
 * site behaves exactly as a static site does -- with one addition: an AI agent
 * that asks for a page as Markdown (Accept: text/markdown, or the address with
 * .md on the end) gets the page's content as Markdown (see src/markdown.js).
 *
 * Storage is one D1 database bound as DB. Until it is bound, every endpoint
 * answers 503 and each page falls back to an email link, so the site is never
 * broken by the database being missing. The tables are created on first use;
 * there is no migration step to remember.
 *
 * Privacy, the same rules as before: no cookies, no IP addresses stored, nothing
 * that identifies anyone. A vote is a random id the visitor's browser made up
 * for itself, which stops the honest double-click and nothing more.
 *
 * Abuse: that id is the visitor's own, so it cannot be what limits anyone --
 * a new one per request made the three-a-day cap and every other write
 * unlimited. Writes are limited instead by Cloudflare's rate limiter
 * (WRITE_LIMIT in wrangler.toml), keyed on the connecting address, which it
 * counts for a minute in memory and we never see or store; and each table has
 * a ceiling, so a flood that gets past that still cannot bury the moderation
 * queue or grow the database without end. An email
 * address is optional, never shown, and kept only to say a request shipped.
 *
 * Moderation: a new request is stored as "pending" and is not shown until it
 * is approved on /requests/admin, which needs the ADMIN_TOKEN secret.
 */

import { toMarkdown, wantsMarkdown } from './markdown.js';

const STATUSES = ['pending', 'open', 'planned', 'building', 'shipped', 'declined'];
const PUBLIC = ['open', 'planned', 'building', 'shipped', 'declined'];
const PRODUCTS = ['extension', 'desktop', 'website'];
const REASONS = new Set(['no-data', 'confusing', 'once', 'missing', 'price', 'other-tool', 'other']);
const SUBMITS_PER_DAY = 3;
const MAX_PENDING = 200;          // unmoderated requests held at once
const MAX_EMAILS = 5000;          // addresses kept for one request
const MAX_FEEDBACK_DAY = 1000;    // goodbye answers kept in one day

// The home page's roadmap list. Each item is a request with a fixed slug, so
// its "I'd use this" button and the board share one count.
const SEED = [
  ['reorder', 'Reorder columns', 'Include, exclude and rename work today; dragging columns into a new order does not.', 'open'],
  ['images', 'Download the image files, not just their URLs', 'Save the pictures themselves alongside the sheet.', 'open'],
  ['media', 'Video and media URLs', 'Only images are captured now.', 'open'],
  ['sheets', 'Send results to Google Sheets', 'Today: copy, or export a file and import it. Being looked at: one click into a new sheet, and Pro runs that add rows to the same sheet automatically.', 'open'],
  ['window', 'Keep it open beside the page', 'Shipped in 1.22.0: pin it to the side panel and it stays while you click.', 'shipped'],
];

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
const now = () => new Date().toISOString();
const clip = (v, n) => String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, n);
const clipText = (v, n) => String(v == null ? '' : v).replace(/\r\n?/g, '\n').replace(/\n{3,}/g, '\n\n').trim().slice(0, n);
const okVoter = (v) => /^[a-z0-9]{8,64}$/.test(String(v || ''));
const okEmail = (e) => /^[^@\s]{1,64}@[^@\s.]+(\.[^@\s.]+)+$/.test(e) && e.length <= 160;

let ready = null;
function schema(db) {
  if (!ready) {
    const t = now();
    ready = db.batch([
      db.prepare(`CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT UNIQUE,
        title TEXT NOT NULL, body TEXT NOT NULL DEFAULT '', product TEXT NOT NULL DEFAULT 'extension',
        status TEXT NOT NULL DEFAULT 'pending', note TEXT NOT NULL DEFAULT '',
        votes INTEGER NOT NULL DEFAULT 0, merged_into INTEGER,
        created TEXT NOT NULL, updated TEXT NOT NULL)`),
      db.prepare(`CREATE TABLE IF NOT EXISTS votes (
        request_id INTEGER NOT NULL, voter TEXT NOT NULL, at TEXT NOT NULL,
        PRIMARY KEY (request_id, voter))`),
      db.prepare(`CREATE TABLE IF NOT EXISTS emails (
        request_id INTEGER NOT NULL, email TEXT NOT NULL, at TEXT NOT NULL,
        PRIMARY KEY (request_id, email))`),
      db.prepare(`CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT, reason TEXT NOT NULL, v TEXT NOT NULL DEFAULT '',
        site TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '', at TEXT NOT NULL)`),
      db.prepare(`CREATE TABLE IF NOT EXISTS submits (
        voter TEXT NOT NULL, day TEXT NOT NULL, n INTEGER NOT NULL, PRIMARY KEY (voter, day))`),
      db.prepare(`CREATE INDEX IF NOT EXISTS requests_status ON requests (status, votes)`),
      // the goodbye answers are counted per day and blanked by age
      db.prepare(`CREATE INDEX IF NOT EXISTS feedback_at ON feedback (at)`),
      ...SEED.map(([slug, title, body, status]) => db.prepare(
        `INSERT OR IGNORE INTO requests (slug, title, body, product, status, created, updated)
         VALUES (?, ?, ?, 'extension', ?, ?, ?)`).bind(slug, title, body, status, t, t)),
    ]).catch((e) => { ready = null; throw e; });
  }
  return ready;
}

const publicRow = (r) => ({
  id: r.id, title: r.title, body: r.body, product: r.product, status: r.status,
  note: r.note, votes: r.votes, created: String(r.created).slice(0, 10), updated: String(r.updated).slice(0, 10),
});

async function vote(db, id, voter) {
  const res = await db.batch([
    db.prepare('INSERT OR IGNORE INTO votes (request_id, voter, at) VALUES (?, ?, ?)').bind(id, voter, now()),
    db.prepare('UPDATE requests SET votes = (SELECT COUNT(*) FROM votes WHERE request_id = ?) WHERE id = ?').bind(id, id),
    db.prepare('SELECT votes FROM requests WHERE id = ?').bind(id),
  ]);
  const inserted = res[0].meta.changes > 0;
  return { ok: true, already: !inserted, count: (res[2].results[0] || {}).votes || 0 };
}

async function saveEmail(db, id, email) {
  const has = await db.prepare('SELECT COUNT(*) AS n FROM emails WHERE request_id = ?').bind(id).first();
  if (has && has.n >= MAX_EMAILS) return false;
  await db.prepare('INSERT OR IGNORE INTO emails (request_id, email, at) VALUES (?, ?, ?)').bind(id, email, now()).run();
}

async function visible(db, id) {
  return db.prepare(`SELECT * FROM requests WHERE id = ? AND status IN (${PUBLIC.map(() => '?').join(',')}) AND merged_into IS NULL`)
    .bind(id, ...PUBLIC).first();
}

// ---- public: the board ----------------------------------------------------------
async function requests(request, env, parts) {
  const db = env.DB;
  if (request.method === 'GET' && parts.length === 0) {
    const url = new URL(request.url);
    const sort = url.searchParams.get('sort') === 'new' ? 'created DESC' : 'votes DESC, created DESC';
    const rows = (await db.prepare(
      `SELECT * FROM requests WHERE status IN (${PUBLIC.map(() => '?').join(',')}) AND merged_into IS NULL ORDER BY ${sort} LIMIT 300`)
      .bind(...PUBLIC).all()).results;
    return json({ requests: rows.map(publicRow) });
  }
  if (request.method !== 'POST') return json({ error: 'method not allowed' }, 405);
  let body;
  try { body = await request.json(); } catch (e) { return json({ error: 'bad json' }, 400); }

  if (parts.length === 0) {                                   // a new request
    if (body.website) return json({ ok: true, pending: true });          // honeypot: pretend, store nothing
    if (Number(body.t) > 0 && Number(body.t) < 3000) return json({ error: 'too fast' }, 429);
    const voter = String(body.voter || '');
    if (!okVoter(voter)) return json({ error: 'bad voter' }, 400);
    const title = clip(body.title, 90), text = clipText(body.body, 800);
    if (title.length < 6) return json({ error: 'Give the request a title of a few words.' }, 400);
    const product = PRODUCTS.includes(body.product) ? body.product : 'extension';
    const day = now().slice(0, 10);
    const used = await db.prepare('SELECT n FROM submits WHERE voter = ? AND day = ?').bind(voter, day).first();
    if (used && used.n >= SUBMITS_PER_DAY) return json({ error: 'That is plenty for one day, thank you. Try again tomorrow.' }, 429);
    const queued = await db.prepare(`SELECT COUNT(*) AS n FROM requests WHERE status = 'pending'`).first();
    if (queued && queued.n >= MAX_PENDING) {
      return json({ error: 'The queue is full while we catch up. Please try again in a day or two, or email us.' }, 429);
    }
    const t = now();
    const res = await db.batch([
      db.prepare(`INSERT INTO requests (title, body, product, status, created, updated) VALUES (?, ?, ?, 'pending', ?, ?)`)
        .bind(title, text, product, t, t),
      db.prepare(`INSERT INTO submits (voter, day, n) VALUES (?, ?, 1) ON CONFLICT (voter, day) DO UPDATE SET n = n + 1`).bind(voter, day),
    ]);
    const id = res[0].meta.last_row_id;
    await db.batch([
      db.prepare('INSERT OR IGNORE INTO votes (request_id, voter, at) VALUES (?, ?, ?)').bind(id, voter, t),
      db.prepare('UPDATE requests SET votes = 1 WHERE id = ?').bind(id),
    ]);
    const email = clip(body.email, 160);
    if (email && okEmail(email)) await saveEmail(db, id, email);
    return json({ ok: true, pending: true });
  }

  const id = Number(parts[0]);
  if (!Number.isInteger(id) || id < 1) return json({ error: 'unknown request' }, 404);
  const row = await visible(db, id);
  if (!row) return json({ error: 'unknown request' }, 404);
  if (parts[1] === 'vote') {
    if (!okVoter(body.voter)) return json({ error: 'bad voter' }, 400);
    if (row.status === 'shipped' || row.status === 'declined') return json({ error: 'This one is closed.' }, 409);
    return json(await vote(db, id, body.voter));
  }
  if (parts[1] === 'notify') {
    const email = clip(body.email, 160);
    if (!okEmail(email)) return json({ error: 'That email address does not look right.' }, 400);
    if (!(await saveEmail(db, id, email))) return json({ error: 'This list is full for now.' }, 429);
    return json({ ok: true });
  }
  return json({ error: 'not found' }, 404);
}

// ---- public: the home page's roadmap buttons (same counts as the board) -----------
async function roadmap(request, env) {
  const db = env.DB;
  if (request.method === 'GET') {
    const rows = (await db.prepare('SELECT slug, votes FROM requests WHERE slug IS NOT NULL').all()).results;
    const counts = {};
    rows.forEach((r) => { counts[r.slug] = r.votes; });
    return json({ counts });
  }
  if (request.method !== 'POST') return json({ error: 'method not allowed' }, 405);
  let body;
  try { body = await request.json(); } catch (e) { return json({ error: 'bad json' }, 400); }
  const row = await db.prepare('SELECT id, status, merged_into FROM requests WHERE slug = ?').bind(String(body.item || '')).first();
  if (!row || row.merged_into != null || !PUBLIC.includes(row.status)) return json({ error: 'unknown item' }, 400);
  if (!okVoter(body.voter)) return json({ error: 'bad voter' }, 400);
  // the same rule as the board: a shipped or declined item takes no votes
  if (row.status === 'shipped' || row.status === 'declined') return json({ error: 'This one is closed.' }, 409);
  const out = await vote(db, row.id, body.voter);
  const email = clip(body.email, 160);
  if (email && okEmail(email)) await saveEmail(db, row.id, email);
  return json(out);
}

// ---- public: why people removed the extension ---------------------------------------
async function feedback(request, env) {
  if (request.method !== 'POST') return json({ error: 'method not allowed' }, 405);
  let body;
  try { body = await request.json(); } catch (e) { return json({ error: 'bad json' }, 400); }
  const reason = String(body.reason || '');
  if (!REASONS.has(reason)) return json({ error: 'unknown reason' }, 400);
  const v = String(body.v || '').slice(0, 20);
  const day = now().slice(0, 10);
  const today = await env.DB.prepare('SELECT COUNT(*) AS n FROM feedback WHERE at = ?').bind(day).first();
  // Past the day's ceiling the answer is thanked and not kept: the page has
  // nothing else to say to the person leaving, and a flood stops counting.
  if (today && today.n >= MAX_FEEDBACK_DAY) return json({ ok: true });
  await env.DB.batch([
    env.DB.prepare('INSERT INTO feedback (reason, v, site, note, at) VALUES (?, ?, ?, ?, ?)')
      .bind(reason, /^\d+(\.\d+){0,3}$/.test(v) ? v : '', clip(body.site, 200), clipText(body.note, 800), day),
    // A typed answer is kept for about a year; the reason itself stays as a count.
    env.DB.prepare(`UPDATE feedback SET site = '', note = '' WHERE at < date('now', '-400 days') AND (site != '' OR note != '')`),
  ]);
  return json({ ok: true });
}

// ---- admin --------------------------------------------------------------------------
async function authorised(request, env) {
  const want = env.ADMIN_TOKEN || '';
  const got = (request.headers.get('authorization') || '').replace(/^Bearer\s+/i, '');
  if (want.length < 20 || got.length !== want.length) return false;
  const a = new TextEncoder().encode(got), b = new TextEncoder().encode(want);
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

async function admin(request, env, parts) {
  if (!env.ADMIN_TOKEN) return json({ error: 'admin is not set up: add the ADMIN_TOKEN secret' }, 503);
  if (!(await authorised(request, env))) return json({ error: 'wrong token' }, 401);
  const db = env.DB;
  const [what, idStr] = parts;

  if (what === 'requests' && request.method === 'GET') {
    const rows = (await db.prepare(
      `SELECT r.*, (SELECT COUNT(*) FROM emails e WHERE e.request_id = r.id) AS emails
       FROM requests r ORDER BY CASE r.status WHEN 'pending' THEN 0 ELSE 1 END, r.votes DESC, r.created DESC LIMIT 1000`).all()).results;
    return json({ requests: rows });
  }
  if (what === 'requests' && idStr) {
    const id = Number(idStr);
    if (request.method === 'DELETE') {
      await db.batch([
        db.prepare('DELETE FROM votes WHERE request_id = ?').bind(id),
        db.prepare('DELETE FROM emails WHERE request_id = ?').bind(id),
        db.prepare('DELETE FROM requests WHERE id = ?').bind(id),
      ]);
      return json({ ok: true });
    }
    if (request.method === 'POST') {
      let b; try { b = await request.json(); } catch (e) { return json({ error: 'bad json' }, 400); }
      const row = await db.prepare('SELECT * FROM requests WHERE id = ?').bind(id).first();
      if (!row) return json({ error: 'unknown request' }, 404);
      if (b.merge_into) {
        const into = Number(b.merge_into);
        if (!into || into === id) return json({ error: 'bad merge target' }, 400);
        await db.batch([
          db.prepare('INSERT OR IGNORE INTO votes (request_id, voter, at) SELECT ?, voter, at FROM votes WHERE request_id = ?').bind(into, id),
          db.prepare('INSERT OR IGNORE INTO emails (request_id, email, at) SELECT ?, email, at FROM emails WHERE request_id = ?').bind(into, id),
          db.prepare('UPDATE requests SET votes = (SELECT COUNT(*) FROM votes WHERE request_id = ?), updated = ? WHERE id = ?').bind(into, now(), into),
          db.prepare('UPDATE requests SET merged_into = ?, updated = ? WHERE id = ?').bind(into, now(), id),
        ]);
        return json({ ok: true });
      }
      if (b.clear_emails) {
        await db.prepare('DELETE FROM emails WHERE request_id = ?').bind(id).run();
        return json({ ok: true });
      }
      const status = STATUSES.includes(b.status) ? b.status : row.status;
      const product = PRODUCTS.includes(b.product) ? b.product : row.product;
      await db.prepare('UPDATE requests SET title = ?, body = ?, note = ?, status = ?, product = ?, updated = ? WHERE id = ?')
        .bind(b.title != null ? clip(b.title, 90) : row.title, b.body != null ? clipText(b.body, 800) : row.body,
              b.note != null ? clipText(b.note, 600) : row.note, status, product, now(), id).run();
      return json({ ok: true });
    }
  }
  if (what === 'emails' && idStr && request.method === 'GET') {
    const rows = (await db.prepare('SELECT email, at FROM emails WHERE request_id = ? ORDER BY at').bind(Number(idStr)).all()).results;
    return json({ emails: rows });
  }
  if (what === 'feedback' && request.method === 'GET') {
    const counts = (await db.prepare('SELECT reason, COUNT(*) AS n FROM feedback GROUP BY reason ORDER BY n DESC').all()).results;
    const recent = (await db.prepare(`SELECT reason, v, site, note, at FROM feedback WHERE site != '' OR note != '' ORDER BY id DESC LIMIT 200`).all()).results;
    return json({ counts, recent });
  }
  return json({ error: 'not found' }, 404);
}

// Cloudflare's rate limiter, when it is bound. The address is its key, held in
// its own counter for the period and not passed to us or stored.
async function allowed(request, env) {
  if (!env.WRITE_LIMIT) return true;
  try {
    const key = request.headers.get('cf-connecting-ip') || 'unknown';
    const { success } = await env.WRITE_LIMIT.limit({ key });
    return success;
  } catch (e) {
    return true;                   // a limiter that fails does not take the board down with it
  }
}

// Pages that are not for agents or search engines: robots.txt keeps them out,
// and they are not offered as Markdown.
const NOT_FOR_AGENTS = /^\/(admin-requests|thanks)(\.html|\.md)?$/;

// A page as Markdown, when the request asks for it. Null when it does not, or
// when there is no HTML page at that address -- the caller then serves the
// request as usual, 404 and all.
async function asMarkdown(request, env, url) {
  if (request.method !== 'GET' && request.method !== 'HEAD') return null;
  const byName = url.pathname.endsWith('.md');
  if (!byName && !wantsMarkdown(request)) return null;
  if (NOT_FOR_AGENTS.test(url.pathname)) return null;
  let target = new URL(url);
  if (byName) target.pathname = url.pathname.replace(/(\/index)?\.md$/, '') || '/';
  let res = await env.ASSETS.fetch(new Request(target, { headers: { accept: 'text/html' } }));
  // /demo -> /demo/ and the like: follow the assets' own redirect once.
  if (res.status >= 300 && res.status < 400 && res.headers.get('location')) {
    target = new URL(res.headers.get('location'), target);
    res = await env.ASSETS.fetch(new Request(target, { headers: { accept: 'text/html' } }));
  }
  if (!res.ok || !/text\/html/i.test(res.headers.get('content-type') || '')) return null;
  const md = toMarkdown(await res.text(), target.href);
  return new Response(request.method === 'HEAD' ? null : md, {
    headers: {
      'content-type': 'text/markdown; charset=utf-8',
      'vary': 'Accept',
      'x-content-type-options': 'nosniff',
      'cache-control': 'public, max-age=300',
      'link': `<${target.href}>; rel="canonical"`,
    },
  });
}

// An HTML page says where its Markdown is, and that the answer depends on
// Accept, so a cache never hands Markdown to a browser or HTML to an agent.
async function page(request, env, url) {
  const md = await asMarkdown(request, env, url);
  if (md) return md;
  const res = await env.ASSETS.fetch(request);
  if (!/text\/html/i.test(res.headers.get('content-type') || '') || NOT_FOR_AGENTS.test(url.pathname)) return res;
  const out = new Response(res.body, res);
  out.headers.append('vary', 'Accept');
  const mdPath = url.pathname.endsWith('/') ? url.pathname + 'index.md' : url.pathname.replace(/\.html$/, '') + '.md';
  out.headers.append('link', `<${mdPath}>; rel="alternate"; type="text/markdown"`);
  return out;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith('/api/')) return page(request, env, url);
    if (!env.DB) return json({ error: 'not configured' }, 503);
    try {
      await schema(env.DB);
      const parts = url.pathname.replace(/^\/api\//, '').split('/').filter(Boolean);
      if (request.method === 'POST' && parts[0] !== 'admin' && !(await allowed(request, env))) {
        return json({ error: 'That is a lot at once. Please wait a minute and try again.' }, 429);
      }
      if (parts[0] === 'requests') return await requests(request, env, parts.slice(1));
      if (parts[0] === 'roadmap') return await roadmap(request, env);
      if (parts[0] === 'feedback') return await feedback(request, env);
      if (parts[0] === 'admin') return await admin(request, env, parts.slice(1));
      return json({ error: 'not found' }, 404);
    } catch (e) {
      return json({ error: 'server error' }, 500);
    }
  },
};

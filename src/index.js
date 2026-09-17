/*
 * The roadmap's vote counter.
 *
 * The site was assets-only and is now a Worker in front of the same assets,
 * for one reason: the "What's being built" list is worthless as a planning
 * tool unless it can tell you which items people actually want. A roadmap you
 * order by guesswork is a list of your own opinions.
 *
 * Deliberately small. It counts votes and keeps optional emails for the one
 * item someone cared enough to leave an address for. It does not set cookies,
 * does not log IP addresses, and does not know who anyone is. The dedupe is a
 * random id the browser keeps for itself, which stops the honest double-click
 * and would not stop anyone determined -- and that is the right trade, because
 * a vote count is a weak signal being read as a weak signal.
 *
 * Needs one KV namespace bound as ROADMAP. Without it the API returns 503 and
 * the page falls back to a mailto link, so the site is never broken by the
 * binding being absent.
 */

const ITEMS = new Set(['reorder', 'images', 'media', 'window', 'sheets']);
const MAX_EMAIL = 160;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith('/api/roadmap')) {
      return env.ASSETS.fetch(request);
    }
    if (!env.ROADMAP) return json({ error: 'not configured' }, 503);

    if (request.method === 'GET') {
      const counts = {};
      await Promise.all([...ITEMS].map(async (k) => {
        counts[k] = Number(await env.ROADMAP.get('v:' + k)) || 0;
      }));
      return json({ counts });
    }

    if (request.method === 'POST') {
      let body;
      try { body = await request.json(); } catch (e) { return json({ error: 'bad json' }, 400); }

      const item = String(body.item || '');
      if (!ITEMS.has(item)) return json({ error: 'unknown item' }, 400);

      // One vote per browser per item. `voter` is a random id the page made up
      // for itself; it identifies nobody and is never joined to anything else.
      const voter = String(body.voter || '').slice(0, 64);
      if (!/^[a-z0-9]{8,64}$/.test(voter)) return json({ error: 'bad voter' }, 400);

      const seen = 's:' + item + ':' + voter;
      if (await env.ROADMAP.get(seen)) {
        return json({ ok: true, already: true,
                      count: Number(await env.ROADMAP.get('v:' + item)) || 0 });
      }

      const count = (Number(await env.ROADMAP.get('v:' + item)) || 0) + 1;
      await env.ROADMAP.put('v:' + item, String(count));
      await env.ROADMAP.put(seen, '1', { expirationTtl: 60 * 60 * 24 * 365 });

      // Optional, and only ever the address plus which item it was left on.
      const email = String(body.email || '').trim().slice(0, MAX_EMAIL);
      if (email && /^[^@\s]+@[^@\s.]+\.[^@\s]+$/.test(email)) {
        await env.ROADMAP.put('e:' + item + ':' + Date.now() + ':' + voter, email);
      }
      return json({ ok: true, count });
    }

    return json({ error: 'method not allowed' }, 405);
  },
};

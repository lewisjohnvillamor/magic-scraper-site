/*
 * A page of this site as Markdown, for AI agents that ask for it.
 *
 * Agents read pages to answer "how do I get this table into a spreadsheet",
 * and an HTML page spends most of its bytes on navigation, styles and markup.
 * A request with `Accept: text/markdown`, or for the page's address with .md
 * on the end, gets the page's main content as Markdown instead: headings,
 * paragraphs, links, lists, tables and the questions and answers.
 *
 * The pages are our own, written by hand or by our own scripts, so a small
 * converter that knows their shapes is enough; no library is loaded.
 */

const ENTITIES = {
  amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', mdash: '—', ndash: '–',
  rsquo: '’', lsquo: '‘', rdquo: '”', ldquo: '“', hellip: '…', middot: '·', rarr: '→',
  larr: '←', times: '×', copy: '©', trade: '™', reg: '®', bull: '•', deg: '°', euro: '€',
  pound: '£', yen: '¥', frac12: '½', frac14: '¼', frac34: '¾', minus: '−', check: '✓',
  laquo: '«', raquo: '»', lsaquo: '‹', rsaquo: '›', bdquo: '„', sbquo: '‚', dagger: '†',
  Dagger: '‡', sect: '§', para: '¶', iexcl: '¡', iquest: '¿', cent: '¢', shy: '', plusmn: '±',
  micro: 'µ', sup1: '¹', sup2: '²', sup3: '³', ordf: 'ª', ordm: 'º', szlig: 'ß', aelig: 'æ',
  AElig: 'Æ', oslash: 'ø', Oslash: 'Ø', eth: 'ð', thorn: 'þ', oelig: 'œ', OElig: 'Œ', prime: '′',
  Prime: '″', larr: '←', uarr: '↑', darr: '↓', harr: '↔', ensp: ' ', emsp: ' ', thinsp: ' ',
  zwj: '', zwnj: '', star: '☆', starf: '★',
};
// é, ä, ñ, ç and the rest: a letter and an accent, composed.
const ACCENTS = { acute: '\u0301', grave: '\u0300', circ: '\u0302', tilde: '\u0303', uml: '\u0308', ring: '\u030A', cedil: '\u0327', caron: '\u030C' };
function accented(name) {
  const m = /^([a-zA-Z])(acute|grave|circ|tilde|uml|ring|cedil|caron)$/.exec(name);
  return m ? (m[1] + ACCENTS[m[2]]).normalize('NFC') : null;
}

function decode(s) {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z0-9]+);/gi, (m, e) => {
    if (e[0] === '#') {
      const n = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      return Number.isFinite(n) ? String.fromCodePoint(n) : m;
    }
    if (Object.prototype.hasOwnProperty.call(ENTITIES, e)) return ENTITIES[e];
    if (Object.prototype.hasOwnProperty.call(ENTITIES, e.toLowerCase())) return ENTITIES[e.toLowerCase()];
    return accented(e) || m;
  });
}

const attr = (tag, name) => {
  const m = new RegExp(`\\s${name}\\s*=\\s*("([^"]*)"|'([^']*)')`, 'i').exec(tag);
  return m ? decode(m[2] !== undefined ? m[2] : m[3]) : '';
};

function absolute(href, base) {
  try { return new URL(href, base).href; } catch (e) { return href; }
}

// Inline markup inside a block: links, emphasis, code, images; tags dropped.
function inline(html, base) {
  let s = html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<img\b[^>]*>/gi, (t) => { const a = attr(t, 'alt'); return a ? `![${a}](${absolute(attr(t, 'src'), base)})` : ''; })
    .replace(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi, (m, a, text) => {
      const t = inline(text, base).trim();
      const href = attr(`<a${a}>`, 'href');
      if (!t) return '';
      if (!href || href.startsWith('#') && href.length === 1) return t;
      return `[${t}](${absolute(href, base)})`;
    })
    .replace(/<(strong|b)\b[^>]*>([\s\S]*?)<\/\1>/gi, (m, tag, t) => (t.trim() ? `**${t.trim()}**` : ''))
    .replace(/<(em|i)\b[^>]*>([\s\S]*?)<\/\1>/gi, (m, tag, t) => (t.trim() ? `*${t.trim()}*` : ''))
    .replace(/<code\b[^>]*>([\s\S]*?)<\/code>/gi, (m, t) => '`' + t.replace(/<[^>]+>/g, '') + '`')
    .replace(/<[^>]+>/g, '');
  s = decode(s).replace(/[ \t\r\f\v]+/g, ' ').replace(/ *\n */g, '\n');
  return s;
}

function table(html, base) {
  const rows = [];
  html.replace(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi, (m, tr) => {
    const cells = [];
    tr.replace(/<(t[hd])\b[^>]*>([\s\S]*?)<\/\1>/gi, (c, tag, inner) => {
      cells.push(inline(inner, base).replace(/\n+/g, ' ').replace(/\|/g, '\\|').trim());
      return c;
    });
    if (cells.length) rows.push(cells);
    return m;
  });
  if (!rows.length) return '';
  const width = Math.max(...rows.map((r) => r.length));
  const line = (r) => '| ' + Array.from({ length: width }, (_, i) => r[i] || '').join(' | ') + ' |';
  return '\n\n' + [line(rows[0]), '|' + ' --- |'.repeat(width), ...rows.slice(1).map(line)].join('\n') + '\n\n';
}

export function toMarkdown(html, url) {
  const title = decode((/<title>([\s\S]*?)<\/title>/i.exec(html) || [, ''])[1]).trim();
  const descTag = (/<meta\s+name="description"[^>]*>/i.exec(html) || [''])[0];
  const description = descTag ? attr(descTag, 'content') : '';
  const canonTag = (/<link\s+rel="canonical"[^>]*>/i.exec(html) || [''])[0];
  const canonical = canonTag ? attr(canonTag, 'href') : url;

  let body = (/<main\b[^>]*>([\s\S]*?)<\/main>/i.exec(html) || /<body\b[^>]*>([\s\S]*?)<\/body>/i.exec(html) || [, html])[1];
  body = body
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<(script|style|svg|noscript|template|button|form|iframe|nav)\b[\s\S]*?<\/\1>/gi, '')
    .replace(/<table\b[^>]*>([\s\S]*?)<\/table>/gi, (m, t) => '\u0000T' + encodeURIComponent(table(t, canonical)) + '\u0000');

  let md = body
    .replace(/<pre\b[^>]*>([\s\S]*?)<\/pre>/gi, (m, t) => '\n\n```\n' + decode(t.replace(/<[^>]+>/g, '')).trim() + '\n```\n\n')
    .replace(/<h([1-6])\b[^>]*>([\s\S]*?)<\/h\1>/gi, (m, n, t) => `\n\n${'#'.repeat(+n)} ${inline(t, canonical).replace(/\n+/g, ' ').trim()}\n\n`)
    .replace(/<summary\b[^>]*>([\s\S]*?)<\/summary>/gi, (m, t) => `\n\n### ${inline(t, canonical).replace(/\n+/g, ' ').trim()}\n\n`)
    .replace(/<li\b[^>]*>([\s\S]*?)<\/li>/gi, (m, t) => `\n- ${inline(t, canonical).replace(/\n+/g, ' ').trim()}`)
    .replace(/<(p|div|section|article|aside|details|blockquote|ul|ol|dl|dd|dt|header|footer|figure|figcaption)\b[^>]*>/gi, '\n\n')
    .replace(/<\/(p|div|section|article|aside|details|blockquote|ul|ol|dl|dd|dt|header|footer|figure|figcaption)>/gi, '\n\n');
  md = inline(md, canonical)
    .replace(/\u0000T([^\u0000]*)\u0000/g, (m, t) => decodeURIComponent(t))
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  const front = ['---', `title: ${JSON.stringify(title)}`];
  if (description) front.push(`description: ${JSON.stringify(description)}`);
  front.push(`url: ${canonical}`, '---');
  return front.join('\n') + '\n\n' + md + '\n';
}

// Whether the request asks for Markdown: an Accept header naming text/markdown
// with a weight above zero. Browsers never send it.
export function wantsMarkdown(request) {
  const accept = request.headers.get('accept') || '';
  return accept.split(',').some((part) => {
    const [type, ...params] = part.trim().split(';');
    if (type.trim().toLowerCase() !== 'text/markdown') return false;
    const q = params.map((p) => p.trim()).find((p) => p.startsWith('q='));
    return !q || parseFloat(q.slice(2)) > 0;
  });
}

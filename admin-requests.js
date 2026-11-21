/*
 * Admin for the feature request board. The token is the ADMIN_TOKEN secret set
 * on the Worker; it is kept in sessionStorage (gone when the tab closes) and
 * sent as a Bearer header. This page is never linked and is noindex; without
 * the token every call answers 401.
 *
 * Requests are a table: one line each, filtered by status, searched, sorted by
 * any column, with the status changed in place. Edit opens the full form under
 * its line -- title, details, the public reply, merging, the emails kept for
 * it, delete. The goodbye answers are a table too.
 */
(function () {
  'use strict';
  var STATUSES = ['pending', 'open', 'planned', 'building', 'shipped', 'declined'];
  var PRODUCTS = ['extension', 'desktop', 'website'];
  var msg = document.getElementById('admMsg');
  var body = document.getElementById('admBody');
  var reqBox = document.getElementById('admRequests');
  var fbBox = document.getElementById('admFeedback');
  var token = '';
  try { token = sessionStorage.getItem('ms_admin') || ''; } catch (e) {}

  // What the requests table is showing: kept across reloads after a save.
  var view = { filter: 'active', q: '', sort: 'votes', dir: -1, open: null };
  var rows = [];

  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  function say(t, err) { msg.textContent = t; msg.className = 'rq-msg' + (err ? ' err' : ''); }
  function call(method, path, data) {
    return fetch('/api/admin/' + path, {
      method: method,
      headers: { authorization: 'Bearer ' + token, 'content-type': 'application/json' },
      body: data ? JSON.stringify(data) : undefined
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) { var e = new Error(d.error || r.status); e.status = r.status; throw e; }
        return d;
      });
    });
  }
  function field(label, node, cls) { var l = el('label', cls || null, label); l.appendChild(node); return l; }
  function select(opts, val, labels) {
    var s = el('select');
    opts.forEach(function (o) { var op = el('option', null, labels ? labels[o] : o); op.value = o; if (o === val) op.selected = true; s.appendChild(op); });
    return s;
  }
  function day(s) { return String(s || '').slice(0, 10); }

  /* ---------- requests ---------- */

  var FILTERS = [
    ['active', 'Active'], ['pending', 'Waiting'], ['open', 'Open'], ['planned', 'Planned'],
    ['building', 'Building'], ['shipped', 'Shipped'], ['declined', 'Declined'], ['merged', 'Merged'], ['all', 'All']
  ];
  var COLS = [
    ['id', '#', 'num'], ['title', 'Request', ''], ['product', 'For', ''], ['status', 'Status', ''],
    ['votes', 'Votes', 'num'], ['emails', 'Emails', 'num'], ['created', 'Added', 'num']
  ];

  function shows(r) {
    var f = view.filter;
    if (f === 'merged') { if (!r.merged_into) return false; }
    else if (r.merged_into && f !== 'all') return false;
    else if (f === 'active' && (r.status === 'shipped' || r.status === 'declined')) return false;
    else if (f !== 'active' && f !== 'all' && r.status !== f) return false;
    if (!view.q) return true;
    var q = view.q.toLowerCase();
    return (r.title + ' ' + r.body + ' ' + r.note + ' ' + (r.slug || '') + ' #' + r.id).toLowerCase().indexOf(q) >= 0;
  }
  function count(f) { var keep = view.filter; view.filter = f; var q = view.q; view.q = ''; var n = rows.filter(shows).length; view.filter = keep; view.q = q; return n; }

  function sorted(list) {
    var k = view.sort, dir = view.dir;
    return list.slice().sort(function (a, b) {
      var x = a[k], y = b[k];
      if (k === 'status') { x = STATUSES.indexOf(x); y = STATUSES.indexOf(y); }
      if (typeof x === 'string') { x = x.toLowerCase(); y = String(y || '').toLowerCase(); }
      if (x < y) return -dir;
      if (x > y) return dir;
      return b.id - a.id;
    });
  }

  function renderRequests() {
    reqBox.textContent = '';
    var pending = rows.filter(function (r) { return r.status === 'pending' && !r.merged_into; }).length;

    var bar = el('div', 'adm-bar');
    var chips = el('div', 'adm-chips');
    FILTERS.forEach(function (f) {
      var n = count(f[0]);
      var b = el('button', null, f[1] + ' ' + n);
      b.type = 'button';
      b.setAttribute('aria-pressed', String(view.filter === f[0]));
      if (f[0] === 'pending' && n) b.className = 'warn';
      b.addEventListener('click', function () { view.filter = f[0]; view.open = null; renderRequests(); });
      chips.appendChild(b);
    });
    bar.appendChild(chips);
    var search = el('input');
    search.type = 'search'; search.placeholder = 'Search requests'; search.value = view.q;
    search.setAttribute('aria-label', 'Search requests');
    search.addEventListener('input', function () { view.q = search.value; drawTable(); });
    bar.appendChild(search);
    reqBox.appendChild(bar);
    reqBox.appendChild(el('p', 'rq-msg', rows.length + ' requests' + (pending ? ', ' + pending + ' waiting to be read.' : ', none waiting to be read.')));

    var scroll = el('div', 'adm-scroll');
    reqBox.appendChild(scroll);

    function drawTable() {
      scroll.textContent = '';
      var list = sorted(rows.filter(shows));
      if (!list.length) { scroll.appendChild(el('p', 'rq-msg', 'Nothing here.')); return; }
      var t = el('table', 'adm-table');
      var head = el('tr');
      COLS.forEach(function (c) {
        var th = el('th', c[2] || null);
        var b = el('button', null, c[1] + (view.sort === c[0] ? (view.dir > 0 ? ' ↑' : ' ↓') : ''));
        b.type = 'button';
        b.setAttribute('aria-label', 'Sort by ' + c[1]);
        b.addEventListener('click', function () {
          if (view.sort === c[0]) view.dir = -view.dir;
          else { view.sort = c[0]; view.dir = (c[2] === 'num') ? -1 : 1; }
          drawTable();
        });
        th.appendChild(b);
        th.setAttribute('aria-sort', view.sort === c[0] ? (view.dir > 0 ? 'ascending' : 'descending') : 'none');
        head.appendChild(th);
      });
      head.appendChild(el('th', 'act', ''));
      var thead = el('thead'); thead.appendChild(head); t.appendChild(thead);
      var tb = el('tbody');
      list.forEach(function (r) { line(r, tb); });
      t.appendChild(tb);
      scroll.appendChild(t);
    }
    drawTable();
  }

  function line(r, tb) {
    var tr = el('tr', r.status === 'pending' && !r.merged_into ? 'pending' : null);
    tr.appendChild(el('td', 'num', String(r.id)));

    var what = el('td', 'what');
    what.appendChild(el('b', null, r.title));
    var sub = r.body ? r.body : '';
    if (r.merged_into) sub = 'Merged into #' + r.merged_into + (sub ? ' · ' + sub : '');
    if (sub) what.appendChild(el('span', 'sub', sub));
    if (r.note) what.appendChild(el('span', 'reply', 'Reply: ' + r.note));
    tr.appendChild(what);

    tr.appendChild(el('td', 'muted', r.product));

    // The status changes in place and is saved at once: the commonest edit,
    // and a whole form for it was the reason the cards were slow to use.
    var stCell = el('td');
    var st = select(STATUSES, r.status);
    st.className = 'adm-st st-' + r.status;
    st.setAttribute('aria-label', 'Status of #' + r.id);
    st.addEventListener('change', function () {
      call('POST', 'requests/' + r.id, { status: st.value }).then(function () {
        say('#' + r.id + ' is ' + st.value + '.'); reload();
      }, fail);
    });
    stCell.appendChild(st);
    tr.appendChild(stCell);

    tr.appendChild(el('td', 'num', String(r.votes)));
    tr.appendChild(el('td', 'num', String(r.emails)));
    tr.appendChild(el('td', 'num muted', day(r.created)));

    var act = el('td', 'act');
    if (r.status === 'pending' && !r.merged_into) {
      var ap = el('button', 'primary', 'Approve'); ap.type = 'button';
      ap.addEventListener('click', function () { call('POST', 'requests/' + r.id, { status: 'open' }).then(done, fail); });
      act.appendChild(ap);
    }
    var ed = el('button', null, view.open === r.id ? 'Close' : 'Edit'); ed.type = 'button';
    ed.setAttribute('aria-expanded', String(view.open === r.id));
    ed.addEventListener('click', function () { view.open = view.open === r.id ? null : r.id; renderRequests(); });
    act.appendChild(ed);
    tr.appendChild(act);
    tb.appendChild(tr);

    if (view.open === r.id) tb.appendChild(editor(r));
  }

  function editor(r) {
    var tr = el('tr', 'adm-edit');
    var td = el('td'); td.colSpan = COLS.length + 1;
    var title = el('input'); title.value = r.title; title.maxLength = 90;
    var text = el('textarea'); text.value = r.body; text.maxLength = 800;
    var note = el('textarea'); note.value = r.note; note.maxLength = 600; note.placeholder = 'Public reply, shown under the request';
    var st = select(STATUSES, r.status), pr = select(PRODUCTS, r.product);
    var merge = el('input'); merge.placeholder = 'Request #'; merge.inputMode = 'numeric';

    var grid = el('div', 'adm-form');
    grid.appendChild(field('Title', title, 'wide'));
    grid.appendChild(field('Details', text, 'wide'));
    grid.appendChild(field('Reply (public)', note, 'wide'));
    grid.appendChild(field('Status', st));
    grid.appendChild(field('For', pr));
    grid.appendChild(field('Merge into', merge));
    td.appendChild(grid);

    var acts = el('div', 'acts');
    function btn(t, cls, fn) { var b = el('button', cls, t); b.type = 'button'; b.addEventListener('click', fn); acts.appendChild(b); return b; }
    btn('Save', 'primary', function () {
      call('POST', 'requests/' + r.id, { title: title.value, body: text.value, note: note.value, status: st.value, product: pr.value }).then(function () {
        view.open = null; done();
      }, fail);
    });
    btn('Merge', '', function () {
      if (!merge.value) return say('Type the number of the request to merge into.', true);
      call('POST', 'requests/' + r.id, { merge_into: Number(merge.value) }).then(function () { view.open = null; done(); }, fail);
    });
    if (r.emails) {
      btn('Copy ' + r.emails + ' email' + (r.emails === 1 ? '' : 's'), '', function () {
        call('GET', 'emails/' + r.id).then(function (d) { return navigator.clipboard.writeText(d.emails.map(function (e) { return e.email; }).join(', ')); })
          .then(function () { say('Emails copied. Send the news, then press Forget emails.'); }, fail);
      });
      btn('Forget emails', '', function () {
        if (confirm('Delete the ' + r.emails + ' addresses kept for this request?')) call('POST', 'requests/' + r.id, { clear_emails: true }).then(done, fail);
      });
    }
    btn('Delete', 'danger', function () {
      if (confirm('Delete request #' + r.id + ' and its votes?')) call('DELETE', 'requests/' + r.id).then(function () { view.open = null; done(); }, fail);
    });
    td.appendChild(acts);
    tr.appendChild(td);
    return tr;
  }

  function loadRequests() {
    return call('GET', 'requests').then(function (d) { rows = d.requests || []; renderRequests(); });
  }
  function reload() { return loadRequests().catch(fail); }

  /* ---------- goodbye answers ---------- */

  // The goodbye page's choices, as people read them.
  var REASONS = {
    'no-data': "It didn't find the data on my site",
    'confusing': "Couldn't work out how to use it",
    'once': 'Only needed it once',
    'missing': 'Missing something I needed',
    'price': "Free wasn't enough, Pro not worth it",
    'other-tool': 'Using a different tool',
    'other': 'Something else'
  };
  function reason(r) { return REASONS[r] || r; }

  // A small table: rows of cells, each [text, className].
  function table(heads, rows) {
    var w = el('div', 'adm-scroll'), t = el('table', 'adm-table');
    var h = el('tr'); heads.forEach(function (x) { h.appendChild(el('th', x[1] || null, x[0])); });
    var th = el('thead'); th.appendChild(h); t.appendChild(th);
    var tb = el('tbody');
    rows.forEach(function (r) { var tr = el('tr'); r.forEach(function (c) { tr.appendChild(el('td', c[1] || null, c[0])); }); tb.appendChild(tr); });
    t.appendChild(tb); w.appendChild(t); return w;
  }
  function loadFeedback() {
    return call('GET', 'feedback').then(function (d) {
      fbBox.textContent = '';
      var recent = d.recent || [];
      // Reports from the panel's "Tell us which site" are not reasons for
      // leaving: they get their own table and stay out of the shares.
      var reports = recent.filter(function (f) { return f.reason === 'report'; });
      var goodbyes = recent.filter(function (f) { return f.reason !== 'report'; });
      var counts = (d.counts || []).filter(function (c) { return c.reason !== 'report'; });

      fbBox.appendChild(el('h2', null, 'Sites reported from the panel'));
      fbBox.appendChild(el('p', 'rq-msg', 'Pages where Magic Scraper found nothing, sent with "Tell us which site" (2.1.2 on).'));
      if (!reports.length) fbBox.appendChild(el('p', 'rq-msg', 'No reports yet.'));
      else fbBox.appendChild(table([['Date'], ['Version'], ['Page'], ['What they wanted']], reports.map(function (f) {
        return [[day(f.at), 'muted nowrap'], [f.v ? 'v' + f.v : '', 'muted'], [f.site || '\u2014', 'what'], [f.note || '\u2014', 'what' + (f.note ? '' : ' muted')]];
      })));

      var total = counts.reduce(function (s, c) { return s + c.n; }, 0);
      fbBox.appendChild(el('h2', null, 'Why people removed it'));
      if (!total) fbBox.appendChild(el('p', 'rq-msg', 'No answers yet.'));
      else fbBox.appendChild(table([['Reason'], ['Answers', 'num'], ['Share', 'num']], counts.map(function (c) {
        return [[reason(c.reason)], [String(c.n), 'num'], [Math.round(100 * c.n / total) + '%', 'num muted']];
      })));

      fbBox.appendChild(el('h2', null, 'Every goodbye answer, newest first'));
      if (!goodbyes.length) { fbBox.appendChild(el('p', 'rq-msg', 'No answers yet.')); return; }
      var typed = goodbyes.filter(function (f) { return f.site || f.note; }).length;
      fbBox.appendChild(el('p', 'rq-msg', typed + ' of ' + goodbyes.length + ' named a site or wrote something. The site box is optional; since this version of the goodbye page, choosing "didn\u2019t find the data" asks for it.'));
      fbBox.appendChild(table([['Date'], ['Reason'], ['Version'], ['Site'], ['What they wrote']], goodbyes.map(function (f) {
        return [[day(f.at), 'muted nowrap'], [reason(f.reason)], [f.v ? 'v' + f.v : '', 'muted'],
          [f.site || '\u2014', 'what' + (f.site ? '' : ' muted')], [f.note || '\u2014', 'what' + (f.note ? '' : ' muted')]];
      })));
    });
  }

  /* ---------- unlocking ---------- */

  function done() { say('Saved.'); reload(); }
  function fail(e) {
    if (e.status === 401) {
      // The Worker also refuses every token while its own is under 20
      // characters, so a short secret can never unlock, typed right or not.
      var short = token.length < 20;
      token = ''; try { sessionStorage.removeItem('ms_admin'); } catch (x) {}
      body.hidden = true;
      return say(short
        ? 'Wrong token. The admin token is at least 20 characters: set a longer ADMIN_TOKEN on the Worker (Settings, Runtime variables and secrets) and paste that here.'
        : 'Wrong token. Paste the ADMIN_TOKEN secret exactly, with no space or line break at the end.', true);
    }
    if (e.status === 503) return say('Admin is not set up yet: add an ADMIN_TOKEN secret on the Worker (Settings, Runtime variables and secrets).', true);
    say(e.message || 'Something went wrong.', true);
  }
  function open() {
    say('Loading…');
    loadRequests().then(function () { body.hidden = false; say(''); return loadFeedback(); }).catch(fail);
  }

  document.getElementById('admAuth').addEventListener('submit', function (ev) {
    ev.preventDefault();
    token = document.getElementById('admToken').value.trim();
    try { sessionStorage.setItem('ms_admin', token); } catch (e) {}
    open();
  });
  document.querySelector('.adm-tabs').addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-tab]'); if (!b) return;
    document.querySelectorAll('.adm-tabs button').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
    reqBox.hidden = b.getAttribute('data-tab') !== 'requests';
    fbBox.hidden = b.getAttribute('data-tab') !== 'feedback';
  });
  if (token) open();
})();

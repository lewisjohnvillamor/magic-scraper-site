/*
 * Admin for the feature request board. The token is the ADMIN_TOKEN secret set
 * on the Worker; it is kept in sessionStorage (gone when the tab closes) and
 * sent as a Bearer header. This page is never linked and is noindex; without
 * the token every call answers 401.
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

  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  function say(t, err) { msg.textContent = t; msg.className = 'rq-msg' + (err ? ' err' : ''); }
  function call(method, path, data) {
    return fetch('/api/admin/' + path, {
      method: method,
      headers: { authorization: 'Bearer ' + token, 'content-type': 'application/json' },
      body: data ? JSON.stringify(data) : undefined
    }).then(function (r) { return r.json().catch(function () { return {}; }).then(function (d) { if (!r.ok) { var e = new Error(d.error || r.status); e.status = r.status; throw e; } return d; }); });
  }
  function field(label, node) { var l = el('label', null, label); l.appendChild(node); return l; }
  function select(opts, val) { var s = el('select'); opts.forEach(function (o) { var op = el('option', null, o); op.value = o; if (o === val) op.selected = true; s.appendChild(op); }); return s; }

  function loadRequests() {
    return call('GET', 'requests').then(function (d) {
      reqBox.textContent = '';
      var pending = d.requests.filter(function (r) { return r.status === 'pending' && !r.merged_into; }).length;
      reqBox.appendChild(el('p', 'rq-msg', d.requests.length + ' requests, ' + pending + ' waiting to be read.'));
      d.requests.forEach(function (r) {
        var box = el('div', 'adm-row' + (r.status === 'pending' ? ' pending' : ''));
        box.appendChild(el('div', 'meta', '#' + r.id + (r.slug ? ' (' + r.slug + ')' : '') + ' · ' + r.votes + ' votes · ' + r.emails + ' emails · ' + String(r.created).slice(0, 10) + (r.merged_into ? ' · merged into #' + r.merged_into : '')));
        var title = el('input'); title.value = r.title;
        var text = el('textarea'); text.value = r.body;
        var note = el('textarea'); note.value = r.note; note.placeholder = 'Public reply, shown under the request';
        var st = select(STATUSES, r.status), pr = select(PRODUCTS, r.product);
        var grid = el('div', 'grid');
        grid.appendChild(field('Status', st)); grid.appendChild(field('For', pr));
        var merge = el('input'); merge.placeholder = 'id'; merge.inputMode = 'numeric';
        grid.appendChild(field('Merge into request #', merge));
        box.appendChild(field('Title', title)); box.appendChild(field('Details', text)); box.appendChild(field('Reply', note)); box.appendChild(grid);
        var acts = el('div', 'acts');
        function btn(t, cls, fn) { var b = el('button', cls, t); b.type = 'button'; b.addEventListener('click', fn); acts.appendChild(b); return b; }
        if (r.status === 'pending') btn('Approve', 'primary', function () { save({ status: 'open' }); });
        btn('Save', r.status === 'pending' ? '' : 'primary', function () { save({}); });
        btn('Merge', '', function () { if (!merge.value) return say('Type the id to merge into.', true); call('POST', 'requests/' + r.id, { merge_into: Number(merge.value) }).then(done, fail); });
        if (r.emails) {
          btn('Copy ' + r.emails + ' emails', '', function () {
            call('GET', 'emails/' + r.id).then(function (d) { return navigator.clipboard.writeText(d.emails.map(function (e) { return e.email; }).join(', ')); })
              .then(function () { say('Emails copied. Send the news, then press Forget emails.'); }, fail);
          });
          btn('Forget emails', '', function () { if (confirm('Delete the ' + r.emails + ' addresses kept for this request?')) call('POST', 'requests/' + r.id, { clear_emails: true }).then(done, fail); });
        }
        btn('Delete', 'danger', function () { if (confirm('Delete request #' + r.id + ' and its votes?')) call('DELETE', 'requests/' + r.id).then(done, fail); });
        function save(extra) {
          var d = { title: title.value, body: text.value, note: note.value, status: st.value, product: pr.value };
          Object.keys(extra).forEach(function (k) { d[k] = extra[k]; });
          call('POST', 'requests/' + r.id, d).then(done, fail);
        }
        box.appendChild(acts);
        reqBox.appendChild(box);
      });
    });
  }
  function loadFeedback() {
    return call('GET', 'feedback').then(function (d) {
      fbBox.textContent = '';
      var t = el('table', 'compare');
      var tb = el('tbody');
      d.counts.forEach(function (c) { var tr = el('tr'); tr.appendChild(el('td', null, c.reason)); tr.appendChild(el('td', null, String(c.n))); tb.appendChild(tr); });
      t.appendChild(tb); fbBox.appendChild(el('h2', null, 'Why people removed it')); fbBox.appendChild(t);
      fbBox.appendChild(el('h2', null, 'What they wrote'));
      if (!d.recent.length) fbBox.appendChild(el('p', 'rq-msg', 'No typed answers yet.'));
      d.recent.forEach(function (f) {
        var box = el('div', 'adm-row');
        box.appendChild(el('div', 'meta', f.at + ' · ' + f.reason + (f.v ? ' · v' + f.v : '')));
        if (f.site) box.appendChild(el('p', null, 'Site: ' + f.site));
        if (f.note) box.appendChild(el('p', null, f.note));
        fbBox.appendChild(box);
      });
    });
  }
  function done() { say('Saved.'); loadRequests().catch(fail); }
  function fail(e) {
    if (e.status === 401) { token = ''; try { sessionStorage.removeItem('ms_admin'); } catch (x) {} body.hidden = true; }
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

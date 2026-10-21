/*
 * The feature request board. Lists requests from /api/requests, votes, and
 * sends new ones. Everything typed by visitors is shown with textContent, never
 * as HTML. If the API is not set up yet (503) or fails, the board says so and
 * the form turns into a prefilled email, so a request is never simply lost.
 */
(function () {
  'use strict';
  var API = '/api/requests';
  var MAIL = 'support@magicscraper.app';
  var STATUS = { open: 'Open', planned: 'Planned', building: 'Building', shipped: 'Shipped', declined: 'Declined' };
  var PRODUCT = { extension: 'Extension', desktop: 'Desktop', website: 'Website' };
  var list = document.getElementById('rqList');
  var load = document.getElementById('rqLoad');
  var tools = document.getElementById('rqTools');
  var form = document.getElementById('rqForm');
  var formMsg = document.getElementById('rqFormMsg');
  var opened = Date.now();
  var sort = 'top', filter = 'active', all = [], offline = false;

  // The same random id the home page's roadmap uses. It identifies nobody.
  var voter = '';
  try {
    voter = localStorage.getItem('ms_voter') || '';
    if (!/^[a-z0-9]{8,64}$/.test(voter)) {
      voter = Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
      localStorage.setItem('ms_voter', voter);
    }
  } catch (e) { voter = Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2); }
  var voted = {};
  try { voted = JSON.parse(localStorage.getItem('ms_voted') || '{}') || {}; } catch (e) {}
  function remember(id) { voted[id] = 1; try { localStorage.setItem('ms_voted', JSON.stringify(voted)); } catch (e) {} }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function post(url, body) {
    return fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (d) { if (!r.ok) { var e = new Error(d.error || r.status); e.status = r.status; throw e; } return d; }); });
  }

  function render() {
    list.textContent = '';
    var rows = all.filter(function (r) {
      if (filter === 'all') return true;
      if (filter === 'active') return r.status === 'open' || r.status === 'planned' || r.status === 'building';
      return r.status === filter;
    });
    if (sort === 'new') rows.sort(function (a, b) { return a.created < b.created ? 1 : a.created > b.created ? -1 : b.id - a.id; });
    else rows.sort(function (a, b) { return b.votes - a.votes || (a.created < b.created ? 1 : -1); });
    if (!rows.length) { list.appendChild(el('li', 'rq-empty', 'Nothing here yet. Be the first to ask, below.')); return; }
    rows.forEach(function (r) {
      var li = el('li', 'rq');
      var closed = r.status === 'shipped' || r.status === 'declined';
      var btn = el('button', 'rq-up');
      btn.type = 'button';
      btn.setAttribute('aria-pressed', voted[r.id] ? 'true' : 'false');
      btn.setAttribute('aria-label', (voted[r.id] ? 'You voted for: ' : 'Vote for: ') + r.title + ', ' + r.votes + (r.votes === 1 ? ' vote' : ' votes'));
      btn.appendChild(el('span', 'arr', '▲'));
      var n = el('span', 'n', String(r.votes));
      btn.appendChild(n);
      if (closed || voted[r.id]) btn.disabled = true;
      btn.addEventListener('click', function () { vote(r, btn, n, li); });
      var main = el('div');
      main.appendChild(el('h3', null, r.title));
      if (r.body) main.appendChild(el('p', null, r.body));
      var meta = el('div', 'meta');
      meta.appendChild(el('span', 'st ' + r.status, STATUS[r.status] || r.status));
      meta.appendChild(document.createTextNode(' · ' + (PRODUCT[r.product] || '') + ' · ' + r.created));
      main.appendChild(meta);
      if (r.note) {
        var note = el('div', 'note');
        note.appendChild(el('b', null, 'From us: '));
        note.appendChild(document.createTextNode(r.note));
        main.appendChild(note);
      }
      li.appendChild(btn); li.appendChild(main);
      list.appendChild(li);
    });
  }

  function vote(r, btn, n, li) {
    btn.disabled = true;
    post(API + '/' + r.id + '/vote', { voter: voter }).then(function (d) {
      r.votes = d.count; n.textContent = String(d.count);
      remember(r.id);
      btn.setAttribute('aria-pressed', 'true');
      btn.setAttribute('aria-label', 'You voted for: ' + r.title + ', ' + d.count + (d.count === 1 ? ' vote' : ' votes'));
      if (!d.already) askEmail(r, li.lastChild);
    }, function () { btn.disabled = false; });
  }

  // Asked once, after a vote, never required: the vote already counted.
  function askEmail(r, into) {
    if (into.querySelector('.votemail')) return;
    var f = el('form', 'votemail');
    var lab = el('label', null, 'Want telling when it ships? ');
    lab.appendChild(el('span', null, 'Optional.'));
    var inp = el('input'); inp.type = 'email'; inp.placeholder = 'you@work.com'; inp.autocomplete = 'email';
    lab.appendChild(inp);
    var go = el('button', null, 'Tell me'); go.type = 'submit';
    f.appendChild(lab); f.appendChild(go);
    into.appendChild(f);
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var v = inp.value.trim();
      if (!v) { f.remove(); return; }
      post(API + '/' + r.id + '/notify', { email: v }).then(function () {
        f.textContent = ''; f.appendChild(el('p', 'ok', 'Noted. We’ll tell you when it ships.'));
      }, function (e) {
        var m = f.querySelector('.ok') || el('p', 'ok'); m.textContent = e.message || 'Could not save that.'; f.appendChild(m);
      });
    });
  }

  function mailto(title, body) {
    return 'mailto:' + MAIL + '?subject=' + encodeURIComponent('Feature request: ' + (title || '')) +
      '&body=' + encodeURIComponent(body || '');
  }

  function goOffline() {
    offline = true;
    load.textContent = 'The request board is not switched on yet. You can still ask by email, and the form below will write it for you.';
    form.querySelector('button[type=submit]').textContent = 'Write it as an email';
  }

  tools.addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-sort]');
    if (!b) return;
    sort = b.getAttribute('data-sort');
    tools.querySelectorAll('button[data-sort]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
    render();
  });
  document.getElementById('rqStatus').addEventListener('change', function (ev) { filter = ev.target.value; render(); });

  fetch(API, { headers: { accept: 'application/json' } })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (d) {
      all = d.requests || [];
      load.textContent = all.length ? '' : '';
      load.hidden = true;
      tools.hidden = false;
      render();
    })
    .catch(goOffline);

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    formMsg.className = 'rq-msg';
    var title = form.title.value.trim(), body = form.body.value.trim();
    if (title.length < 6) { formMsg.className = 'rq-msg err'; formMsg.textContent = 'Give the request a title of a few words.'; form.title.focus(); return; }
    if (offline) { location.href = mailto(title, body + '\n\nFor: ' + form.product.value); return; }
    var btn = form.querySelector('button[type=submit]');
    btn.disabled = true;
    post(API, {
      title: title, body: body, product: form.product.value, email: form.email.value.trim(),
      website: form.website.value, voter: voter, t: Date.now() - opened
    }).then(function () {
      form.reset();
      formMsg.textContent = 'Thanks. It will appear here once it has been read, usually within a couple of days.';
      btn.disabled = false;
    }, function (e) {
      btn.disabled = false;
      formMsg.className = 'rq-msg err';
      if (e.status === 503 || !e.status) {
        formMsg.textContent = 'That could not be saved just now. ';
        var a = el('a', null, 'Send it as an email instead'); a.href = mailto(title, body);
        formMsg.appendChild(a);
      } else formMsg.textContent = e.message;
    });
  });
})();

/*
 * "I'd use this" on the roadmap.
 *
 * Progressive enhancement in the strict sense: the list is complete and
 * readable with this file absent, blocked or broken. Everything below only
 * adds to it, and if the API is not there yet -- the KV namespace is one
 * manual step -- each button quietly becomes a mailto instead, so the page
 * never presents a control that does nothing.
 */
(function () {
  'use strict';
  var API = '/api/roadmap';
  var MAIL = 'support@magicscraper.app';
  var list = document.querySelector('#next .dots');
  if (!list) return;

  // A random id this browser keeps for itself. It stops the honest
  // double-click and identifies nobody; there is no cookie and nothing is
  // joined to it server-side.
  var voter = '';
  try {
    voter = localStorage.getItem('ms_voter') || '';
    if (!/^[a-z0-9]{8,64}$/.test(voter)) {
      voter = Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
      localStorage.setItem('ms_voter', voter);
    }
  } catch (e) { voter = ''; }          // private window: vote, just do not remember

  var items = [].slice.call(list.querySelectorAll('[data-item]'));
  if (!items.length) return;

  function mailtoFor(li) {
    var what = (li.querySelector('b') || {}).textContent || li.getAttribute('data-item');
    return 'mailto:' + MAIL +
      '?subject=' + encodeURIComponent('I would use: ' + what) +
      '&body=' + encodeURIComponent('I would use "' + what + '" because:\n\n');
  }

  items.forEach(function (li) {
    var row = document.createElement('div');
    row.className = 'voterow';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'vote';
    btn.textContent = "I'd use this";
    var count = document.createElement('span');
    count.className = 'votecount';
    row.appendChild(btn);
    row.appendChild(count);
    li.appendChild(row);
    li._btn = btn; li._count = count;
  });

  function show(el, n) {
    el.textContent = n > 0 ? (n === 1 ? '1 person' : n + ' people') : '';
  }

  function degrade() {
    // No API yet. Turn each button into the thing that always works, and say
    // so rather than leaving a button that silently fails.
    items.forEach(function (li) {
      var a = document.createElement('a');
      a.className = 'vote';
      a.href = mailtoFor(li);
      a.textContent = "I'd use this";
      li._btn.parentNode.replaceChild(a, li._btn);
    });
    var note = document.getElementById('voteNote');
    if (note) note.innerHTML =
      'Press <b>I’d use this</b> on anything you want &mdash; it opens an email, ' +
      'and that is how the list gets ordered. ' +
      '<a href="/support">Something missing? Say so.</a>';
  }

  fetch(API, { headers: { accept: 'application/json' } })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (d) {
      items.forEach(function (li) {
        show(li._count, (d.counts || {})[li.getAttribute('data-item')] || 0);
      });
    })
    .catch(degrade);

  list.addEventListener('click', function (ev) {
    var btn = ev.target.closest('button.vote');
    if (!btn) return;
    var li = btn.closest('[data-item]');
    if (!li || btn.disabled) return;
    btn.disabled = true;
    btn.textContent = 'Thanks';

    fetch(API, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ item: li.getAttribute('data-item'), voter: voter })
    })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
      .then(function (d) {
        show(li._count, d.count || 0);
        if (d.already) { btn.textContent = 'Counted'; return; }
        askEmail(li);
      })
      .catch(function () {
        // The vote did not land, so do not pretend it did.
        btn.disabled = false;
        btn.textContent = "I'd use this";
        var a = document.createElement('a');
        a.className = 'vote'; a.href = mailtoFor(li); a.textContent = 'Email instead';
        btn.parentNode.appendChild(a);
      });
  });

  // Asked once, after the vote, and never required. The vote is already
  // counted by this point, so closing it costs nothing.
  function askEmail(li) {
    if (li.querySelector('.votemail')) return;
    var wrap = document.createElement('form');
    wrap.className = 'votemail';
    wrap.innerHTML =
      '<label>Want telling when it ships? <span>Optional.</span>' +
      '<input type="email" placeholder="you@work.com" autocomplete="email" /></label>' +
      '<button type="submit">Tell me</button>';
    li.appendChild(wrap);
    wrap.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var email = wrap.querySelector('input').value.trim();
      if (!email) { wrap.remove(); return; }
      fetch(API, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ item: li.getAttribute('data-item'), voter: voter, email: email })
      }).then(function () {
        wrap.innerHTML = '<p class="ok">Noted &mdash; we’ll tell you.</p>';
      }, function () {
        wrap.innerHTML = '<p class="ok">Could not save that. ' +
          '<a href="' + mailtoFor(li) + '">Email instead?</a></p>';
      });
    });
  }
})();

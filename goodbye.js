/* The goodbye page's one form. Posts to /api/feedback; if that is not set up
 * yet (503) or fails, it hands the same answer over as a prefilled email
 * instead, so an answer is never simply lost. */
(function () {
  var form = document.getElementById('gb');
  if (!form) return;
  var v = (new URLSearchParams(location.search).get('v') || '').slice(0, 20);
  var LABELS = {};
  Array.prototype.forEach.call(form.querySelectorAll('input[name=reason]'), function (r) {
    LABELS[r.value] = r.parentNode.textContent.trim();
  });

  // "It didn't find the data on my site" is the answer that can be fixed,
  // and only with the site: two people picked it and left the box empty. So
  // picking it asks for the address, there and then.
  var siteLabel = form.site.closest('label');
  var siteAsk = siteLabel.firstChild.nodeValue;
  var optional = siteLabel.querySelector('span');
  // Asking was not enough (a "no data" answer still came without a site), so
  // Send asks once more, in words, and the second press sends regardless.
  var nudge = document.createElement('p');
  nudge.id = 'gbNudge'; nudge.hidden = true; nudge.setAttribute('role', 'status');
  siteLabel.parentNode.insertBefore(nudge, siteLabel.nextSibling);
  var nudged = false;
  // "Something else" and "I couldn't work out how to use it" came back with
  // nothing written, twice each: the answers that most need a sentence. Picking
  // either asks its own question in the note box, and Send asks once more.
  var NOTE_ASK = {
    other: 'What happened? One sentence is plenty. ',
    confusing: 'What were you trying to do, and where did you get stuck? '
  };
  var noteLabel = form.note.closest('label');
  var noteAsk = noteLabel.firstChild.nodeValue;
  var noteOptional = noteLabel.querySelector('span');
  var noteNudge = document.createElement('p');
  noteNudge.id = 'gbNoteNudge'; noteNudge.className = 'gb-nudge'; noteNudge.hidden = true; noteNudge.setAttribute('role', 'status');
  noteLabel.parentNode.insertBefore(noteNudge, noteLabel.nextSibling);
  var noteNudged = false;
  Array.prototype.forEach.call(form.querySelectorAll('input[name=reason]'), function (r) {
    r.addEventListener('change', function () {
      var ask = r.checked && NOTE_ASK[r.value];
      noteLabel.classList.toggle('ask', !!ask);
      if (noteOptional) noteOptional.hidden = !!ask;
      if (!ask) noteNudge.hidden = true;
      noteLabel.firstChild.nodeValue = ask || noteAsk;
      if (ask) { form.note.focus({ preventScroll: true }); noteLabel.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
    });
  });
  Array.prototype.forEach.call(form.querySelectorAll('input[name=reason]'), function (r) {
    r.addEventListener('change', function () {
      var need = r.checked && (r.value === 'no-data' || r.value === 'missing');
      siteLabel.classList.toggle('ask', need);
      if (optional) optional.hidden = need;
      if (!need) nudge.hidden = true;
      siteLabel.firstChild.nodeValue = need
        ? (r.value === 'no-data' ? 'Which site was it? Paste the address: it is what gets it fixed. '
                                  : 'On which site did you need it? ')
        : siteAsk;
      if (need) { form.site.placeholder = 'e.g. https://www.example.com/directory'; form.site.focus({ preventScroll: true }); siteLabel.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
      else form.site.placeholder = 'e.g. a directory, a shop, a search page';
    });
  });

  function done() { form.hidden = true; document.getElementById('gbDone').hidden = false; }

  function fallback(body) {
    var text = 'Why I removed Magic Scraper' + (body.v ? ' ' + body.v : '') + ':\n\n' +
      (LABELS[body.reason] || body.reason || '') +
      (body.site ? '\nSite: ' + body.site : '') + (body.note ? '\n\n' + body.note : '');
    var a = 'mailto:support@magicscraper.app?subject=' + encodeURIComponent('Why I removed Magic Scraper') +
      '&body=' + encodeURIComponent(text);
    var p = document.getElementById('gbFallback');
    p.innerHTML = 'That could not be saved just now. <a href="' + a + '">Send it as an email instead</a> ' +
      '&mdash; it is already written.';
    p.hidden = false;
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var picked = form.querySelector('input[name=reason]:checked');
    var body = {
      reason: picked ? picked.value : '',
      site: form.site.value.trim().slice(0, 200),
      note: form.note.value.trim().slice(0, 800),
      v: v
    };
    if (!body.reason && !body.site && !body.note) { form.querySelector('input[name=reason]').focus(); return; }
    if (!body.reason) body.reason = 'other';
    if (body.reason === 'no-data' && !body.site && !nudged) {
      nudged = true;
      nudge.textContent = 'Even just the site\'s name helps us fix it \u2014 or press Send again to skip.';
      nudge.hidden = false;
      form.site.focus();
      return;
    }
    if (NOTE_ASK[body.reason] && !body.note && !noteNudged) {
      noteNudged = true;
      noteNudge.textContent = 'Even a few words help us fix it \u2014 or press Send again to skip.';
      noteNudge.hidden = false;
      form.note.focus();
      return;
    }
    var btn = document.getElementById('gbSend');
    btn.disabled = true;
    fetch('/api/feedback', {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body)
    }).then(function (r) { if (!r.ok) throw new Error(r.status); done(); })
      .catch(function () { btn.disabled = false; fallback(body); });
  });
})();

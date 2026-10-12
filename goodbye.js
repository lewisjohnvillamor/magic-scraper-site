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
    var btn = document.getElementById('gbSend');
    btn.disabled = true;
    fetch('/api/feedback', {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body)
    }).then(function (r) { if (!r.ok) throw new Error(r.status); done(); })
      .catch(function () { btn.disabled = false; fallback(body); });
  });
})();

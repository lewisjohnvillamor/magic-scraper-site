/* /report: "Tell us which site" from the extension's panel, when it found
 * nothing on a page. The extension puts the page's address after the # --
 * report#u=<address>&v=<version> -- so it never reaches the server on its own:
 * a browser does not send what follows #. It is shown in an editable box and
 * sent only when Send is pressed. If saving fails, the same report is handed
 * over as a prefilled email, as the goodbye page does. */
(function () {
  var form = document.getElementById('rp');
  if (!form) return;
  var frag = new URLSearchParams(location.hash.replace(/^#/, ''));
  var u = (frag.get('u') || '').slice(0, 200);
  var v = (frag.get('v') || '').slice(0, 20);
  if (u) { form.site.value = u; document.getElementById('rpHint').hidden = false; }
  // Out of the address bar too, so a copied link or a screenshot does not
  // carry it further.
  try { history.replaceState(null, '', location.pathname); } catch (e) {}
  (u ? form.note : form.site).focus({ preventScroll: true });

  function fallback(body) {
    var text = 'A page Magic Scraper found nothing on' + (body.v ? ' (' + body.v + ')' : '') + ':\n\n' +
      body.site + (body.note ? '\n\n' + body.note : '');
    var a = 'mailto:support@magicscraper.app?subject=' + encodeURIComponent('A page Magic Scraper could not read') +
      '&body=' + encodeURIComponent(text);
    var p = document.getElementById('rpFallback');
    p.innerHTML = 'That could not be saved just now. <a href="' + a + '">Send it as an email instead</a> ' +
      '&mdash; it is already written.';
    p.hidden = false;
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var body = { reason: 'report', site: form.site.value.trim().slice(0, 200), note: form.note.value.trim().slice(0, 800), v: v };
    if (!body.site) { form.site.focus(); return; }
    var btn = document.getElementById('rpSend');
    btn.disabled = true;
    fetch('/api/feedback', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); form.hidden = true; document.getElementById('rpDone').hidden = false; })
      .catch(function () { btn.disabled = false; fallback(body); });
  });
})();

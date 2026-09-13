/* The masthead nav collapses behind a burger below 820px.
   Progressive enhancement: the .js class is set inline in <head>, so a page
   that never runs this file keeps a plain visible nav that wraps, rather than
   a hidden nav behind a button that does nothing. */
(function () {
  var mast = document.querySelector('.masthead');
  if (!mast) return;
  var btn = mast.querySelector('.burger');
  var nav = mast.querySelector('nav');
  if (!btn || !nav) return;

  function set(open) {
    mast.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    set(btn.getAttribute('aria-expanded') !== 'true');
  });

  /* In-page anchors (#price, #what) do not navigate, so the panel has to be
     told to close or it stays open over the section you just jumped to. */
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) set(false);
  });

  document.addEventListener('click', function (e) {
    if (!mast.contains(e.target)) set(false);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') set(false);
  });
})();

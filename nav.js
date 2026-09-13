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

/* The hero video: 3.9MB that used to autoplay on every load, including a
   phone on cellular, with no way to stop it. It now starts paused behind a
   poster and downloads nothing until someone asks for it, or until we decide
   the visitor is on a wide screen, has not asked for reduced motion, and is
   not on a metered or slow connection. The toggle is always present either
   way -- WCAG 2.2.2 wants a way to pause anything that moves for more than
   five seconds. */
(function () {
  var v = document.getElementById('promo');
  var btn = document.querySelector('.vtoggle');
  if (!v || !btn) return;

  var PLAY = 'Play the 30-second demo';
  var PAUSE = 'Pause the demo';

  function label() {
    var playing = !v.paused && !v.ended;
    btn.textContent = playing ? PAUSE : PLAY;
    btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
    document.querySelector('.stage').classList.toggle('playing', playing);
  }

  btn.addEventListener('click', function () {
    if (v.paused) { v.play().catch(function () {}); } else { v.pause(); }
  });
  v.addEventListener('play', label);
  v.addEventListener('pause', label);

  function mq(q) { return window.matchMedia && window.matchMedia(q).matches; }
  var conn = navigator.connection || {};
  var cheap = !conn.saveData && !/2g/.test(conn.effectiveType || '');

  if (mq('(min-width: 821px)') && !mq('(prefers-reduced-motion: reduce)') && cheap) {
    v.autoplay = true;
    v.play().catch(function () {});   /* a refused autoplay just leaves the poster */
  }
  label();
})();

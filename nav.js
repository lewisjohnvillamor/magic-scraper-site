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

  var PLAY = 'Play the 36-second demo';
  var PAUSE = 'Pause the demo';

  function label() {
    var playing = !v.paused && !v.ended;
    btn.textContent = playing ? PAUSE : PLAY;
    btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
    document.querySelector('.stage').classList.toggle('playing', playing);
  }

  /* Some browsers cannot decode H.264 -- Firefox without the OpenH264 plugin,
     and Chromium builds compiled without proprietary codecs. There the poster
     stays up and the button does nothing at all when pressed, which is the one
     thing the rest of this page is careful never to do. Say so, and hand over
     the file instead. */
  function noCodec() {
    if (!btn.parentNode) return;
    var a = document.createElement('a');
    a.className = 'vtoggle';
    a.href = v.currentSrc || v.getAttribute('src');
    a.setAttribute('download', '');
    a.textContent = 'Download the demo (36s)';
    btn.parentNode.replaceChild(a, btn);
    var cap = document.querySelector('.caption span');
    if (cap) {
      var note = document.createElement('b');
      note.className = 'warn';
      note.textContent = 'This browser cannot play H.264 video. ';
      cap.insertBefore(note, cap.firstChild);
    }
  }

  // An autoplay a browser refuses is NotAllowedError and is fine -- the poster
  // is the fallback. A codec it cannot decode is NotSupportedError, or leaves
  // v.error set, and is not fine.
  function refused(e) {
    if (v.error || (e && e.name === 'NotSupportedError')) noCodec();
  }

  btn.addEventListener('click', function () {
    if (v.paused) { v.play().catch(refused); } else { v.pause(); }
  });
  v.addEventListener('play', label);
  v.addEventListener('pause', label);
  v.addEventListener('error', noCodec);

  function mq(q) { return window.matchMedia && window.matchMedia(q).matches; }
  var conn = navigator.connection || {};
  var cheap = !conn.saveData && !/2g/.test(conn.effectiveType || '');

  if (mq('(min-width: 821px)') && !mq('(prefers-reduced-motion: reduce)') && cheap) {
    v.autoplay = true;
    v.play().catch(refused);   /* a refused autoplay just leaves the poster */
  }
  label();
})();

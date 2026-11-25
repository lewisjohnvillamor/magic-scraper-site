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
    // Read the length off the caption rather than repeating it: a literal here
    // went on saying 36s after the cut grew to 46, in the one place a visitor
    // who cannot play the video is looking.
    var len = (document.querySelector('.caption b') || {}).textContent || '';
    a.textContent = 'Download the demo' + (/^\d?\d:\d\d$/.test(len.trim())
      ? ' (' + String(Number(len.trim().split(':')[1])) + 's)' : '');
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

/* Black Friday, 2026: Magic Scraper Pro for $5 with the code BLACKFRIDAY,
   Friday 27 November only, then back to the $19 founding price. A strip
   above the masthead on every page, by the visitor's own calendar: "this
   Friday" before it, "today only" on the day, and nothing from Saturday on,
   so it needs no second deploy to take down. Closing it hides it for the
   rest of the visit. Nothing is stored beyond this tab, nothing is sent. */
(function () {
  var now = new Date(), y = now.getFullYear(), m = now.getMonth(), d = now.getDate();
  if (y !== 2026 || m !== 10 || d < 20 || d > 27) return;   // 20-27 November 2026, local time
  try { if (sessionStorage.getItem('mds_bf_closed')) return; } catch (e) {}
  var today = d === 27;
  var bar = document.createElement('div');
  bar.className = 'bf-bar';
  bar.setAttribute('role', 'region');
  bar.setAttribute('aria-label', 'Black Friday offer');
  var text = document.createElement('p');
  var tag = document.createElement('b');
  tag.textContent = today ? 'Today only' : 'Black Friday';
  text.appendChild(tag);
  text.appendChild(document.createTextNode(today
    ? ': Magic Scraper Pro for $5 (normally $19) with the code BLACKFRIDAY. One time only.'
    : ': Magic Scraper Pro for $5 (normally $19), this Friday, 27 November only. Code BLACKFRIDAY.'));
  var go = document.createElement('a');
  go.href = today ? 'https://magicscraper.gumroad.com/l/magicscraper/BLACKFRIDAY' : '/#price';
  go.textContent = today ? 'Get Pro for $5' : 'See Pro';
  var close = document.createElement('button');
  close.type = 'button';
  close.className = 'bf-close';
  close.setAttribute('aria-label', 'Close the Black Friday notice');
  close.textContent = '×';
  close.addEventListener('click', function () {
    bar.remove();
    try { sessionStorage.setItem('mds_bf_closed', '1'); } catch (e) {}
  });
  bar.appendChild(text); bar.appendChild(go); bar.appendChild(close);
  var skip = document.querySelector('.skip');
  if (skip && skip.parentNode === document.body) skip.after(bar); else document.body.prepend(bar);
})();

/* Pricing icons (see style.css): a staggered jiggle the first time the plans
   come into view, and a soft tap when a line is clicked, its sound panned
   toward where the icon sits on screen. The sound is made here with Web
   Audio -- no file is fetched -- and only after a click, which browsers
   require anyway. Reduced motion skips the jiggle; the sound stays tied to
   the click. */
(function () {
  var plans = document.querySelector('.plans');
  if (!plans || !plans.querySelector('.ico')) return;
  // Each plan jiggles in turn the first time it comes into view: on a phone
  // the two are stacked, taller than the screen together.
  var cards = plans.querySelectorAll('.plan');
  for (var c = 0; c < cards.length; c++) {
    var icons = cards[c].querySelectorAll('.ico');
    for (var i = 0; i < icons.length; i++) icons[i].style.setProperty('--n', i);
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('seen'); io.unobserve(e.target); } });
    }, { threshold: 0.3 });
    for (var k = 0; k < cards.length; k++) io.observe(cards[k]);
  }
  var ac = null;
  function tap(x) {
    try {
      ac = ac || new (window.AudioContext || window.webkitAudioContext)();
      var t = ac.currentTime, o = ac.createOscillator(), g = ac.createGain();
      o.type = 'triangle';
      o.frequency.setValueAtTime(880, t);
      o.frequency.exponentialRampToValueAtTime(1320, t + 0.05);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.07, t + 0.008);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.13);
      var out = g;
      if (ac.createStereoPanner) { var p = ac.createStereoPanner(); p.pan.value = Math.max(-0.8, Math.min(0.8, x * 2 - 1)); g.connect(p); out = p; }
      o.connect(g); out.connect(ac.destination);
      o.start(t); o.stop(t + 0.15);
    } catch (e) {}
  }
  plans.addEventListener('click', function (e) {
    var li = e.target.closest('li');
    if (!li || !li.querySelector('.ico') || e.target.closest('a')) return;
    var ico = li.querySelector('.ico'), r = ico.getBoundingClientRect();
    if (ico.animate && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      ico.animate([{ transform: 'none' }, { transform: 'rotate(-14deg) scale(1.16)', offset: .18 }, { transform: 'rotate(11deg) scale(1.16)', offset: .36 },
        { transform: 'rotate(-7deg) scale(1.08)', offset: .54 }, { transform: 'rotate(4deg)', offset: .72 }, { transform: 'none' }], { duration: 550, easing: 'ease-in-out' });
    }
    tap((r.left + r.width / 2) / window.innerWidth);
  });
})();

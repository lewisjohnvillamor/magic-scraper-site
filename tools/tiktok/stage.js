/* The short-form timeline.
 *
 * One page, recorded rather than browsed: a controller walks a list of beats,
 * swaps which plate is showing and where it is seeked to, and reveals the
 * caption for that beat. Nothing is composited afterwards except the music,
 * which means what you see in a browser is what lands in the file.
 *
 * The captions are motion-anything's kinetic-headline recipe (vendored, see
 * ../vendor/motion-anything/). That recipe reveals everything on load, which
 * is right for a page and wrong for a timeline, so the reveal is taken back
 * and handed out per beat instead. The split it does -- words or letters into
 * .k-unit spans with staggered delays -- is used exactly as shipped.
 */
(function () {
  'use strict';

  // Each beat: which plate, where in it, how long, and which caption.
  // `at` is a second inside the source plate; `hold` is how long we sit there.
  var BEATS = [
    // 2.4 and 3.0, not 3.6: at 3.6 the plate has already moved to the Crawl
    // tab, so the hook opened on a form instead of on the rows it is about.
    { cap: 'hook',    plate: 'bulk', at: 2.4,  hold: 2.8 },
    { cap: 'find',    plate: 'bulk', at: 3.0,  hold: 2.2 },
    { cap: 'crawl',   plate: 'bulk', at: null, hold: 5.0, chase: true },
    { cap: 'drill',   plate: 'main', at: 'drill',   hold: 3.4 },
    { cap: 'changes', plate: 'main', at: 'changes', hold: 3.6 },
    { cap: 'out',     plate: 'bulk', at: null, hold: 2.6, tail: true },
    { cap: 'end',     plate: null,   at: null, hold: 3.4 },
  ];

  var vids = { bulk: document.getElementById('v-bulk'), main: document.getElementById('v-main') };
  var caps = {};
  document.querySelectorAll('[data-beat]').forEach(function (el) { caps[el.dataset.beat] = el; });
  var bar = document.getElementById('bar');

  // Take back kinetic-headline's on-load reveal so it can be given per beat.
  function disarm() {
    document.querySelectorAll('[data-kinetic]').forEach(function (el) { el.classList.remove('is-in'); });
  }
  function reveal(el) {
    el.querySelectorAll('[data-kinetic]').forEach(function (k) {
      k.classList.remove('is-in');
      void k.offsetWidth;                 // restart the transition
      k.classList.add('is-in');
    });
  }
  // count-up runs on an IntersectionObserver, which has already fired by the
  // time this beat arrives. Re-run it by hand, on the beat.
  function recount(el) {
    el.querySelectorAll('[data-count]').forEach(function (n) {
      var target = parseFloat(n.getAttribute('data-count')) || 0;
      var dur = parseInt(n.getAttribute('data-count-duration'), 10) || 900;
      var t0 = null;
      function step(ts) {
        if (t0 === null) t0 = ts;
        var p = Math.min((ts - t0) / dur, 1);
        n.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString();
        if (p < 1) requestAnimationFrame(step);
      }
      n.textContent = '0';
      requestAnimationFrame(step);
    });
  }

  var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };

  function show(name) {
    Object.keys(caps).forEach(function (k) { caps[k].classList.toggle('on', k === name); });
  }
  function plate(name) {
    Object.keys(vids).forEach(function (k) {
      vids[k].classList.toggle('on', k === name);
      if (k !== name) vids[k].pause();
    });
  }

  window.__maDone = false;
  window.__maStart = function (sources, marks) {
    vids.bulk.src = sources.bulk;
    vids.main.src = sources.main;

    var total = BEATS.reduce(function (a, b) { return a + b.hold; }, 0);
    var elapsed = 0;

    function ready(v) {
      return new Promise(function (res) {
        if (v.readyState >= 2) return res();
        v.addEventListener('loadeddata', function () { res(); }, { once: true });
      });
    }

    return Promise.all([ready(vids.bulk), ready(vids.main)]).then(async function () {
      disarm();
      await sleep(250);

      for (var i = 0; i < BEATS.length; i++) {
        var b = BEATS[i];
        if (b.plate) {
          var v = vids[b.plate];
          // `chase` rides the counter live; `tail` sits on the finished total.
          if (b.chase) v.currentTime = marks.chaseFrom;
          else if (b.tail) v.currentTime = marks.tail;
          else v.currentTime = (typeof b.at === 'string') ? marks[b.at] : b.at;
          plate(b.plate);
          try { await v.play(); } catch (e) { /* muted autoplay */ }
        } else {
          plate(null);
        }
        show(b.cap);
        reveal(caps[b.cap]);
        recount(caps[b.cap]);
        // The recorder films from the moment the context opens, which is before
        // fonts, before the plates decode and before any of this. Mark the head
        // AFTER the first line has staggered in: on a feed the first frame is
        // the whole job, and trimming to the start of the reveal opens on an
        // empty screen.
        if (i === 0) { await sleep(560); window.__maFirstBeat = Date.now(); }

        var step = b.hold * 1000, t = 0;
        while (t < step) {
          await sleep(50); t += 50; elapsed += 50;
          bar.style.width = ((elapsed / (total * 1000)) * 100).toFixed(2) + '%';
        }
      }
      Object.keys(vids).forEach(function (k) { vids[k].pause(); });
      window.__maDone = true;
    });
  };
})();

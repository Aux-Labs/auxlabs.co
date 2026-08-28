/* Aux Labs — shared behaviour.
   1. Boot sequence dismissal (the curtain lift).
   2. Research gallery: reveal on scroll, status filtering, card expansion.
   Everything here is progressive enhancement. With this file blocked, the
   head-script failsafe still lifts the curtain and the research index still
   renders as static, readable, crawlable HTML. */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduced = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ─── 1. BOOT ──────────────────────────────────────────────────────────── */
  (function boot() {
    var el = document.getElementById('axl-boot');
    if (!el || !root.classList.contains('axl-booting')) return;

    var done = false;
    var timers = [];

    function lift() {
      if (done) return;
      done = true;
      timers.forEach(clearTimeout);
      try { sessionStorage.setItem('axl-booted', '1'); } catch (e) {}
      el.classList.add('axl-boot-out');
      window.setTimeout(function () {
        root.classList.remove('axl-booting');
      }, 280);
      window.removeEventListener('keydown', lift);
      window.removeEventListener('pointerdown', lift);
      window.removeEventListener('wheel', lift);
      window.removeEventListener('touchstart', lift);
    }

    // Any input skips it. A curtain you cannot walk through is a gate.
    window.addEventListener('keydown', lift);
    window.addEventListener('pointerdown', lift);
    window.addEventListener('wheel', lift, { passive: true });
    window.addEventListener('touchstart', lift, { passive: true });

    var lines = el.querySelectorAll('.axl-boot-line');
    Array.prototype.forEach.call(lines, function (line, i) {
      timers.push(window.setTimeout(function () {
        line.classList.add('is-on');
      }, 70 + i * 95));
    });

    var bar = el.querySelector('.axl-boot-bar span');
    if (bar) {
      timers.push(window.setTimeout(function () {
        bar.style.transition = 'width 720ms cubic-bezier(.3,.8,.3,1)';
        bar.style.width = '100%';
      }, 90));
    }

    var seal = el.querySelector('.axl-boot-seal');
    if (seal) {
      timers.push(window.setTimeout(function () { seal.classList.add('is-on'); }, 820));
    }

    timers.push(window.setTimeout(lift, 1180));
  })();

  /* ─── 2. RESEARCH GALLERY ──────────────────────────────────────────────── */
  (function gallery() {
    var grid = document.getElementById('axl-paper-grid');
    if (!grid) return;

    var cards = Array.prototype.slice.call(grid.querySelectorAll('.axl-paper'));
    var live = document.getElementById('axl-filter-status');

    /* Reveal on scroll. Cards start visible in CSS terms for crawlers; the
       .axl-reveal class is added here so a no-JS visitor never gets a
       permanently invisible grid. */
    if (!reduced && 'IntersectionObserver' in window) {
      cards.forEach(function (c) { c.classList.add('axl-reveal'); });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var i = cards.indexOf(entry.target);
          entry.target.style.transitionDelay = Math.min(i, 6) * 55 + 'ms';
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
      cards.forEach(function (c) { io.observe(c); });
    }

    /* Expansion */
    cards.forEach(function (card) {
      var btn = card.querySelector('.axl-paper-toggle');
      if (!btn) return;
      btn.addEventListener('click', function () {
        var open = card.getAttribute('data-open') === 'true';
        card.setAttribute('data-open', open ? 'false' : 'true');
        btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      });
    });

    /* Filtering */
    var filters = Array.prototype.slice.call(document.querySelectorAll('.axl-filter'));
    if (!filters.length) return;

    function apply(key, value) {
      var shown = 0;
      cards.forEach(function (card) {
        var match =
          key === 'all' ? true :
          key === 'flagship' ? card.getAttribute('data-flagship') === 'true' :
          key === 'domain' ? (card.getAttribute('data-domains') || '').split(' ').indexOf(value) > -1 :
          card.getAttribute('data-status') === value;
        card.hidden = !match;
        if (match) shown++;
        // Anything filtered back in should not sit at zero opacity.
        card.classList.add('is-in');
      });
      if (live) {
        live.textContent = shown + (shown === 1 ? ' paper shown' : ' papers shown');
      }
    }

    filters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filters.forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
        btn.setAttribute('aria-pressed', 'true');
        apply(btn.getAttribute('data-filter'), btn.getAttribute('data-value') || '');
      });
    });
  })();
})();

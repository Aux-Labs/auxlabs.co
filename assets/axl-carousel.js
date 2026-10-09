/* Research carousel: an endless, slowly drifting row of working papers.
 *
 *   - The row drifts left on its own. Hover or focus slows it to a stop; the
 *     pause button stops it for good. Drag, swipe, trackpad or the arrows move it.
 *   - Cards wrap around, so there is no end; the DOM order never changes, so
 *     screen readers and Tab still walk WP-01 to WP-10 in order.
 *   - A WebGL layer redraws each cover as a sheet of paper: it flexes, ripples
 *     and lifts off the card when the row moves fast, and settles flat when it
 *     stops. Each cover also drifts a little inside its frame (parallax).
 *   - No WebGL: the same carousel, with the plain images. Reduced motion or no
 *     JS: the original native scroller, untouched.
 */
(function () {
  var car = document.querySelector('.axl-car');
  var track = car && car.querySelector('.axl-car-track');
  if (!track) return;
  var cards = [].slice.call(track.querySelectorAll('.axl-car-card'));
  var btns = [].slice.call(car.querySelectorAll('.axl-car-btn[data-dir]'));
  var pauseBtn = car.querySelector('.axl-car-pause');
  var status = document.getElementById('axl-car-status');
  var N = cards.length;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduce) { nativeMode(); return; }

  car.classList.add('axl-car--live');
  if (pauseBtn) pauseBtn.hidden = false;

  /* ── geometry ─────────────────────────────────────────────────────────── */
  var step = 300, padL = 32, total = 3000, vw = 1000;
  function measure() {
    for (var i = 0; i < N; i++) cards[i].style.transform = '';
    var a = cards[0].getBoundingClientRect(), b = cards[1].getBoundingClientRect();
    var t = track.getBoundingClientRect();
    step = b.left - a.left; padL = a.left - t.left; total = step * N; vw = t.width;
  }

  /* ── motion state ─────────────────────────────────────────────────────── */
  var DRIFT = window.innerWidth < 640 ? 22 : 30;   // px per second: about one card every 10–12 s
  var pos = 0, target = 0, vel = 0, flex = 0;      // flex: smoothed, normalised speed for the shader
  var drift = 1, held = false, paused = false, idleUntil = 0, visible = true;
  var drag = null, moved = false;

  function wrap(v, m) { return ((v % m) + m) % m; }
  function now() { return performance.now(); }
  function poke(ms) { idleUntil = now() + (ms || 3500); }

  function layout() {
    var lo = padL - step;
    for (var i = 0; i < N; i++) {
      var base = padL + i * step;
      var x = wrap(base - pos - lo, total) + lo;
      cards[i].style.transform = 'translate3d(' + (x - base).toFixed(2) + 'px,0,0)';
    }
  }

  function label() {
    var per = Math.max(1, Math.round(vw / step));
    var first = Math.round(wrap(target, total) / step) % N;
    var a = first + 1, z = (first + per - 1) % N + 1;
    status.textContent = 'Papers ' + a + (per > 1 ? '–' + z : '') + ' of ' + N;
  }

  /* ── input ────────────────────────────────────────────────────────────── */
  btns.forEach(function (b) {
    b.disabled = false;
    b.addEventListener('click', function () {
      target = Math.round(target / step) * step + step * Number(b.dataset.dir);
      poke(5000); label();
    });
  });
  if (pauseBtn) pauseBtn.addEventListener('click', function () {
    paused = !paused;
    pauseBtn.setAttribute('aria-pressed', paused ? 'true' : 'false');
    pauseBtn.setAttribute('aria-label', paused ? 'Play the drift' : 'Pause the drift');
    pauseBtn.textContent = paused ? '>' : '||';
  });
  track.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); btns[1].click(); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); btns[0].click(); }
  });
  car.addEventListener('mouseenter', function () { held = true; });
  car.addEventListener('mouseleave', function () { held = false; });
  car.addEventListener('focusin', function (e) {
    held = true;
    var card = e.target.closest && e.target.closest('.axl-car-card');
    if (!card) return;
    // Focus makes the browser scroll the clipped track to the element; undo that
    // (the script owns the motion), then bring the card fully into view.
    track.scrollLeft = 0;
    var r = card.getBoundingClientRect(), t = track.getBoundingClientRect();
    if (r.left < t.left + padL - 1 || r.right > t.right - 1) { target += r.left - t.left - padL; pos = target; poke(5000); label(); }
  });
  car.addEventListener('focusout', function () { held = false; });

  track.addEventListener('wheel', function (e) {
    var dx = e.deltaX || (e.shiftKey ? e.deltaY : 0);
    if (Math.abs(dx) <= Math.abs(e.deltaY) && !e.shiftKey) return;   // vertical: let the page scroll
    e.preventDefault(); target += dx; poke();
  }, { passive: false });

  track.addEventListener('pointerdown', function (e) {
    if (e.button !== 0) return;
    drag = { id: e.pointerId, x: e.clientX, y: e.clientY, t0: target, lx: e.clientX, lt: now(), v: 0, live: false };
    moved = false;
  });
  track.addEventListener('pointermove', function (e) {
    if (!drag || e.pointerId !== drag.id) return;
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!drag.live) {
      if (Math.abs(dx) < 6 || Math.abs(dx) < Math.abs(dy)) return;
      drag.live = true; moved = true; car.classList.add('is-dragging');
      try { track.setPointerCapture(e.pointerId); } catch (_) {}
    }
    var t = now(), dt = Math.max(1, t - drag.lt);
    drag.v = 0.8 * ((drag.lx - e.clientX) / dt) + 0.2 * drag.v;   // px per ms, scroll direction
    drag.lx = e.clientX; drag.lt = t;
    target = drag.t0 - dx * (e.pointerType === 'touch' ? 1.15 : 1);
    pos = target - (target - pos) * 0.35;   // stay glued to the finger
    poke();
  });
  function endDrag(e) {
    if (!drag || (e && e.pointerId !== drag.id)) return;
    if (drag.live) {
      target += drag.v * 260;                                   // fling
      target = Math.round(target / step) * step;                // settle on a card edge
      poke(e && e.pointerType === 'touch' ? 5000 : 3500); label();
    }
    car.classList.remove('is-dragging'); drag = null;
  }
  track.addEventListener('pointerup', endDrag);
  track.addEventListener('pointercancel', endDrag);
  track.addEventListener('lostpointercapture', endDrag);
  // A drag is not a click: swallow the click that ends one.
  track.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  track.addEventListener('dragstart', function (e) { e.preventDefault(); });
  track.addEventListener('scroll', function () { if (track.scrollLeft) track.scrollLeft = 0; }, { passive: true });

  /* ── WebGL paper layer ────────────────────────────────────────────────── */
  var gl = null, canvas, prog, loc = {}, quads = [], dpr = 1, gridCount = 0;
  try { initGL(); } catch (err) { gl = null; if (window.console) console.warn("axl-carousel: WebGL off,", err && err.message); }

  function initGL() {
    canvas = document.createElement('canvas');
    canvas.className = 'axl-car-gl';
    canvas.setAttribute('aria-hidden', 'true');
    gl = canvas.getContext('webgl2', { alpha: true, premultipliedAlpha: true, antialias: true });
    if (!gl) return;

    var vs = '#version 300 es\n' +
      'in vec2 aP;\n' +
      'uniform vec4 uRect; uniform vec2 uRes; uniform float uFlex, uTime, uSeed;\n' +
      'out vec2 vUv; out float vShade;\n' +
      'const float PI = 3.14159265;\n' +
      'void main(){\n' +
      '  float f = uFlex, a = abs(f);\n' +
      '  float bow = sin(aP.x * PI);\n' +
      // Depth into the screen (in card widths): a bow across the sheet, a ripple running
      // down it, and a whisper of flutter even at rest so the covers never look frozen.
      '  float ripple = sin(aP.y * 6.2832 + aP.x * 2.4 - uTime * 3.2 + uSeed);\n' +
      '  float idle = 0.010 * sin(aP.x * 3.1 + aP.y * 2.3 + uTime * 0.9 + uSeed);\n' +
      '  float z = a * (0.20 * bow + 0.05 * ripple) + idle * bow;\n' +
      '  vec2 q = (aP - 0.5) * (1.0 - 0.10 * a);\n' +           // lifts off the card while moving
      '  q.y += f * 0.045 * bow;\n' +                            // the sheet bends against the motion
      '  q.x += f * 0.020 * (aP.y - 0.5) * (aP.y - 0.5);\n' +
      '  q /= (1.0 + z * 1.4);\n' +                              // perspective: deeper = smaller
      '  vec2 px = uRect.xy + uRect.zw * 0.5 + q * uRect.zw;\n' +
      '  vec2 c = px / uRes * 2.0 - 1.0;\n' +
      '  gl_Position = vec4(c.x, -c.y, 0.0, 1.0);\n' +
      '  float slope = a * 0.20 * PI * cos(aP.x * PI) + 0.03 * a * cos(aP.y * 6.2832 - uTime * 3.2 + uSeed);\n' +
      '  vShade = 1.0 + 0.55 * slope - 0.25 * a * bow;\n' +   // light from the left; the bowed middle sits in shadow
      '  vUv = aP;\n' +
      '}';
    var fs = '#version 300 es\nprecision highp float;\n' +
      'in vec2 vUv; in float vShade;\n' +
      'uniform sampler2D uTex; uniform vec2 uCover; uniform float uPar, uFlex, uAlpha;\n' +
      'out vec4 o;\n' +
      'float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }\n' +
      'void main(){\n' +
      '  vec2 uv = (vUv - 0.5) * uCover / 1.10 + 0.5;\n' +     // 10% headroom for the parallax
      '  uv.x += uPar * 0.045;\n' +
      '  vec3 c = texture(uTex, uv).rgb * vShade;\n' +
      '  c += (h(gl_FragCoord.xy) - 0.5) * (0.025 + 0.05 * abs(uFlex));\n' +   // paper grain
      '  o = vec4(c * uAlpha, uAlpha);\n' +
      '}';
    prog = link(compile(gl.VERTEX_SHADER, vs), compile(gl.FRAGMENT_SHADER, fs));
    ['aP', 'uRect', 'uRes', 'uFlex', 'uTime', 'uSeed', 'uTex', 'uCover', 'uPar', 'uAlpha'].forEach(function (k) {
      loc[k] = k === 'aP' ? gl.getAttribLocation(prog, k) : gl.getUniformLocation(prog, k);
    });

    // One shared grid mesh, 40 × 40 cells, as a triangle strip per row.
    var S = 40, verts = [];
    for (var y = 0; y < S; y++) {
      for (var x = 0; x <= S; x++) { verts.push(x / S, y / S, x / S, (y + 1) / S); }
      if (y < S - 1) verts.push(1, (y + 1) / S, 0, (y + 1) / S);   // degenerate joins between rows
    }
    gridCount = verts.length / 2;
    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(verts), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(loc.aP);
    gl.vertexAttribPointer(loc.aP, 2, gl.FLOAT, false, 0, 0);

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.enable(gl.SCISSOR_TEST);

    track.appendChild(canvas);
    canvas.addEventListener('webglcontextlost', function (e) {
      e.preventDefault(); gl = null; canvas.remove();
      quads.forEach(function (q) { q.art.classList.remove('is-gl'); });
    });

    cards.forEach(function (card, i) {
      var art = card.querySelector('.axl-car-art'), img = art && art.querySelector('img');
      if (!img) return;
      var q = { art: art, tex: null, w: 1, h: 1, seed: i * 1.7, a: 0 };
      quads.push(q);
      var im = new Image();
      im.decoding = 'async';
      im.onload = function () {
        if (!gl) return;
        q.tex = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, q.tex);
        gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
        gl.generateMipmap(gl.TEXTURE_2D);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        q.w = im.naturalWidth; q.h = im.naturalHeight;
        art.classList.add('is-gl');
      };
      im.src = img.currentSrc || img.src;
    });
  }
  function compile(type, src) {
    var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }
  function link(v, f) {
    var p = gl.createProgram(); gl.attachShader(p, v); gl.attachShader(p, f); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    gl.useProgram(p); return p;
  }

  function sizeCanvas() {
    if (!gl) return;
    dpr = Math.min(window.devicePixelRatio || 1, window.innerWidth < 640 ? 2 : 1.75);
    var w = track.clientWidth, h = track.clientHeight;
    canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
  }

  function draw(time) {
    if (!gl) return;
    var W = canvas.width, H = canvas.height;
    gl.viewport(0, 0, W, H);
    gl.disable(gl.SCISSOR_TEST); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); gl.enable(gl.SCISSOR_TEST);
    gl.uniform2f(loc.uRes, W, H);
    gl.uniform1f(loc.uTime, time);
    gl.uniform1f(loc.uFlex, flex);
    var t = track.getBoundingClientRect(), mid = t.left + t.width / 2;
    for (var i = 0; i < quads.length; i++) {
      var q = quads[i];
      if (!q.tex) continue;
      var r = q.art.getBoundingClientRect();
      if (r.right < t.left || r.left > t.right) continue;
      q.a = Math.min(1, q.a + 0.06);                       // fade each cover in once it has loaded
      // Inside the 2px card border, in canvas pixels.
      var x = (r.left - t.left + 2) * dpr, y = (r.top - t.top + 2) * dpr;
      var w = (r.width - 4) * dpr, h = (r.height - 4) * dpr;
      gl.scissor(Math.floor(x), Math.floor(H - y - h), Math.ceil(w), Math.ceil(h));
      gl.uniform4f(loc.uRect, x, y, w, h);
      var ra = w / h, ia = q.w / q.h;                      // object-fit: cover
      gl.uniform2f(loc.uCover, ra > ia ? 1 : ra / ia, ra > ia ? ia / ra : 1);
      gl.uniform1f(loc.uPar, Math.max(-1, Math.min(1, (r.left + r.width / 2 - mid) / (t.width / 2))));
      gl.uniform1f(loc.uSeed, q.seed);
      gl.uniform1f(loc.uAlpha, q.a);
      gl.bindTexture(gl.TEXTURE_2D, q.tex);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, gridCount);
    }
  }

  /* ── loop ─────────────────────────────────────────────────────────────── */
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) kick(); }, { rootMargin: '100px' }).observe(track);
  }
  var last = 0, raf = 0;
  function kick() { if (!raf) { last = 0; raf = requestAnimationFrame(frame); } }
  function frame(t) {
    raf = 0;
    if (!visible) return;
    var dt = last ? Math.min(0.05, (t - last) / 1000) : 0.016; last = t;
    var go = !paused && !held && !drag && t > idleUntil;
    drift += ((go ? 1 : 0) - drift) * (1 - Math.exp(-dt * (go ? 1.2 : 4)));   // ease in slowly, ease out quickly
    target += DRIFT * drift * dt;
    var prev = pos;
    pos += (target - pos) * (1 - Math.exp(-dt * 7));
    vel = (pos - prev) / dt;
    var f = Math.max(-1, Math.min(1, vel / 1400));
    flex += (f - flex) * (1 - Math.exp(-dt * 6));
    // Keep the numbers small; the layout is periodic anyway.
    if (pos > total * 4 || pos < -total * 4) { var k = Math.round(pos / total) * total; pos -= k; target -= k; }
    layout(); draw(t / 1000);
    raf = requestAnimationFrame(frame);
  }

  function onResize() {
    DRIFT = window.innerWidth < 640 ? 22 : 30;
    var idx = pos / step; measure(); pos = target = idx * step; sizeCanvas(); layout(); label();
  }
  if ('ResizeObserver' in window) new ResizeObserver(onResize).observe(track); else window.addEventListener('resize', onResize);
  onResize(); status.textContent = 'Drag, swipe or use the arrows';
  kick();

  /* ── reduced motion: the original native scroller ─────────────────────── */
  function nativeMode() {
    function stepW() { return cards[0].getBoundingClientRect().width + 24; }
    function sync() { var max = track.scrollWidth - track.clientWidth - 2;
      btns[0].disabled = track.scrollLeft <= 2; btns[1].disabled = track.scrollLeft >= max; }
    function lbl() { var w = stepW(), first = Math.round(track.scrollLeft / w) + 1, per = Math.max(1, Math.round(track.clientWidth / w));
      var lst = Math.min(N, first + per - 1); status.textContent = 'Papers ' + first + (lst > first ? '–' + lst : '') + ' of ' + N; }
    btns.forEach(function (b) { b.addEventListener('click', function () { track.scrollBy({ left: stepW() * Number(b.dataset.dir), behavior: 'auto' }); }); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); btns[1].click(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); btns[0].click(); } });
    track.addEventListener('scroll', function () { sync(); lbl(); }, { passive: true });
    window.addEventListener('resize', function () { sync(); lbl(); });
    sync(); lbl();
  }
})();

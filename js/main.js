/* НеСутулься — эффекты и логика. Vanilla JS, без зависимостей. */
(function () {
  'use strict';

  // ====== НАСТРОЙКИ ======
  // URL обработчика формы (POST, JSON {name, phone, page}). Пусто — форма показывает «успех» и предлагает позвонить.
  var FORM_ENDPOINT = '';
  var WORK_FROM = 10, WORK_TO = 21; // часы работы по Москве

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var isMobile = window.matchMedia('(max-width: 760px)').matches;
  var root = document.documentElement;

  // ====== PRELOADER ======
  var pre = $('#preloader');
  function finishPreload() {
    if (!pre || pre.classList.contains('is-done')) return;
    pre.classList.add('is-done');
    document.body.classList.remove('is-loading');
    document.body.classList.add('is-ready');
    setTimeout(function () { pre && pre.remove(); }, 1200);
    slapStickers();
  }
  function runPreloader() {
    if (!pre) { document.body.classList.add('is-ready'); return; }
    if (reduce) { finishPreload(); return; }
    var cv = $('#preFx'), path = $('#sprayPath'), svg = $('.preloader__logo');
    var ctx = cv.getContext('2d'), dpr = Math.min(window.devicePixelRatio || 1, 2);
    function size() { cv.width = innerWidth * dpr; cv.height = innerHeight * dpr; }
    size();
    var parts = [], t0 = performance.now(), DUR = 1500, DELAY = 250, len = 0;
    try { len = path.getTotalLength(); } catch (e) { len = 0; }
    var colors = ['#bdf06b', '#bdf06b', '#ffe14d', '#ff2d8a'];
    (function loop(now) {
      if (!pre || pre.classList.contains('is-done')) return;
      var p = Math.min(Math.max((now - t0 - DELAY) / DUR, 0), 1);
      // cubic-bezier(.6,.1,.4,1) approx
      var e = p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
      ctx.clearRect(0, 0, cv.width, cv.height);
      if (len && p > 0 && p < 1) {
        var pt = path.getPointAtLength(e * len), r = svg.getBoundingClientRect();
        var sx = r.width / 900, x = (r.left + pt.x * sx) * dpr, y = (r.top + pt.y * sx) * dpr;
        for (var i = 0; i < 14; i++) {
          var a = Math.random() * 6.283, d = Math.pow(Math.random(), 1.8) * 70 * dpr;
          parts.push({ x: x + Math.cos(a) * d, y: y + Math.sin(a) * d, r: (Math.random() * 2.4 + .6) * dpr, l: 1, c: colors[i % 4] });
        }
      }
      for (var j = parts.length - 1; j >= 0; j--) {
        var q = parts[j]; q.l -= .03; q.y += .3 * dpr;
        if (q.l <= 0) { parts.splice(j, 1); continue; }
        ctx.globalAlpha = q.l; ctx.fillStyle = q.c; ctx.beginPath(); ctx.arc(q.x, q.y, q.r, 0, 6.283); ctx.fill();
      }
      ctx.globalAlpha = 1;
      requestAnimationFrame(loop);
    })(t0);
    var done = false;
    function go() { if (done) return; done = true; setTimeout(finishPreload, Math.max(0, DELAY + DUR + 350 - (performance.now() - t0))); }
    if (document.readyState === 'complete') go(); else window.addEventListener('load', go);
    setTimeout(finishPreload, 4500); // страховка
  }
  runPreloader();

  // ====== SPLIT TITLES ======
  $$('.spray-title').forEach(function (h) {
    var text = h.textContent, i = 0;
    h.setAttribute('aria-label', text);
    h.innerHTML = text.split(' ').map(function (w) {
      return '<span class="w" aria-hidden="true" style="display:inline-block;white-space:nowrap">' + w.split('').map(function (c) {
        return '<span class="ch" style="--i:' + (i++) + '">' + c + '</span>';
      }).join('') + '</span>';
    }).join('<span class="ch ch--sp" aria-hidden="true" style="--i:' + i + '"> </span>');
  });

  // ====== FIT MEGA TITLE ======
  var mega = $('.mega');
  function fitMega() {
    if (!mega) return;
    mega.style.fontSize = '';
    var w = mega.parentElement.clientWidth, s = $('.mega__s', mega), sw = s.scrollWidth;
    if (sw > w) mega.style.fontSize = (parseFloat(getComputedStyle(mega).fontSize) * w / sw * 0.97).toFixed(1) + 'px';
  }
  fitMega();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitMega);
  window.addEventListener('resize', fitMega);

  // ====== REVEAL ======
  var revealEls = $$('.reveal, .spray-title, .sec-head, .zapis, .tilt');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    revealEls.forEach(function (el) { if (!el.closest('.wall, .docs')) io.observe(el); });
    // горизонтальные ленты на мобильном: проявляем всех детей, когда лента попала в экран
    $$('.wall, .docs').forEach(function (box) {
      var bio = new IntersectionObserver(function (ents) {
        ents.forEach(function (en) { if (en.isIntersecting) { $$('.reveal', box).forEach(function (c) { c.classList.add('in'); }); bio.disconnect(); } });
      }, { threshold: 0.1 });
      bio.observe(box);
    });
  } else revealEls.forEach(function (el) { el.classList.add('in'); });

  // ====== HEADER / PROGRESS / PARALLAX / SPRAY LINE ======
  var hdr = $('#hdr'), bar = $('#progressBar'), lastY = 0, ticking = false;
  var para = reduce ? [] : $$('[data-speed]');
  var line = $('#sprayLine'), stepsWrap = $('.steps-wrap');
  function onScroll() {
    var y = window.scrollY, h = root.scrollHeight - innerHeight;
    hdr.classList.toggle('is-scrolled', y > 40);
    hdr.classList.toggle('is-hidden', y > 500 && y > lastY && !menuOpen);
    lastY = y;
    if (bar) bar.style.transform = 'scaleX(' + (h > 0 ? y / h : 0) + ')';
    var k = isMobile ? 0.45 : 1;
    for (var i = 0; i < para.length; i++) {
      var el = para[i], r = el.parentElement.getBoundingClientRect();
      if (r.bottom < -200 || r.top > innerHeight + 200) continue;
      var c = (r.top + r.height / 2 - innerHeight / 2);
      el.style.translate = '0 ' + (c * -parseFloat(el.dataset.speed) * k).toFixed(1) + 'px';
    }
    if (line && stepsWrap) {
      var sr = stepsWrap.getBoundingClientRect();
      var p = Math.min(Math.max((innerHeight * 0.7 - sr.top) / sr.height, 0), 1);
      line.style.strokeDashoffset = reduce ? 0 : (1 - p);
    }
    ticking = false;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  window.addEventListener('resize', function () { isMobile = window.matchMedia('(max-width: 760px)').matches; onScroll(); });
  onScroll();

  // ====== MOBILE MENU ======
  var burger = $('#burger'), mnav = $('#mnav'), menuOpen = false;
  function setMenu(open) {
    menuOpen = open;
    burger.setAttribute('aria-expanded', open);
    mnav.classList.toggle('is-open', open);
    mnav.setAttribute('aria-hidden', !open);
    document.body.style.overflow = open ? 'hidden' : '';
  }
  burger.addEventListener('click', function () { setMenu(!menuOpen); });
  $$('a', mnav).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { setMenu(false); closeLb(); } });

  // ====== STATUS BY MOSCOW TIME ======
  function mskHour() {
    var d = new Date(), utc = d.getTime() + d.getTimezoneOffset() * 60000, m = new Date(utc + 3 * 3600000);
    return m.getHours() + m.getMinutes() / 60;
  }
  function updStatus() {
    var h = mskHour(), open = h >= WORK_FROM && h < WORK_TO;
    $$('[data-status]').forEach(function (s) {
      s.classList.toggle('is-open', open);
      s.querySelector('span').textContent = open ? 'Сейчас открыто · до 21:00' : 'Сейчас закрыто · откроемся в 10:00';
    });
  }
  updStatus(); setInterval(updStatus, 60000);

  // ====== TYPER ======
  var words = ['Боли в спине?', 'Боли в шее?', 'Сутулость?', 'Плоскостопие?', 'После операции?', 'Спортивная травма?', 'Головные боли?'];
  var typer = $('#typer');
  if (typer && !reduce) {
    var wi = 0, ci = words[0].length, del = true;
    (function tick() {
      var w = words[wi];
      if (del) { ci--; if (ci <= 0) { del = false; wi = (wi + 1) % words.length; } }
      else { ci++; if (ci >= words[wi].length) { del = true; typer.textContent = words[wi]; return setTimeout(tick, 1700); } }
      typer.textContent = words[wi].slice(0, Math.max(ci, 0)) || '\u00a0';
      setTimeout(tick, del ? 38 : 75);
    })();
  }

  // ====== GLITCH ======
  var glitches = $$('.glitch');
  if (!reduce) {
    var glitchAll = function () {
      glitches.forEach(function (g) {
        var r = g.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight) return;
        g.classList.remove('is-glitch'); void g.offsetWidth; g.classList.add('is-glitch');
        setTimeout(function () { g.classList.remove('is-glitch'); }, 460);
      });
    };
    setTimeout(function () { glitchAll(); setInterval(glitchAll, 5200); }, 7000);
    glitches.forEach(function (g) { g.addEventListener('mouseenter', function () { g.classList.add('is-glitch'); setTimeout(function () { g.classList.remove('is-glitch'); }, 460); }); });
  }

  // ====== COUNTERS ======
  function fmt(n, sp) { return sp ? String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '\u00a0') : String(n); }
  var counters = $$('[data-count]');
  if ('IntersectionObserver' in window && !reduce) {
    var cio = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (!en.isIntersecting) return; cio.unobserve(en.target);
        var el = en.target, to = +el.dataset.count, sp = el.dataset.format === 'space', t0 = performance.now(), D = 1400;
        (function f(now) { var p = Math.min((now - t0) / D, 1), e = 1 - Math.pow(1 - p, 4); el.textContent = fmt(Math.round(to * e), sp); if (p < 1) requestAnimationFrame(f); })(t0);
      });
    }, { threshold: .6 });
    counters.forEach(function (c) { c.textContent = '0'; cio.observe(c); });
  }

  // ====== MAGNETIC BUTTONS ======
  if (finePointer && !reduce) {
    $$('.magnetic').forEach(function (b) {
      b.addEventListener('mousemove', function (e) {
        var r = b.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
        b.style.setProperty('--bx', ((x - r.width / 2) * .28).toFixed(1) + 'px');
        b.style.setProperty('--by', ((y - r.height / 2) * .38).toFixed(1) + 'px');
        b.style.setProperty('--mx', x + 'px'); b.style.setProperty('--my', y + 'px');
      });
      b.addEventListener('mouseleave', function () { b.style.setProperty('--bx', '0px'); b.style.setProperty('--by', '0px'); });
    });
    // ====== 3D TILT ======
    $$('.tilt').forEach(function (c) {
      c.addEventListener('mousemove', function (e) {
        var r = c.getBoundingClientRect(), px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
        c.classList.add('is-tilting');
        c.style.setProperty('--ry', ((px - .5) * 14).toFixed(2) + 'deg');
        c.style.setProperty('--rx', ((.5 - py) * 12).toFixed(2) + 'deg');
        c.style.setProperty('--gx', (px * 100) + '%'); c.style.setProperty('--gy', (py * 100) + '%');
      });
      c.addEventListener('mouseleave', function () { c.classList.remove('is-tilting'); c.style.setProperty('--rx', '0deg'); c.style.setProperty('--ry', '0deg'); });
    });
  }

  // ====== STICKERS WITH PHYSICS ======
  var stickers = $$('[data-drag]');
  function slapStickers() {
    if (reduce) return;
    stickers.forEach(function (s, i) { setTimeout(function () { s.classList.add('slap'); }, 900 + i * 220); });
  }
  stickers.forEach(function (s) {
    var st = { x: 0, y: 0, vx: 0, vy: 0, rot: parseFloat(getComputedStyle(s).getPropertyValue('--rot')) || 0, drag: false, lx: 0, ly: 0, lt: 0, raf: 0 };
    var zone = s.closest('[data-sticker-zone]') || s.parentElement;
    function apply() { s.style.setProperty('--x', st.x.toFixed(1) + 'px'); s.style.setProperty('--y', st.y.toFixed(1) + 'px'); s.style.setProperty('--rot', st.rot.toFixed(1) + 'deg'); }
    function bounds() {
      var z = zone.getBoundingClientRect(), r = s.getBoundingClientRect();
      var bx = r.left - st.x, by = r.top - st.y; // базовая позиция без смещения
      return { minX: z.left - bx - 10, maxX: z.right - bx - r.width + 10, minY: z.top - by - 10, maxY: z.bottom - by - r.height + 10 };
    }
    function fly() {
      if (st.drag) return;
      var b = bounds();
      st.vx *= .95; st.vy *= .95; st.vy += .35;
      st.x += st.vx; st.y += st.vy;
      if (st.x < b.minX) { st.x = b.minX; st.vx = -st.vx * .6; }
      if (st.x > b.maxX) { st.x = b.maxX; st.vx = -st.vx * .6; }
      if (st.y < b.minY) { st.y = b.minY; st.vy = -st.vy * .6; }
      if (st.y > b.maxY) { st.y = b.maxY; st.vy = -st.vy * .55; st.vx *= .85; }
      st.rot += st.vx * .4;
      apply();
      if (Math.abs(st.vx) + Math.abs(st.vy) > .25 || st.y < b.maxY - 1) st.raf = requestAnimationFrame(fly);
    }
    s.addEventListener('pointerdown', function (e) {
      st.drag = true; cancelAnimationFrame(st.raf); s.setPointerCapture(e.pointerId);
      st.lx = e.clientX; st.ly = e.clientY; st.lt = performance.now(); s.style.zIndex = 20; s.style.setProperty('--s', 1.12);
    });
    s.addEventListener('pointermove', function (e) {
      if (!st.drag) return;
      var dx = e.clientX - st.lx, dy = e.clientY - st.ly, now = performance.now(), dt = Math.max(now - st.lt, 1);
      st.x += dx; st.y += dy; st.vx = dx / dt * 16; st.vy = dy / dt * 16; st.rot += dx * .15;
      st.lx = e.clientX; st.ly = e.clientY; st.lt = now; apply();
    });
    function up() { if (!st.drag) return; st.drag = false; s.style.setProperty('--s', 1); if (!reduce) st.raf = requestAnimationFrame(fly); }
    s.addEventListener('pointerup', up); s.addEventListener('pointercancel', up);
    s.addEventListener('click', function () { if (Math.abs(st.vx) + Math.abs(st.vy) < 1 && !reduce) { st.vy = -14; st.vx = (Math.random() - .5) * 12; st.raf = requestAnimationFrame(fly); } });
  });

  // ====== SPRAY CURSOR (desktop) ======
  if (finePointer && !reduce && !isMobile) {
    root.classList.add('has-spray');
    var cv = $('#sprayCursor'), can = $('#canCursor'), ctx = cv.getContext('2d'), dpr = Math.min(window.devicePixelRatio || 1, 2);
    var P = [], mx = -100, my = -100, down = false, running = false, pal = ['#bdf06b', '#ffe14d', '#ff2d8a', '#38f5ff'], ci = 0;
    function rs() { cv.width = innerWidth * dpr; cv.height = innerHeight * dpr; }
    rs(); window.addEventListener('resize', rs);
    function emit(n, spread) {
      var col = pal[ci];
      for (var i = 0; i < n; i++) {
        var a = Math.random() * 6.283, d = Math.pow(Math.random(), 2) * spread;
        P.push({ x: mx + Math.cos(a) * d, y: my + Math.sin(a) * d, r: Math.random() * 1.8 + .4, l: 1, c: col, drip: down && Math.random() < .015 ? Math.random() * 40 + 10 : 0, vy: 0 });
      }
      if (P.length > 1400) P.splice(0, P.length - 1400);
      if (!running) { running = true; requestAnimationFrame(draw); }
    }
    function draw() {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, innerWidth, innerHeight);
      for (var i = P.length - 1; i >= 0; i--) {
        var p = P[i]; p.l -= p.drip ? .006 : .018;
        if (p.drip > 0) { p.y += .6; p.drip -= .6; }
        if (p.l <= 0) { P.splice(i, 1); continue; }
        ctx.globalAlpha = p.l * .9; ctx.fillStyle = p.c; ctx.beginPath(); ctx.arc(p.x, p.y, p.drip > 0 ? 2.2 : p.r, 0, 6.283); ctx.fill();
      }
      ctx.globalAlpha = 1;
      if (P.length) requestAnimationFrame(draw); else running = false;
    }
    window.addEventListener('mousemove', function (e) {
      var dx = e.clientX - mx, dy = e.clientY - my; mx = e.clientX; my = e.clientY;
      can.style.transform = 'translate(' + (mx - 4) + 'px,' + (my - 36) + 'px)';
      var sp = Math.min(Math.hypot(dx, dy), 60);
      emit(down ? 26 : Math.round(sp / 6), down ? 26 : 12);
    }, { passive: true });
    window.addEventListener('mousedown', function (e) { if (e.target.closest('input,textarea,[data-drag]')) return; down = true; can.classList.add('is-down'); var t = setInterval(function () { if (!down) return clearInterval(t); emit(18, 30); }, 30); });
    window.addEventListener('mouseup', function () { if (down) { down = false; ci = (ci + 1) % pal.length; can.classList.remove('is-down'); } });
    document.addEventListener('mouseover', function (e) { can.classList.toggle('is-hover', !!e.target.closest('a,button,summary,label,[data-drag]')); });
    document.addEventListener('mouseleave', function () { can.style.transform = 'translate(-100px,-100px)'; });
  }

  // ====== HERO VIDEO (lazy) ======
  var vid = $('.tv__v');
  if (vid) {
    var startVid = function () { if (!vid.src) { vid.src = vid.dataset.src; } if (!reduce) { var p = vid.play(); if (p && p.catch) p.catch(function () {}); } };
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (ents) { ents.forEach(function (en) { if (en.isIntersecting) startVid(); else if (vid.src) vid.pause(); }); }, { threshold: .2 }).observe(vid);
    } else startVid();
  }

  // ====== LIGHTBOX ======
  var lb = $('#lightbox'), lbImg = lb && $('img', lb);
  function closeLb() { if (lb && !lb.hidden) { lb.hidden = true; lbImg.src = ''; document.body.style.overflow = ''; } }
  $$('.polaroid').forEach(function (p) {
    p.addEventListener('click', function () { lbImg.src = p.dataset.full; lbImg.alt = p.querySelector('img').alt; lb.hidden = false; document.body.style.overflow = 'hidden'; $('.lightbox__x', lb).focus(); });
  });
  if (lb) lb.addEventListener('click', function (e) { if (e.target !== lbImg) closeLb(); });

  // ====== FAQ: one open at a time ======
  $$('.qa').forEach(function (d) { d.addEventListener('toggle', function () { if (d.open) $$('.qa').forEach(function (o) { if (o !== d) o.open = false; }); }); });

  // ====== FORM ======
  var form = $('#leadForm');
  if (form) {
    var phone = form.elements.phone, err = $('.form__err', form), ok = $('.form__ok', form);
    phone.addEventListener('input', function () {
      var d = phone.value.replace(/\D/g, '');
      if (d[0] === '8') d = '7' + d.slice(1);
      if (d && d[0] !== '7') d = '7' + d;
      d = d.slice(0, 11);
      var o = d ? '+7' : '';
      if (d.length > 1) o += ' (' + d.slice(1, 4);
      if (d.length >= 4) o += ') ' + d.slice(4, 7);
      if (d.length >= 7) o += '-' + d.slice(7, 9);
      if (d.length >= 9) o += '-' + d.slice(9, 11);
      phone.value = o;
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = form.elements.name, agree = form.elements.agree, bad = [];
      [name, phone, agree].forEach(function (el) { el.classList.remove('is-bad'); });
      if (name.value.trim().length < 2) bad.push(name);
      if (phone.value.replace(/\D/g, '').length !== 11) bad.push(phone);
      if (!agree.checked) bad.push(agree);
      if (bad.length) {
        bad.forEach(function (el) { void el.offsetWidth; el.classList.add('is-bad'); });
        err.textContent = !agree.checked && bad.length === 1 ? 'Поставь галочку согласия — без неё не можем принять заявку.' : 'Проверь имя и телефон — нужен номер из 11 цифр.';
        err.hidden = false; bad[0].focus(); return;
      }
      err.hidden = true;
      if (form.elements.website.value) return; // бот
      var btn = form.querySelector('[type=submit]'); btn.disabled = true;
      var payload = { name: name.value.trim(), phone: phone.value, page: location.href };
      var done = function () { ok.hidden = false; btn.disabled = false; form.reset(); };
      if (!FORM_ENDPOINT) { setTimeout(done, 500); return; }
      fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); done(); })
        .catch(function () { btn.disabled = false; err.innerHTML = 'Не получилось отправить. Позвони нам: <a href="tel:+79266911805">+7 926 691-18-05</a>'; err.hidden = false; });
    });
  }
})();

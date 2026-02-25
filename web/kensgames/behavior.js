/* ═══════════════════════════════════════════════════════════════════
   KEN'S GAMES — MANIFOLD BEHAVIOR
   ═══════════════════════════════════════════════════════════════════
   z = x · y — Behavior emerges from the substrate.
   
   Every constant is φ or Fibonacci.
   Every animation follows the golden ratio.
   3D immersive. Multi-layer parallax. Forced perspective.
   ═══════════════════════════════════════════════════════════════════ */

;(function manifold() {
  'use strict';

  const PHI = 1.618033988749895;
  const PHI_INV = 0.618033988749895;
  const FIB = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610];

  /* ═══ LAYER 1 · SPARK — Starfield & game spark canvases ═══ */

  function initStarfield() {
    const canvas = document.getElementById('starfield');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let w, h, stars;

    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    }

    function createStars() {
      /* 233 Fibonacci stars — 3 depth bands at 0.382, 0.618, 1.0 */
      stars = [];
      const count = 233;
      for (let i = 0; i < count; i++) {
        const band = i < 89 ? 0 : i < 178 ? 1 : 2;
        const alpha = [0.2, 0.45, 0.8][band];
        const radius = [0.5, 1, 1.5][band];
        const speed = [0.08, 0.15, 0.28][band];
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          r: radius,
          a: alpha,
          s: speed,
          tw: Math.random() * Math.PI * 2, /* twinkle phase */
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      const t = Date.now() * 0.001;
      for (const s of stars) {
        s.y -= s.s;
        if (s.y < -2) { s.y = h + 2; s.x = Math.random() * w; }
        /* φ-modulated twinkle */
        const twinkle = 0.5 + 0.5 * Math.sin(t * PHI + s.tw);
        ctx.globalAlpha = s.a * twinkle;
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      requestAnimationFrame(draw);
    }

    resize();
    createStars();
    draw();
    window.addEventListener('resize', () => { resize(); createStars(); });
  }

  function initGameSparks() {
    const canvas = document.getElementById('game-sparks');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let w, h, sparks;

    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    }

    function createSparks() {
      /* 34 Fibonacci game sparks — colored by Genesis layers */
      const colors = [
        'rgba(255,68,102,',   /* fire */
        'rgba(255,215,0,',    /* gold */
        'rgba(64,255,255,',   /* neon */
        'rgba(155,89,182,',   /* purple */
        'rgba(52,152,219,',   /* blue */
        'rgba(39,174,96,',    /* green */
        'rgba(243,156,18,',   /* orange */
      ];
      sparks = [];
      for (let i = 0; i < 34; i++) {
        sparks.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * PHI_INV,
          vy: (Math.random() - 0.5) * PHI_INV,
          r: FIB[Math.floor(Math.random() * 4)] * 0.8,
          color: colors[i % 7],
          phase: Math.random() * Math.PI * 2,
          life: 0.3 + Math.random() * 0.7,
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      const t = Date.now() * 0.001;
      for (const s of sparks) {
        s.x += s.vx;
        s.y += s.vy;
        /* Wrap */
        if (s.x < -10) s.x = w + 10;
        if (s.x > w + 10) s.x = -10;
        if (s.y < -10) s.y = h + 10;
        if (s.y > h + 10) s.y = -10;

        /* φ-breath pulse */
        const pulse = 0.3 + 0.7 * Math.abs(Math.sin(t * PHI_INV + s.phase));
        const alpha = s.life * pulse * 0.4;

        /* Radial glow */
        const grad = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 3);
        grad.addColorStop(0, s.color + alpha + ')');
        grad.addColorStop(0.618, s.color + (alpha * 0.3) + ')');
        grad.addColorStop(1, s.color + '0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI * 2);
        ctx.fill();
      }
      requestAnimationFrame(draw);
    }

    resize();
    createSparks();
    draw();
    window.addEventListener('resize', () => { resize(); createSparks(); });
  }


  /* ═══ LAYER 2 · MIRROR — Multi-layer 3D parallax ═══ */

  function initParallax() {
    const layers = document.querySelectorAll('.depth-layer');
    if (!layers.length) return;

    /* Depth factors — deeper layers move more slowly (forced perspective) */
    const depthFactors = {
      1: 0.03,
      2: 0.05,
      3: 0.08,
      4: 0.12,
      5: 0.18,
      6: 0.25,
      7: 0.35,
    };

    let mouseX = 0, mouseY = 0, tiltX = 0, tiltY = 0;

    document.addEventListener('mousemove', e => {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    function tick() {
      /* φ-damped interpolation */
      tiltX += (mouseX - tiltX) * PHI_INV * 0.08;
      tiltY += (mouseY - tiltY) * PHI_INV * 0.08;

      layers.forEach(layer => {
        const d = parseInt(layer.dataset.depth) || 4;
        const factor = depthFactors[d] || 0.12;
        const dx = tiltX * factor * 100;
        const dy = tiltY * factor * 100;
        const rz = tiltX * factor * 2;
        const baseScale = parseFloat(getComputedStyle(layer).transform.split(',')[3]) || 1;
        layer.style.transform =
          `translateZ(${-FIB[10 - d] || -55}px) ` +
          `translate(${dx}px, ${dy}px) ` +
          `rotateY(${tiltX * factor * 3}deg) ` +
          `rotateX(${-tiltY * factor * 3}deg)`;
      });

      requestAnimationFrame(tick);
    }

    tick();
  }


  /* ═══ LAYER 4 · FORM — 3D card tilt ═══ */

  function initCardTilt() {
    const cards = document.querySelectorAll('.game-card');
    cards.forEach(card => {
      card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        /* Tilt by ±8° — φ-scaled */
        const ry = (x - 0.5) * 16;
        const rx = (y - 0.5) * -16;
        card.style.setProperty('--rx', rx + 'deg');
        card.style.setProperty('--ry', ry + 'deg');
        card.style.setProperty('--mx', (x * 100) + '%');
        card.style.setProperty('--my', (y * 100) + '%');
      });

      card.addEventListener('mouseleave', () => {
        card.style.setProperty('--rx', '0deg');
        card.style.setProperty('--ry', '0deg');
      });
    });
  }


  /* ═══ LAYER 6 · MIND — Navigation ═══ */

  function initNav() {
    const burger = document.querySelector('.burger');
    const drawer = document.getElementById('drawer');
    const overlay = document.getElementById('overlay');
    const close = drawer ? drawer.querySelector('.drawer-close') : null;

    function openDrawer() {
      drawer.classList.add('open');
      overlay.classList.add('visible');
    }

    function closeDrawer() {
      drawer.classList.remove('open');
      overlay.classList.remove('visible');
    }

    if (burger) burger.addEventListener('click', openDrawer);
    if (close) close.addEventListener('click', closeDrawer);
    if (overlay) overlay.addEventListener('click', closeDrawer);

    /* Close on nav link tap */
    if (drawer) {
      drawer.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', closeDrawer);
      });
    }

    /* Smooth anchor scroll */
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });

    /* Header glass on scroll */
    const header = document.querySelector('header');
    if (header) {
      window.addEventListener('scroll', () => {
        header.style.borderBottomColor =
          window.scrollY > 55
            ? 'rgba(255, 68, 102, 0.2)'
            : 'rgba(255, 255, 255, 0.08)';
      }, { passive: true });
    }
  }


  /* ═══ LAYER 7 · COMPLETION — Scroll reveal ═══ */

  function initScrollReveal() {
    const reveals = document.querySelectorAll('.reveal');
    if (!reveals.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          /* Fibonacci stagger: each sibling delays by 89ms × index */
          const siblings = entry.target.parentElement.querySelectorAll('.reveal');
          let idx = 0;
          siblings.forEach((s, j) => { if (s === entry.target) idx = j; });
          setTimeout(() => {
            entry.target.classList.add('visible');
          }, idx * 89);
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.15,
      rootMargin: '0px 0px -55px 0px',
    });

    reveals.forEach(el => observer.observe(el));
  }


  /* ═══ DEPTH WORLD — Forced perspective scroll ═══ */

  function initForcedPerspective() {
    const world = document.querySelector('.depth-world');
    if (!world) return;

    /* Apply subtle z-rotation and perspective shift on scroll */
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      const delta = y - lastScroll;
      lastScroll = y;

      /* Very subtle depth wobble — φ-dampened */
      const wobble = Math.sin(y * 0.003) * PHI_INV;
      world.style.transform = `rotateX(${wobble * 0.3}deg) rotateY(${wobble * 0.15}deg)`;
    }, { passive: true });
  }


  /* ═══ BOOT ═══ */

  function boot() {
    /* Layer 1 — Spark (canvases) */
    initStarfield();
    initGameSparks();

    /* Layer 2 — Mirror (parallax) */
    initParallax();

    /* Layer 4 — Form (card tilt) */
    initCardTilt();

    /* Layer 6 — Mind (nav) */
    initNav();

    /* Layer 7 — Completion (scrollreveal, perspective) */
    initScrollReveal();
    initForcedPerspective();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

})();

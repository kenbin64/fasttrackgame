/* ═══════════════════════════════════════════════════════════════════
   KEN'S GAMES — 80s ARCADE MANIFOLD BEHAVIOR v2.0
   ═══════════════════════════════════════════════════════════════════
   z = x · y — every interaction is a manifold surface.
   SVG faces: vector shapes that grow without losing quality.
   Enveloping parallax: multi-depth layers respond to scroll + mouse.
   80s Arcade: neon grid, CRT flicker, synthwave atmosphere.
   ═══════════════════════════════════════════════════════════════════ */

;(function () {
  'use strict';

  const PHI   = 1.618033988749895;
  const PHI_I = 0.618033988749895;
  const TAU   = Math.PI * 2;
  const FIB   = [1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987];

  /* ─── Neon palette ─── */
  const NEON = [
    '#ff2d95',  /* pink   */
    '#00d4ff',  /* blue   */
    '#b24dff',  /* purple */
    '#39ff14',  /* green  */
    '#ffe600',  /* yellow */
    '#ff6b00',  /* orange */
    '#ff073a',  /* red    */
  ];

  /* ─────────────────────────────────────────────────
     SVG FACE FACTORY — Vector shapes, infinite scale
     ───────────────────────────────────────────────── */

  const SVG_NS = 'http://www.w3.org/2000/svg';

  function svgEl(tag, attrs) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    return el;
  }

  /* Create a complete SVG element with viewBox centered at 0,0 */
  function createSVG(size, content, color) {
    const svg = svgEl('svg', {
      viewBox: `-${size} -${size} ${size * 2} ${size * 2}`,
      width: '100%', height: '100%',
    });
    svg.style.filter = `drop-shadow(0 0 8px ${color}44) drop-shadow(0 0 21px ${color}22)`;
    svg.appendChild(content);
    return svg;
  }

  /* Shape 1: Icosahedron wireframe — 12 vertices projected */
  function svgIcosahedron(color, phase) {
    const g = svgEl('g', {});
    const t = (1 + Math.sqrt(5)) / 2;
    const verts = [
      [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
      [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
      [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1],
    ];
    const edges = [
      [0,1],[0,5],[0,7],[0,10],[0,11],[1,5],[1,7],[1,8],[1,9],
      [2,3],[2,4],[2,6],[2,10],[2,11],[3,4],[3,6],[3,8],[3,9],
      [4,5],[4,9],[4,11],[5,9],[5,11],[6,7],[6,8],[6,10],
      [7,8],[7,10],[8,9],[10,11],
    ];
    const s = 22;
    const ca = Math.cos(phase), sa = Math.sin(phase);
    const proj = verts.map(([x, y, z]) => {
      const ry = x * ca - z * sa;
      const rz = x * sa + z * ca;
      return [ry * s, y * s];
    });
    edges.forEach(([a, b]) => {
      g.appendChild(svgEl('line', {
        x1: proj[a][0], y1: proj[a][1],
        x2: proj[b][0], y2: proj[b][1],
        stroke: color, 'stroke-width': 1.5, opacity: 0.6,
      }));
    });
    return createSVG(60, g, color);
  }

  /* Shape 2: Pyramid — 4-face tetrahedron */
  function svgPyramid(color, phase) {
    const g = svgEl('g', {});
    const ca = Math.cos(phase), sa = Math.sin(phase);
    const apex = [0, -35];
    const s = 28;
    const baseVerts = [0, 1, 2].map(i => {
      const a = (i * TAU / 3) + phase * 0.5;
      return [Math.cos(a) * s, 18 + Math.sin(a) * s * 0.35];
    });
    /* Base triangle */
    const basePts = baseVerts.map(p => p.join(',')).join(' ');
    g.appendChild(svgEl('polygon', {
      points: basePts, fill: 'none', stroke: color,
      'stroke-width': 1.5, opacity: 0.5,
    }));
    /* Edges to apex */
    baseVerts.forEach(v => {
      g.appendChild(svgEl('line', {
        x1: apex[0], y1: apex[1], x2: v[0], y2: v[1],
        stroke: color, 'stroke-width': 1.5, opacity: 0.7,
      }));
    });
    /* Face fill */
    g.appendChild(svgEl('polygon', {
      points: `${apex.join(',')  } ${baseVerts[0].join(',')} ${baseVerts[1].join(',')}`,
      fill: color, opacity: 0.06,
    }));
    return createSVG(50, g, color);
  }

  /* Shape 3: Cube wireframe with perspective */
  function svgCube(color, phase) {
    const g = svgEl('g', {});
    const s = 22;
    const ca = Math.cos(phase), sa = Math.sin(phase);
    const cb = Math.cos(phase * PHI_I), sb = Math.sin(phase * PHI_I);
    const raw = [
      [-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],
      [-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1],
    ];
    const proj = raw.map(([x,y,z]) => {
      let rx = x*ca - z*sa, rz = x*sa + z*ca;
      let ry = y*cb - rz*sb; rz = y*sb + rz*cb;
      return [rx*s, ry*s];
    });
    const edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
    edges.forEach(([a,b]) => {
      g.appendChild(svgEl('line', {
        x1:proj[a][0], y1:proj[a][1], x2:proj[b][0], y2:proj[b][1],
        stroke: color, 'stroke-width': 1.5, opacity: 0.55,
      }));
    });
    /* One face filled */
    const face = [0,1,2,3].map(i => proj[i].join(',')).join(' ');
    g.appendChild(svgEl('polygon', { points: face, fill: color, opacity: 0.05 }));
    return createSVG(50, g, color);
  }

  /* Shape 4: Diamond (octahedron) */
  function svgDiamond(color, phase) {
    const g = svgEl('g', {});
    const ca = Math.cos(phase), sa = Math.sin(phase);
    const s = 30;
    const verts = [[0,-1,0],[0,1,0],[1,0,0],[-1,0,0],[0,0,1],[0,0,-1]];
    const proj = verts.map(([x,y,z]) => {
      const rx = x*ca - z*sa;
      return [rx * s, y * s];
    });
    const faces = [[0,2,4],[0,4,3],[0,3,5],[0,5,2],[1,2,4],[1,4,3],[1,3,5],[1,5,2]];
    faces.forEach((f, i) => {
      const pts = f.map(v => proj[v].join(',')).join(' ');
      g.appendChild(svgEl('polygon', {
        points: pts, fill: color, stroke: color,
        'stroke-width': 1, opacity: (i < 4) ? 0.06 : 0.03,
      }));
    });
    return createSVG(50, g, color);
  }

  /* Shape 5: Star — 5-pointed */
  function svgStar(color, phase) {
    const g = svgEl('g', {});
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const r = (i % 2 === 0) ? 32 : 14;
      const a = (i * TAU / 10) - Math.PI / 2 + phase * 0.3;
      pts.push(`${Math.cos(a) * r},${Math.sin(a) * r}`);
    }
    g.appendChild(svgEl('polygon', {
      points: pts.join(' '), fill: color, stroke: color,
      'stroke-width': 1, opacity: 0.08, 'fill-opacity': 0.06,
    }));
    g.appendChild(svgEl('polygon', {
      points: pts.join(' '), fill: 'none', stroke: color,
      'stroke-width': 1.5, opacity: 0.6,
    }));
    return createSVG(50, g, color);
  }

  /* Shape 6: Hexagonal prism */
  function svgHexPrism(color, phase) {
    const g = svgEl('g', {});
    const r = 25, h = 18;
    const top = [], bot = [];
    for (let i = 0; i < 6; i++) {
      const a = (i * TAU / 6) + phase * 0.4;
      const x = Math.cos(a) * r, y = Math.sin(a) * r * 0.5;
      top.push([x, y - h]);
      bot.push([x, y + h * 0.3]);
    }
    /* Top face */
    g.appendChild(svgEl('polygon', {
      points: top.map(p => p.join(',')).join(' '),
      fill: color, stroke: color, 'stroke-width': 1.5,
      opacity: 0.08, 'fill-opacity': 0.06,
    }));
    /* Bottom face */
    g.appendChild(svgEl('polygon', {
      points: bot.map(p => p.join(',')).join(' '),
      fill: 'none', stroke: color, 'stroke-width': 1, opacity: 0.3,
    }));
    /* Vertical edges */
    for (let i = 0; i < 6; i++) {
      g.appendChild(svgEl('line', {
        x1: top[i][0], y1: top[i][1], x2: bot[i][0], y2: bot[i][1],
        stroke: color, 'stroke-width': 1, opacity: 0.4,
      }));
    }
    return createSVG(50, g, color);
  }

  /* Shape 7: Torus ring (circle of circles) */
  function svgRing(color, phase) {
    const g = svgEl('g', {});
    const R = 28, segments = 13;
    for (let i = 0; i < segments; i++) {
      const a = (i * TAU / segments) + phase * 0.3;
      const cx = Math.cos(a) * R;
      const cy = Math.sin(a) * R * 0.45;
      const r  = 5 + Math.sin(a + phase) * 2;
      g.appendChild(svgEl('circle', {
        cx, cy, r,
        fill: 'none', stroke: color, 'stroke-width': 1.2,
        opacity: 0.3 + Math.cos(a) * 0.3,
      }));
    }
    return createSVG(55, g, color);
  }

  const SHAPE_BUILDERS = [
    svgIcosahedron, svgPyramid, svgCube, svgDiamond,
    svgStar, svgHexPrism, svgRing,
  ];


  /* ─────────────────────────────────────────────────
     PARALLAX ENGINE — Enveloping multi-depth layers
     ───────────────────────────────────────────────── */

  let mouseX = 0.5, mouseY = 0.5;                /* 0→1 normalized */
  let scrollY = 0;
  const SHAPES = [];                              /* live shape refs */

  function spawnSVGFaces() {
    const layers = document.querySelectorAll('.parallax-layer');
    if (!layers.length) return;

    const COUNTS = { back: 8, mid: 7, front: 6 };  /* 21 total = Fibonacci */
    const depthNames = ['back', 'mid', 'front'];

    layers.forEach(layer => {
      const depth   = layer.dataset.depth;
      const count   = COUNTS[depth] || 5;
      const dIdx    = depthNames.indexOf(depth);

      for (let i = 0; i < count; i++) {
        const shapeIdx = (i + dIdx * 3) % SHAPE_BUILDERS.length;
        const color    = NEON[(i + dIdx * 2) % NEON.length];
        const phase    = (i * PHI * TAU) % TAU;

        /* Size: φ-scaled, larger in back */
        const baseSize = 34 + (2 - dIdx) * 21;
        const size     = baseSize + Math.sin(i * PHI) * 13;

        /* Position: golden-ratio distributed */
        const x = ((i * PHI_I * 100) % 95) + 2;
        const y = ((i * PHI * 80 + dIdx * 30) % 180) + 5;

        const wrapper = document.createElement('div');
        wrapper.className = 'svg-face';
        wrapper.style.width  = size + 'px';
        wrapper.style.height = size + 'px';
        wrapper.style.left   = x + '%';
        wrapper.style.top    = y + '%';

        const svg = SHAPE_BUILDERS[shapeIdx](color, phase);
        wrapper.appendChild(svg);
        layer.appendChild(wrapper);

        SHAPES.push({
          el: wrapper, svg, depth: dIdx, color,
          baseX: x, baseY: y, phase,
          builder: SHAPE_BUILDERS[shapeIdx],
          size, speed: 0.3 + dIdx * 0.4,
        });
      }
    });

    /* Fade in with Fibonacci stagger */
    SHAPES.forEach((s, i) => {
      const delay = FIB[Math.min(i, FIB.length - 1)] * 8;
      setTimeout(() => s.el.classList.add('visible'), delay);
    });
  }

  /* Refresh SVG faces with new phase (rotation) — keeps them vector-crisp */
  function updateFaces(time) {
    SHAPES.forEach(s => {
      const newPhase = s.phase + time * 0.0003 * (1 + s.depth * 0.3);
      /* Only rebuild SVG every ~200ms for perf */
      if (Math.floor(time / 200) !== Math.floor((time - 16) / 200)) {
        const newSvg = s.builder(s.color, newPhase);
        s.el.replaceChild(newSvg, s.el.firstChild);
        s.svg = newSvg;
      }
    });
  }

  /* Enveloping parallax: shapes drift with mouse + scroll */
  function updateParallax() {
    const cx = (mouseX - 0.5) * 2;  /* -1 → +1 */
    const cy = (mouseY - 0.5) * 2;

    SHAPES.forEach(s => {
      const depthFactor = (3 - s.depth) * 13;    /* deeper = more movement */
      const scrollFactor = (3 - s.depth) * 0.03; /* deeper = slower scroll */
      const dx = cx * depthFactor;
      const dy = cy * depthFactor + scrollY * scrollFactor;
      s.el.style.transform = `translate(${dx}px, ${dy}px)`;
    });

    /* Move the envelope layers themselves for deep parallax */
    document.querySelectorAll('.parallax-layer').forEach(layer => {
      const d = layer.dataset.depth;
      const factor = d === 'back' ? 0.04 : d === 'mid' ? 0.02 : 0.01;
      const mx = cx * factor * 100;
      const my = cy * factor * 100;
      const baseZ = d === 'back' ? -300 : d === 'mid' ? -150 : -50;
      const baseS = d === 'back' ? 1.3 : d === 'mid' ? 1.15 : 1.05;
      layer.style.transform = `translateZ(${baseZ}px) scale(${baseS}) translate(${mx}px, ${my}px)`;
    });
  }


  /* ─────────────────────────────────────────────────
     STARFIELD — φ-distributed neon dots
     ───────────────────────────────────────────────── */

  function initStarfield(canvas) {
    const ctx = canvas.getContext('2d');
    let W, H;
    const STAR_COUNT = 233;
    const stars = [];

    function resize() {
      W = canvas.width  = window.innerWidth;
      H = canvas.height = window.innerHeight;
    }

    function seedStars() {
      stars.length = 0;
      for (let i = 0; i < STAR_COUNT; i++) {
        const fi = (i * PHI_I) % 1;
        stars.push({
          x: fi * W,
          y: ((i * PHI) % 1) * H,
          r: 0.3 + Math.random() * 1.5,
          a: Math.random(),
          speed: 0.05 + Math.random() * 0.15,
          color: NEON[i % NEON.length],
          twinkleOffset: i * PHI,
        });
      }
    }

    function draw(time) {
      ctx.clearRect(0, 0, W, H);
      stars.forEach(s => {
        const twinkle = 0.3 + 0.7 * Math.abs(Math.sin(time * 0.001 * s.speed + s.twinkleOffset));
        ctx.globalAlpha = s.a * twinkle;
        ctx.fillStyle = s.color;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, TAU);
        ctx.fill();
        /* Glow */
        if (s.r > 0.8) {
          ctx.globalAlpha = s.a * twinkle * 0.15;
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r * 3, 0, TAU);
          ctx.fill();
        }
      });
      ctx.globalAlpha = 1;
    }

    resize();
    seedStars();
    window.addEventListener('resize', () => { resize(); seedStars(); });
    return draw;
  }


  /* ─────────────────────────────────────────────────
     NEON GRID FLOOR — 80s Tron-style perspective
     ───────────────────────────────────────────────── */

  function initArcadeFloor(canvas) {
    const ctx = canvas.getContext('2d');
    let W, H;

    function resize() {
      W = canvas.width  = window.innerWidth;
      H = canvas.height = window.innerHeight;
    }

    function draw(time) {
      ctx.clearRect(0, 0, W, H);

      /* Floor only in bottom portion */
      const floorTop = H * 0.65;
      const horizon  = H * 0.45;

      /* Perspective grid lines */
      ctx.save();

      /* Horizontal lines — receding into distance */
      const lineCount = 21;
      for (let i = 0; i < lineCount; i++) {
        const t = i / lineCount;
        const y = horizon + (floorTop - horizon + H * 0.6) * Math.pow(t, 1.8);
        if (y < floorTop - 5) continue;
        const alpha = 0.05 + t * 0.15;
        const scrollOffset = (time * 0.0002 * (1 + t * 0.5)) % 1;
        const yOff = y + scrollOffset * (H * 0.04);

        ctx.strokeStyle = `rgba(178, 77, 255, ${alpha})`;
        ctx.lineWidth = 0.5 + t;
        ctx.beginPath();
        ctx.moveTo(0, yOff);
        ctx.lineTo(W, yOff);
        ctx.stroke();
      }

      /* Vertical lines — converging to vanishing point */
      const vanishX = W / 2 + (mouseX - 0.5) * 60;
      const vertCount = 13;
      for (let i = -vertCount; i <= vertCount; i++) {
        const alpha = 0.03 + (1 - Math.abs(i) / vertCount) * 0.12;
        const baseX = W / 2 + i * (W / (vertCount * 1.5));
        ctx.strokeStyle = `rgba(0, 212, 255, ${alpha})`;
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(vanishX, horizon);
        ctx.lineTo(baseX, H + 50);
        ctx.stroke();
      }

      /* Horizon glow */
      const hGrad = ctx.createLinearGradient(0, horizon - 30, 0, horizon + 80);
      hGrad.addColorStop(0, 'transparent');
      hGrad.addColorStop(0.4, 'rgba(255, 45, 149, 0.06)');
      hGrad.addColorStop(0.6, 'rgba(178, 77, 255, 0.04)');
      hGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = hGrad;
      ctx.fillRect(0, horizon - 30, W, 110);

      ctx.restore();
    }

    resize();
    window.addEventListener('resize', resize);
    return draw;
  }


  /* ─────────────────────────────────────────────────
     CARD TILT — 3D mouse-reactive neon glow
     ───────────────────────────────────────────────── */

  function initCardTilt() {
    document.querySelectorAll('.game-card').forEach(card => {
      card.addEventListener('mousemove', e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width;
        const y = (e.clientY - r.top) / r.height;
        card.style.setProperty('--mx', (x * 100) + '%');
        card.style.setProperty('--my', (y * 100) + '%');
        card.style.setProperty('--rx', ((y - 0.5) * -8) + 'deg');
        card.style.setProperty('--ry', ((x - 0.5) * 8) + 'deg');
      });
      card.addEventListener('mouseleave', () => {
        card.style.setProperty('--rx', '0deg');
        card.style.setProperty('--ry', '0deg');
      });
    });
  }


  /* ─────────────────────────────────────────────────
     NAV — Hamburger drawer + scroll opacity
     ───────────────────────────────────────────────── */

  function initNav() {
    const burger  = document.querySelector('.burger');
    const drawer  = document.querySelector('.drawer');
    const overlay = document.querySelector('.overlay');
    const close   = document.querySelector('.drawer-close');

    if (!burger || !drawer) return;

    function open()  { drawer.classList.add('open'); overlay.classList.add('visible'); }
    function shut()  { drawer.classList.remove('open'); overlay.classList.remove('visible'); }

    burger.addEventListener('click', open);
    close?.addEventListener('click', shut);
    overlay?.addEventListener('click', shut);

    drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', shut));
  }


  /* ─────────────────────────────────────────────────
     SCROLL REVEAL — Fibonacci stagger
     ───────────────────────────────────────────────── */

  function initScrollReveal() {
    const items = document.querySelectorAll('.reveal');
    if (!items.length) return;

    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -55px 0px' });

    items.forEach((el, i) => {
      /* Fibonacci stagger */
      const fib = FIB[Math.min(i, FIB.length - 1)];
      el.style.transitionDelay = (fib * 13) + 'ms';
      obs.observe(el);
    });
  }


  /* ─────────────────────────────────────────────────
     CRT FLICKER — Subtle screen distortion
     ───────────────────────────────────────────────── */

  function initCRTFlicker() {
    const overlay = document.querySelector('.crt-overlay');
    if (!overlay) return;

    setInterval(() => {
      if (Math.random() < 0.05) { /* 5% chance per interval */
        overlay.style.opacity = 0.6 + Math.random() * 0.4;
        setTimeout(() => { overlay.style.opacity = 1; }, 50 + Math.random() * 80);
      }
    }, 377);
  }


  /* ─────────────────────────────────────────────────
     MOUSE TRACKER — Global mouse for parallax + floor
     ───────────────────────────────────────────────── */

  function initMouse() {
    window.addEventListener('mousemove', e => {
      mouseX = e.clientX / window.innerWidth;
      mouseY = e.clientY / window.innerHeight;
    });
    window.addEventListener('scroll', () => {
      scrollY = window.scrollY;
    }, { passive: true });
  }


  /* ─────────────────────────────────────────────────
     ANIMATION LOOP — z = x·y manifold surface
     ───────────────────────────────────────────────── */

  function boot() {
    const starCanvas  = document.getElementById('starfield');
    const floorCanvas = document.getElementById('arcade-scene');

    let drawStars = null;
    let drawFloor = null;

    if (starCanvas)  drawStars = initStarfield(starCanvas);
    if (floorCanvas) drawFloor = initArcadeFloor(floorCanvas);

    spawnSVGFaces();
    initCardTilt();
    initNav();
    initScrollReveal();
    initCRTFlicker();
    initMouse();

    function loop(time) {
      if (drawStars) drawStars(time);
      if (drawFloor) drawFloor(time);
      updateParallax();
      updateFaces(time);
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }

  /* ─── Ignite ─── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

})();

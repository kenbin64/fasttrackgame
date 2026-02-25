/* ═══════════════════════════════════════════════════════════════════
   KEN'S GAMES — MANIFOLD BEHAVIOR
   ═══════════════════════════════════════════════════════════════════
   z = x · y — Behavior emerges from the substrate.
   
   Every constant is φ or Fibonacci.
   Every animation follows the golden ratio.
   Full 3D shape engine: spheres, pyramids, cubes, dice, rings.
   Perspective-projected, gradient-shaded, immersive.
   ═══════════════════════════════════════════════════════════════════ */

;(function manifold() {
  'use strict';

  const PHI = 1.618033988749895;
  const PHI_INV = 0.618033988749895;
  const TAU = Math.PI * 2;
  const FIB = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610];

  /* Genesis palette — game-energy colors */
  const PALETTE = [
    [255, 68, 102],   /* fire red */
    [255, 215, 0],    /* gold */
    [64, 255, 255],   /* neon cyan */
    [155, 89, 182],   /* purple */
    [52, 152, 219],   /* blue */
    [39, 174, 96],    /* green */
    [243, 156, 18],   /* orange */
  ];

  /* Shared mouse state */
  let mx = 0, my = 0;
  document.addEventListener('mousemove', e => {
    mx = (e.clientX / window.innerWidth - 0.5) * 2;
    my = (e.clientY / window.innerHeight - 0.5) * 2;
  });


  /* ═══════════════════════════════════════════════════════════
     3D MATH — perspective projection, rotation, lighting
     ═══════════════════════════════════════════════════════════ */

  function rotX(p, a) {
    const c = Math.cos(a), s = Math.sin(a);
    return [p[0], p[1]*c - p[2]*s, p[1]*s + p[2]*c];
  }
  function rotY(p, a) {
    const c = Math.cos(a), s = Math.sin(a);
    return [p[0]*c + p[2]*s, p[1], -p[0]*s + p[2]*c];
  }
  function rotZ(p, a) {
    const c = Math.cos(a), s = Math.sin(a);
    return [p[0]*c - p[1]*s, p[0]*s + p[1]*c, p[2]];
  }

  function project(p3, cx, cy, fov) {
    const z = p3[2] + fov;
    if (z <= 0) return null;
    const scale = fov / z;
    return { x: cx + p3[0] * scale, y: cy + p3[1] * scale, s: scale, z: p3[2] };
  }

  /* Directional light (top-right-front) */
  function lightIntensity(nx, ny, nz) {
    const lx = 0.4, ly = -0.6, lz = 0.7;
    const len = Math.sqrt(lx*lx + ly*ly + lz*lz);
    const dot = (nx*lx + ny*ly + nz*lz) / len;
    return 0.25 + 0.75 * Math.max(0, dot);
  }


  /* ═══════════════════════════════════════════════════════════
     LAYER 1 · SPARK — Stars + 3D floating game shapes
     ═══════════════════════════════════════════════════════════ */

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
      stars = [];
      for (let i = 0; i < 233; i++) {
        const band = i < 89 ? 0 : i < 178 ? 1 : 2;
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          r: [0.5, 1.0, 1.8][band],
          a: [0.15, 0.35, 0.75][band],
          s: [0.06, 0.13, 0.25][band],
          tw: Math.random() * TAU,
          color: PALETTE[Math.floor(Math.random() * 7)],
          bright: Math.random() > 0.85, /* some are colored */
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      const t = Date.now() * 0.001;
      for (const s of stars) {
        s.y -= s.s;
        if (s.y < -2) { s.y = h + 2; s.x = Math.random() * w; }
        const twinkle = 0.4 + 0.6 * Math.sin(t * PHI + s.tw);
        ctx.globalAlpha = s.a * twinkle;
        if (s.bright) {
          const [r, g, b] = s.color;
          ctx.fillStyle = `rgb(${r},${g},${b})`;
        } else {
          ctx.fillStyle = '#fff';
        }
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, TAU);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      requestAnimationFrame(draw);
    }

    resize();
    createStars();
    draw();
    window.addEventListener('resize', () => { resize(); createStars(); });
  }


  /* ═══════════════════════════════════════════════════════════
     3D SHAPES ENGINE — The immersive game shapes canvas
     
     Renders: gradient spheres, wireframe pyramids, shaded cubes,
     glowing dice, spinning rings, floating diamonds — all
     perspective-projected with φ-governed orbits.
     ═══════════════════════════════════════════════════════════ */

  function initShapes3D() {
    const canvas = document.getElementById('game-sparks');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let w, h;

    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    }

    /* Shape types */
    const SPHERE = 0, PYRAMID = 1, CUBE = 2, DIAMOND = 3, RING = 4, DODECA = 5, DIE = 6;

    /* Create 21 Fibonacci shapes across the scene */
    const shapes = [];
    function createShapes() {
      shapes.length = 0;
      const types = [SPHERE, SPHERE, PYRAMID, CUBE, DIAMOND, RING,
                     SPHERE, DODECA, PYRAMID, CUBE, SPHERE, RING,
                     DIE, SPHERE, DIAMOND, PYRAMID, RING, CUBE,
                     SPHERE, DODECA, DIE];
      for (let i = 0; i < 21; i++) {
        const color = PALETTE[i % 7];
        shapes.push({
          type: types[i],
          /* Orbit in 3D — φ-spaced */
          orbitRadius: 200 + Math.random() * 600,
          orbitSpeed: (0.1 + Math.random() * 0.3) * (i % 2 ? 1 : -1),
          orbitPhase: (i / 21) * TAU * PHI,
          yOffset: (Math.random() - 0.5) * h * 0.9,
          yBob: 20 + Math.random() * 60,
          yBobSpeed: 0.3 + Math.random() * 0.4,
          zBase: -400 + Math.random() * 300,
          size: 18 + Math.random() * 40,
          rotSpeed: [0.3 + Math.random() * 0.5, 0.2 + Math.random() * 0.4, 0.1 + Math.random() * 0.3],
          color: color,
          alpha: 0.25 + Math.random() * 0.45,
          glowSize: 1.2 + Math.random() * 0.8,
        });
      }
    }

    /* ─── Draw a gradient sphere ─── */
    function drawSphere(ctx, px, py, r, color, alpha) {
      const [cr, cg, cb] = color;
      /* Radial gradient — lit from top-left */
      const grad = ctx.createRadialGradient(
        px - r * 0.3, py - r * 0.3, r * 0.05,
        px, py, r
      );
      grad.addColorStop(0, `rgba(${Math.min(255, cr+80)},${Math.min(255, cg+80)},${Math.min(255, cb+80)},${alpha})`);
      grad.addColorStop(0.618, `rgba(${cr},${cg},${cb},${alpha * 0.7})`);
      grad.addColorStop(1, `rgba(${cr>>1},${cg>>1},${cb>>1},${alpha * 0.3})`);
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(px, py, r, 0, TAU);
      ctx.fill();

      /* Specular highlight */
      const spec = ctx.createRadialGradient(
        px - r * 0.35, py - r * 0.35, 0,
        px - r * 0.35, py - r * 0.35, r * 0.5
      );
      spec.addColorStop(0, `rgba(255,255,255,${alpha * 0.6})`);
      spec.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = spec;
      ctx.beginPath();
      ctx.arc(px, py, r, 0, TAU);
      ctx.fill();

      /* Outer glow */
      const glow = ctx.createRadialGradient(px, py, r * 0.8, px, py, r * 2.5);
      glow.addColorStop(0, `rgba(${cr},${cg},${cb},${alpha * 0.15})`);
      glow.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(px, py, r * 2.5, 0, TAU);
      ctx.fill();
    }

    /* ─── Draw a wireframe+shaded pyramid ─── */
    function drawPyramid(ctx, px, py, scale, rx, ry, color, alpha) {
      const [cr, cg, cb] = color;
      const s = 30 * scale;

      /* 4 vertices: apex + 3 base */
      let verts = [
        [0, -s * PHI, 0],            /* apex */
        [-s,  s * 0.5, -s * 0.577],  /* base front-left  */
        [ s,  s * 0.5, -s * 0.577],  /* base front-right */
        [ 0,  s * 0.5,  s * 0.577],  /* base back        */
      ];

      /* Rotate */
      verts = verts.map(v => rotY(rotX(v, rx), ry));

      /* Project */
      const fov = 600;
      const pts = verts.map(v => project(v, px, py, fov));
      if (pts.some(p => !p)) return;

      /* Faces: [apex, b1, b2] */
      const faces = [[0,1,2],[0,2,3],[0,3,1],[1,2,3]];
      const normals = faces.map(f => {
        const a = verts[f[0]], b = verts[f[1]], c = verts[f[2]];
        const ux = b[0]-a[0], uy = b[1]-a[1], uz = b[2]-a[2];
        const vx = c[0]-a[0], vy = c[1]-a[1], vz = c[2]-a[2];
        const nx = uy*vz-uz*vy, ny = uz*vx-ux*vz, nz = ux*vy-uy*vx;
        const len = Math.sqrt(nx*nx+ny*ny+nz*nz)||1;
        return [nx/len, ny/len, nz/len];
      });

      /* Sort back-to-front */
      const faceOrder = [0,1,2,3].sort((a,b) => {
        const za = (verts[faces[a][0]][2]+verts[faces[a][1]][2]+verts[faces[a][2]][2]);
        const zb = (verts[faces[b][0]][2]+verts[faces[b][1]][2]+verts[faces[b][2]][2]);
        return za - zb;
      });

      for (const fi of faceOrder) {
        const f = faces[fi];
        const n = normals[fi];
        if (n[2] > 0.1 && fi !== 3) continue; /* crude backface cull */
        const lit = lightIntensity(n[0], n[1], n[2]);
        const r = Math.floor(cr * lit), g = Math.floor(cg * lit), b = Math.floor(cb * lit);
        ctx.fillStyle = `rgba(${r},${g},${b},${alpha * 0.7})`;
        ctx.strokeStyle = `rgba(${Math.min(255,cr+60)},${Math.min(255,cg+60)},${Math.min(255,cb+60)},${alpha})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(pts[f[0]].x, pts[f[0]].y);
        ctx.lineTo(pts[f[1]].x, pts[f[1]].y);
        ctx.lineTo(pts[f[2]].x, pts[f[2]].y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      }
    }

    /* ─── Draw a shaded cube ─── */
    function drawCube(ctx, px, py, scale, rx, ry, color, alpha) {
      const [cr, cg, cb] = color;
      const s = 22 * scale;

      let verts = [
        [-s,-s,-s],[s,-s,-s],[s,s,-s],[-s,s,-s],
        [-s,-s,s],[s,-s,s],[s,s,s],[-s,s,s],
      ];
      verts = verts.map(v => rotY(rotX(v, rx), ry));

      const fov = 600;
      const pts = verts.map(v => project(v, px, py, fov));
      if (pts.some(p => !p)) return;

      const faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[0,3,7,4],[1,2,6,5]];
      const faceOrder = faces.map((f,i) => i).sort((a,b) => {
        const za = faces[a].reduce((s,vi) => s+verts[vi][2], 0);
        const zb = faces[b].reduce((s,vi) => s+verts[vi][2], 0);
        return za - zb;
      });

      for (const fi of faceOrder) {
        const f = faces[fi];
        const a = verts[f[0]], b2 = verts[f[1]], c = verts[f[2]];
        const ux = b2[0]-a[0], uy = b2[1]-a[1], uz = b2[2]-a[2];
        const vx = c[0]-a[0], vy = c[1]-a[1], vz = c[2]-a[2];
        let nx = uy*vz-uz*vy, ny = uz*vx-ux*vz, nz = ux*vy-uy*vx;
        const len = Math.sqrt(nx*nx+ny*ny+nz*nz)||1;
        nx/=len; ny/=len; nz/=len;

        const lit = lightIntensity(nx, ny, nz);
        const rr = Math.floor(cr * lit), gg = Math.floor(cg * lit), bb = Math.floor(cb * lit);

        /* Gradient across face */
        ctx.fillStyle = `rgba(${rr},${gg},${bb},${alpha * 0.6})`;
        ctx.strokeStyle = `rgba(${Math.min(255,cr+40)},${Math.min(255,cg+40)},${Math.min(255,cb+40)},${alpha * 0.8})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(pts[f[0]].x, pts[f[0]].y);
        for (let i = 1; i < 4; i++) ctx.lineTo(pts[f[i]].x, pts[f[i]].y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      }
    }

    /* ─── Draw a diamond (octahedron) ─── */
    function drawDiamond(ctx, px, py, scale, rx, ry, color, alpha) {
      const [cr, cg, cb] = color;
      const s = 28 * scale;

      let verts = [
        [0,-s*PHI,0],[0,s*PHI,0],
        [-s,0,-s],[s,0,-s],[s,0,s],[-s,0,s],
      ];
      verts = verts.map(v => rotY(rotX(rotZ(v, ry*0.3), rx), ry));

      const fov = 600;
      const pts = verts.map(v => project(v, px, py, fov));
      if (pts.some(p => !p)) return;

      /* 8 triangular faces */
      const faces = [
        [0,2,3],[0,3,4],[0,4,5],[0,5,2],
        [1,3,2],[1,4,3],[1,5,4],[1,2,5],
      ];

      const faceOrder = faces.map((_,i) => i).sort((a,b) => {
        const za = faces[a].reduce((s,vi) => s+verts[vi][2],0);
        const zb = faces[b].reduce((s,vi) => s+verts[vi][2],0);
        return za - zb;
      });

      for (const fi of faceOrder) {
        const f = faces[fi];
        const a = verts[f[0]], b2 = verts[f[1]], c = verts[f[2]];
        const ux = b2[0]-a[0], uy = b2[1]-a[1], uz = b2[2]-a[2];
        const vx = c[0]-a[0], vy = c[1]-a[1], vz = c[2]-a[2];
        let nx = uy*vz-uz*vy, ny = uz*vx-ux*vz, nz = ux*vy-uy*vx;
        const len = Math.sqrt(nx*nx+ny*ny+nz*nz)||1;
        nx/=len; ny/=len; nz/=len;

        const lit = lightIntensity(nx, ny, nz);
        const rr = Math.floor(cr * lit), gg = Math.floor(cg * lit), bb = Math.floor(cb * lit);
        ctx.fillStyle = `rgba(${rr},${gg},${bb},${alpha * 0.7})`;
        ctx.strokeStyle = `rgba(${Math.min(255,cr+50)},${Math.min(255,cg+50)},${Math.min(255,cb+50)},${alpha})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(pts[f[0]].x, pts[f[0]].y);
        ctx.lineTo(pts[f[1]].x, pts[f[1]].y);
        ctx.lineTo(pts[f[2]].x, pts[f[2]].y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      }
    }

    /* ─── Draw a glowing ring (torus silhouette) ─── */
    function drawRing(ctx, px, py, scale, rx, ry, color, alpha) {
      const [cr, cg, cb] = color;
      const R = 30 * scale;   /* major */
      const r = 8 * scale;    /* minor */
      const segs = 34;

      ctx.strokeStyle = `rgba(${cr},${cg},${cb},${alpha * 0.8})`;
      ctx.lineWidth = r * 0.8;
      ctx.lineCap = 'round';

      ctx.beginPath();
      const fov = 600;
      for (let i = 0; i <= segs; i++) {
        const a = (i / segs) * TAU;
        let p = [Math.cos(a) * R, 0, Math.sin(a) * R];
        p = rotY(rotX(p, rx), ry);
        const proj = project(p, px, py, fov);
        if (!proj) continue;
        if (i === 0) ctx.moveTo(proj.x, proj.y);
        else ctx.lineTo(proj.x, proj.y);
      }
      ctx.stroke();

      /* Inner glow */
      const glow = ctx.createRadialGradient(px, py, R * 0.3, px, py, R * 2);
      glow.addColorStop(0, `rgba(${cr},${cg},${cb},${alpha * 0.08})`);
      glow.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(px, py, R * 2, 0, TAU);
      ctx.fill();
    }

    /* ─── Draw a dodecahedron (simplified wireframe) ─── */
    function drawDodeca(ctx, px, py, scale, rx, ry, color, alpha) {
      const [cr, cg, cb] = color;
      const s = 20 * scale;

      /* Dodecahedron vertices from golden ratio */
      const p = PHI * s, q = s / PHI;
      let verts = [
        [s,s,s],[s,s,-s],[s,-s,s],[s,-s,-s],
        [-s,s,s],[-s,s,-s],[-s,-s,s],[-s,-s,-s],
        [0,q,p],[0,q,-p],[0,-q,p],[0,-q,-p],
        [q,p,0],[q,-p,0],[-q,p,0],[-q,-p,0],
        [p,0,q],[p,0,-q],[-p,0,q],[-p,0,-q],
      ];
      verts = verts.map(v => rotY(rotX(v, rx), ry));

      const fov = 600;
      const pts = verts.map(v => project(v, px, py, fov));

      /* Draw edges of the dual — simplified wireframe */
      ctx.strokeStyle = `rgba(${cr},${cg},${cb},${alpha * 0.6})`;
      ctx.lineWidth = 1.2;
      const edges = [
        [0,8],[0,12],[0,16],[8,4],[8,10],[4,14],[4,18],
        [12,1],[12,14],[1,9],[1,17],[14,5],[5,9],[5,19],
        [16,2],[16,17],[2,10],[2,13],[17,3],[3,11],[3,13],
        [10,6],[6,15],[6,18],[18,19],[19,7],[7,11],[7,15],
        [9,11],[13,15],
      ];
      for (const [a,b] of edges) {
        if (!pts[a] || !pts[b]) continue;
        ctx.beginPath();
        ctx.moveTo(pts[a].x, pts[a].y);
        ctx.lineTo(pts[b].x, pts[b].y);
        ctx.stroke();
      }

      /* Center glow */
      const glow = ctx.createRadialGradient(px, py, 0, px, py, s * 2.5);
      glow.addColorStop(0, `rgba(${cr},${cg},${cb},${alpha * 0.1})`);
      glow.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(px, py, s * 2.5, 0, TAU);
      ctx.fill();
    }

    /* ─── Draw a game die (cube with dots) ─── */
    function drawDie(ctx, px, py, scale, rx, ry, color, alpha) {
      /* Draw cube first */
      drawCube(ctx, px, py, scale, rx, ry, color, alpha);
      /* Add pips on the front face */
      const s = 22 * scale;
      let center = [0, 0, s]; /* front face */
      center = rotY(rotX(center, rx), ry);
      const fov = 600;
      const cp = project(center, px, py, fov);
      if (!cp) return;
      const pipR = 3 * cp.s;
      ctx.fillStyle = `rgba(255,255,255,${alpha * 0.8})`;
      /* 5-pip pattern */
      const offsets = [[0,0],[-1,-1],[1,-1],[-1,1],[1,1]];
      for (const [ox, oy] of offsets) {
        ctx.beginPath();
        ctx.arc(cp.x + ox * s * 0.35 * cp.s, cp.y + oy * s * 0.35 * cp.s, pipR, 0, TAU);
        ctx.fill();
      }
    }

    /* ─── Main shape loop ─── */
    function draw() {
      ctx.clearRect(0, 0, w, h);
      const t = Date.now() * 0.001;
      const cx = w / 2, cy = h / 2;
      const scrollY = window.scrollY || 0;

      /* Sort shapes by z for proper overlap */
      const sorted = shapes.map((s, i) => {
        /* φ-spiral orbit */
        const angle = t * s.orbitSpeed * PHI_INV + s.orbitPhase;
        const x = Math.cos(angle) * s.orbitRadius;
        const z = s.zBase + Math.sin(angle) * s.orbitRadius * 0.5;
        const yBob = Math.sin(t * s.yBobSpeed + s.orbitPhase) * s.yBob;
        const y = s.yOffset + yBob - scrollY * 0.15;
        return { ...s, wx: x, wy: y, wz: z, idx: i };
      }).sort((a, b) => a.wz - b.wz);

      for (const s of sorted) {
        /* Mouse-reactive parallax: shapes shift with cursor */
        const parallaxX = mx * (s.wz + 500) * 0.03;
        const parallaxY = my * (s.wz + 500) * 0.02;

        const fov = 800;
        const proj = project([s.wx + parallaxX, s.wy + parallaxY, s.wz], cx, cy, fov);
        if (!proj || proj.x < -100 || proj.x > w + 100 || proj.y < -200 || proj.y > h + 200) continue;

        const sz = s.size * proj.s;
        if (sz < 2 || sz > 300) continue;

        /* Rotation angles — φ-coupled */
        const rx = t * s.rotSpeed[0];
        const ry = t * s.rotSpeed[1];

        ctx.save();
        const drawFns = [drawSphere, drawPyramid, drawCube, drawDiamond, drawRing, drawDodeca, drawDie];
        drawFns[s.type](ctx, proj.x, proj.y, proj.s * (s.size / 28), rx, ry, s.color, s.alpha);
        ctx.restore();
      }

      requestAnimationFrame(draw);
    }

    resize();
    createShapes();
    draw();
    window.addEventListener('resize', () => { resize(); createShapes(); });
  }


  /* ═══ LAYER 4 · FORM — 3D card tilt with tracking glow ═══ */

  function initCardTilt() {
    const cards = document.querySelectorAll('.game-card');
    cards.forEach(card => {
      card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
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


  /* ═══ LAYER 6 · MIND — Navigation & interactions ═══ */

  function initNav() {
    const burger = document.querySelector('.burger');
    const drawer = document.getElementById('drawer');
    const overlay = document.getElementById('overlay');
    const close = drawer ? drawer.querySelector('.drawer-close') : null;

    function openDrawer() {
      if (drawer) drawer.classList.add('open');
      if (overlay) overlay.classList.add('visible');
    }
    function closeDrawer() {
      if (drawer) drawer.classList.remove('open');
      if (overlay) overlay.classList.remove('visible');
    }

    if (burger) burger.addEventListener('click', openDrawer);
    if (close) close.addEventListener('click', closeDrawer);
    if (overlay) overlay.addEventListener('click', closeDrawer);

    if (drawer) {
      drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', closeDrawer));
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

    /* Header glass intensify on scroll */
    const header = document.querySelector('header');
    if (header) {
      window.addEventListener('scroll', () => {
        header.style.borderBottomColor =
          window.scrollY > 55
            ? 'rgba(255, 68, 102, 0.25)'
            : 'rgba(255, 255, 255, 0.08)';
      }, { passive: true });
    }
  }


  /* ═══ LAYER 7 · COMPLETION — Scroll reveal + forced perspective ═══ */

  function initScrollReveal() {
    const reveals = document.querySelectorAll('.reveal');
    if (!reveals.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const siblings = entry.target.parentElement.querySelectorAll('.reveal');
          let idx = 0;
          siblings.forEach((s, j) => { if (s === entry.target) idx = j; });
          setTimeout(() => entry.target.classList.add('visible'), idx * 89);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -55px 0px' });

    reveals.forEach(el => observer.observe(el));
  }

  function initForcedPerspective() {
    const world = document.querySelector('.depth-world');
    if (!world) return;

    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      const wobble = Math.sin(y * 0.002) * PHI_INV;
      world.style.transform =
        `rotateX(${wobble * 0.25}deg) rotateY(${wobble * 0.12}deg)`;
    }, { passive: true });
  }


  /* ═══ BOOT — Ignite all layers ═══ */

  function boot() {
    initStarfield();
    initShapes3D();
    initCardTilt();
    initNav();
    initScrollReveal();
    initForcedPerspective();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

})();

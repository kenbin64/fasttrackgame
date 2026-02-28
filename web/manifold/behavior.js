/* ═══════════════════════════════════════════════════════════════════
   BUTTERFLYFX — BEHAVIOR DIMENSION
   ═══════════════════════════════════════════════════════════════════
   Pure behavior. No presentation. No structure.
   Every constant is φ-derived. Every loop is Fibonacci-bounded.
   
   Replaces 880 lines of inline <script> with ~300 lines of manifold.
   ═══════════════════════════════════════════════════════════════════ */

const PHI = 1.618033988749895;
const PHI_INV = 0.618033988749895;
const GOLDEN_ANGLE = 2.399963229728653;
const FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597];
const GENESIS_HUES = [45, 280, 200, 320, 160, 220, 60];

/* ─── HYPERSPACE STARFIELD ─── */
function initStarfield(canvas) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let w, h, stars = [];

  function resize() {
    w = canvas.width = innerWidth;
    h = canvas.height = innerHeight;
    stars = Array.from({ length: 233 }, (_, i) => {
      const a = i * GOLDEN_ANGLE;
      const r = Math.sqrt(i / 233);
      return {
        x: (0.5 + r * Math.cos(a) * 0.5) * w,
        y: (0.5 + r * Math.sin(a) * 0.5) * h,
        z: (i / 233) * 1597 + 377,
        speed: PHI_INV + (i % 8) * 0.1 * PHI_INV,
        hue: GENESIS_HUES[i % 7]
      };
    });
  }

  function draw() {
    ctx.fillStyle = 'rgba(5,5,8,0.15)';
    ctx.fillRect(0, 0, w, h);
    const cx = w / 2, cy = h / 2;
    for (const s of stars) {
      s.z -= s.speed * PHI;
      if (s.z < 1) {
        const a = Math.random() * Math.PI * 2;
        const r = Math.sqrt(Math.random());
        s.x = (0.5 + r * Math.cos(a) * 0.5) * w;
        s.y = (0.5 + r * Math.sin(a) * 0.5) * h;
        s.z = 1597;
      }
      const d = 610 / s.z;
      const sx = (s.x - cx) * d + cx;
      const sy = (s.y - cy) * d + cy;
      const sz = Math.max(0.5, (1 - s.z / 1597) * PHI * 2);
      const alpha = 1 - s.z / 1597;
      ctx.fillStyle = `hsla(${s.hue},80%,70%,${alpha})`;
      ctx.beginPath();
      ctx.arc(sx, sy, sz, 0, Math.PI * 2);
      ctx.fill();
      // Trail
      const tx = (s.x - cx) * (610 / (s.z + 55)) + cx;
      const ty = (s.y - cy) * (610 / (s.z + 55)) + cy;
      ctx.strokeStyle = `hsla(${s.hue},70%,60%,${alpha * PHI_INV})`;
      ctx.lineWidth = sz * PHI_INV;
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(tx, ty);
      ctx.stroke();
    }
    requestAnimationFrame(draw);
  }

  addEventListener('resize', resize);
  resize();
  draw();
}

/* ─── WIREFRAME MANIFOLD ─── */
function initWireframe(canvas) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let w, h, mx = 0, my = 0, tmx = 0, tmy = 0;

  const vec = (x, y, z) => ({ x, y, z });
  const rotX = (v, a) => { const c = Math.cos(a), s = Math.sin(a); return vec(v.x, v.y*c - v.z*s, v.y*s + v.z*c); };
  const rotY = (v, a) => { const c = Math.cos(a), s = Math.sin(a); return vec(v.x*c + v.z*s, v.y, -v.x*s + v.z*c); };
  const rotZ = (v, a) => { const c = Math.cos(a), s = Math.sin(a); return vec(v.x*c - v.y*s, v.x*s + v.y*c, v.z); };
  const project = (v, cx, cy) => { const f = 800 / (800 + v.z + 100); return { x: v.x*f + cx, y: v.y*f + cy, s: f }; };

  // Shape library — vertices + edges encoded
  const SHAPES = {
    dodecahedron: (() => {
      const p = PHI, ip = PHI_INV;
      return {
        v: [[1,1,1],[1,1,-1],[1,-1,1],[1,-1,-1],[-1,1,1],[-1,1,-1],[-1,-1,1],[-1,-1,-1],
            [0,ip,p],[0,ip,-p],[0,-ip,p],[0,-ip,-p],[ip,p,0],[ip,-p,0],[-ip,p,0],[-ip,-p,0],
            [p,0,ip],[p,0,-ip],[-p,0,ip],[-p,0,-ip]],
        e: [[0,8],[8,4],[4,14],[14,12],[12,0],[0,16],[16,2],[2,10],[10,8],[4,18],[18,6],[6,10],
            [14,5],[5,19],[19,18],[12,1],[1,17],[17,16],[2,13],[13,3],[3,17],[6,15],[15,7],[7,19],
            [5,9],[9,1],[3,11],[11,9],[7,11],[13,15]]
      };
    })(),
    cube: {
      v: [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],
      e: [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    },
    octahedron: {
      v: [[0,-1.5,0],[0,1.5,0],[-1.5,0,0],[1.5,0,0],[0,0,-1.5],[0,0,1.5]],
      e: [[0,2],[0,3],[0,4],[0,5],[1,2],[1,3],[1,4],[1,5],[2,4],[4,3],[3,5],[5,2]]
    }
  };

  const COLORS = [
    [255,170,34],[136,85,255],[64,255,255],[255,85,170],[96,255,144],[100,120,255],[255,215,0]
  ];

  let shapes = [];

  function resize() {
    w = canvas.width = innerWidth;
    h = canvas.height = innerHeight;
    mx = tmx = w / 2;
    my = tmy = h / 2;
    shapes = [];
    const types = Object.keys(SHAPES);
    // Golden angle positions around viewport — Fibonacci sizes
    const pos = [
      [-0.15,-0.09,233,0],[1.15,-0.09,377,0],[-0.09,1.09,233,0],[1.09,1.09,233,0],
      [0.5,-0.15,144,1],[-0.12,0.5,233,1],[1.12,0.5,144,1],[0.5,1.12,144,1],
      [0.236,0.309,89,2],[0.764,0.691,89,2]
    ];
    pos.forEach(([px,py,size,layer], i) => {
      const def = SHAPES[types[i % types.length]];
      shapes.push({
        verts: def.v.map(v => vec(v[0]*size, v[1]*size, v[2]*size)),
        edges: def.e, x: px*w, y: py*h, ox: px*w, oy: py*h,
        vx: 0, vy: 0, rx: Math.random()*6.28, ry: Math.random()*6.28, rz: Math.random()*6.28,
        rvx: (Math.random()-0.5)*0.003*PHI_INV, rvy: (Math.random()-0.5)*0.003*PHI_INV, rvz: (Math.random()-0.5)*0.002*PHI_INV,
        color: COLORS[i % 7], layer, opacity: 0.144 + layer*0.055,
        bp: Math.random()*6.28, bs: 0.005*PHI_INV + Math.random()*0.003*PHI_INV
      });
    });
  }

  function animate() {
    mx += (tmx - mx) * 0.05;
    my += (tmy - my) * 0.05;
    ctx.clearRect(0, 0, w, h);

    for (const s of shapes) {
      s.bp += s.bs;
      const dx = mx - s.x, dy = my - s.y;
      const dist = Math.sqrt(dx*dx + dy*dy) || 1;
      const gf = Math.min(1, 377/dist) * (1 - s.layer*0.2);
      s.vx += (dx/dist)*0.013*gf + (s.ox - s.x)*0.005;
      s.vy += (dy/dist)*0.013*gf + (s.oy - s.y)*0.005;
      s.vx *= 0.96; s.vy *= 0.96;
      const sp = Math.sqrt(s.vx*s.vx + s.vy*s.vy);
      if (sp > PHI) { s.vx = s.vx/sp*PHI; s.vy = s.vy/sp*PHI; }
      s.x += s.vx; s.y += s.vy;
      const rm = 1 + gf*0.5;
      s.rx += s.rvx*rm; s.ry += s.rvy*rm; s.rz += s.rvz*rm;

      const breathe = 1 + Math.sin(s.bp)*0.03;
      const proj = s.verts.map(v => {
        let t = vec(v.x*breathe, v.y*breathe, v.z*breathe);
        t = rotX(t, s.rx); t = rotY(t, s.ry); t = rotZ(t, s.rz);
        return project(vec(t.x + s.x - w/2, t.y + s.y - h/2, t.z + s.layer*144), w/2, h/2);
      });

      const prox = Math.max(0, 1 - dist/610) * PHI_INV;
      const alpha = s.opacity*(1 - s.layer*0.144) + prox;
      const [r,g,b] = s.color;
      ctx.strokeStyle = `rgba(${r},${g},${b},${alpha})`;
      ctx.lineWidth = 1 + (2-s.layer)*0.5;
      ctx.shadowColor = `rgba(${r},${g},${b},${alpha*PHI_INV})`;
      ctx.shadowBlur = 8 + prox*21;

      for (const [a,b2] of s.edges) {
        if (a < proj.length && b2 < proj.length) {
          ctx.beginPath();
          ctx.moveTo(proj[a].x, proj[a].y);
          ctx.lineTo(proj[b2].x, proj[b2].y);
          ctx.stroke();
        }
      }
      ctx.shadowBlur = 0;
    }
    requestAnimationFrame(animate);
  }

  addEventListener('mousemove', e => { tmx = e.clientX; tmy = e.clientY; });
  addEventListener('touchmove', e => { if(e.touches[0]) { tmx = e.touches[0].clientX; tmy = e.touches[0].clientY; } });
  addEventListener('resize', resize);
  resize();
  animate();
}

/* ─── MANIFOLD z=xy CANVAS ─── */
function initManifold(canvas) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = 450; canvas.height = 380;
  const W = 450, H = 380;
  let angle = 0, dragging = false, lastX = 0, dragOff = 0;
  const S = 1.1, CAM_Z = -5.5, FOV = Math.PI/4;

  canvas.addEventListener('mousedown', e => { dragging = true; lastX = e.clientX; canvas.style.cursor = 'grabbing'; });
  canvas.addEventListener('mousemove', e => { if(dragging) { dragOff += (e.clientX-lastX)*0.01; lastX = e.clientX; } });
  canvas.addEventListener('mouseup', () => { dragging = false; canvas.style.cursor = 'grab'; });
  canvas.addEventListener('mouseleave', () => { dragging = false; canvas.style.cursor = 'grab'; });
  canvas.addEventListener('touchstart', e => { e.preventDefault(); dragging = true; lastX = e.touches[0].clientX; });
  canvas.addEventListener('touchmove', e => { if(dragging) { e.preventDefault(); dragOff += (e.touches[0].clientX-lastX)*0.01; lastX = e.touches[0].clientX; } });
  canvas.addEventListener('touchend', () => { dragging = false; });
  canvas.style.cursor = 'grab';

  function proj(x, y, z) {
    const r = angle + dragOff, c = Math.cos(r), s = Math.sin(r);
    const rx = x*c - z*s, rz = x*s + z*c, dz = rz - CAM_Z;
    if (dz <= 0.1) return { x: -1e3, y: -1e3, z: dz, s: 0 };
    const sc = 1 / (dz * Math.tan(FOV/2));
    return { x: W/2 + rx*sc*H/2, y: H/2 - y*sc*H/2, z: dz, s: sc };
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    const items = [];
    // Cube edges
    const V = [[-S,-S,-S],[S,-S,-S],[S,S,-S],[-S,S,-S],[-S,-S,S],[S,-S,S],[S,S,S],[-S,S,S]];
    const E = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
    const pv = V.map(v => proj(...v));
    E.forEach(([a,b]) => {
      const p1 = pv[a], p2 = pv[b], az = (p1.z+p2.z)/2;
      items.push({ t: 'e', p1, p2, z: az });
    });
    // Saddle surface z=xy/S
    const G = 45, step = 2*S/G;
    for (let i = 0; i <= G; i++) for (let j = 0; j <= G; j++) {
      const x = -S+i*step, y = -S+j*step, z = x*y/S;
      const p = proj(x, y, z);
      items.push({ t: 'd', p, z: p.z });
    }
    // Axes
    const ax1 = proj(-S,0,0), ax2 = proj(S,0,0), ay1 = proj(0,-S,0), ay2 = proj(0,S,0);
    items.push({ t: 'ax', p1: ax1, p2: ax2, z: (ax1.z+ax2.z)/2+0.01, c: '0,255,255' });
    items.push({ t: 'ax', p1: ay1, p2: ay2, z: (ay1.z+ay2.z)/2+0.01, c: '100,255,150' });

    items.sort((a,b) => b.z - a.z);
    for (const d of items) {
      if (d.t === 'e') {
        ctx.strokeStyle = 'rgba(100,180,255,0.7)'; ctx.lineWidth = 1.5; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(d.p1.x, d.p1.y); ctx.lineTo(d.p2.x, d.p2.y); ctx.stroke();
      } else if (d.t === 'd') {
        const sz = Math.max(1.2, 2.5*d.p.s*1.5), a = 0.4+0.5*Math.min(1,d.p.s*0.8);
        ctx.fillStyle = `rgba(180,100,255,${a})`; ctx.beginPath(); ctx.arc(d.p.x, d.p.y, sz, 0, Math.PI*2); ctx.fill();
      } else if (d.t === 'ax') {
        ctx.strokeStyle = `rgba(${d.c},0.9)`; ctx.lineWidth = 2; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(d.p1.x, d.p1.y); ctx.lineTo(d.p2.x, d.p2.y); ctx.stroke();
      }
    }
    const lp = proj(0,0,0);
    ctx.fillStyle = 'rgba(0,255,100,0.95)'; ctx.font = 'bold 11px Courier New';
    ctx.textAlign = 'center'; ctx.fillText('z = xy', lp.x, lp.y-8);
    if (!dragging) angle += 0.006;
    requestAnimationFrame(draw);
  }
  draw();
}

/* ─── MOBILE NAV ─── */
function initNav() {
  const burger = document.querySelector('.burger');
  const drawer = document.querySelector('.drawer');
  const overlay = document.querySelector('.overlay');
  const close = document.querySelector('.drawer-close');
  if (!burger) return;

  const open = () => { drawer.classList.add('open'); overlay.classList.add('visible'); document.body.style.overflow = 'hidden'; };
  const shut = () => { drawer.classList.remove('open'); overlay.classList.remove('visible'); document.body.style.overflow = ''; };

  burger.addEventListener('click', open);
  close?.addEventListener('click', shut);
  overlay?.addEventListener('click', shut);
  drawer?.querySelectorAll('a').forEach(a => a.addEventListener('click', shut));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') shut(); });
}

/* ─── HOW IT WORKS OVERLAY ─── */
function initHIW() {
  const toggle = document.querySelector('.hiw-toggle');
  const panel = document.querySelector('.hiw-panel');
  const close = panel?.querySelector('.close');
  if (!toggle || !panel) return;

  const flip = () => panel.classList.toggle('open');
  toggle.addEventListener('click', flip);
  close?.addEventListener('click', flip);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && panel.classList.contains('open')) flip(); });

  // Tabs
  panel.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      panel.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      panel.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`section-${tab.dataset.section}`)?.classList.add('active');
    });
  });
}

/* ─── SCROLL REVEAL — Fibonacci stagger ─── */
function initReveal() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 55);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}

/* ─── PARALLAX (φ-scaled scroll) ─── */
function initParallax() {
  const shapes = document.querySelectorAll('.mirror > *');
  if (!shapes.length) return;
  let scrollY = 0;

  addEventListener('scroll', () => {
    scrollY = window.scrollY;
    shapes.forEach((s, i) => {
      const speed = 0.034 + i * 0.021 * PHI_INV;
      const y = scrollY * speed;
      const rot = scrollY * 0.021 * (i % 2 ? -1 : 1);
      s.style.transform = `translateY(${y}px) rotate(${rot}deg)`;
    });
  });

  if (innerWidth > 768) {
    const fibI = [13, 21, 34, 55];
    addEventListener('mousemove', e => {
      const mx = (e.clientX / innerWidth - 0.5) * 2;
      const my = (e.clientY / innerHeight - 0.5) * 2;
      shapes.forEach((s, i) => {
        const intensity = fibI[i % 4];
        const sy = scrollY * (0.034 + i * 0.021 * PHI_INV);
        s.style.transform = `translate(${mx*intensity}px, ${my*intensity + sy}px) rotate(${mx*8.5}deg)`;
      });
    });
  }
}

/* ─── HOLODECK CARD GLOW ─── */
function initCardGlow() {
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100) + '%');
      card.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100) + '%');
    });
  });
}

/* ═══ MANIFEST — Boot the manifold ═══ */
document.addEventListener('DOMContentLoaded', () => {
  initStarfield(document.getElementById('hyperspace'));
  initWireframe(document.getElementById('wireframe'));
  initManifold(document.getElementById('manifoldCanvas'));
  initNav();
  initHIW();
  initReveal();
  initParallax();
  initCardGlow();
});

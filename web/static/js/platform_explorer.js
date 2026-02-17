// ================================================================
// ButterflyFX Dimensional Platform Explorer
// "Content exists in n-dimensional space"
// ================================================================

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const contentContainer = document.getElementById('content-container');

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

// ========================
// Platform Data
// ========================

const platformData = {
    name: 'ButterflyFX / DimensionsOS',
    version: '1.0.0',
    author: 'Kenneth Bingham',
    license: 'CC BY 4.0 (Infrastructure) / Proprietary (Apps)',
    
    stats: {
        helixLevels: 7,
        dimensions: 4,
        tesseractVertices: 16,
        tesseractEdges: 32,
        osiLayers: 7,
        manifoldEndpoints: 8
    },
    
    levels: [
        { num: 1, name: 'POINT', osi: 'Physical', desc: 'Singular data element', color: '#ff6464' },
        { num: 2, name: 'LINE', osi: 'Data Link', desc: 'Linear sequence / timeline', color: '#ffb464' },
        { num: 3, name: 'PLANE', osi: 'Network', desc: '2D grid / traditional layout', color: '#e0e060' },
        { num: 4, name: 'VOLUME', osi: 'Transport', desc: '3D spatial navigation', color: '#64ff64' },
        { num: 5, name: 'TIME', osi: 'Session', desc: '4D manifold with temporal axis', color: '#64c8ff' },
        { num: 6, name: 'PARALLEL', osi: 'Presentation', desc: 'Branching / alternate states', color: '#9664ff' },
        { num: 7, name: 'META', osi: 'Application', desc: 'Observer / system overview', color: '#ff64c8' }
    ],
    
    features: [
        { title: 'Dimensional Addressing', desc: 'Content addressed by (x, y, z, w) coordinates instead of URLs' },
        { title: 'Manifold Transport', desc: 'OSI layers map 1:1 to helix levels for unified networking' },
        { title: 'Mathematical Payloads', desc: 'Send functions, not samples — the model IS the payload' },
        { title: 'Substate Persistence', desc: 'Database stores dimensional substates, not rows' },
        { title: 'Helix Navigation', desc: '7-level dimensional hierarchy for any data structure' },
        { title: 'Tesseract Visualization', desc: '4D hypercube projection for data exploration' }
    ],
    
    timeline: [
        { year: '2024', event: 'Dimensional primitives defined' },
        { year: '2025 Q1', event: 'Helix transport layer' },
        { year: '2025 Q2', event: 'OSI-Manifold mapping' },
        { year: '2025 Q3', event: 'Server architecture' },
        { year: '2026 Q1', event: 'DimensionsOS platform' },
        { year: 'Future', event: 'Global manifold network' }
    ],
    
    branches: [
        { name: 'Core Kernel', desc: 'Pure dimensional primitives', items: ['Vec4', 'Manifold', 'Helix', 'Tesseract'] },
        { name: 'Infrastructure', desc: 'Server & networking', items: ['DimensionalServer', 'OSI-Manifold', 'ManifoldRouter'] },
        { name: 'Applications', desc: 'User-facing tools', items: ['4D Explorer', 'Substrate Editor', 'Seed Manager'] }
    ]
};

// ========================
// Level State
// ========================

let currentLevel = 5;
let time = 0;
let rotXW = 0;
let rotYW = 0;

// ========================
// 4D Math
// ========================

class Vec4 {
    constructor(x=0, y=0, z=0, w=0) { this.x=x; this.y=y; this.z=z; this.w=w; }
    add(v) { return new Vec4(this.x+v.x, this.y+v.y, this.z+v.z, this.w+v.w); }
    sub(v) { return new Vec4(this.x-v.x, this.y-v.y, this.z-v.z, this.w-v.w); }
    mul(s) { return new Vec4(this.x*s, this.y*s, this.z*s, this.w*s); }
    project3D(d=2) {
        const s = d / (d - this.w);
        return { x: this.x*s, y: this.y*s, z: this.z*s, scale: s, w: this.w };
    }
}

function rotateXW(v, a) {
    const c=Math.cos(a), s=Math.sin(a);
    return new Vec4(v.x*c - v.w*s, v.y, v.z, v.x*s + v.w*c);
}

function rotateYW(v, a) {
    const c=Math.cos(a), s=Math.sin(a);
    return new Vec4(v.x, v.y*c - v.w*s, v.z, v.y*s + v.w*c);
}

function rotateXY(v, a) {
    const c=Math.cos(a), s=Math.sin(a);
    return new Vec4(v.x*c - v.y*s, v.x*s + v.y*c, v.z, v.w);
}

// ========================
// Geometry
// ========================

class Tesseract {
    constructor(size=1) {
        this.size = size;
        this.vertices = [];
        this.edges = [];
        for (let w=-1; w<=1; w+=2)
            for (let z=-1; z<=1; z+=2)
                for (let y=-1; y<=1; y+=2)
                    for (let x=-1; x<=1; x+=2)
                        this.vertices.push(new Vec4(x*size, y*size, z*size, w*size));
        
        for (let i=0; i<16; i++) {
            for (let j=i+1; j<16; j++) {
                const v1=this.vertices[i], v2=this.vertices[j];
                let diff = 0;
                if (v1.x !== v2.x) diff++;
                if (v1.y !== v2.y) diff++;
                if (v1.z !== v2.z) diff++;
                if (v1.w !== v2.w) diff++;
                if (diff === 1) this.edges.push([i, j]);
            }
        }
    }
}

class Cube {
    constructor(size=1) {
        this.vertices = [];
        this.edges = [];
        for (let z=-1; z<=1; z+=2)
            for (let y=-1; y<=1; y+=2)
                for (let x=-1; x<=1; x+=2)
                    this.vertices.push({x: x*size, y: y*size, z: z*size});
        
        for (let i=0; i<8; i++) {
            for (let j=i+1; j<8; j++) {
                const v1=this.vertices[i], v2=this.vertices[j];
                let diff = 0;
                if (v1.x !== v2.x) diff++;
                if (v1.y !== v2.y) diff++;
                if (v1.z !== v2.z) diff++;
                if (diff === 1) this.edges.push([i, j]);
            }
        }
    }
}

const tesseract = new Tesseract(0.8);
const cube = new Cube(1);

// ========================
// Camera
// ========================

const camera = {
    distance: 5,
    rotX: 0.3,
    rotY: 0.5,
    
    project(p) {
        let {x, y, z} = p;
        const cosY = Math.cos(this.rotY), sinY = Math.sin(this.rotY);
        const x1 = x*cosY - z*sinY, z1 = x*sinY + z*cosY;
        const cosX = Math.cos(this.rotX), sinX = Math.sin(this.rotX);
        const y1 = y*cosX - z1*sinX, z2 = y*sinX + z1*cosX;
        const scale = this.distance / (this.distance - z2);
        return {
            x: x1 * scale * 150 + canvas.width/2,
            y: -y1 * scale * 150 + canvas.height/2,
            z: z2,
            scale: scale * (p.scale || 1)
        };
    }
};

// ========================
// Mouse interaction
// ========================

let isDragging = false, lastMouseX = 0, lastMouseY = 0;

canvas.addEventListener('mousedown', e => {
    isDragging = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
});

canvas.addEventListener('mousemove', e => {
    if (isDragging) {
        camera.rotY += (e.clientX - lastMouseX) * 0.01;
        camera.rotX += (e.clientY - lastMouseY) * 0.01;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
    }
});

canvas.addEventListener('mouseup', () => isDragging = false);
canvas.addEventListener('mouseleave', () => isDragging = false);

canvas.addEventListener('wheel', e => {
    camera.distance = Math.max(2, Math.min(10, camera.distance + e.deltaY * 0.01));
    e.preventDefault();
}, { passive: false });

// Time slider
const timeSlider = document.getElementById('time-slider');
const timeValue = document.getElementById('time-value');

timeSlider.addEventListener('input', e => {
    rotXW = parseFloat(e.target.value) * Math.PI;
    timeValue.textContent = `W: ${parseFloat(e.target.value).toFixed(2)}`;
});

// ========================
// Level Switching
// ========================

function setLevel(level) {
    currentLevel = level;
    
    // Update UI
    document.querySelectorAll('.helix-level').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.level) === level);
    });
    
    const levelInfo = platformData.levels[level - 1];
    document.getElementById('level-title').textContent = 
        `Level ${level}: ${levelInfo.name} — ${levelInfo.desc}`;
    
    // Update dimension badges
    const dims = ['dim-x', 'dim-y', 'dim-z', 'dim-w'];
    const activeCount = Math.min(level, 4);
    dims.forEach((id, i) => {
        const el = document.getElementById(id);
        el.classList.toggle('active', i < activeCount || (level >= 5 && i === 3));
    });
    
    // Update coordinate display
    const rows = ['row-x', 'row-y', 'row-z', 'row-w'];
    rows.forEach((id, i) => {
        document.getElementById(id).classList.toggle('hidden', 
            (level === 1 && i > 0) ||
            (level === 2 && i > 1) ||
            (level === 3 && i > 1) ||
            (level === 4 && i > 2) ||
            (level < 5 && i === 3)
        );
    });
    
    // Time slider visibility
    document.getElementById('time-control').classList.toggle('hidden', level < 5);
    
    // Update nav hint
    const hints = {
        1: 'Single data point — the atomic unit of dimensional space',
        2: 'Drag along timeline • Click points to explore',
        3: 'Scroll to explore • Click cards for details',
        4: 'Drag to rotate 3D cube • Scroll to zoom',
        5: 'Drag to rotate • Slider controls W (4th dimension)',
        6: 'Compare parallel branches of the platform',
        7: 'Observe the complete system architecture'
    };
    document.getElementById('nav-hint').textContent = hints[level];
    
    // Render level content
    renderLevelContent(level);
}

// ========================
// Content Renderers
// ========================

function renderLevelContent(level) {
    contentContainer.innerHTML = '';
    contentContainer.className = '';
    
    switch(level) {
        case 1: renderLevel1(); break;
        case 2: renderLevel2(); break;
        case 3: renderLevel3(); break;
        case 4: 
        case 5: renderLevel4or5(); break;
        case 6: renderLevel6(); break;
        case 7: renderLevel7(); break;
    }
}

function renderLevel1() {
    contentContainer.className = 'level-1-layout';
    contentContainer.innerHTML = `
        <div class="content-panel center">
            <h2>POINT — Singular Focus</h2>
            <p>At Level 1, we observe a single data point. This is the atomic unit of dimensional space — 
            a coordinate with a value.</p>
            <div class="stat"><span class="stat-label">Platform</span><span class="stat-value">${platformData.name}</span></div>
            <div class="stat"><span class="stat-label">Version</span><span class="stat-value">${platformData.version}</span></div>
            <div class="stat"><span class="stat-label">Author</span><span class="stat-value">${platformData.author}</span></div>
            <div class="stat"><span class="stat-label">License</span><span class="stat-value">CC BY 4.0</span></div>
            <div class="stat"><span class="stat-label">Coordinate</span><span class="stat-value">(0, 0, 0, 0)</span></div>
            <h3>Philosophy</h3>
            <p>"A point contains infinite potential — all higher dimensions emerge from this singularity."</p>
        </div>
    `;
}

function renderLevel2() {
    contentContainer.innerHTML = `
        <div id="timeline"></div>
    `;
    const timeline = document.getElementById('timeline');
    
    platformData.timeline.forEach((item, i) => {
        const pct = (i / (platformData.timeline.length - 1)) * 100;
        const point = document.createElement('div');
        point.className = 'timeline-point';
        point.style.left = `${pct}%`;
        point.innerHTML = `<div class="timeline-label">${item.year}<br>${item.event}</div>`;
        timeline.appendChild(point);
    });
}

function renderLevel3() {
    contentContainer.className = 'level-3-layout';
    contentContainer.style.display = 'grid';
    contentContainer.style.pointerEvents = 'auto';
    
    platformData.features.forEach(feature => {
        const card = document.createElement('div');
        card.className = 'grid-card';
        card.innerHTML = `<h3>${feature.title}</h3><p>${feature.desc}</p>`;
        contentContainer.appendChild(card);
    });
}

function renderLevel4or5() {
    // 3D/4D visualization handled by canvas
    contentContainer.innerHTML = '';
}

function renderLevel6() {
    contentContainer.innerHTML = `<div class="branch-container"></div>`;
    const container = contentContainer.querySelector('.branch-container');
    
    platformData.branches.forEach((branch, i) => {
        const classes = ['branch-a', 'branch-b', 'branch-c'];
        const el = document.createElement('div');
        el.className = `branch ${classes[i]}`;
        el.innerHTML = `
            <h3 style="color: ${platformData.levels[i*2].color}">${branch.name}</h3>
            <p>${branch.desc}</p>
            <ul>${branch.items.map(item => `<li>${item}</li>`).join('')}</ul>
        `;
        container.appendChild(el);
    });
}

function renderLevel7() {
    contentContainer.innerHTML = `
        <div class="meta-view">
            <div class="meta-diagram">
                <h2>ButterflyFX System Architecture</h2>
                <div class="architecture-layers">
                    ${platformData.levels.map(l => `
                        <div class="arch-layer l${l.num}">
                            <div class="layer-num">${l.num}</div>
                            <div class="layer-info">
                                <div class="layer-name">${l.name}</div>
                                <div class="layer-desc">${l.desc}</div>
                                <div class="layer-osi">OSI: ${l.osi} Layer</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

// ========================
// Render Loop
// ========================

function render() {
    ctx.fillStyle = '#0a0a12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    time += 0.016;
    
    // Auto-rotate W slightly
    if (!isDragging && currentLevel >= 5) {
        rotYW = Math.sin(time * 0.3) * 0.15;
    }
    
    // Draw based on level
    if (currentLevel === 1) {
        drawPoint();
    } else if (currentLevel === 2) {
        drawLine();
    } else if (currentLevel === 3) {
        drawPlane();
    } else if (currentLevel === 4) {
        drawCube();
    } else if (currentLevel === 5) {
        drawTesseract();
    } else if (currentLevel === 6) {
        drawParallel();
    } else if (currentLevel === 7) {
        drawMeta();
    }
    
    updateCoordinates();
    requestAnimationFrame(render);
}

function drawPoint() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // Pulsing glow
    const pulse = 0.8 + Math.sin(time * 2) * 0.2;
    const size = 30 * pulse;
    
    const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, size * 3);
    gradient.addColorStop(0, 'rgba(255, 100, 100, 1)');
    gradient.addColorStop(0.5, 'rgba(255, 100, 100, 0.3)');
    gradient.addColorStop(1, 'rgba(255, 100, 100, 0)');
    
    ctx.beginPath();
    ctx.arc(cx, cy, size * 3, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();
    
    ctx.beginPath();
    ctx.arc(cx, cy, size * 0.5, 0, Math.PI * 2);
    ctx.fillStyle = '#ff6464';
    ctx.fill();
}

function drawLine() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const len = 300;
    
    // Animated line
    ctx.beginPath();
    ctx.moveTo(cx - len, cy);
    ctx.lineTo(cx + len, cy);
    
    const gradient = ctx.createLinearGradient(cx - len, 0, cx + len, 0);
    gradient.addColorStop(0, '#4060ff');
    gradient.addColorStop(0.5, '#ffb464');
    gradient.addColorStop(1, '#ff4080');
    
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 4;
    ctx.stroke();
    
    // Moving point
    const pos = Math.sin(time) * len;
    ctx.beginPath();
    ctx.arc(cx + pos, cy, 10, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
}

function drawPlane() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const size = 200;
    
    // Grid
    ctx.strokeStyle = 'rgba(224, 224, 96, 0.3)';
    ctx.lineWidth = 1;
    
    for (let x = -5; x <= 5; x++) {
        ctx.beginPath();
        ctx.moveTo(cx + x * 40, cy - size);
        ctx.lineTo(cx + x * 40, cy + size);
        ctx.stroke();
    }
    for (let y = -5; y <= 5; y++) {
        ctx.beginPath();
        ctx.moveTo(cx - size, cy + y * 40);
        ctx.lineTo(cx + size, cy + y * 40);
        ctx.stroke();
    }
    
    // Border
    ctx.strokeStyle = '#e0e060';
    ctx.lineWidth = 2;
    ctx.strokeRect(cx - size, cy - size, size * 2, size * 2);
}

function drawCube() {
    const projected = cube.vertices.map(v => camera.project(v));
    
    // Edges
    cube.edges.forEach(([i, j]) => {
        const p1 = projected[i], p2 = projected[j];
        const alpha = 0.3 + (p1.z + p2.z + 2) * 0.15;
        
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = `rgba(100, 255, 100, ${Math.max(0.2, alpha)})`;
        ctx.lineWidth = 2;
        ctx.stroke();
    });
    
    // Vertices
    projected.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 5 * p.scale, 0, Math.PI * 2);
        ctx.fillStyle = '#64ff64';
        ctx.fill();
    });
}

function drawTesseract() {
    // Transform vertices
    const vertices4D = tesseract.vertices.map(v => {
        let t = v;
        t = rotateXY(t, time * 0.1);
        t = rotateXW(t, rotXW);
        t = rotateYW(t, rotYW);
        return t;
    });
    
    // Project
    const projected = vertices4D.map(v => {
        const v3D = v.project3D(2.5);
        return camera.project(v3D);
    });
    
    // Draw edges sorted by depth
    const sortedEdges = [...tesseract.edges].sort((a, b) => {
        return (projected[a[0]].z + projected[a[1]].z) - (projected[b[0]].z + projected[b[1]].z);
    });
    
    sortedEdges.forEach(([i, j]) => {
        const p1 = projected[i], p2 = projected[j];
        const w = (vertices4D[i].w + vertices4D[j].w) / 2;
        
        const r = Math.floor(100 + (w + 1) * 77);
        const g = Math.floor(80 - Math.abs(w) * 30);
        const b = Math.floor(255 - (w + 1) * 50);
        const alpha = 0.3 + (p1.z + p2.z + 2) * 0.15;
        
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${Math.max(0.1, Math.min(1, alpha))})`;
        ctx.lineWidth = 1.5 * (p1.scale + p2.scale) / 2;
        ctx.stroke();
    });
    
    // Draw vertices
    projected.forEach((p, i) => {
        const w = vertices4D[i].w;
        const size = 3 * p.scale;
        const hue = 220 + w * 40;
        
        const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, size * 3);
        gradient.addColorStop(0, `hsla(${hue}, 80%, 60%, 1)`);
        gradient.addColorStop(0.5, `hsla(${hue}, 80%, 60%, 0.3)`);
        gradient.addColorStop(1, `hsla(${hue}, 80%, 60%, 0)`);
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, size * 3, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fillStyle = `hsl(${hue}, 80%, 70%)`;
        ctx.fill();
    });
}

function drawParallel() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // Draw three branching paths
    const colors = ['#4060ff', '#9664ff', '#ff64c8'];
    const offsets = [-200, 0, 200];
    
    offsets.forEach((off, i) => {
        const startY = cy + 150;
        const endY = cy - 150;
        
        ctx.beginPath();
        ctx.moveTo(cx, startY);
        ctx.bezierCurveTo(cx, cy, cx + off, cy, cx + off, endY);
        ctx.strokeStyle = colors[i];
        ctx.lineWidth = 3;
        ctx.stroke();
        
        // Endpoint
        ctx.beginPath();
        ctx.arc(cx + off, endY, 8, 0, Math.PI * 2);
        ctx.fillStyle = colors[i];
        ctx.fill();
    });
    
    // Origin point
    ctx.beginPath();
    ctx.arc(cx, cy + 150, 10, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
}

function drawMeta() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // Draw helix spiral encompassing all
    ctx.beginPath();
    for (let t = 0; t < Math.PI * 6; t += 0.05) {
        const radius = 80 + t * 15;
        const x = cx + Math.cos(t + time * 0.3) * radius * 0.5;
        const y = cy + Math.sin(t + time * 0.3) * radius * 0.3 - t * 10;
        
        if (t === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    
    const gradient = ctx.createLinearGradient(cx - 200, cy - 200, cx + 200, cy + 200);
    gradient.addColorStop(0, 'rgba(255, 100, 100, 0.4)');
    gradient.addColorStop(0.5, 'rgba(100, 200, 255, 0.4)');
    gradient.addColorStop(1, 'rgba(255, 100, 200, 0.4)');
    
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 3;
    ctx.stroke();
}

function updateCoordinates() {
    const wVal = parseFloat(timeSlider.value);
    document.getElementById('coord-x').textContent = (Math.sin(camera.rotY) * 2).toFixed(2);
    document.getElementById('coord-y').textContent = (Math.sin(camera.rotX) * 2).toFixed(2);
    document.getElementById('coord-z').textContent = (Math.cos(camera.rotY) * Math.cos(camera.rotX) * 2).toFixed(2);
    document.getElementById('coord-w').textContent = wVal.toFixed(2);
}

// ========================
// Initialize
// ========================

document.querySelectorAll('.helix-level').forEach(el => {
    el.addEventListener('click', () => setLevel(parseInt(el.dataset.level)));
});

setLevel(5);
render();

console.log(`
╔══════════════════════════════════════════════════╗
║    ButterflyFX Dimensional Platform Explorer     ║
╠══════════════════════════════════════════════════╣
║  7 Helix Levels:                                 ║
║    1 POINT    → Single data element              ║
║    2 LINE     → Timeline / 1D sequence           ║
║    3 PLANE    → 2D grid layout                   ║
║    4 VOLUME   → 3D spatial navigation            ║
║    5 TIME     → 4D manifold (tesseract)          ║
║    6 PARALLEL → Branching states                 ║
║    7 META     → System overview                  ║
╠══════════════════════════════════════════════════╣
║  ${platformData.name} v${platformData.version}              ║
║  Author: ${platformData.author}                  ║
╚══════════════════════════════════════════════════╝
`);
// ============================================================
// ButterflyFX Dimensional Helix Demo
// "Every point is a dimension. Every dimension contains points."
// ============================================================

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

// ============================================================
// PANEL MANAGEMENT - Draggable, Bring-to-Front
// ============================================================

let highestZ = 100;
const panels = document.querySelectorAll('.info-panel');

panels.forEach(panel => {
    let isDragging = false;
    let startX, startY, startLeft, startTop;
    
    panel.addEventListener('mouseenter', () => {
        panel.classList.add('focused');
        panel.style.zIndex = ++highestZ;
    });
    
    panel.addEventListener('mouseleave', () => {
        if (!isDragging) panel.classList.remove('focused');
    });
    
    panel.addEventListener('mousedown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'A') return;
        isDragging = true;
        panel.classList.add('dragging');
        panel.style.zIndex = ++highestZ;
        startX = e.clientX;
        startY = e.clientY;
        startLeft = panel.offsetLeft;
        startTop = panel.offsetTop;
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        panel.style.left = (startLeft + dx) + 'px';
        panel.style.top = (startTop + dy) + 'px';
        panel.style.right = 'auto';
        panel.style.bottom = 'auto';
    });
    
    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            panel.classList.remove('dragging');
        }
    });
});

// ============================================================
// DIMENSION CONTENT - Each dimension tells its story
// ============================================================

const dimensionContent = {
    0: {
        title: "Dimension 0 — THE VOID",
        subtitle: "Pure Potential",
        color: "#888",
        content: `
            <p>Before differentiation. All possibilities superposed. The void is not empty — it contains <span class="highlight">everything</span> in potential form.</p>
            <div class="insight">
                In ButterflyFX, a null value is not "nothing" — it's the set of all possible values, awaiting observation.
            </div>
            <p>θ = 0. The origin. The seed from which dimensions emerge.</p>
        `
    },
    1: {
        title: "Dimension 1 — THE POINT",
        subtitle: "A Single Value Emerges",
        color: "#ff6464",
        content: `
            <p>The most basic unit of existence. A <span class="highlight">point</span> is a dimension that contains no sub-points — it IS the value.</p>
            <div class="code-block">
# A point is both location AND value
point = substrate.at(0, 1, 0)
value = point.materialize()  # The point IS the data
            </div>
            <div class="insight">
                Key insight: A "row ID" is a 0D point. A "primary key" is a point. An "atom" is a point.
            </div>
            <div class="metric">
                <span class="metric-label">Example</span>
                <span class="metric-value">id=42, name="Alice"</span>
            </div>
        `
    },
    2: {
        title: "Dimension 2 — THE LINE",
        subtitle: "Points Form Sequence",
        color: "#ffaa44",
        content: `
            <p>A <span class="highlight">line</span> is a dimension whose points are arranged in sequence. Each point is a value with position.</p>
            <div class="code-block">
# A line is a dimension containing points
row = [42, "Alice", 28, "Engineer"]
# Each cell is a 0D point
# The row itself is a 1D dimension
            </div>
            <div class="insight">
                A "row" in a database is a 1D dimension. Its "cells" are 0D points. The row IS a line of points.
            </div>
            <div class="metric">
                <span class="metric-label">Properties</span>
                <span class="metric-value">Length, Order, Index</span>
            </div>
        `
    },
    3: {
        title: "Dimension 3 — THE PLANE",
        subtitle: "Lines Form Surface",
        color: "#44dd44",
        content: `
            <p>A <span class="highlight">plane</span> is a dimension whose points are lines. Width means meaning — values gain attributes.</p>
            <div class="code-block">
# A table is a 2D dimension
table = [
    [1, "Alice", 28],
    [2, "Bob", 35],
    [3, "Carol", 42]
]
# Each row is a 1D dimension (line)
# Each cell is a 0D dimension (point)
            </div>
            <div class="insight">
                A "table" is a 2D plane. Rows are 1D lines. Cells are 0D points. All are dimensions.
            </div>
            <div class="metric">
                <span class="metric-label">Properties</span>
                <span class="metric-value">Rows × Columns, Area</span>
            </div>
        `
    },
    4: {
        title: "Dimension 4 — THE VOLUME",
        subtitle: "Surfaces Form Space",
        color: "#44aaff",
        content: `
            <p>A <span class="highlight">volume</span> is a dimension whose points are planes. Depth emerges — structures gain time or version.</p>
            <div class="code-block">
# A complete record with history
document = {
    "current": {"name": "Alice", "age": 28},
    "history": [
        {"name": "Alice", "age": 27},
        {"name": "Alice", "age": 26}
    ]
}
# The document is 3D: current state + time depth
            </div>
            <div class="insight">
                A "database" is 3D: tables (2D) × time (1D) = volume. A "git repo" is 3D: files × commits.
            </div>
            <div class="metric">
                <span class="metric-label">The Tesseract</span>
                <span class="metric-value">16 vertices, 32 edges</span>
            </div>
        `
    },
    5: {
        title: "Dimension 5 — THE NETWORK",
        subtitle: "Systems Connect",
        color: "#aa66ff",
        content: `
            <p>A <span class="highlight">network</span> is a dimension whose points are complete systems. Multiple 4D applications connect.</p>
            <div class="code-block">
# Systems as points in network space
network = {
    "system_a": TesseractApp("database"),
    "system_b": TesseractApp("api_server"),
    "system_c": TesseractApp("frontend")
}
# Each system is a 4D dimension
# The network is 5D: systems × connections
            </div>
            <div class="insight">
                A "microservices architecture" is 5D. Each service is a 4D system. Together they form a 5D network.
            </div>
            <div class="metric">
                <span class="metric-label">Connections</span>
                <span class="metric-value">API, Events, State</span>
            </div>
        `
    },
    6: {
        title: "Dimension 6 — THE INTERNET",
        subtitle: "Networks Unify",
        color: "#ff66aa",
        content: `
            <p>The <span class="highlight">internet</span> is a dimension whose points are networks. Everything connected. The substrate of digital existence.</p>
            <div class="code-block">
# The internet as dimensional space
internet = Manifold({
    "network_eu": Network([...]),
    "network_us": Network([...]),
    "network_asia": Network([...])
})
# Every IP is a 4D coordinate
# 192.168.1.1 → D(192, 168, 1, 1)
            </div>
            <div class="insight">
                The internet is 6D. Networks are 5D. Systems are 4D. All the way down to 0D points.
            </div>
            <div class="metric">
                <span class="metric-label">Your Position</span>
                <span class="metric-value" id="internet-position">Loading...</span>
            </div>
        `
    }
};

let currentDimension = 4;
const dimPanel = document.getElementById('panel-dimension');
const dimTitle = document.getElementById('dim-panel-title');
const dimSubtitle = document.getElementById('dim-panel-subtitle');
const dimContent = document.getElementById('dim-panel-content');

function updateDimensionPanel(dim) {
    const data = dimensionContent[dim];
    dimTitle.textContent = data.title;
    dimTitle.style.color = data.color;
    dimSubtitle.textContent = data.subtitle;
    dimContent.innerHTML = data.content;
    dimPanel.style.display = 'block';
    
    // Update internet position if viewing dim 6
    if (dim === 6) {
        const ipEl = document.getElementById('your-ip');
        const posEl = document.getElementById('internet-position');
        if (posEl && ipEl) {
            posEl.textContent = ipEl.textContent;
        }
    }
}

// Dimension button handlers
document.querySelectorAll('.dim-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.dim-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentDimension = parseInt(btn.dataset.dim);
        updateDimensionPanel(currentDimension);
    });
});

// ============================================================
// 4D MATHEMATICS
// ============================================================

class Vec4 {
    constructor(x = 0, y = 0, z = 0, w = 0) {
        this.x = x; this.y = y; this.z = z; this.w = w;
    }
    
    project3D(wDist = 2.5) {
        const scale = wDist / (wDist - this.w);
        return { x: this.x * scale, y: this.y * scale, z: this.z * scale, scale };
    }
}

function rotateXY(v, a) { const c = Math.cos(a), s = Math.sin(a); return new Vec4(v.x*c - v.y*s, v.x*s + v.y*c, v.z, v.w); }
function rotateXZ(v, a) { const c = Math.cos(a), s = Math.sin(a); return new Vec4(v.x*c - v.z*s, v.y, v.x*s + v.z*c, v.w); }
function rotateXW(v, a) { const c = Math.cos(a), s = Math.sin(a); return new Vec4(v.x*c - v.w*s, v.y, v.z, v.x*s + v.w*c); }
function rotateYZ(v, a) { const c = Math.cos(a), s = Math.sin(a); return new Vec4(v.x, v.y*c - v.z*s, v.y*s + v.z*c, v.w); }
function rotateYW(v, a) { const c = Math.cos(a), s = Math.sin(a); return new Vec4(v.x, v.y*c - v.w*s, v.z, v.y*s + v.w*c); }
function rotateZW(v, a) { const c = Math.cos(a), s = Math.sin(a); return new Vec4(v.x, v.y, v.z*c - v.w*s, v.z*s + v.w*c); }

// Tesseract
class Tesseract {
    constructor(size = 1) {
        this.vertices = [];
        this.edges = [];
        for (let w = -1; w <= 1; w += 2)
            for (let z = -1; z <= 1; z += 2)
                for (let y = -1; y <= 1; y += 2)
                    for (let x = -1; x <= 1; x += 2)
                        this.vertices.push(new Vec4(x * size, y * size, z * size, w * size));
        
        for (let i = 0; i < 16; i++) {
            for (let j = i + 1; j < 16; j++) {
                const v1 = this.vertices[i], v2 = this.vertices[j];
                let diff = 0;
                if (v1.x !== v2.x) diff++;
                if (v1.y !== v2.y) diff++;
                if (v1.z !== v2.z) diff++;
                if (v1.w !== v2.w) diff++;
                if (diff === 1) this.edges.push([i, j]);
            }
        }
    }
    
    getTransformed(rotXY, rotXZ, rotXW, rotYW) {
        return this.vertices.map(v => {
            let r = rotateXY(v, rotXY);
            r = rotateXZ(r, rotXZ);
            r = rotateXW(r, rotXW);
            r = rotateYW(r, rotYW);
            return r;
        });
    }
}

// Camera
const camera = { rotX: 0.3, rotY: 0.5, zoom: 150 };
let isDragging = false, lastMX = 0, lastMY = 0;

canvas.addEventListener('mousedown', (e) => { isDragging = true; lastMX = e.clientX; lastMY = e.clientY; });
canvas.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    camera.rotY += (e.clientX - lastMX) * 0.005;
    camera.rotX += (e.clientY - lastMY) * 0.005;
    lastMX = e.clientX; lastMY = e.clientY;
});
canvas.addEventListener('mouseup', () => { isDragging = false; });
canvas.addEventListener('wheel', (e) => { camera.zoom = Math.max(50, Math.min(400, camera.zoom - e.deltaY * 0.5)); e.preventDefault(); }, { passive: false });

// Animation state
let time = 0;
let rotXW = 0, rotYW = 0;
const tesseract = new Tesseract(1);

const timeSlider = document.getElementById('time-slider');
const timeValue = document.getElementById('time-value');
timeSlider.addEventListener('input', () => {
    const t = parseFloat(timeSlider.value);
    timeValue.textContent = `t=${t.toFixed(2)}`;
});

// Project 3D to 2D
function project3Dto2D(p3) {
    const cosX = Math.cos(camera.rotX), sinX = Math.sin(camera.rotX);
    const cosY = Math.cos(camera.rotY), sinY = Math.sin(camera.rotY);
    
    let x = p3.x, y = p3.y, z = p3.z;
    let x1 = x * cosY - z * sinY;
    let z1 = x * sinY + z * cosY;
    let y1 = y * cosX - z1 * sinX;
    let z2 = y * sinX + z1 * cosX;
    
    const scale = 800 / (800 - z2);
    return {
        x: canvas.width / 2 + x1 * camera.zoom * scale,
        y: canvas.height / 2 + y1 * camera.zoom * scale,
        z: z2,
        scale
    };
}

// ============================================================
// RENDER FUNCTIONS FOR EACH DIMENSION
// ============================================================

function renderVoid() {
    const cx = canvas.width / 2, cy = canvas.height / 2;
    
    // Subtle noise field
    for (let i = 0; i < 50; i++) {
        const angle = Math.random() * Math.PI * 2;
        const dist = Math.random() * 200 + 50;
        const x = cx + Math.cos(angle + time * 0.1) * dist;
        const y = cy + Math.sin(angle + time * 0.1) * dist;
        const alpha = Math.random() * 0.3;
        
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(100, 100, 120, ${alpha})`;
        ctx.fill();
    }
    
    // Center void
    const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, 100);
    gradient.addColorStop(0, 'rgba(50, 50, 80, 0.5)');
    gradient.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.arc(cx, cy, 100, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();
    
    ctx.font = 'bold 16px monospace';
    ctx.fillStyle = 'rgba(100, 100, 120, 0.8)';
    ctx.textAlign = 'center';
    ctx.fillText('THE VOID', cx, cy - 130);
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(100, 100, 120, 0.5)';
    ctx.fillText('All possibilities superposed', cx, cy + 140);
}

function renderPoint() {
    const cx = canvas.width / 2, cy = canvas.height / 2;
    
    // Pulsing point
    const pulse = 1 + Math.sin(time * 3) * 0.3;
    const size = 20 * pulse;
    
    const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, size * 2);
    gradient.addColorStop(0, '#ff6464');
    gradient.addColorStop(0.5, 'rgba(255, 100, 100, 0.5)');
    gradient.addColorStop(1, 'transparent');
    
    ctx.beginPath();
    ctx.arc(cx, cy, size * 2, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();
    
    ctx.beginPath();
    ctx.arc(cx, cy, size / 2, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
    
    ctx.font = 'bold 16px monospace';
    ctx.fillStyle = 'rgba(255, 100, 100, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('THE POINT', cx, cy - 80);
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(255, 150, 150, 0.6)';
    ctx.fillText('A dimension with no sub-dimensions', cx, cy + 100);
    ctx.fillText('The point IS the value', cx, cy + 120);
}

function renderLine() {
    const cx = canvas.width / 2, cy = canvas.height / 2;
    const numPoints = 12;
    
    // Draw line of points
    ctx.beginPath();
    ctx.moveTo(cx - 200, cy);
    ctx.lineTo(cx + 200, cy);
    ctx.strokeStyle = 'rgba(255, 170, 68, 0.3)';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    for (let i = 0; i < numPoints; i++) {
        const x = cx - 180 + (i / (numPoints - 1)) * 360;
        const offset = Math.sin(time * 2 + i * 0.5) * 10;
        const y = cy + offset;
        
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 15);
        gradient.addColorStop(0, '#ffaa44');
        gradient.addColorStop(1, 'transparent');
        
        ctx.beginPath();
        ctx.arc(x, y, 12, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();
        
        ctx.font = '9px monospace';
        ctx.fillStyle = 'rgba(255, 170, 68, 0.7)';
        ctx.textAlign = 'center';
        ctx.fillText(`P${i}`, x, y + 25);
    }
    
    ctx.font = 'bold 16px monospace';
    ctx.fillStyle = 'rgba(255, 170, 68, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('THE LINE', cx, cy - 80);
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(255, 200, 100, 0.6)';
    ctx.fillText('Points arranged in sequence', cx, cy + 100);
}

function renderPlane() {
    const cx = canvas.width / 2, cy = canvas.height / 2;
    const cols = 6, rows = 4;
    const cellW = 60, cellH = 35;
    const startX = cx - (cols * cellW) / 2;
    const startY = cy - (rows * cellH) / 2;
    
    // Draw grid
    for (let r = 0; r <= rows; r++) {
        ctx.beginPath();
        ctx.moveTo(startX, startY + r * cellH);
        ctx.lineTo(startX + cols * cellW, startY + r * cellH);
        ctx.strokeStyle = 'rgba(68, 221, 68, 0.3)';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
    for (let c = 0; c <= cols; c++) {
        ctx.beginPath();
        ctx.moveTo(startX + c * cellW, startY);
        ctx.lineTo(startX + c * cellW, startY + rows * cellH);
        ctx.stroke();
    }
    
    // Highlight cells
    const labels = ['ID', 'Name', 'Age', 'Role', 'Dept', 'Level'];
    for (let c = 0; c < cols; c++) {
        ctx.font = '10px monospace';
        ctx.fillStyle = 'rgba(68, 221, 68, 0.8)';
        ctx.textAlign = 'center';
        ctx.fillText(labels[c], startX + c * cellW + cellW/2, startY - 8);
    }
    
    // Sample data
    const data = [
        ['1', 'Alice', '28', 'Eng', 'R&D', '5'],
        ['2', 'Bob', '35', 'Mgr', 'Ops', '7'],
        ['3', 'Carol', '42', 'Dir', 'Exec', '9'],
        ['4', 'Dave', '29', 'Eng', 'R&D', '4']
    ];
    
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            ctx.font = '10px monospace';
            ctx.fillStyle = 'rgba(200, 255, 200, 0.7)';
            ctx.textAlign = 'center';
            ctx.fillText(data[r][c], startX + c * cellW + cellW/2, startY + r * cellH + cellH/2 + 4);
        }
    }
    
    ctx.font = 'bold 16px monospace';
    ctx.fillStyle = 'rgba(68, 221, 68, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('THE PLANE', cx, cy - 100);
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(100, 255, 100, 0.6)';
    ctx.fillText('Lines (rows) form a surface (table)', cx, cy + 100);
}

function renderVolume() {
    const cx = canvas.width / 2, cy = canvas.height / 2;
    const t = parseFloat(timeSlider.value);
    
    rotXW = time * 0.15;
    rotYW = time * 0.1;
    
    const vertices4D = tesseract.getTransformed(time * 0.1, 0, rotXW, rotYW);
    const projected = vertices4D.map(v => {
        const p3 = v.project3D(2.5);
        return project3Dto2D(p3);
    });
    
    // Sort edges by Z
    const sortedEdges = [...tesseract.edges].sort((a, b) => {
        const zA = (projected[a[0]].z + projected[a[1]].z) / 2;
        const zB = (projected[b[0]].z + projected[b[1]].z) / 2;
        return zA - zB;
    });
    
    // Draw edges
    sortedEdges.forEach(([i, j]) => {
        const p1 = projected[i], p2 = projected[j];
        const avgZ = (p1.z + p2.z) / 2;
        const alpha = 0.3 + (avgZ + 2) * 0.15;
        const hue = 200 + avgZ * 20;
        
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = `hsla(${hue}, 80%, 60%, ${alpha})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
    });
    
    // Draw vertices
    projected.forEach((p, i) => {
        const size = 3 + p.scale * 2;
        const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, size * 2);
        gradient.addColorStop(0, 'rgba(68, 170, 255, 0.8)');
        gradient.addColorStop(1, 'transparent');
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, size * 2, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, size / 2, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();
    });
    
    ctx.font = 'bold 16px monospace';
    ctx.fillStyle = 'rgba(68, 170, 255, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('THE TESSERACT', cx, cy - 180);
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(100, 200, 255, 0.6)';
    ctx.fillText('4D hypercube: 16 vertices, 32 edges', cx, cy + 200);
    ctx.fillText('Each vertex is a 3D point. The tesseract is a 4D dimension.', cx, cy + 220);
}

function renderNetwork() {
    const cx = canvas.width / 2, cy = canvas.height / 2;
    
    // Draw 3 connected tesseracts
    const systems = [
        { x: -180, name: 'SYSTEM A', type: 'Database' },
        { x: 0, name: 'SYSTEM B', type: 'API Server' },
        { x: 180, name: 'SYSTEM C', type: 'Frontend' }
    ];
    
    // Connection lines
    ctx.setLineDash([6, 4]);
    ctx.strokeStyle = 'rgba(170, 102, 255, 0.4)';
    ctx.lineWidth = 2;
    systems.forEach((s1, i) => {
        systems.forEach((s2, j) => {
            if (i < j) {
                ctx.beginPath();
                ctx.moveTo(cx + s1.x, cy);
                ctx.lineTo(cx + s2.x, cy);
                ctx.stroke();
            }
        });
    });
    ctx.setLineDash([]);
    
    // Flowing packets
    for (let p = 0; p < 8; p++) {
        const progress = ((time * 0.3 + p / 8) % 1);
        const fromIdx = p % 3;
        const toIdx = (fromIdx + 1) % 3;
        const x = cx + systems[fromIdx].x + (systems[toIdx].x - systems[fromIdx].x) * progress;
        const y = cy + Math.sin(progress * Math.PI) * -25;
        
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 6);
        gradient.addColorStop(0, 'rgba(170, 102, 255, 0.9)');
        gradient.addColorStop(1, 'transparent');
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
    }
    
    // Mini tesseracts for each system
    systems.forEach((sys, idx) => {
        const mini = new Tesseract(0.4);
        const verts = mini.getTransformed(time * 0.1 + idx, 0, time * 0.15, time * 0.1);
        const proj = verts.map(v => {
            const p3 = v.project3D(2.5);
            const cosY = Math.cos(camera.rotY), sinY = Math.sin(camera.rotY);
            const x1 = p3.x * cosY - p3.z * sinY;
            return {
                x: cx + sys.x + x1 * 50,
                y: cy + p3.y * 50,
                z: p3.z
            };
        });
        
        mini.edges.forEach(([i, j]) => {
            ctx.beginPath();
            ctx.moveTo(proj[i].x, proj[i].y);
            ctx.lineTo(proj[j].x, proj[j].y);
            ctx.strokeStyle = `rgba(170, 102, 255, 0.5)`;
            ctx.lineWidth = 1;
            ctx.stroke();
        });
        
        ctx.font = 'bold 10px monospace';
        ctx.fillStyle = 'rgba(170, 102, 255, 0.9)';
        ctx.textAlign = 'center';
        ctx.fillText(sys.name, cx + sys.x, cy + 80);
        ctx.font = '9px monospace';
        ctx.fillStyle = 'rgba(200, 150, 255, 0.6)';
        ctx.fillText(sys.type, cx + sys.x, cy + 95);
    });
    
    ctx.font = 'bold 16px monospace';
    ctx.fillStyle = 'rgba(170, 102, 255, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('THE NETWORK', cx, cy - 120);
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(200, 150, 255, 0.6)';
    ctx.fillText('Systems (4D) connect to form network (5D)', cx, cy + 150);
}

function renderInternet() {
    const cx = canvas.width / 2, cy = canvas.height / 2;
    
    const clusters = [
        { x: 0, y: -80, name: 'NAM', color: '#ff6464', nodes: 5 },
        { x: 130, y: -20, name: 'EUR', color: '#44dd44', nodes: 6 },
        { x: -130, y: -20, name: 'ASIA', color: '#4488ff', nodes: 7 },
        { x: 80, y: 80, name: 'AFR', color: '#ffdd44', nodes: 4 },
        { x: -80, y: 80, name: 'SAM', color: '#ff44ff', nodes: 4 }
    ];
    
    // Global ring
    ctx.beginPath();
    ctx.ellipse(cx, cy, 200, 80, 0, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255, 102, 170, 0.15)';
    ctx.lineWidth = 30;
    ctx.stroke();
    
    // Inter-cluster connections
    clusters.forEach((c1, i) => {
        clusters.forEach((c2, j) => {
            if (i < j) {
                const pulse = Math.sin(time * 1.5 + i + j) * 0.2 + 0.3;
                ctx.beginPath();
                ctx.moveTo(cx + c1.x, cy + c1.y);
                ctx.lineTo(cx + c2.x, cy + c2.y);
                ctx.strokeStyle = `rgba(255, 255, 255, ${pulse})`;
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        });
    });
    
    // Flowing packets
    for (let p = 0; p < 15; p++) {
        const from = clusters[p % clusters.length];
        const to = clusters[(p + 1) % clusters.length];
        const progress = ((time * 0.4 + p * 0.1) % 1);
        const x = cx + from.x + (to.x - from.x) * progress;
        const y = cy + from.y + (to.y - from.y) * progress;
        
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.fill();
    }
    
    // Draw clusters
    clusters.forEach((cluster, ci) => {
        const clusterX = cx + cluster.x;
        const clusterY = cy + cluster.y;
        
        // Nodes in cluster
        for (let n = 0; n < cluster.nodes; n++) {
            const angle = (n / cluster.nodes) * Math.PI * 2 + time * 0.2 + ci;
            const dist = 20;
            const nx = clusterX + Math.cos(angle) * dist;
            const ny = clusterY + Math.sin(angle) * dist * 0.6;
            
            ctx.beginPath();
            ctx.arc(nx, ny, 3, 0, Math.PI * 2);
            ctx.fillStyle = cluster.color;
            ctx.fill();
        }
        
        // Center
        const gradient = ctx.createRadialGradient(clusterX, clusterY, 0, clusterX, clusterY, 15);
        gradient.addColorStop(0, cluster.color + '80');
        gradient.addColorStop(1, 'transparent');
        ctx.beginPath();
        ctx.arc(clusterX, clusterY, 12, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        ctx.font = 'bold 9px monospace';
        ctx.fillStyle = cluster.color;
        ctx.textAlign = 'center';
        ctx.fillText(cluster.name, clusterX, clusterY + 35);
    });
    
    ctx.font = 'bold 16px monospace';
    ctx.fillStyle = 'rgba(255, 102, 170, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('THE INTERNET', cx, cy - 140);
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(255, 150, 200, 0.6)';
    ctx.fillText('Networks (5D) unify into internet (6D)', cx, cy + 140);
    ctx.fillText('Every IP is a coordinate in this space', cx, cy + 160);
}

// ============================================================
// MAIN RENDER LOOP
// ============================================================

const renderFunctions = [renderVoid, renderPoint, renderLine, renderPlane, renderVolume, renderNetwork, renderInternet];

function render() {
    time += 0.016;
    
    // Clear
    ctx.fillStyle = '#060610';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Subtle grid
    ctx.strokeStyle = 'rgba(40, 40, 80, 0.2)';
    ctx.lineWidth = 1;
    const gridSize = 50;
    for (let x = 0; x < canvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
    
    // Render current dimension
    renderFunctions[currentDimension]();
    
    requestAnimationFrame(render);
}

// ============================================================
// FETCH DATA
// ============================================================

// Get user's dimensional position
fetch('/api/dimensional/myposition')
    .then(r => r.json())
    .then(data => {
        if (data.ip) {
            document.getElementById('your-ip').textContent = data.ip;
            document.getElementById('your-coords').textContent = 
                `(${data.dimensional.x}, ${data.dimensional.y}, ${data.dimensional.z}, ${data.dimensional.m})`;
            document.getElementById('substrate-notation').textContent = 
                `r = ${data.dimensional.x},${data.dimensional.y},${data.dimensional.z},${data.dimensional.m}`;
        }
    })
    .catch(() => {
        document.getElementById('your-ip').textContent = '(local)';
    });

// Get benchmarks
fetch('/api/dimensional/benchmark')
    .then(r => r.json())
    .then(data => {
        if (data.benchmarks) {
            const enc = data.benchmarks.find(b => b.name.includes('encode'));
            const der = data.benchmarks.find(b => b.name.includes('geometric') || b.name.includes('derive'));
            if (enc) document.getElementById('bench-encode').textContent = enc.per_op;
            if (der) document.getElementById('bench-derive').textContent = der.per_op;
        }
    })
    .catch(() => {});

// Initialize
updateDimensionPanel(currentDimension);
render();
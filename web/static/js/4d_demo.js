// ===========================================================
// ButterflyFX 4D Website Demo
// "A website where content exists in 4-dimensional space"
// ===========================================================

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// Resize handler
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

// =========================
// 4D Mathematics
// =========================

class Vec4 {
    constructor(x = 0, y = 0, z = 0, w = 0) {
        this.x = x; this.y = y; this.z = z; this.w = w;
    }
    
    add(v) { return new Vec4(this.x + v.x, this.y + v.y, this.z + v.z, this.w + v.w); }
    sub(v) { return new Vec4(this.x - v.x, this.y - v.y, this.z - v.z, this.w - v.w); }
    mul(s) { return new Vec4(this.x * s, this.y * s, this.z * s, this.w * s); }
    
    // Project 4D to 3D (perspective projection from W)
    project3D(w_distance = 2) {
        const scale = w_distance / (w_distance - this.w);
        return {
            x: this.x * scale,
            y: this.y * scale,
            z: this.z * scale,
            scale: scale
        };
    }
}

// 4D rotation matrices
function rotateXY(v, angle) {
    const c = Math.cos(angle), s = Math.sin(angle);
    return new Vec4(
        v.x * c - v.y * s,
        v.x * s + v.y * c,
        v.z,
        v.w
    );
}

function rotateXZ(v, angle) {
    const c = Math.cos(angle), s = Math.sin(angle);
    return new Vec4(
        v.x * c - v.z * s,
        v.y,
        v.x * s + v.z * c,
        v.w
    );
}

function rotateXW(v, angle) {
    const c = Math.cos(angle), s = Math.sin(angle);
    return new Vec4(
        v.x * c - v.w * s,
        v.y,
        v.z,
        v.x * s + v.w * c
    );
}

function rotateYZ(v, angle) {
    const c = Math.cos(angle), s = Math.sin(angle);
    return new Vec4(
        v.x,
        v.y * c - v.z * s,
        v.y * s + v.z * c,
        v.w
    );
}

function rotateYW(v, angle) {
    const c = Math.cos(angle), s = Math.sin(angle);
    return new Vec4(
        v.x,
        v.y * c - v.w * s,
        v.z,
        v.y * s + v.w * c
    );
}

function rotateZW(v, angle) {
    const c = Math.cos(angle), s = Math.sin(angle);
    return new Vec4(
        v.x,
        v.y,
        v.z * c - v.w * s,
        v.z * s + v.w * c
    );
}

// =========================
// Tesseract (4D Hypercube)
// =========================

class Tesseract {
    constructor(size = 1) {
        this.size = size;
        this.vertices = [];
        this.edges = [];
        this.generateGeometry();
    }
    
    generateGeometry() {
        // 16 vertices of a tesseract (all combinations of ±1 in 4D)
        for (let w = -1; w <= 1; w += 2) {
            for (let z = -1; z <= 1; z += 2) {
                for (let y = -1; y <= 1; y += 2) {
                    for (let x = -1; x <= 1; x += 2) {
                        this.vertices.push(new Vec4(
                            x * this.size,
                            y * this.size,
                            z * this.size,
                            w * this.size
                        ));
                    }
                }
            }
        }
        
        // 32 edges: connect vertices that differ in exactly one coordinate
        for (let i = 0; i < 16; i++) {
            for (let j = i + 1; j < 16; j++) {
                const v1 = this.vertices[i];
                const v2 = this.vertices[j];
                let diff = 0;
                if (v1.x !== v2.x) diff++;
                if (v1.y !== v2.y) diff++;
                if (v1.z !== v2.z) diff++;
                if (v1.w !== v2.w) diff++;
                if (diff === 1) {
                    this.edges.push([i, j]);
                }
            }
        }
    }
    
    getTransformedVertices(rotXY, rotXZ, rotXW, rotYW) {
        return this.vertices.map(v => {
            let transformed = v;
            transformed = rotateXY(transformed, rotXY);
            transformed = rotateXZ(transformed, rotXZ);
            transformed = rotateXW(transformed, rotXW);
            transformed = rotateYW(transformed, rotYW);
            return transformed;
        });
    }
}

// =========================
// Camera & Projection
// =========================

class Camera {
    constructor() {
        this.distance = 5;
        this.rotX = 0.3;
        this.rotY = 0.5;
    }
    
    project(point3D) {
        // Apply 3D rotation
        let x = point3D.x;
        let y = point3D.y;
        let z = point3D.z;
        
        // Rotate around Y axis
        const cosY = Math.cos(this.rotY);
        const sinY = Math.sin(this.rotY);
        const x1 = x * cosY - z * sinY;
        const z1 = x * sinY + z * cosY;
        
        // Rotate around X axis
        const cosX = Math.cos(this.rotX);
        const sinX = Math.sin(this.rotX);
        const y1 = y * cosX - z1 * sinX;
        const z2 = y * sinX + z1 * cosX;
        
        // Perspective projection
        const scale = this.distance / (this.distance - z2);
        
        return {
            x: x1 * scale * 150 + canvas.width / 2,
            y: -y1 * scale * 150 + canvas.height / 2,
            z: z2,
            scale: scale * (point3D.scale || 1)
        };
    }
}

// =========================
// State
// =========================

const tesseract = new Tesseract(0.8);
const camera = new Camera();

let rotXW = 0;  // 4D rotation angle (controlled by time slider)
let rotYW = 0;  // Secondary 4D rotation
let autoRotate = true;
let time = 0;
let currentLevel = 5;  // Current helix level (1-7), start at TESSERACT

// Helix level descriptions
const HELIX_LEVELS = {
    1: { name: 'POINT', dimension: '0D', description: 'A single point. The origin. All complexity collapses to unity.' },
    2: { name: 'LINE', dimension: '1D', description: 'Connection between two points. The first relationship.' },
    3: { name: 'PLANE', dimension: '2D', description: 'A surface emerges. Four points define a square.' },
    4: { name: 'VOLUME', dimension: '3D', description: 'Space itself. Eight vertices form a cube.' },
    5: { name: 'TIME', dimension: '4D', description: 'The tesseract. Sixteen vertices in 4-dimensional spacetime.' },
    6: { name: 'PARALLEL', dimension: '5D', description: 'Multiple timelines. Branching possibilities.' },
    7: { name: 'META', dimension: '6D', description: 'The system observing itself. Full dimensional awareness.' }
};

// Mouse/touch interaction
let isDragging = false;
let lastMouseX = 0;
let lastMouseY = 0;

canvas.addEventListener('mousedown', e => {
    isDragging = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
});

canvas.addEventListener('mousemove', e => {
    if (isDragging) {
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        camera.rotY += dx * 0.01;
        camera.rotX += dy * 0.01;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
    }
});

canvas.addEventListener('mouseup', () => isDragging = false);
canvas.addEventListener('mouseleave', () => isDragging = false);

canvas.addEventListener('wheel', e => {
    camera.distance += e.deltaY * 0.01;
    camera.distance = Math.max(2, Math.min(10, camera.distance));
    e.preventDefault();
}, { passive: false });

// Time slider control
const timeSlider = document.getElementById('time-slider');
const timeValue = document.getElementById('time-value');

timeSlider.addEventListener('input', e => {
    rotXW = parseFloat(e.target.value) * Math.PI;
    timeValue.textContent = `W: ${parseFloat(e.target.value).toFixed(2)}`;
    updateCoordinates();
});

// =========================
// Content Panels in 4D Space
// =========================

const contentPanels = [
    {
        id: 'panel-past',
        title: 'Historical State',
        content: 'Content from the past dimension. In ButterflyFX, history is not lost — it exists at a different W coordinate.',
        position4D: new Vec4(-1.5, 0.5, 0, -0.8),
        element: null
    },
    {
        id: 'panel-present',
        title: 'Current Manifold',
        content: 'The present moment — where all dimensions converge. Mathematical functions evaluated at W=0.',
        position4D: new Vec4(1.5, 0, 0.5, 0),
        element: null
    },
    {
        id: 'panel-future',
        title: 'Projected State',
        content: 'Future possibilities emerge from the manifold. The butterfly effect in action — small changes, vast consequences.',
        position4D: new Vec4(-0.5, -0.5, -1, 0.8),
        element: null
    }
];

// Create panel elements
contentPanels.forEach(panel => {
    const el = document.createElement('div');
    el.className = 'content-panel';
    el.id = panel.id;
    el.innerHTML = `<h2>${panel.title}</h2><p>${panel.content}</p>`;
    document.body.appendChild(el);
    panel.element = el;
});

function updatePanels() {
    contentPanels.forEach(panel => {
        // Apply 4D rotation to panel position
        let pos = panel.position4D;
        pos = rotateXW(pos, rotXW);
        pos = rotateYW(pos, rotYW);
        
        // Project to 3D then to 2D
        const pos3D = pos.project3D(3);
        const pos2D = camera.project(pos3D);
        
        // Update panel position and opacity based on W coordinate
        const wFade = Math.max(0, 1 - Math.abs(pos.w) * 0.5);
        const scale = Math.max(0.5, Math.min(1.5, pos2D.scale * 0.8));
        
        panel.element.style.left = (pos2D.x - 150) + 'px';
        panel.element.style.top = (pos2D.y - 50) + 'px';
        panel.element.style.opacity = wFade * 0.9;
        panel.element.style.transform = `scale(${scale})`;
        panel.element.style.zIndex = Math.floor(50 + pos2D.z * 10);
        panel.element.style.pointerEvents = wFade > 0.3 ? 'auto' : 'none';
    });
}

// =========================
// Update coordinate display
// =========================

function updateCoordinates() {
    const wVal = parseFloat(timeSlider.value);
    document.getElementById('coord-x').textContent = (Math.sin(camera.rotY) * 2).toFixed(2);
    document.getElementById('coord-y').textContent = (Math.sin(camera.rotX) * 2).toFixed(2);
    document.getElementById('coord-z').textContent = (Math.cos(camera.rotY) * Math.cos(camera.rotX) * 2).toFixed(2);
    document.getElementById('coord-w').textContent = wVal.toFixed(2);
}

// =========================
// Render Loop
// =========================

function render() {
    ctx.fillStyle = '#0a0a12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Subtle auto-rotation of 4D (W dimension wobble)
    if (autoRotate && !isDragging) {
        rotYW = Math.sin(time * 0.3) * 0.2;
    }
    time += 0.016;
    
    // Render based on current helix level
    switch(currentLevel) {
        case 1: renderPoint(); break;
        case 2: renderLine(); break;
        case 3: renderPlane(); break;
        case 4: renderVolume(); break;
        case 5: renderTesseract(); break;
        case 6: renderParallel(); break;
        case 7: renderMeta(); break;
        default: renderTesseract();
    }
    
    // Draw central helix spiral
    drawHelixSpiral();
    
    // Update content panels
    updatePanels();
    updateCoordinates();
    
    requestAnimationFrame(render);
}

// Level 1: POINT - The most basic unit
function renderPoint() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // Pulsing point emerging from void
    const pulse = Math.sin(time * 2) * 0.3 + 1;
    const size = 25 * pulse;
    
    // Draw the void background with subtle particles
    for (let i = 0; i < 30; i++) {
        const angle = time * 0.1 + i * 0.3;
        const dist = 100 + Math.sin(time + i) * 50;
        const px = cx + Math.cos(angle) * dist;
        const py = cy + Math.sin(angle) * dist;
        const alpha = 0.1 + Math.sin(time + i * 0.5) * 0.05;
        ctx.beginPath();
        ctx.arc(px, py, 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(100, 100, 150, ${alpha})`;
        ctx.fill();
    }
    
    // Outer glow rings - emergence from void
    for (let i = 5; i > 0; i--) {
        const ringSize = size * (1 + i * 0.6);
        const alpha = 0.15 * (6 - i) / 5;
        ctx.beginPath();
        ctx.arc(cx, cy, ringSize, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 64, 128, ${alpha})`;
        ctx.lineWidth = 2;
        ctx.stroke();
    }
    
    // Core point with intense glow
    const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, size * 2.5);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
    gradient.addColorStop(0.2, 'rgba(255, 200, 255, 0.9)');
    gradient.addColorStop(0.4, 'rgba(255, 64, 128, 0.6)');
    gradient.addColorStop(0.7, 'rgba(64, 96, 255, 0.3)');
    gradient.addColorStop(1, 'rgba(64, 96, 255, 0)');
    
    ctx.beginPath();
    ctx.arc(cx, cy, size * 2.5, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();
    
    // The point itself
    ctx.beginPath();
    ctx.arc(cx, cy, size * 0.25, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
    
    // Text
    ctx.font = 'bold 18px monospace';
    ctx.fillStyle = 'rgba(255, 64, 128, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('0D — THE POINT', cx, cy - 120);
    
    ctx.font = '14px monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillText('The most basic unit.', cx, cy + 100);
    ctx.fillText('From the void, observation creates existence.', cx, cy + 125);
    
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(150, 150, 200, 0.6)';
    ctx.fillText('An ID is born. A single value. A measurement.', cx, cy + 160);
    ctx.fillText('Everything begins here.', cx, cy + 180);
}

// Level 2: LINE - 1D Linear, a row of values
function renderLine() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const length = 300;
    
    // Animate points flowing along the line
    const numPoints = 12;
    const x1 = cx - length;
    const x2 = cx + length;
    
    // Line glow
    ctx.beginPath();
    ctx.moveTo(x1, cy);
    ctx.lineTo(x2, cy);
    ctx.strokeStyle = 'rgba(64, 96, 255, 0.2)';
    ctx.lineWidth = 30;
    ctx.stroke();
    
    // Main line gradient
    const lineGrad = ctx.createLinearGradient(x1, cy, x2, cy);
    lineGrad.addColorStop(0, '#ff4080');
    lineGrad.addColorStop(0.5, '#fff');
    lineGrad.addColorStop(1, '#4060ff');
    
    ctx.beginPath();
    ctx.moveTo(x1, cy);
    ctx.lineTo(x2, cy);
    ctx.strokeStyle = lineGrad;
    ctx.lineWidth = 3;
    ctx.stroke();
    
    // Draw animated points along the line (values)
    for (let i = 0; i < numPoints; i++) {
        const t = (i / numPoints + time * 0.05) % 1;
        const x = x1 + (x2 - x1) * t;
        const pulse = Math.sin(time * 3 + i) * 0.3 + 1;
        const size = 8 * pulse;
        
        const gradient = ctx.createRadialGradient(x, cy, 0, x, cy, size * 2);
        gradient.addColorStop(0, `hsla(${220 + t * 100}, 80%, 70%, 1)`);
        gradient.addColorStop(1, 'transparent');
        
        ctx.beginPath();
        ctx.arc(x, cy, size * 2, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(x, cy, size * 0.4, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();
        
        // Value labels
        ctx.font = '10px monospace';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.textAlign = 'center';
        ctx.fillText(`v${i}`, x, cy - 25);
    }
    
    // Endpoints with arrows
    [[x1, '▶'], [x2, '◀']].forEach(([x, arrow], i) => {
        ctx.beginPath();
        ctx.arc(x, cy, 12, 0, Math.PI * 2);
        ctx.fillStyle = i === 0 ? '#ff4080' : '#4060ff';
        ctx.fill();
    });
    
    // Text
    ctx.font = 'bold 18px monospace';
    ctx.fillStyle = 'rgba(255, 180, 100, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('1D — THE LINE', cx, cy - 100);
    
    ctx.font = '14px monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillText('A sequence of points. A row. A length.', cx, cy + 80);
    ctx.fillText('The ID now has VALUES.', cx, cy + 105);
    
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(150, 150, 200, 0.6)';
    ctx.fillText('Linear data: [v0, v1, v2, v3, ...]', cx, cy + 140);
    ctx.fillText('A single dimension of measurement.', cx, cy + 160);
}

// Level 3: PLANE - 2D Table, records with attributes
function renderPlane() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const cellSize = 50;
    const rows = 5;
    const cols = 6;
    
    const tableWidth = cols * cellSize;
    const tableHeight = rows * cellSize;
    const startX = cx - tableWidth / 2;
    const startY = cy - tableHeight / 2;
    
    // Slight rotation for 3D effect
    const tilt = 0.15;
    
    // Draw table background with perspective
    ctx.save();
    ctx.translate(cx, cy);
    ctx.transform(1, 0, tilt, 1, 0, 0);
    ctx.translate(-cx, -cy);
    
    // Table fill
    ctx.fillStyle = 'rgba(30, 40, 80, 0.5)';
    ctx.fillRect(startX, startY, tableWidth, tableHeight);
    
    // Draw grid
    ctx.strokeStyle = 'rgba(100, 150, 255, 0.3)';
    ctx.lineWidth = 1;
    
    // Vertical lines
    for (let i = 0; i <= cols; i++) {
        ctx.beginPath();
        ctx.moveTo(startX + i * cellSize, startY);
        ctx.lineTo(startX + i * cellSize, startY + tableHeight);
        ctx.stroke();
    }
    
    // Horizontal lines
    for (let i = 0; i <= rows; i++) {
        ctx.beginPath();
        ctx.moveTo(startX, startY + i * cellSize);
        ctx.lineTo(startX + tableWidth, startY + i * cellSize);
        ctx.stroke();
    }
    
    // Draw data points in cells
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const x = startX + col * cellSize + cellSize / 2;
            const y = startY + row * cellSize + cellSize / 2;
            
            const pulse = Math.sin(time * 2 + row + col * 0.5) * 0.3 + 0.7;
            const hue = 200 + col * 25;
            const size = 6 * pulse;
            
            // Cell glow
            ctx.beginPath();
            ctx.arc(x, y, size * 2, 0, Math.PI * 2);
            const grad = ctx.createRadialGradient(x, y, 0, x, y, size * 2);
            grad.addColorStop(0, `hsla(${hue}, 70%, 60%, 0.8)`);
            grad.addColorStop(1, 'transparent');
            ctx.fillStyle = grad;
            ctx.fill();
            
            ctx.beginPath();
            ctx.arc(x, y, size * 0.5, 0, Math.PI * 2);
            ctx.fillStyle = '#fff';
            ctx.fill();
        }
    }
    
    // Header row highlight
    ctx.fillStyle = 'rgba(255, 180, 100, 0.15)';
    ctx.fillRect(startX, startY, tableWidth, cellSize);
    
    // Column labels (attributes)
    const attrs = ['ID', 'Name', 'Type', 'Value', 'Time', 'Meta'];
    ctx.font = '10px monospace';
    ctx.fillStyle = 'rgba(255, 200, 100, 0.9)';
    ctx.textAlign = 'center';
    attrs.forEach((attr, i) => {
        ctx.fillText(attr, startX + i * cellSize + cellSize / 2, startY + cellSize / 2 + 4);
    });
    
    // Row labels (records)
    ctx.fillStyle = 'rgba(100, 200, 255, 0.7)';
    for (let i = 1; i < rows; i++) {
        ctx.fillText(`R${i}`, startX - 20, startY + i * cellSize + cellSize / 2 + 4);
    }
    
    ctx.restore();
    
    // Text
    ctx.font = 'bold 18px monospace';
    ctx.fillStyle = 'rgba(255, 255, 100, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('2D — THE PLANE', cx, cy - 160);
    
    ctx.font = '14px monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillText('Width means MEANING.', cx, cy + 160);
    ctx.fillText('Values now have ATTRIBUTES. Categories.', cx, cy + 185);
    
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(150, 150, 200, 0.6)';
    ctx.fillText('A table. A record. Rows and columns.', cx, cy + 220);
    ctx.fillText('Data becomes structured.', cx, cy + 240);
}

// Level 4: VOLUME - 3D Depth, change over time, complete unit
function renderVolume() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const size = 100;
    
    // 8 vertices of a cube (representing a complete data unit)
    const verts3D = [];
    for (let z = -1; z <= 1; z += 2) {
        for (let y = -1; y <= 1; y += 2) {
            for (let x = -1; x <= 1; x += 2) {
                verts3D.push({ x: x * size, y: y * size, z: z * size });
            }
        }
    }
    
    // Rotate
    const rotY = time * 0.3;
    const rotX = time * 0.2;
    
    const projected = verts3D.map(v => {
        let x = v.x * Math.cos(rotY) - v.z * Math.sin(rotY);
        let z = v.x * Math.sin(rotY) + v.z * Math.cos(rotY);
        let y = v.y * Math.cos(rotX) - z * Math.sin(rotX);
        z = v.y * Math.sin(rotX) + z * Math.cos(rotX);
        const scale = 400 / (400 - z);
        return { x: cx + x * scale, y: cy + y * scale, z, scale };
    });
    
    // Draw time layers (depth slices)
    const numSlices = 5;
    for (let s = 0; s < numSlices; s++) {
        const offset = (s - numSlices / 2) * 25;
        const alpha = 0.1 + (numSlices - s) * 0.05;
        
        ctx.strokeStyle = `rgba(100, 255, 100, ${alpha})`;
        ctx.lineWidth = 1;
        ctx.strokeRect(cx - 60 + offset * 0.3, cy - 60 + offset * 0.3, 120, 120);
    }
    
    // Edges of cube
    const edges = [
        [0,1],[2,3],[4,5],[6,7],
        [0,2],[1,3],[4,6],[5,7],
        [0,4],[1,5],[2,6],[3,7]
    ];
    
    edges.sort((a, b) => {
        const zA = (projected[a[0]].z + projected[a[1]].z) / 2;
        const zB = (projected[b[0]].z + projected[b[1]].z) / 2;
        return zA - zB;
    });
    
    edges.forEach(([i, j]) => {
        const p1 = projected[i];
        const p2 = projected[j];
        const avgZ = (p1.z + p2.z) / 2;
        const alpha = 0.4 + (avgZ + size) / (size * 2) * 0.4;
        
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = `rgba(100, 255, 100, ${alpha})`;
        ctx.lineWidth = 2;
        ctx.stroke();
    });
    
    // Vertices with data indication
    projected.sort((a, b) => a.z - b.z).forEach((p, i) => {
        const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, 15 * p.scale);
        gradient.addColorStop(0, '#64ff64');
        gradient.addColorStop(1, 'transparent');
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, 15 * p.scale, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, 5 * p.scale, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();
    });
    
    // Draw time arrow 
    ctx.beginPath();
    ctx.moveTo(cx + 180, cy - 80);
    ctx.lineTo(cx + 180, cy + 80);
    ctx.strokeStyle = 'rgba(100, 255, 100, 0.5)';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    ctx.fillStyle = 'rgba(100, 255, 100, 0.7)';
    ctx.beginPath();
    ctx.moveTo(cx + 180, cy + 90);
    ctx.lineTo(cx + 170, cy + 75);
    ctx.lineTo(cx + 190, cy + 75);
    ctx.fill();
    
    ctx.font = '10px monospace';
    ctx.fillStyle = 'rgba(100, 255, 100, 0.7)';
    ctx.textAlign = 'center';
    ctx.fillText('TIME', cx + 180, cy + 110);
    
    // Text
    ctx.font = 'bold 18px monospace';
    ctx.fillStyle = 'rgba(100, 255, 100, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('3D — THE VOLUME', cx, cy - 150);
    
    ctx.font = '14px monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillText('Depth emerges. Change over TIME.', cx, cy + 160);
    ctx.fillText('A COMPLETE UNIT.', cx, cy + 185);
    
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(150, 150, 200, 0.6)';
    ctx.fillText('Database records. State over time.', cx, cy + 220);
    ctx.fillText('Can be measured as a single point of higher dimension.', cx, cy + 240);
}

// Level 5: 4D TESSERACT - An entire system/app
function renderTesseract() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // Get transformed tesseract vertices
    const vertices4D = tesseract.getTransformedVertices(
        time * 0.1,
        0,
        rotXW,
        rotYW
    );
    
    // Project 4D → 3D → 2D
    const projected = vertices4D.map(v => {
        const v3D = v.project3D(2.5);
        return camera.project(v3D);
    });
    
    // Draw "system" background elements
    for (let i = 0; i < 8; i++) {
        const angle = time * 0.2 + i * Math.PI / 4;
        const dist = 200 + Math.sin(time + i) * 20;
        const px = cx + Math.cos(angle) * dist;
        const py = cy + Math.sin(angle) * dist;
        
        ctx.beginPath();
        ctx.arc(px, py, 3, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(100, 200, 255, 0.3)';
        ctx.fill();
        
        // Connection to center
        ctx.beginPath();
        ctx.moveTo(px, py);
        ctx.lineTo(cx, cy);
        ctx.strokeStyle = 'rgba(100, 200, 255, 0.1)';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
    
    // Draw edges (sorted by depth)
    const sortedEdges = [...tesseract.edges].sort((a, b) => {
        const zA = (projected[a[0]].z + projected[a[1]].z) / 2;
        const zB = (projected[b[0]].z + projected[b[1]].z) / 2;
        return zA - zB;
    });
    
    sortedEdges.forEach(([i, j]) => {
        const p1 = projected[i];
        const p2 = projected[j];
        const w1 = vertices4D[i].w;
        const w2 = vertices4D[j].w;
        const wAvg = (w1 + w2) / 2;
        
        const r = Math.floor(100 + (wAvg + 1) * 77);
        const g = Math.floor(180 - Math.abs(wAvg) * 30);
        const b = 255;
        
        const avgZ = (p1.z + p2.z) / 2;
        const alpha = 0.4 + (avgZ + 2) * 0.15;
        
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.lineWidth = 2 * ((p1.scale + p2.scale) / 2);
        ctx.stroke();
    });
    
    // Draw vertices with component labels
    const components = ['UI', 'API', 'DB', 'Auth', 'Log', 'Cache', 'Queue', 'Core', 
                        'Net', 'Store', 'Events', 'State', 'Config', 'Router', 'Render', 'Ctrl'];
    projected.forEach((p, i) => {
        const w = vertices4D[i].w;
        const size = 4 * p.scale;
        const hue = 200 + w * 30;
        const lightness = 55 + w * 10;
        
        // Glow
        const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, size * 3);
        gradient.addColorStop(0, `hsla(${hue}, 80%, ${lightness}%, 1)`);
        gradient.addColorStop(0.5, `hsla(${hue}, 80%, ${lightness}%, 0.3)`);
        gradient.addColorStop(1, 'transparent');
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, size * 3, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();
        
        // Component label
        ctx.font = '9px monospace';
        ctx.fillStyle = `hsla(${hue}, 70%, 80%, 0.8)`;
        ctx.textAlign = 'center';
        ctx.fillText(components[i] || '', p.x, p.y - size * 2);
    });
    
    // Text
    ctx.font = 'bold 18px monospace';
    ctx.fillStyle = 'rgba(100, 200, 255, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('4D — THE SYSTEM', cx, cy - 180);
    
    ctx.font = '14px monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillText('An ENTIRE APPLICATION.', cx, cy + 200);
    ctx.fillText('16 components. Interconnected. Complete.', cx, cy + 225);
    
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(150, 150, 200, 0.6)';
    ctx.fillText('The tesseract: a self-contained system.', cx, cy + 260);
    ctx.fillText('Ready to connect to other systems.', cx, cy + 280);
}

// Level 6: NETWORK - Multiple connected systems
function renderParallel() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // System names for each tesseract
    const systems = ['SYSTEM A', 'SYSTEM B', 'SYSTEM C'];
    const systemTypes = ['Database', 'API Server', 'Frontend'];
    
    // Draw 3 connected tesseracts representing networked systems
    const offsets = [-200, 0, 200];
    const phases = [0, Math.PI / 3, Math.PI * 2 / 3];
    
    // First draw connection lines between systems
    ctx.save();
    
    // Data packets flowing between systems
    const packetCount = 8;
    for (let p = 0; p < packetCount; p++) {
        const progress = ((time * 0.3 + p / packetCount) % 1);
        const fromIdx = Math.floor(p / 3) % 3;
        const toIdx = (fromIdx + 1) % 3;
        
        const x = cx + offsets[fromIdx] + (offsets[toIdx] - offsets[fromIdx]) * progress;
        const y = cy + Math.sin(progress * Math.PI) * -30;
        
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 8);
        gradient.addColorStop(0, 'rgba(0, 255, 200, 0.9)');
        gradient.addColorStop(1, 'transparent');
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
    }
    
    // Network links
    ctx.setLineDash([8, 4]);
    ctx.lineWidth = 2;
    for (let i = 0; i < offsets.length; i++) {
        for (let j = i + 1; j < offsets.length; j++) {
            const pulse = Math.sin(time * 2 + i + j) * 0.3 + 0.5;
            ctx.strokeStyle = `rgba(0, 255, 200, ${pulse * 0.4})`;
            ctx.beginPath();
            ctx.moveTo(cx + offsets[i], cy);
            ctx.quadraticCurveTo(cx + (offsets[i] + offsets[j]) / 2, cy - 40, cx + offsets[j], cy);
            ctx.stroke();
        }
    }
    ctx.setLineDash([]);
    ctx.restore();
    
    // Draw each tesseract system
    offsets.forEach((offset, idx) => {
        const vertices4D = tesseract.getTransformedVertices(
            time * 0.08 + phases[idx],
            0,
            rotXW + phases[idx] * 0.3,
            rotYW
        );
        
        const projected = vertices4D.map(v => {
            const v3D = v.project3D(3);
            const p = camera.project(v3D);
            return { x: p.x * 0.5 + offset, y: p.y * 0.5, z: p.z, scale: p.scale };
        });
        
        // Draw edges
        const sortedEdges = [...tesseract.edges].sort((a, b) => {
            const zA = (projected[a[0]].z + projected[a[1]].z) / 2;
            const zB = (projected[b[0]].z + projected[b[1]].z) / 2;
            return zA - zB;
        });
        
        const hues = [180, 220, 280]; // Cyan, Blue, Purple
        sortedEdges.forEach(([i, j]) => {
            const p1 = projected[i];
            const p2 = projected[j];
            const avgZ = (p1.z + p2.z) / 2;
            const alpha = 0.3 + (avgZ + 2) * 0.15;
            
            ctx.beginPath();
            ctx.moveTo(p1.x + cx, p1.y + cy);
            ctx.lineTo(p2.x + cx, p2.y + cy);
            ctx.strokeStyle = `hsla(${hues[idx]}, 70%, 60%, ${alpha})`;
            ctx.lineWidth = 1.5;
            ctx.stroke();
        });
        
        // System label below each tesseract
        ctx.font = 'bold 11px monospace';
        ctx.fillStyle = `hsla(${hues[idx]}, 70%, 70%, 0.9)`;
        ctx.textAlign = 'center';
        ctx.fillText(systems[idx], cx + offset, cy + 100);
        ctx.font = '10px monospace';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.fillText(systemTypes[idx], cx + offset, cy + 115);
    });
    
    // Title
    ctx.font = 'bold 18px monospace';
    ctx.fillStyle = 'rgba(0, 255, 200, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('5D — THE NETWORK', cx, cy - 160);
    
    ctx.font = '14px monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillText('Systems CONNECT to other systems.', cx, cy + 180);
    ctx.fillText('Data flows. Services communicate.', cx, cy + 200);
    
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(150, 200, 180, 0.6)';
    ctx.fillText('Each tesseract is a complete application.', cx, cy + 240);
    ctx.fillText('Together they form something greater.', cx, cy + 260);
}

// Level 7: INTERNET - The network of all networks
function renderMeta() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // Draw a global network visualization
    // Multiple clusters representing different networks, all interconnected
    
    // Network clusters around the globe
    const clusters = [
        { x: 0, y: -100, name: 'NAM', color: '#ff6464', nodes: 5 },
        { x: 150, y: -30, name: 'EUR', color: '#64ff64', nodes: 6 },
        { x: -150, y: -30, name: 'ASIA', color: '#6464ff', nodes: 7 },
        { x: 100, y: 100, name: 'AFR', color: '#ffff64', nodes: 4 },
        { x: -100, y: 100, name: 'SAM', color: '#ff64ff', nodes: 4 },
        { x: 0, y: 0, name: 'CORE', color: '#64ffff', nodes: 8 }
    ];
    
    // Draw global orbital ring
    ctx.beginPath();
    ctx.ellipse(cx, cy, 250, 100, 0, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(100, 200, 255, 0.15)';
    ctx.lineWidth = 40;
    ctx.stroke();
    
    // Draw inter-cluster connections first (backbone)
    ctx.lineWidth = 1;
    for (let i = 0; i < clusters.length; i++) {
        for (let j = i + 1; j < clusters.length; j++) {
            const c1 = clusters[i];
            const c2 = clusters[j];
            const pulse = Math.sin(time * 1.5 + i * 0.7 + j * 0.3) * 0.3 + 0.4;
            
            ctx.beginPath();
            ctx.moveTo(cx + c1.x, cy + c1.y);
            // Curved connection
            const midX = (c1.x + c2.x) / 2;
            const midY = (c1.y + c2.y) / 2 - 30;
            ctx.quadraticCurveTo(cx + midX, cy + midY, cx + c2.x, cy + c2.y);
            ctx.strokeStyle = `rgba(255, 255, 255, ${pulse * 0.2})`;
            ctx.stroke();
        }
    }
    
    // Draw packets flowing on backbone
    const packetCount = 20;
    for (let p = 0; p < packetCount; p++) {
        const fromCluster = clusters[p % clusters.length];
        const toCluster = clusters[(p + 1) % clusters.length];
        const progress = ((time * 0.4 + p * 0.15) % 1);
        
        const x = cx + fromCluster.x + (toCluster.x - fromCluster.x) * progress;
        const y = cy + fromCluster.y + (toCluster.y - fromCluster.y) * progress;
        const lift = Math.sin(progress * Math.PI) * -20;
        
        const gradient = ctx.createRadialGradient(x, y + lift, 0, x, y + lift, 5);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
        gradient.addColorStop(1, 'transparent');
        ctx.beginPath();
        ctx.arc(x, y + lift, 4, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
    }
    
    // Draw each cluster with its nodes
    clusters.forEach((cluster, ci) => {
        const clusterX = cx + cluster.x;
        const clusterY = cy + cluster.y;
        
        // Draw nodes in this cluster
        for (let n = 0; n < cluster.nodes; n++) {
            const angle = (n / cluster.nodes) * Math.PI * 2 + time * 0.2 + ci;
            const dist = 25 + (n % 2) * 10;
            const nx = clusterX + Math.cos(angle) * dist;
            const ny = clusterY + Math.sin(angle) * dist * 0.6;
            
            // Intra-cluster connections
            const prevAngle = ((n - 1 + cluster.nodes) / cluster.nodes) * Math.PI * 2 + time * 0.2 + ci;
            const px = clusterX + Math.cos(prevAngle) * (25 + ((n - 1 + cluster.nodes) % 2) * 10);
            const py = clusterY + Math.sin(prevAngle) * (25 + ((n - 1 + cluster.nodes) % 2) * 10) * 0.6;
            
            ctx.beginPath();
            ctx.moveTo(px, py);
            ctx.lineTo(nx, ny);
            ctx.strokeStyle = cluster.color + '40';
            ctx.lineWidth = 1;
            ctx.stroke();
            
            // Node
            const gradient = ctx.createRadialGradient(nx, ny, 0, nx, ny, 6);
            gradient.addColorStop(0, cluster.color);
            gradient.addColorStop(1, 'transparent');
            ctx.beginPath();
            ctx.arc(nx, ny, 4, 0, Math.PI * 2);
            ctx.fillStyle = gradient;
            ctx.fill();
        }
        
        // Cluster center
        const centerGrad = ctx.createRadialGradient(clusterX, clusterY, 0, clusterX, clusterY, 20);
        centerGrad.addColorStop(0, cluster.color + '60');
        centerGrad.addColorStop(1, 'transparent');
        ctx.beginPath();
        ctx.arc(clusterX, clusterY, 15, 0, Math.PI * 2);
        ctx.fillStyle = centerGrad;
        ctx.fill();
        
        // Cluster label
        ctx.font = 'bold 9px monospace';
        ctx.fillStyle = cluster.color;
        ctx.textAlign = 'center';
        ctx.fillText(cluster.name, clusterX, clusterY + 45);
    });
    
    // Central core pulse
    const coreRadius = 20 + Math.sin(time * 2) * 5;
    const coreGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreRadius * 2);
    coreGrad.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
    coreGrad.addColorStop(0.5, 'rgba(100, 200, 255, 0.3)');
    coreGrad.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.arc(cx, cy, coreRadius, 0, Math.PI * 2);
    ctx.fillStyle = coreGrad;
    ctx.fill();
    
    // Title
    ctx.font = 'bold 18px monospace';
    ctx.fillStyle = 'rgba(255, 200, 100, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('6D — THE INTERNET', cx, cy - 180);
    
    ctx.font = '14px monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillText('The NETWORK of networks.', cx, cy + 180);
    ctx.fillText('Every system, every connection, UNIFIED.', cx, cy + 200);
    
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(200, 180, 150, 0.6)';
    ctx.fillText('Data flows everywhere, instantly.', cx, cy + 240);
    ctx.fillText('The substrate upon which all digital life exists.', cx, cy + 260);
}

function drawHelixSpiral() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    ctx.beginPath();
    for (let t = 0; t < Math.PI * 4; t += 0.05) {
        const radius = 30 + t * 8;
        const x = cx + Math.cos(t + time * 0.5) * radius * Math.cos(camera.rotY);
        const y = cy + Math.sin(t + time * 0.5) * radius * Math.cos(camera.rotX) - t * 5;
        
        if (t === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    
    const gradient = ctx.createLinearGradient(cx - 100, cy - 100, cx + 100, cy + 100);
    gradient.addColorStop(0, 'rgba(64, 96, 255, 0.3)');
    gradient.addColorStop(0.5, 'rgba(150, 64, 255, 0.3)');
    gradient.addColorStop(1, 'rgba(255, 64, 128, 0.3)');
    
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 2;
    ctx.stroke();
}

// =========================
// Manifold API Integration
// =========================

// Store dimensional coordinates for visualization
let myDimensionalCoords = { x: 127, y: 0, z: 0, m: 1 };

async function fetchManifoldData() {
    try {
        const response = await fetch('/api/manifold/evaluate?x=0&y=0&z=0');
        if (response.ok) {
            const data = await response.json();
            console.log('Manifold data:', data);
        }
    } catch (e) {
        console.log('Manifold API not available, running in demo mode');
    }
}

// Fetch dimensional IP coordinates
async function fetchDimensionalIP() {
    try {
        const response = await fetch('/api/dimensional/encode?ip=0.0.0.0');
        if (response.ok) {
            const data = await response.json();
            if (data.client_dimensional) {
                const cd = data.client_dimensional;
                myDimensionalCoords = cd.dimensional;
                
                document.getElementById('my-ip').textContent = cd.ip;
                document.getElementById('dim-x').textContent = cd.dimensional.x;
                document.getElementById('dim-y').textContent = cd.dimensional.y;
                document.getElementById('dim-z').textContent = cd.dimensional.z;
                document.getElementById('dim-m').textContent = cd.dimensional.m;
                document.getElementById('substrate-r').textContent = cd.substrate_r;
                document.getElementById('manifold-uri').textContent = cd.manifold_uri;
                
                // Update content panels with real IP data
                updateContentPanelsWithIP(cd);
            }
        }
    } catch (e) {
        console.log('Dimensional IP API not available');
    }
}

// Fetch benchmarks
async function fetchBenchmarks() {
    try {
        const response = await fetch('/api/dimensional/benchmark?iterations=200');
        if (response.ok) {
            const data = await response.json();
            if (data.benchmarks) {
                const html = Object.entries(data.benchmarks).map(([name, bench]) => `
                    <div class="bench-row">
                        <span>${bench.operation}</span>
                        <span class="bench-value">${bench.avg_latency_us.toFixed(1)}μs</span>
                    </div>
                `).join('');
                document.getElementById('bench-content').innerHTML = html;
            }
        }
    } catch (e) {
        document.getElementById('bench-content').innerHTML = '<span style="color:#6080aa">Offline mode</span>';
    }
}

// Update content panels with dimensional IP info
function updateContentPanelsWithIP(clientData) {
    const panels = document.querySelectorAll('.content-panel');
    if (panels[0]) {
        panels[0].innerHTML = `
            <h2>Your Manifold Origin</h2>
            <p>You exist at position <strong>${clientData.substrate_r}</strong> in the 4D network manifold. 
            Your normalized Vec4: (${clientData.vec4_normalized.x.toFixed(3)}, ${clientData.vec4_normalized.y.toFixed(3)}, 
            ${clientData.vec4_normalized.z.toFixed(3)}, ${clientData.vec4_normalized.w.toFixed(3)})</p>
        `;
    }
    if (panels[1]) {
        panels[1].innerHTML = `
            <h2>The Network IS Geometry</h2>
            <p>IP addresses are dimensional coordinates. The internet is not a series of tubes — 
            it is a 4-dimensional manifold where ${clientData.ip} becomes the point 
            (${clientData.dimensional.x}, ${clientData.dimensional.y}, ${clientData.dimensional.z}, ${clientData.dimensional.m}).</p>
        `;
    }
    if (panels[2]) {
        panels[2].innerHTML = `
            <h2>Manifold Addressing</h2>
            <p>Your URI in manifold space: <strong>${clientData.manifold_uri}</strong><br>
            Routing is geodesic — packets follow the shortest path through curved dimensional space.</p>
        `;
    }
}

// =========================
// Initialize
// =========================

fetchManifoldData();
fetchDimensionalIP();
fetchBenchmarks();
render();

// Refresh dimensional data periodically
setInterval(fetchDimensionalIP, 60000);

// Helix level click handlers
document.querySelectorAll('.helix-level').forEach(el => {
    el.addEventListener('click', () => {
        document.querySelectorAll('.helix-level').forEach(e => e.classList.remove('active'));
        el.classList.add('active');
        
        // Extract level number from class (level-1, level-2, etc.)
        const levelClass = [...el.classList].find(c => c.startsWith('level-'));
        if (levelClass) {
            currentLevel = parseInt(levelClass.split('-')[1]);
            console.log(`Switching to Helix Level ${currentLevel}: ${HELIX_LEVELS[currentLevel].name}`);
        }
    });
});

console.log(`
╔══════════════════════════════════════════════════╗
║          ButterflyFX 4D Website Demo             ║
║                                                  ║
║  "The payload is the model.                      ║
║   The network is the manifold."                  ║
║                                                  ║
║  Dimensions active: X, Y, Z, W (Time)            ║
║  Tesseract vertices: 16                          ║
║  Tesseract edges: 32                             ║
║  Helix level: 4 (VOLUME + TIME)                  ║
╚══════════════════════════════════════════════════╝
`);
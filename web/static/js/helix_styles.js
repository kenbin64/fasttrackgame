/**
 * ButterflyFX HelixStyles - Substrate Rendering Engine
 * 
 * Copyright (c) 2024-2026 Kenneth Bingham
 * Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
 * https://creativecommons.org/licenses/by/4.0/
 * 
 * Attribution required: Kenneth Bingham - https://butterflyfx.us
 * 
 * This is NOT CSS animation. This is dimensional substrate presentation where:
 * - Visual elements exist as tokens in the helix manifold
 * - Animations are spiral movements through dimensional levels
 * - Text/images decompose into particle swarms
 * - Each render is mathematically unique via phi-based seeds
 */

// =============================================================================
// MATHEMATICAL CONSTANTS
// =============================================================================

const PHI = (1 + Math.sqrt(5)) / 2;  // Golden ratio ≈ 1.618
const TAU = Math.PI * 2;
const FIBONACCI = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610];

// Level definitions
const VISUAL_LEVELS = {
    POTENTIAL: 0,  // Invisible
    POINT: 1,      // Single point
    LENGTH: 2,     // Lines/strokes
    WIDTH: 3,      // Outlines
    PLANE: 4,      // Filled shapes
    VOLUME: 5,     // 3D effects
    WHOLE: 6       // Full 4D immersion
};

const LEVEL_OPACITY = [0, 0.1, 0.3, 0.6, 0.9, 1.0, 1.0];
const LEVEL_BLUR = [20, 15, 10, 5, 2, 0, 0];

// =============================================================================
// HELIX COLOR CLASS
// =============================================================================

class HelixColor {
    constructor(angle = 0, radius = 1, spiral = 0, level = 6) {
        this.angle = angle;    // Hue as radians around helix
        this.radius = radius;  // Saturation
        this.spiral = spiral;  // Lightness
        this.level = level;    // Alpha/complexity
    }
    
    toRGB() {
        const hue = ((this.angle % TAU) / TAU + 1) % 1;
        const sat = Math.min(1, Math.max(0, this.radius));
        const light = 0.5 + 0.4 * Math.tanh(this.spiral / 3);
        
        return this._hslToRgb(hue, sat, light);
    }
    
    toRGBA() {
        const [r, g, b] = this.toRGB();
        const alpha = LEVEL_OPACITY[this.level];
        return [r, g, b, alpha];
    }
    
    toCSS() {
        const [r, g, b, a] = this.toRGBA();
        return `rgba(${r}, ${g}, ${b}, ${a})`;
    }
    
    toHex() {
        const [r, g, b] = this.toRGB();
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }
    
    spiralTo(target, t) {
        // Phi-based spiral interpolation
        const phiT = (1 - Math.cos(t * Math.PI * PHI)) / 2;
        return new HelixColor(
            this.angle + (target.angle - this.angle) * phiT,
            this.radius + (target.radius - this.radius) * phiT,
            this.spiral + (target.spiral - this.spiral) * phiT,
            Math.round(this.level + (target.level - this.level) * phiT)
        );
    }
    
    _hslToRgb(h, s, l) {
        let r, g, b;
        if (s === 0) {
            r = g = b = Math.round(l * 255);
        } else {
            const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1/6) return p + (q - p) * 6 * t;
                if (t < 1/2) return q;
                if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                return p;
            };
            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = Math.round(hue2rgb(p, q, h + 1/3) * 255);
            g = Math.round(hue2rgb(p, q, h) * 255);
            b = Math.round(hue2rgb(p, q, h - 1/3) * 255);
        }
        return [r, g, b];
    }
    
    static fromRGB(r, g, b, level = 6) {
        // RGB to HSL
        const rn = r / 255, gn = g / 255, bn = b / 255;
        const max = Math.max(rn, gn, bn);
        const min = Math.min(rn, gn, bn);
        const l = (max + min) / 2;
        
        let h, s;
        if (max === min) {
            h = s = 0;
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case rn: h = ((gn - bn) / d + (gn < bn ? 6 : 0)) / 6; break;
                case gn: h = ((bn - rn) / d + 2) / 6; break;
                case bn: h = ((rn - gn) / d + 4) / 6; break;
            }
        }
        
        return new HelixColor(h * TAU, s, (l - 0.5) * 3 / 0.4, level);
    }
    
    static rainbow(t, level = 6) {
        return new HelixColor(t * TAU, 1, 0, level);
    }
}


// =============================================================================
// PARTICLE CLASS
// =============================================================================

class Particle {
    constructor(options = {}) {
        this.id = options.id || Math.random().toString(36).substr(2, 9);
        this.content = options.content || '';
        
        // Position
        this.x = options.x || 0;
        this.y = options.y || 0;
        this.z = options.z || 0;
        
        // Target position (for formations)
        this.targetX = this.x;
        this.targetY = this.y;
        this.targetZ = this.z;
        
        // Velocity
        this.vx = options.vx || 0;
        this.vy = options.vy || 0;
        this.vz = options.vz || 0;
        
        // Helix properties
        this.level = options.level || 6;
        this.spiral = options.spiral || 0;
        
        // Visual
        this.color = options.color || new HelixColor(Math.random() * TAU, 1, 0, 6);
        this.scale = options.scale || 1;
        this.rotation = options.rotation || 0;
        this.opacity = options.opacity || 1;
        
        // Physics
        this.mass = options.mass || 1;
        this.drag = options.drag || 0.02;
        this.attractStrength = options.attractStrength || 0.05;
        
        // State
        this.isAlive = true;
        this.age = 0;
        this.lifespan = options.lifespan || Infinity;
    }
    
    update(dt) {
        if (!this.isAlive) return;
        
        this.age += dt;
        if (this.age > this.lifespan) {
            this.opacity *= 0.9;
            if (this.opacity < 0.01) {
                this.isAlive = false;
            }
        }
        
        // Attract to target
        const dx = this.targetX - this.x;
        const dy = this.targetY - this.y;
        const dz = this.targetZ - this.z;
        const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 0.001;
        
        const force = this.attractStrength / this.mass;
        this.vx += (dx / dist) * force;
        this.vy += (dy / dist) * force;
        this.vz += (dz / dist) * force;
        
        // Apply drag
        this.vx *= (1 - this.drag);
        this.vy *= (1 - this.drag);
        this.vz *= (1 - this.drag);
        
        // Update position
        this.x += this.vx * dt * 60;
        this.y += this.vy * dt * 60;
        this.z += this.vz * dt * 60;
        
        // Update rotation
        this.rotation += (this.vx + this.vy) * 0.01;
    }
    
    attractTo(tx, ty, tz, strength = null) {
        this.targetX = tx;
        this.targetY = ty;
        this.targetZ = tz;
        if (strength !== null) {
            this.attractStrength = strength;
        }
    }
    
    applyForce(fx, fy, fz) {
        this.vx += fx / this.mass;
        this.vy += fy / this.mass;
        this.vz += fz / this.mass;
    }
    
    render(ctx, offsetX = 0, offsetY = 0) {
        if (!this.isAlive || this.opacity < 0.01) return;
        
        ctx.save();
        
        // 3D projection (simple perspective)
        const perspective = 1000;
        const scale3d = perspective / (perspective + this.z);
        const screenX = this.x * scale3d + offsetX;
        const screenY = this.y * scale3d + offsetY;
        
        ctx.globalAlpha = this.opacity * LEVEL_OPACITY[this.level] * scale3d;
        ctx.translate(screenX, screenY);
        ctx.rotate(this.rotation);
        ctx.scale(this.scale * scale3d, this.scale * scale3d);
        
        // Apply level-based blur (via shadow blur approximation)
        const blur = LEVEL_BLUR[this.level];
        if (blur > 0) {
            ctx.shadowBlur = blur;
            ctx.shadowColor = this.color.toCSS();
        }
        
        ctx.fillStyle = this.color.toCSS();
        ctx.font = '20px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.content, 0, 0);
        
        ctx.restore();
    }
}


// =============================================================================
// PARTICLE SWARM CLASS
// =============================================================================

class ParticleSwarm {
    constructor() {
        this.particles = [];
        this.formation = 'scattered';
        this.centerX = 0;
        this.centerY = 0;
        this.cohesion = 0.001;
        this.separation = 0.02;
        this.alignment = 0.01;
    }
    
    static fromText(text, options = {}) {
        const swarm = new ParticleSwarm();
        const startX = options.x || 0;
        const startY = options.y || 0;
        const charSpacing = options.charSpacing || 18;
        const lineHeight = options.lineHeight || 30;
        const baseColor = options.color || new HelixColor(0, 1, 0, 6);
        
        let currX = startX;
        let currY = startY;
        let charIndex = 0;
        
        for (const char of text) {
            if (char === '\n') {
                currX = startX;
                currY += lineHeight;
                continue;
            }
            
            // Each character gets a unique color based on position
            const charColor = new HelixColor(
                baseColor.angle + charIndex * 0.05,
                baseColor.radius,
                baseColor.spiral,
                baseColor.level
            );
            
            swarm.particles.push(new Particle({
                id: `char_${charIndex}`,
                content: char,
                x: currX,
                y: currY,
                z: 0,
                color: charColor,
                level: 6
            }));
            
            currX += charSpacing;
            charIndex++;
        }
        
        swarm.formation = 'text';
        swarm.updateCenter();
        return swarm;
    }
    
    updateCenter() {
        if (this.particles.length === 0) return;
        let sumX = 0, sumY = 0;
        for (const p of this.particles) {
            sumX += p.x;
            sumY += p.y;
        }
        this.centerX = sumX / this.particles.length;
        this.centerY = sumY / this.particles.length;
    }
    
    explode(strength = 100, centerX = null, centerY = null) {
        const cx = centerX ?? this.centerX;
        const cy = centerY ?? this.centerY;
        
        for (const p of this.particles) {
            const dx = p.x - cx;
            const dy = p.y - cy;
            const dist = Math.sqrt(dx*dx + dy*dy) + 0.001;
            const randomFactor = 0.5 + Math.random();
            
            p.vx += (dx / dist) * strength * randomFactor;
            p.vy += (dy / dist) * strength * randomFactor;
            p.vz += (Math.random() - 0.5) * strength * 0.5;
            
            // Random rotation on explode
            p.rotation = Math.random() * TAU;
        }
        
        this.formation = 'scattered';
    }
    
    implode(targetX, targetY, strength = 0.1) {
        for (const p of this.particles) {
            p.attractTo(targetX, targetY, 0, strength);
        }
    }
    
    morphToText(newText, charSpacing = 18, startX = 0, startY = 0) {
        const targets = [];
        let x = startX, y = startY;
        
        for (const char of newText) {
            if (char === '\n') {
                x = startX;
                y += 30;
                continue;
            }
            targets.push({ x, y, char });
            x += charSpacing;
        }
        
        // Match existing particles to new targets
        for (let i = 0; i < Math.max(this.particles.length, targets.length); i++) {
            if (i < this.particles.length && i < targets.length) {
                // Update existing particle
                const p = this.particles[i];
                const t = targets[i];
                p.content = t.char;
                p.attractTo(t.x, t.y, 0, 0.08);
                p.opacity = 1;
            } else if (i >= this.particles.length) {
                // Need new particle
                const t = targets[i];
                const newP = new Particle({
                    content: t.char,
                    x: this.centerX + (Math.random() - 0.5) * 200,
                    y: this.centerY + (Math.random() - 0.5) * 200,
                    z: Math.random() * 100 - 50,
                    level: 6
                });
                newP.attractTo(t.x, t.y, 0, 0.08);
                this.particles.push(newP);
            } else {
                // Fade out excess particle
                this.particles[i].opacity *= 0.95;
                this.particles[i].lifespan = 0;
            }
        }
        
        this.formation = 'text';
    }
    
    spiralFormation(centerX, centerY, radius = 100) {
        const n = this.particles.length;
        for (let i = 0; i < n; i++) {
            const p = this.particles[i];
            const t = (i / n) * TAU * 3;  // 3 full rotations
            const r = radius * (0.5 + (i / n) * 0.5);
            
            p.attractTo(
                centerX + r * Math.cos(t),
                centerY + r * Math.sin(t),
                i * 3,  // Rising helix
                0.03
            );
        }
        this.formation = 'helix';
    }
    
    sphereFormation(centerX, centerY, centerZ, radius = 100) {
        const n = this.particles.length;
        const goldenAngle = Math.PI * (3 - Math.sqrt(5));  // Golden angle
        
        for (let i = 0; i < n; i++) {
            const y = 1 - (i / (n - 1)) * 2;  // y goes from 1 to -1
            const radiusAtY = Math.sqrt(1 - y * y);
            const theta = goldenAngle * i;
            
            const px = centerX + radius * radiusAtY * Math.cos(theta);
            const py = centerY + radius * y;
            const pz = centerZ + radius * radiusAtY * Math.sin(theta);
            
            this.particles[i].attractTo(px, py, pz, 0.04);
        }
        this.formation = 'sphere';
    }
    
    waveFormation(centerX, centerY, width = 500, amplitude = 50, frequency = 2) {
        const n = this.particles.length;
        const time = Date.now() * 0.001;
        
        for (let i = 0; i < n; i++) {
            const p = this.particles[i];
            const x = centerX - width / 2 + (i / n) * width;
            const phase = (i / n) * frequency * TAU + time;
            const y = centerY + Math.sin(phase) * amplitude;
            const z = Math.cos(phase * PHI) * amplitude * 0.5;
            
            p.attractTo(x, y, z, 0.05);
        }
        this.formation = 'wave';
    }
    
    applyLevelTransition(fromLevel, toLevel, progress) {
        const currentLevel = Math.round(fromLevel + (toLevel - fromLevel) * progress);
        for (const p of this.particles) {
            p.level = currentLevel;
            p.opacity = LEVEL_OPACITY[currentLevel];
        }
    }
    
    update(dt) {
        // Apply swarm behaviors
        this._applySeparation();
        
        // Update each particle
        for (const p of this.particles) {
            p.update(dt);
        }
        
        // Remove dead particles
        this.particles = this.particles.filter(p => p.isAlive);
        
        this.updateCenter();
    }
    
    _applySeparation() {
        const minDist = 15;
        for (let i = 0; i < this.particles.length; i++) {
            const p1 = this.particles[i];
            for (let j = i + 1; j < this.particles.length; j++) {
                const p2 = this.particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                
                if (dist < minDist && dist > 0) {
                    const force = (minDist - dist) / dist * this.separation;
                    p1.vx += dx * force;
                    p1.vy += dy * force;
                    p2.vx -= dx * force;
                    p2.vy -= dy * force;
                }
            }
        }
    }
    
    render(ctx, offsetX = 0, offsetY = 0) {
        // Sort by z for proper depth ordering
        const sorted = [...this.particles].sort((a, b) => a.z - b.z);
        for (const p of sorted) {
            p.render(ctx, offsetX, offsetY);
        }
    }
}


// =============================================================================
// SUBSTRATE ELEMENT
// =============================================================================

class SubstrateElement {
    constructor(options = {}) {
        this.id = options.id || Math.random().toString(36).substr(2, 9);
        this.type = options.type || 'text';
        this.content = options.content || '';
        
        // Helix position
        this.level = options.level || 6;
        this.spiral = options.spiral || 0;
        this.angle = options.angle || 0;
        
        // Signature (which levels this element exists at)
        this.signature = options.signature || new Set([4, 5, 6]);
        
        // Visual properties (derived from helix position)
        this.color = options.color || new HelixColor(this.angle, 1, this.spiral, this.level);
        
        // Particle decomposition
        this.particles = null;
        this.isDecomposed = false;
        
        // DOM reference (if any)
        this.domElement = null;
        
        // Transitions
        this.transitions = [];
    }
    
    getVisuals() {
        const opacity = LEVEL_OPACITY[this.level];
        const blur = LEVEL_BLUR[this.level];
        const scale = Math.pow(PHI, this.spiral * 0.1);
        const zDepth = this.spiral * 10;
        const glowIntensity = this.level >= 5 ? 0.3 : 0;
        
        return {
            opacity,
            blur,
            scale,
            zDepth,
            glowIntensity,
            shadowDepth: zDepth * 0.5,
            color: this.color
        };
    }
    
    spiralUp() {
        if (this.level < 6) this.level++;
        this.color.level = this.level;
        return this;
    }
    
    spiralDown() {
        if (this.level > 0) this.level--;
        this.color.level = this.level;
        return this;
    }
    
    invokeAt(level) {
        this.level = Math.max(0, Math.min(6, level));
        this.color.level = this.level;
        return this;
    }
    
    decompose() {
        if (this.type === 'text' && this.content && !this.isDecomposed) {
            this.particles = ParticleSwarm.fromText(this.content, {
                color: this.color
            });
            this.isDecomposed = true;
        }
        return this;
    }
    
    recompose() {
        this.isDecomposed = false;
        return this;
    }
    
    toCSS() {
        const v = this.getVisuals();
        return {
            opacity: v.opacity,
            filter: `blur(${v.blur}px)`,
            transform: `scale(${v.scale}) translateZ(${v.zDepth}px)`,
            color: v.color.toCSS(),
            boxShadow: v.glowIntensity > 0 
                ? `0 0 ${v.glowIntensity * 30}px ${v.color.toCSS()}` 
                : 'none'
        };
    }
    
    applyToDOM(element = null) {
        const el = element || this.domElement;
        if (!el) return;
        
        const css = this.toCSS();
        Object.assign(el.style, css);
    }
}


// =============================================================================
// HELIX TRANSITION
// =============================================================================

class HelixTransition {
    constructor(options = {}) {
        this.type = options.type || 'spiralUp';
        this.duration = options.duration || 1000;  // ms
        this.fromLevel = options.fromLevel || 0;
        this.toLevel = options.toLevel || 6;
        this.phiFactor = options.phiFactor || PHI;
        
        this.startTime = null;
        this.progress = 0;
        this.isComplete = false;
        this.onUpdate = options.onUpdate || null;
        this.onComplete = options.onComplete || null;
    }
    
    start() {
        this.startTime = performance.now();
        this.progress = 0;
        this.isComplete = false;
    }
    
    update(currentTime = null) {
        if (this.isComplete) return 1;
        
        const now = currentTime || performance.now();
        const elapsed = now - this.startTime;
        this.progress = Math.min(1, elapsed / this.duration);
        
        const eased = this._phiEase(this.progress);
        
        if (this.onUpdate) {
            this.onUpdate(eased, this.getCurrentLevel());
        }
        
        if (this.progress >= 1) {
            this.isComplete = true;
            if (this.onComplete) {
                this.onComplete();
            }
        }
        
        return eased;
    }
    
    _phiEase(t) {
        if (t <= 0) return 0;
        if (t >= 1) return 1;
        
        // Phi-based easing - creates organic spiral movement
        return (
            0.5 * (1 - Math.cos(t * Math.PI)) +
            0.3 * Math.sin(t * Math.PI * this.phiFactor) * (1 - t) +
            0.2 * t * t * (3 - 2 * t)
        );
    }
    
    getCurrentLevel() {
        const eased = this._phiEase(this.progress);
        return this.fromLevel + (this.toLevel - this.fromLevel) * eased;
    }
}


// =============================================================================
// MANIFOLD SKIN (Theme)
// =============================================================================

class ManifoldSkin {
    constructor(name, options = {}) {
        this.name = name;
        this.radiusScale = options.radiusScale || 1;
        this.pitchScale = options.pitchScale || PHI;
        
        this.levelColors = options.levelColors || {};
        this.levelBlur = options.levelBlur || {};
        this.levelGlow = options.levelGlow || {};
        this.levelScale = options.levelScale || {};
        
        this.ambientParticles = options.ambientParticles || false;
        this.particleDensity = options.particleDensity || 0.1;
        this.backgroundSpiral = options.backgroundSpiral || true;
        
        this.perspectiveDepth = options.perspectiveDepth || 1000;
        this.timeScale = options.timeScale || 1;
    }
    
    static defaultDark() {
        return new ManifoldSkin('dark', {
            levelColors: {
                0: HelixColor.fromRGB(255, 255, 255),
                1: HelixColor.fromRGB(100, 150, 255),
                2: HelixColor.fromRGB(150, 100, 255),
                3: HelixColor.fromRGB(200, 100, 200),
                4: HelixColor.fromRGB(255, 100, 150),
                5: HelixColor.fromRGB(255, 150, 100),
                6: HelixColor.fromRGB(255, 200, 100)
            },
            ambientParticles: true,
            backgroundSpiral: true
        });
    }
    
    static neonCyber() {
        return new ManifoldSkin('neon', {
            levelColors: {
                0: HelixColor.fromRGB(0, 0, 0),
                1: HelixColor.fromRGB(255, 0, 128),
                2: HelixColor.fromRGB(0, 255, 128),
                3: HelixColor.fromRGB(0, 128, 255),
                4: HelixColor.fromRGB(255, 128, 0),
                5: HelixColor.fromRGB(128, 0, 255),
                6: HelixColor.fromRGB(255, 255, 0)
            },
            levelGlow: { 0: 0, 1: 0.2, 2: 0.4, 3: 0.6, 4: 0.8, 5: 1.0, 6: 1.2 },
            ambientParticles: true,
            particleDensity: 0.3
        });
    }
    
    static cosmicDream() {
        return new ManifoldSkin('cosmic', {
            levelColors: {
                0: HelixColor.fromRGB(10, 5, 30),
                1: HelixColor.fromRGB(50, 20, 100),
                2: HelixColor.fromRGB(100, 50, 150),
                3: HelixColor.fromRGB(150, 100, 200),
                4: HelixColor.fromRGB(200, 150, 220),
                5: HelixColor.fromRGB(220, 200, 255),
                6: HelixColor.fromRGB(255, 255, 255)
            },
            ambientParticles: true,
            particleDensity: 0.5,
            backgroundSpiral: true
        });
    }
}


// =============================================================================
// HELIX PRESENTATION ENGINE
// =============================================================================

class HelixPresentation {
    constructor(canvas, options = {}) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
        
        this.skin = options.skin || ManifoldSkin.defaultDark();
        this.elements = new Map();
        this.swarms = [];
        this.transitions = [];
        this.ambientParticles = [];
        
        this.time = 0;
        this.timeScale = options.timeScale || 1;
        this.lastFrameTime = 0;
        
        this.isRunning = false;
        
        this._initAmbientParticles();
    }
    
    _initAmbientParticles() {
        if (!this.skin.ambientParticles) return;
        
        const count = Math.floor(this.width * this.height * this.skin.particleDensity / 10000);
        for (let i = 0; i < count; i++) {
            this.ambientParticles.push(new Particle({
                content: ['·', '•', '✦', '✧', '*'][Math.floor(Math.random() * 5)],
                x: Math.random() * this.width,
                y: Math.random() * this.height,
                z: Math.random() * 500 - 250,
                color: this.skin.levelColors[Math.floor(Math.random() * 7)],
                level: Math.floor(Math.random() * 3) + 4,
                scale: 0.3 + Math.random() * 0.7,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                drag: 0.001
            }));
        }
    }
    
    addElement(element) {
        this.elements.set(element.id, element);
        return element;
    }
    
    createText(id, content, level = 6) {
        const elem = new SubstrateElement({
            id, type: 'text', content, level
        });
        return this.addElement(elem);
    }
    
    addSwarm(swarm) {
        this.swarms.push(swarm);
        return swarm;
    }
    
    createTextSwarm(text, x, y, options = {}) {
        const swarm = ParticleSwarm.fromText(text, { x, y, ...options });
        return this.addSwarm(swarm);
    }
    
    transition(elementId, type, toLevel, duration = 1000) {
        const elem = this.elements.get(elementId);
        if (!elem) return null;
        
        const trans = new HelixTransition({
            type,
            fromLevel: elem.level,
            toLevel,
            duration,
            onUpdate: (progress, level) => {
                elem.invokeAt(Math.round(level));
                if (elem.particles) {
                    elem.particles.applyLevelTransition(trans.fromLevel, trans.toLevel, progress);
                }
            }
        });
        
        trans.start();
        this.transitions.push(trans);
        return trans;
    }
    
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this.lastFrameTime = performance.now();
        this._animate();
    }
    
    stop() {
        this.isRunning = false;
    }
    
    _animate() {
        if (!this.isRunning) return;
        
        const now = performance.now();
        const dt = (now - this.lastFrameTime) / 1000;
        this.lastFrameTime = now;
        this.time += dt * this.timeScale;
        
        this._update(dt);
        this._render();
        
        requestAnimationFrame(() => this._animate());
    }
    
    _update(dt) {
        // Update transitions
        for (let i = this.transitions.length - 1; i >= 0; i--) {
            this.transitions[i].update();
            if (this.transitions[i].isComplete) {
                this.transitions.splice(i, 1);
            }
        }
        
        // Update swarms
        for (const swarm of this.swarms) {
            swarm.update(dt);
        }
        
        // Update element particles
        for (const elem of this.elements.values()) {
            if (elem.particles) {
                elem.particles.update(dt);
            }
        }
        
        // Update ambient particles
        for (const p of this.ambientParticles) {
            p.update(dt);
            
            // Wrap around screen
            if (p.x < -50) p.x = this.width + 50;
            if (p.x > this.width + 50) p.x = -50;
            if (p.y < -50) p.y = this.height + 50;
            if (p.y > this.height + 50) p.y = -50;
        }
    }
    
    _render() {
        const ctx = this.ctx;
        
        // Clear with slight fade for trails
        ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
        ctx.fillRect(0, 0, this.width, this.height);
        
        // Render background spiral if enabled
        if (this.skin.backgroundSpiral) {
            this._renderBackgroundSpiral();
        }
        
        // Render ambient particles
        for (const p of this.ambientParticles) {
            p.render(ctx, this.width / 2, this.height / 2);
        }
        
        // Render swarms
        for (const swarm of this.swarms) {
            swarm.render(ctx, this.width / 2, this.height / 2);
        }
        
        // Render element particles
        for (const elem of this.elements.values()) {
            if (elem.isDecomposed && elem.particles) {
                elem.particles.render(ctx, this.width / 2, this.height / 2);
            }
        }
    }
    
    _renderBackgroundSpiral() {
        const ctx = this.ctx;
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        
        ctx.save();
        ctx.globalAlpha = 0.1;
        ctx.strokeStyle = this.skin.levelColors[4]?.toCSS() || '#4060ff';
        ctx.lineWidth = 1;
        
        ctx.beginPath();
        for (let t = 0; t < TAU * 5; t += 0.05) {
            const r = 50 + t * 20;
            const angle = t + this.time * 0.1;
            const x = centerX + r * Math.cos(angle);
            const y = centerY + r * Math.sin(angle);
            
            if (t === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();
        ctx.restore();
    }
    
    resize(width, height) {
        this.width = width;
        this.height = height;
        this.canvas.width = width;
        this.canvas.height = height;
    }
}


// =============================================================================
// CONVENIENCE FUNCTIONS
// =============================================================================

function createPresentation(canvas, skinName = 'dark') {
    const skins = {
        dark: ManifoldSkin.defaultDark,
        neon: ManifoldSkin.neonCyber,
        cosmic: ManifoldSkin.cosmicDream
    };
    return new HelixPresentation(canvas, {
        skin: skins[skinName]?.() || skins.dark()
    });
}

function textSwarm(text, x = 0, y = 0) {
    return ParticleSwarm.fromText(text, { x, y });
}

function helixColor(hue, saturation = 1, lightness = 0.5, level = 6) {
    return new HelixColor(hue * TAU, saturation, (lightness - 0.5) * 6, level);
}


// =============================================================================
// EXPORT FOR MODULES
// =============================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        PHI, TAU, FIBONACCI, VISUAL_LEVELS,
        HelixColor, Particle, ParticleSwarm,
        SubstrateElement, HelixTransition, ManifoldSkin, HelixPresentation,
        createPresentation, textSwarm, helixColor
    };
}

// Global export for browser
if (typeof window !== 'undefined') {
    window.HelixStyles = {
        PHI, TAU, FIBONACCI, VISUAL_LEVELS,
        HelixColor, Particle, ParticleSwarm,
        SubstrateElement, HelixTransition, ManifoldSkin, HelixPresentation,
        createPresentation, textSwarm, helixColor
    };
}

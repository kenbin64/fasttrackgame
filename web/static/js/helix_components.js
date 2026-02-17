/**
 * ButterflyFX HelixStyles - Canvas-Based UI Components
 * 
 * Copyright (c) 2024-2026 Kenneth Bingham
 * Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
 * 
 * Canvas-rendered form components using substrate presentation.
 * These are NOT DOM elements - they render directly to canvas with
 * particle effects, level transitions, and helix-based styling.
 */

(function() {
    'use strict';
    
    // Get HelixStyles reference
    const HS = window.HelixStyles || {};
    const PHI = HS.PHI || 1.618033988749895;
    const TAU = HS.TAU || Math.PI * 2;
    
    // =============================================================================
    // BASE COMPONENT CLASS
    // =============================================================================
    
    class HelixComponent {
        constructor(options = {}) {
            this.id = options.id || `hc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            this.x = options.x || 0;
            this.y = options.y || 0;
            this.width = options.width || 200;
            this.height = options.height || 40;
            this.level = options.level || 6;
            this.visible = options.visible !== false;
            this.enabled = options.enabled !== false;
            
            // Visual state
            this.opacity = 1;
            this.scale = 1;
            this.rotation = 0;
            this.glowIntensity = 0;
            
            // Interaction state
            this.isHovered = false;
            this.isFocused = false;
            this.isPressed = false;
            
            // Colors (using HelixColor if available)
            this.primaryColor = options.primaryColor || { h: 220, s: 70, l: 60 };
            this.secondaryColor = options.secondaryColor || { h: 280, s: 60, l: 50 };
            this.textColor = options.textColor || { h: 0, s: 0, l: 100 };
            this.backgroundColor = options.backgroundColor || { h: 230, s: 30, l: 15 };
            
            // Particles for effects
            this.particles = [];
            this.maxParticles = options.maxParticles || 20;
            
            // Callbacks
            this.onChange = options.onChange || null;
            this.onFocus = options.onFocus || null;
            this.onBlur = options.onBlur || null;
            
            // Animation
            this.animationTime = 0;
        }
        
        // Color helpers
        hsl(color, alpha = 1) {
            return `hsla(${color.h}, ${color.s}%, ${color.l}%, ${alpha})`;
        }
        
        adjustLightness(color, delta) {
            return { h: color.h, s: color.s, l: Math.max(0, Math.min(100, color.l + delta)) };
        }
        
        // Bounds checking
        containsPoint(px, py) {
            return px >= this.x && px <= this.x + this.width &&
                   py >= this.y && py <= this.y + this.height;
        }
        
        // Particle effects
        emitParticles(count, originX, originY) {
            for (let i = 0; i < count && this.particles.length < this.maxParticles; i++) {
                this.particles.push({
                    x: originX,
                    y: originY,
                    vx: (Math.random() - 0.5) * 4,
                    vy: (Math.random() - 0.5) * 4,
                    life: 1,
                    decay: 0.02 + Math.random() * 0.02,
                    size: 2 + Math.random() * 3,
                    color: this.primaryColor
                });
            }
        }
        
        updateParticles(dt) {
            for (let i = this.particles.length - 1; i >= 0; i--) {
                const p = this.particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.1; // gravity
                p.life -= p.decay;
                if (p.life <= 0) {
                    this.particles.splice(i, 1);
                }
            }
        }
        
        renderParticles(ctx) {
            for (const p of this.particles) {
                ctx.fillStyle = this.hsl(p.color, p.life * 0.8);
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size * p.life, 0, TAU);
                ctx.fill();
            }
        }
        
        // Level-based rendering helpers
        getLevelAlpha() {
            const alphas = [0, 0.1, 0.3, 0.6, 0.9, 1.0, 1.0];
            return alphas[Math.min(6, Math.max(0, this.level))];
        }
        
        getLevelBlur() {
            const blurs = [20, 15, 10, 5, 2, 0, 0];
            return blurs[Math.min(6, Math.max(0, this.level))];
        }
        
        // Override in subclasses
        update(dt) {
            this.animationTime += dt;
            this.updateParticles(dt);
            
            // Smooth glow transitions
            const targetGlow = this.isHovered ? 0.6 : (this.isFocused ? 0.4 : 0);
            this.glowIntensity += (targetGlow - this.glowIntensity) * 0.1;
        }
        
        render(ctx) {
            // Override in subclasses
        }
        
        // Event handlers (return true if handled)
        onMouseMove(x, y) {
            const wasHovered = this.isHovered;
            this.isHovered = this.containsPoint(x, y);
            if (this.isHovered && !wasHovered) {
                this.emitParticles(3, x, y);
            }
            return this.isHovered;
        }
        
        onMouseDown(x, y) {
            if (this.containsPoint(x, y) && this.enabled) {
                this.isPressed = true;
                this.emitParticles(5, x, y);
                return true;
            }
            return false;
        }
        
        onMouseUp(x, y) {
            this.isPressed = false;
            return this.containsPoint(x, y);
        }
        
        onClick(x, y) {
            return this.containsPoint(x, y) && this.enabled;
        }
        
        onKeyDown(key) {
            return false;
        }
        
        focus() {
            this.isFocused = true;
            if (this.onFocus) this.onFocus(this);
        }
        
        blur() {
            this.isFocused = false;
            if (this.onBlur) this.onBlur(this);
        }
    }
    
    // =============================================================================
    // HELIX BUTTON
    // =============================================================================
    
    class HelixButton extends HelixComponent {
        constructor(options = {}) {
            super(options);
            this.text = options.text || 'Button';
            this.fontSize = options.fontSize || 16;
            this.borderRadius = options.borderRadius || 8;
            this.onClick_ = options.onClick || null;
            
            // Button-specific animation
            this.pressScale = 1;
            this.ripples = [];
        }
        
        update(dt) {
            super.update(dt);
            
            // Press animation
            const targetScale = this.isPressed ? 0.95 : 1;
            this.pressScale += (targetScale - this.pressScale) * 0.2;
            
            // Update ripples
            for (let i = this.ripples.length - 1; i >= 0; i--) {
                const r = this.ripples[i];
                r.radius += r.speed;
                r.opacity -= 0.03;
                if (r.opacity <= 0) {
                    this.ripples.splice(i, 1);
                }
            }
        }
        
        render(ctx) {
            if (!this.visible) return;
            
            ctx.save();
            
            const centerX = this.x + this.width / 2;
            const centerY = this.y + this.height / 2;
            
            ctx.translate(centerX, centerY);
            ctx.scale(this.pressScale, this.pressScale);
            ctx.translate(-centerX, -centerY);
            
            // Background with glow
            if (this.glowIntensity > 0) {
                ctx.shadowBlur = 20 * this.glowIntensity;
                ctx.shadowColor = this.hsl(this.primaryColor, 0.6);
            }
            
            // Button background
            const bgColor = this.isHovered ? 
                this.adjustLightness(this.primaryColor, 10) : 
                this.primaryColor;
            
            ctx.fillStyle = this.hsl(bgColor, this.getLevelAlpha());
            this.roundRect(ctx, this.x, this.y, this.width, this.height, this.borderRadius);
            ctx.fill();
            
            // Border
            ctx.strokeStyle = this.hsl(this.adjustLightness(this.primaryColor, 20), 0.5);
            ctx.lineWidth = 1;
            ctx.stroke();
            
            // Ripple effects
            ctx.save();
            this.clipRoundRect(ctx, this.x, this.y, this.width, this.height, this.borderRadius);
            for (const r of this.ripples) {
                ctx.fillStyle = this.hsl(this.textColor, r.opacity * 0.3);
                ctx.beginPath();
                ctx.arc(r.x, r.y, r.radius, 0, TAU);
                ctx.fill();
            }
            ctx.restore();
            
            // Text
            ctx.shadowBlur = 0;
            ctx.fillStyle = this.hsl(this.textColor, this.getLevelAlpha());
            ctx.font = `${this.fontSize}px -apple-system, BlinkMacSystemFont, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(this.text, centerX, centerY);
            
            ctx.restore();
            
            // Render particles
            this.renderParticles(ctx);
        }
        
        roundRect(ctx, x, y, w, h, r) {
            ctx.beginPath();
            ctx.moveTo(x + r, y);
            ctx.lineTo(x + w - r, y);
            ctx.quadraticCurveTo(x + w, y, x + w, y + r);
            ctx.lineTo(x + w, y + h - r);
            ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
            ctx.lineTo(x + r, y + h);
            ctx.quadraticCurveTo(x, y + h, x, y + h - r);
            ctx.lineTo(x, y + r);
            ctx.quadraticCurveTo(x, y, x + r, y);
            ctx.closePath();
        }
        
        clipRoundRect(ctx, x, y, w, h, r) {
            this.roundRect(ctx, x, y, w, h, r);
            ctx.clip();
        }
        
        onClick(x, y) {
            if (super.onClick(x, y)) {
                // Add ripple
                this.ripples.push({
                    x: x,
                    y: y,
                    radius: 0,
                    speed: 5,
                    opacity: 1
                });
                
                this.emitParticles(10, x, y);
                
                if (this.onClick_) {
                    this.onClick_(this);
                }
                return true;
            }
            return false;
        }
    }
    
    // =============================================================================
    // HELIX TEXT FIELD
    // =============================================================================
    
    class HelixTextField extends HelixComponent {
        constructor(options = {}) {
            super(options);
            this.value = options.value || '';
            this.placeholder = options.placeholder || '';
            this.fontSize = options.fontSize || 16;
            this.borderRadius = options.borderRadius || 6;
            this.maxLength = options.maxLength || 1000;
            this.password = options.password || false;
            
            // Cursor
            this.cursorPosition = this.value.length;
            this.cursorBlink = 0;
            this.selectionStart = null;
            this.selectionEnd = null;
            
            // Scroll for long text
            this.scrollOffset = 0;
            this.padding = 12;
        }
        
        update(dt) {
            super.update(dt);
            this.cursorBlink += dt * 3;
        }
        
        render(ctx) {
            if (!this.visible) return;
            
            ctx.save();
            
            // Background
            const bgColor = this.isFocused ? 
                this.adjustLightness(this.backgroundColor, 5) : 
                this.backgroundColor;
            
            if (this.glowIntensity > 0 || this.isFocused) {
                ctx.shadowBlur = this.isFocused ? 15 : 10 * this.glowIntensity;
                ctx.shadowColor = this.hsl(this.primaryColor, 0.4);
            }
            
            ctx.fillStyle = this.hsl(bgColor, this.getLevelAlpha());
            this.roundRect(ctx, this.x, this.y, this.width, this.height, this.borderRadius);
            ctx.fill();
            
            // Border
            const borderColor = this.isFocused ? this.primaryColor : 
                this.adjustLightness(this.backgroundColor, 30);
            ctx.strokeStyle = this.hsl(borderColor, 0.8);
            ctx.lineWidth = this.isFocused ? 2 : 1;
            ctx.stroke();
            
            ctx.shadowBlur = 0;
            
            // Clip text area
            ctx.save();
            ctx.beginPath();
            ctx.rect(this.x + this.padding, this.y, this.width - this.padding * 2, this.height);
            ctx.clip();
            
            // Text or placeholder
            const displayValue = this.password ? '•'.repeat(this.value.length) : this.value;
            const hasValue = this.value.length > 0;
            
            ctx.font = `${this.fontSize}px -apple-system, BlinkMacSystemFont, monospace`;
            ctx.textBaseline = 'middle';
            
            const textY = this.y + this.height / 2;
            const textX = this.x + this.padding - this.scrollOffset;
            
            if (hasValue) {
                ctx.fillStyle = this.hsl(this.textColor, this.getLevelAlpha());
                ctx.fillText(displayValue, textX, textY);
            } else {
                ctx.fillStyle = this.hsl(this.adjustLightness(this.textColor, -50), 0.5);
                ctx.fillText(this.placeholder, textX, textY);
            }
            
            // Cursor
            if (this.isFocused && Math.sin(this.cursorBlink) > 0) {
                const textBeforeCursor = displayValue.substring(0, this.cursorPosition);
                const cursorX = textX + ctx.measureText(textBeforeCursor).width;
                
                ctx.fillStyle = this.hsl(this.primaryColor, 0.9);
                ctx.fillRect(cursorX, this.y + 8, 2, this.height - 16);
            }
            
            ctx.restore();
            ctx.restore();
            
            this.renderParticles(ctx);
        }
        
        roundRect(ctx, x, y, w, h, r) {
            ctx.beginPath();
            ctx.moveTo(x + r, y);
            ctx.lineTo(x + w - r, y);
            ctx.quadraticCurveTo(x + w, y, x + w, y + r);
            ctx.lineTo(x + w, y + h - r);
            ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
            ctx.lineTo(x + r, y + h);
            ctx.quadraticCurveTo(x, y + h, x, y + h - r);
            ctx.lineTo(x, y + r);
            ctx.quadraticCurveTo(x, y, x + r, y);
            ctx.closePath();
        }
        
        onClick(x, y) {
            if (super.onClick(x, y)) {
                this.focus();
                // Set cursor position based on click
                // (simplified - puts cursor at end)
                this.cursorPosition = this.value.length;
                return true;
            }
            return false;
        }
        
        onKeyDown(key, event) {
            if (!this.isFocused) return false;
            
            if (key === 'Backspace') {
                if (this.cursorPosition > 0) {
                    this.value = this.value.slice(0, this.cursorPosition - 1) + 
                                 this.value.slice(this.cursorPosition);
                    this.cursorPosition--;
                    this.emitParticles(2, this.x + this.width / 2, this.y + this.height / 2);
                    if (this.onChange) this.onChange(this.value, this);
                }
                return true;
            }
            
            if (key === 'Delete') {
                if (this.cursorPosition < this.value.length) {
                    this.value = this.value.slice(0, this.cursorPosition) + 
                                 this.value.slice(this.cursorPosition + 1);
                    if (this.onChange) this.onChange(this.value, this);
                }
                return true;
            }
            
            if (key === 'ArrowLeft') {
                this.cursorPosition = Math.max(0, this.cursorPosition - 1);
                return true;
            }
            
            if (key === 'ArrowRight') {
                this.cursorPosition = Math.min(this.value.length, this.cursorPosition + 1);
                return true;
            }
            
            if (key === 'Home') {
                this.cursorPosition = 0;
                return true;
            }
            
            if (key === 'End') {
                this.cursorPosition = this.value.length;
                return true;
            }
            
            // Regular character input
            if (key.length === 1 && this.value.length < this.maxLength) {
                this.value = this.value.slice(0, this.cursorPosition) + 
                             key + 
                             this.value.slice(this.cursorPosition);
                this.cursorPosition++;
                this.emitParticles(1, this.x + this.width / 2, this.y + this.height / 2);
                if (this.onChange) this.onChange(this.value, this);
                return true;
            }
            
            return false;
        }
    }
    
    // =============================================================================
    // HELIX SLIDER
    // =============================================================================
    
    class HelixSlider extends HelixComponent {
        constructor(options = {}) {
            super(options);
            this.height = options.height || 30;
            this.min = options.min || 0;
            this.max = options.max || 100;
            this.value = options.value || 50;
            this.step = options.step || 1;
            this.showValue = options.showValue !== false;
            
            this.thumbRadius = 10;
            this.trackHeight = 6;
            this.isDragging = false;
        }
        
        getNormalizedValue() {
            return (this.value - this.min) / (this.max - this.min);
        }
        
        getThumbX() {
            return this.x + this.thumbRadius + 
                   this.getNormalizedValue() * (this.width - this.thumbRadius * 2);
        }
        
        setValueFromX(x) {
            const trackStart = this.x + this.thumbRadius;
            const trackEnd = this.x + this.width - this.thumbRadius;
            const normalized = Math.max(0, Math.min(1, (x - trackStart) / (trackEnd - trackStart)));
            
            let newValue = this.min + normalized * (this.max - this.min);
            
            // Apply step
            newValue = Math.round(newValue / this.step) * this.step;
            newValue = Math.max(this.min, Math.min(this.max, newValue));
            
            if (newValue !== this.value) {
                this.value = newValue;
                this.emitParticles(2, this.getThumbX(), this.y + this.height / 2);
                if (this.onChange) this.onChange(this.value, this);
            }
        }
        
        update(dt) {
            super.update(dt);
        }
        
        render(ctx) {
            if (!this.visible) return;
            
            ctx.save();
            
            const centerY = this.y + this.height / 2;
            const thumbX = this.getThumbX();
            
            // Track background
            ctx.fillStyle = this.hsl(this.backgroundColor, 0.8);
            ctx.beginPath();
            ctx.roundRect(
                this.x + this.thumbRadius, 
                centerY - this.trackHeight / 2, 
                this.width - this.thumbRadius * 2, 
                this.trackHeight, 
                this.trackHeight / 2
            );
            ctx.fill();
            
            // Track filled portion
            ctx.fillStyle = this.hsl(this.primaryColor, this.getLevelAlpha());
            ctx.beginPath();
            ctx.roundRect(
                this.x + this.thumbRadius, 
                centerY - this.trackHeight / 2, 
                thumbX - this.x - this.thumbRadius, 
                this.trackHeight, 
                this.trackHeight / 2
            );
            ctx.fill();
            
            // Thumb glow
            if (this.isDragging || this.isHovered) {
                ctx.shadowBlur = 15;
                ctx.shadowColor = this.hsl(this.primaryColor, 0.6);
            }
            
            // Thumb
            ctx.fillStyle = this.hsl(
                this.isDragging ? this.adjustLightness(this.primaryColor, 15) : this.primaryColor
            );
            ctx.beginPath();
            ctx.arc(thumbX, centerY, this.thumbRadius, 0, TAU);
            ctx.fill();
            
            ctx.shadowBlur = 0;
            
            // Value display
            if (this.showValue) {
                ctx.fillStyle = this.hsl(this.textColor, 0.8);
                ctx.font = '12px -apple-system, BlinkMacSystemFont, sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';
                ctx.fillText(this.value.toFixed(this.step < 1 ? 1 : 0), thumbX, this.y - 2);
            }
            
            ctx.restore();
            
            this.renderParticles(ctx);
        }
        
        onMouseDown(x, y) {
            if (this.containsPoint(x, y) && this.enabled) {
                this.isDragging = true;
                this.setValueFromX(x);
                return true;
            }
            return false;
        }
        
        onMouseMove(x, y) {
            super.onMouseMove(x, y);
            if (this.isDragging) {
                this.setValueFromX(x);
            }
            return this.isHovered || this.isDragging;
        }
        
        onMouseUp(x, y) {
            this.isDragging = false;
            return super.onMouseUp(x, y);
        }
    }
    
    // =============================================================================
    // HELIX CHECKBOX / TOGGLE
    // =============================================================================
    
    class HelixToggle extends HelixComponent {
        constructor(options = {}) {
            super(options);
            this.width = options.width || 50;
            this.height = options.height || 26;
            this.checked = options.checked || false;
            this.label = options.label || '';
            
            this.togglePosition = this.checked ? 1 : 0;
        }
        
        update(dt) {
            super.update(dt);
            
            // Animate toggle position
            const target = this.checked ? 1 : 0;
            this.togglePosition += (target - this.togglePosition) * 0.15;
        }
        
        render(ctx) {
            if (!this.visible) return;
            
            ctx.save();
            
            const trackWidth = this.width;
            const trackHeight = this.height;
            const thumbSize = trackHeight - 4;
            
            // Track background
            const trackColor = this.checked ? 
                this.primaryColor : 
                this.adjustLightness(this.backgroundColor, 20);
            
            if (this.glowIntensity > 0) {
                ctx.shadowBlur = 10 * this.glowIntensity;
                ctx.shadowColor = this.hsl(this.primaryColor, 0.4);
            }
            
            ctx.fillStyle = this.hsl(trackColor, this.getLevelAlpha());
            ctx.beginPath();
            ctx.roundRect(this.x, this.y, trackWidth, trackHeight, trackHeight / 2);
            ctx.fill();
            
            ctx.shadowBlur = 0;
            
            // Thumb
            const thumbX = this.x + 2 + this.togglePosition * (trackWidth - thumbSize - 4);
            ctx.fillStyle = this.hsl(this.textColor, 1);
            ctx.beginPath();
            ctx.arc(thumbX + thumbSize / 2, this.y + trackHeight / 2, thumbSize / 2, 0, TAU);
            ctx.fill();
            
            // Label
            if (this.label) {
                ctx.fillStyle = this.hsl(this.textColor, this.getLevelAlpha());
                ctx.font = '14px -apple-system, BlinkMacSystemFont, sans-serif';
                ctx.textAlign = 'left';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.label, this.x + trackWidth + 10, this.y + trackHeight / 2);
            }
            
            ctx.restore();
            
            this.renderParticles(ctx);
        }
        
        onClick(x, y) {
            if (this.containsPoint(x, y) && this.enabled) {
                this.checked = !this.checked;
                this.emitParticles(8, this.x + this.width / 2, this.y + this.height / 2);
                if (this.onChange) this.onChange(this.checked, this);
                return true;
            }
            return false;
        }
    }
    
    // =============================================================================
    // HELIX PANEL (Container)
    // =============================================================================
    
    class HelixPanel extends HelixComponent {
        constructor(options = {}) {
            super(options);
            this.width = options.width || 300;
            this.height = options.height || 200;
            this.title = options.title || '';
            this.borderRadius = options.borderRadius || 12;
            this.children = [];
            this.padding = options.padding || 15;
            this.titleHeight = this.title ? 40 : 0;
        }
        
        addChild(component) {
            this.children.push(component);
            return component;
        }
        
        removeChild(component) {
            const idx = this.children.indexOf(component);
            if (idx >= 0) this.children.splice(idx, 1);
        }
        
        update(dt) {
            super.update(dt);
            for (const child of this.children) {
                child.update(dt);
            }
        }
        
        render(ctx) {
            if (!this.visible) return;
            
            ctx.save();
            
            // Panel background with glass effect
            ctx.fillStyle = this.hsl(this.backgroundColor, 0.85 * this.getLevelAlpha());
            
            if (this.glowIntensity > 0) {
                ctx.shadowBlur = 20 * this.glowIntensity;
                ctx.shadowColor = this.hsl(this.primaryColor, 0.3);
            }
            
            ctx.beginPath();
            ctx.roundRect(this.x, this.y, this.width, this.height, this.borderRadius);
            ctx.fill();
            
            // Border
            ctx.strokeStyle = this.hsl(this.adjustLightness(this.primaryColor, -20), 0.3);
            ctx.lineWidth = 1;
            ctx.stroke();
            
            ctx.shadowBlur = 0;
            
            // Title
            if (this.title) {
                // Title bar
                ctx.fillStyle = this.hsl(this.adjustLightness(this.backgroundColor, 5), 0.5);
                ctx.beginPath();
                ctx.roundRect(this.x, this.y, this.width, this.titleHeight, [this.borderRadius, this.borderRadius, 0, 0]);
                ctx.fill();
                
                // Title text
                ctx.fillStyle = this.hsl(this.textColor, this.getLevelAlpha());
                ctx.font = 'bold 14px -apple-system, BlinkMacSystemFont, sans-serif';
                ctx.textAlign = 'left';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.title, this.x + this.padding, this.y + this.titleHeight / 2);
                
                // Separator line
                ctx.strokeStyle = this.hsl(this.primaryColor, 0.2);
                ctx.beginPath();
                ctx.moveTo(this.x, this.y + this.titleHeight);
                ctx.lineTo(this.x + this.width, this.y + this.titleHeight);
                ctx.stroke();
            }
            
            ctx.restore();
            
            // Render children
            for (const child of this.children) {
                child.render(ctx);
            }
            
            this.renderParticles(ctx);
        }
        
        onMouseMove(x, y) {
            super.onMouseMove(x, y);
            for (const child of this.children) {
                child.onMouseMove(x, y);
            }
            return this.isHovered;
        }
        
        onMouseDown(x, y) {
            for (const child of this.children) {
                if (child.onMouseDown(x, y)) return true;
            }
            return super.onMouseDown(x, y);
        }
        
        onMouseUp(x, y) {
            for (const child of this.children) {
                child.onMouseUp(x, y);
            }
            return super.onMouseUp(x, y);
        }
        
        onClick(x, y) {
            // Blur all children first
            for (const child of this.children) {
                if (child.isFocused && !child.containsPoint(x, y)) {
                    child.blur();
                }
            }
            
            // Then click the one at point
            for (const child of this.children) {
                if (child.onClick(x, y)) return true;
            }
            return super.onClick(x, y);
        }
        
        onKeyDown(key, event) {
            for (const child of this.children) {
                if (child.isFocused && child.onKeyDown(key, event)) return true;
            }
            return false;
        }
    }
    
    // =============================================================================
    // HELIX FORM (Manager)
    // =============================================================================
    
    class HelixForm {
        constructor(canvas, options = {}) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.components = [];
            this.focusedComponent = null;
            
            this.backgroundColor = options.backgroundColor || { h: 230, s: 20, l: 8 };
            this.isRunning = false;
            this.lastTime = 0;
            
            this._bindEvents();
        }
        
        _bindEvents() {
            this.canvas.addEventListener('mousemove', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                for (const c of this.components) {
                    c.onMouseMove(x, y);
                }
            });
            
            this.canvas.addEventListener('mousedown', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                for (const c of this.components) {
                    c.onMouseDown(x, y);
                }
            });
            
            this.canvas.addEventListener('mouseup', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                for (const c of this.components) {
                    c.onMouseUp(x, y);
                }
            });
            
            this.canvas.addEventListener('click', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                // Blur currently focused
                if (this.focusedComponent) {
                    this.focusedComponent.blur();
                    this.focusedComponent = null;
                }
                
                for (const c of this.components) {
                    if (c.onClick(x, y)) {
                        if (c.isFocused) {
                            this.focusedComponent = c;
                        }
                        break;
                    }
                }
            });
            
            document.addEventListener('keydown', (e) => {
                if (this.focusedComponent) {
                    if (this.focusedComponent.onKeyDown(e.key, e)) {
                        e.preventDefault();
                    }
                }
                
                // Also pass to panels
                for (const c of this.components) {
                    if (c instanceof HelixPanel) {
                        if (c.onKeyDown(e.key, e)) {
                            e.preventDefault();
                        }
                    }
                }
            });
        }
        
        add(component) {
            this.components.push(component);
            return component;
        }
        
        remove(component) {
            const idx = this.components.indexOf(component);
            if (idx >= 0) this.components.splice(idx, 1);
        }
        
        getValues() {
            const values = {};
            const collectValues = (components) => {
                for (const c of components) {
                    if (c.id) {
                        if ('value' in c) values[c.id] = c.value;
                        else if ('checked' in c) values[c.id] = c.checked;
                    }
                    if (c.children) collectValues(c.children);
                }
            };
            collectValues(this.components);
            return values;
        }
        
        setValues(values) {
            const applyValues = (components) => {
                for (const c of components) {
                    if (c.id && values.hasOwnProperty(c.id)) {
                        if ('value' in c) c.value = values[c.id];
                        else if ('checked' in c) c.checked = values[c.id];
                    }
                    if (c.children) applyValues(c.children);
                }
            };
            applyValues(this.components);
        }
        
        start() {
            if (this.isRunning) return;
            this.isRunning = true;
            this.lastTime = performance.now();
            this._animate();
        }
        
        stop() {
            this.isRunning = false;
        }
        
        _animate() {
            if (!this.isRunning) return;
            
            const now = performance.now();
            const dt = (now - this.lastTime) / 1000;
            this.lastTime = now;
            
            this._update(dt);
            this._render();
            
            requestAnimationFrame(() => this._animate());
        }
        
        _update(dt) {
            for (const c of this.components) {
                c.update(dt);
            }
        }
        
        _render() {
            const ctx = this.ctx;
            
            // Clear with background
            ctx.fillStyle = `hsl(${this.backgroundColor.h}, ${this.backgroundColor.s}%, ${this.backgroundColor.l}%)`;
            ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            // Render components (back to front)
            for (const c of this.components) {
                c.render(ctx);
            }
        }
    }
    
    // =============================================================================
    // HELIX LABEL (Display text)
    // =============================================================================
    
    class HelixLabel extends HelixComponent {
        constructor(options = {}) {
            super(options);
            this.text = options.text || '';
            this.fontSize = options.fontSize || 16;
            this.fontWeight = options.fontWeight || 'normal';
            this.textAlign = options.textAlign || 'left';
        }
        
        render(ctx) {
            if (!this.visible) return;
            
            ctx.save();
            ctx.fillStyle = this.hsl(this.textColor, this.getLevelAlpha());
            ctx.font = `${this.fontWeight} ${this.fontSize}px -apple-system, BlinkMacSystemFont, sans-serif`;
            ctx.textAlign = this.textAlign;
            ctx.textBaseline = 'top';
            ctx.fillText(this.text, this.x, this.y);
            ctx.restore();
        }
    }
    
    // =============================================================================
    // HELIX OUTPUT (Display dynamic values)
    // =============================================================================
    
    class HelixOutput extends HelixComponent {
        constructor(options = {}) {
            super(options);
            this.value = options.value || '';
            this.fontSize = options.fontSize || 14;
            this.borderRadius = options.borderRadius || 6;
            this.prefix = options.prefix || '';
            this.suffix = options.suffix || '';
        }
        
        render(ctx) {
            if (!this.visible) return;
            
            ctx.save();
            
            // Background
            ctx.fillStyle = this.hsl(this.adjustLightness(this.backgroundColor, 5), 0.6 * this.getLevelAlpha());
            ctx.beginPath();
            ctx.roundRect(this.x, this.y, this.width, this.height, this.borderRadius);
            ctx.fill();
            
            // Border
            ctx.strokeStyle = this.hsl(this.primaryColor, 0.3);
            ctx.lineWidth = 1;
            ctx.stroke();
            
            // Value
            const displayText = `${this.prefix}${this.value}${this.suffix}`;
            ctx.fillStyle = this.hsl(this.primaryColor, this.getLevelAlpha());
            ctx.font = `${this.fontSize}px -apple-system, BlinkMacSystemFont, monospace`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(displayText, this.x + this.width / 2, this.y + this.height / 2);
            
            ctx.restore();
        }
    }
    
    // =============================================================================
    // EXPORTS
    // =============================================================================
    
    const HelixComponents = {
        HelixComponent,
        HelixButton,
        HelixTextField,
        HelixSlider,
        HelixToggle,
        HelixPanel,
        HelixForm,
        HelixLabel,
        HelixOutput
    };
    
    // Module export
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = HelixComponents;
    }
    
    // Browser export
    if (typeof window !== 'undefined') {
        window.HelixComponents = HelixComponents;
    }
    
})();

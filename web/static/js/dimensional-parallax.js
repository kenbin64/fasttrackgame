/**
 * Dimensional Parallax & 3D Effects Engine
 * 
 * Creates holodeck-style depth and immersion with:
 * - 7-layer parallax based on Genesis model
 * - 3D card tilt effects (mouse/gyroscope)
 * - Device-adaptive behaviors
 * - Fibonacci-timed animations
 * 
 * @version 2.0.0
 * @author ButterflyFX
 */

(function() {
    'use strict';

    // Constants
    const PHI = 1.618033988749895;
    const FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377];
    
    // Depth multipliers for 7 layers (Genesis model)
    const DEPTH_LAYERS = {
        spark: 0.1,
        mirror: 0.2, 
        relation: 0.35,
        form: 0.5,
        life: 0.7,
        mind: 0.85,
        completion: 1.0
    };

    // Device detection
    const Device = {
        isMobile: /iPhone|iPad|iPod|Android/i.test(navigator.userAgent),
        isTablet: /iPad|Android/i.test(navigator.userAgent) && window.innerWidth >= 768,
        hasTouch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
        hasGyroscope: 'DeviceOrientationEvent' in window,
        prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        
        get type() {
            if (this.isMobile && !this.isTablet) return 'mobile';
            if (this.isTablet) return 'tablet';
            return 'desktop';
        },
        
        get canHover() {
            return window.matchMedia('(hover: hover)').matches;
        }
    };

    /**
     * Dimensional Parallax Controller
     */
    class DimensionalParallax {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' 
                ? document.querySelector(container) 
                : container;
            
            if (!this.container) {
                console.warn('DimensionalParallax: Container not found');
                return;
            }

            this.options = {
                intensity: options.intensity || 1,
                smooth: options.smooth !== false,
                gyroscope: options.gyroscope !== false && Device.hasGyroscope,
                mouse: options.mouse !== false && Device.canHover,
                scroll: options.scroll !== false,
                layers: options.layers || null,
                ...options
            };

            this.state = {
                scrollY: 0,
                mouseX: 0,
                mouseY: 0,
                gyroX: 0,
                gyroY: 0,
                rafId: null
            };

            this.layers = [];
            this.init();
        }

        init() {
            // Find all parallax layers
            this.layers = Array.from(
                this.container.querySelectorAll('[data-parallax-depth], [data-depth]')
            ).map(el => ({
                element: el,
                depth: parseFloat(el.dataset.parallaxDepth || el.dataset.depth) || 0.5,
                offsetX: 0,
                offsetY: 0,
                scale: 1
            }));

            if (this.layers.length === 0) {
                console.warn('DimensionalParallax: No layers found');
                return;
            }

            this.bindEvents();
            this.animate();
        }

        bindEvents() {
            // Scroll parallax
            if (this.options.scroll) {
                window.addEventListener('scroll', () => {
                    this.state.scrollY = window.pageYOffset;
                }, { passive: true });
            }

            // Mouse parallax (desktop)
            if (this.options.mouse && Device.canHover) {
                this.container.addEventListener('mousemove', (e) => {
                    const rect = this.container.getBoundingClientRect();
                    this.state.mouseX = (e.clientX - rect.left - rect.width / 2) / rect.width;
                    this.state.mouseY = (e.clientY - rect.top - rect.height / 2) / rect.height;
                }, { passive: true });

                this.container.addEventListener('mouseleave', () => {
                    this.state.mouseX = 0;
                    this.state.mouseY = 0;
                });
            }

            // Gyroscope parallax (mobile)
            if (this.options.gyroscope && Device.hasGyroscope && Device.isMobile) {
                this.requestGyroscopePermission();
            }

            // Resize handler
            window.addEventListener('resize', this.handleResize.bind(this), { passive: true });
        }

        async requestGyroscopePermission() {
            if (typeof DeviceOrientationEvent.requestPermission === 'function') {
                try {
                    const permission = await DeviceOrientationEvent.requestPermission();
                    if (permission === 'granted') {
                        this.enableGyroscope();
                    }
                } catch (e) {
                    console.log('Gyroscope permission denied');
                }
            } else {
                this.enableGyroscope();
            }
        }

        enableGyroscope() {
            window.addEventListener('deviceorientation', (e) => {
                if (e.gamma !== null && e.beta !== null) {
                    // Normalize to -1 to 1 range
                    this.state.gyroX = Math.max(-1, Math.min(1, e.gamma / 45));
                    this.state.gyroY = Math.max(-1, Math.min(1, (e.beta - 45) / 45));
                }
            }, { passive: true });
        }

        handleResize() {
            // Recalculate dimensions if needed
        }

        animate() {
            if (Device.prefersReducedMotion) return;

            const update = () => {
                this.layers.forEach(layer => {
                    let x = 0, y = 0, scale = 1;
                    const depth = layer.depth * this.options.intensity;

                    // Scroll effect
                    if (this.options.scroll) {
                        const rect = layer.element.getBoundingClientRect();
                        const inView = rect.top < window.innerHeight && rect.bottom > 0;
                        if (inView) {
                            y += this.state.scrollY * depth * 0.3;
                        }
                    }

                    // Mouse/touch effect
                    if (this.options.mouse && Device.canHover) {
                        x += this.state.mouseX * depth * 50;
                        y += this.state.mouseY * depth * 50;
                    }

                    // Gyroscope effect
                    if (this.options.gyroscope && Device.isMobile) {
                        x += this.state.gyroX * depth * 30;
                        y += this.state.gyroY * depth * 30;
                    }

                    // Smooth interpolation
                    if (this.options.smooth) {
                        layer.offsetX += (x - layer.offsetX) * 0.1;
                        layer.offsetY += (y - layer.offsetY) * 0.1;
                    } else {
                        layer.offsetX = x;
                        layer.offsetY = y;
                    }

                    // Apply transform
                    layer.element.style.transform = `translate3d(${layer.offsetX}px, ${layer.offsetY}px, 0)`;
                });

                this.state.rafId = requestAnimationFrame(update);
            };

            this.state.rafId = requestAnimationFrame(update);
        }

        destroy() {
            if (this.state.rafId) {
                cancelAnimationFrame(this.state.rafId);
            }
        }
    }

    /**
     * 3D Holodeck Card Effect
     */
    class HolodeckCard {
        constructor(element, options = {}) {
            this.element = typeof element === 'string' 
                ? document.querySelector(element) 
                : element;

            if (!this.element) return;

            this.options = {
                maxTilt: options.maxTilt || 15,
                perspective: options.perspective || 1000,
                scale: options.scale || 1.05,
                speed: options.speed || 400,
                glare: options.glare !== false,
                gyroscope: options.gyroscope !== false && Device.isMobile,
                ...options
            };

            this.state = {
                tiltX: 0,
                tiltY: 0,
                rafId: null
            };

            this.init();
        }

        init() {
            this.element.style.transformStyle = 'preserve-3d';
            this.element.style.willChange = 'transform';

            if (this.options.glare) {
                this.createGlare();
            }

            this.bindEvents();
        }

        createGlare() {
            this.glareElement = document.createElement('div');
            this.glareElement.className = 'holodeck-glare';
            this.glareElement.style.cssText = `
                position: absolute;
                inset: 0;
                pointer-events: none;
                border-radius: inherit;
                background: linear-gradient(
                    135deg,
                    rgba(255, 255, 255, 0.25) 0%,
                    rgba(255, 255, 255, 0) 60%
                );
                opacity: 0;
                transition: opacity ${this.options.speed}ms;
            `;
            this.element.style.position = 'relative';
            this.element.appendChild(this.glareElement);
        }

        bindEvents() {
            if (Device.canHover) {
                this.element.addEventListener('mouseenter', this.onEnter.bind(this));
                this.element.addEventListener('mousemove', this.onMove.bind(this));
                this.element.addEventListener('mouseleave', this.onLeave.bind(this));
            }

            if (this.options.gyroscope && Device.isMobile) {
                this.element.addEventListener('touchstart', this.onTouchStart.bind(this));
                this.element.addEventListener('touchend', this.onTouchEnd.bind(this));
            }
        }

        onEnter() {
            this.element.style.transition = `transform ${this.options.speed}ms`;
            if (this.glareElement) {
                this.glareElement.style.opacity = '1';
            }
        }

        onMove(e) {
            const rect = this.element.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const tiltX = ((y - centerY) / centerY) * this.options.maxTilt;
            const tiltY = ((centerX - x) / centerX) * this.options.maxTilt;

            this.applyTransform(tiltX, tiltY);

            // Update glare position
            if (this.glareElement) {
                const glareX = (x / rect.width) * 100;
                const glareY = (y / rect.height) * 100;
                this.glareElement.style.background = `
                    radial-gradient(
                        circle at ${glareX}% ${glareY}%,
                        rgba(255, 255, 255, 0.3) 0%,
                        rgba(255, 255, 255, 0) 60%
                    )
                `;
            }
        }

        onLeave() {
            this.element.style.transition = `transform ${this.options.speed}ms`;
            this.applyTransform(0, 0, false);
            if (this.glareElement) {
                this.glareElement.style.opacity = '0';
            }
        }

        onTouchStart() {
            // Enable gyroscope tilt on touch
            if (Device.hasGyroscope) {
                this.gyroHandler = (e) => {
                    const tiltX = (e.beta - 45) / 3; // Normalize beta
                    const tiltY = e.gamma / 3; // Normalize gamma
                    this.applyTransform(
                        Math.max(-this.options.maxTilt, Math.min(this.options.maxTilt, tiltX)),
                        Math.max(-this.options.maxTilt, Math.min(this.options.maxTilt, tiltY))
                    );
                };
                window.addEventListener('deviceorientation', this.gyroHandler);
            }
        }

        onTouchEnd() {
            if (this.gyroHandler) {
                window.removeEventListener('deviceorientation', this.gyroHandler);
                this.applyTransform(0, 0);
            }
        }

        applyTransform(tiltX, tiltY, scale = true) {
            const transform = `
                perspective(${this.options.perspective}px)
                rotateX(${tiltX}deg)
                rotateY(${tiltY}deg)
                ${scale ? `scale(${this.options.scale})` : 'scale(1)'}
            `;
            this.element.style.transform = transform;
            
            // Update CSS custom properties for other elements to use
            this.element.style.setProperty('--tilt-x', `${tiltX}deg`);
            this.element.style.setProperty('--tilt-y', `${tiltY}deg`);
        }
    }

    /**
     * Starfield Background
     */
    class StarfieldBackground {
        constructor(canvas, options = {}) {
            this.canvas = typeof canvas === 'string' 
                ? document.querySelector(canvas) 
                : canvas;

            if (!this.canvas) return;

            this.ctx = this.canvas.getContext('2d');
            this.options = {
                starCount: options.starCount || 200,
                speed: options.speed || 0.5,
                depth: options.depth || 3,
                colors: options.colors || ['#ffffff', '#8855ff', '#40ffff', '#ff55aa'],
                ...options
            };

            this.stars = [];
            this.init();
        }

        init() {
            this.resize();
            this.createStars();
            this.animate();

            window.addEventListener('resize', () => this.resize());
        }

        resize() {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }

        createStars() {
            this.stars = [];
            for (let i = 0; i < this.options.starCount; i++) {
                this.stars.push({
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height,
                    z: Math.random() * this.options.depth,
                    radius: Math.random() * 2,
                    color: this.options.colors[Math.floor(Math.random() * this.options.colors.length)],
                    opacity: Math.random() * 0.5 + 0.5,
                    twinkleSpeed: Math.random() * 0.02 + 0.01
                });
            }
        }

        animate() {
            if (Device.prefersReducedMotion) {
                this.drawStatic();
                return;
            }

            const draw = () => {
                this.ctx.fillStyle = 'rgba(5, 5, 8, 0.2)';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

                this.stars.forEach(star => {
                    // Move star based on depth (parallax)
                    star.y += this.options.speed * (1 + star.z / this.options.depth);
                    
                    // Reset if off screen
                    if (star.y > this.canvas.height) {
                        star.y = 0;
                        star.x = Math.random() * this.canvas.width;
                    }

                    // Twinkle
                    star.opacity += star.twinkleSpeed;
                    if (star.opacity > 1 || star.opacity < 0.3) {
                        star.twinkleSpeed *= -1;
                    }

                    // Draw star
                    const size = star.radius * (1 + star.z / this.options.depth);
                    this.ctx.beginPath();
                    this.ctx.arc(star.x, star.y, size, 0, Math.PI * 2);
                    this.ctx.fillStyle = star.color;
                    this.ctx.globalAlpha = star.opacity;
                    this.ctx.fill();
                    
                    // Glow effect
                    if (size > 1) {
                        this.ctx.beginPath();
                        this.ctx.arc(star.x, star.y, size * 2, 0, Math.PI * 2);
                        this.ctx.fillStyle = star.color;
                        this.ctx.globalAlpha = star.opacity * 0.2;
                        this.ctx.fill();
                    }
                });

                this.ctx.globalAlpha = 1;
                requestAnimationFrame(draw);
            };

            draw();
        }

        drawStatic() {
            this.ctx.fillStyle = '#050508';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            this.stars.forEach(star => {
                this.ctx.beginPath();
                this.ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
                this.ctx.fillStyle = star.color;
                this.ctx.globalAlpha = 0.7;
                this.ctx.fill();
            });
            this.ctx.globalAlpha = 1;
        }
    }

    /**
     * Responsive Navigation
     */
    class ResponsiveNav {
        constructor(options = {}) {
            this.options = {
                toggleSelector: '.nav-mobile-toggle',
                drawerSelector: '.nav-drawer',
                backdropSelector: '.nav-drawer-backdrop',
                ...options
            };

            this.isOpen = false;
            this.init();
        }

        init() {
            this.toggle = document.querySelector(this.options.toggleSelector);
            this.drawer = document.querySelector(this.options.drawerSelector);
            this.backdrop = document.querySelector(this.options.backdropSelector);

            if (!this.toggle) return;

            // Create backdrop if not exists
            if (!this.backdrop) {
                this.backdrop = document.createElement('div');
                this.backdrop.className = 'nav-drawer-backdrop';
                document.body.appendChild(this.backdrop);
            }

            // Create drawer if not exists
            if (!this.drawer) {
                this.createDrawer();
            }

            this.bindEvents();
        }

        createDrawer() {
            this.drawer = document.createElement('nav');
            this.drawer.className = 'nav-drawer';
            
            // Clone nav links from desktop nav
            const desktopNav = document.querySelector('.nav-desktop, nav');
            if (desktopNav) {
                const links = desktopNav.querySelectorAll('a');
                links.forEach(link => {
                    const clone = link.cloneNode(true);
                    this.drawer.appendChild(clone);
                });
            }
            
            document.body.appendChild(this.drawer);
        }

        bindEvents() {
            this.toggle.addEventListener('click', () => this.toggleNav());
            this.backdrop.addEventListener('click', () => this.closeNav());
            
            // Close on escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.closeNav();
                }
            });

            // Close on link click
            this.drawer.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => this.closeNav());
            });
        }

        toggleNav() {
            this.isOpen ? this.closeNav() : this.openNav();
        }

        openNav() {
            this.isOpen = true;
            this.toggle.classList.add('active');
            this.drawer.classList.add('open');
            this.backdrop.classList.add('visible');
            document.body.style.overflow = 'hidden';
        }

        closeNav() {
            this.isOpen = false;
            this.toggle.classList.remove('active');
            this.drawer.classList.remove('open');
            this.backdrop.classList.remove('visible');
            document.body.style.overflow = '';
        }
    }

    /**
     * Initialize device classes
     */
    function initDeviceClasses() {
        document.documentElement.classList.add(`device-${Device.type}`);
        
        if (Device.hasTouch) {
            document.documentElement.classList.add('touch-device');
        } else {
            document.documentElement.classList.add('hover-device');
        }

        if (Device.prefersReducedMotion) {
            document.documentElement.classList.add('reduced-motion');
        }
    }

    /**
     * Auto-initialize holodeck cards
     */
    function initHolodeckCards() {
        document.querySelectorAll('.holodeck-card, [data-holodeck]').forEach(el => {
            new HolodeckCard(el);
        });
    }

    /**
     * Auto-initialize parallax containers
     */
    function initParallax() {
        document.querySelectorAll('[data-parallax], .parallax-container').forEach(el => {
            new DimensionalParallax(el);
        });
    }

    // Export to global
    window.Dimensional = {
        PHI,
        FIBONACCI,
        DEPTH_LAYERS,
        Device,
        Parallax: DimensionalParallax,
        HolodeckCard,
        Starfield: StarfieldBackground,
        ResponsiveNav,
        
        init() {
            initDeviceClasses();
            initHolodeckCards();
            initParallax();
            new ResponsiveNav();
        }
    };

    // Auto-init on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => window.Dimensional.init());
    } else {
        window.Dimensional.init();
    }
})();

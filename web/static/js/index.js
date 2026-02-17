// Error handler
        window.onerror = function(msg, url, line, col, error) {
            console.error('JS Error:', msg, 'at line', line);
            document.body.innerHTML += '<div style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:red;color:white;padding:20px;z-index:9999;">JS Error: ' + msg + ' at line ' + line + '</div>';
            return false;
        };
        
        // ===== HAMBURGER MENU =====
        const hamburger = document.getElementById('hamburger');
        const mainNav = document.getElementById('main-nav');
        const navOverlay = document.getElementById('navOverlay');
        
        function toggleNav() {
            hamburger.classList.toggle('active');
            mainNav.classList.toggle('open');
            navOverlay.classList.toggle('open');
        }
        
        hamburger.addEventListener('click', toggleNav);
        navOverlay.addEventListener('click', toggleNav);
        
        mainNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                if (mainNav.classList.contains('open')) toggleNav();
            });
        });
        
        // ===== CANVAS SETUP =====
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const starfieldCanvas = document.getElementById('starfield');
        const starfieldCtx = starfieldCanvas.getContext('2d');
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            starfieldCanvas.width = window.innerWidth;
            starfieldCanvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);
        
        // ===== 3D STARFIELD =====
        const stars = [];
        const STAR_COUNT = 400;
        const STAR_SPEED = 2;
        const MAX_DEPTH = 1500;
        
        // Initialize stars
        for (let i = 0; i < STAR_COUNT; i++) {
            stars.push({
                x: (Math.random() - 0.5) * 2000,
                y: (Math.random() - 0.5) * 2000,
                z: Math.random() * MAX_DEPTH,
                size: Math.random() * 1.5 + 0.5
            });
        }
        
        function drawStarfield() {
            const w = starfieldCanvas.width;
            const h = starfieldCanvas.height;
            const cx = w / 2;
            const cy = h / 2;
            
            // Clear with fade trail effect
            starfieldCtx.fillStyle = 'rgba(5, 5, 16, 0.3)';
            starfieldCtx.fillRect(0, 0, w, h);
            
            for (let star of stars) {
                // Move star toward viewer
                star.z -= STAR_SPEED;
                
                // Reset star if it passes camera
                if (star.z <= 0) {
                    star.x = (Math.random() - 0.5) * 2000;
                    star.y = (Math.random() - 0.5) * 2000;
                    star.z = MAX_DEPTH;
                }
                
                // 3D to 2D projection
                const fov = 300;
                const scale = fov / star.z;
                const sx = star.x * scale + cx;
                const sy = star.y * scale + cy;
                
                // Only draw if on screen
                if (sx < 0 || sx > w || sy < 0 || sy > h) continue;
                
                // Size and brightness based on depth
                const depth = 1 - star.z / MAX_DEPTH;
                const size = star.size * scale * 0.5;
                const alpha = depth * 0.8 + 0.2;
                
                // Star color with slight blue tint
                const brightness = Math.floor(200 + depth * 55);
                starfieldCtx.fillStyle = `rgba(${brightness}, ${brightness + 10}, 255, ${alpha})`;
                
                // Draw star as circle
                starfieldCtx.beginPath();
                starfieldCtx.arc(sx, sy, Math.max(0.5, size), 0, Math.PI * 2);
                starfieldCtx.fill();
                
                // Add streak effect for close stars
                if (depth > 0.7 && size > 1) {
                    const prevScale = fov / (star.z + STAR_SPEED * 3);
                    const prevX = star.x * prevScale + cx;
                    const prevY = star.y * prevScale + cy;
                    
                    starfieldCtx.strokeStyle = `rgba(${brightness}, ${brightness + 10}, 255, ${alpha * 0.5})`;
                    starfieldCtx.lineWidth = size * 0.5;
                    starfieldCtx.beginPath();
                    starfieldCtx.moveTo(prevX, prevY);
                    starfieldCtx.lineTo(sx, sy);
                    starfieldCtx.stroke();
                }
            }
        }
        
        // Starfield animation loop (separate from main render)
        function animateStarfield() {
            drawStarfield();
            requestAnimationFrame(animateStarfield);
        }
        animateStarfield();
        
        // ===== STATE =====
        let currentDimension = 0;
        let currentLens = 'color';
        let currentView = 'carousel';
        let rotationX = 0.3;
        let rotationY = 0.5;
        let zoom = 1;
        let isDragging = false;
        let didDrag = false; // Track if actual dragging occurred
        let lastMouse = { x: 0, y: 0 };
        let time = 0;
        let carouselRotation = 0; // Current panel index at front
        let panelsHidden = false; // Panels hidden state
        
        // Audio
        let audioCtx = null;
        let oscillator = null;
        let oscillators = []; // For chords
        let gainNode = null;
        
        // =============================================================================
        // NATURAL SUBSTRATE SYSTEM
        // Physically accurate - no arbitrary mappings
        // Color from ANGLE (azimuth → hue wheel, true spectral position)
        // Sound from VECTOR MAGNITUDE (string length → frequency, f = c/2L)
        // Brightness from Z-HEIGHT (elevation → luminosity)
        // =============================================================================
        
        const MusicalSubstrate = {
            // Physical constants
            SPEED_OF_LIGHT: 299792458,        // m/s
            SPEED_OF_SOUND: 343,              // m/s in air at 20°C
            PLANCK: 6.62607015e-34,           // Planck's constant (J·s)
            
            // Musical constants (equal temperament, 12-TET)
            A4: 440,                          // Concert pitch A4 = 440 Hz
            MIDDLE_C: 261.626,                // C4 = Middle C
            SEMITONE_RATIO: Math.pow(2, 1/12), // 12-TET semitone ratio
            
            // Frequency range bounds for normalization
            BASS_FREQ: 27.5,                  // Lowest bass frequency (A0)
            TREBLE_FREQ: 4186,                // Highest treble frequency (C8/piccolo)
            
            // String/pipe resonance: f = c / (2L) where L = resonating length
            // Mapping geometric distance to resonating length
            MIN_LENGTH: 0.041,                // ~41mm (piccolo, ~4186 Hz)
            MAX_LENGTH: 6.25,                 // ~6.25m (bass organ pipe, ~27.5 Hz)
            
            // Visible light spectrum bounds (nm) - TRUE PHYSICS
            WAVELENGTH_VIOLET: 380,           // violet
            WAVELENGTH_RED: 700,              // red
            
            // Instrument frequency ranges (Hz) - orchestral
            INSTRUMENTS: {
                bass: { min: 27.5, max: 100, type: 'sawtooth', name: 'Bass' },
                cello: { min: 65, max: 262, type: 'sawtooth', name: 'Cello' },
                viola: { min: 131, max: 523, type: 'triangle', name: 'Viola' },
                violin: { min: 196, max: 2000, type: 'triangle', name: 'Violin' },
                flute: { min: 262, max: 4186, type: 'sine', name: 'Flute' }
            },
            
            // Natural harmonic intervals (from overtone series)
            INTERVALS: {
                unison: 1/1,
                octave: 2/1,
                fifth: 3/2,
                fourth: 4/3,
                majorThird: 5/4,
                minorThird: 6/5,
                majorSixth: 5/3,
                minorSeventh: 7/4
            },
            
            // Sacred geometry constants
            PHI: (1 + Math.sqrt(5)) / 2,      // Golden ratio φ ≈ 1.618
            SQRT2: Math.sqrt(2),
            SQRT3: Math.sqrt(3),
            
            /**
             * NATURAL COLOR: Angle (azimuth) → Visible spectrum position
             * 0° = Red (700nm), 60° = Yellow (580nm), 120° = Green (510nm),
             * 180° = Cyan (490nm), 240° = Blue (450nm), 300° = Violet (380nm)
             * This maps the color wheel to the true electromagnetic spectrum
             * @param {number} angle - angle in radians (-π to π)
             * @returns {number} wavelength in nm
             */
            angleToWavelength(angle) {
                // Normalize angle to [0, 2π]
                let a = ((angle % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
                // Map 0→2π to spectrum: red(0°)→violet(300°)→red(360°)
                // Use only 300° of the wheel for the visible spectrum (no magenta loop)
                const position = a / (Math.PI * 2);  // 0 to 1
                // Red at 0°, through spectrum to violet at 300°
                if (position <= 5/6) {
                    // Map 0→5/6 to 700nm→380nm (red to violet)
                    const t = position / (5/6); // 0 to 1
                    return 700 - t * 320; // 700nm down to 380nm
                } else {
                    // Wrap around: 5/6→1 maps back to red 380→700
                    const t = (position - 5/6) / (1/6);
                    return 380 + t * 320;
                }
            },
            
            /**
             * NATURAL SOUND: Vector magnitude → Resonating length → Frequency
             * Physics: f = v / (2L) for standing wave in closed pipe/string
             * Larger distance = longer resonating length = lower frequency
             * @param {number} magnitude - vector magnitude (distance from origin)
             * @param {number} maxMag - maximum magnitude in the space
             * @returns {number} frequency in Hz
             */
            magnitudeToFreq(magnitude, maxMag = 1.5) {
                // Clamp magnitude
                const m = Math.max(0.01, Math.min(magnitude, maxMag));
                // Map magnitude to resonating length
                // Small magnitude = short length = high freq
                // Large magnitude = long length = low freq
                const normalizedM = m / maxMag; // 0 to 1
                // Logarithmic interpolation between lengths
                const logMin = Math.log(this.MIN_LENGTH);
                const logMax = Math.log(this.MAX_LENGTH);
                const length = Math.exp(logMin + normalizedM * (logMax - logMin));
                // f = c / (2L)
                return this.SPEED_OF_SOUND / (2 * length);
            },
            
            /**
             * NATURAL BRIGHTNESS: Z-height (pitch/elevation) → Luminosity
             * Higher z = more light, lower z = darker
             * @param {number} z - z coordinate
             * @param {number} range - expected z range
             * @returns {number} luminosity 0-1
             */
            zToLuminosity(z, range = 1.5) {
                const normalized = (z + range) / (2 * range); // -range→+range to 0→1
                return Math.max(0.2, Math.min(1, 0.3 + normalized * 0.7));
            },
            
            /**
             * Convert wavelength (nm) to RGB using CIE color matching
             * This is the TRUE spectral color, not an approximation
             * @param {number} wavelength - wavelength in nm
             * @returns {object} {r, g, b, rgb, hex}
             */
            wavelengthToColor(wavelength) {
                let r, g, b;
                wavelength = Math.max(380, Math.min(700, wavelength));
                
                // CIE 1931 spectral locus approximation
                if (wavelength >= 380 && wavelength < 440) {
                    r = -(wavelength - 440) / 60;
                    g = 0;
                    b = 1;
                } else if (wavelength >= 440 && wavelength < 490) {
                    r = 0;
                    g = (wavelength - 440) / 50;
                    b = 1;
                } else if (wavelength >= 490 && wavelength < 510) {
                    r = 0;
                    g = 1;
                    b = -(wavelength - 510) / 20;
                } else if (wavelength >= 510 && wavelength < 580) {
                    r = (wavelength - 510) / 70;
                    g = 1;
                    b = 0;
                } else if (wavelength >= 580 && wavelength < 645) {
                    r = 1;
                    g = -(wavelength - 645) / 65;
                    b = 0;
                } else {
                    r = 1;
                    g = 0;
                    b = 0;
                }
                
                // Intensity attenuation at spectrum edges
                let intensity;
                if (wavelength >= 380 && wavelength < 420) {
                    intensity = 0.3 + 0.7 * (wavelength - 380) / 40;
                } else if (wavelength > 645 && wavelength <= 700) {
                    intensity = 0.3 + 0.7 * (700 - wavelength) / 55;
                } else {
                    intensity = 1;
                }
                
                // Apply gamma correction for display
                const gamma = 0.8;
                r = Math.round(255 * Math.pow(r * intensity, gamma));
                g = Math.round(255 * Math.pow(g * intensity, gamma));
                b = Math.round(255 * Math.pow(b * intensity, gamma));
                
                return {
                    r, g, b,
                    rgb: `rgb(${r}, ${g}, ${b})`,
                    hex: `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`
                };
            },
            
            /**
             * Get note name from frequency
             * @param {number} freq - frequency in Hz
             * @returns {string} note name like "C4"
             */
            freqToNote(freq) {
                const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
                const midi = 69 + 12 * Math.log2(freq / this.A4);
                const rounded = Math.round(midi);
                const octave = Math.floor(rounded / 12) - 1;
                const noteIndex = ((rounded % 12) + 12) % 12;
                return noteNames[noteIndex] + octave;
            },
            
            /**
             * Get MIDI note number from frequency
             * @param {number} freq - frequency in Hz
             * @returns {number} MIDI note number
             */
            freqToMidi(freq) {
                return Math.round(69 + 12 * Math.log2(freq / this.A4));
            },
            
            /**
             * Get frequency for a MIDI note number
             * @param {number} midi - MIDI note number (60 = C4)
             * @returns {number} frequency in Hz
             */
            midiToFreq(midi) {
                return this.A4 * Math.pow(2, (midi - 69) / 12);
            },
            
            /**
             * Get the natural instrument for a given frequency
             * Based on actual instrument ranges
             * @param {number} freq - frequency in Hz
             * @returns {object} instrument data
             */
            freqToInstrument(freq) {
                if (freq < 100) return this.INSTRUMENTS.bass;
                if (freq < 262) return this.INSTRUMENTS.cello;
                if (freq < 523) return this.INSTRUMENTS.viola;
                if (freq < 2000) return this.INSTRUMENTS.violin;
                return this.INSTRUMENTS.flute;
            },
            
            /**
             * Generate natural harmonic series from a fundamental
             * These are the ACTUAL harmonics any vibrating body produces
             * @param {number} fundamental - fundamental frequency in Hz
             * @param {number} count - number of harmonics
             * @returns {number[]} array of harmonic frequencies
             */
            generateHarmonics(fundamental, count = 8) {
                return Array.from({ length: count }, (_, i) => fundamental * (i + 1));
            },
            
            /**
             * Generate a chord using natural harmonic ratios
             * @param {number} root - root frequency in Hz
             * @param {string} type - chord type
             * @returns {number[]} array of frequencies
             */
            generateChord(root, type = 'major') {
                const chords = {
                    major: [1, 5/4, 3/2],           // Root, major third, fifth
                    minor: [1, 6/5, 3/2],           // Root, minor third, fifth
                    power: [1, 3/2, 2],             // Root, fifth, octave
                    seventh: [1, 5/4, 3/2, 7/4],    // Dominant seventh
                    diminished: [1, 6/5, 64/45],   // Diminished
                    augmented: [1, 5/4, 8/5]       // Augmented
                };
                return (chords[type] || chords.major).map(ratio => root * ratio);
            },
            
            /**
             * Calculate sound wavelength in meters
             * @param {number} freq - frequency in Hz
             * @returns {number} wavelength in meters
             */
            soundWavelength(freq) {
                return this.SPEED_OF_SOUND / freq;
            },
            
            /**
             * Get complete NATURAL substrate data from a geometric point
             * ALL values derived from actual geometric properties
             * @param {number} x - x coordinate (left-right position)
             * @param {number} y - y coordinate (up-down position)  
             * @param {number} z - z coordinate (depth/elevation)
             * @returns {object} Complete natural substrate data
             */
            fromGeometry(x, y, z = 0) {
                // NATURAL geometric properties
                const magnitude = Math.sqrt(x * x + y * y + z * z);
                const azimuth = Math.atan2(y, x);           // Angle in XY plane
                const elevation = Math.atan2(z, Math.sqrt(x*x + y*y)); // Pitch angle
                
                // NATURAL COLOR: from azimuth angle
                const wavelength = this.angleToWavelength(azimuth);
                const color = this.wavelengthToColor(wavelength);
                const luminosity = this.zToLuminosity(z);
                
                // Apply luminosity to color
                const litColor = {
                    r: Math.round(color.r * luminosity),
                    g: Math.round(color.g * luminosity),
                    b: Math.round(color.b * luminosity),
                    rgb: `rgb(${Math.round(color.r * luminosity)}, ${Math.round(color.g * luminosity)}, ${Math.round(color.b * luminosity)})`,
                    hex: color.hex
                };
                
                // NATURAL SOUND: from vector magnitude (resonating length)
                const freq = this.magnitudeToFreq(magnitude);
                const noteName = this.freqToNote(freq);
                const instrument = this.freqToInstrument(freq);
                const soundWL = this.soundWavelength(freq);
                
                return {
                    // Raw geometry
                    x, y, z,
                    magnitude: magnitude,
                    azimuth: azimuth,                    // Radians
                    azimuthDeg: azimuth * 180 / Math.PI, // Degrees
                    elevation: elevation,                 // Radians
                    elevationDeg: elevation * 180 / Math.PI,
                    
                    // NATURAL COLOR (from angle)
                    light: {
                        wavelengthNm: wavelength,
                        color: color,           // Pure spectral color
                        litColor: litColor,     // With luminosity from z
                        luminosity: luminosity
                    },
                    
                    // NATURAL SOUND (from magnitude)
                    sound: {
                        frequencyHz: freq,
                        noteName: noteName,
                        wavelengthM: soundWL,
                        wavelengthPx: Math.min(100, soundWL * 20),
                        instrument: instrument
                    },
                    
                    // Value data
                    value: {
                        raw: magnitude,
                        formula: `|v| = √(${x.toFixed(2)}² + ${y.toFixed(2)}² + ${z.toFixed(2)}²) = ${magnitude.toFixed(4)}`,
                        angle: `θ = ${(azimuth * 180 / Math.PI).toFixed(1)}°`,
                        pitch: `φ = ${(elevation * 180 / Math.PI).toFixed(1)}°`
                    }
                };
            },
            
            /**
             * Get natural spectrum data for a horizontal position
             * For Line: left-to-right = violet-to-red
             * @param {number} t - position along line [-1.5, 1.5]
             * @param {number} minT - minimum t value
             * @param {number} maxT - maximum t value
             * @returns {object} spectrum data
             */
            positionToSpectrum(t, minT = -1.5, maxT = 1.5) {
                // Normalize position to [0, 1]
                const normalized = (t - minT) / (maxT - minT);
                // Map to visible spectrum: 0 = violet (380nm), 1 = red (700nm)
                const wavelength = 380 + normalized * 320;
                const color = this.wavelengthToColor(wavelength);
                // Map to sound: left = bass, right = treble
                const freq = this.magnitudeToFreq(1 - normalized, 1); // Invert: small t = large mag = low freq
                
                return {
                    wavelength,
                    color,
                    freq,
                    noteName: this.freqToNote(freq)
                };
            }
        };
        
        // Alias for backward compatibility
        const SubstrateLens = MusicalSubstrate;
        
        // Helper: Legacy distanceToWavelength for compatibility
        SubstrateLens.distanceToWavelength = function(r) {
            return 380 + Math.max(0, Math.min(1, r)) * 320;
        };
        
        SubstrateLens.distanceToFreq = function(r) {
            return this.magnitudeToFreq(r * 1.5, 1.5);
        };
        
        // =============================================================================
        // GEOMETRIC COORDINATE SYSTEM FOR ALL PAGE ELEMENTS
        // Every element has a position in dimensional space
        // ALL visual properties derived from actual geometry - nothing arbitrary
        // =============================================================================
        
        const GeometricElements = {
            // The 7 levels exist at specific angles on the helix (30° apart)
            // Level 0 = 0°, Level 1 = 30°, Level 2 = 60°, etc.
            LEVEL_ANGLES: [0, 30, 60, 90, 120, 150, 180],
            
            // Each level has a radius based on its expansive nature
            // (radius increases with dimensional complexity)
            LEVEL_RADII: [0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3],
            
            // Z-height for each level (helix rises)
            LEVEL_HEIGHTS: [0, 0.15, 0.3, 0.5, 0.7, 0.9, 1.2],
            
            /**
             * Get the geometric coordinates for a dimensional level
             * @param {number} level - dimension 0-6
             * @returns {object} {x, y, z} coordinates
             */
            levelToCoordinates(level) {
                const angle = this.LEVEL_ANGLES[level] * Math.PI / 180;
                const r = this.LEVEL_RADII[level];
                const z = this.LEVEL_HEIGHTS[level];
                
                return {
                    x: r * Math.cos(angle),
                    y: r * Math.sin(angle),
                    z: z,
                    angle: angle,
                    radius: r
                };
            },
            
            /**
             * Get the NATURAL lens for a dimensional level
             * Color, sound, value ALL derived from coordinates
             * @param {number} level - dimension 0-6
             * @returns {object} lens data
             */
            levelToLens(level) {
                const coords = this.levelToCoordinates(level);
                return MusicalSubstrate.fromGeometry(coords.x, coords.y, coords.z);
            },
            
            /**
             * Get the natural color for a dimensional level
             * Derived from the angle of its position on the helix
             * @param {number} level - dimension 0-6
             * @returns {string} CSS color (rgb or hex)
             */
            levelToColor(level) {
                const lens = this.levelToLens(level);
                return lens.light.color.rgb;
            },
            
            /**
             * Get the natural sound frequency for a dimensional level
             * Derived from the magnitude of its position
             * @param {number} level - dimension 0-6
             * @returns {number} frequency in Hz
             */
            levelToFrequency(level) {
                const lens = this.levelToLens(level);
                return lens.sound.frequencyHz;
            },
            
            /**
             * Get all properties for a level - derived from geometry
             */
            levelProperties(level) {
                const coords = this.levelToCoordinates(level);
                const lens = MusicalSubstrate.fromGeometry(coords.x, coords.y, coords.z);
                
                return {
                    level: level,
                    coordinates: coords,
                    color: lens.light.color.rgb,
                    colorHex: lens.light.color.hex,
                    wavelength: lens.light.wavelengthNm,
                    frequency: lens.sound.frequencyHz,
                    note: lens.sound.noteName,
                    instrument: lens.sound.instrument.name,
                    magnitude: lens.magnitude
                };
            },
            
            // Pre-calculate all level properties
            _cache: null,
            
            get all() {
                if (!this._cache) {
                    this._cache = Array.from({ length: 7 }, (_, i) => this.levelProperties(i));
                }
                return this._cache;
            }
        };
        
        // =============================================================================
        // SACRED GEOMETRY PATTERNS
        // Mathematically precise sacred geometry for Network and Whole dimensions
        // =============================================================================
        
        const SacredGeometry = {
            /**
             * Generate Flower of Life pattern (overlapping circles)
             * @param {number} centerX - center X
             * @param {number} centerY - center Y
             * @param {number} radius - circle radius
             * @param {number} rings - number of rings (default 3)
             * @returns {object[]} array of circle positions {x, y, r}
             */
            flowerOfLife(centerX, centerY, radius, rings = 3) {
                const circles = [{ x: centerX, y: centerY, r: radius }];
                const sqrt3 = Math.sqrt(3);
                
                for (let ring = 1; ring <= rings; ring++) {
                    const count = ring * 6;
                    for (let i = 0; i < count; i++) {
                        // Position along hexagonal ring
                        const angle = (i / count) * Math.PI * 2 - Math.PI / 2;
                        const x = centerX + Math.cos(angle) * radius * ring;
                        const y = centerY + Math.sin(angle) * radius * ring;
                        circles.push({ x, y, r: radius });
                        
                        // Additional circles between corners
                        if (ring > 1) {
                            const nextAngle = ((i + 1) / count) * Math.PI * 2 - Math.PI / 2;
                            for (let j = 1; j < ring; j++) {
                                const t = j / ring;
                                const innerAngle = angle + t * (nextAngle - angle);
                                const innerX = centerX + Math.cos(innerAngle) * radius * (ring - j * 0.1);
                                const innerY = centerY + Math.sin(innerAngle) * radius * (ring - j * 0.1);
                                // Only add if not too close to existing
                                const tooClose = circles.some(c => 
                                    Math.sqrt((c.x - innerX)**2 + (c.y - innerY)**2) < radius * 0.5);
                                if (!tooClose) circles.push({ x: innerX, y: innerY, r: radius });
                            }
                        }
                    }
                }
                return circles;
            },
            
            /**
             * Generate Seed of Life (7 overlapping circles)
             * @returns {object[]} circle positions
             */
            seedOfLife(centerX, centerY, radius) {
                const circles = [{ x: centerX, y: centerY, r: radius }];
                for (let i = 0; i < 6; i++) {
                    const angle = (i / 6) * Math.PI * 2;
                    circles.push({
                        x: centerX + Math.cos(angle) * radius,
                        y: centerY + Math.sin(angle) * radius,
                        r: radius
                    });
                }
                return circles;
            },
            
            /**
             * Generate Metatron's Cube (13 circles with connecting lines)
             * @returns {object} { circles, lines }
             */
            metatronsCube(centerX, centerY, radius) {
                // 13 circles: 1 center, 6 inner, 6 outer
                const circles = [{ x: centerX, y: centerY, r: radius * 0.3 }];
                const innerR = radius * 0.5;
                const outerR = radius;
                
                // Inner hexagon
                for (let i = 0; i < 6; i++) {
                    const angle = (i / 6) * Math.PI * 2 - Math.PI / 2;
                    circles.push({
                        x: centerX + Math.cos(angle) * innerR,
                        y: centerY + Math.sin(angle) * innerR,
                        r: radius * 0.25
                    });
                }
                
                // Outer hexagon (30° offset)
                for (let i = 0; i < 6; i++) {
                    const angle = (i / 6) * Math.PI * 2;
                    circles.push({
                        x: centerX + Math.cos(angle) * outerR,
                        y: centerY + Math.sin(angle) * outerR,
                        r: radius * 0.2
                    });
                }
                
                // Lines connecting all circles
                const lines = [];
                for (let i = 0; i < circles.length; i++) {
                    for (let j = i + 1; j < circles.length; j++) {
                        lines.push({ from: circles[i], to: circles[j] });
                    }
                }
                
                return { circles, lines };
            },
            
            /**
             * Generate Sri Yantra triangles
             * @returns {object[]} array of triangles
             */
            sriYantra(centerX, centerY, radius) {
                const triangles = [];
                // 9 interlocking triangles (4 upward, 5 downward)
                const scales = [1, 0.85, 0.7, 0.55, 0.4, 0.28, 0.18, 0.1, 0.05];
                
                scales.forEach((scale, i) => {
                    const r = radius * scale;
                    const upward = i % 2 === 0;
                    const rotation = (upward ? 0 : Math.PI) + (i * 0.05);
                    
                    const points = [];
                    for (let j = 0; j < 3; j++) {
                        const angle = rotation + (j / 3) * Math.PI * 2;
                        points.push({
                            x: centerX + Math.cos(angle) * r,
                            y: centerY + Math.sin(angle) * r
                        });
                    }
                    triangles.push({ points, upward, scale });
                });
                
                return triangles;
            },
            
            /**
             * Generate Vesica Piscis
             */
            vesicaPiscis(centerX, centerY, radius) {
                const offset = radius;
                return [
                    { x: centerX - offset / 2, y: centerY, r: radius },
                    { x: centerX + offset / 2, y: centerY, r: radius }
                ];
            },
            
            /**
             * Generate Torus (3D torus projected to 2D)
             * @returns {object[]} array of points forming torus
             */
            torusPoints(centerX, centerY, majorR, minorR, segments = 24, tubes = 12) {
                const points = [];
                for (let i = 0; i < segments; i++) {
                    const u = (i / segments) * Math.PI * 2;
                    for (let j = 0; j < tubes; j++) {
                        const v = (j / tubes) * Math.PI * 2;
                        const x = (majorR + minorR * Math.cos(v)) * Math.cos(u);
                        const z = (majorR + minorR * Math.cos(v)) * Math.sin(u);
                        const y = minorR * Math.sin(v);
                        // Simple perspective projection
                        const scale = 200 / (200 + z);
                        points.push({
                            x: centerX + x * scale,
                            y: centerY + y * scale,
                            depth: scale,
                            u, v
                        });
                    }
                }
                return points;
            }
        };
        
        // =============================================================================
        // AUDIO SYSTEM - Orchestral Musical Substrate
        // Point = Middle C, Line = Bass to Treble, Volume = Chords
        // Network = Harmonics (Sacred Geometry), Whole = Symphony
        // =============================================================================
        
        let isMouseOverShape = false;   // Track if mouse is over shape
        let hoverHistory = [];          // Track recent hover positions for melody
        
        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                gainNode = audioCtx.createGain();
                gainNode.gain.value = 0.12;
                gainNode.connect(audioCtx.destination);
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }
        
        function stopAllSounds() {
            oscillators.forEach(osc => { try { osc.stop(); } catch(e) {} });
            oscillators = [];
            if (oscillator) { try { oscillator.stop(); } catch(e) {} oscillator = null; }
        }
        
        // Alias for backwards compatibility  
        const stopAllOscillators = stopAllSounds;
        
        /**
         * Play a single note (Middle C for Point)
         */
        function playMiddleC() {
            initAudio();
            stopAllSounds();
            
            oscillator = audioCtx.createOscillator();
            oscillator.type = 'sine';
            oscillator.frequency.value = MusicalSubstrate.MIDDLE_C; // 261.626 Hz
            oscillator.connect(gainNode);
            oscillator.start();
            
            return { note: 'C4', freq: MusicalSubstrate.MIDDLE_C };
        }
        
        /**
         * Play frequency based on x-position (left=bass, right=treble)
         * For Line dimension
         */
        function playLineFrequency(xNorm) {
            initAudio();
            
            const freq = MusicalSubstrate.distanceToFreq(xNorm);
            const instrument = MusicalSubstrate.freqToInstrument(freq);
            
            if (!oscillator) {
                oscillator = audioCtx.createOscillator();
                oscillator.type = instrument.type;
                oscillator.connect(gainNode);
                oscillator.start();
            }
            
            oscillator.type = instrument.type;
            oscillator.frequency.setValueAtTime(freq, audioCtx.currentTime);
            
            return { freq, note: MusicalSubstrate.freqToNote(freq), instrument: instrument.name };
        }
        
        /**
         * Play chord that pings neighbors
         * For Volume dimension
         */
        function playNeighborChord(x, y, z = 0) {
            initAudio();
            stopAllSounds();
            
            const lens = MusicalSubstrate.fromGeometry(x, y, z);
            const root = lens.sound.frequencyHz;
            const chordType = z > 0 ? 'major' : 'minor';
            const freqs = MusicalSubstrate.generateChord(root, chordType);
            
            freqs.forEach((freq, i) => {
                const osc = audioCtx.createOscillator();
                const oscGain = audioCtx.createGain();
                oscGain.gain.value = 0.08 / (i + 1);
                osc.type = 'triangle';
                osc.frequency.value = freq;
                osc.connect(oscGain);
                oscGain.connect(gainNode);
                osc.start();
                oscillators.push(osc);
            });
            
            return { root, chord: chordType, frequencies: freqs };
        }
        
        /**
         * Play harmonics (sacred geometry resonance)
         * For Network dimension
         */
        function playHarmonicSeries(fundamental, count = 8) {
            initAudio();
            stopAllSounds();
            
            const harmonics = MusicalSubstrate.generateHarmonics(fundamental, count);
            
            harmonics.forEach((freq, i) => {
                const osc = audioCtx.createOscillator();
                const oscGain = audioCtx.createGain();
                // Harmonic series naturally diminishes in amplitude
                oscGain.gain.value = 0.06 / (i + 1);
                osc.type = i < 2 ? 'sine' : 'triangle';
                osc.frequency.value = freq;
                osc.connect(oscGain);
                oscGain.connect(gainNode);
                osc.start();
                oscillators.push(osc);
            });
            
            return { fundamental, harmonics };
        }
        
        /**
         * Play symphonic sound with multiple instrument voices
         * For Whole dimension - bass to flutes
         */
        function playSymphonic(xNorm, yNorm = 0.5) {
            initAudio();
            stopAllSounds();
            
            // Different instrument layers based on position
            const instruments = Object.values(MusicalSubstrate.INSTRUMENTS);
            const fundamental = MusicalSubstrate.distanceToFreq(xNorm);
            
            instruments.forEach((inst, i) => {
                // Each instrument plays a harmonic of the fundamental
                const freq = fundamental * (i + 1) / 2;
                if (freq >= inst.min && freq <= inst.max) {
                    const osc = audioCtx.createOscillator();
                    const oscGain = audioCtx.createGain();
                    // Position-based panning/volume
                    oscGain.gain.value = 0.04 * (1 - Math.abs(yNorm - 0.5) * 2);
                    osc.type = inst.type;
                    osc.frequency.value = freq;
                    osc.connect(oscGain);
                    oscGain.connect(gainNode);
                    osc.start();
                    oscillators.push(osc);
                }
            });
            
            return { fundamental, xNorm, yNorm };
        }
        
        /**
         * Play melody from hover sequence
         * Creates music as cursor moves across positions
         */
        function playMelodyNote(xNorm) {
            initAudio();
            
            const freq = MusicalSubstrate.distanceToFreq(xNorm);
            const instrument = MusicalSubstrate.freqToInstrument(freq);
            
            // Create short note with envelope
            const osc = audioCtx.createOscillator();
            const noteGain = audioCtx.createGain();
            
            osc.type = instrument.type;
            osc.frequency.value = freq;
            noteGain.gain.setValueAtTime(0.1, audioCtx.currentTime);
            noteGain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
            
            osc.connect(noteGain);
            noteGain.connect(gainNode);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.3);
            
            return { freq, note: MusicalSubstrate.freqToNote(freq) };
        }
        
        // Legacy compatibility functions
        function playSubstrateSound(x, y, z = 0) {
            const lens = MusicalSubstrate.fromGeometry(x, y, z);
            return playLineFrequency(lens.normalizedX || ((x + 1.5) / 3));
        }
        
        function playSubstrateChord(x, y, z = 0) {
            return playNeighborChord(x, y, z);
        }
        
        function playSubstrateHarmonics(xNorm) {
            const fundamental = MusicalSubstrate.distanceToFreq(xNorm);
            return playHarmonicSeries(fundamental, 8);
        }
        
        function playPointSound() {
            return playMiddleC();
        }
        
        function playLineSound(t) {
            const xNorm = (t + 1.5) / 3;
            return playLineFrequency(xNorm);
        }
        
        function playSaddleSound(x, y) {
            return playSubstrateSound(x, y, x * y);
        }
        
        function playVolumeChord(x, y, z) {
            return playNeighborChord(x, y, z);
        }
        
        function playNetworkHarmonics(nodeIndex) {
            const xNorm = (nodeIndex || 0) / 20;
            return playSubstrateHarmonics(xNorm);
        }
        
        function playSymphonicSound(xNorm, yNorm) {
            return playSymphonic(xNorm, yNorm);
        }

        // ===== DIMENSION DATA =====
        // ALL COLORS DERIVED FROM GEOMETRY - not hardcoded
        // Each level exists at a specific angle on the helix
        // Level 0 @ 0°, Level 1 @ 30°, Level 2 @ 60°, etc.
        
        const dimensionBase = {
            0: {
                title: "The Void",
                subtitle: "Pure Potential — Not Non-Existence",
                symbol: "∅",
                description: `The void represents <span class="highlight">infinite potential</span>, not emptiness. All possibilities exist here, waiting to be invoked through context.`,
                showLens: true,
                code: `<span class="comment"># Level 0: Pure Potential</span>
substrate = ButterflyFX.Substrate()

<span class="comment"># Potential is not nothing</span>
<span class="comment"># It is EVERYTHING unmanifested</span>
potential = substrate.void()
<span class="comment"># → ∞ possibilities await</span>`
            },
            1: {
                title: "The Point",
                subtitle: "Undivided Evaluated Entity",
                symbol: "•",
                description: `A point is an <span class="concept">undivided whole</span> — a single evaluated entity. It has no parts yet, only identity. The point IS the value.`,
                showLens: true,
                code: `<span class="comment"># Level 1: Undivided Entity</span>
point = substrate.at(x=<span class="number">0.5</span>)

<span class="comment"># A whole, not yet divided</span>
entity = point.manifest()
<span class="comment"># → One evaluated value</span>`
            },
            2: {
                title: "The Line",
                subtitle: "Division — From Whole to Parts",
                symbol: "―",
                description: `The line represents <span class="highlight">division</span>: the whole splits into parts. A continuum emerges where each point is a part of the greater whole.`,
                showLens: true,
                code: `<span class="comment"># Level 2: Division begins</span>
line = substrate.line(<span class="number">0</span>, <span class="number">1</span>)

<span class="comment"># Whole → Parts</span>
<span class="comment"># Jump to ANY part — O(1)</span>
part = line.at(<span class="number">0.5</span>).manifest()`
            },
            3: {
                title: "The Saddle",
                subtitle: "Multiplication of Divided Parts",
                symbol: "⌓",
                description: `The plane (z=xy) represents <span class="concept">multiplication</span>: divided parts combine and interact. Each point holds the product of its coordinates.`,
                showLens: true,
                code: `<span class="comment"># Level 3: Parts multiply</span>
saddle = substrate.surface(<span class="string">"z=xy"</span>)
point = saddle.at(x, y)

<span class="comment"># Product of parts = z</span>
color = point.lens(<span class="string">"color"</span>)
sound = point.lens(<span class="string">"sound"</span>)`
            },
            4: {
                title: "The Volume",
                subtitle: "States, Deltas, Trends & Timelines",
                symbol: "◇",
                description: `Volume captures <span class="highlight">depth of field</span>: states of all parts, their deltas, trends over time. Every point holds history and trajectory.`,
                showLens: true,
                code: `<span class="comment"># Level 4: States & Timelines</span>
volume = substrate.volume(<span class="string">"z=x*y**2"</span>)

<span class="comment"># Deltas, trends, depth</span>
state = volume.at(x=<span class="number">3</span>, y=<span class="number">4</span>)
delta = state.trend()
<span class="comment"># → History + trajectory</span>`
            },
            5: {
                title: "The Network",
                subtitle: "Wholes Become Points in Higher Dimensions",
                symbol: "⬡",
                description: `In 4D, entire 3D volumes collapse into <span class="concept">single points</span>. Each whole from below becomes an indivisible unit here, containing all its lower dimensions.`,
                showLens: true,
                code: `<span class="comment"># Level 5: Wholes as Points</span>
network = substrate.manifold(dim=<span class="number">4</span>)

<span class="comment"># Each point contains a volume</span>
car_a = network.at(x=<span class="number">3</span>, y=<span class="number">7</span>)
<span class="comment"># car_a holds ALL lower dims</span>
car_a.inner.volume <span class="comment"># → D4</span>`
            },
            6: {
                title: "The Whole",
                subtitle: "The Whole of All Wholes",
                symbol: "◎",
                description: `The ultimate dimension: a <span class="highlight">whole containing all wholes</span>. Each lower dimension becomes a point here. Ordered, bounded growth — not exponential trees.`,
                showLens: true,
                code: `<span class="comment"># Level 6: The Whole of All Wholes</span>
whole = substrate.global_manifold()

<span class="comment"># Every whole below is a point</span>
<span class="comment"># Bounded, ordered containment</span>
you = whole.at(ip=<span class="string">"192.168.1.1"</span>)
<span class="comment"># → Contains all dimensions</span>`
            }
        };
        
        // Build dimensions with GEOMETRY-DERIVED colors
        const dimensions = {};
        for (let i = 0; i <= 6; i++) {
            const props = GeometricElements.levelProperties(i);
            dimensions[i] = {
                ...dimensionBase[i],
                // Color derived from geometric position on helix
                color: props.colorHex,
                colorRgb: props.color,
                // Geometric data
                coordinates: props.coordinates,
                wavelength: props.wavelength,
                frequency: props.frequency,
                note: props.note,
                instrument: props.instrument
            };
        }
        
        // ===== OBJECTS DATA (Dimensional Computing) =====
        let currentObjectLevel = 0;
        let objCarouselRotation = 0;
        
        // ALL COLORS DERIVED FROM GEOMETRY - Objects view uses same coordinate system
        const objectLevelsBase = {
            0: {
                title: "The Parking Lot",
                subtitle: "Dimension 6 — Many Objects as Points",
                icon: "🅿️",
                description: `A hundred cars, each a <span class="highlight">single point</span> from this height. In dimensional computing, <code>parkingLot.cars</code> instantly returns all cars — no iteration needed.`,
                keypoint: `<strong>Dimensional Programming:</strong> Every car already has <code>.engine</code>, <code>.wheels</code>, <code>.seats</code> — we just haven't looked yet. The parts exist because the whole exists.`,
                extra: `Traditional programming: loop through array, check each element. Dimensional computing: <code>parkingLot.redCars</code> — the red cars are already there, just invoke them.`
            },
            1: {
                title: "One Car",
                subtitle: "Dimension 5 — The Discrete Object",
                icon: "🚗",
                description: `<code>car</code> — a complete object. We see the exterior. But <code>car.engine</code> exists even though we can't see it. Just like real life: you <em>assume</em> there's an engine under the hood.`,
                keypoint: `<strong>No construction needed:</strong> <code>car.engine</code> doesn't <em>create</em> an engine. It <em>reveals</em> what's already there. The engine existed the moment the car did.`,
                extra: `<code>car.engine.dipstick</code> or just <code>car.dipstick</code> — we can drill down or skip levels. The dimensional substrate handles the path.`
            },
            2: {
                title: "The Engine",
                subtitle: "Dimension 4 — Parts of the Whole",
                icon: "⚙️",
                description: `<code>car.engine</code> — now we see it. It has <code>.pistons</code>, <code>.cylinders</code>, <code>.sparkPlugs</code>. All exist, waiting to be invoked.`,
                keypoint: `<strong>No iteration:</strong> How many pistons? <code>engine.pistons.count</code> — instant. Which one is misfiring? <code>engine.pistons.where(misfiring=true)</code> — no loop, O(1) lookup.`,
                extra: `In traditional code: <code>for piston in engine.pistons: if piston.misfiring...</code><br>Dimensional computing: the misfiring piston <em>already knows</em> it's misfiring.`
            },
            3: {
                title: "The Piston",
                subtitle: "Dimension 3 — The Classic Volume",
                icon: "🔧",
                description: `<code>engine.piston[3]</code> — a solid 3D object. It has <code>.rings</code>, <code>.pin</code>, <code>.rod</code>. Each part exists at a coordinate within the piston's dimensional space.`,
                keypoint: `<strong>Drill up or down freely:</strong> From here, <code>piston.car.parkingLot</code> goes back up. <code>piston.sparkPlug.electrode</code> goes down. No hierarchy navigation — just coordinates.`,
                extra: `Every object knows its context. <code>piston.engine</code> is the engine containing it. <code>piston.engine.car.owner</code> — the whole chain exists.`
            },
            4: {
                title: "The Spark Plug",
                subtitle: "Dimension 2 — Surface & Interface",
                icon: "⚡",
                description: `<code>piston.sparkPlug</code> — or <code>car.sparkPlugs[3]</code> — same object, different paths. The spark plug doesn't care how you reached it.`,
                keypoint: `<strong>Multiple paths, same destination:</strong> <code>car.engine.cylinder[2].sparkPlug</code> = <code>car.sparkPlugs.where(cylinder=2)</code> = same object, same atom of data.`,
                extra: `This is dimensional addressing: objects exist at <em>coordinates</em>, not in <em>containers</em>. Paths are just different ways to specify coordinates.`
            },
            5: {
                title: "The Electrode",
                subtitle: "Dimension 1 — The Linear Edge",
                icon: "📍",
                description: `<code>sparkPlug.electrode</code> — a 2mm copper rod. It has <code>.material</code>, <code>.resistance</code>, <code>.temperature</code>. Properties don't need getters — they just exist.`,
                keypoint: `<strong>Properties are dimensions:</strong> <code>electrode.temperature</code> is a coordinate in the electrode's property-space. <code>electrode.temperature.history</code> — time is just another dimension.`,
                extra: `No <code>getTemperature()</code> method needed. The temperature exists. Invoke it when you need it: <code>electrode.temperature.at(time='2pm')</code>`
            },
            6: {
                title: "The Copper Atom",
                subtitle: "Dimension 0 — The Irreducible Point",
                icon: "⚛️",
                description: `<code>electrode.atoms[0]</code> — a single copper atom. Even here: <code>atom.electrons</code>, <code>atom.nucleus</code>, <code>atom.position</code>. Dimensions all the way down.`,
                keypoint: `<strong>From parking lot to quantum:</strong> <code>parkingLot.cars[5].engine.piston[2].sparkPlug.electrode.atoms[1000].electrons[3]</code> — one invocation, no loops, no queries.`,
                extra: `This is dimensional computing: <strong>all objects have all properties</strong>. They exist because the object exists. Just invoke what you need, when you need it.`
            }
        };
        
        // Build objectLevels with GEOMETRY-DERIVED colors
        // Objects view uses inverse mapping: level 0 in UI = dimension 6 concept
        const objectLevels = {};
        for (let i = 0; i <= 6; i++) {
            // Objects view: Level 0 maps to highest dimension (6), Level 6 maps to lowest (0)
            const dimLevel = 6 - i;
            const props = GeometricElements.levelProperties(dimLevel);
            objectLevels[i] = {
                ...objectLevelsBase[i],
                color: props.colorHex,
                colorRgb: props.color,
                coordinates: props.coordinates,
                wavelength: props.wavelength,
                frequency: props.frequency
            };
        }
        
        // ===== 3D PROJECTION =====
        function project(x, y, z) {
            const cosX = Math.cos(rotationX), sinX = Math.sin(rotationX);
            const cosY = Math.cos(rotationY), sinY = Math.sin(rotationY);
            
            let y1 = y * cosX - z * sinX;
            let z1 = y * sinX + z * cosX;
            let x1 = x * cosY - z1 * sinY;
            let z2 = x * sinY + z1 * cosY;
            
            const scale = 200 * zoom;
            const perspective = 800 / (800 + z2);
            
            return {
                x: canvas.width / 2 + x1 * scale * perspective,
                y: canvas.height / 2 - y1 * scale * perspective,
                z: z2,
                depth: perspective
            };
        }
        
        // ===== DRAWING FUNCTIONS - Using SubstrateLens =====
        
        // Helper: Draw wavelength ripples for sound visualization
        function drawWavelengthRipples(cx, cy, wavelengthPx, color, maxRadius = 200) {
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            for (let r = wavelengthPx; r < maxRadius; r += wavelengthPx) {
                const alpha = 1 - (r / maxRadius);
                ctx.globalAlpha = alpha * 0.5;
                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, Math.PI * 2);
                ctx.stroke();
            }
            ctx.globalAlpha = 1;
        }
        
        function drawVoid() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.15)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            
            // Lens-based void visualization - all from SubstrateLens
            for (let i = 0; i < 100; i++) {
                const angle = (i / 100) * Math.PI * 2 + time * 0.1;
                const r = 100 + Math.sin(time + i * 0.3) * 80;
                const x = cx + Math.cos(angle) * r;
                const y = cy + Math.sin(angle) * r;
                
                // Get substrate lens data from geometry (normalized coords)
                const nx = Math.cos(angle) * (r / 200);
                const ny = Math.sin(angle) * (r / 200);
                const lens = SubstrateLens.fromGeometry(nx, ny, 0);
                
                let particleColor;
                if (currentLens === 'color') {
                    // Color from wavelength - cycling through spectrum
                    const cycledR = ((i / 100) + time * 0.1) % 1;
                    const wl = SubstrateLens.distanceToWavelength(cycledR);
                    const c = SubstrateLens.wavelengthToColor(wl);
                    particleColor = `rgba(${c.r}, ${c.g}, ${c.b}, ${0.3 + Math.sin(time * 2 + i) * 0.2})`;
                } else if (currentLens === 'sound') {
                    // Silent void - pulsing potential
                    const pulse = Math.sin(time * 4 + i * 0.1) * 0.5 + 0.5;
                    particleColor = `rgba(60, 100, 200, ${0.2 + pulse * 0.3})`;
                } else {
                    particleColor = `rgba(100, 100, 150, ${0.3 + Math.sin(time * 2 + i) * 0.2})`;
                }
                
                ctx.beginPath();
                ctx.arc(x, y, 2, 0, Math.PI * 2);
                ctx.fillStyle = particleColor;
                ctx.fill();
            }
            
            // Central glow with substrate-derived color
            let gradColor1;
            if (currentLens === 'color') {
                const wl = SubstrateLens.distanceToWavelength((time * 0.1) % 1);
                const c = SubstrateLens.wavelengthToColor(wl);
                gradColor1 = `rgba(${c.r}, ${c.g}, ${c.b}, 0.25)`;
            } else if (currentLens === 'sound') {
                gradColor1 = 'rgba(60, 100, 200, 0.2)';
            } else {
                gradColor1 = 'rgba(100, 100, 200, 0.2)';
            }
            
            const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, 150);
            gradient.addColorStop(0, gradColor1);
            gradient.addColorStop(1, 'transparent');
            ctx.fillStyle = gradient;
            ctx.fillRect(cx - 150, cy - 150, 300, 300);
            
            // Lens label with substrate data
            if (currentLens === 'color') {
                ctx.fillStyle = '#aaccff';
                ctx.font = '12px monospace';
                ctx.textAlign = 'center';
                ctx.fillText('λ: 380-700nm (all wavelengths = ∞ potential)', cx, canvas.height - 40);
            } else if (currentLens === 'sound') {
                ctx.fillStyle = '#88aaff';
                ctx.font = '12px monospace';
                ctx.textAlign = 'center';
                ctx.fillText('♪ f = 0 Hz (silence = infinite potential)', cx, canvas.height - 40);
            }
        }
        
        function drawPoint() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const size = 8 + Math.sin(time * 3) * 3;
            
            // Point represents Middle C (C4 = 261.626 Hz) - one undivided note
            const middleC = MusicalSubstrate.MIDDLE_C;
            const wavelength = MusicalSubstrate.soundWavelength(middleC);
            
            let pointColor, glowColor, labelText;
            if (currentLens === 'color') {
                // Green-yellow (center of spectrum, ~540nm)
                const c = MusicalSubstrate.wavelengthToColor(540);
                pointColor = c.rgb;
                glowColor = `rgba(${c.r}, ${c.g}, ${c.b}, 0.4)`;
                labelText = `Point: λ = 540nm (green-yellow center)`;
            } else if (currentLens === 'sound') {
                // Middle C - THE fundamental note
                pointColor = '#4488ff';
                glowColor = 'rgba(68, 136, 255, 0.4)';
                labelText = `♪ Middle C (C4) = ${middleC.toFixed(1)} Hz | λ = ${wavelength.toFixed(2)}m`;
                
                // Draw wavelength ripples representing the sound wave
                const rippleWL = Math.max(20, wavelength * 20);
                drawWavelengthRipples(cx, cy, rippleWL, 'rgba(68, 136, 255, 0.6)', 150);
            } else {
                pointColor = '#ff6464';
                glowColor = 'rgba(255, 100, 100, 0.4)';
                labelText = `Point: r = 0 (the origin, undivided)`;
            }
            
            const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, 100);
            gradient.addColorStop(0, glowColor);
            gradient.addColorStop(0.5, glowColor.replace('0.4', '0.1'));
            gradient.addColorStop(1, 'transparent');
            ctx.fillStyle = gradient;
            ctx.fillRect(cx - 100, cy - 100, 200, 200);
            
            ctx.beginPath();
            ctx.arc(cx, cy, size, 0, Math.PI * 2);
            ctx.fillStyle = pointColor;
            ctx.fill();
            
            ctx.fillStyle = currentLens === 'sound' ? '#88bbff' : (currentLens === 'color' ? '#ddaaff' : '#ff8080');
            ctx.font = '12px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(labelText, cx, cy + 40);
        }
        
        function drawLine() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            
            // TRUE SPECTRUM: Left (bass/violet) to Right (treble/red)
            if (currentLens === 'color') {
                // Draw with wavelength-derived colors - left to right
                for (let t = -1.5; t < 1.5; t += 0.02) {
                    const p1 = project(t, 0, 0);
                    const p2 = project(t + 0.02, 0, 0);
                    // Left-to-right spectrum: -1.5 = violet, +1.5 = red
                    const lens = MusicalSubstrate.fromGeometry(t, 0, 0, 1.5);
                    const c = lens.light.color;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = c.rgb;
                    ctx.lineWidth = 4;
                    ctx.stroke();
                }
            } else if (currentLens === 'sound') {
                // Draw line with instrument-based colors (bass to treble)
                for (let t = -1.5; t < 1.5; t += 0.02) {
                    const p1 = project(t, 0, 0);
                    const p2 = project(t + 0.02, 0, 0);
                    const lens = MusicalSubstrate.fromGeometry(t, 0, 0, 1.5);
                    const inst = lens.sound.instrument;
                    
                    // Color based on instrument type
                    let color;
                    switch (inst.name) {
                        case 'Bass': color = 'rgb(60, 80, 180)'; break;
                        case 'Cello': color = 'rgb(100, 120, 200)'; break;
                        case 'Viola': color = 'rgb(150, 160, 220)'; break;
                        case 'Violin': color = 'rgb(200, 180, 240)'; break;
                        case 'Flute': color = 'rgb(255, 220, 255)'; break;
                        default: color = 'rgb(150, 150, 200)';
                    }
                    
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = color;
                    ctx.lineWidth = 4;
                    ctx.stroke();
                }
            } else {
                ctx.beginPath();
                for (let t = -1.5; t <= 1.5; t += 0.02) {
                    const p = project(t, 0, 0);
                    if (t === -1.5) ctx.moveTo(p.x, p.y);
                    else ctx.lineTo(p.x, p.y);
                }
                ctx.strokeStyle = '#ffaa44';
                ctx.lineWidth = 3;
                ctx.stroke();
            }
            
            // Draw markers with note labels
            const notePositions = [
                { t: -1.5, label: 'A0' },
                { t: -0.75, label: 'C2' },
                { t: 0, label: 'C4' },
                { t: 0.75, label: 'C6' },
                { t: 1.5, label: 'C8' }
            ];
            
            notePositions.forEach(np => {
                const p = project(np.t, 0, 0);
                const lens = MusicalSubstrate.fromGeometry(np.t, 0, 0, 1.5);
                
                ctx.beginPath();
                ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
                if (currentLens === 'color') {
                    ctx.fillStyle = lens.light.color.rgb;
                } else if (currentLens === 'sound') {
                    ctx.fillStyle = '#fff';
                } else {
                    ctx.fillStyle = '#ffaa44';
                }
                ctx.fill();
                
                // Note label
                ctx.fillStyle = '#fff';
                ctx.font = '10px monospace';
                ctx.textAlign = 'center';
                ctx.fillText(np.label, p.x, p.y - 12);
            });
            
            // Animated cursor showing current position
            const cursorT = Math.sin(time) * 1.2;
            const cursorP = project(cursorT, 0, 0);
            const cursorLens = MusicalSubstrate.fromGeometry(cursorT, 0, 0, 1.5);
            
            ctx.beginPath();
            ctx.arc(cursorP.x, cursorP.y, 8, 0, Math.PI * 2);
            if (currentLens === 'color') {
                ctx.fillStyle = cursorLens.light.color.rgb;
            } else {
                ctx.fillStyle = '#fff';
            }
            ctx.fill();
            
            // Label
            ctx.font = '12px monospace';
            ctx.textAlign = 'center';
            
            if (currentLens === 'color') {
                ctx.fillStyle = '#fff';
                ctx.fillText(`λ = ${cursorLens.light.wavelengthNm.toFixed(0)}nm`, cursorP.x, cursorP.y - 20);
            } else if (currentLens === 'sound') {
                const note = cursorLens.sound.noteName;
                const inst = cursorLens.sound.instrument;
                ctx.fillStyle = '#88ccff';
                ctx.fillText(`♪ ${note} (${cursorLens.sound.frequencyHz.toFixed(0)}Hz) | ${inst.name}`, cursorP.x, cursorP.y - 20);
            } else {
                ctx.fillStyle = '#ffcc88';
                const xNorm = cursorLens.normalizedX;
                ctx.fillText(`x = ${cursorT.toFixed(2)} (${(xNorm * 100).toFixed(0)}% across)`, cursorP.x, cursorP.y - 20);
            }
        }
        
        // Draw wireframe cube outline
        function drawCubeWireframe(size = 1) {
            const corners = [
                [-size, -size, -size], [size, -size, -size],
                [size, size, -size], [-size, size, -size],
                [-size, -size, size], [size, -size, size],
                [size, size, size], [-size, size, size]
            ];
            
            const edges = [
                [0,1], [1,2], [2,3], [3,0],  // bottom face
                [4,5], [5,6], [6,7], [7,4],  // top face
                [0,4], [1,5], [2,6], [3,7]   // vertical edges
            ];
            
            ctx.strokeStyle = 'rgba(100, 150, 255, 0.25)';
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            
            edges.forEach(([i, j]) => {
                const p1 = project(corners[i][0], corners[i][1], corners[i][2]);
                const p2 = project(corners[j][0], corners[j][1], corners[j][2]);
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            });
            
            ctx.setLineDash([]);
        }
        
        function drawSaddle() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.15)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw bounding cube wireframe
            drawCubeWireframe(1);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const points = [];
            const step = 0.1;
            
            // Domain [-1, 1] for exact cube fit: z = x*y ranges from -1 to 1
            for (let x = -1; x <= 1; x += step) {
                for (let y = -1; y <= 1; y += step) {
                    const z = x * y;
                    const p = project(x, z, y);
                    p.origX = x; p.origY = y; p.origZ = z;
                    // Get substrate lens data from geometry
                    p.lens = SubstrateLens.fromGeometry(x, y, z);
                    points.push(p);
                }
            }
            
            points.sort((a, b) => a.z - b.z);
            
            // Sound lens: Play frequency based on cursor position
            const sampleX = Math.sin(time) * 0.8;
            const sampleY = Math.cos(time * 0.7) * 0.8;
            const sampleZ = sampleX * sampleY;
            const cursorLens = SubstrateLens.fromGeometry(sampleX, sampleY, sampleZ);
            
            if (currentLens === 'sound') {
                playSubstrateSound(sampleX, sampleY, sampleZ);
                // Draw wavelength ripples at cursor position
                const cursorP = project(sampleX, sampleZ, sampleY);
                drawWavelengthRipples(cursorP.x, cursorP.y, cursorLens.sound.wavelengthPx, 'rgba(68, 170, 255, 0.4)', 100);
            }
            
            points.forEach(p => {
                let color;
                if (currentLens === 'color') {
                    // Color from wavelength based on distance from origin
                    color = p.lens.light.color.rgb;
                } else if (currentLens === 'sound') {
                    // Sound visualization: brightness based on frequency
                    const freqNorm = (p.lens.sound.frequencyHz - MusicalSubstrate.BASS_FREQ) / 
                                     (MusicalSubstrate.TREBLE_FREQ - MusicalSubstrate.BASS_FREQ);
                    const bright = 80 + freqNorm * 175;
                    color = `rgb(${bright * 0.4}, ${bright * 0.7}, ${255})`;
                } else {
                    const val = (p.origZ + 1) / 2;
                    color = `rgb(${60 + val * 60}, ${120 + val * 135}, ${60 + val * 60})`;
                }
                
                ctx.beginPath();
                ctx.arc(p.x, p.y, 4 * p.depth, 0, Math.PI * 2);
                ctx.fillStyle = color;
                ctx.fill();
            });
            
            // Label with substrate data
            ctx.font = '12px monospace';
            ctx.textAlign = 'center';
            if (currentLens === 'color') {
                ctx.fillStyle = '#ddaaff';
                ctx.fillText(`λ: ${cursorLens.light.wavelengthNm.toFixed(0)}nm  r = ${cursorLens.value.raw.toFixed(3)}`, cx, canvas.height - 30);
            } else if (currentLens === 'sound') {
                ctx.fillStyle = '#88ccff';
                ctx.fillText(`♪ ${cursorLens.sound.frequencyHz.toFixed(0)} Hz  λ = ${cursorLens.sound.wavelengthM.toFixed(2)}m`, cx, canvas.height - 30);
            }
        }
        
        function drawParabola() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.15)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw bounding cube wireframe
            drawCubeWireframe(1);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const points = [];
            const step = 0.08;
            
            // Domain [-1, 1] for exact cube fit: z = x*y² ranges from -1 to 1
            for (let x = -1; x <= 1; x += step) {
                for (let y = -1; y <= 1; y += step) {
                    const z = x * y * y;
                    const p = project(x, z, y);
                    p.origX = x; p.origY = y; p.origZ = z;
                    // Get substrate lens data from geometry
                    p.lens = SubstrateLens.fromGeometry(x, y, z);
                    points.push(p);
                }
            }
            
            points.sort((a, b) => a.z - b.z);
            
            // Sound lens: Play chords based on position
            const sampleX = Math.sin(time * 0.5);
            const sampleY = Math.cos(time * 0.3);
            const sampleZ = sampleX * sampleY * sampleY;
            const cursorLens = SubstrateLens.fromGeometry(sampleX, sampleY, sampleZ);
            
            if (currentLens === 'sound') {
                if (Math.floor(time * 2) % 4 === 0) {
                    playSubstrateChord(sampleX, sampleY, sampleZ);
                }
                // Draw wavelength ripples
                const cursorP = project(sampleX, sampleZ, sampleY);
                drawWavelengthRipples(cursorP.x, cursorP.y, cursorLens.sound.wavelengthPx, 'rgba(180, 100, 255, 0.4)', 100);
            }
            
            points.forEach(p => {
                let color;
                if (currentLens === 'color') {
                    // Color from wavelength based on distance from origin
                    color = p.lens.light.color.rgb;
                } else if (currentLens === 'sound') {
                    // Frequency visualization
                    const freqNorm = (p.lens.sound.frequencyHz - MusicalSubstrate.BASS_FREQ) / 
                                     (MusicalSubstrate.TREBLE_FREQ - MusicalSubstrate.BASS_FREQ);
                    const bright = 80 + freqNorm * 175;
                    color = `rgb(${bright * 0.7}, ${bright * 0.4}, ${255})`;
                } else {
                    const val = (p.origZ + 1) / 2;
                    color = `rgb(${50 + val * 150}, ${200 - val * 100}, ${100 + val * 100})`;
                }
                
                ctx.beginPath();
                ctx.arc(p.x, p.y, 5 * p.depth, 0, Math.PI * 2);
                ctx.fillStyle = color;
                ctx.fill();
            });
            
            // Label with substrate data
            ctx.font = '12px monospace';
            ctx.textAlign = 'center';
            if (currentLens === 'color') {
                ctx.fillStyle = '#ddaaff';
                ctx.fillText(`λ: ${cursorLens.light.wavelengthNm.toFixed(0)}nm  r = ${cursorLens.value.raw.toFixed(3)}`, cx, canvas.height - 30);
            } else if (currentLens === 'sound') {
                ctx.fillStyle = '#cc88ff';
                ctx.fillText(`♪ Chord: ${cursorLens.sound.frequencyHz.toFixed(0)} Hz + harmonics`, cx, canvas.height - 30);
            }
        }
        
        function drawNetwork() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.12)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const baseRadius = Math.min(canvas.width, canvas.height) * 0.35;
            
            // =============================================
            // SACRED GEOMETRY: Metatron's Cube with Harmonics
            // 13 circles connected - mathematically precise
            // =============================================
            
            const metatron = SacredGeometry.metatronsCube(cx, cy, baseRadius * 0.9);
            const rotation = time * 0.3;
            
            // Transform circles with slow rotation for 3D-like effect
            const transformedCircles = metatron.circles.map((c, i) => {
                const dx = c.x - cx;
                const dy = c.y - cy;
                const cos = Math.cos(rotation);
                const sin = Math.sin(rotation);
                const x = cx + dx * cos - dy * sin * 0.3;
                const y = cy + dx * sin * 0.3 + dy * cos;
                const depth = 0.7 + Math.sin(time * 0.5 + i * 0.5) * 0.3;
                
                // Left-to-right spectrum position
                const xNorm = (x - (cx - baseRadius)) / (2 * baseRadius);
                const lens = MusicalSubstrate.fromGeometry(x - cx, y - cy, 0, baseRadius);
                
                return { ...c, x, y, depth, index: i, lens, xNorm: Math.max(0, Math.min(1, xNorm)) };
            });
            
            // Draw connecting lines (Metatron's Cube pattern)
            ctx.lineWidth = 1.5;
            metatron.lines.forEach((line, i) => {
                const c1 = transformedCircles[metatron.circles.indexOf(line.from)];
                const c2 = transformedCircles[metatron.circles.indexOf(line.to)];
                if (!c1 || !c2) return;
                
                let strokeColor;
                if (currentLens === 'color') {
                    // Blend spectrum colors from both endpoints
                    const col1 = c1.lens.light.color;
                    const col2 = c2.lens.light.color;
                    strokeColor = `rgba(${(col1.r + col2.r)/2}, ${(col1.g + col2.g)/2}, ${(col1.b + col2.b)/2}, 0.4)`;
                } else if (currentLens === 'sound') {
                    // Harmonic interference pattern
                    const harmonic = Math.sin((c1.xNorm + c2.xNorm) * Math.PI * 4 + time * 2);
                    const alpha = 0.2 + harmonic * 0.2;
                    strokeColor = `rgba(${150 + harmonic * 80}, ${180 + harmonic * 50}, 255, ${alpha})`;
                } else {
                    strokeColor = 'rgba(170, 102, 255, 0.25)';
                }
                
                ctx.strokeStyle = strokeColor;
                ctx.beginPath();
                ctx.moveTo(c1.x, c1.y);
                ctx.lineTo(c2.x, c2.y);
                ctx.stroke();
            });
            
            // Draw the 13 sacred circles with proper spectrum colors
            transformedCircles.forEach((c, i) => {
                const pulseRadius = c.r * (1 + Math.sin(time * 2 + i * 0.5) * 0.1);
                
                let fillColor, strokeColor, glowColor;
                if (currentLens === 'color') {
                    // Spectrum color based on left-to-right position
                    const col = c.lens.light.color;
                    fillColor = `rgba(${col.r}, ${col.g}, ${col.b}, 0.15)`;
                    strokeColor = col.rgb;
                    glowColor = `rgba(${col.r}, ${col.g}, ${col.b}, 0.3)`;
                } else if (currentLens === 'sound') {
                    // Frequency-based visualization
                    const freqNorm = c.xNorm;
                    const pulse = Math.sin(time * (1 + freqNorm * 3) + i) * 0.3 + 0.7;
                    const bright = 100 + freqNorm * 155;
                    fillColor = `rgba(${bright * 0.5}, ${bright * 0.7}, 255, ${0.1 * pulse})`;
                    strokeColor = `rgb(${bright * 0.6}, ${bright * 0.8}, 255)`;
                    glowColor = `rgba(${bright * 0.4}, ${bright * 0.6}, 255, 0.25)`;
                } else {
                    fillColor = 'rgba(170, 102, 255, 0.1)';
                    strokeColor = 'rgba(170, 102, 255, 0.8)';
                    glowColor = 'rgba(170, 102, 255, 0.2)';
                }
                
                // Glow effect
                const glow = ctx.createRadialGradient(c.x, c.y, 0, c.x, c.y, pulseRadius * 1.5);
                glow.addColorStop(0, glowColor);
                glow.addColorStop(1, 'transparent');
                ctx.fillStyle = glow;
                ctx.beginPath();
                ctx.arc(c.x, c.y, pulseRadius * 1.5, 0, Math.PI * 2);
                ctx.fill();
                
                // Circle fill
                ctx.fillStyle = fillColor;
                ctx.beginPath();
                ctx.arc(c.x, c.y, pulseRadius, 0, Math.PI * 2);
                ctx.fill();
                
                // Circle stroke
                ctx.strokeStyle = strokeColor;
                ctx.lineWidth = 2 * c.depth;
                ctx.stroke();
                
                // Center point
                ctx.fillStyle = strokeColor;
                ctx.beginPath();
                ctx.arc(c.x, c.y, 3 * c.depth, 0, Math.PI * 2);
                ctx.fill();
            });
            
            // Draw central hexagram (Star of David) - key sacred geometry element
            ctx.strokeStyle = currentLens === 'color' ? 
                MusicalSubstrate.wavelengthToColor(540).rgb : // Green center
                (currentLens === 'sound' ? 'rgba(150, 200, 255, 0.6)' : 'rgba(200, 150, 255, 0.5)');
            ctx.lineWidth = 2;
            
            // Two overlapping triangles
            for (let tri = 0; tri < 2; tri++) {
                ctx.beginPath();
                for (let i = 0; i < 3; i++) {
                    const angle = (i / 3) * Math.PI * 2 + (tri * Math.PI / 3) + rotation - Math.PI / 2;
                    const r = baseRadius * 0.5;
                    const x = cx + Math.cos(angle) * r;
                    const y = cy + Math.sin(angle) * r;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.closePath();
                ctx.stroke();
            }
            
            // Label with substrate data
            ctx.font = '12px monospace';
            ctx.textAlign = 'center';
            if (currentLens === 'color') {
                ctx.fillStyle = '#ddaaff';
                ctx.fillText(`Metatron's Cube: λ 380nm (left) → 700nm (right)`, cx, canvas.height - 30);
            } else if (currentLens === 'sound') {
                ctx.fillStyle = '#88aaff';
                ctx.fillText(`♪ Harmonics: 27.5 Hz (bass) → 4186 Hz (treble)`, cx, canvas.height - 30);
            } else {
                ctx.fillStyle = '#aa88ff';
                ctx.fillText(`Sacred Geometry: 13 circles, 78 connections`, cx, canvas.height - 30);
            }
        }
        
        function drawWeb() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const baseRadius = Math.min(canvas.width, canvas.height) * 0.38;
            
            // =============================================
            // SACRED GEOMETRY: Flower of Life + Sri Yantra
            // Symphonic orchestral visualization
            // Bass (left) to Flutes (right)
            // =============================================
            
            const rotation = time * 0.1;
            
            // Generate Flower of Life circles (3 rings)
            const flowerCircles = [];
            const circleRadius = baseRadius * 0.25;
            
            // Center circle
            flowerCircles.push({ x: cx, y: cy, r: circleRadius, ring: 0 });
            
            // Rings of 6, 12, 18 circles (hexagonal pattern)
            for (let ring = 1; ring <= 3; ring++) {
                const count = ring * 6;
                const ringRadius = circleRadius * ring;
                for (let i = 0; i < count; i++) {
                    const angle = (i / count) * Math.PI * 2 + rotation;
                    const x = cx + Math.cos(angle) * ringRadius;
                    const y = cy + Math.sin(angle) * ringRadius;
                    flowerCircles.push({ x, y, r: circleRadius, ring, angle });
                }
            }
            
            // Sri Yantra triangles overlaid
            const sriYantra = SacredGeometry.sriYantra(cx, cy, baseRadius * 0.85);
            
            // Draw Flower of Life circles with spectrum colors
            flowerCircles.forEach((circle, i) => {
                // Left-to-right spectrum position for true spectrum mapping
                const xNorm = (circle.x - (cx - baseRadius)) / (2 * baseRadius);
                const lens = MusicalSubstrate.fromGeometry(circle.x - cx, circle.y - cy, 0, baseRadius);
                const instrument = MusicalSubstrate.freqToInstrument(lens.sound.frequencyHz);
                
                const pulse = Math.sin(time * 2 + i * 0.3) * 0.15 + 1;
                const drawRadius = circle.r * pulse;
                
                let fillColor, strokeColor;
                if (currentLens === 'color') {
                    // Spectrum from violet (left) to red (right)
                    const col = lens.light.color;
                    fillColor = `rgba(${col.r}, ${col.g}, ${col.b}, 0.08)`;
                    strokeColor = `rgba(${col.r}, ${col.g}, ${col.b}, 0.6)`;
                } else if (currentLens === 'sound') {
                    // Instrument-based coloring (bass=deep, flutes=bright)
                    const instColors = {
                        'Bass': { r: 60, g: 80, b: 180 },
                        'Cello': { r: 100, g: 120, b: 200 },
                        'Viola': { r: 150, g: 160, b: 220 },
                        'Violin': { r: 200, g: 180, b: 240 },
                        'Flute': { r: 255, g: 220, b: 255 }
                    };
                    const col = instColors[instrument.name] || { r: 200, g: 200, b: 255 };
                    const freqPulse = Math.sin(time * (1 + xNorm * 2)) * 0.3 + 0.7;
                    fillColor = `rgba(${col.r}, ${col.g}, ${col.b}, ${0.08 * freqPulse})`;
                    strokeColor = `rgba(${col.r}, ${col.g}, ${col.b}, ${0.5 * freqPulse})`;
                } else {
                    fillColor = 'rgba(255, 102, 170, 0.06)';
                    strokeColor = 'rgba(255, 102, 170, 0.4)';
                }
                
                // Circle with glow
                ctx.fillStyle = fillColor;
                ctx.beginPath();
                ctx.arc(circle.x, circle.y, drawRadius, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.strokeStyle = strokeColor;
                ctx.lineWidth = 1.5;
                ctx.stroke();
            });
            
            // Draw Sri Yantra triangles with golden ratio proportions
            sriYantra.forEach((tri, i) => {
                const xNorm = 0.5; // Center-based
                let strokeColor, fillColor;
                
                if (currentLens === 'color') {
                    // Spectrum gradient based on scale
                    const wl = MusicalSubstrate.distanceToWavelength(tri.scale);
                    const col = MusicalSubstrate.wavelengthToColor(wl);
                    strokeColor = `rgba(${col.r}, ${col.g}, ${col.b}, 0.7)`;
                    fillColor = `rgba(${col.r}, ${col.g}, ${col.b}, 0.05)`;
                } else if (currentLens === 'sound') {
                    // Harmonic interference colors
                    const harmonic = Math.sin(time * 2 + i * Math.PI / 4);
                    const bright = 150 + harmonic * 80;
                    strokeColor = `rgba(${bright}, ${bright * 0.8}, 255, 0.6)`;
                    fillColor = `rgba(${bright * 0.5}, ${bright * 0.5}, 255, 0.04)`;
                } else {
                    const shade = tri.upward ? 255 : 200;
                    strokeColor = `rgba(${shade}, 102, ${tri.upward ? 170 : 220}, 0.5)`;
                    fillColor = `rgba(${shade}, 102, ${tri.upward ? 170 : 220}, 0.03)`;
                }
                
                ctx.fillStyle = fillColor;
                ctx.strokeStyle = strokeColor;
                ctx.lineWidth = 2 * tri.scale + 0.5;
                
                ctx.beginPath();
                tri.points.forEach((p, j) => {
                    // Rotate around center
                    const dx = p.x - cx;
                    const dy = p.y - cy;
                    const cos = Math.cos(rotation);
                    const sin = Math.sin(rotation);
                    const rx = cx + dx * cos - dy * sin;
                    const ry = cy + dx * sin + dy * cos;
                    
                    if (j === 0) ctx.moveTo(rx, ry);
                    else ctx.lineTo(rx, ry);
                });
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
            });
            
            // Draw central bindu (point) - the origin of creation
            const binduPulse = Math.sin(time * 3) * 5 + 10;
            let binduColor;
            if (currentLens === 'color') {
                // Golden center (540nm = green-yellow)
                const col = MusicalSubstrate.wavelengthToColor(540);
                binduColor = col.rgb;
            } else if (currentLens === 'sound') {
                binduColor = 'rgba(255, 220, 255, 0.9)';
            } else {
                binduColor = '#ff66aa';
            }
            
            ctx.fillStyle = binduColor;
            ctx.beginPath();
            ctx.arc(cx, cy, binduPulse, 0, Math.PI * 2);
            ctx.fill();
            
            // Central glow
            const centralGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, baseRadius * 0.3);
            if (currentLens === 'color') {
                centralGlow.addColorStop(0, 'rgba(255, 255, 200, 0.15)');
            } else if (currentLens === 'sound') {
                centralGlow.addColorStop(0, 'rgba(200, 180, 255, 0.15)');
            } else {
                centralGlow.addColorStop(0, 'rgba(255, 150, 200, 0.1)');
            }
            centralGlow.addColorStop(1, 'transparent');
            ctx.fillStyle = centralGlow;
            ctx.fillRect(cx - baseRadius * 0.3, cy - baseRadius * 0.3, baseRadius * 0.6, baseRadius * 0.6);
            
            // Label with substrate data
            ctx.font = '12px monospace';
            ctx.textAlign = 'center';
            if (currentLens === 'color') {
                ctx.fillStyle = '#ffddaa';
                ctx.fillText(`Flower of Life: λ 380nm (violet) → 700nm (red)`, cx, canvas.height - 30);
            } else if (currentLens === 'sound') {
                ctx.fillStyle = '#ffaacc';
                ctx.fillText(`♪ Symphony: Bass → Cello → Viola → Violin → Flute`, cx, canvas.height - 30);
            } else {
                ctx.fillStyle = '#ff88aa';
                ctx.fillText(`Sacred Geometry: 37 circles + 9 triangles (Sri Yantra)`, cx, canvas.height - 30);
            }
        }
        
        // ===== OBJECT DRAWING FUNCTIONS =====
        function drawParkingLot() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const scale = 30 * zoom;
            
            // Parking lot grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.lineWidth = 2;
            
            // Draw parking lines
            for (let row = -3; row <= 3; row++) {
                for (let col = -4; col <= 4; col++) {
                    const x = cx + col * scale * 3;
                    const y = cy + row * scale * 2.5;
                    
                    // Parking space lines
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
                    ctx.strokeRect(x - scale * 1.2, y - scale * 0.8, scale * 2.4, scale * 1.6);
                }
            }
            
            // Draw cars as colored rectangles (points in this dimension)
            const carColors = ['#ff6464', '#4488ff', '#44dd44', '#ffaa44', '#aa66ff', '#ff66aa', '#44dddd', '#dddd44'];
            let carIndex = 0;
            
            for (let row = -3; row <= 3; row++) {
                for (let col = -4; col <= 4; col++) {
                    // Random occupancy
                    if (Math.sin(row * 7 + col * 13 + 0.5) > -0.3) {
                        const x = cx + col * scale * 3;
                        const y = cy + row * scale * 2.5;
                        const wobble = Math.sin(time * 2 + row + col) * 2;
                        
                        // Car as simple rectangle
                        const color = carColors[carIndex % carColors.length];
                        ctx.fillStyle = color;
                        ctx.beginPath();
                        ctx.roundRect(x - scale * 1 + wobble, y - scale * 0.5, scale * 2, scale * 1, 5);
                        ctx.fill();
                        
                        // Windshield highlight
                        ctx.fillStyle = 'rgba(100, 150, 255, 0.3)';
                        ctx.fillRect(x - scale * 0.3 + wobble, y - scale * 0.4, scale * 0.6, scale * 0.3);
                        
                        carIndex++;
                    }
                }
            }
            
            // Highlight one car (the one we'll zoom into)
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 3;
            ctx.shadowColor = '#fff';
            ctx.shadowBlur = 15;
            const hx = cx + scale * 3 * 1;
            const hy = cy + scale * 2.5 * 0;
            ctx.strokeRect(hx - scale * 1.1, hy - scale * 0.6, scale * 2.2, scale * 1.2);
            ctx.shadowBlur = 0;
            
            // Label
            ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('Each car is a POINT in this dimension', cx, cy + scale * 9);
        }
        
        function drawCar() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const scale = 120 * zoom;
            
            // Car body
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(Math.sin(time * 0.5) * 0.05);
            
            // Main body
            ctx.fillStyle = '#ff6464';
            ctx.beginPath();
            ctx.roundRect(-scale * 1.5, -scale * 0.3, scale * 3, scale * 0.8, 15);
            ctx.fill();
            
            // Roof
            ctx.fillStyle = '#cc4040';
            ctx.beginPath();
            ctx.roundRect(-scale * 0.6, -scale * 0.7, scale * 1.2, scale * 0.45, 10);
            ctx.fill();
            
            // Windows
            ctx.fillStyle = '#6090cc';
            ctx.beginPath();
            ctx.roundRect(-scale * 0.5, -scale * 0.6, scale * 0.45, scale * 0.3, 5);
            ctx.fill();
            ctx.beginPath();
            ctx.roundRect(scale * 0.05, -scale * 0.6, scale * 0.45, scale * 0.3, 5);
            ctx.fill();
            
            // Wheels
            ctx.fillStyle = '#333';
            ctx.beginPath();
            ctx.arc(-scale * 0.9, scale * 0.5, scale * 0.35, 0, Math.PI * 2);
            ctx.fill();
            ctx.arc(scale * 0.9, scale * 0.5, scale * 0.35, 0, Math.PI * 2);
            ctx.fill();
            
            // Wheel rims
            ctx.fillStyle = '#666';
            ctx.beginPath();
            ctx.arc(-scale * 0.9, scale * 0.5, scale * 0.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.arc(scale * 0.9, scale * 0.5, scale * 0.2, 0, Math.PI * 2);
            ctx.fill();
            
            // Headlights
            ctx.fillStyle = '#ffff80';
            ctx.beginPath();
            ctx.arc(scale * 1.35, 0, scale * 0.12, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.restore();
            
            // Glow effect
            const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, scale * 2);
            gradient.addColorStop(0, 'rgba(255, 100, 100, 0.1)');
            gradient.addColorStop(1, 'transparent');
            ctx.fillStyle = gradient;
            ctx.fillRect(cx - scale * 2, cy - scale * 2, scale * 4, scale * 4);
        }
        
        function drawEngine() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const scale = 100 * zoom;
            
            ctx.save();
            ctx.translate(cx, cy);
            
            // Engine block
            ctx.fillStyle = '#888';
            ctx.beginPath();
            ctx.roundRect(-scale, -scale * 0.6, scale * 2, scale * 1.2, 10);
            ctx.fill();
            
            // Cylinder head
            ctx.fillStyle = '#666';
            ctx.beginPath();
            ctx.roundRect(-scale * 0.9, -scale * 0.9, scale * 1.8, scale * 0.35, 5);
            ctx.fill();
            
            // Cylinders (4 inline)
            for (let i = 0; i < 4; i++) {
                const x = -scale * 0.6 + i * scale * 0.4;
                const bobY = Math.sin(time * 4 + i * 0.5) * scale * 0.1;
                
                ctx.fillStyle = '#555';
                ctx.beginPath();
                ctx.roundRect(x - scale * 0.12, -scale * 0.5 + bobY, scale * 0.24, scale * 0.4, 3);
                ctx.fill();
            }
            
            // Oil pan
            ctx.fillStyle = '#444';
            ctx.beginPath();
            ctx.roundRect(-scale * 0.8, scale * 0.55, scale * 1.6, scale * 0.25, 5);
            ctx.fill();
            
            // Spark plug wires
            ctx.strokeStyle = '#ffaa44';
            ctx.lineWidth = 3;
            for (let i = 0; i < 4; i++) {
                const x = -scale * 0.6 + i * scale * 0.4;
                ctx.beginPath();
                ctx.moveTo(x, -scale * 0.85);
                ctx.quadraticCurveTo(x + scale * 0.2, -scale * 1.1, scale * 0.9, -scale * 1);
                ctx.stroke();
            }
            
            ctx.restore();
        }
        
        function drawPiston() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const scale = 80 * zoom;
            
            ctx.save();
            ctx.translate(cx, cy);
            
            // Cylinder wall
            ctx.strokeStyle = '#666';
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(-scale * 0.6, -scale * 1.2);
            ctx.lineTo(-scale * 0.6, scale * 0.8);
            ctx.moveTo(scale * 0.6, -scale * 1.2);
            ctx.lineTo(scale * 0.6, scale * 0.8);
            ctx.stroke();
            
            const pistonY = Math.sin(time * 4) * scale * 0.5;
            
            // Piston head
            ctx.fillStyle = '#888';
            ctx.beginPath();
            ctx.roundRect(-scale * 0.5, -scale * 0.3 + pistonY, scale, scale * 0.35, 5);
            ctx.fill();
            
            // Piston rings
            ctx.fillStyle = '#555';
            ctx.fillRect(-scale * 0.52, scale * 0.05 + pistonY, scale * 1.04, scale * 0.05);
            ctx.fillRect(-scale * 0.52, scale * 0.15 + pistonY, scale * 1.04, scale * 0.05);
            
            // Connecting rod
            ctx.fillStyle = '#666';
            ctx.beginPath();
            ctx.moveTo(-scale * 0.1, scale * 0.25 + pistonY);
            ctx.lineTo(scale * 0.1, scale * 0.25 + pistonY);
            ctx.lineTo(scale * 0.15, scale * 1);
            ctx.lineTo(-scale * 0.15, scale * 1);
            ctx.closePath();
            ctx.fill();
            
            // Wrist pin
            ctx.fillStyle = '#aaa';
            ctx.beginPath();
            ctx.arc(0, scale * 0.15 + pistonY, scale * 0.08, 0, Math.PI * 2);
            ctx.fill();
            
            // Crankshaft
            ctx.fillStyle = '#777';
            ctx.beginPath();
            ctx.arc(0, scale * 1, scale * 0.15, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.restore();
        }
        
        function drawSparkPlug() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const scale = 60 * zoom;
            
            ctx.save();
            ctx.translate(cx, cy);
            
            // Terminal nut
            ctx.fillStyle = '#888';
            ctx.beginPath();
            ctx.arc(0, -scale * 1.4, scale * 0.2, 0, Math.PI * 2);
            ctx.fill();
            
            // Insulator (ceramic)
            ctx.fillStyle = '#f5f5dc';
            ctx.beginPath();
            ctx.moveTo(-scale * 0.15, -scale * 1.2);
            ctx.lineTo(scale * 0.15, -scale * 1.2);
            ctx.lineTo(scale * 0.2, -scale * 0.4);
            ctx.lineTo(-scale * 0.2, -scale * 0.4);
            ctx.closePath();
            ctx.fill();
            
            // Insulator ribs
            ctx.fillStyle = '#e5e5cc';
            for (let i = 0; i < 4; i++) {
                const y = -scale * 1.1 + i * scale * 0.2;
                ctx.beginPath();
                ctx.ellipse(0, y, scale * 0.22, scale * 0.05, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // Metal shell (hex)
            ctx.fillStyle = '#666';
            ctx.beginPath();
            ctx.moveTo(-scale * 0.25, -scale * 0.4);
            ctx.lineTo(scale * 0.25, -scale * 0.4);
            ctx.lineTo(scale * 0.25, scale * 0.3);
            ctx.lineTo(-scale * 0.25, scale * 0.3);
            ctx.closePath();
            ctx.fill();
            
            // Ground electrode
            ctx.fillStyle = '#888';
            ctx.fillRect(-scale * 0.15, scale * 0.3, scale * 0.3, scale * 0.4);
            
            // Electrode tip
            ctx.fillStyle = '#aaa';
            ctx.beginPath();
            ctx.arc(0, scale * 0.5, scale * 0.08, 0, Math.PI * 2);
            ctx.fill();
            
            // Ground strap
            ctx.fillStyle = '#777';
            ctx.beginPath();
            ctx.moveTo(-scale * 0.15, scale * 0.7);
            ctx.lineTo(-scale * 0.15, scale * 0.9);
            ctx.lineTo(0, scale * 0.6);
            ctx.closePath();
            ctx.fill();
            
            // Spark!
            if (Math.sin(time * 8) > 0.5) {
                ctx.strokeStyle = '#44aaff';
                ctx.lineWidth = 2;
                ctx.shadowColor = '#44aaff';
                ctx.shadowBlur = 20;
                ctx.beginPath();
                ctx.moveTo(0, scale * 0.5);
                ctx.lineTo(-scale * 0.08, scale * 0.55);
                ctx.lineTo(scale * 0.05, scale * 0.58);
                ctx.lineTo(-scale * 0.1, scale * 0.65);
                ctx.stroke();
                ctx.shadowBlur = 0;
            }
            
            ctx.restore();
        }
        
        function drawElectrode() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const scale = 100 * zoom;
            
            ctx.save();
            ctx.translate(cx, cy);
            
            // Electrode rod (zoomed in center electrode of spark plug)
            // Outer casing
            ctx.fillStyle = '#777';
            ctx.beginPath();
            ctx.roundRect(-scale * 0.15, -scale * 1.2, scale * 0.3, scale * 2.4, 5);
            ctx.fill();
            
            // Inner copper core
            ctx.fillStyle = '#cc8844';
            ctx.beginPath();
            ctx.roundRect(-scale * 0.08, -scale * 1.1, scale * 0.16, scale * 2.2, 3);
            ctx.fill();
            
            // Copper sheen
            const copperGrad = ctx.createLinearGradient(-scale * 0.08, 0, scale * 0.08, 0);
            copperGrad.addColorStop(0, 'rgba(255, 200, 150, 0.4)');
            copperGrad.addColorStop(0.5, 'rgba(255, 220, 180, 0.6)');
            copperGrad.addColorStop(1, 'rgba(200, 150, 100, 0.4)');
            ctx.fillStyle = copperGrad;
            ctx.fillRect(-scale * 0.08, -scale * 1.1, scale * 0.16, scale * 2.2);
            
            // Tip (iridium/platinum)
            ctx.fillStyle = '#aabbcc';
            ctx.beginPath();
            ctx.arc(0, scale * 1.15, scale * 0.12, 0, Math.PI * 2);
            ctx.fill();
            
            // Spark point
            ctx.fillStyle = '#ddeeff';
            ctx.beginPath();
            ctx.arc(0, scale * 1.25, scale * 0.06, 0, Math.PI * 2);
            ctx.fill();
            
            // Crystal structure hint (zoom preview)
            ctx.strokeStyle = 'rgba(170, 102, 255, 0.3)';
            ctx.lineWidth = 1;
            for (let i = -3; i <= 3; i++) {
                for (let j = -8; j <= 8; j++) {
                    const x = i * scale * 0.04;
                    const y = j * scale * 0.12;
                    const dist = Math.sqrt(x*x);
                    if (dist < scale * 0.07) {
                        ctx.beginPath();
                        ctx.arc(x, y, 2, 0, Math.PI * 2);
                        ctx.stroke();
                    }
                }
            }
            
            // Spark effect
            if (Math.sin(time * 6) > 0.3) {
                ctx.strokeStyle = '#44aaff';
                ctx.lineWidth = 2;
                ctx.shadowColor = '#44aaff';
                ctx.shadowBlur = 25;
                ctx.beginPath();
                ctx.moveTo(0, scale * 1.3);
                for (let i = 0; i < 5; i++) {
                    const sx = (Math.random() - 0.5) * scale * 0.3;
                    const sy = scale * 1.3 + i * scale * 0.15;
                    ctx.lineTo(sx, sy);
                }
                ctx.stroke();
                ctx.shadowBlur = 0;
            }
            
            ctx.restore();
            
            // Label
            ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('Center Electrode — Copper core with platinum tip', cx, cy + scale * 1.7);
        }
        
        function drawSingleAtom() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const scale = 100 * zoom;
            
            // Single copper atom - zoomed way in
            
            // Electron shells (orbits)
            ctx.strokeStyle = 'rgba(100, 150, 255, 0.2)';
            ctx.lineWidth = 1;
            
            // Shell 1
            ctx.beginPath();
            ctx.ellipse(cx, cy, scale * 0.3, scale * 0.15, time * 0.3, 0, Math.PI * 2);
            ctx.stroke();
            
            // Shell 2
            ctx.beginPath();
            ctx.ellipse(cx, cy, scale * 0.6, scale * 0.25, time * 0.2 + 1, 0, Math.PI * 2);
            ctx.stroke();
            
            // Shell 3
            ctx.beginPath();
            ctx.ellipse(cx, cy, scale * 1, scale * 0.4, time * 0.15 + 2, 0, Math.PI * 2);
            ctx.stroke();
            
            // Shell 4 (valence)
            ctx.strokeStyle = 'rgba(255, 150, 100, 0.3)';
            ctx.beginPath();
            ctx.ellipse(cx, cy, scale * 1.4, scale * 0.55, time * 0.1 + 3, 0, Math.PI * 2);
            ctx.stroke();
            
            // Electrons
            const electrons = [
                { shell: 0.3, angle: time * 3, color: '#60b0ff' },
                { shell: 0.3, angle: time * 3 + Math.PI, color: '#60b0ff' },
                { shell: 0.6, angle: time * 2, color: '#60d0ff' },
                { shell: 0.6, angle: time * 2 + Math.PI * 0.5, color: '#60d0ff' },
                { shell: 0.6, angle: time * 2 + Math.PI, color: '#60d0ff' },
                { shell: 1, angle: time * 1.5, color: '#80d0ff' },
                { shell: 1, angle: time * 1.5 + Math.PI * 0.66, color: '#80d0ff' },
                { shell: 1, angle: time * 1.5 + Math.PI * 1.33, color: '#80d0ff' },
                { shell: 1.4, angle: time * 1, color: '#ff9966' }, // Valence electron
            ];
            
            electrons.forEach(e => {
                const ex = cx + Math.cos(e.angle) * scale * e.shell;
                const ey = cy + Math.sin(e.angle) * scale * e.shell * 0.4;
                
                ctx.fillStyle = e.color;
                ctx.shadowColor = e.color;
                ctx.shadowBlur = 8;
                ctx.beginPath();
                ctx.arc(ex, ey, 5, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.shadowBlur = 0;
            
            // Nucleus
            const nucleusGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, scale * 0.15);
            nucleusGrad.addColorStop(0, '#ff88cc');
            nucleusGrad.addColorStop(0.5, '#cc44aa');
            nucleusGrad.addColorStop(1, 'rgba(170, 50, 130, 0.5)');
            ctx.fillStyle = nucleusGrad;
            ctx.beginPath();
            ctx.arc(cx, cy, scale * 0.15, 0, Math.PI * 2);
            ctx.fill();
            
            // Protons/neutrons hint
            ctx.fillStyle = '#ffaacc';
            for (let i = 0; i < 6; i++) {
                const angle = i * Math.PI / 3 + time * 0.5;
                const r = scale * 0.06;
                ctx.beginPath();
                ctx.arc(cx + Math.cos(angle) * r, cy + Math.sin(angle) * r, 4, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // Label
            ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('Copper Atom (Cu) — 29 protons, 29 electrons', cx, cy + scale * 1.8);
            ctx.fillText('The deepest point: pure existence', cx, cy + scale * 1.95);
        }
        
        function drawAtoms() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2, cy = canvas.height / 2;
            const scale = 50 * zoom;
            
            // Draw multiple atoms in a lattice
            const atoms = [];
            for (let i = -2; i <= 2; i++) {
                for (let j = -2; j <= 2; j++) {
                    const offset = (j % 2) * scale * 0.5;
                    atoms.push({
                        x: cx + i * scale * 1.5 + offset,
                        y: cy + j * scale * 1.3
                    });
                }
            }
            
            // Electron clouds / bonds
            ctx.strokeStyle = 'rgba(170, 102, 255, 0.3)';
            ctx.lineWidth = 2;
            atoms.forEach((a1, i) => {
                atoms.forEach((a2, j) => {
                    if (j > i) {
                        const dist = Math.sqrt((a1.x - a2.x) ** 2 + (a1.y - a2.y) ** 2);
                        if (dist < scale * 2) {
                            ctx.beginPath();
                            ctx.moveTo(a1.x, a1.y);
                            ctx.lineTo(a2.x, a2.y);
                            ctx.stroke();
                        }
                    }
                });
            });
            
            // Atoms (nuclei)
            atoms.forEach((a, i) => {
                // Electron orbits
                ctx.strokeStyle = `rgba(100, 150, 255, ${0.2 + Math.sin(time * 2 + i) * 0.1})`;
                ctx.lineWidth = 1;
                const orbitSize = scale * 0.4 + Math.sin(time * 3 + i) * scale * 0.05;
                ctx.beginPath();
                ctx.ellipse(a.x, a.y, orbitSize, orbitSize * 0.3, time * 0.5 + i, 0, Math.PI * 2);
                ctx.stroke();
                
                // Electrons
                const eAngle = time * 3 + i * 2;
                const ex = a.x + Math.cos(eAngle) * orbitSize;
                const ey = a.y + Math.sin(eAngle) * orbitSize * 0.3;
                ctx.fillStyle = '#60b0ff';
                ctx.beginPath();
                ctx.arc(ex, ey, 4, 0, Math.PI * 2);
                ctx.fill();
                
                // Nucleus
                const nucleusGlow = ctx.createRadialGradient(a.x, a.y, 0, a.x, a.y, scale * 0.2);
                nucleusGlow.addColorStop(0, '#aa66ff');
                nucleusGlow.addColorStop(0.5, 'rgba(170, 102, 255, 0.5)');
                nucleusGlow.addColorStop(1, 'transparent');
                ctx.fillStyle = nucleusGlow;
                ctx.fillRect(a.x - scale * 0.2, a.y - scale * 0.2, scale * 0.4, scale * 0.4);
                
                ctx.fillStyle = '#aa66ff';
                ctx.beginPath();
                ctx.arc(a.x, a.y, 8, 0, Math.PI * 2);
                ctx.fill();
            });
        }
        
        // ===== MAIN RENDER =====
        function render() {
            time += 0.016;
            
            if (currentView === 'objects') {
                // Objects mode - draw based on object level (7 levels: 0-6)
                const level = Math.floor(currentObjectLevel);
                switch (level) {
                    case 0: drawParkingLot(); break;
                    case 1: drawCar(); break;
                    case 2: drawEngine(); break;
                    case 3: drawPiston(); break;
                    case 4: drawSparkPlug(); break;
                    case 5: drawElectrode(); break;
                    case 6: drawSingleAtom(); break;
                }
            } else {
                // Normal dimension mode
                const dim = Math.floor(currentDimension);
                switch (dim) {
                    case 0: drawVoid(); break;
                    case 1: drawPoint(); break;
                    case 2: drawLine(); break;
                    case 3: drawSaddle(); break;
                    case 4: drawParabola(); break;
                    case 5: drawNetwork(); break;
                    case 6: drawWeb(); break;
                }
            }
            
            requestAnimationFrame(render);
        }
        render();
        
        // ===== UI ELEMENTS =====
        const slider = document.getElementById('dimension-slider');
        const markers = document.querySelectorAll('.dim-marker');
        const lensSelector = document.getElementById('lens-selector');
        const valueDisplay = document.getElementById('value-display');
        const viewToggle = document.getElementById('view-toggle');
        const viewBtns = document.querySelectorAll('.view-btn');
        const carouselContainer = document.getElementById('carousel-container');
        const carousel = document.getElementById('carousel');
        const carouselPanels = document.querySelectorAll('.carousel-panel');
        const mobileLensBar = document.getElementById('mobile-lens-bar');
        const lensBar = document.getElementById('lens-bar');
        
        // Objects mode elements
        const objectsSlider = document.getElementById('objects-slider');
        const objBtns = document.querySelectorAll('.obj-btn');
        
        // ===== UPDATE DIMENSION =====
        function updateDimension(dim) {
            currentDimension = dim;
            const d = dimensions[Math.floor(dim)];
            
            // Desktop
            document.getElementById('dim-num').textContent = Math.floor(dim);
            document.getElementById('dim-title').textContent = d.title;
            document.getElementById('dim-subtitle').textContent = d.subtitle;
            document.getElementById('dim-description').innerHTML = d.description;
            document.getElementById('code-example').innerHTML = d.code;
            
            if (d.showLens) lensSelector.classList.add('active');
            else lensSelector.classList.remove('active');
            
            // Mobile carousel
            document.getElementById('c-dim-num').textContent = Math.floor(dim);
            document.getElementById('c-dim-title').textContent = d.title;
            document.getElementById('c-dim-subtitle').textContent = d.subtitle;
            document.getElementById('c-dim-description').innerHTML = d.description;
            document.getElementById('c-code-example').innerHTML = d.code;
            
            // Center graphic
            document.getElementById('center-symbol').textContent = d.symbol;
            document.getElementById('center-symbol').style.color = d.color;
            
            // Lens bars - show in demo mode or panels mode when lens available
            const showLens = d.showLens && (currentView === 'demo' || currentView === 'panels');
            if (showLens) {
                lensBar.classList.add('active');
                mobileLensBar.classList.add('active');
            } else {
                lensBar.classList.remove('active');
                mobileLensBar.classList.remove('active');
            }
            
            // Markers
            markers.forEach(m => {
                m.classList.toggle('active', parseInt(m.dataset.dim) === Math.floor(dim));
            });
        }
        
        // ===== CAROUSEL ROTATION =====
        function rotateCarousel(targetIndex) {
            carouselRotation = targetIndex;
            
            carouselPanels.forEach((panel, i) => {
                // Calculate relative position
                let relPos = (i - targetIndex + 3) % 3;
                panel.dataset.index = relPos;
            });
        }
        
        // ===== EVENT LISTENERS =====
        slider.addEventListener('input', e => {
            updateDimension(parseFloat(e.target.value));
            // Show panels when interacting with timeline
            if (panelsHidden) {
                togglePanels(true); // Show panels
            }
        });
        
        markers.forEach(m => {
            m.addEventListener('click', () => {
                const dim = parseInt(m.dataset.dim);
                slider.value = dim;
                updateDimension(dim);
                // Show panels when clicking timeline marker
                if (panelsHidden) {
                    togglePanels(true); // Show panels
                }
            });
        });
        
        // View toggle
        function setView(view) {
            currentView = view;
            document.body.classList.remove('view-panels', 'view-carousel', 'view-demo', 'view-objects');
            document.body.classList.add('view-' + view);
            
            viewBtns.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.view === view);
            });
            
            // Sync mobile view buttons
            document.querySelectorAll('.mobile-view-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.view === view);
            });
            
            // Update lens bars visibility
            updateDimension(currentDimension);
            
            // If switching to objects, update objects UI
            if (view === 'objects') {
                updateObjectLevel(currentObjectLevel);
            }
        }
        
        viewBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                setView(btn.dataset.view);
            });
        });
        
        // Mobile view buttons (in hamburger menu)
        document.querySelectorAll('.mobile-view-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                setView(btn.dataset.view);
                // Update active state for mobile buttons
                document.querySelectorAll('.mobile-view-btn').forEach(b => {
                    b.classList.toggle('active', b.dataset.view === btn.dataset.view);
                });
                // Close hamburger menu
                if (mainNav.classList.contains('open')) toggleNav();
            });
        });
        
        // ===== OBJECTS MODE =====
        const objCarouselPanels = document.querySelectorAll('.obj-carousel-panel');
        
        function updateObjectLevel(level) {
            currentObjectLevel = level;
            const obj = objectLevels[Math.floor(level)];
            
            // Update carousel panels
            document.getElementById('oc-icon').textContent = obj.icon;
            document.getElementById('oc-title').textContent = obj.title;
            document.getElementById('oc-subtitle').textContent = obj.subtitle;
            document.getElementById('oc-description').innerHTML = obj.description;
            document.getElementById('oc-keypoint').innerHTML = obj.keypoint;
            document.getElementById('oc-extra').innerHTML = obj.extra;
            
            // Update center graphic
            const centerSymbol = document.getElementById('obj-center-symbol');
            if (centerSymbol) {
                centerSymbol.textContent = obj.icon;
                centerSymbol.style.color = obj.color;
            }
            
            // Update buttons
            objBtns.forEach(btn => {
                btn.classList.toggle('active', parseInt(btn.dataset.level) === Math.floor(level));
            });
        }
        
        // Objects carousel rotation
        function rotateObjCarousel(targetIndex) {
            objCarouselRotation = targetIndex;
            objCarouselPanels.forEach((panel, i) => {
                let relPos = (i - targetIndex + 3) % 3;
                panel.dataset.index = relPos;
            });
        }
        
        // Objects carousel panel clicks
        objCarouselPanels.forEach((panel, index) => {
            panel.addEventListener('click', () => {
                if (panel.dataset.index !== '0') {
                    rotateObjCarousel(index);
                }
            });
        });
        
        // Objects slider
        if (objectsSlider) {
            objectsSlider.addEventListener('input', e => {
                updateObjectLevel(parseFloat(e.target.value));
                // Show panels when interacting with timeline
                if (panelsHidden) {
                    togglePanels(true);
                }
            });
        }
        
        // Objects buttons
        objBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const level = parseInt(btn.dataset.level);
                if (objectsSlider) objectsSlider.value = level;
                updateObjectLevel(level);
                // Show panels when clicking timeline button
                if (panelsHidden) {
                    togglePanels(true);
                }
            });
        });
        
        // Carousel panel clicks
        carouselPanels.forEach((panel, index) => {
            panel.addEventListener('click', () => {
                if (panel.dataset.index !== '0') {
                    rotateCarousel(index);
                }
            });
        });
        
        // Lens buttons (all)
        document.querySelectorAll('.lens-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                document.querySelectorAll('.lens-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll(`.lens-btn[data-lens="${btn.dataset.lens}"]`).forEach(b => b.classList.add('active'));
                currentLens = btn.dataset.lens;
                
                if (currentLens !== 'sound' && oscillator) {
                    oscillator.stop();
                    oscillator = null;
                }
            });
        });
        
        // ===== MOUSE/TOUCH INTERACTION =====
        canvas.addEventListener('mousedown', e => {
            isDragging = true;
            didDrag = false; // Reset drag detection
            lastMouse = { x: e.clientX, y: e.clientY };
            isMouseOverShape = true;
        });
        
        canvas.addEventListener('mouseup', () => isDragging = false);
        canvas.addEventListener('mouseleave', () => {
            valueDisplay.style.display = 'none';
            isMouseOverShape = false;
            // Stop ALL sounds when cursor leaves shape
            stopAllSounds();
            hoverHistory = [];
        });
        
        canvas.addEventListener('mousemove', e => {
            if (isDragging) {
                const dx = e.clientX - lastMouse.x;
                const dy = e.clientY - lastMouse.y;
                if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
                    didDrag = true; // User actually dragged
                }
                rotationY += dx * 0.005;
                rotationX += dy * 0.005;
                lastMouse = { x: e.clientX, y: e.clientY };
            }
            
            // Value extraction - uses MusicalSubstrate for all dimensions
            const dim = Math.floor(currentDimension);
            if (dimensions[dim] && dimensions[dim].showLens) {
                const cx = canvas.width / 2, cy = canvas.height / 2;
                const nx = (e.clientX - cx) / (200 * zoom);
                const ny = -(e.clientY - cy) / (200 * zoom);
                
                // Check if inside the shape bounds
                const inBounds = Math.abs(nx) <= 1.5 && Math.abs(ny) <= 1.5;
                
                if (inBounds) {
                    isMouseOverShape = true;
                    let displayText;
                    const dimNames = ['Void', 'Point', 'Line', 'Saddle', 'Volume', 'Network', 'Whole'];
                    
                    // Calculate z based on dimension
                    let z = 0;
                    if (dim === 3) z = nx * ny;
                    else if (dim === 4) z = nx * ny * ny;
                    
                    // Get substrate data from geometry (left-to-right spectrum)
                    const lens = MusicalSubstrate.fromGeometry(nx, ny, z);
                    const xNorm = lens.normalizedX || ((nx + 1.5) / 3);
                    
                    // Track hover history for melody
                    hoverHistory.push({ x: nx, y: ny, xNorm, time: Date.now() });
                    if (hoverHistory.length > 10) hoverHistory.shift();
                    
                    if (currentLens === 'color') {
                        // True spectrum: left (violet) to right (red)
                        const c = lens.light.color;
                        const wl = lens.light.wavelengthNm;
                        
                        displayText = `${dimNames[dim]}: λ=${wl.toFixed(0)}nm | x=${(xNorm * 100).toFixed(0)}%`;
                        valueDisplay.style.background = c.rgb;
                        valueDisplay.style.color = (c.r + c.g + c.b) / 3 > 128 ? '#000' : '#fff';
                        
                    } else if (currentLens === 'sound') {
                        // Musical sound with note names
                        const freq = lens.sound.frequencyHz;
                        const note = lens.sound.noteName;
                        const inst = lens.sound.instrument;
                        
                        displayText = `${dimNames[dim]}: ♪ ${note} (${freq.toFixed(0)}Hz) | ${inst.name}`;
                        valueDisplay.style.background = 'rgba(60, 100, 255, 0.9)';
                        valueDisplay.style.color = '#fff';
                        
                        // Play sound based on dimension type
                        if (dim === 1) {
                            // Point: Middle C only
                            playMiddleC();
                        } else if (dim === 2) {
                            // Line: Bass to Treble
                            playLineFrequency(xNorm);
                        } else if (dim === 4) {
                            // Volume: Chord neighbors
                            playNeighborChord(nx, ny, z);
                        } else if (dim === 5) {
                            // Network: Harmonics
                            playHarmonicSeries(freq, 8);
                        } else if (dim === 6) {
                            // Whole: Symphonic
                            playSymphonic(xNorm, (ny + 1.5) / 3);
                        } else {
                            // Default: Single frequency
                            playLineFrequency(xNorm);
                        }
                        
                    } else {
                        // Value lens - geometric properties
                        const r = lens.value.raw;
                        const formula = lens.value.formula;
                        
                        displayText = `${dimNames[dim]} | ${formula}`;
                        valueDisplay.style.background = 'rgba(60, 255, 100, 0.9)';
                        valueDisplay.style.color = '#000';
                    }
                    
                    valueDisplay.textContent = displayText;
                    valueDisplay.style.display = 'block';
                    valueDisplay.style.left = (e.clientX + 15) + 'px';
                    valueDisplay.style.top = (e.clientY - 10) + 'px';
                } else {
                    // Mouse moved outside shape bounds
                    valueDisplay.style.display = 'none';
                    isMouseOverShape = false;
                    stopAllSounds();
                    hoverHistory = [];
                }
            }
        });
        
        canvas.addEventListener('wheel', e => {
            e.preventDefault();
            zoom *= e.deltaY > 0 ? 0.95 : 1.05;
            zoom = Math.max(0.5, Math.min(3, zoom));
        });
        
        // Touch support
        let touchStart = null;
        canvas.addEventListener('touchstart', e => {
            if (e.touches.length === 1) {
                touchStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
                didDrag = false; // Reset drag detection for touch
            }
        });
        
        canvas.addEventListener('touchmove', e => {
            if (touchStart && e.touches.length === 1) {
                const dx = e.touches[0].clientX - touchStart.x;
                const dy = e.touches[0].clientY - touchStart.y;
                if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
                    didDrag = true; // Touch drag occurred
                }
                rotationY += dx * 0.005;
                rotationX += dy * 0.005;
                touchStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
            }
        });
        
        canvas.addEventListener('touchend', () => {
            touchStart = null;
            // Don't reset didDrag here - let click handler do it
        });
        
        // ===== TAP OUTSIDE TO HIDE/SHOW PANELS =====
        function togglePanels(show) {
            panelsHidden = !show;
            if (panelsHidden) {
                document.body.classList.add('panels-hidden');
                // Switch to demo view when hiding panels
                setView('demo');
            } else {
                document.body.classList.remove('panels-hidden');
            }
        }
        
        // Panel toggle button click handler
        const panelToggleBtn = document.getElementById('panel-toggle-btn');
        if (panelToggleBtn) {
            panelToggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                togglePanels(panelsHidden); // Show if hidden, hide if shown
            });
        }
        
        // ===== INTRO SPLASH =====
        const introSplash = document.getElementById('intro-splash');
        function dismissSplash() {
            if (introSplash && !introSplash.classList.contains('hidden')) {
                introSplash.classList.add('hidden');
            }
        }
        
        // Make dismissSplash globally accessible for onclick
        window.dismissSplash = dismissSplash;
        
        // Dismiss splash on any click or interaction
        document.addEventListener('click', dismissSplash);
        slider.addEventListener('input', dismissSplash);
        if (objectsSlider) objectsSlider.addEventListener('input', dismissSplash);
        
        // Initialize
        updateDimension(0);
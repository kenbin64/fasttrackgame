/**
 * ============================================================
 * BUTTERFLYFX DIMENSIONAL PROGRAMMING STANDARD
 * ============================================================
 * 
 * PARADIGM: Objects are dimensions containing points. Each point
 * is an object in a lower dimension containing its own points.
 * All properties, attributes, and behaviors exist as infinite
 * potentials — invoke only when needed. No pre-calculation,
 * no storage. Geometry IS information.
 * 
 * ============================================================
 * FASTTRACK GAME SOUND EFFECTS (SFX)
 * Theme-Aware Procedural Sound Generation
 * ============================================================
 * 
 * Sound events:
 * - step: Peg moving through holes (traversal)
 * - arrive: Peg reaching destination
 * - fasttrack: Entering FastTrack lane
 * - bullseye: Entering center bullseye
 * - safezone: Entering safe/home zone
 * - boot: Cutting opponent's peg (send home)
 * - victory: Winning the game
 * - drawCard: Drawing a card
 * - extraTurn: Getting an extra turn (6 card)
 * 
 * All sounds procedurally generated - 100% original!
 */

'use strict';

const GameSFX = {
    version: '1.0.0',
    name: 'FastTrack Sound Effects',
    
    // Audio context (shared with MusicSubstrate)
    audioContext: null,
    masterGain: null,
    
    // Volume settings
    volume: 0.5,
    enabled: true,
    
    // Current theme affects sound character
    currentTheme: 'DEFAULT',
    
    // ============================================================
    // THEME SOUND PROFILES
    // Each theme has different sound characteristics
    // ============================================================
    themeProfiles: {
        DEFAULT: {
            stepWave: 'triangle',
            stepBaseFreq: 440,
            arriveChord: [523.25, 659.25, 783.99],  // C major chord
            fasttrackSweep: { start: 300, end: 1200 },
            bullseyeTone: 880,
            safezoneTone: 392,
            bootWave: 'sawtooth',
            victoryScale: [523.25, 587.33, 659.25, 698.46, 783.99, 880, 987.77, 1046.5]
        },
        SPACE_ACE: {
            stepWave: 'sine',
            stepBaseFreq: 330,
            arriveChord: [329.63, 440, 523.25],  // E minor-ish
            fasttrackSweep: { start: 200, end: 1500 },
            bullseyeTone: 660,
            safezoneTone: 293.66,
            bootWave: 'square',
            victoryScale: [329.63, 369.99, 440, 493.88, 587.33, 659.25, 739.99, 659.25]
        },
        UNDERSEA: {
            stepWave: 'sine',
            stepBaseFreq: 220,
            arriveChord: [261.63, 329.63, 392],  // C major underwater
            fasttrackSweep: { start: 150, end: 800 },
            bullseyeTone: 440,
            safezoneTone: 246.94,
            bootWave: 'triangle',
            victoryScale: [261.63, 293.66, 329.63, 349.23, 392, 440, 493.88, 523.25]
        },
        ROMAN_COLISEUM: {
            stepWave: 'square',
            stepBaseFreq: 392,
            arriveChord: [392, 493.88, 587.33],  // G major fanfare
            fasttrackSweep: { start: 250, end: 1000 },
            bullseyeTone: 783.99,
            safezoneTone: 349.23,
            bootWave: 'sawtooth',
            victoryScale: [392, 440, 493.88, 523.25, 587.33, 659.25, 739.99, 783.99]
        },
        // Fibonacci theme: frequencies based on golden ratio and Fibonacci sequence
        // Scale uses Fibonacci semitone intervals from A4 (440Hz)
        FIBONACCI: {
            stepWave: 'sine',
            stepBaseFreq: 440,  // A4 - base of Fibonacci scale
            // Chord built from Fibonacci intervals: root, +3 semitones, +8 semitones
            arriveChord: [440, 523.25, 698.46],
            // Sweep uses golden ratio relationship
            fasttrackSweep: { start: 272, end: 1127 },  // 440/φ to 440*2.56 (φ squared)
            bullseyeTone: 712,  // 440 * φ ≈ 712 Hz
            safezoneTone: 272,  // 440 / φ ≈ 272 Hz
            bootWave: 'triangle',
            // Victory scale uses Fibonacci semitone intervals from 440Hz
            victoryScale: [
                440,                                    // Root (0)
                440 * Math.pow(2, 1/12),               // +1 semitone
                440 * Math.pow(2, 2/12),               // +2 semitones
                440 * Math.pow(2, 3/12),               // +3 semitones
                440 * Math.pow(2, 5/12),               // +5 semitones
                440 * Math.pow(2, 8/12),               // +8 semitones
                440 * Math.pow(2, 13/12),              // +13 semitones
                440 * Math.pow(2, 21/12)               // +21 semitones
            ]
        }
    },
    
    // ============================================================
    // INITIALIZATION
    // ============================================================
    
    init() {
        console.log('🔊 [GameSFX] Initialized - awaiting user interaction');
    },
    
    /**
     * Activate audio context (called from user interaction)
     */
    activate() {
        // Share context with MusicSubstrate if available
        if (!this.audioContext && typeof MusicSubstrate !== 'undefined' && MusicSubstrate.audioContext) {
            this.audioContext = MusicSubstrate.audioContext;
            this.masterGain = this.audioContext.createGain();
            this.masterGain.gain.value = this.volume;
            this.masterGain.connect(this.audioContext.destination);
            console.log('🔊 [GameSFX] Using shared audio context from MusicSubstrate');
            return true;
        }
        
        if (this.audioContext) {
            if (this.audioContext.state === 'suspended') {
                this.audioContext.resume();
            }
            return true;
        }
        
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            if (this.audioContext.state === 'suspended') {
                this.audioContext.resume();
            }
            this.masterGain = this.audioContext.createGain();
            this.masterGain.gain.value = this.volume;
            this.masterGain.connect(this.audioContext.destination);
            console.log('🔊 [GameSFX] Audio context activated');
            return true;
        } catch (e) {
            console.error('Could not create audio context:', e);
            return false;
        }
    },
    
    /**
     * Set current theme (affects sound character)
     */
    setTheme(themeName) {
        this.currentTheme = themeName || 'DEFAULT';
        console.log(`🔊 [GameSFX] Theme set to: ${this.currentTheme}`);
    },
    
    /**
     * Get current theme profile
     */
    getProfile() {
        return this.themeProfiles[this.currentTheme] || this.themeProfiles.DEFAULT;
    },
    
    /**
     * Set volume (0-1)
     */
    setVolume(vol) {
        this.volume = Math.max(0, Math.min(1, vol));
        if (this.masterGain) {
            this.masterGain.gain.value = this.volume;
        }
    },
    
    /**
     * Enable/disable SFX
     */
    toggle() {
        this.enabled = !this.enabled;
        console.log(`🔊 [GameSFX] ${this.enabled ? 'Enabled' : 'Disabled'}`);
        return this.enabled;
    },
    
    // ============================================================
    // SOUND EFFECTS
    // ============================================================
    
    /**
     * STEP SOUND - Peg moving through each hole during traversal
     * Uses position to vary pitch (dimensional coordinate → frequency)
     * @param {number} stepIndex - Current step in the path (0-N)
     * @param {number} totalSteps - Total steps in move
     */
    playStep(stepIndex = 0, totalSteps = 1) {
        if (!this.enabled || !this.activate()) return;
        
        const profile = this.getProfile();
        const now = this.audioContext.currentTime;
        
        // Pitch rises slightly with each step (progress through move)
        const progress = totalSteps > 1 ? stepIndex / (totalSteps - 1) : 0;
        const freq = profile.stepBaseFreq * (1 + progress * 0.3);
        
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();
        
        osc.type = profile.stepWave;
        osc.frequency.value = freq;
        
        // Quick click/tap envelope
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(this.volume * 0.15, now + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + 0.1);
    },
    
    /**
     * ARRIVE SOUND - Peg reaching final destination
     * Satisfying chord resolution
     */
    playArrive() {
        if (!this.enabled || !this.activate()) return;
        
        const profile = this.getProfile();
        const now = this.audioContext.currentTime;
        
        // Play a nice resolving chord
        profile.arriveChord.forEach((freq, i) => {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            osc.type = 'triangle';
            osc.frequency.value = freq;
            
            // Staggered attack for richness
            const attackDelay = i * 0.02;
            gain.gain.setValueAtTime(0, now + attackDelay);
            gain.gain.linearRampToValueAtTime(this.volume * 0.2, now + attackDelay + 0.03);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
            
            osc.connect(gain);
            gain.connect(this.masterGain);
            
            osc.start(now + attackDelay);
            osc.stop(now + 0.5);
        });
        
        console.log('🔊 [GameSFX] Arrive!');
    },
    
    /**
     * FASTTRACK ENTRY - Exciting rising sweep
     * Player entering the FastTrack lane!
     */
    playFasttrack() {
        if (!this.enabled || !this.activate()) return;
        
        const profile = this.getProfile();
        const now = this.audioContext.currentTime;
        const duration = 0.5;
        
        // Rising sweep oscillator
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();
        
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(profile.fasttrackSweep.start, now);
        osc.frequency.exponentialRampToValueAtTime(profile.fasttrackSweep.end, now + duration * 0.8);
        
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(this.volume * 0.3, now + 0.05);
        gain.gain.setValueAtTime(this.volume * 0.3, now + duration * 0.6);
        gain.gain.exponentialRampToValueAtTime(0.001, now + duration);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + duration + 0.1);
        
        // Add sparkle layer
        this._playSparkle(now + 0.1, 3);
        
        console.log('🚀 [GameSFX] FastTrack entry!');
    },
    
    /**
     * BULLSEYE ENTRY - Target hit sound with fanfare
     * Center bullseye reached!
     */
    playBullseye() {
        if (!this.enabled || !this.activate()) return;
        
        const profile = this.getProfile();
        const now = this.audioContext.currentTime;
        
        // Main bullseye tone
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();
        
        osc.type = 'sine';
        osc.frequency.value = profile.bullseyeTone;
        
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(this.volume * 0.4, now + 0.02);
        gain.gain.setValueAtTime(this.volume * 0.4, now + 0.15);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + 0.7);
        
        // Impact thump
        this._playImpact(now, 0.3);
        
        // Celebration sparkles
        this._playSparkle(now + 0.05, 5);
        
        console.log('🎯 [GameSFX] Bullseye!');
    },
    
    /**
     * SAFE ZONE ENTRY - Warm, secure arrival sound
     * Peg entering home/safe zone
     */
    playSafezone() {
        if (!this.enabled || !this.activate()) return;
        
        const profile = this.getProfile();
        const now = this.audioContext.currentTime;
        
        // Warm pad sound
        const osc1 = this.audioContext.createOscillator();
        const osc2 = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();
        
        osc1.type = 'triangle';
        osc2.type = 'sine';
        osc1.frequency.value = profile.safezoneTone;
        osc2.frequency.value = profile.safezoneTone * 1.5;  // Perfect fifth
        
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(this.volume * 0.25, now + 0.05);
        gain.gain.setValueAtTime(this.volume * 0.25, now + 0.2);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
        
        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(this.masterGain);
        
        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.6);
        osc2.stop(now + 0.6);
        
        console.log('🏠 [GameSFX] Safe zone!');
    },
    
    /**
     * BOOT/CUT - Opponent peg sent home!
     * Aggressive, dramatic sound
     */
    playBoot() {
        if (!this.enabled || !this.activate()) return;
        
        const profile = this.getProfile();
        const now = this.audioContext.currentTime;
        
        // Dramatic descending sweep
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();
        
        osc.type = profile.bootWave;
        osc.frequency.setValueAtTime(600, now);
        osc.frequency.exponentialRampToValueAtTime(100, now + 0.3);
        
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(this.volume * 0.4, now + 0.01);
        gain.gain.linearRampToValueAtTime(this.volume * 0.35, now + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + 0.4);
        
        // Add impact
        this._playImpact(now, 0.5);
        
        // Second hit for emphasis
        setTimeout(() => this._playImpact(this.audioContext.currentTime, 0.3), 120);
        
        console.log('💥 [GameSFX] Boot!');
    },
    
    /**
     * VICTORY - Winner celebration fanfare!
     * Full triumphant scale with sparkles
     */
    playVictory() {
        if (!this.enabled || !this.activate()) return;
        
        const profile = this.getProfile();
        const now = this.audioContext.currentTime;
        
        // Ascending victory scale
        profile.victoryScale.forEach((freq, i) => {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            osc.type = i < 4 ? 'triangle' : 'square';
            osc.frequency.value = freq;
            
            const noteStart = now + i * 0.12;
            const noteDuration = 0.4;
            
            gain.gain.setValueAtTime(0, noteStart);
            gain.gain.linearRampToValueAtTime(this.volume * 0.3, noteStart + 0.02);
            gain.gain.setValueAtTime(this.volume * 0.3, noteStart + noteDuration * 0.5);
            gain.gain.exponentialRampToValueAtTime(0.001, noteStart + noteDuration);
            
            osc.connect(gain);
            gain.connect(this.masterGain);
            
            osc.start(noteStart);
            osc.stop(noteStart + noteDuration + 0.05);
        });
        
        // Final chord resolution
        setTimeout(() => {
            const finalNow = this.audioContext.currentTime;
            [523.25, 659.25, 783.99, 1046.5].forEach((freq, i) => {
                const osc = this.audioContext.createOscillator();
                const gain = this.audioContext.createGain();
                
                osc.type = 'triangle';
                osc.frequency.value = freq;
                
                gain.gain.setValueAtTime(0, finalNow);
                gain.gain.linearRampToValueAtTime(this.volume * 0.35, finalNow + 0.03);
                gain.gain.setValueAtTime(this.volume * 0.35, finalNow + 0.8);
                gain.gain.exponentialRampToValueAtTime(0.001, finalNow + 1.5);
                
                osc.connect(gain);
                gain.connect(this.masterGain);
                
                osc.start(finalNow);
                osc.stop(finalNow + 1.6);
            });
            
            // Celebration sparkles
            this._playSparkle(finalNow, 10);
        }, profile.victoryScale.length * 120 + 100);
        
        console.log('🏆 [GameSFX] Victory!');
    },
    
    /**
     * DRAW CARD - Card flip/draw sound
     */
    playDrawCard() {
        if (!this.enabled || !this.activate()) return;
        
        const now = this.audioContext.currentTime;
        
        // Quick snap sound
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();
        
        osc.type = 'square';
        osc.frequency.setValueAtTime(200, now);
        osc.frequency.exponentialRampToValueAtTime(400, now + 0.03);
        
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(this.volume * 0.15, now + 0.005);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + 0.1);
        
        // Soft reveal tone
        setTimeout(() => {
            const revealNow = this.audioContext.currentTime;
            const osc2 = this.audioContext.createOscillator();
            const gain2 = this.audioContext.createGain();
            
            osc2.type = 'sine';
            osc2.frequency.value = 523.25;
            
            gain2.gain.setValueAtTime(0, revealNow);
            gain2.gain.linearRampToValueAtTime(this.volume * 0.1, revealNow + 0.02);
            gain2.gain.exponentialRampToValueAtTime(0.001, revealNow + 0.15);
            
            osc2.connect(gain2);
            gain2.connect(this.masterGain);
            
            osc2.start(revealNow);
            osc2.stop(revealNow + 0.2);
        }, 80);
    },
    
    /**
     * EXTRA TURN - 6 card special sound!
     */
    playExtraTurn() {
        if (!this.enabled || !this.activate()) return;
        
        const now = this.audioContext.currentTime;
        
        // Exciting rising arpeggio
        const notes = [261.63, 329.63, 392, 523.25, 659.25];
        notes.forEach((freq, i) => {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            osc.type = 'triangle';
            osc.frequency.value = freq;
            
            const noteStart = now + i * 0.06;
            
            gain.gain.setValueAtTime(0, noteStart);
            gain.gain.linearRampToValueAtTime(this.volume * 0.2, noteStart + 0.01);
            gain.gain.exponentialRampToValueAtTime(0.001, noteStart + 0.2);
            
            osc.connect(gain);
            gain.connect(this.masterGain);
            
            osc.start(noteStart);
            osc.stop(noteStart + 0.25);
        });
        
        console.log('🎲 [GameSFX] Extra turn!');
    },
    
    /**
     * ROYAL EXIT - King/Queen/Jack exiting bullseye
     */
    playRoyalExit() {
        if (!this.enabled || !this.activate()) return;
        
        const now = this.audioContext.currentTime;
        
        // Regal fanfare
        const fanfare = [392, 523.25, 659.25, 783.99];
        fanfare.forEach((freq, i) => {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            osc.type = 'square';
            osc.frequency.value = freq;
            
            const noteStart = now + i * 0.1;
            
            gain.gain.setValueAtTime(0, noteStart);
            gain.gain.linearRampToValueAtTime(this.volume * 0.25, noteStart + 0.02);
            gain.gain.setValueAtTime(this.volume * 0.25, noteStart + 0.12);
            gain.gain.exponentialRampToValueAtTime(0.001, noteStart + 0.35);
            
            osc.connect(gain);
            gain.connect(this.masterGain);
            
            osc.start(noteStart);
            osc.stop(noteStart + 0.4);
        });
        
        console.log('👑 [GameSFX] Royal exit!');
    },
    
    /**
     * PEG ENTRY - New peg entering the board (A, 6, Joker)
     */
    playPegEntry() {
        if (!this.enabled || !this.activate()) return;
        
        const now = this.audioContext.currentTime;
        
        // "Pop" onto board
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(150, now);
        osc.frequency.exponentialRampToValueAtTime(500, now + 0.05);
        osc.frequency.exponentialRampToValueAtTime(350, now + 0.15);
        
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(this.volume * 0.3, now + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + 0.3);
        
        console.log('➕ [GameSFX] Peg entry!');
    },
    
    // ============================================================
    // HELPER SOUNDS
    // ============================================================
    
    /**
     * Sparkle/shimmer effect (celebration, achievement)
     */
    _playSparkle(startTime, count = 3) {
        const now = startTime || this.audioContext.currentTime;
        
        for (let i = 0; i < count; i++) {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            osc.type = 'sine';
            const freq = 1200 + Math.random() * 2000;
            osc.frequency.value = freq;
            
            const sparkleStart = now + i * 0.05 + Math.random() * 0.1;
            
            gain.gain.setValueAtTime(0, sparkleStart);
            gain.gain.linearRampToValueAtTime(this.volume * 0.1, sparkleStart + 0.005);
            gain.gain.exponentialRampToValueAtTime(0.001, sparkleStart + 0.1);
            
            osc.connect(gain);
            gain.connect(this.masterGain);
            
            osc.start(sparkleStart);
            osc.stop(sparkleStart + 0.15);
        }
    },
    
    /**
     * Impact/thump effect (collision, boot)
     */
    _playImpact(startTime, intensity = 0.5) {
        const now = startTime || this.audioContext.currentTime;
        
        // Low frequency thump
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(100, now);
        osc.frequency.exponentialRampToValueAtTime(40, now + 0.1);
        
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(this.volume * intensity, now + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + 0.2);
    },
    
    // ============================================================
    // CONVENIENCE METHODS - Play by event name
    // ============================================================
    
    /**
     * Play sound effect by event name
     * @param {string} eventName - step, arrive, fasttrack, bullseye, safezone, boot, victory, etc.
     * @param {object} options - Event-specific options (e.g., stepIndex, totalSteps)
     */
    play(eventName, options = {}) {
        switch (eventName) {
            case 'step':
                this.playStep(options.stepIndex || 0, options.totalSteps || 1);
                break;
            case 'arrive':
                this.playArrive();
                break;
            case 'fasttrack':
                this.playFasttrack();
                break;
            case 'bullseye':
                this.playBullseye();
                break;
            case 'safezone':
                this.playSafezone();
                break;
            case 'boot':
            case 'cut':
                this.playBoot();
                break;
            case 'victory':
            case 'win':
                this.playVictory();
                break;
            case 'draw':
            case 'drawCard':
                this.playDrawCard();
                break;
            case 'extraTurn':
            case 'extra':
                this.playExtraTurn();
                break;
            case 'royal':
            case 'royalExit':
                this.playRoyalExit();
                break;
            case 'entry':
            case 'pegEntry':
                this.playPegEntry();
                break;
            default:
                console.warn(`[GameSFX] Unknown event: ${eventName}`);
        }
    }
};

// Initialize on load
GameSFX.init();

// Expose globally
window.GameSFX = GameSFX;

console.log('🔊 [GameSFX] Module loaded');
console.log('   Sound Events: step, arrive, fasttrack, bullseye, safezone, boot, victory, drawCard, extraTurn, pegEntry, royalExit');

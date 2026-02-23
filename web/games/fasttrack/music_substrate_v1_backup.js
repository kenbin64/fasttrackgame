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
 * FASTTRACK MUSIC SUBSTRATE
 * Procedural Theme-Based Music Generation
 * ============================================================
 * 
 * Generates original, royalty-free music using Web Audio API
 * Themes: Space Ace, Undersea, Roman Coliseum, Default
 * 
 * All music is procedurally generated - 100% original!
 */

'use strict';

const MusicSubstrate = {
    version: '1.0.0',
    name: 'FastTrack Music Engine',
    
    // Audio context
    audioContext: null,
    masterGain: null,
    
    // State
    isPlaying: false,
    currentTheme: 'DEFAULT',
    volume: 0.4,
    resolutionTimeout: null,  // Track pending resolution timeout
    
    // Oscillators and nodes
    oscillators: [],
    intervals: [],
    
    // ============================================================
    // MUSICAL SCALES (frequencies in Hz)
    // ============================================================
    scales: {
        C_MAJOR: [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25],
        D_MINOR: [293.66, 329.63, 349.23, 392.00, 440.00, 466.16, 523.25, 587.33],
        G_MAJOR: [392.00, 440.00, 493.88, 523.25, 587.33, 659.25, 739.99, 783.99],
        A_MINOR: [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00],
        // Fibonacci scale: A4 (440Hz) + Fibonacci semitone intervals (1,1,2,3,5,8,13,21)
        // Each frequency = 440 * 2^(n/12) where n is Fibonacci number
        FIBONACCI: [
            440.00,                          // Root (A4)
            440 * Math.pow(2, 1/12),         // +1 semitone  = 466.16 Hz
            440 * Math.pow(2, 2/12),         // +2 semitones = 493.88 Hz
            440 * Math.pow(2, 3/12),         // +3 semitones = 523.25 Hz
            440 * Math.pow(2, 5/12),         // +5 semitones = 587.33 Hz
            440 * Math.pow(2, 8/12),         // +8 semitones = 698.46 Hz
            440 * Math.pow(2, 13/12),        // +13 semitones = 932.33 Hz
            440 * Math.pow(2, 21/12)         // +21 semitones = 1479.98 Hz
        ]
    },
    
    // Golden ratio constant for timing relationships
    PHI: 1.618033988749895,
    
    // ============================================================
    // THEME CONFIGURATIONS
    // ============================================================
    themes: {
        DEFAULT: {
            name: 'Classic Arena',
            scale: 'C_MAJOR',
            bpm: 120,
            instruments: ['square', 'sawtooth', 'triangle'],
            bassOctave: -2,
            melodyPattern: [0, 2, 4, 5, 4, 2, 0, 3, 5, 7, 5, 3],
            bassPattern: [0, 0, 4, 4, 5, 5, 4, 4],
            arpPattern: [0, 2, 4, 7, 4, 2],
            drumEnabled: true,
            style: 'upbeat',
            // Resolution: V-I cadence (G → C in C Major)
            phraseLength: 8, // bars per phrase
            resolutionMelody: [7, 5, 4, 2, 0], // Walk down to resolve
            resolutionBass: [4, 0], // V → I
            resolutionDuration: 2 // beats for final note
        },
        SPACE_ACE: {
            name: 'Cosmic Odyssey',
            scale: 'D_MINOR',
            bpm: 100,
            instruments: ['sine', 'triangle', 'sawtooth'],
            bassOctave: -2,
            melodyPattern: [0, 3, 5, 7, 5, 3, 0, 2, 4, 6, 4, 2],
            bassPattern: [0, 0, 0, 0, 4, 4, 5, 5],
            arpPattern: [0, 4, 7, 11, 7, 4],
            drumEnabled: true,
            style: 'ethereal',
            // Resolution: iv-V-i cadence (G-A-Dm)
            phraseLength: 8,
            resolutionMelody: [5, 4, 3, 2, 0], // Haunting descent
            resolutionBass: [3, 4, 0], // iv-V-i
            resolutionDuration: 3,
            effects: {
                reverb: 0.6,
                delay: 0.4,
                lfo: { rate: 0.5, depth: 20 }
            }
        },
        UNDERSEA: {
            name: 'Island Calypso',
            scale: 'G_MAJOR',
            bpm: 95,
            instruments: ['triangle', 'sine', 'square'],
            bassOctave: -2,
            melodyPattern: [0, 2, 4, 2, 0, 4, 5, 4, 2, 0, 2, 4],
            bassPattern: [0, 4, 3, 4, 0, 4, 5, 4],
            arpPattern: [0, 2, 4, 5, 4, 2],
            drumEnabled: true,
            style: 'tropical',
            // Resolution: IV-V-I cadence for bright tropical feel
            phraseLength: 8,
            resolutionMelody: [4, 5, 7, 5, 4, 2, 0], // Playful resolution
            resolutionBass: [3, 4, 0], // IV-V-I
            resolutionDuration: 2,
            effects: {
                reverb: 0.3,
                chorus: 0.5
            }
        },
        ROMAN_COLISEUM: {
            name: 'Roman Fanfare',
            scale: 'A_MINOR',
            bpm: 80,
            instruments: ['sawtooth', 'triangle', 'square'],
            bassOctave: -2,
            melodyPattern: [0, 0, 4, 4, 3, 3, 4, 5, 4, 3, 0, 0],
            bassPattern: [0, 0, 0, 0, 3, 3, 4, 4],
            arpPattern: [0, 3, 4, 7, 4, 3],
            drumEnabled: true,
            style: 'epic',
            // Resolution: V-i with dramatic pause
            phraseLength: 8,
            resolutionMelody: [4, 4, 3, 2, 0, 0], // Epic descent
            resolutionBass: [4, 0], // V-i
            resolutionDuration: 4, // Long dramatic hold
            effects: {
                reverb: 0.7
            }
        },
        
        // ============================================================
        // FIBONACCI SPIRAL - Based on the golden ratio and Fibonacci sequence
        // All timing relationships use φ (1.618...)
        // All intervals derived from: 1, 1, 2, 3, 5, 8, 13, 21
        // ============================================================
        FIBONACCI: {
            name: 'Golden Spiral',
            scale: 'FIBONACCI',
            bpm: 89,  // 89 is a Fibonacci number!
            instruments: ['sine', 'triangle', 'sine'],
            bassOctave: -2,
            // Melody walks the Fibonacci sequence as scale degrees
            melodyPattern: [0, 1, 1, 2, 3, 5, 3, 2, 1, 1, 0, 2, 3, 5, 3, 2],
            // Bass uses root (0) and the golden positions (3, 5)
            bassPattern: [0, 0, 3, 0, 5, 0, 3, 0],
            // Arpeggio spirals through Fibonacci intervals
            arpPattern: [0, 1, 2, 3, 5, 3, 2, 1],
            drumEnabled: true,
            style: 'mathematical',
            // Resolution: Golden spiral back to root
            phraseLength: 8,
            resolutionMelody: [5, 3, 2, 1, 1, 0], // Fibonacci descent to root
            resolutionBass: [3, 0], // Tension to root
            resolutionDuration: 2.618, // φ + 1 beats
            // Chords built from Fibonacci intervals
            chordMode: true,
            chords: [
                [0, 2, 4],      // i chord: root, +2, +5 semitones
                [0, 3, 5],      // ii chord: root, +3, +8 semitones  
                [0, 2, 5],      // III chord: root, +2, +8 semitones
                [0, 3, 6],      // iv chord: root, +3, +13 semitones
                [0, 4, 6],      // V chord: root, +5, +13 semitones
                [0, 2, 4, 6],   // Full spiral: root through +13
                [0, 3, 5, 7],   // Golden stack: all the way to +21
                [0, 1, 3, 5]    // Fibonacci cluster
            ],
            // Chord progression follows Fibonacci pattern
            chordProgression: [0, 1, 1, 2, 3, 5 % 8, 3, 2],
            effects: {
                reverb: 0.5,
                // Delay time based on golden ratio subdivision
                delay: 0.382,  // 1/φ ≈ 0.618, 1/φ² ≈ 0.382
                lfo: { rate: 0.618, depth: 15 }  // LFO at golden ratio Hz
            }
        }
    },
    
    // ============================================================
    // INITIALIZATION
    // ============================================================
    
    init() {
        console.log('🎵 [MusicSubstrate] Initialized - awaiting user interaction');
    },
    
    /**
     * Activate audio context (must be called from user interaction)
     */
    activate() {
        if (this.audioContext) {
            // Context exists but might be suspended - resume it
            if (this.audioContext.state === 'suspended') {
                this.audioContext.resume().then(() => {
                    console.log('🔊 [MusicSubstrate] Audio context resumed!');
                }).catch(e => {
                    console.warn('Could not resume audio context:', e);
                });
            }
            return true;
        }
        
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Resume immediately if suspended (required for user gesture)
            if (this.audioContext.state === 'suspended') {
                this.audioContext.resume();
            }
            
            // Create master gain
            this.masterGain = this.audioContext.createGain();
            this.masterGain.gain.value = this.volume;
            this.masterGain.connect(this.audioContext.destination);
            
            console.log('🔊 [MusicSubstrate] Audio context activated!');
            return true;
        } catch (e) {
            console.error('Could not create audio context:', e);
            return false;
        }
    },
    
    // ============================================================
    // MUSIC GENERATION
    // ============================================================
    
    /**
     * Start playing theme music
     */
    play(themeName = null) {
        if (themeName) this.currentTheme = themeName;
        
        if (!this.activate()) return;
        
        // Stop any existing music
        this.stop();
        
        const theme = this.themes[this.currentTheme];
        if (!theme) {
            console.error('Unknown theme:', this.currentTheme);
            return;
        }
        
        console.log(`🎵 [MusicSubstrate] Playing: ${theme.name} (${theme.bpm} BPM)`);
        
        this.isPlaying = true;
        
        // Start all layers
        this._startBass(theme);
        this._startMelody(theme);
        this._startArpeggio(theme);
        if (theme.drumEnabled) this._startDrums(theme);
        
        // Fibonacci-specific layers
        if (theme.chordMode) {
            this._startFibonacciChords(theme);
            this._startFibonacciRhythm(theme);
        }
    },
    
    /**
     * Stop all music
     */
    stop() {
        this.isPlaying = false;
        
        // Cancel any pending resolution timeout
        if (this.resolutionTimeout) {
            clearTimeout(this.resolutionTimeout);
            this.resolutionTimeout = null;
        }
        
        // Stop all oscillators
        this.oscillators.forEach(osc => {
            try { osc.stop(); } catch (e) {}
        });
        this.oscillators = [];
        
        // Clear all intervals
        this.intervals.forEach(id => clearInterval(id));
        this.intervals = [];
        
        console.log('🔇 [MusicSubstrate] Music stopped');
    },
    
    /**
     * Stop with a resolving cadence - plays a satisfying ending
     */
    stopWithResolution() {
        const theme = this.themes[this.currentTheme];
        const scale = this.scales[theme?.scale || 'C_MAJOR'];
        const beatMs = 60000 / (theme?.bpm || 120);
        
        // Clear intervals so patterns stop
        this.intervals.forEach(id => clearInterval(id));
        this.intervals = [];
        
        if (!this.audioContext) {
            this.stop();
            return;
        }
        
        console.log('🎵 [MusicSubstrate] Playing final resolution...');
        
        // Play a satisfying V-I (dominant to tonic) cadence
        // V chord (scale degree 4 in zero-indexed)
        setTimeout(() => {
            // Dominant chord
            this._playTone(scale[4] / 2, beatMs / 1000 * 1.5, 'triangle', 0.12);
            this._playTone(scale[4], beatMs / 1000 * 1.2, 'sine', 0.08);
            this._playTone(scale[6] || scale[4] * 1.5, beatMs / 1000 * 1, 'sine', 0.06);
        }, 0);
        
        // I chord (root/tonic) - the resolution
        setTimeout(() => {
            // Root - the satisfying resolution
            const rootFreq = scale[0];
            this._playTone(rootFreq / 2, beatMs / 1000 * 3, 'triangle', 0.15); // Deep bass
            this._playTone(rootFreq, beatMs / 1000 * 2.5, 'sine', 0.12);       // Root
            this._playTone(rootFreq * 2, beatMs / 1000 * 2, 'sine', 0.08);     // Octave
            
            // Add the third for a major feeling (scale degree 2)
            if (scale[2]) {
                this._playTone(scale[2], beatMs / 1000 * 2, 'sine', 0.05);
            }
        }, beatMs * 1.5);
        
        // Final stop after cadence completes
        this.resolutionTimeout = setTimeout(() => {
            this.resolutionTimeout = null;
            this.isPlaying = false;
            this.oscillators.forEach(osc => {
                try { osc.stop(); } catch (e) {}
            });
            this.oscillators = [];
            console.log('🔇 [MusicSubstrate] Music resolved and stopped');
        }, beatMs * 4);
    },
    
    /**
     * Play a resolution cadence without stopping (for phrase endings in game)
     */
    playCadence() {
        const theme = this.themes[this.currentTheme];
        const scale = this.scales[theme?.scale || 'C_MAJOR'];
        const beatMs = 60000 / (theme?.bpm || 120);
        
        if (!this.audioContext || !this.isPlaying) return;
        
        // Quick V-I resolution
        this._playTone(scale[4] / 2, beatMs / 1000 * 0.8, 'triangle', 0.1);
        
        setTimeout(() => {
            this._playTone(scale[0] / 2, beatMs / 1000 * 1.5, 'triangle', 0.12);
            this._playTone(scale[0], beatMs / 1000 * 1.2, 'sine', 0.08);
        }, beatMs * 0.8);
    },
    
    // ============================================================
    // INSTRUMENT LAYERS
    // ============================================================
    
    /**
     * Bass line layer with phrase resolution
     */
    _startBass(theme) {
        const scale = this.scales[theme.scale];
        const beatMs = (60000 / theme.bpm) * 2; // Half notes for bass
        let step = 0;
        const phraseLength = theme.phraseLength || 8;
        const beatsPerPhrase = phraseLength * (theme.bassPattern.length / 2);
        
        const playBassNote = () => {
            if (!this.isPlaying) return;
            
            const phrasePosition = step % beatsPerPhrase;
            const isResolutionTime = phrasePosition >= beatsPerPhrase - (theme.resolutionBass?.length || 2);
            
            let noteIndex, duration;
            
            if (isResolutionTime && theme.resolutionBass) {
                // Play resolution bass notes
                const resolutionIndex = phrasePosition - (beatsPerPhrase - theme.resolutionBass.length);
                noteIndex = theme.resolutionBass[resolutionIndex % theme.resolutionBass.length];
                // Final note of resolution is longer
                const isFinalNote = resolutionIndex === theme.resolutionBass.length - 1;
                duration = isFinalNote ? (theme.resolutionDuration || 2) : 1;
            } else {
                noteIndex = theme.bassPattern[step % theme.bassPattern.length];
                duration = 0.8;
            }
            
            const freq = scale[noteIndex % scale.length] / Math.pow(2, Math.abs(theme.bassOctave));
            
            this._playTone(freq, beatMs / 1000 * duration, 'triangle', 0.15);
            step++;
        };
        
        playBassNote();
        this.intervals.push(setInterval(playBassNote, beatMs));
    },
    
    /**
     * Melody layer with phrase resolution
     */
    _startMelody(theme) {
        const scale = this.scales[theme.scale];
        const beatMs = (60000 / theme.bpm);
        let step = 0;
        const phraseLength = theme.phraseLength || 8;
        const beatsPerPhrase = phraseLength * (theme.melodyPattern.length / 3);
        
        const playMelodyNote = () => {
            if (!this.isPlaying) return;
            
            const phrasePosition = step % beatsPerPhrase;
            const resolutionLength = theme.resolutionMelody?.length || 4;
            const isResolutionTime = phrasePosition >= beatsPerPhrase - resolutionLength;
            
            let noteIndex, duration, volume;
            
            if (isResolutionTime && theme.resolutionMelody) {
                // Play resolution melody - no skipping!
                const resolutionIndex = phrasePosition - (beatsPerPhrase - resolutionLength);
                noteIndex = theme.resolutionMelody[resolutionIndex % resolutionLength];
                
                // Build up to final resolution note
                const isFinalNote = resolutionIndex === resolutionLength - 1;
                duration = isFinalNote ? (theme.resolutionDuration || 2) : 0.7;
                volume = isFinalNote ? 0.12 : 0.09; // Slightly louder resolution
            } else {
                // Regular pattern with variation (skip some notes)
                if (Math.random() > 0.7) {
                    step++;
                    return;
                }
                noteIndex = theme.melodyPattern[step % theme.melodyPattern.length];
                duration = 0.6;
                volume = 0.08;
            }
            
            const freq = scale[noteIndex % scale.length] * 2; // One octave up
            
            this._playTone(freq, beatMs / 1000 * duration, theme.instruments[0], volume);
            step++;
        };
        
        // Start melody slightly offset
        setTimeout(() => {
            playMelodyNote();
            this.intervals.push(setInterval(playMelodyNote, beatMs));
        }, beatMs / 2);
    },
    
    /**
     * Arpeggio layer with phrase resolution
     */
    _startArpeggio(theme) {
        const scale = this.scales[theme.scale];
        const beatMs = (60000 / theme.bpm) / 2; // Eighth notes
        let step = 0;
        const phraseLength = theme.phraseLength || 8;
        // Arpeggios run faster, so more beats per phrase
        const beatsPerPhrase = phraseLength * theme.arpPattern.length * 2;
        
        // Resolution arpeggio - descends to root
        const resolutionArp = [4, 2, 1, 0];
        
        const playArp = () => {
            if (!this.isPlaying) return;
            
            const phrasePosition = step % beatsPerPhrase;
            const isResolutionTime = phrasePosition >= beatsPerPhrase - resolutionArp.length;
            
            let noteIndex, duration, volume;
            
            if (isResolutionTime) {
                // Resolution: cascade down to root
                const resolutionIndex = phrasePosition - (beatsPerPhrase - resolutionArp.length);
                noteIndex = resolutionArp[resolutionIndex % resolutionArp.length];
                
                // Final note holds longer
                const isFinalNote = resolutionIndex === resolutionArp.length - 1;
                duration = isFinalNote ? 1.5 : 0.6;
                volume = isFinalNote ? 0.08 : 0.06;
            } else {
                noteIndex = theme.arpPattern[step % theme.arpPattern.length];
                duration = 0.5;
                volume = 0.05;
            }
            
            const freq = scale[noteIndex % scale.length];
            this._playTone(freq, beatMs / 1000 * duration, 'sine', volume);
            step++;
        };
        
        // Start arp offset
        setTimeout(() => {
            this.intervals.push(setInterval(playArp, beatMs));
        }, beatMs / 4);
    },
    
    /**
     * Drum layer (synthesized percussion)
     */
    _startDrums(theme) {
        const beatMs = (60000 / theme.bpm);
        let beat = 0;
        
        const playDrum = () => {
            if (!this.isPlaying) return;
            
            // Kick on 1 and 3
            if (beat % 4 === 0) {
                this._playKick();
            }
            
            // Snare on 2 and 4
            if (beat % 4 === 2) {
                this._playSnare();
            }
            
            // Hi-hat on every eighth
            this._playHiHat(beat % 2 === 0 ? 0.1 : 0.05);
            
            beat++;
        };
        
        this.intervals.push(setInterval(playDrum, beatMs / 2));
    },
    
    // ============================================================
    // SOUND SYNTHESIS
    // ============================================================
    
    /**
     * Play a tone with envelope
     */
    _playTone(frequency, duration, waveType = 'sine', volume = 0.1) {
        if (!this.audioContext || !this.isPlaying) return;
        
        const osc = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        osc.type = waveType;
        osc.frequency.value = frequency;
        
        // ADSR envelope
        const now = this.audioContext.currentTime;
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(volume, now + 0.02); // Attack
        gainNode.gain.exponentialRampToValueAtTime(volume * 0.7, now + 0.1); // Decay
        gainNode.gain.setValueAtTime(volume * 0.7, now + duration - 0.1); // Sustain
        gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration); // Release
        
        osc.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + duration);
        
        this.oscillators.push(osc);
    },
    
    /**
     * Synthesized kick drum
     */
    _playKick() {
        if (!this.audioContext) return;
        
        const osc = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(150, this.audioContext.currentTime);
        osc.frequency.exponentialRampToValueAtTime(30, this.audioContext.currentTime + 0.15);
        
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + 0.2);
        
        osc.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        osc.start(this.audioContext.currentTime);
        osc.stop(this.audioContext.currentTime + 0.2);
        
        this.oscillators.push(osc);
    },
    
    /**
     * Synthesized snare drum
     */
    _playSnare() {
        if (!this.audioContext) return;
        
        // Noise burst for snare
        const bufferSize = this.audioContext.sampleRate * 0.1;
        const buffer = this.audioContext.createBuffer(1, bufferSize, this.audioContext.sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < bufferSize; i++) {
            data[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
        }
        
        const noise = this.audioContext.createBufferSource();
        noise.buffer = buffer;
        
        const gainNode = this.audioContext.createGain();
        gainNode.gain.setValueAtTime(0.15, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + 0.1);
        
        const filter = this.audioContext.createBiquadFilter();
        filter.type = 'highpass';
        filter.frequency.value = 1000;
        
        noise.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        noise.start();
    },
    
    /**
     * Synthesized hi-hat
     */
    _playHiHat(volume = 0.1) {
        if (!this.audioContext) return;
        
        const bufferSize = this.audioContext.sampleRate * 0.05;
        const buffer = this.audioContext.createBuffer(1, bufferSize, this.audioContext.sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < bufferSize; i++) {
            data[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
        }
        
        const noise = this.audioContext.createBufferSource();
        noise.buffer = buffer;
        
        const gainNode = this.audioContext.createGain();
        gainNode.gain.setValueAtTime(volume, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + 0.05);
        
        const filter = this.audioContext.createBiquadFilter();
        filter.type = 'highpass';
        filter.frequency.value = 7000;
        
        noise.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        noise.start();
    },
    
    /**
     * Play a chord - multiple tones simultaneously
     * Uses Fibonacci-derived intervals for mathematical harmony
     */
    _playChord(frequencies, duration, waveType = 'sine', volume = 0.08) {
        if (!this.audioContext || !this.isPlaying) return;
        
        // Reduce volume per voice to avoid clipping
        const perVoiceVolume = volume / Math.sqrt(frequencies.length);
        
        frequencies.forEach((freq, i) => {
            // Slight detune for warmth (based on golden ratio)
            const detune = (i - frequencies.length / 2) * 2;
            const detuneRatio = Math.pow(2, detune / 1200);
            this._playTone(freq * detuneRatio, duration, waveType, perVoiceVolume);
        });
    },
    
    /**
     * Build a chord from scale degrees for Fibonacci theme
     * @param {Array} scale - The frequency scale
     * @param {Array} degrees - Scale degrees to include in chord
     * @param {number} octaveShift - Octave shift (2 = up one octave)
     */
    _buildChord(scale, degrees, octaveShift = 1) {
        return degrees.map(degree => {
            const freq = scale[degree % scale.length];
            // Handle octave wrapping
            const octaves = Math.floor(degree / scale.length);
            return freq * Math.pow(2, octaves) * octaveShift;
        });
    },
    
    /**
     * Fibonacci chord progression layer
     * Unique to the FIBONACCI theme
     */
    _startFibonacciChords(theme) {
        const scale = this.scales[theme.scale];
        // BPM subdivided by golden ratio for chord changes
        const chordDuration = (60000 / theme.bpm) * this.PHI * 2;
        let step = 0;
        
        const playChord = () => {
            if (!this.isPlaying) return;
            
            // Get chord from Fibonacci progression
            const chordIndex = theme.chordProgression[step % theme.chordProgression.length];
            const chordDegrees = theme.chords[chordIndex % theme.chords.length];
            const frequencies = this._buildChord(scale, chordDegrees, 0.5);
            
            // Play the chord with a warm pad sound
            this._playChord(frequencies, chordDuration / 1000 * 0.9, 'triangle', 0.12);
            
            // Add a subtle sine layer for depth
            this._playChord(
                frequencies.map(f => f * 2), // octave up
                chordDuration / 1000 * 0.7,
                'sine',
                0.04
            );
            
            step++;
        };
        
        playChord();
        this.intervals.push(setInterval(playChord, chordDuration));
    },
    
    /**
     * Fibonacci-specific rhythmic pattern using golden ratio
     * Creates polyrhythm based on Fibonacci numbers
     */
    _startFibonacciRhythm(theme) {
        const beatMs = 60000 / theme.bpm;
        
        // Layer 1: Pulse every 3 beats (Fibonacci)
        let count3 = 0;
        const playPulse3 = () => {
            if (!this.isPlaying) return;
            // Soft wooden knock sound
            const freq = 200 + (count3 % 3) * 50;
            this._playTone(freq, 0.05, 'triangle', 0.06);
            count3++;
        };
        this.intervals.push(setInterval(playPulse3, beatMs * 3));
        
        // Layer 2: Pulse every 5 beats (Fibonacci)
        let count5 = 0;
        const playPulse5 = () => {
            if (!this.isPlaying) return;
            // Bell-like tone
            const freq = 800 + (count5 % 2) * 200;
            this._playTone(freq, 0.15, 'sine', 0.04);
            count5++;
        };
        setTimeout(() => {
            this.intervals.push(setInterval(playPulse5, beatMs * 5));
        }, beatMs * 2);
        
        // Layer 3: Pulse every 8 beats (Fibonacci)
        const playPulse8 = () => {
            if (!this.isPlaying) return;
            // Deep resonance
            this._playTone(110, 0.4, 'sine', 0.08);
            this._playTone(220, 0.3, 'triangle', 0.04);
        };
        setTimeout(() => {
            this.intervals.push(setInterval(playPulse8, beatMs * 8));
        }, beatMs * 5);
    },
    
    // ============================================================
    // STINGERS & SPECIAL EFFECTS
    // ============================================================
    
    /**
     * Victory fanfare
     */
    playVictoryFanfare() {
        if (!this.activate()) return;
        
        const scale = this.scales['C_MAJOR'];
        const notes = [0, 2, 4, 5, 7, 7, 7];
        const delays = [0, 0.15, 0.3, 0.45, 0.6, 0.75, 1.0];
        
        notes.forEach((note, i) => {
            setTimeout(() => {
                this._playTone(scale[note] * 2, 0.4, 'sawtooth', 0.15);
                this._playTone(scale[note], 0.4, 'triangle', 0.1);
            }, delays[i] * 1000);
        });
        
        console.log('🏆 [MusicSubstrate] Victory fanfare!');
    },
    
    /**
     * Capture impact sound
     */
    playCaptureImpact() {
        if (!this.activate()) return;
        
        // Impact boom
        const osc = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(200, this.audioContext.currentTime);
        osc.frequency.exponentialRampToValueAtTime(40, this.audioContext.currentTime + 0.3);
        
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + 0.4);
        
        osc.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        osc.start();
        osc.stop(this.audioContext.currentTime + 0.4);
        
        console.log('💥 [MusicSubstrate] Capture impact!');
    },
    
    /**
     * Tension build
     */
    playTensionBuild() {
        if (!this.activate()) return;
        
        const osc = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(80, this.audioContext.currentTime);
        osc.frequency.exponentialRampToValueAtTime(200, this.audioContext.currentTime + 2);
        
        gainNode.gain.setValueAtTime(0.05, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.15, this.audioContext.currentTime + 2);
        
        osc.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        osc.start();
        osc.stop(this.audioContext.currentTime + 2);
        
        console.log('😰 [MusicSubstrate] Tension building...');
    },
    
    // ============================================================
    // CONTROLS
    // ============================================================
    
    setVolume(value) {
        this.volume = Math.max(0, Math.min(1, value));
        if (this.masterGain) {
            this.masterGain.gain.value = this.volume;
        }
        console.log(`🔊 [MusicSubstrate] Volume: ${Math.round(this.volume * 100)}%`);
    },
    
    setTheme(themeName) {
        if (this.themes[themeName]) {
            const wasPlaying = this.isPlaying;
            this.currentTheme = themeName;
            console.log(`🎨 [MusicSubstrate] Theme: ${this.themes[themeName].name}`);
            if (wasPlaying) {
                this.play();
            }
        }
    },
    
    // ============================================================
    // PING-BASED SOUND GENERATION
    // The substrate is a virtual 2D surface where each point has
    // a natural frequency. Pinging a point produces that sound.
    // ============================================================
    
    /**
     * Substrate grid configuration
     * The grid maps (x, y) coordinates to frequencies
     * x-axis: pitch (low to high)
     * y-axis: timbre/octave modifier
     */
    substrateConfig: {
        width: 100,    // Virtual grid width
        height: 100,   // Virtual grid height
        baseFreq: 110, // A2 - base frequency
        octaves: 4,    // Span 4 octaves
        // Harmonic series regions for different timbres
        regions: {
            bass: { yMin: 0, yMax: 25, waveType: 'sine', octaveShift: -1 },
            mid: { yMin: 25, yMax: 50, waveType: 'triangle', octaveShift: 0 },
            treble: { yMin: 50, yMax: 75, waveType: 'sawtooth', octaveShift: 1 },
            bright: { yMin: 75, yMax: 100, waveType: 'square', octaveShift: 2 }
        }
    },
    
    /**
     * Ping a point on the music substrate using NaturalLens
     * Coordinates map to the z=xy manifold - sound derived from magnitude.
     * 
     * @param {number} x - X coordinate (0-100) - normalized to manifold
     * @param {number} y - Y coordinate (0-100) - normalized to manifold
     * @param {object} options - Optional: duration, volume, attack, decay
     * @returns {object} - { frequency, color, lens, played: boolean }
     */
    ping(x, y, options = {}) {
        // Ensure audio context is active
        if (!this.activate()) {
            console.warn('🔇 [Ping] Cannot ping - audio not activated');
            return { frequency: 0, played: false };
        }
        
        // If context is suspended, queue the ping after resume
        if (this.audioContext.state === 'suspended') {
            console.log('🔇 [Ping] Context suspended, resuming first...');
            this.audioContext.resume().then(() => {
                this._playPing(x, y, options);
            });
            return { frequency: 0, played: false, pending: true };
        }
        
        return this._playPing(x, y, options);
    },
    
    /**
     * Internal: Actually play the ping sound
     */
    _playPing(x, y, options = {}) {
        // Normalize coordinates to -1.5 to 1.5 range (manifold space)
        const normX = ((x / 100) * 3) - 1.5;
        const normY = ((y / 100) * 3) - 1.5;
        
        // Use NaturalLens if available - geometry IS information!
        let frequency, waveType, color, lens;
        if (typeof NaturalLens !== 'undefined') {
            // Ping the manifold - z computed automatically as z = x*y
            lens = NaturalLens.ping(normX, normY);
            
            // Sound derived from magnitude (physics-based)
            frequency = lens.sound.frequency_hz;
            color = lens.color;
            
            // Determine wave type from y region (timbre)
            const yNorm = ((y / 100) * 100);  // Keep 0-100 for region lookup
            if (yNorm < 25) waveType = 'sine';
            else if (yNorm < 50) waveType = 'triangle';
            else if (yNorm < 75) waveType = 'sawtooth';
            else waveType = 'square';
        } else {
            // Fallback: direct frequency calculation
            const octaveRange = this.substrateConfig.octaves;
            const baseFreq = this.substrateConfig.baseFreq;
            const semitones = (x / 100) * (octaveRange * 12);
            frequency = baseFreq * Math.pow(2, semitones / 12);
            
            let region = this.substrateConfig.regions.mid;
            for (const [name, r] of Object.entries(this.substrateConfig.regions)) {
                if (y >= r.yMin && y < r.yMax) {
                    region = r;
                    break;
                }
            }
            frequency *= Math.pow(2, region.octaveShift);
            waveType = region.waveType;
        }
        
        // Sound parameters
        const duration = options.duration || 0.3;
        const volume = options.volume || 0.2;
        const attack = options.attack || 0.01;
        const decay = options.decay || 0.2;
        
        // Create and play the ping sound
        const now = this.audioContext.currentTime;
        const osc = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        osc.type = waveType;
        osc.frequency.value = frequency;
        
        // ADSR envelope for natural ping sound
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(volume, now + attack);
        gainNode.gain.exponentialRampToValueAtTime(volume * 0.5, now + attack + decay * 0.3);
        gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);
        
        osc.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + duration + 0.05);
        
        console.log(`🎵 [NaturalLens Ping] (${x}, ${y}) → ${frequency.toFixed(1)}Hz (${waveType})${color ? ` | ${color.hex}` : ''}`);
        
        return {
            frequency: frequency,
            waveType: waveType,
            duration: duration,
            x: x,
            y: y,
            color: color || null,
            lens: lens || null,
            played: true
        };
    },
    
    /**
     * Ping multiple points in sequence (melody)
     * @param {Array} points - Array of {x, y} coordinates
     * @param {number} interval - Time between pings (ms)
     * @param {object} options - Ping options
     */
    pingSequence(points, interval = 200, options = {}) {
        points.forEach((point, i) => {
            setTimeout(() => {
                this.ping(point.x, point.y, options);
            }, i * interval);
        });
    },
    
    /**
     * Ping a chord (multiple points simultaneously)
     * @param {Array} points - Array of {x, y} coordinates
     * @param {object} options - Ping options
     */
    pingChord(points, options = {}) {
        // Ensure audio is ready
        if (!this.activate()) {
            console.warn('🔇 [Chord] Cannot ping chord - audio not activated');
            return;
        }
        
        // If context is suspended, resume then play
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume().then(() => {
                this._playChord(points, options);
            });
        } else {
            this._playChord(points, options);
        }
    },
    
    /**
     * Internal: Play chord pings
     */
    _playChord(points, options) {
        points.forEach(point => {
            this.ping(point.x, point.y, { ...options, volume: (options.volume || 0.2) / points.length * 2 });
        });
    },
    
    /**
     * Generate a sound check ping - distinctive arpeggio
     */
    pingSoundCheck() {
        console.log('🔔 [Sound Check] Starting sound check...');
        
        // Ensure audio context is activated and running
        if (!this.activate()) {
            console.warn('🔇 [Sound Check] Cannot activate audio context');
            return;
        }
        
        // If context is suspended, wait for resume then play
        if (this.audioContext.state === 'suspended') {
            console.log('🔔 [Sound Check] Resuming suspended audio context...');
            this.audioContext.resume().then(() => {
                console.log('🔔 [Sound Check] Context resumed, playing arpeggio');
                this._playSoundCheckArpeggio();
            }).catch(e => {
                console.warn('🔇 [Sound Check] Failed to resume:', e);
            });
        } else {
            console.log('🔔 [Sound Check] Context running, playing arpeggio');
            this._playSoundCheckArpeggio();
        }
    },
    
    /**
     * Internal: Play the sound check arpeggio
     */
    _playSoundCheckArpeggio() {
        // Ping a C major chord arpeggio across the substrate
        const checkPoints = [
            { x: 0, y: 50 },    // C (root)
            { x: 33, y: 50 },   // E (major third)
            { x: 50, y: 50 },   // G (fifth)
            { x: 100, y: 50 }   // C (octave)
        ];
        this.pingSequence(checkPoints, 150, { duration: 0.25, volume: 0.25 });
        console.log('🔔 [Sound Check] Arpeggio complete!');
    },
    
    /**
     * Convert game board hole position to substrate coordinates
     * Maps FastTrack board holes to musical positions
     * @param {string} holeId - The hole ID (e.g., 'ft-0', 'outer-2-3', 'center')
     * @returns {object} - { x, y } substrate coordinates
     */
    holeToSubstrate(holeId) {
        if (!holeId) return { x: 50, y: 50 };
        
        // Center/bullseye - special bright ping
        if (holeId === 'center') {
            return { x: 75, y: 90 }; // High bright tone
        }
        
        // FastTrack holes (ft-0 to ft-5) - rising scale
        if (holeId.startsWith('ft-')) {
            const idx = parseInt(holeId.replace('ft-', ''));
            return { x: 40 + idx * 10, y: 60 }; // Treble region
        }
        
        // Safe zone - gentle tones
        if (holeId.startsWith('safe-')) {
            const parts = holeId.split('-');
            const safeNum = parseInt(parts[2]);
            return { x: 20 + safeNum * 15, y: 30 }; // Mid region, rising pitch
        }
        
        // Outer track - bass/mid tones based on position
        if (holeId.startsWith('outer-')) {
            const parts = holeId.split('-');
            const section = parseInt(parts[1]);
            const pos = parseInt(parts[2]);
            return { x: (section * 16 + pos * 4) % 100, y: 40 }; // Varied bass
        }
        
        // Side tracks - transitional tones
        if (holeId.startsWith('side-')) {
            const parts = holeId.split('-');
            const section = parseInt(parts[2]);
            const pos = parseInt(parts[3]);
            return { x: 30 + section * 10 + pos * 5, y: 55 };
        }
        
        // Home/holding - low anchor tone
        if (holeId.startsWith('home-') || holeId.startsWith('hold-')) {
            const parts = holeId.split('-');
            const playerIdx = parseInt(parts[1]);
            return { x: 10 + playerIdx * 15, y: 15 }; // Bass region
        }
        
        // Default center position
        return { x: 50, y: 50 };
    },
    
    /**
     * Ping a hole on the game board - converts to substrate and pings
     * @param {string} holeId - The hole ID
     * @param {object} options - Ping options
     */
    pingHole(holeId, options = {}) {
        const coords = this.holeToSubstrate(holeId);
        return this.ping(coords.x, coords.y, options);
    }
};

// Initialize
MusicSubstrate.init();

// Export
if (typeof window !== 'undefined') {
    window.MusicSubstrate = MusicSubstrate;
}

console.log('🎵 [MusicSubstrate] Procedural Music Engine ready!');
console.log('   Themes: Classic Arena, Cosmic Odyssey, Island Calypso, Roman Fanfare');
console.log('   Ping API: MusicSubstrate.ping(x, y) | pingHole(holeId) | pingSoundCheck()');

/**
 * ============================================================
 * FASTTRACK MINIMAL GAME UI
 * ============================================================
 * 
 * Clean, minimal interface:
 * - Top left: Current player only (avatar, name, deck info)
 * - Right side: Retractable settings panel (hamburger on mobile)
 * 
 * ButterflyFX Dimensional Programming Standard
 */

'use strict';

const GameUIMinimal = {
    version: '1.0.0',
    
    // State
    currentPlayer: null,
    deckCount: 52,
    drawnCard: null,
    menuOpen: false,
    isMobile: false,
    players: [],  // All players for indicator bar
    currentPlayerIndex: 0,
    
    // DOM Elements
    elements: {
        container: null,
        playerPanel: null,
        menuPanel: null,
        menuToggle: null,
        overlay: null,
        indicatorBar: null
    },
    
    // ============================================================
    // INITIALIZATION
    // ============================================================
    
    init() {
        console.log('[GameUIMinimal] Initializing...');
        
        // Detect mobile
        this.isMobile = window.innerWidth <= 768;
        
        // Create styles
        this.injectStyles();
        
        // Create UI elements
        this.createCurrentPlayerPanel();
        this.createPlayerIndicatorBar();
        this.createMenuPanel();
        
        // Listen for resize
        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth <= 768;
            this.updateLayout();
        });
        
        // Auto-start music on first user interaction if toggle is active
        const startMusicOnce = () => {
            const toggle = document.getElementById('toggle-music');
            if (toggle && toggle.classList.contains('active') && window.MusicSubstrate) {
                window.MusicSubstrate.play();
            }
            document.removeEventListener('click', startMusicOnce);
            document.removeEventListener('touchstart', startMusicOnce);
            document.removeEventListener('keydown', startMusicOnce);
        };
        document.addEventListener('click', startMusicOnce, { once: true });
        document.addEventListener('touchstart', startMusicOnce, { once: true });
        document.addEventListener('keydown', startMusicOnce, { once: true });
        
        console.log('[GameUIMinimal] Ready');
        return this;
    },
    
    // ============================================================
    // STYLES
    // ============================================================
    
    injectStyles() {
        if (document.getElementById('game-ui-minimal-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'game-ui-minimal-styles';
        style.textContent = `
            /* ===== CURRENT PLAYER PANEL (Top Left, Compact HUD) ===== */
            #current-player-panel {
                position: fixed;
                top: 10px;
                left: 10px;
                z-index: 10005;
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 14px;
                background: rgba(0, 0, 0, 0.65);
                border: 2px solid var(--player-color, #3498db);
                border-radius: 28px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4),
                            0 0 15px var(--player-glow, rgba(52, 152, 219, 0.2));
                backdrop-filter: blur(10px);
                transition: all 0.35s ease, opacity 0.4s ease, transform 0.35s ease;
                font-family: 'Poppins', -apple-system, sans-serif;
                opacity: 0.45;
                pointer-events: auto;
            }
            
            /* Disabled state — not the current human player's turn */
            #current-player-panel.panel-disabled {
                opacity: 0.35;
                filter: grayscale(0.5) brightness(0.7);
                pointer-events: none;
            }
            
            #current-player-panel:hover,
            #current-player-panel.active-turn {
                opacity: 1;
                background: rgba(0, 0, 0, 0.82);
                transform: scale(1.06);
                box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5),
                            0 0 30px var(--player-glow, rgba(52, 152, 219, 0.45));
            }
            
            /* Flowing glow animation when it's the active player's turn */
            #current-player-panel.active-turn {
                animation: panel-glow-flow 2.5s ease-in-out infinite;
            }
            
            @keyframes panel-glow-flow {
                0%, 100% {
                    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5),
                                0 0 25px var(--player-glow, rgba(52, 152, 219, 0.4)),
                                0 0 50px var(--player-glow, rgba(52, 152, 219, 0.15));
                    border-color: var(--player-color, #3498db);
                }
                50% {
                    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.5),
                                0 0 40px var(--player-glow, rgba(52, 152, 219, 0.6)),
                                0 0 70px var(--player-glow, rgba(52, 152, 219, 0.25));
                    border-color: #fff;
                }
            }
            
            .cp-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #2c3e50, #1a252f);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                border: 2px solid var(--player-color, #3498db);
                box-shadow: 0 0 10px var(--player-glow, rgba(52, 152, 219, 0.4));
                flex-shrink: 0;
            }
            
            .cp-info {
                display: flex;
                flex-direction: column;
                gap: 1px;
            }
            
            .cp-name {
                font-size: 0.82em;
                font-weight: 700;
                color: #fff;
                text-shadow: 0 0 8px var(--player-glow, rgba(52, 152, 219, 0.4));
                max-width: 90px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            
            .cp-turn-label {
                font-size: 0.55em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: var(--player-color, #3498db);
                font-weight: 600;
            }
            
            .cp-deck-info {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-left: 4px;
                padding-left: 8px;
                border-left: 1px solid rgba(255, 255, 255, 0.15);
            }
            
            .cp-deck-stack {
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
                transition: transform 0.2s;
            }
            
            .cp-deck-stack:hover {
                transform: scale(1.05);
            }
            
            .cp-deck-icon {
                width: 32px;
                height: 42px;
                background:
                    repeating-linear-gradient(45deg, transparent, transparent 3px, rgba(255,255,255,0.07) 3px, rgba(255,255,255,0.07) 6px),
                    repeating-linear-gradient(-45deg, transparent, transparent 3px, rgba(0,0,0,0.08) 3px, rgba(0,0,0,0.08) 6px),
                    linear-gradient(135deg, #2980b9, #1a5276);
                border-radius: 3px;
                border: 1.5px solid #fff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.65em;
                font-weight: 700;
                color: #fff;
                box-shadow: 1px 1px 4px rgba(0,0,0,0.4);
                position: relative;
            }
            
            .cp-deck-icon::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 10px;
                height: 10px;
                transform: translate(-50%, -50%) rotate(45deg);
                border: 1px solid rgba(255,255,255,0.4);
                border-radius: 2px;
                pointer-events: none;
            }
            
            .cp-deck-icon::after {
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: 2px;
                bottom: 2px;
                background:
                    repeating-linear-gradient(45deg, transparent, transparent 3px, rgba(255,255,255,0.05) 3px, rgba(255,255,255,0.05) 6px),
                    linear-gradient(135deg, #3498db, #2471a3);
                border-radius: 3px;
                border: 1px solid rgba(255,255,255,0.3);
                z-index: -1;
            }
            
            .cp-drawn-card {
                width: 36px;
                height: 48px;
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                border-radius: 4px;
                border: 1.5px solid #333;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.15em;
                font-weight: 900;
                color: #c0392b;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.35);
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .cp-drawn-card:hover {
                transform: scale(1.12) rotate(-3deg);
            }
            
            .cp-drawn-card.black {
                color: #2c3e50;
            }
            
            .cp-drawn-card.empty {
                background: rgba(255,255,255,0.1);
                border: 1.5px dashed rgba(255,255,255,0.3);
                color: rgba(255,255,255,0.3);
                font-size: 0.8em;
            }

            /* Card hint badge — appears below drawn card */
            .cp-card-hint {
                position: absolute;
                bottom: -16px;
                left: 50%;
                transform: translateX(-50%);
                white-space: nowrap;
                font-size: 0.5em;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.3px;
                padding: 1px 5px;
                border-radius: 5px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s;
            }
            .cp-card-hint.visible {
                opacity: 1;
            }
            .cp-card-hint.extra-turn {
                background: rgba(46, 204, 113, 0.85);
                color: #fff;
                box-shadow: 0 0 8px rgba(46, 204, 113, 0.5);
            }
            .cp-card-hint.backward {
                background: rgba(231, 76, 60, 0.85);
                color: #fff;
                box-shadow: 0 0 8px rgba(231, 76, 60, 0.5);
            }
            .cp-card-hint.split {
                background: rgba(155, 89, 182, 0.85);
                color: #fff;
                box-shadow: 0 0 8px rgba(155, 89, 182, 0.5);
            }
            .cp-card-hint.royal {
                background: rgba(241, 196, 15, 0.85);
                color: #1a1a2e;
                box-shadow: 0 0 8px rgba(241, 196, 15, 0.5);
            }

            /* Drawn card wrapper needs relative for hint positioning */
            .cp-drawn-card-wrap {
                position: relative;
                display: inline-flex;
            }
            
            /* ===== MENU TOGGLE BUTTON ===== */
            #menu-toggle-btn {
                position: fixed;
                top: 15px;
                right: 15px;
                z-index: 10010;
                width: 50px;
                height: 50px;
                background: rgba(0, 0, 0, 0.85);
                border: 2px solid #555;
                border-radius: 12px;
                cursor: pointer;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 5px;
                transition: all 0.3s;
                backdrop-filter: blur(10px);
            }
            
            #menu-toggle-btn:hover {
                border-color: #3498db;
                transform: scale(1.05);
            }
            
            #menu-toggle-btn.open {
                border-color: #e74c3c;
            }
            
            .menu-bar {
                width: 24px;
                height: 3px;
                background: #fff;
                border-radius: 2px;
                transition: all 0.3s;
            }
            
            #menu-toggle-btn.open .menu-bar:nth-child(1) {
                transform: rotate(45deg) translate(5px, 5px);
            }
            
            #menu-toggle-btn.open .menu-bar:nth-child(2) {
                opacity: 0;
            }
            
            #menu-toggle-btn.open .menu-bar:nth-child(3) {
                transform: rotate(-45deg) translate(6px, -6px);
            }
            
            /* ===== SIDE MENU PANEL ===== */
            #game-menu-panel {
                position: fixed;
                top: 0;
                right: -320px;
                width: 300px;
                height: 100vh;
                z-index: 10008;
                background: rgba(15, 20, 30, 0.95);
                border-left: 2px solid #333;
                backdrop-filter: blur(15px);
                transition: right 0.3s ease;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            #game-menu-panel.open {
                right: 0;
            }
            
            .menu-header {
                padding: 70px 20px 20px;
                border-bottom: 1px solid #333;
                background: linear-gradient(180deg, rgba(52, 152, 219, 0.2), transparent);
            }
            
            .menu-header h3 {
                margin: 0;
                font-size: 1.3em;
                color: #fff;
                font-weight: 700;
            }
            
            .menu-content {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
            }
            
            .menu-section {
                margin-bottom: 20px;
            }
            
            .menu-section-title {
                font-size: 0.75em;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #888;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 1px solid #333;
            }

            /* ===== DIMENSIONAL ACCORDION CATEGORIES ===== */
            .menu-category {
                margin-bottom: 6px;
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid rgba(255,255,255,0.06);
                background: rgba(255,255,255,0.02);
                transition: border-color 0.3s, box-shadow 0.3s;
            }
            .menu-category:hover {
                border-color: rgba(52,152,219,0.25);
            }
            .menu-category.expanded {
                border-color: rgba(52,152,219,0.35);
                box-shadow: 0 0 12px rgba(52,152,219,0.08), inset 0 0 20px rgba(52,152,219,0.03);
            }
            .menu-category-header {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 13px 14px;
                cursor: pointer;
                user-select: none;
                -webkit-user-select: none;
                background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
                transition: background 0.2s;
                position: relative;
            }
            .menu-category-header::after {
                content: '';
                position: absolute;
                bottom: 0; left: 14px; right: 14px;
                height: 1px;
                background: rgba(255,255,255,0.05);
                opacity: 0;
                transition: opacity 0.3s;
            }
            .menu-category.expanded .menu-category-header::after {
                opacity: 1;
            }
            .menu-category-header:active {
                background: rgba(52,152,219,0.15);
            }
            .cat-icon {
                font-size: 1.15em;
                width: 24px;
                text-align: center;
                filter: drop-shadow(0 0 3px rgba(255,255,255,0.15));
            }
            .cat-title {
                flex: 1;
                color: #ddd;
                font-size: 0.92em;
                font-weight: 600;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                font-family: 'Orbitron', 'Rajdhani', sans-serif;
            }
            .menu-category.expanded .cat-title {
                color: #fff;
                text-shadow: 0 0 8px rgba(52,152,219,0.4);
            }
            .cat-chevron {
                font-size: 0.85em;
                color: #666;
                transition: transform 0.3s cubic-bezier(0.4,0,0.2,1), color 0.3s;
            }
            .menu-category.expanded .cat-chevron {
                transform: rotate(90deg);
                color: #3498db;
            }
            .menu-category-body {
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.35s cubic-bezier(0.4,0,0.2,1), padding 0.35s;
                padding: 0 12px;
            }
            .menu-category.expanded .menu-category-body {
                max-height: 600px;
                padding: 10px 12px 14px;
            }
            /* Dimensional glow line at top of expanded body */
            .menu-category.expanded .menu-category-body::before {
                content: '';
                display: block;
                height: 1px;
                margin-bottom: 8px;
                background: linear-gradient(90deg, transparent, rgba(52,152,219,0.4), rgba(155,89,182,0.3), transparent);
            }
            /* Theme button grid */
            .theme-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 6px;
            }
            .theme-grid .menu-btn {
                padding: 10px 10px;
                font-size: 0.85em;
                justify-content: center;
                text-align: center;
                gap: 6px;
            }
            .theme-grid .menu-btn.active-theme {
                border-color: #3498db;
                background: rgba(52,152,219,0.2);
                box-shadow: 0 0 10px rgba(52,152,219,0.15);
            }
            /* Camera view grid */
            .camera-grid {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 6px;
                margin-bottom: 10px;
            }
            .camera-grid .menu-btn {
                padding: 10px 8px;
                font-size: 0.82em;
                justify-content: center;
                text-align: center;
                gap: 5px;
            }
            .camera-grid .menu-btn.active-cam {
                border-color: #e67e22;
                background: rgba(230,126,34,0.18);
                box-shadow: 0 0 8px rgba(230,126,34,0.12);
            }
            .cam-speed-row {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 6px 4px;
            }
            .cam-speed-row .cam-speed-label {
                font-size: 0.75em;
                color: #888;
            }
            .cam-speed-row .menu-volume-slider {
                flex: 1;
            }
            .cam-speed-row .cam-speed-val {
                font-size: 0.72em;
                color: #aaa;
                width: 50px;
                text-align: right;
            }
            
            .menu-btn {
                width: 100%;
                padding: 12px 15px;
                margin-bottom: 8px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid #333;
                border-radius: 10px;
                color: #fff;
                font-size: 0.95em;
                text-align: left;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .menu-btn:hover {
                background: rgba(52, 152, 219, 0.2);
                border-color: #3498db;
                transform: translateX(5px);
            }
            
            .menu-btn-icon {
                font-size: 1.2em;
            }
            
            .menu-toggle-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 15px;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid #333;
                border-radius: 10px;
                margin-bottom: 8px;
            }
            
            .menu-toggle-label {
                color: #ccc;
                font-size: 0.9em;
            }
            
            .menu-toggle {
                width: 50px;
                height: 26px;
                background: #333;
                border-radius: 13px;
                cursor: pointer;
                position: relative;
                transition: background 0.3s;
            }
            
            .menu-toggle.active {
                background: #27ae60;
            }
            
            .menu-toggle::after {
                content: '';
                position: absolute;
                top: 3px;
                left: 3px;
                width: 20px;
                height: 20px;
                background: #fff;
                border-radius: 50%;
                transition: left 0.3s;
            }
            
            .menu-toggle.active::after {
                left: 27px;
            }
            
            /* ===== VOLUME SLIDERS ===== */
            .menu-volume-row {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 6px 15px 12px;
                margin-top: -4px;
            }
            .menu-volume-row .vol-icon {
                font-size: 0.8em;
                color: #888;
                width: 18px;
                text-align: center;
            }
            .menu-volume-slider {
                -webkit-appearance: none;
                appearance: none;
                flex: 1;
                height: 4px;
                background: #333;
                border-radius: 2px;
                outline: none;
            }
            .menu-volume-slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                appearance: none;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: #9b59b6;
                cursor: pointer;
                border: 2px solid rgba(255,255,255,0.2);
                transition: background 0.2s;
            }
            .menu-volume-slider::-webkit-slider-thumb:hover {
                background: #a76bc8;
            }
            .menu-volume-slider::-moz-range-thumb {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: #9b59b6;
                cursor: pointer;
                border: 2px solid rgba(255,255,255,0.2);
            }
            .menu-volume-pct {
                color: #888;
                font-size: 0.75em;
                width: 30px;
                text-align: right;
            }
            
            /* ===== YOUR TURN POPUP ===== */
            #your-turn-popup {
                position: fixed;
                top: 18px;
                left: 50%;
                transform: translateX(-50%) translateY(-80px);
                z-index: 9999;
                background: linear-gradient(135deg, rgba(39,174,96,0.92), rgba(46,204,113,0.88));
                color: #fff;
                padding: 14px 36px;
                border-radius: 40px;
                font-family: 'Orbitron', 'Rajdhani', sans-serif;
                font-size: 1.3em;
                font-weight: 700;
                letter-spacing: 1px;
                display: flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 6px 30px rgba(39,174,96,0.4), inset 0 1px 0 rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.15);
                pointer-events: none;
                opacity: 0;
                transition: transform 0.4s cubic-bezier(0.34,1.56,0.64,1), opacity 0.4s;
            }
            #your-turn-popup.visible {
                transform: translateX(-50%) translateY(0);
                opacity: 1;
            }
            #your-turn-popup.fade-out {
                opacity: 0;
                transform: translateX(-50%) translateY(-20px);
                transition: transform 0.5s ease-in, opacity 0.5s ease-in;
            }
            #your-turn-popup .turn-glyph {
                font-size: 1.4em;
                animation: turn-pulse 0.8s ease-in-out infinite alternate;
            }
            /* Bot turn styling */
            #your-turn-popup.bot-turn {
                background: linear-gradient(135deg, rgba(142,68,173,0.92), rgba(155,89,182,0.88));
                box-shadow: 0 6px 30px rgba(142,68,173,0.4), inset 0 1px 0 rgba(255,255,255,0.2);
                font-size: 1.1em;
            }
            @keyframes turn-pulse {
                from { transform: scale(1); }
                to { transform: scale(1.15); }
            }

            /* ===== CARD DRAWN POPUP ===== */
            #card-drawn-popup {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) scale(0.3);
                z-index: 20003;
                pointer-events: none;
                opacity: 0;
                transition: transform 0.4s cubic-bezier(0.18,1.2,0.4,1), opacity 0.25s ease-out;
            }
            #card-drawn-popup.visible {
                opacity: 1;
                transform: translate(-50%, -50%) scale(1);
            }
            #card-drawn-popup.fade-out {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0.8);
                transition: transform 0.5s ease-in, opacity 0.4s ease-in;
            }
            .card-popup-face {
                width: 100px;
                height: 140px;
                background: linear-gradient(145deg, #fff, #f0f0f0);
                border-radius: 10px;
                border: 3px solid #333;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-size: 2.8em;
                font-weight: 900;
                color: #c0392b;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5), 0 0 60px rgba(255,255,255,0.15);
                position: relative;
            }
            .card-popup-face.black { color: #2c3e50; }
            .card-popup-suit {
                font-size: 0.5em;
                margin-top: -4px;
            }
            @media (max-width: 768px) {
                .card-popup-face {
                    width: 120px;
                    height: 168px;
                    font-size: 3.2em;
                }
                #your-turn-popup {
                    font-size: 1.4em;
                    padding: 16px 40px;
                }
            }

            /* ===== OVERLAY ===== */
            #menu-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0, 0, 0, 0.5);
                z-index: 10007;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.3s;
            }
            
            #menu-overlay.visible {
                opacity: 1;
                pointer-events: auto;
            }
            
            /* ===== ALL PLAYERS LIST IN MENU ===== */
            .players-list {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .player-list-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 10px;
                border: 1px solid transparent;
                transition: all 0.2s;
            }
            
            .player-list-item.current {
                border-color: var(--player-color, #3498db);
                background: rgba(52, 152, 219, 0.1);
            }
            
            .player-list-avatar {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: #2c3e50;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.3em;
            }
            
            .player-list-info {
                flex: 1;
            }
            
            .player-list-name {
                color: #fff;
                font-weight: 600;
                font-size: 0.9em;
            }
            
            .player-list-pegs {
                font-size: 0.75em;
                color: #888;
            }
            
            /* ===== BOT BADGE ===== */
            .bot-badge {
                display: inline-block;
                padding: 2px 6px;
                margin-left: 6px;
                background: linear-gradient(135deg, #8e44ad, #9b59b6);
                border-radius: 4px;
                font-size: 0.65em;
                font-weight: 700;
                letter-spacing: 0.5px;
                color: #fff;
                text-transform: uppercase;
                vertical-align: middle;
            }
            
            .player-list-item.is-bot .player-list-avatar {
                background: linear-gradient(135deg, #8e44ad, #6c3483);
            }
            
            #current-player-panel.is-bot {
                border-color: #9b59b6;
                --player-color: #9b59b6;
                --player-glow: rgba(155, 89, 182, 0.5);
            }
            
            #current-player-panel.is-bot .cp-turn-label {
                color: #9b59b6;
            }
            
            /* ===== MOBILE ADJUSTMENTS ===== */
            @media (max-width: 768px) {
                #current-player-panel {
                    top: 6px;
                    left: 6px;
                    padding: 8px 12px;
                    gap: 10px;
                }
                
                .cp-avatar {
                    width: 42px;
                    height: 42px;
                    font-size: 22px;
                }
                
                .cp-name {
                    font-size: 0.9em;
                    max-width: 80px;
                }
                
                .cp-turn-label {
                    font-size: 0.6em;
                }
                
                .cp-deck-info {
                    gap: 10px;
                    margin-left: 6px;
                    padding-left: 10px;
                }
                
                .cp-deck-icon {
                    width: 36px;
                    height: 46px;
                    font-size: 0.75em;
                }
                
                .cp-drawn-card {
                    width: 38px;
                    height: 50px;
                    font-size: 1.15em;
                }
                
                #game-menu-panel {
                    width: 280px;
                    right: -290px;
                }
            }
            
            @media (max-width: 480px) {
                #current-player-panel {
                    max-width: calc(100vw - 16px);
                    flex-wrap: wrap;
                }
                
                .cp-avatar {
                    width: 38px;
                    height: 38px;
                    font-size: 20px;
                }
                
                .cp-deck-icon {
                    width: 34px;
                    height: 44px;
                    font-size: 0.7em;
                }
                
                .cp-drawn-card {
                    width: 36px;
                    height: 48px;
                    font-size: 1.1em;
                }
                
                .cp-deck-label {
                    display: none;
                }
                
                .cp-info {
                    display: none;
                }
                
                .cp-turn-dots {
                    border-left: none;
                    border-top: 1px solid rgba(255, 255, 255, 0.12);
                    margin-left: 0;
                    padding-left: 0;
                    padding-top: 4px;
                    margin-top: 1px;
                    width: 100%;
                    justify-content: center;
                }
                
                .pi-dot {
                    width: 20px;
                    height: 20px;
                    font-size: 9px;
                }
            }
            
            /* ===== PLAYER TURN INDICATORS (inside current-player panel) ===== */
            .cp-turn-dots {
                display: flex;
                align-items: center;
                gap: 4px;
                margin-left: 4px;
                padding-left: 8px;
                border-left: 1px solid rgba(255, 255, 255, 0.15);
            }
            
            .pi-dot {
                width: 26px;
                height: 26px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 11px;
                background: var(--dot-color, #555);
                border: 1.5px solid rgba(255, 255, 255, 0.25);
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
            }

            .pi-dot .pi-peg-badge {
                position: absolute;
                bottom: -4px;
                right: -4px;
                min-width: 14px;
                height: 14px;
                border-radius: 7px;
                background: rgba(0, 0, 0, 0.9);
                border: 1px solid var(--dot-color, #555);
                color: #fff;
                font-size: 8px;
                font-weight: 700;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 0 2px;
                line-height: 1;
            }
            
            .pi-dot:hover {
                transform: scale(1.15);
                border-color: rgba(255, 255, 255, 0.7);
            }
            
            .pi-dot.current {
                transform: scale(1.18);
                border: 2px solid #fff;
                box-shadow: 0 0 10px var(--dot-color, #555),
                            0 0 18px var(--dot-color, #555);
                animation: pulse-glow 2s ease-in-out infinite;
            }
            
            @keyframes pulse-glow {
                0%, 100% { box-shadow: 0 0 10px var(--dot-color, #555), 0 0 18px var(--dot-color, #555); }
                50% { box-shadow: 0 0 14px var(--dot-color, #555), 0 0 24px var(--dot-color, #555); }
            }
            
            .pi-dot.is-bot::after {
                content: '🤖';
                position: absolute;
                bottom: -3px;
                right: -3px;
                font-size: 8px;
                background: #8e44ad;
                border-radius: 50%;
                width: 13px;
                height: 13px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .pi-dot .pi-tooltip {
                position: absolute;
                top: 110%;
                left: 50%;
                transform: translateX(-50%);
                margin-top: 4px;
                padding: 6px 10px;
                background: rgba(0, 0, 0, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                white-space: nowrap;
                font-size: 12px;
                color: #fff;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.2s;
            }
            
            .pi-dot:hover .pi-tooltip {
                opacity: 1;
            }
            
            .pi-tooltip-name {
                font-weight: 600;
                margin-bottom: 2px;
            }
            
            .pi-tooltip-status {
                font-size: 10px;
                color: #aaa;
            }
            
            /* Mobile: smaller dots */
            @media (max-width: 768px) {
                .cp-turn-dots {
                    gap: 4px;
                    margin-left: 6px;
                    padding-left: 8px;
                }
                
                .pi-dot {
                    width: 26px;
                    height: 26px;
                    font-size: 11px;
                }
                
                .pi-dot.current {
                    transform: scale(1.15);
                }

                .pi-dot .pi-peg-badge {
                    min-width: 14px;
                    height: 14px;
                    font-size: 8px;
                }
            }
        `;
        
        document.head.appendChild(style);
    },
    
    // ============================================================
    // CREATE UI ELEMENTS
    // ============================================================
    
    createCurrentPlayerPanel() {
        // Remove existing
        const existing = document.getElementById('current-player-panel');
        if (existing) existing.remove();
        
        const panel = document.createElement('div');
        panel.id = 'current-player-panel';
        panel.innerHTML = `
            <div class="cp-avatar" id="cp-avatar">👤</div>
            <div class="cp-info">
                <div class="cp-turn-label">Current Turn</div>
                <div class="cp-name" id="cp-name">Player 1</div>
            </div>
            <div class="cp-deck-info">
                <div class="cp-deck-stack" id="cp-deck" title="Draw a card">
                    <div class="cp-deck-icon" id="cp-deck-count">52</div>
                </div>
                <div class="cp-drawn-card-wrap">
                    <div class="cp-drawn-card empty" id="cp-drawn-card" title="Your drawn card">?</div>
                    <div class="cp-card-hint" id="cp-card-hint"></div>
                </div>
            </div>
            <div class="cp-turn-dots" id="player-indicator-bar">
                <!-- Populated by setPlayers() -->
            </div>
        `;
        
        document.body.appendChild(panel);
        this.elements.playerPanel = panel;
        
        // Click to draw card
        document.getElementById('cp-deck').addEventListener('click', () => {
            this.onDrawCard();
        });
    },
    
    createPlayerIndicatorBar() {
        // Indicator bar is now embedded inside the current-player-panel
        // Just grab the reference
        this.elements.indicatorBar = document.getElementById('player-indicator-bar');
    },
    
    updatePlayerIndicatorBar() {
        const bar = this.elements.indicatorBar;
        if (!bar || !this.players.length) {
            console.log('[GameUIMinimal.updatePlayerIndicatorBar] Skipping - bar:', !!bar, 'players:', this.players.length);
            return;
        }
        
        console.log('[GameUIMinimal.updatePlayerIndicatorBar] Rendering', this.players.length, 'players');
        console.log('[GameUIMinimal.updatePlayerIndicatorBar] Player data:', this.players.map(p => ({
            name: p.name,
            avatar: p.avatar,
            isAI: p.isAI,
            isBot: p.isBot,
            isHuman: p.isHuman
        })));
        
        // Use actual board theme colors if available, fallback to defaults
        const fallbackColors = ['#e74c3c', '#3498db', '#f1c40f', '#27ae60', '#9b59b6', '#e67e22'];
        const botIcons = ['🤖', '🔧', '⚙️', '🎮', '💻'];
        
        bar.innerHTML = this.players.map((p, i) => {
            const isBot = p.isAI || p.isBot || (p.name && (p.name.includes('🤖') || p.name.includes('🔧')));
            const isCurrent = i === this.currentPlayerIndex;
            // Get the actual themed player color from the board (matches peg/section colors)
            let color = fallbackColors[i % fallbackColors.length];
            if (typeof getThemedPlayerColor === 'function') {
                try {
                    const themeColor = getThemedPlayerColor(i);
                    color = '#' + (themeColor >>> 0).toString(16).padStart(6, '0');
                } catch(e) { /* fallback */ }
            } else if (p.colorHex) {
                color = p.colorHex;
            }
            // Use player's avatar if not a bot, otherwise use bot icon
            const avatar = isBot ? botIcons[i % botIcons.length] : (p.avatar || '👤');
            const pegsInHolding = p.pegsInHolding ?? 4;
            const pegsHome = p.pegsInSafeZone || p.pegsHome || 0;
            const pegsOnBoard = p.pegsOnBoard || 0;
            const status = isCurrent ? 'Playing...' : `Hold: ${pegsInHolding} | Board: ${pegsOnBoard} | Home: ${pegsHome}`;
            
            return `
                <div class="pi-dot ${isCurrent ? 'current' : ''} ${isBot ? 'is-bot' : ''}" 
                     style="--dot-color: ${color}; background: ${color};">
                    ${avatar}
                    <span class="pi-peg-badge">${pegsInHolding}</span>
                    <div class="pi-tooltip">
                        <div class="pi-tooltip-name">${p.name || 'Player ' + (i + 1)}</div>
                        <div class="pi-tooltip-status">${status}</div>
                    </div>
                </div>
            `;
        }).join('');
    },
    
    createMenuPanel() {
        // Remove existing
        ['menu-toggle-btn', 'game-menu-panel', 'menu-overlay'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.remove();
        });
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.id = 'menu-overlay';
        overlay.addEventListener('click', () => this.toggleMenu(false));
        document.body.appendChild(overlay);
        this.elements.overlay = overlay;
        
        // Create toggle button
        const toggle = document.createElement('button');
        toggle.id = 'menu-toggle-btn';
        toggle.innerHTML = `
            <div class="menu-bar"></div>
            <div class="menu-bar"></div>
            <div class="menu-bar"></div>
        `;
        toggle.addEventListener('click', () => this.toggleMenu());
        document.body.appendChild(toggle);
        this.elements.menuToggle = toggle;
        
        // Create menu panel
        const menu = document.createElement('div');
        menu.id = 'game-menu-panel';
        menu.innerHTML = `
            <div class="menu-header">
                <h3>⚡ FastTrack</h3>
            </div>
            <div class="menu-content">
                <!-- Players bar — always visible -->
                <div class="menu-section">
                    <div class="menu-section-title">Players</div>
                    <div class="players-list" id="menu-players-list"></div>
                </div>

                <!-- ═══ THEME ═══ -->
                <div class="menu-category" data-cat="theme">
                    <div class="menu-category-header" onclick="GameUIMinimal.toggleCategory('theme')">
                        <span class="cat-icon">🎨</span>
                        <span class="cat-title">Theme</span>
                        <span class="cat-chevron">▸</span>
                    </div>
                    <div class="menu-category-body">
                        <div class="theme-grid">
                            <button class="menu-btn" data-theme="cosmic" onclick="GameUIMinimal.setTheme('cosmic')">
                                <span class="menu-btn-icon">🌌</span> Cosmic
                            </button>
                            <button class="menu-btn" data-theme="spaceace" onclick="GameUIMinimal.setTheme('spaceace')">
                                <span class="menu-btn-icon">🚀</span> Space Ace ✦
                            </button>
                            <button class="menu-btn" data-theme="undersea" onclick="GameUIMinimal.setTheme('undersea')">
                                <span class="menu-btn-icon">🌊</span> Undersea
                            </button>
                            <button class="menu-btn" data-theme="colosseum" onclick="GameUIMinimal.setTheme('colosseum')">
                                <span class="menu-btn-icon">⚔️</span> Colosseum
                            </button>
                            <button class="menu-btn" data-theme="highcontrast" onclick="GameUIMinimal.setTheme('highcontrast')">
                                <span class="menu-btn-icon">👁️</span> Clean
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ═══ SOUNDS ═══ -->
                <div class="menu-category" data-cat="sounds">
                    <div class="menu-category-header" onclick="GameUIMinimal.toggleCategory('sounds')">
                        <span class="cat-icon">🔊</span>
                        <span class="cat-title">Sounds</span>
                        <span class="cat-chevron">▸</span>
                    </div>
                    <div class="menu-category-body">
                        <div class="menu-toggle-row">
                            <span class="menu-toggle-label">🎵 Music</span>
                            <div class="menu-toggle active" id="toggle-music" onclick="GameUIMinimal.toggleMusic()"></div>
                        </div>
                        <div class="menu-volume-row">
                            <span class="vol-icon">🔈</span>
                            <input type="range" class="menu-volume-slider" id="slider-music" min="0" max="100" value="20" oninput="GameUIMinimal.setMusicVolume(this.value)">
                            <span class="menu-volume-pct" id="pct-music">20%</span>
                        </div>
                        <div class="menu-toggle-row">
                            <span class="menu-toggle-label">🔊 Sound FX</span>
                            <div class="menu-toggle active" id="toggle-sfx" onclick="GameUIMinimal.toggleSFX()"></div>
                        </div>
                        <div class="menu-volume-row">
                            <span class="vol-icon">🔈</span>
                            <input type="range" class="menu-volume-slider" id="slider-sfx" min="0" max="100" value="60" oninput="GameUIMinimal.setSfxVolume(this.value)">
                            <span class="menu-volume-pct" id="pct-sfx">60%</span>
                        </div>
                        <div class="menu-toggle-row">
                            <span class="menu-toggle-label">🎤 Commentary</span>
                            <div class="menu-toggle" id="toggle-commentary" onclick="GameUIMinimal.toggleCommentary()"></div>
                        </div>
                    </div>
                </div>

                <!-- ═══ CONTROLS ═══ -->
                <div class="menu-category" data-cat="controls">
                    <div class="menu-category-header" onclick="GameUIMinimal.toggleCategory('controls')">
                        <span class="cat-icon">🎮</span>
                        <span class="cat-title">Controls</span>
                        <span class="cat-chevron">▸</span>
                    </div>
                    <div class="menu-category-body">
                        <button class="menu-btn" onclick="GameUIMinimal.askMom()">
                            <span class="menu-btn-icon">👩‍👧</span> Ask Mom for Help
                        </button>
                        <button class="menu-btn" onclick="GameUIMinimal.restartGame()">
                            <span class="menu-btn-icon">🔄</span> Restart Game
                        </button>
                        <button class="menu-btn" onclick="GameUIMinimal.exitGame()">
                            <span class="menu-btn-icon">🚪</span> Exit to Menu
                        </button>
                    </div>
                </div>

                <!-- ═══ CAMERA ═══ -->
                <div class="menu-category" data-cat="camera">
                    <div class="menu-category-header" onclick="GameUIMinimal.toggleCategory('camera')">
                        <span class="cat-icon">📹</span>
                        <span class="cat-title">Camera</span>
                        <span class="cat-chevron">▸</span>
                    </div>
                    <div class="menu-category-body">
                        <div class="camera-grid">
                            <button class="menu-btn active-cam" data-cam="board" onclick="GameUIMinimal.setCameraView('board')">
                                <span class="menu-btn-icon">🎯</span> Board
                            </button>
                            <button class="menu-btn" data-cam="ground" onclick="GameUIMinimal.setCameraView('ground')">
                                <span class="menu-btn-icon">🏃</span> Ground
                            </button>
                            <button class="menu-btn" data-cam="chase" onclick="GameUIMinimal.setCameraView('chase')">
                                <span class="menu-btn-icon">🎬</span> Chase
                            </button>
                            <button class="menu-btn" data-cam="orbit" onclick="GameUIMinimal.setCameraView('orbit')">
                                <span class="menu-btn-icon">🌀</span> Orbit
                            </button>
                            <button class="menu-btn" data-cam="manual" onclick="GameUIMinimal.setCameraView('manual')">
                                <span class="menu-btn-icon">✋</span> Manual
                            </button>
                            <button class="menu-btn" data-cam="pegeye" onclick="GameUIMinimal.enterPegEyeView()">
                                <span class="menu-btn-icon">👁️</span> Peg's Eye
                            </button>
                        </div>
                        <div class="cam-speed-row">
                            <span class="cam-speed-label">🐢</span>
                            <input type="range" class="menu-volume-slider" id="menu-cam-speed" min="0.2" max="2.0" step="0.1" value="0.6" oninput="GameUIMinimal.setCameraSpeed(this.value)">
                            <span class="cam-speed-val" id="menu-cam-speed-val">Smooth</span>
                        </div>
                    </div>
                </div>

                <!-- ═══ RULES ═══ -->
                <div class="menu-category" data-cat="rules">
                    <div class="menu-category-header" onclick="GameUIMinimal.toggleCategory('rules')">
                        <span class="cat-icon">📖</span>
                        <span class="cat-title">Rules</span>
                        <span class="cat-chevron">▸</span>
                    </div>
                    <div class="menu-category-body">
                        <button class="menu-btn" onclick="GameUIMinimal.showRules()">
                            <span class="menu-btn-icon">📜</span> Quick Rules
                        </button>
                        <button class="menu-btn" onclick="window.open('docs.html','_blank')">
                            <span class="menu-btn-icon">📘</span> Full Guide
                        </button>
                    </div>
                </div>

                <!-- ═══ TUTORIAL ═══ -->
                <div class="menu-category" data-cat="tutorial">
                    <div class="menu-category-header" onclick="GameUIMinimal.toggleCategory('tutorial')">
                        <span class="cat-icon">🎓</span>
                        <span class="cat-title">Tutorial</span>
                        <span class="cat-chevron">▸</span>
                    </div>
                    <div class="menu-category-body">
                        <button class="menu-btn" onclick="GameUIMinimal.startTutorial()">
                            <span class="menu-btn-icon">▶️</span> Start Tutorial
                        </button>
                        <button class="menu-btn" onclick="GameUIMinimal.showBoardTooltips()">
                            <span class="menu-btn-icon">💡</span> Board Tooltips
                        </button>
                    </div>
                </div>

            </div>
        `;
        
        document.body.appendChild(menu);
        this.elements.menuPanel = menu;
    },
    
    // ============================================================
    // UPDATE METHODS
    // ============================================================
    
    setCurrentPlayer(player, playerIndex = 0) {
        console.log('[GameUIMinimal.setCurrentPlayer] Called with player:', {
            name: player?.name,
            avatar: player?.avatar,
            isAI: player?.isAI,
            isHuman: player?.isHuman,
            isBot: player?.isBot
        }, 'playerIndex:', playerIndex);
        
        this.currentPlayer = player;
        this.currentPlayerIndex = playerIndex;
        
        const colors = [
            { color: '#e74c3c', glow: 'rgba(231, 76, 60, 0.5)' },
            { color: '#3498db', glow: 'rgba(52, 152, 219, 0.5)' },
            { color: '#f1c40f', glow: 'rgba(241, 196, 15, 0.5)' },
            { color: '#27ae60', glow: 'rgba(39, 174, 96, 0.5)' },
            { color: '#9b59b6', glow: 'rgba(155, 89, 182, 0.5)' },
            { color: '#e67e22', glow: 'rgba(230, 126, 34, 0.5)' }
        ];
        
        const colorSet = colors[playerIndex % colors.length];
        const panel = this.elements.playerPanel;
        
        if (panel) {
            panel.style.setProperty('--player-color', colorSet.color);
            panel.style.setProperty('--player-glow', colorSet.glow);
            
            // Detect if this is a bot
            const isBot = player.isAI || player.isBot || (player.name && player.name.includes('🤖')) || (player.name && player.name.includes('🔧'));
            
            // Bot icons rotation
            const botIcons = ['🤖', '🔧', '⚙️', '🎮', '💻'];
            const botIcon = botIcons[playerIndex % botIcons.length];
            
            const avatarEl = document.getElementById('cp-avatar');
            const nameEl = document.getElementById('cp-name');
            const labelEl = document.querySelector('.cp-turn-label');
            
            if (isBot) {
                // Show bot icon and label
                avatarEl.textContent = botIcon;
                nameEl.textContent = player.name || `Bot ${playerIndex}`;
                if (labelEl) labelEl.textContent = 'Bot Turn';
                panel.classList.add('is-bot');
                // Panel is disabled/faded during bot turns
                panel.classList.add('panel-disabled');
                panel.classList.remove('active-turn');
                // Show bot playing popup
                this.showBotTurnPopup(player.name || `Bot ${playerIndex + 1}`);
            } else {
                // Show player's chosen avatar
                avatarEl.textContent = player.avatar || '👤';
                nameEl.textContent = player.name || player.username || `Player ${playerIndex + 1}`;
                if (labelEl) labelEl.textContent = 'Your Turn';
                panel.classList.remove('is-bot');
                // Panel is active and glowing during human turn
                panel.classList.remove('panel-disabled');
                panel.classList.add('active-turn');
                // Show "Your Turn!" popup
                this.showYourTurnPopup();
            }
        }
        
        // Update indicator bar to highlight current player
        this.updatePlayerIndicatorBar();
    },
    
    setDeckCount(count) {
        this.deckCount = count;
        const deckEl = document.getElementById('cp-deck-count');
        if (deckEl) {
            deckEl.textContent = count;
        }
    },
    
    setDrawnCard(card) {
        this.drawnCard = card;
        const cardEl = document.getElementById('cp-drawn-card');
        const hintEl = document.getElementById('cp-card-hint');
        
        if (!cardEl) return;
        
        // Clear hint
        if (hintEl) {
            hintEl.className = 'cp-card-hint';
            hintEl.textContent = '';
        }
        
        if (!card) {
            cardEl.className = 'cp-drawn-card empty';
            cardEl.textContent = '?';
            return;
        }
        
        // Determine color
        const isRed = card.suit === '♥' || card.suit === '♦' || 
                      card.includes?.('♥') || card.includes?.('♦');
        
        cardEl.className = 'cp-drawn-card' + (isRed ? '' : ' black');
        
        // Format card display
        if (typeof card === 'string') {
            cardEl.textContent = card;
        } else if (card.value) {
            cardEl.textContent = card.value + (card.suit || '');
        } else {
            cardEl.textContent = card;
        }
        
        // Show contextual card hint
        if (hintEl) {
            const v = card.value || '';
            const vUp = v.toString().toUpperCase();
            if (vUp === '4') {
                hintEl.textContent = '⬅ Back 4';
                hintEl.className = 'cp-card-hint backward visible';
            } else if (vUp === '7') {
                hintEl.textContent = '✂ Split 7';
                hintEl.className = 'cp-card-hint split visible';
            } else if (vUp === 'J' || vUp === 'Q' || vUp === 'K') {
                hintEl.textContent = '👑 +Turn · Exit 🎯';
                hintEl.className = 'cp-card-hint royal visible';
            } else if (vUp === 'A' || vUp === '1' || vUp === 'JOKER') {
                hintEl.textContent = '🔄 +Turn · Enter';
                hintEl.className = 'cp-card-hint extra-turn visible';
            } else if (vUp === '6') {
                hintEl.textContent = '🔄 +Turn · Enter';
                hintEl.className = 'cp-card-hint extra-turn visible';
            }
        }
    },
    
    setPlayers(players, currentIndex = 0) {
        console.log('[GameUIMinimal.setPlayers] Called with', players?.length, 'players');
        console.log('[GameUIMinimal.setPlayers] Player data:', JSON.stringify(players?.map(p => ({
            name: p.name, 
            avatar: p.avatar, 
            isAI: p.isAI, 
            isHuman: p.isHuman
        }))));
        
        this.players = players;
        this.currentPlayerIndex = currentIndex;
        
        // Update indicator bar (always visible at bottom)
        this.updatePlayerIndicatorBar();
        
        // Update menu list
        const list = document.getElementById('menu-players-list');
        if (!list) return;
        
        const botIcons = ['🤖', '🔧', '⚙️', '🎮', '💻'];
        
        list.innerHTML = players.map((p, i) => {
            const isBot = p.isAI || p.isBot || (p.name && p.name.includes('🤖')) || (p.name && p.name.includes('🔧'));
            const avatar = isBot ? botIcons[i % botIcons.length] : (p.avatar || '👤');
            const label = isBot ? 'Bot' : '';
            
            return `
            <div class="player-list-item ${i === currentIndex ? 'current' : ''} ${isBot ? 'is-bot' : ''}" 
                 style="--player-color: ${this.getPlayerColor(i)}">
                <div class="player-list-avatar">${avatar}</div>
                <div class="player-list-info">
                    <div class="player-list-name">${p.name || p.username || 'Player ' + (i + 1)} ${label ? '<span class="bot-badge">BOT</span>' : ''}</div>
                    <div class="player-list-pegs">${p.pegsHome || 0}/5 pegs home</div>
                </div>
            </div>
        `;
        }).join('');
    },
    
    getPlayerColor(index) {
        const colors = ['#e74c3c', '#3498db', '#f1c40f', '#27ae60', '#9b59b6', '#e67e22'];
        return colors[index % colors.length];
    },
    
    // ============================================================
    // MENU CONTROLS
    // ============================================================
    
    toggleMenu(force = null) {
        this.menuOpen = force !== null ? force : !this.menuOpen;
        
        this.elements.menuPanel?.classList.toggle('open', this.menuOpen);
        this.elements.menuToggle?.classList.toggle('open', this.menuOpen);
        this.elements.overlay?.classList.toggle('visible', this.menuOpen);
    },
    
    updateLayout() {
        // Adjust UI for screen size
        // Currently handled by CSS media queries
    },
    
    // ============================================================
    // ACTION HANDLERS
    // ============================================================
    
    onDrawCard() {
        // Dismiss turn popup immediately
        this.dismissYourTurnPopup();
        // Trigger draw card action
        if (window.drawCard) {
            window.drawCard();
        } else if (window.FastrackEngine?.drawCard) {
            window.FastrackEngine.drawCard();
        }
        console.log('[GameUIMinimal] Draw card triggered');
    },
    
    setTheme(themeName) {
        if (typeof window.setTheme === 'function') {
            window.setTheme(themeName);
        } else if (window.FastTrackThemes?.apply) {
            console.warn('[GameUIMinimal] window.setTheme not found, theme may not apply correctly');
            window.FastTrackThemes.apply(themeName);
        }
        // Highlight active theme button
        document.querySelectorAll('.theme-grid .menu-btn').forEach(btn => {
            btn.classList.toggle('active-theme', btn.dataset.theme === themeName);
        });
    },

    // ============================================================
    // ACCORDION CATEGORY TOGGLE
    // ============================================================

    toggleCategory(catName) {
        const cat = document.querySelector(`.menu-category[data-cat="${catName}"]`);
        if (!cat) return;
        const wasExpanded = cat.classList.contains('expanded');
        // Collapse all categories first (accordion behavior — one open at a time)
        document.querySelectorAll('.menu-category.expanded').forEach(el => {
            el.classList.remove('expanded');
        });
        // Toggle the selected one
        if (!wasExpanded) {
            cat.classList.add('expanded');
        }
    },

    // ============================================================
    // CAMERA (delegates to board_3d setCameraViewMode)
    // ============================================================

    setCameraView(viewName) {
        if (typeof window.setCameraViewMode === 'function') {
            window.setCameraViewMode(viewName);
        }
        // Highlight active camera button
        document.querySelectorAll('.camera-grid .menu-btn').forEach(btn => {
            btn.classList.toggle('active-cam', btn.dataset.cam === viewName);
        });
    },

    setCameraSpeed(val) {
        if (typeof window.setCameraSpeed === 'function') {
            window.setCameraSpeed(val);
        }
        const speedLabel = document.getElementById('menu-cam-speed-val');
        if (speedLabel) {
            const v = parseFloat(val);
            if (v <= 0.4) speedLabel.textContent = 'Slow';
            else if (v <= 0.8) speedLabel.textContent = 'Smooth';
            else if (v <= 1.3) speedLabel.textContent = 'Fast';
            else speedLabel.textContent = 'Blazing';
        }
        // Sync the board_3d slider if present
        const boardSlider = document.getElementById('camera-speed-slider');
        if (boardSlider) boardSlider.value = val;
    },

    enterPegEyeView() {
        if (typeof window.enterPegEyeMode === 'function') {
            window.enterPegEyeMode();
        }
        this.toggleMenu(false);
    },

    // ============================================================
    // ASK MOM / TUTORIAL / TOOLTIPS
    // ============================================================

    askMom() {
        if (typeof window.showMomHelp === 'function') {
            window.showMomHelp();
        }
        this.toggleMenu(false);
    },

    startTutorial() {
        if (window.FastTrackTutorial && typeof window.FastTrackTutorial.start === 'function') {
            window.FastTrackTutorial.start();
        }
        this.toggleMenu(false);
    },

    showBoardTooltips() {
        if (window.BoardTooltips && typeof window.BoardTooltips.toggle === 'function') {
            window.BoardTooltips.toggle();
        } else if (window.BoardTooltips && typeof window.BoardTooltips.enable === 'function') {
            window.BoardTooltips.enable();
        }
        this.toggleMenu(false);
    },
    
    toggleMusic() {
        const toggle = document.getElementById('toggle-music');
        toggle?.classList.toggle('active');
        
        if (window.MusicSubstrate) {
            if (toggle?.classList.contains('active')) {
                window.MusicSubstrate.play();
            } else {
                window.MusicSubstrate.stop();
            }
        }
    },
    
    toggleSFX() {
        const toggle = document.getElementById('toggle-sfx');
        toggle?.classList.toggle('active');
        
        if (window.GameSFX) {
            window.GameSFX.enabled = toggle?.classList.contains('active');
        }
    },
    
    toggleCommentary() {
        const toggle = document.getElementById('toggle-commentary');
        toggle?.classList.toggle('active');
        
        if (window.CommentarySubstrate) {
            window.CommentarySubstrate.enabled = toggle?.classList.contains('active');
        }
    },

    // ============================================================
    // YOUR TURN POPUP
    // ============================================================

    _turnPopupTimer: null,

    showYourTurnPopup() {
        // Create popup if it doesn't exist
        let popup = document.getElementById('your-turn-popup');
        if (!popup) {
            popup = document.createElement('div');
            popup.id = 'your-turn-popup';
            popup.innerHTML = '<span class="turn-glyph">🎯</span> Your Turn!';
            document.body.appendChild(popup);
        }

        // Clear any pending fade
        if (this._turnPopupTimer) clearTimeout(this._turnPopupTimer);
        popup.classList.remove('fade-out', 'visible');

        // Trigger slide-in on next frame
        requestAnimationFrame(() => {
            popup.classList.add('visible');
        });

        // Auto-fade after 3 seconds
        this._turnPopupTimer = setTimeout(() => {
            this.dismissYourTurnPopup();
        }, 3000);
    },

    dismissYourTurnPopup() {
        const popup = document.getElementById('your-turn-popup');
        if (!popup) return;
        if (this._turnPopupTimer) {
            clearTimeout(this._turnPopupTimer);
            this._turnPopupTimer = null;
        }
        popup.classList.remove('visible');
        popup.classList.add('fade-out');
    },

    // ============================================================
    // BOT TURN POPUP
    // ============================================================

    showBotTurnPopup(botName) {
        let popup = document.getElementById('your-turn-popup');
        if (!popup) {
            popup = document.createElement('div');
            popup.id = 'your-turn-popup';
            document.body.appendChild(popup);
        }

        if (this._turnPopupTimer) clearTimeout(this._turnPopupTimer);
        popup.classList.remove('fade-out', 'visible', 'bot-turn');
        popup.innerHTML = `<span class="turn-glyph">🤖</span> ${botName} is playing`;
        popup.classList.add('bot-turn');

        requestAnimationFrame(() => {
            popup.classList.add('visible');
        });

        this._turnPopupTimer = setTimeout(() => {
            this.dismissYourTurnPopup();
        }, 2500);
    },

    // ============================================================
    // CARD DRAWN POPUP
    // ============================================================

    _cardPopupTimer: null,

    showCardDrawnPopup(cardValue, cardSuit, isRed) {
        // Remove existing
        let popup = document.getElementById('card-drawn-popup');
        if (popup) popup.remove();

        popup = document.createElement('div');
        popup.id = 'card-drawn-popup';
        const colorClass = isRed ? '' : ' black';
        popup.innerHTML = `
            <div class="card-popup-face${colorClass}">
                <span>${cardValue || '?'}</span>
                <span class="card-popup-suit">${cardSuit || ''}</span>
            </div>
        `;
        document.body.appendChild(popup);

        if (this._cardPopupTimer) clearTimeout(this._cardPopupTimer);

        requestAnimationFrame(() => {
            popup.classList.add('visible');
        });

        // The popup stays until dismissCardDrawnPopup() is called (when camera is ready)
        // But auto-dismiss after 5 seconds as fallback
        this._cardPopupTimer = setTimeout(() => {
            this.dismissCardDrawnPopup();
        }, 5000);
    },

    dismissCardDrawnPopup() {
        const popup = document.getElementById('card-drawn-popup');
        if (!popup) return;
        if (this._cardPopupTimer) {
            clearTimeout(this._cardPopupTimer);
            this._cardPopupTimer = null;
        }
        popup.classList.remove('visible');
        popup.classList.add('fade-out');
        setTimeout(() => popup.remove(), 600);
    },

    // ============================================================
    // CAMERA-GATE STATE
    // ============================================================

    cameraReady: true,

    setCameraReady(ready) {
        this.cameraReady = ready;
        if (ready) {
            // Dismiss card popup when camera is in place
            this.dismissCardDrawnPopup();
        }
    },

    setMusicVolume(pct) {
        const val = parseInt(pct, 10);
        const pctEl = document.getElementById('pct-music');
        if (pctEl) pctEl.textContent = val + '%';
        if (window.MusicSubstrate) {
            window.MusicSubstrate.setVolume(val / 100);
        }
    },

    setSfxVolume(pct) {
        const val = parseInt(pct, 10);
        const pctEl = document.getElementById('pct-sfx');
        if (pctEl) pctEl.textContent = val + '%';
        if (window.GameSFX) {
            window.GameSFX.setVolume(val / 100);
        }
    },

    showRules() {
        // Show rules modal
        if (window.showRulesModal) {
            window.showRulesModal();
        } else {
            window.open('index.html#rules', '_blank');
        }
        this.toggleMenu(false);
    },
    
    restartGame() {
        if (confirm('Restart the game?')) {
            location.reload();
        }
    },
    
    exitGame() {
        if (confirm('Exit to main menu?')) {
            window.location.href = 'index.html';
        }
    },
    
    // ============================================================
    // INTEGRATION
    // ============================================================
    
    /**
     * Called when game state updates
     */
    updateFromGameState(gameState) {
        if (!gameState) return;
        
        // Update current player
        const currentIdx = gameState.currentPlayerIndex || 0;
        const currentPlayer = gameState.players?.[currentIdx];
        
        if (currentPlayer) {
            this.setCurrentPlayer(currentPlayer, currentIdx);
        }
        
        // Update deck count
        if (gameState.deckCount !== undefined) {
            this.setDeckCount(gameState.deckCount);
        }
        
        // Update drawn card
        this.setDrawnCard(gameState.currentCard || gameState.drawnCard || null);
        
        // Update players list in menu
        if (gameState.players) {
            this.setPlayers(gameState.players, currentIdx);
        }
    },
    
    /**
     * Disable old panel systems
     */
    disableOldPanels() {
        // Hide old panels
        ['player-panels', 'player-panels-new', 'player-panels-v2-container'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });
        
        // Disable old panel modules
        if (window.PlayerPanelsV2) {
            window.PlayerPanelsV2.enabled = false;
        }
        
        console.log('[GameUIMinimal] Old panel systems disabled');
    }
};

// Auto-initialize when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => GameUIMinimal.init());
} else {
    GameUIMinimal.init();
}

// Export
window.GameUIMinimal = GameUIMinimal;

console.log('[GameUIMinimal] Module loaded - Clean, minimal game UI');

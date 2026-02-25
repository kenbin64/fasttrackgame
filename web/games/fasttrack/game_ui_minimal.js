/**
 * ============================================================
 * FASTTRACK MINIMAL GAME UI
 * ============================================================
 * 
 * Clean, minimal interface:
 * - Top left: Current player only (avatar, name, deck info)
 * - Right side: Retractable settings panel (cog icon)
 * - Dimensional drill-down navigation (ButterflyFX standard)
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
    
    // Dimensional navigation state
    dimensionStack: [],       // navigation history for back-traversal
    currentDimension: 'root', // currently displayed dimension level
    
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
            
            /* ===== MENU COG BUTTON ===== */
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
                align-items: center;
                justify-content: center;
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
            
            .menu-cog {
                width: 26px;
                height: 26px;
                fill: #fff;
                transition: transform 0.6s cubic-bezier(0.4,0,0.2,1);
            }
            
            #menu-toggle-btn:hover .menu-cog {
                transform: rotate(45deg);
            }
            
            #menu-toggle-btn.open .menu-cog {
                transform: rotate(180deg);
                fill: #e74c3c;
            }
            
            /* ===== SIDE MENU PANEL ===== */
            #game-menu-panel {
                position: fixed;
                top: 0;
                right: -400px;
                width: 380px;
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

            /* ===== DIMENSIONAL NAVIGATION ===== */
            .dim-viewport {
                position: relative;
                overflow: hidden;
            }
            .dim-layer {
                animation: dimSlideIn 0.28s cubic-bezier(0.4,0,0.2,1) forwards;
            }
            .dim-layer.slide-out {
                animation: dimSlideOut 0.22s cubic-bezier(0.4,0,0.2,1) forwards;
            }
            @keyframes dimSlideIn {
                from { opacity: 0; transform: translateX(30px); }
                to   { opacity: 1; transform: translateX(0); }
            }
            @keyframes dimSlideOut {
                from { opacity: 1; transform: translateX(0); }
                to   { opacity: 0; transform: translateX(-30px); }
            }
            /* Back-arrow row */
            .dim-back {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 14px;
                margin-bottom: 8px;
                cursor: pointer;
                border-radius: 10px;
                background: rgba(52,152,219,0.08);
                border: 1px solid rgba(52,152,219,0.15);
                transition: all 0.2s;
                user-select: none;
                -webkit-user-select: none;
            }
            .dim-back:hover {
                background: rgba(52,152,219,0.18);
                border-color: rgba(52,152,219,0.35);
            }
            .dim-back:active {
                transform: translateX(-3px);
            }
            .dim-back-arrow {
                font-size: 1.2em;
                color: #3498db;
            }
            .dim-back-label {
                color: #aaa;
                font-size: 0.85em;
                font-family: 'Orbitron', 'Rajdhani', sans-serif;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            /* Dimension items — categories & actions */
            .dim-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 16px;
                margin-bottom: 6px;
                border-radius: 12px;
                cursor: pointer;
                border: 1px solid rgba(255,255,255,0.06);
                background: rgba(255,255,255,0.02);
                transition: all 0.2s;
                user-select: none;
                -webkit-user-select: none;
            }
            .dim-item:hover {
                border-color: rgba(52,152,219,0.3);
                background: rgba(52,152,219,0.12);
                transform: translateX(4px);
            }
            .dim-item:active {
                background: rgba(52,152,219,0.2);
            }
            .dim-item-icon {
                font-size: 1.3em;
                width: 28px;
                text-align: center;
                filter: drop-shadow(0 0 3px rgba(255,255,255,0.15));
            }
            .dim-item-text {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 2px;
            }
            .dim-item-label {
                color: #ddd;
                font-size: 0.95em;
                font-weight: 600;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                font-family: 'Orbitron', 'Rajdhani', sans-serif;
            }
            .dim-item-about {
                color: #777;
                font-size: 0.75em;
                font-weight: 400;
                letter-spacing: 0;
                text-transform: none;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                line-height: 1.3;
            }
            .dim-item-arrow {
                font-size: 0.85em;
                color: #555;
                transition: transform 0.2s, color 0.2s;
            }
            .dim-item:hover .dim-item-arrow {
                color: #3498db;
                transform: translateX(3px);
            }
            /* Active state for themes / cameras */
            .dim-item.active-item {
                border-color: rgba(52,152,219,0.4);
                background: rgba(52,152,219,0.15);
                box-shadow: 0 0 12px rgba(52,152,219,0.1);
            }
            .dim-item.active-item .dim-item-label {
                color: #fff;
                text-shadow: 0 0 8px rgba(52,152,219,0.4);
            }
            /* Toggle rows inside dimensions */
            .dim-toggle-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 14px 16px;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px;
                margin-bottom: 6px;
            }
            .dim-toggle-label {
                display: flex;
                align-items: center;
                gap: 10px;
                color: #ccc;
                font-size: 0.9em;
            }
            .dim-toggle-label-icon {
                font-size: 1.15em;
            }
            /* Slider rows inside dimensions */
            .dim-slider-row {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 16px 14px;
                margin-top: -4px;
            }
            .dim-slider-icon {
                font-size: 0.8em;
                color: #888;
                width: 18px;
                text-align: center;
            }
            .dim-slider-val {
                font-size: 0.72em;
                color: #aaa;
                width: 40px;
                text-align: right;
            }
            /* Section divider inside a dimension */
            .dim-divider {
                height: 1px;
                margin: 12px 0;
                background: linear-gradient(90deg, transparent, rgba(52,152,219,0.3), rgba(155,89,182,0.2), transparent);
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
                    width: 320px;
                    right: -340px;
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
        
        // Create cog toggle button
        const toggle = document.createElement('button');
        toggle.id = 'menu-toggle-btn';
        toggle.innerHTML = `
            <svg class="menu-cog" viewBox="0 0 24 24">
                <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 00.12-.61l-1.92-3.32a.49.49 0 00-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 00-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.49.49 0 00-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58a.49.49 0 00-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6A3.6 3.6 0 1112 8.4a3.6 3.6 0 010 7.2z"/>
            </svg>
        `;
        toggle.addEventListener('click', () => this.toggleMenu());
        document.body.appendChild(toggle);
        this.elements.menuToggle = toggle;
        
        // Create menu panel (dimensional shell)
        const menu = document.createElement('div');
        menu.id = 'game-menu-panel';
        menu.innerHTML = `
            <div class="menu-header">
                <h3>⚡ FastTrack</h3>
            </div>
            <div class="menu-content">
                <div class="dim-viewport" id="dim-viewport"></div>
            </div>
        `;
        
        document.body.appendChild(menu);
        this.elements.menuPanel = menu;
        
        // Render root dimension
        this.dimensionStack = [];
        this.currentDimension = 'root';
        this.renderDimension('root');
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
        
        // Reset to root dimension when opening
        if (this.menuOpen) {
            this.dimensionStack = [];
            this.currentDimension = 'root';
            this.renderDimension('root');
        }
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
        // Re-render current dimension to update active state
        if (this.currentDimension === 'theme') {
            this.renderDimension('theme');
        }
    },

    // ============================================================
    // DIMENSIONAL NAVIGATION
    // ============================================================

    /**
     * Theme metadata — name, icon, about description
     */
    themeInfo: {
        cosmic:       { icon: '🌌', label: 'Cosmic',       about: 'Deep space nebulae, floating shapes and stardust particles' },
        spaceace:     { icon: '🚀', label: 'Space Ace ✦',  about: 'Retro arcade adventure with asteroids and cosmic dust' },
        undersea:     { icon: '🌊', label: 'Undersea',     about: 'Ocean depths with jellyfish, sea turtles and coral' },
        colosseum:    { icon: '⚔️', label: 'Colosseum',    about: 'Ancient Rome — toga-clad spectators and golden thrones' },
        fibonacci:    { icon: '🔢', label: 'Fibonacci',    about: 'Mathematical beauty with golden spirals and sacred ratios' },
        highcontrast: { icon: '👁️', label: 'Clean',        about: 'High contrast, minimal distractions for focused play' }
    },

    /**
     * Drill down into a sub-dimension
     */
    drillDown(dimensionId) {
        this.dimensionStack.push(this.currentDimension);
        this.currentDimension = dimensionId;
        this.renderDimension(dimensionId);
    },

    /**
     * Navigate back up one dimension level
     */
    drillUp() {
        if (this.dimensionStack.length === 0) return;
        this.currentDimension = this.dimensionStack.pop();
        this.renderDimension(this.currentDimension, true);
    },

    /**
     * Render a specific dimension into the viewport
     */
    renderDimension(dimensionId, isBack = false) {
        const vp = document.getElementById('dim-viewport');
        if (!vp) return;

        let html = '';
        switch (dimensionId) {
            case 'root':    html = this._renderRoot(); break;
            case 'theme':   html = this._renderTheme(); break;
            case 'sounds':  html = this._renderSounds(); break;
            case 'controls': html = this._renderControls(); break;
            case 'camera':  html = this._renderCamera(); break;
            case 'rules':   html = this._renderRules(); break;
            case 'tutorial': html = this._renderTutorial(); break;
            default:        html = this._renderRoot(); break;
        }

        // Wrap in animated layer
        const dir = isBack ? 'back' : 'forward';
        vp.innerHTML = `<div class="dim-layer" style="animation-name: ${isBack ? 'dimSlideInBack' : 'dimSlideIn'}">${html}</div>`;

        // Add reverse animation keyframes if back
        if (isBack) {
            // Inject back-animation if not present
            if (!document.getElementById('dim-back-anim')) {
                const s = document.createElement('style');
                s.id = 'dim-back-anim';
                s.textContent = `
                    @keyframes dimSlideInBack {
                        from { opacity: 0; transform: translateX(-30px); }
                        to   { opacity: 1; transform: translateX(0); }
                    }
                `;
                document.head.appendChild(s);
            }
        }
    },

    _renderRoot() {
        const categories = [
            { id: 'theme',    icon: '🎨', label: 'Theme' },
            { id: 'sounds',   icon: '🔊', label: 'Sounds' },
            { id: 'controls', icon: '🎮', label: 'Controls' },
            { id: 'camera',   icon: '📹', label: 'Camera' },
            { id: 'rules',    icon: '📖', label: 'Rules' },
            { id: 'tutorial', icon: '🎓', label: 'Tutorial' }
        ];

        return categories.map(c => `
            <div class="dim-item" onclick="GameUIMinimal.drillDown('${c.id}')">
                <span class="dim-item-icon">${c.icon}</span>
                <div class="dim-item-text">
                    <span class="dim-item-label">${c.label}</span>
                </div>
                <span class="dim-item-arrow">▸</span>
            </div>
        `).join('');
    },

    _renderTheme() {
        const currentTheme = window.currentThemeName || 'spaceace';
        const themes = Object.entries(this.themeInfo);

        return `
            <div class="dim-back" onclick="GameUIMinimal.drillUp()">
                <span class="dim-back-arrow">◂</span>
                <span class="dim-back-label">Back</span>
            </div>
            ${themes.map(([key, t]) => `
                <div class="dim-item ${key === currentTheme ? 'active-item' : ''}" onclick="GameUIMinimal.setTheme('${key}')">
                    <span class="dim-item-icon">${t.icon}</span>
                    <div class="dim-item-text">
                        <span class="dim-item-label">${t.label}</span>
                        <span class="dim-item-about">${t.about}</span>
                    </div>
                </div>
            `).join('')}
        `;
    },

    _renderSounds() {
        // Read current states
        const musicActive = document.getElementById('toggle-music')?.classList.contains('active') ?? true;
        const sfxActive = document.getElementById('toggle-sfx')?.classList.contains('active') ?? true;
        const commActive = document.getElementById('toggle-commentary')?.classList.contains('active') ?? false;
        const musicVol = document.getElementById('slider-music')?.value ?? 20;
        const sfxVol = document.getElementById('slider-sfx')?.value ?? 60;

        return `
            <div class="dim-back" onclick="GameUIMinimal.drillUp()">
                <span class="dim-back-arrow">◂</span>
                <span class="dim-back-label">Back</span>
            </div>
            <div class="dim-toggle-row">
                <span class="dim-toggle-label"><span class="dim-toggle-label-icon">🎵</span> Music</span>
                <div class="menu-toggle ${musicActive ? 'active' : ''}" id="toggle-music" onclick="GameUIMinimal.toggleMusic()"></div>
            </div>
            <div class="dim-slider-row">
                <span class="dim-slider-icon">🔈</span>
                <input type="range" class="menu-volume-slider" id="slider-music" min="0" max="100" value="${musicVol}" oninput="GameUIMinimal.setMusicVolume(this.value)">
                <span class="menu-volume-pct" id="pct-music">${musicVol}%</span>
            </div>
            <div class="dim-toggle-row">
                <span class="dim-toggle-label"><span class="dim-toggle-label-icon">🔊</span> Sound FX</span>
                <div class="menu-toggle ${sfxActive ? 'active' : ''}" id="toggle-sfx" onclick="GameUIMinimal.toggleSFX()"></div>
            </div>
            <div class="dim-slider-row">
                <span class="dim-slider-icon">🔈</span>
                <input type="range" class="menu-volume-slider" id="slider-sfx" min="0" max="100" value="${sfxVol}" oninput="GameUIMinimal.setSfxVolume(this.value)">
                <span class="menu-volume-pct" id="pct-sfx">${sfxVol}%</span>
            </div>
            <div class="dim-toggle-row">
                <span class="dim-toggle-label"><span class="dim-toggle-label-icon">🎤</span> Commentary</span>
                <div class="menu-toggle ${commActive ? 'active' : ''}" id="toggle-commentary" onclick="GameUIMinimal.toggleCommentary()"></div>
            </div>
        `;
    },

    _renderControls() {
        return `
            <div class="dim-back" onclick="GameUIMinimal.drillUp()">
                <span class="dim-back-arrow">◂</span>
                <span class="dim-back-label">Back</span>
            </div>
            <div class="dim-item" onclick="GameUIMinimal.askMom()">
                <span class="dim-item-icon">👩‍👧</span>
                <div class="dim-item-text">
                    <span class="dim-item-label">Ask Mom</span>
                    <span class="dim-item-about">Get helpful hints for your next move</span>
                </div>
            </div>
            <div class="dim-item" onclick="GameUIMinimal.restartGame()">
                <span class="dim-item-icon">🔄</span>
                <div class="dim-item-text">
                    <span class="dim-item-label">Restart</span>
                    <span class="dim-item-about">Start a new game from scratch</span>
                </div>
            </div>
            <div class="dim-item" onclick="GameUIMinimal.exitGame()">
                <span class="dim-item-icon">🚪</span>
                <div class="dim-item-text">
                    <span class="dim-item-label">Exit</span>
                    <span class="dim-item-about">Return to the main menu</span>
                </div>
            </div>
        `;
    },

    _renderCamera() {
        const currentCam = window.currentCameraMode || 'board';
        const cams = [
            { id: 'board',  icon: '🎯', label: 'Board',     about: 'Classic overhead view of the entire board' },
            { id: 'ground', icon: '🏃', label: 'Ground',    about: 'Low-angle view from table level' },
            { id: 'chase',  icon: '🎬', label: 'Chase',     about: 'Follows the action dynamically' },
            { id: 'orbit',  icon: '🌀', label: 'Orbit',     about: 'Slowly circles the board' },
            { id: 'manual', icon: '✋', label: 'Manual',    about: 'Free camera — drag to look around' },
            { id: 'pegeye', icon: '👁️', label: "Peg's Eye", about: 'See the board from your peg\'s perspective' }
        ];
        const speedVal = document.getElementById('menu-cam-speed')?.value ?? 0.6;
        const v = parseFloat(speedVal);
        let speedLabel = 'Smooth';
        if (v <= 0.4) speedLabel = 'Slow';
        else if (v <= 0.8) speedLabel = 'Smooth';
        else if (v <= 1.3) speedLabel = 'Fast';
        else speedLabel = 'Blazing';

        return `
            <div class="dim-back" onclick="GameUIMinimal.drillUp()">
                <span class="dim-back-arrow">◂</span>
                <span class="dim-back-label">Back</span>
            </div>
            ${cams.map(c => {
                const action = c.id === 'pegeye' 
                    ? 'GameUIMinimal.enterPegEyeView()' 
                    : `GameUIMinimal.setCameraView('${c.id}')`;
                return `
                <div class="dim-item ${c.id === currentCam ? 'active-item' : ''}" 
                     onclick="${action}">
                    <span class="dim-item-icon">${c.icon}</span>
                    <div class="dim-item-text">
                        <span class="dim-item-label">${c.label}</span>
                        <span class="dim-item-about">${c.about}</span>
                    </div>
                </div>
            `}).join('')}
            <div class="dim-divider"></div>
            <div class="dim-slider-row">
                <span class="dim-slider-icon">🐢</span>
                <input type="range" class="menu-volume-slider" id="menu-cam-speed" min="0.2" max="2.0" step="0.1" value="${speedVal}" oninput="GameUIMinimal.setCameraSpeed(this.value)">
                <span class="dim-slider-val" id="menu-cam-speed-val">${speedLabel}</span>
            </div>
        `;
    },

    _renderRules() {
        return `
            <div class="dim-back" onclick="GameUIMinimal.drillUp()">
                <span class="dim-back-arrow">◂</span>
                <span class="dim-back-label">Back</span>
            </div>
            <div class="dim-item" onclick="GameUIMinimal.showRules()">
                <span class="dim-item-icon">📜</span>
                <div class="dim-item-text">
                    <span class="dim-item-label">Quick Rules</span>
                    <span class="dim-item-about">Essential rules at a glance</span>
                </div>
            </div>
            <div class="dim-item" onclick="window.open('docs.html','_blank')">
                <span class="dim-item-icon">📘</span>
                <div class="dim-item-text">
                    <span class="dim-item-label">Full Guide</span>
                    <span class="dim-item-about">Complete rules and strategy guide</span>
                </div>
            </div>
        `;
    },

    _renderTutorial() {
        return `
            <div class="dim-back" onclick="GameUIMinimal.drillUp()">
                <span class="dim-back-arrow">◂</span>
                <span class="dim-back-label">Back</span>
            </div>
            <div class="dim-item" onclick="GameUIMinimal.startTutorial()">
                <span class="dim-item-icon">▶️</span>
                <div class="dim-item-text">
                    <span class="dim-item-label">Start Tutorial</span>
                    <span class="dim-item-about">Learn how to play step by step</span>
                </div>
            </div>
            <div class="dim-item" onclick="GameUIMinimal.showBoardTooltips()">
                <span class="dim-item-icon">💡</span>
                <div class="dim-item-text">
                    <span class="dim-item-label">Board Tooltips</span>
                    <span class="dim-item-about">Hover hints explaining board spaces</span>
                </div>
            </div>
        `;
    },

    // ============================================================
    // CAMERA (delegates to board_3d setCameraViewMode)
    // ============================================================

    setCameraView(viewName) {
        if (typeof window.setCameraViewMode === 'function') {
            window.setCameraViewMode(viewName);
        }
        // Re-render camera dimension to update active state
        if (this.currentDimension === 'camera') {
            this.renderDimension('camera');
        }
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

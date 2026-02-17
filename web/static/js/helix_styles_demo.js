/**
 * HelixStyles Demo - Interactive Showcase
 * 
 * Copyright (c) 2024-2026 Kenneth Bingham
 * Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
 */

(function() {
    'use strict';
    
    // =============================================================================
    // STATE
    // =============================================================================
    
    var canvas, ctx;
    var presentation = null;
    var currentSwarm = null;
    var currentLevel = 6;
    var currentTheme = 'dark';
    var HS = null;  // HelixStyles reference
    
    var LEVEL_NAMES = [
        'Potential', 'Point', 'Length', 'Width', 'Plane', 'Volume', 'Whole'
    ];
    
    // =============================================================================
    // INITIALIZATION
    // =============================================================================
    
    function init() {
        canvas = document.getElementById('canvas');
        if (!canvas) {
            console.error('Canvas element not found!');
            showError('Canvas element not found');
            return;
        }
        
        ctx = canvas.getContext('2d');
        
        // IMMEDIATE VISUAL TEST - draw something right away
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        ctx.fillStyle = '#0a0f1e';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#4060ff';
        ctx.font = '48px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('HelixStyles Loading...', canvas.width/2, canvas.height/2);
        console.log('Initial canvas test drawn');
        
        // Check if HelixStyles is available
        HS = window.HelixStyles;
        if (!HS) {
            console.error('HelixStyles not loaded!');
            showError('HelixStyles library not loaded');
            return;
        }
        
        console.log('HelixStyles loaded:', Object.keys(HS));
        
        // Setup canvas
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // Init presentation
        initPresentation();
        
        // Setup event listeners
        setupEventListeners();
        
        // Hide loading message
        var loadingMsg = document.getElementById('loading-msg');
        if (loadingMsg) {
            loadingMsg.style.display = 'none';
        }
        
        console.log('HelixStyles Demo initialized!');
    }
    
    function showError(msg) {
        var overlay = document.getElementById('ui-overlay');
        if (overlay) {
            overlay.innerHTML = '<div style="color:red;padding:50px;text-align:center;"><h1>Error</h1><p>' + msg + '</p></div>';
        }
    }
    
    function resizeCanvas() {
        if (!canvas) return;
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        if (presentation) {
            presentation.resize(canvas.width, canvas.height);
        }
    }
    
    // =============================================================================
    // PRESENTATION SETUP
    // =============================================================================
    
    function initPresentation() {
        presentation = HS.createPresentation(canvas, currentTheme);
        
        // Create initial text swarm
        currentSwarm = presentation.createTextSwarm('ButterflyFX', -100, 0, {
            charSpacing: 25,
            color: new HS.HelixColor(0, 1, 0, 6)
        });
        
        // Add some visual interest - explode and then reform
        setTimeout(function() {
            if (currentSwarm) {
                currentSwarm.explode(30);
                setTimeout(function() {
                    if (currentSwarm) {
                        currentSwarm.morphToText('ButterflyFX', 25, -100);
                    }
                }, 1500);
            }
        }, 500);
        
        presentation.start();
    }
    
    // =============================================================================
    // CONTROL FUNCTIONS
    // =============================================================================
    
    function createNewSwarm() {
        var textInput = document.getElementById('swarm-text');
        var text = (textInput && textInput.value) ? textInput.value : 'ButterflyFX';
        
        if (currentSwarm && presentation) {
            // Remove old swarm
            var idx = presentation.swarms.indexOf(currentSwarm);
            if (idx >= 0) presentation.swarms.splice(idx, 1);
        }
        
        // Create new swarm with rainbow colors
        currentSwarm = presentation.createTextSwarm(text, -text.length * 9, 0, {
            charSpacing: 22,
            color: new HS.HelixColor(Math.random() * HS.TAU, 1, 0, currentLevel)
        });
        
        // Dramatic entrance
        for (var i = 0; i < currentSwarm.particles.length; i++) {
            var p = currentSwarm.particles[i];
            p.x = (Math.random() - 0.5) * canvas.width;
            p.y = (Math.random() - 0.5) * canvas.height;
            p.z = (Math.random() - 0.5) * 500;
            p.attractStrength = 0.08;
        }
        
        // Set targets to form text
        setTimeout(function() {
            if (currentSwarm) {
                currentSwarm.morphToText(text, 22, -text.length * 11);
            }
        }, 100);
    }
    
    function explodeSwarm() {
        if (currentSwarm) {
            currentSwarm.explode(80);
            
            // Add some extra chaos
            for (var i = 0; i < currentSwarm.particles.length; i++) {
                var p = currentSwarm.particles[i];
                p.rotation = Math.random() * HS.TAU;
                p.vz = (Math.random() - 0.5) * 30;
            }
        }
    }
    
    function implodeSwarm() {
        if (currentSwarm) {
            currentSwarm.implode(0, 0, 0.15);
        }
    }
    
    function spiralFormation() {
        if (currentSwarm) {
            currentSwarm.spiralFormation(0, 0, 150);
        }
    }
    
    function sphereFormation() {
        if (currentSwarm) {
            currentSwarm.sphereFormation(0, 0, 0, 150);
        }
    }
    
    function waveFormation() {
        if (currentSwarm) {
            currentSwarm.waveFormation(0, 0, 400, 80, 2);
        }
    }
    
    function textFormation() {
        if (currentSwarm) {
            var textInput = document.getElementById('swarm-text');
            var text = (textInput && textInput.value) ? textInput.value : 'ButterflyFX';
            currentSwarm.morphToText(text, 22, -text.length * 11);
        }
    }
    
    function setLevel(level) {
        currentLevel = level;
        
        // Update button states
        var buttons = document.querySelectorAll('.level-buttons button');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].classList.toggle('active', i === level);
        }
        
        // Update indicator
        var indicator = document.getElementById('current-level');
        if (indicator) {
            indicator.textContent = 'Level ' + level + ': ' + LEVEL_NAMES[level];
        }
        
        // Apply to swarm with transition
        if (currentSwarm && currentSwarm.particles.length > 0) {
            var fromLevel = currentSwarm.particles[0].level || 6;
            
            // Create transition effect
            var transition = new HS.HelixTransition({
                fromLevel: fromLevel,
                toLevel: level,
                duration: 500,
                onUpdate: function(progress, currentLvl) {
                    if (currentSwarm) {
                        currentSwarm.applyLevelTransition(fromLevel, level, progress);
                    }
                }
            });
            transition.start();
            
            var runTransition = function() {
                transition.update();
                if (!transition.isComplete) {
                    requestAnimationFrame(runTransition);
                }
            };
            runTransition();
        }
    }
    
    function changeTheme(themeName) {
        currentTheme = themeName;
        
        // Update body class for CSS theme styling
        document.body.className = 'theme-' + themeName;
        
        // Save current text
        var textInput = document.getElementById('swarm-text');
        var currentText = (textInput && textInput.value) ? textInput.value : 'ButterflyFX';
        
        // Reinitialize presentation with new theme
        if (presentation) {
            presentation.stop();
        }
        
        // Create new presentation
        presentation = HS.createPresentation(canvas, themeName);
        
        // Recreate swarm
        currentSwarm = presentation.createTextSwarm(currentText, -currentText.length * 9, 0, {
            charSpacing: 22,
            color: new HS.HelixColor(Math.random() * HS.TAU, 1, 0, currentLevel)
        });
        
        presentation.start();
    }
    
    function morphText() {
        if (!currentSwarm) return;
        
        var morphInput = document.getElementById('morph-text');
        var newText = (morphInput && morphInput.value) ? morphInput.value : 'MORPHED';
        
        // First scatter slightly
        for (var i = 0; i < currentSwarm.particles.length; i++) {
            var p = currentSwarm.particles[i];
            p.vx += (Math.random() - 0.5) * 10;
            p.vy += (Math.random() - 0.5) * 10;
            p.vz += (Math.random() - 0.5) * 5;
        }
        
        // Then morph
        setTimeout(function() {
            if (currentSwarm) {
                currentSwarm.morphToText(newText, 22, -newText.length * 11);
            }
        }, 200);
        
        // Swap the text fields
        var swarmInput = document.getElementById('swarm-text');
        if (swarmInput && morphInput) {
            var temp = swarmInput.value;
            swarmInput.value = morphInput.value;
            morphInput.value = temp;
        }
    }
    
    // =============================================================================
    // EVENT LISTENERS
    // =============================================================================
    
    function setupEventListeners() {
        var mouseX = 0, mouseY = 0;
        var isMouseDown = false;
        
        canvas.addEventListener('mousemove', function(e) {
            mouseX = e.clientX - canvas.width / 2;
            mouseY = e.clientY - canvas.height / 2;
            
            // Subtle attraction to mouse
            if (currentSwarm && !isMouseDown) {
                for (var i = 0; i < currentSwarm.particles.length; i++) {
                    var p = currentSwarm.particles[i];
                    var dx = mouseX - p.x;
                    var dy = mouseY - p.y;
                    var dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 200) {
                        p.vx += dx * 0.0001;
                        p.vy += dy * 0.0001;
                    }
                }
            }
        });
        
        canvas.addEventListener('mousedown', function(e) {
            isMouseDown = true;
            mouseX = e.clientX - canvas.width / 2;
            mouseY = e.clientY - canvas.height / 2;
            
            // Strong attraction on click
            if (currentSwarm) {
                currentSwarm.implode(mouseX, mouseY, 0.2);
            }
        });
        
        canvas.addEventListener('mouseup', function() {
            isMouseDown = false;
            
            // Return to text formation
            if (currentSwarm) {
                var textInput = document.getElementById('swarm-text');
                var text = (textInput && textInput.value) ? textInput.value : 'ButterflyFX';
                setTimeout(function() {
                    if (currentSwarm) {
                        currentSwarm.morphToText(text, 22, -text.length * 11);
                    }
                }, 500);
            }
        });
        
        // Touch support
        canvas.addEventListener('touchstart', function(e) {
            e.preventDefault();
            var touch = e.touches[0];
            if (currentSwarm) {
                var tx = touch.clientX - canvas.width / 2;
                var ty = touch.clientY - canvas.height / 2;
                currentSwarm.explode(50, tx, ty);
            }
        });
        
        canvas.addEventListener('touchend', function(e) {
            e.preventDefault();
            if (currentSwarm) {
                var textInput = document.getElementById('swarm-text');
                var text = (textInput && textInput.value) ? textInput.value : 'ButterflyFX';
                setTimeout(function() {
                    if (currentSwarm) {
                        currentSwarm.morphToText(text, 22, -text.length * 11);
                    }
                }, 800);
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Don't handle if typing in input
            if (e.target.tagName === 'INPUT') return;
            
            // Number keys 0-6 for levels
            if (e.key >= '0' && e.key <= '6') {
                setLevel(parseInt(e.key));
            }
            
            // E for explode
            if (e.key === 'e' || e.key === 'E') {
                explodeSwarm();
            }
            
            // I for implode
            if (e.key === 'i' || e.key === 'I') {
                implodeSwarm();
            }
            
            // S for spiral
            if (e.key === 's' || e.key === 'S') {
                spiralFormation();
            }
            
            // W for wave
            if (e.key === 'w' || e.key === 'W') {
                waveFormation();
            }
            
            // Space for new random formation
            if (e.key === ' ') {
                e.preventDefault();
                var formations = [spiralFormation, sphereFormation, waveFormation];
                formations[Math.floor(Math.random() * formations.length)]();
            }
        });
    }
    
    // =============================================================================
    // GLOBAL EXPORTS
    // =============================================================================
    
    // Make functions globally available for HTML onclick handlers
    window.createNewSwarm = createNewSwarm;
    window.explodeSwarm = explodeSwarm;
    window.implodeSwarm = implodeSwarm;
    window.spiralFormation = spiralFormation;
    window.sphereFormation = sphereFormation;
    window.waveFormation = waveFormation;
    window.textFormation = textFormation;
    window.setLevel = setLevel;
    window.changeTheme = changeTheme;
    window.morphText = morphText;
    
    // =============================================================================
    // START
    // =============================================================================
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();

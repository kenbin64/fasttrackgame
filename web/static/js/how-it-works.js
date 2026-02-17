/**
 * ButterflyFX - "How It Works" Persistent Toggle Component
 * Include this script on any page to add the "How It Works" overlay button.
 * 
 * Usage: Add to any page:
 *   <link rel="stylesheet" href="static/css/how-it-works.css">
 *   <script src="static/js/how-it-works.js"></script>
 */

(function() {
    'use strict';
    
    // Check if already initialized
    if (window.hiwInitialized) return;
    window.hiwInitialized = true;
    
    // CSS Variables (inherit from page or use defaults)
    const colors = {
        neonPurple: '#8855ff',
        neonPink: '#ff55aa',
        neonCyan: '#40ffff',
        neonGreen: '#60ff90',
        bg: '#050508',
        bgCard: 'rgba(18, 18, 28, 0.85)',
        text: '#ffffff',
        textDim: '#a0a8c0',
        border: 'rgba(136, 85, 255, 0.3)'
    };
    
    // Inject styles
    const style = document.createElement('style');
    style.textContent = `
        /* How It Works Toggle Button */
        #hiw-toggle {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 9000;
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 14px 24px;
            background: linear-gradient(135deg, ${colors.neonCyan}, ${colors.neonPurple});
            border: none;
            border-radius: 30px;
            color: white;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 5px 30px rgba(64, 255, 255, 0.3);
            transition: all 0.3s;
            font-family: inherit;
        }
        
        #hiw-toggle:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 40px rgba(64, 255, 255, 0.4);
        }
        
        #hiw-toggle .hiw-icon {
            font-size: 1.3em;
        }
        
        /* How It Works Overlay */
        #hiw-overlay {
            position: fixed;
            inset: 0;
            z-index: 9100;
            background: rgba(5, 5, 8, 0.95);
            backdrop-filter: blur(20px);
            opacity: 0;
            visibility: hidden;
            transition: all 0.4s;
            overflow-y: auto;
        }
        
        #hiw-overlay.hiw-open {
            opacity: 1;
            visibility: visible;
        }
        
        .hiw-close-btn {
            position: fixed;
            top: 25px;
            right: 30px;
            z-index: 9110;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: 2px solid ${colors.border};
            background: ${colors.bgCard};
            color: ${colors.text};
            font-size: 1.5em;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }
        
        .hiw-close-btn:hover {
            border-color: ${colors.neonPink};
            box-shadow: 0 0 20px rgba(255, 85, 170, 0.3);
        }
        
        .hiw-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 80px 40px;
        }
        
        .hiw-header {
            text-align: center;
            margin-bottom: 60px;
        }
        
        .hiw-header h2 {
            font-size: 2.5em;
            margin-bottom: 15px;
            background: linear-gradient(135deg, ${colors.neonCyan}, ${colors.neonGreen});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .hiw-header p {
            font-size: 1.2em;
            color: ${colors.textDim};
        }
        
        /* Tabs */
        .hiw-tabs {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 40px;
        }
        
        .hiw-tab-btn {
            padding: 12px 25px;
            background: transparent;
            border: 2px solid ${colors.border};
            border-radius: 25px;
            color: ${colors.textDim};
            font-size: 0.95em;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }
        
        .hiw-tab-btn:hover {
            border-color: ${colors.neonPurple};
            color: ${colors.text};
        }
        
        .hiw-tab-btn.hiw-active {
            background: linear-gradient(135deg, ${colors.neonPurple}, ${colors.neonPink});
            border-color: transparent;
            color: white;
        }
        
        /* Section Panels */
        .hiw-section {
            display: none;
            animation: hiwFadeIn 0.4s;
        }
        
        .hiw-section.hiw-active {
            display: block;
        }
        
        @keyframes hiwFadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .hiw-section h3 {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: ${colors.neonCyan};
        }
        
        .hiw-section > p {
            color: ${colors.textDim};
            line-height: 1.7;
            font-size: 1.1em;
            margin-bottom: 10px;
        }
        
        .hiw-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }
        
        .hiw-card {
            background: ${colors.bgCard};
            border: 1px solid ${colors.border};
            border-radius: 16px;
            padding: 25px;
            transition: all 0.3s;
        }
        
        .hiw-card:hover {
            border-color: ${colors.neonPurple};
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(136, 85, 255, 0.2);
        }
        
        .hiw-card .hiw-card-icon {
            font-size: 2.5em;
            margin-bottom: 15px;
            display: block;
        }
        
        .hiw-card h4 {
            font-size: 1.2em;
            margin-bottom: 10px;
            color: ${colors.text};
        }
        
        .hiw-card p {
            color: ${colors.textDim};
            line-height: 1.6;
            font-size: 0.95em;
        }
        
        .hiw-card a {
            display: inline-block;
            margin-top: 15px;
            color: ${colors.neonCyan};
            text-decoration: none;
            font-size: 0.9em;
        }
        
        .hiw-card a:hover { text-decoration: underline; }
        
        /* Quick Links */
        .hiw-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid ${colors.border};
        }
        
        .hiw-links a {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 25px;
            background: rgba(136, 85, 255, 0.1);
            border: 1px solid ${colors.border};
            border-radius: 25px;
            color: ${colors.text};
            text-decoration: none;
            transition: all 0.3s;
        }
        
        .hiw-links a:hover {
            background: ${colors.neonPurple};
            border-color: ${colors.neonPurple};
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            #hiw-toggle {
                bottom: 20px;
                right: 20px;
                padding: 12px 20px;
                font-size: 0.9em;
            }
            
            .hiw-container {
                padding: 60px 20px;
            }
            
            .hiw-header h2 {
                font-size: 1.8em;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Create HTML structure
    const html = `
        <button id="hiw-toggle">
            <span class="hiw-icon">◇</span>
            <span>How It Works</span>
        </button>
        
        <div id="hiw-overlay">
            <button class="hiw-close-btn">✕</button>
            <div class="hiw-container">
                <div class="hiw-header">
                    <h2>How Dimensional Computing Works</h2>
                    <p>Shapes hold data. Dimensions hold meaning. Objects exist complete.</p>
                </div>
                
                <div class="hiw-tabs">
                    <button class="hiw-tab-btn hiw-active" data-section="substrate">🌊 Substrate</button>
                    <button class="hiw-tab-btn" data-section="manifold">◇ Manifold</button>
                    <button class="hiw-tab-btn" data-section="dimensions">📐 Dimensions</button>
                    <button class="hiw-tab-btn" data-section="kernel">⚙️ Kernel</button>
                </div>
                
                <!-- Substrate Section -->
                <div class="hiw-section hiw-active" id="hiw-substrate">
                    <h3>The Substrate — Mathematical Foundation</h3>
                    <p>Before objects exist, there is the <strong>substrate</strong> — a pure mathematical geometry (like z = xy) that contains all possible values. Objects are not built — they are <em>ingested</em> from the substrate.</p>
                    
                    <div class="hiw-grid">
                        <div class="hiw-card">
                            <span class="hiw-card-icon">🌐</span>
                            <h4>Substrate2D</h4>
                            <p>A 2D coordinate space where x and y combine to produce any value. Colors, sounds, positions — all derived from the same geometry.</p>
                            <a href="docs/substrate.html">Learn more →</a>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">🔮</span>
                            <h4>Value Ingestion</h4>
                            <p>Instead of constructing data, we ingest it from the substrate. Point at coordinates, get the value instantly. O(1) access.</p>
                            <a href="docs/ingestion.html">Learn more →</a>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">🎨</span>
                            <h4>Multiple Lenses</h4>
                            <p>Same geometry, different interpretations. Apply a "color lens" for HSL, a "sound lens" for frequencies, a "value lens" for raw data.</p>
                            <a href="docs/lenses.html">Learn more →</a>
                        </div>
                    </div>
                </div>
                
                <!-- Manifold Section -->
                <div class="hiw-section" id="hiw-manifold">
                    <h3>The Manifold — Shape-Based Computing</h3>
                    <p>The <strong>manifold</strong> is where shapes become data structures. Every geometric form — points, lines, surfaces, volumes — maps directly to computational patterns.</p>
                    
                    <div class="hiw-grid">
                        <div class="hiw-card">
                            <span class="hiw-card-icon">◇</span>
                            <h4>Geometric Data</h4>
                            <p>A line isn't just geometry — it's a range query. A surface is a 2D lookup table. A volume is a 3D database. Shape IS data.</p>
                            <a href="docs/manifold-shapes.html">Learn more →</a>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">⚡</span>
                            <h4>O(1) Access</h4>
                            <p>No iteration, no searching. Calculate the coordinate, get the value. 10x-1000x faster than traditional data structures.</p>
                            <a href="benchmarks.html">View benchmarks →</a>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">🔗</span>
                            <h4>Manifold Linking</h4>
                            <p>Manifolds connect to each other. One shape flows into another, creating complex data pipelines without explicit wiring.</p>
                            <a href="docs/manifold-linking.html">Learn more →</a>
                        </div>
                    </div>
                </div>
                
                <!-- Dimensions Section -->
                <div class="hiw-section" id="hiw-dimensions">
                    <h3>Dimensions — From Void to Whole</h3>
                    <p>There are 7 dimensional levels (0-6). Each level adds complexity and context, from pure potential to complete systems.</p>
                    
                    <div class="hiw-grid">
                        <div class="hiw-card">
                            <span class="hiw-card-icon">∅</span>
                            <h4>0D — Void (Potential)</h4>
                            <p>All values exist but nothing is manifested. Pure possibility before context is applied.</p>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">•</span>
                            <h4>1D — Point (Identity)</h4>
                            <p>A single value chosen. The moment of decision — one point in infinite space.</p>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">―</span>
                            <h4>2D — Line (Range)</h4>
                            <p>Connection between points. Gradients, transitions, continuous values along a path.</p>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">⌓</span>
                            <h4>3D — Surface (Field)</h4>
                            <p>Two-dimensional lookup. The saddle surface z=xy where all combinations exist.</p>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">◇</span>
                            <h4>4D — Volume (Body)</h4>
                            <p>Three-dimensional space. Objects with interior properties, not just surfaces.</p>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">◎</span>
                            <h4>5D-6D — Network & Whole</h4>
                            <p>Multiple objects connected. Complete systems where everything relates to everything.</p>
                        </div>
                    </div>
                    
                    <p style="margin-top: 30px; text-align: center;">
                        <a href="genesis.html" style="color: ${colors.neonCyan};">Read the full Genesis document →</a>
                    </p>
                </div>
                
                <!-- Kernel Section -->
                <div class="hiw-section" id="hiw-kernel">
                    <h3>The Kernel — Core Engine</h3>
                    <p>The <strong>kernel</strong> orchestrates substrates, manifolds, and dimensional transformations. It's the runtime that makes dimensional computing work.</p>
                    
                    <div class="hiw-grid">
                        <div class="hiw-card">
                            <span class="hiw-card-icon">⚙️</span>
                            <h4>Helix Kernel</h4>
                            <p>The Python implementation. Defines primitives, handles transformations, manages dimensional state.</p>
                            <a href="developer.html">Developer docs →</a>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">🧬</span>
                            <h4>Primitives</h4>
                            <p>7 core primitives (INT, REAL, ...) that all data types reduce to. Everything composes from these atoms.</p>
                            <a href="docs/primitives.html">Learn primitives →</a>
                        </div>
                        <div class="hiw-card">
                            <span class="hiw-card-icon">📦</span>
                            <h4>Packages</h4>
                            <p>Pre-built dimensional modules: Graphics, Audio, Finance, AI connectors. Import and use immediately.</p>
                            <a href="docs/packages.html">Browse packages →</a>
                        </div>
                    </div>
                </div>
                
                <!-- Quick Links -->
                <div class="hiw-links">
                    <a href="start-here.html">🚀 Start Here</a>
                    <a href="genesis.html">⚖️ Genesis</a>
                    <a href="platform.html">🧬 Platform</a>
                    <a href="developer.html">👨‍💻 Developers</a>
                    <a href="benchmarks.html">📊 Benchmarks</a>
                    <a href="documents.html">📚 All Docs</a>
                </div>
            </div>
        </div>
    `;
    
    // Insert HTML
    const container = document.createElement('div');
    container.innerHTML = html;
    document.body.appendChild(container);
    
    // Event handlers
    const toggle = document.getElementById('hiw-toggle');
    const overlay = document.getElementById('hiw-overlay');
    const closeBtn = document.querySelector('.hiw-close-btn');
    const tabs = document.querySelectorAll('.hiw-tab-btn');
    
    function openOverlay() {
        overlay.classList.add('hiw-open');
        document.body.style.overflow = 'hidden';
    }
    
    function closeOverlay() {
        overlay.classList.remove('hiw-open');
        document.body.style.overflow = '';
    }
    
    toggle.addEventListener('click', openOverlay);
    closeBtn.addEventListener('click', closeOverlay);
    
    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const section = tab.dataset.section;
            
            // Update tabs
            tabs.forEach(t => t.classList.remove('hiw-active'));
            tab.classList.add('hiw-active');
            
            // Update sections
            document.querySelectorAll('.hiw-section').forEach(s => s.classList.remove('hiw-active'));
            document.getElementById(`hiw-${section}`).classList.add('hiw-active');
        });
    });
    
    // Close with Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.classList.contains('hiw-open')) {
            closeOverlay();
        }
    });
    
    // Close when clicking outside content
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeOverlay();
        }
    });
    
    console.log('ButterflyFX "How It Works" component initialized.');
})();

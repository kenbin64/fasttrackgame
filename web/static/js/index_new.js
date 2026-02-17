// ===== BACKGROUND CANVAS =====
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // Animated background
        let time = 0;
        function drawBackground() {
            ctx.fillStyle = 'rgba(6, 6, 16, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            
            // Draw subtle helix in background
            ctx.strokeStyle = 'rgba(64, 96, 255, 0.08)';
            ctx.lineWidth = 1;
            
            for (let i = 0; i < 200; i++) {
                const t = (i / 200) * Math.PI * 6 + time * 0.2;
                const r = 100 + i * 1.5;
                const x = cx + Math.cos(t) * r * 0.8;
                const y = cy + Math.sin(t) * r * 0.3 + (i - 100) * 1.5;
                
                if (i === 0) {
                    ctx.beginPath();
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
            
            time += 0.01;
            requestAnimationFrame(drawBackground);
        }
        drawBackground();
        
        // ===== LEVEL EXPLANATIONS =====
        const levelData = {
            0: {
                title: "Level 0: The Void",
                color: "#888",
                text: `<strong>Pure potential.</strong> Before any structure exists, there is possibility. 
                    The void is not "nothing" — it's the space where dimensions can emerge. In computing terms: 
                    this is the unallocated memory, the blank canvas, the clean slate before initialization.
                    Even the void is a dimension — the dimension of potential.`
            },
            1: {
                title: "Level 1: The Point",
                color: "#ff6464",
                text: `<strong>A dimension emerges.</strong> The first act of creation: declaring that 
                    something exists. A point has no extent but it has <em>position</em>. In computing: 
                    a single value, a variable, an atom of data. The point IS the value — there is no 
                    separation between the location and what's located there.`
            },
            2: {
                title: "Level 2: The Line",
                color: "#ffaa44",
                text: `<strong>Points form sequence.</strong> Connect two points and you have extent. 
                    Now there are infinite points between them — the line contains continuous values.
                    In computing: an array, a string, a buffer. Each element is a point within the 
                    line's dimension. The line IS its points.`
            },
            3: {
                title: "Level 3: The Plane",
                color: "#44dd44",
                text: `<strong>Lines form surface.</strong> Stack infinite lines and you get a plane — 
                    2D extent. Now every point has (x, y) coordinates. In computing: a table, a 2D array, 
                    an image. Each row is a line, each cell is a point. The plane doesn't "contain" 
                    the data — the plane IS the data at this resolution.`
            },
            4: {
                title: "Level 4: The Volume",
                color: "#44aaff",
                text: `<strong>Surfaces form space.</strong> Stack infinite planes and you get volume — 
                    3D extent with (x, y, z). In computing: a database, a voxel space, a 3D tensor. 
                    Each z-slice is a plane, each plane is lines, each line is points. The dimensional 
                    helix shows the same structure at different resolutions.`
            },
            5: {
                title: "Level 5: The Network",
                color: "#aa66ff",
                text: `<strong>Systems connect.</strong> Volumes connect to other volumes across the 4th 
                    dimension. Now we have time, or connection, or relationship. IP addresses become 
                    4D coordinates: D(x, y, z, m). In computing: a distributed system, a mesh network, 
                    interconnected nodes. Each connection is a dimension linking dimensions.`
            },
            6: {
                title: "Level 6: The Internet",
                color: "#ff66aa",
                text: `<strong>Networks unify.</strong> All networks are one network — the global manifold. 
                    Every device has coordinates. Routing is navigation. Topology is geometry. In computing: 
                    the entire addressable space of connected systems. The internet IS a high-dimensional 
                    geometric object. We're just learning to see its shape.`
            }
        };
        
        const levelCards = document.querySelectorAll('.level-card');
        const levelTitle = document.getElementById('level-title');
        const levelText = document.getElementById('level-text');
        
        levelCards.forEach(card => {
            card.addEventListener('click', () => {
                const level = parseInt(card.dataset.level);
                const data = levelData[level];
                
                // Update active state
                levelCards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                
                // Update explanation
                levelTitle.style.color = data.color;
                levelTitle.textContent = data.title;
                levelText.innerHTML = data.text;
            });
        });
        
        // ===== DETECT USER IP =====
        async function detectIP() {
            try {
                // Try the server's dimensional API first
                const resp = await fetch('/api/dimensional/encode?ip=detect');
                if (resp.ok) {
                    const data = await resp.json();
                    if (data.original_ip) {
                        document.getElementById('your-ip').textContent = data.original_ip;
                        if (data.coordinates) {
                            const c = data.coordinates;
                            document.getElementById('your-coords').textContent = 
                                `(${c.x}, ${c.y}, ${c.z}, ${c.m})`;
                        }
                        return;
                    }
                }
            } catch (e) {}
            
            // Fallback: use external service
            try {
                const resp = await fetch('https://api.ipify.org?format=json');
                const data = await resp.json();
                const ip = data.ip;
                document.getElementById('your-ip').textContent = ip;
                
                // Parse IP to coordinates
                const parts = ip.split('.');
                if (parts.length === 4) {
                    document.getElementById('your-coords').textContent = 
                        `(${parts[0]}, ${parts[1]}, ${parts[2]}, ${parts[3]})`;
                }
            } catch (e) {
                document.getElementById('your-ip').textContent = 'unavailable';
                document.getElementById('your-coords').textContent = '(?, ?, ?, ?)';
            }
        }
        detectIP();
        
        // ===== LOAD BENCHMARKS =====
        async function loadBenchmarks() {
            try {
                const resp = await fetch('/api/dimensional/benchmark');
                if (resp.ok) {
                    const data = await resp.json();
                    if (data.results) {
                        const r = data.results;
                        if (r.encode_decode) {
                            const us = (r.encode_decode.encode_avg_us || 2.3).toFixed(1);
                            document.getElementById('bench-encode').textContent = `${us} μs`;
                        }
                        if (r.substrate) {
                            const deriveNs = r.substrate.derive_avg_ns || 800;
                            document.getElementById('bench-derive').textContent = 
                                `${(deriveNs / 1000).toFixed(1)} μs`;
                        }
                    }
                }
            } catch (e) {}
        }
        loadBenchmarks();
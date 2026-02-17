// ===== HAMBURGER MENU =====
        const hamburger = document.getElementById('hamburger');
        const mainNav = document.getElementById('mainNav');
        const navOverlay = document.getElementById('navOverlay');
        
        function toggleNav() {
            hamburger.classList.toggle('active');
            mainNav.classList.toggle('open');
            navOverlay.classList.toggle('open');
        }
        
        hamburger.addEventListener('click', toggleNav);
        navOverlay.addEventListener('click', toggleNav);
        
        // Close nav when clicking a link
        mainNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                if (mainNav.classList.contains('open')) {
                    toggleNav();
                }
            });
        });
        
        // ===== 3D STARFIELD =====
        const starfieldCanvas = document.getElementById('starfield');
        const ctx = starfieldCanvas.getContext('2d');
        
        function resize() {
            starfieldCanvas.width = window.innerWidth;
            starfieldCanvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);
        
        const stars = [];
        const STAR_COUNT = 400;
        const STAR_SPEED = 2;
        const MAX_DEPTH = 1500;
        
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
            
            ctx.fillStyle = 'rgba(5, 5, 16, 0.3)';
            ctx.fillRect(0, 0, w, h);
            
            for (let star of stars) {
                star.z -= STAR_SPEED;
                
                if (star.z <= 0) {
                    star.x = (Math.random() - 0.5) * 2000;
                    star.y = (Math.random() - 0.5) * 2000;
                    star.z = MAX_DEPTH;
                }
                
                const fov = 300;
                const scale = fov / star.z;
                const sx = star.x * scale + cx;
                const sy = star.y * scale + cy;
                
                if (sx < 0 || sx > w || sy < 0 || sy > h) continue;
                
                const depth = 1 - star.z / MAX_DEPTH;
                const size = star.size * scale * 0.5;
                const alpha = depth * 0.8 + 0.2;
                
                const brightness = Math.floor(200 + depth * 55);
                ctx.fillStyle = `rgba(${brightness}, ${brightness + 10}, 255, ${alpha})`;
                
                ctx.beginPath();
                ctx.arc(sx, sy, Math.max(0.5, size), 0, Math.PI * 2);
                ctx.fill();
                
                if (depth > 0.7 && size > 1) {
                    const prevScale = fov / (star.z + STAR_SPEED * 3);
                    const prevX = star.x * prevScale + cx;
                    const prevY = star.y * prevScale + cy;
                    
                    ctx.strokeStyle = `rgba(${brightness}, ${brightness + 10}, 255, ${alpha * 0.5})`;
                    ctx.lineWidth = size * 0.5;
                    ctx.beginPath();
                    ctx.moveTo(prevX, prevY);
                    ctx.lineTo(sx, sy);
                    ctx.stroke();
                }
            }
        }
        
        function animate() {
            drawStarfield();
            requestAnimationFrame(animate);
        }
        animate();
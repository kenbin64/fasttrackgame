/**
 * BUTTERFLYFX LANDING PAGE - INTERACTIVE FEATURES
 * Cyberpunk theme with smooth animations
 */

// ========== SMOOTH SCROLLING ==========
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ========== COPY TO CLIPBOARD ==========
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', function() {
            const codeBlock = this.previousElementSibling || this.parentElement.querySelector('code');
            const textToCopy = codeBlock ? codeBlock.textContent : '';
            
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                this.style.background = '#39ff14';
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.background = '';
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy:', err);
                this.textContent = 'Failed';
                setTimeout(() => {
                    this.textContent = 'Copy';
                }, 2000);
            });
        });
    });

    // ========== MOBILE MENU TOGGLE ==========
    const createMobileMenu = () => {
        const nav = document.querySelector('.nav-container');
        if (!nav) return;

        // Check if we're on mobile
        if (window.innerWidth <= 768) {
            const navLinks = document.querySelector('.nav-links');
            if (!navLinks) return;

            // Create hamburger button if it doesn't exist
            let hamburger = document.querySelector('.hamburger');
            if (!hamburger) {
                hamburger = document.createElement('button');
                hamburger.className = 'hamburger';
                hamburger.innerHTML = '☰';
                hamburger.style.cssText = `
                    background: transparent;
                    border: 2px solid var(--cyber-cyan);
                    color: var(--cyber-cyan);
                    font-size: 1.5rem;
                    padding: 0.5rem 1rem;
                    cursor: pointer;
                    border-radius: 8px;
                    transition: all 0.3s ease;
                `;
                nav.insertBefore(hamburger, navLinks);

                hamburger.addEventListener('click', () => {
                    navLinks.classList.toggle('active');
                    hamburger.innerHTML = navLinks.classList.contains('active') ? '✕' : '☰';
                });
            }
        }
    };

    createMobileMenu();
    window.addEventListener('resize', createMobileMenu);

    // ========== SCROLL ANIMATIONS ==========
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all sections and cards
    document.querySelectorAll('section, .feature, .product-card, .use-case, .pricing-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // ========== PARALLAX STARFIELD ==========
    let mouseX = 0;
    let mouseY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX / window.innerWidth) * 100;
        mouseY = (e.clientY / window.innerHeight) * 100;
        
        const starfield = document.querySelector('body::before');
        if (starfield) {
            document.body.style.setProperty('--mouse-x', `${mouseX}%`);
            document.body.style.setProperty('--mouse-y', `${mouseY}%`);
        }
    });

    // ========== GLITCH EFFECT ON HOVER ==========
    document.querySelectorAll('.gradient-text').forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.animation = 'glitch 0.3s ease';
        });
        
        element.addEventListener('animationend', function() {
            this.style.animation = 'gradientShift 5s ease infinite';
        });
    });

    // ========== CYBER GRID BACKGROUND ==========
    const createCyberGrid = () => {
        const grid = document.createElement('div');
        grid.className = 'cyber-grid';
        grid.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(176, 38, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: -1;
        `;
        document.body.appendChild(grid);
    };

    createCyberGrid();

    // ========== TYPING EFFECT FOR CODE EXAMPLES ==========
    const typeCode = (element, code, speed = 50) => {
        let i = 0;
        element.textContent = '';
        
        const type = () => {
            if (i < code.length) {
                element.textContent += code.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        };
        
        type();
    };

    // Observe code blocks and trigger typing when visible
    const codeObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.typed) {
                const code = entry.target.textContent;
                entry.target.dataset.typed = 'true';
                typeCode(entry.target, code, 10);
            }
        });
    }, { threshold: 0.5 });

    // Uncomment to enable typing effect (can be slow for large code blocks)
    // document.querySelectorAll('.code-content code').forEach(el => {
    //     codeObserver.observe(el);
    // });
});

// ========== ADD GLITCH ANIMATION TO CSS ==========
const style = document.createElement('style');
style.textContent = `
    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
        100% { transform: translate(0); }
    }
    
    .nav-links.active {
        display: flex !important;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--panel-bg);
        backdrop-filter: blur(10px);
        border: 2px solid var(--cyber-cyan);
        padding: 1rem;
        z-index: 1000;
    }
`;
document.head.appendChild(style);


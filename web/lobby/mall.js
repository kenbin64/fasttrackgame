/* Ken's Arcade Mall interactions (local-only) */
(function(){
  'use strict';

  // Basic user chip init from query (?user=Name) or sessionStorage
  function initUserChip(){
    const params = new URLSearchParams(location.search);
    const fromQuery = params.get('user');
    const stored = sessionStorage.getItem('kg_user');
    const name = fromQuery || stored || 'Guest';
    if(fromQuery){ sessionStorage.setItem('kg_user', fromQuery); }
    const chip = document.getElementById('userChip');
    if(chip){ chip.innerHTML = 'Signed in as <strong>' + name.replace(/</g,'&lt;') + '</strong>'; }
  }

  function navigate(href){
    if(!href) return;
    // Preserve user param if set
    const params = new URLSearchParams(location.search);
    const user = params.get('user') || sessionStorage.getItem('kg_user');
    if(user){
      const url = new URL(href, location.origin);
      url.searchParams.set('user', user);
      location.href = url.toString();
    } else {
      location.href = href;
    }
  }

  function bindCabinets(){
    document.querySelectorAll('.cabinet').forEach(el => {
      const href = el.getAttribute('data-target');
      el.addEventListener('click', () => navigate(href));
      el.addEventListener('keypress', (e) => { if(e.key === 'Enter') navigate(href); });
    });
    document.querySelectorAll('.enter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => { e.stopPropagation(); navigate(btn.getAttribute('data-href')); });
    });
  }

  // Optional: subtle parallax on mouse move
  function enableParallax(){
    const root = document.querySelector('.cabinets');
    if(!root) return;
    root.addEventListener('mousemove', (e) => {
      document.querySelectorAll('.cabinet').forEach(card => {
        const r = card.getBoundingClientRect();
        const cx = r.left + r.width/2;
        const cy = r.top + r.height/2;
        const dx = (e.clientX - cx) / r.width;
        const dy = (e.clientY - cy) / r.height;
        const rx = Math.max(-6, Math.min(6, dy * 8));
        const ry = Math.max(-6, Math.min(6, -dx * 8));
        card.style.transform = `perspective(1200px) rotateX(${rx}deg) rotateY(${ry}deg)`;
      });
    });
    root.addEventListener('mouseleave', () => {
      document.querySelectorAll('.cabinet').forEach(card => {
        card.style.transform = 'perspective(1200px) rotateX(0) rotateY(0)';
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initUserChip();
    bindCabinets();
    enableParallax();
  });
})();

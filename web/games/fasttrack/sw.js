/**
 * Fast Track PWA Service Worker
 * NETWORK-FIRST for everything — cache is ONLY an offline fallback
 */

const CACHE_NAME = 'fasttrack-v3.0.0';
const PRECACHE_URLS = [
  '/fasttrack/board_3d.html',
  '/fasttrack/assets/images/ftLogo.png',
  '/fasttrack/assets/images/icon-192.png',
  '/fasttrack/assets/images/icon-512.png',
  '/fasttrack/manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'
];

// Install — precache a small shell, then take over immediately
self.addEventListener('install', (event) => {
  console.log('[SW] Install v3 — network-first');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS.filter(u => !u.startsWith('http'))))
      .then(() => self.skipWaiting())
  );
});

// Activate — purge ALL old caches, claim clients immediately
self.addEventListener('activate', (event) => {
  console.log('[SW] Activate v3');
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.filter(n => n !== CACHE_NAME).map(n => {
        console.log('[SW] Purging old cache:', n);
        return caches.delete(n);
      }))
    ).then(() => self.clients.claim())
  );
});

// Fetch — ALWAYS try network first, cache result, fall back to cache only when offline
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  if (event.request.url.includes('/ws')) return;

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            const url = event.request.url;
            if (url.startsWith(self.location.origin) ||
                url.includes('cdnjs.cloudflare.com') ||
                url.includes('cdn.jsdelivr.net')) {
              cache.put(event.request, clone);
            }
          });
        }
        return networkResponse;
      })
      .catch(() =>
        caches.match(event.request)
          .then((cached) => cached || caches.match('/fasttrack/board_3d.html'))
      )
  );
});

// Background sync for game state (if supported)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-game-state') {
    console.log('[ServiceWorker] Syncing game state');
    // Could sync saved game state when back online
  }
});

// Push notifications for multiplayer
self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body || 'Your turn!',
    icon: '/fasttrack/assets/images/icon-192.png',
    badge: '/fasttrack/assets/images/icon-72.png',
    vibrate: [200, 100, 200],
    data: { url: data.url || '/fasttrack/mobile.html' },
    actions: [
      { action: 'play', title: 'Play Now', icon: '/fasttrack/assets/images/icon-72.png' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title || 'Fast Track', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  const url = event.notification.data?.url || '/fasttrack/mobile.html';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // Focus existing window if open
        for (const client of windowClients) {
          if (client.url.includes('/fasttrack/') && 'focus' in client) {
            return client.focus();
          }
        }
        // Open new window
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});

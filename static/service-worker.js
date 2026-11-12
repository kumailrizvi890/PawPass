// Service Worker for PawPass PWA


const CACHE_NAME = 'pawpass-v2';
const ASSETS_TO_CACHE = [
  '/',
  '/home',
  '/pets',
  '/add-pet',
  '/static/css/style.css',
  '/static/css/color-blind.css',
  '/static/css/pawpass-redesign.css',
  '/static/js/script.js',
  '/static/js/pawpass-pass.js',
  '/static/images/pawpass-logo.png',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/static/icons/maskable-icon-192x192.png',
  '/static/icons/maskable-icon-512x512.png',
  '/static/manifest.json'
];

// Install event - Cache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(ASSETS_TO_CACHE);
      })
  );
});

// Activate event - Clean up old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - Serve cached content when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request).then(
          response => {
            // Return the response as-is for non-GET requests or if status is not 200
            if(!response || response.status !== 200 || event.request.method !== 'GET') {
              return response;
            }
            // Clone the response as it can only be used once
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
            return response;
          }
        );
      })
    );
});

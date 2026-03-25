const CACHE_VERSION = 'insideredge-v5';
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const DATA_CACHE    = `${CACHE_VERSION}-data`;

// Static assets — cache on install, serve from cache first
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/canada.html',
  '/performance.html',
  '/congress.html',
  '/style.css',
];

// Data files — stale-while-revalidate (serve cache instantly, refresh in background)
const DATA_URLS = [
  '/data/latest.json',
  '/data/canada_latest.json',
  '/data/performance.json',
  '/data/trades.json',
];

// ----------------------------------------------------------------
// Install — pre-cache static assets
// ----------------------------------------------------------------
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// ----------------------------------------------------------------
// Activate — clean up old caches
// ----------------------------------------------------------------
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key.startsWith('insideredge-') && key !== STATIC_CACHE && key !== DATA_CACHE)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// ----------------------------------------------------------------
// Fetch — strategy depends on request type
// ----------------------------------------------------------------
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Skip non-GET and cross-origin (except Google Fonts)
  if (event.request.method !== 'GET') return;
  const isGoogleFonts = url.hostname.includes('fonts.googleapis.com') ||
                        url.hostname.includes('fonts.gstatic.com');
  if (!isGoogleFonts && url.origin !== self.location.origin) return;

  // Data files — stale-while-revalidate (strip cache-busting query params)
  if (DATA_URLS.some(u => url.pathname.endsWith(u)) || url.pathname.includes('/data/')) {
    const cleanRequest = new Request(url.origin + url.pathname);
    event.respondWith(staleWhileRevalidate(cleanRequest, DATA_CACHE));
    return;
  }

  // Google Fonts — cache first
  if (isGoogleFonts) {
    event.respondWith(cacheFirst(event.request, STATIC_CACHE));
    return;
  }

  // Static assets — cache first, fallback to network
  event.respondWith(cacheFirst(event.request, STATIC_CACHE));
});

// ----------------------------------------------------------------
// Strategies
// ----------------------------------------------------------------

// Serve from cache, update cache in background
function staleWhileRevalidate(request, cacheName) {
  return caches.open(cacheName).then(cache =>
    cache.match(request).then(cached => {
      const networkFetch = fetch(request).then(response => {
        if (response.ok) cache.put(request, response.clone());
        return response;
      }).catch(() => null);

      return cached || networkFetch;
    })
  );
}

// Serve from cache, only hit network on miss
function cacheFirst(request, cacheName) {
  return caches.open(cacheName).then(cache =>
    cache.match(request).then(cached => {
      if (cached) return cached;
      return fetch(request).then(response => {
        if (response.ok) cache.put(request, response.clone());
        return response;
      });
    })
  );
}

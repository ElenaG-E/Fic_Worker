// Nombre de la caché
const CACHE_NAME = 'fic-writer-pro-v1';

// Archivos para guardar en caché
const urlsToCache = [
  '/',
  'index.html' // Asegúrate que tu archivo HTML se llame así
];

// Instalar el Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache abierto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Interceptar peticiones de red
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Si está en caché, lo devuelve. Si no, va a la red.
        return response || fetch(event.request);
      })
  );
});

// Nombre de la caché
const CACHE_NAME = 'fic-writer-pro-v1';

// ESTA LÍNEA ES LA MÁS IMPORTANTE
// Está configurada para un repositorio llamado "fic-writer-app"
const REPO_PREFIX = '/fic-writer-app/';

// Archivos para guardar en caché (ahora con el prefijo)
const urlsToCache = [
  REPO_PREFIX,
  REPO_PREFIX + 'index.html',
  REPO_PREFIX + 'manifest.json'
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

// Limpiar cachés antiguas
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME).map(name => caches.delete(name))
      );
    })
  );
});

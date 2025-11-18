// Nombre de la caché
const CACHE_NAME = 'fic-writer-pro-v2'; // Cambiado a v2 para forzar la actualización de caché

// **¡AJUSTA ESTA LÍNEA SI TU REPOSITORIO NO SE LLAMA 'fic-writer-app'!**
const REPO_PREFIX = '/'; // Cambiado a root para evitar problemas de cache

// Archivos principales a guardar en caché (solo recursos estáticos, no index.html para evitar problemas de actualización)
const urlsToCache = [
  REPO_PREFIX + 'manifest.json'
];

// Instalar el Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache abierto:', CACHE_NAME);
        return cache.addAll(urlsToCache);
      })
      .catch(error => console.error('Fallo al precachear archivos:', error))
  );
});

// Limpiar cachés antiguas (Esto forzará la actualización)
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('Eliminando caché antigua:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Interceptar peticiones de red
self.addEventListener('fetch', event => {
  // Solo interceptamos peticiones dentro de nuestro scope
  if (event.request.url.startsWith(self.location.origin)) {
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          // Devolver desde caché, o ir a la red si no se encuentra
          return response || fetch(event.request);
        })
    );
  }
});

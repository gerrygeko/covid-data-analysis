var CACHE_NAME = 'offline-coronavirus-data';
var urlsToCache = [
  '/assets/styles.css',
  '/assets/s1.css',
  '/assets/register-sw.js'
];
self.addEventListener('install', function(event) {
  // install files needed offline
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

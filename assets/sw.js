console.log('Hello from sw.js');


// importScript is a function related to the modern browser, so we need to check this snip as
// out-of-box call from service worker scope. Otherwise, the sw context does not accept it
//Ref: https://developer.mozilla.org/en-US/docs/Web/API/WorkerGlobalScope/importScripts

if( 'function' === typeof importScripts) {
    importScripts('https://storage.googleapis.com/workbox-cdn/releases/3.2.0/workbox-sw.js');
}

//This can be used to detect whether code is running in a typical browser environment
//(e.g. an environment with a browser DOM) or in some other JS environment since the window
//object exists in a typical browser JS, but does not exist in something like a webWorker in a browser.
//Ref: https://stackoverflow.com/questions/32598971/whats-the-purpose-of-if-typeof-window-undefined

if( 'undefined' === typeof window){
    if (workbox) {
      console.log('Yay! Workbox is loaded');

      workbox.precaching.precacheAndRoute([
        {
          "url": "/",
          "revision": "1"
        }
      ]);

      workbox.routing.registerRoute(
        /\.(?:js|css)$/,
        workbox.strategies.staleWhileRevalidate({
          cacheName: 'static-resources',
        }),
      );

      workbox.routing.registerRoute(
        /\.(?:png|gif|jpg|jpeg|svg)$/,
        workbox.strategies.cacheFirst({
          cacheName: 'images',
          plugins: [
            new workbox.expiration.Plugin({
              maxEntries: 60,
              maxAgeSeconds: 30 * 24 * 60 * 60, // 30 Days
            }),
          ],
        }),
      );

      workbox.routing.registerRoute(
        new RegExp('https://fonts.(?:googleapis|gstatic).com/(.*)'),
        workbox.strategies.cacheFirst({
          cacheName: 'googleapis',
          plugins: [
            new workbox.expiration.Plugin({
              maxEntries: 30,
            }),
          ],
        }),
      );
    } else {
      console.log('Boo! Workbox did not load');
    }
}
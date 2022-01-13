if ('serviceWorker' in navigator) {
   // we are checking here to see if the browser supports the  service worker api
window.addEventListener('load', function() {
    navigator.serviceWorker.register('/assets/sw.js', {scope: '/'}).then(function(registration) {
      // Registration was successful
      console.log('Service Worker registration was successful with scope: ', registration.scope);
    }, function(err) {
      // registration failed :(
      console.log('ServiceWorker registration failed: ', err);
    });
  });
}
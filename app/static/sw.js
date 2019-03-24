self.addEventListener('install', function(event) {
    // инсталляция
    console.log('install', event);
});

self.addEventListener('activate', function(event) {
    // активация
    console.log('activate', event);    
});

self.addEventListener('push', function(event) {
  console.log('[Service Worker] Push Received.');
  console.log(`[Service Worker] Push had this data: "${event.data.text()}"`);

  var message = JSON.parse(event.data.text())

  const notificationPromise = self.registration.showNotification(message.title, {
      body: message.body,
      icon: "../static/icons/android-icon-512x512.png",
      badge: "../static/icons/android-icon-96x96.png",
      vibrate: "[100, 100]",
    });
  event.waitUntil(notificationPromise);
});

self.addEventListener('notificationclick', function(event) {
  console.log('[Service Worker] Notification click Received.');

  event.notification.close();

  event.waitUntil(
    clients.openWindow('https://podvozilki.ru/notifications')
  );
});
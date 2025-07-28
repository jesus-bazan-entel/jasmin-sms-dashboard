// Service Worker para Jasmin SMS Dashboard
// Versión 2.0.0

const CACHE_NAME = 'jasmin-sms-dashboard-v2.0.0';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png'
];

// Instalación del Service Worker
self.addEventListener('install', function(event) {
  console.log('Service Worker: Instalando...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Service Worker: Cache abierto');
        return cache.addAll(urlsToCache);
      })
      .catch(function(error) {
        console.error('Service Worker: Error al cachear archivos:', error);
      })
  );
});

// Activación del Service Worker
self.addEventListener('activate', function(event) {
  console.log('Service Worker: Activando...');
  
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Eliminando cache antiguo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Interceptar peticiones de red
self.addEventListener('fetch', function(event) {
  // Solo cachear peticiones GET
  if (event.request.method !== 'GET') {
    return;
  }

  // No cachear peticiones a la API
  if (event.request.url.includes('/api/')) {
    return;
  }

  // No cachear WebSocket connections
  if (event.request.url.includes('/ws')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Si está en cache, devolverlo
        if (response) {
          return response;
        }

        // Si no está en cache, hacer petición de red
        return fetch(event.request).then(function(response) {
          // Verificar si la respuesta es válida
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clonar la respuesta
          var responseToCache = response.clone();

          caches.open(CACHE_NAME)
            .then(function(cache) {
              cache.put(event.request, responseToCache);
            });

          return response;
        });
      })
      .catch(function(error) {
        console.error('Service Worker: Error en fetch:', error);
        
        // Si es una navegación y falla, mostrar página offline
        if (event.request.destination === 'document') {
          return caches.match('/');
        }
      })
  );
});

// Manejar mensajes del cliente
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Notificaciones push (para futuras implementaciones)
self.addEventListener('push', function(event) {
  console.log('Service Worker: Push recibido');
  
  const options = {
    body: event.data ? event.data.text() : 'Nueva notificación de Jasmin SMS Dashboard',
    icon: '/logo192.png',
    badge: '/favicon.ico',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'explore',
        title: 'Ver Dashboard',
        icon: '/logo192.png'
      },
      {
        action: 'close',
        title: 'Cerrar',
        icon: '/favicon.ico'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Jasmin SMS Dashboard', options)
  );
});

// Manejar clicks en notificaciones
self.addEventListener('notificationclick', function(event) {
  console.log('Service Worker: Click en notificación');
  
  event.notification.close();

  if (event.action === 'explore') {
    // Abrir o enfocar la aplicación
    event.waitUntil(
      clients.matchAll().then(function(clientList) {
        for (var i = 0; i < clientList.length; i++) {
          var client = clientList[i];
          if (client.url === '/' && 'focus' in client) {
            return client.focus();
          }
        }
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
    );
  }
});

// Sincronización en segundo plano (para futuras implementaciones)
self.addEventListener('sync', function(event) {
  console.log('Service Worker: Sync event');
  
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // Aquí se pueden sincronizar datos pendientes
      console.log('Service Worker: Sincronización en segundo plano')
    );
  }
});

// Manejar errores
self.addEventListener('error', function(event) {
  console.error('Service Worker: Error:', event.error);
});

self.addEventListener('unhandledrejection', function(event) {
  console.error('Service Worker: Promise rechazada:', event.reason);
});

console.log('Service Worker: Jasmin SMS Dashboard v2.0.0 cargado');
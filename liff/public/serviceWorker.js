// 版本號用於更新快取
const CACHE_NAME = 'kimi-task-cache-v1';
// 需要被快取的資源列表
const urlsToCache = [
  '/',
  '/index.html',
  '/static/css/main.chunk.css',
  '/static/js/main.chunk.js',
  '/static/js/bundle.js',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png'
];

// 安裝 Service Worker 並快取資源
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('已打開快取');
        return cache.addAll(urlsToCache);
      })
  );
});

// 當瀏覽器請求資源時，嘗試從快取中提供
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 如果找到快取的響應，則返回它
        if (response) {
          return response;
        }
        // 否則嘗試從網路取得資源
        return fetch(event.request)
          .then(response => {
            // 檢查是否收到有效的響應
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // 複製響應，以便我們可以將其存入快取同時返回給瀏覽器
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          });
      })
  );
});

// 啟動時清除舊版本的快取
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
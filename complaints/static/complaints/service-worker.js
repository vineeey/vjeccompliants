// Basic offline caching for shell assets
const CACHE = 'complaints-cache-v1';
const ASSETS = [
  '/', '/offline/',
  '/static/complaints/css/custom.css',
  '/static/complaints/js/app.js',
  '/static/complaints/js/hero.js',
  '/static/complaints/img/logo.png',
];

self.addEventListener('install', (event)=>{
  event.waitUntil(
    caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())
  );
});

self.addEventListener('activate', (event)=>{
  event.waitUntil(
    caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>clients.claim())
  );
});

self.addEventListener('fetch', (event)=>{
  const req = event.request;
  if(req.method !== 'GET') return;
  event.respondWith(
    caches.match(req).then(res=> res || fetch(req).catch(()=>{
      if(req.mode==='navigate') return caches.match('/offline/');
    }))
  );
});

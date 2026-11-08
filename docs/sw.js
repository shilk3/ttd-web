/* Service worker: keeps a copy of the game so it starts fast and works offline.
 * 15.3-20261108003342 is replaced by build.sh, so every build is a new worker + cache.
 *
 * Updating: the browser fetches sw.js on every launch; a changed file installs
 * this worker, which downloads the new game files (bypassing the HTTP cache),
 * takes over, deletes old copies and tells open pages, which decide themselves
 * when to reload. (Forcing a reload from here with client.navigate() froze a
 * running game page in testing, so we never do that.) */
const CACHE = 'openttd-15.3-20261108003342';
const FILES = ['./', 'index.html', 'openttd.js', 'openttd.wasm', 'openttd.data',
  'manifest.webmanifest', 'icon-180.png', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE)
    .then(c => c.addAll(FILES.map(u => new Request(u, { cache: 'reload' }))))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    const hadOld = keys.some(k => k !== CACHE);
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
    if (!hadOld) return; // first install, nothing to update
    const wins = await self.clients.matchAll({ type: 'window' });
    wins.forEach(c => c.postMessage({ type: 'updated', version: CACHE }));
  })());
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.open(CACHE)
    .then(c => c.match(e.request, { ignoreSearch: true }))
    .then(hit => hit || fetch(e.request)));
});

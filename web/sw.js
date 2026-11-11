/* Service worker: keeps a copy of the game so it starts fast and works offline.
 *
 * The build (tools/write_sw.py) fills in the version and, for every file, a
 * fingerprint of its contents. The browser fetches sw.js on every launch; when any
 * fingerprint changed, this new worker installs and builds its cache:
 *   - a file the phone already holds with the same contents (checked by
 *     fingerprint, in any older copy) is copied over, not downloaded again;
 *   - only files whose contents changed are downloaded, bypassing the HTTP cache.
 * Then it takes over, deletes old copies and tells open pages, which decide
 * themselves when to reload. (Forcing a reload from here with client.navigate()
 * froze a running game page in testing, so we never do that.) */
const VERSION = '@@VERSION@@';
const CACHE = 'openttd-' + VERSION;
const FILES = /*@@FILES@@*/ {};

async function fingerprint(buf) {
  const digest = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
}

/* A copy of `path` with the wanted contents from an older cache, or null. */
async function reusable(path, want) {
  for (const name of await caches.keys()) {
    if (name === CACHE) continue;
    const old = await (await caches.open(name)).match(path, { ignoreSearch: true });
    if (!old) continue;
    const buf = await old.arrayBuffer();
    if (await fingerprint(buf) === want) return new Response(buf, { headers: old.headers });
  }
  return null;
}

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    const have = {};                                       // fingerprint -> a path already in this cache
    for (const [path, want] of Object.entries(FILES)) {
      if (await cache.match(path)) { have[want] = path; continue; } // done by an earlier, interrupted install
      let res = have[want] ? await cache.match(have[want]) : null;  // same contents under another name ('./' and index.html)
      if (!res) res = await reusable(path, want);
      if (!res) {
        /* ?v= makes every new version a new address for the browser and any CDN */
        res = await fetch(new Request(path + (path.includes('?') ? '&' : '?') + 'v=' + want, { cache: 'reload' }));
        if (!res.ok) throw new Error('download failed: ' + path);
      }
      await cache.put(path, res);
      have[want] = path;
    }
    await self.skipWaiting();
  })());
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

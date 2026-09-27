// Caches just the Bubble & Brew page (everything else on the site is untouched) so it opens with no connection.
// Network-first: online, it always re-fetches (so a republished game reaches installed copies); offline, it serves
// what was last cached. Some hosts redirect /bubble-and-brew.html to /bubble-and-brew, so both spellings are
// handled and only a real (non-redirect) copy of the page is ever cached.
const CACHE = "bubble-brew-v2", KEY = "bubble-and-brew-page", PATHS = ["/bubble-and-brew", "/bubble-and-brew.html"];
const keep = (res) => { if (res.ok && !res.redirected && res.type === "basic") caches.open(CACHE).then((c) => c.put(KEY, res.clone())); return res; };
self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    for (const p of PATHS) { try { const r = await fetch(p, { cache: "no-cache" }); if (r.ok && !r.redirected) { await (await caches.open(CACHE)).put(KEY, r); break; } } catch (err) {} }
  })());
  self.skipWaiting();
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET" || !PATHS.includes(new URL(e.request.url).pathname)) return;
  e.respondWith(fetch(e.request).then(keep).catch(() => caches.match(KEY)));
});

// Ultimate Job Assistant — interview-prep PWA service worker
// Caches the shell + CDN deps so the app runs offline after first load.

const CACHE = "ujassist-prep-v1";
const SHELL = ["./", "./index.html", "./manifest.json", "./icon-192.png", "./icon-512.png"];
const CDN_HOSTS = ["cdn.jsdelivr.net"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL.filter(Boolean))).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // Same-origin OR allowlisted CDNs: cache-first
  const isShell = url.origin === self.location.origin;
  const isCdn = CDN_HOSTS.some((h) => url.host.endsWith(h));
  if (!isShell && !isCdn) return;

  event.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        if (res && res.status === 200 && res.type !== "opaque") {
          const clone = res.clone();
          caches.open(CACHE).then((c) => c.put(req, clone)).catch(() => {});
        }
        return res;
      }).catch(() => hit);
    })
  );
});

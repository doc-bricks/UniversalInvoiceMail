const CACHE_NAME = "universalinvoicemail-companion-v2";
// Inhalts-Hash aller ASSETS-Dateien inkl. Manifest und Icons (web_companion/tests/sw_asset_hash.test.mjs prueft ihn):
// aendert sich eine davon, CACHE_NAME erhoehen, sonst behalten installierte PWAs den alten Code.
const ASSET_HASH = '8ca0d45f4a68'; // eslint-disable-line no-unused-vars
const ASSETS = [
  "./index.html",
  "./styles.css",
  "./library.js",
  "./app.js",
  "./manifest.webmanifest",
  "./icons/favicon.png",
  "./icons/apple-touch-icon-180.png",
  "./icons/Icon-192.png",
  "./icons/Icon-512.png",
  "./icons/Icon-maskable-192.png",
  "./icons/Icon-maskable-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)),
    )),
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request)),
  );
});

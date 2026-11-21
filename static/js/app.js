/* Shared utilities: graceful image fallback + small formatting helpers. */
(function () {
  "use strict";

  var silhouette = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500">',
    '<rect width="800" height="500" fill="#1a1817"/>',
    '<g fill="none" stroke="#eab308" stroke-opacity=".35" stroke-width="2">',
    '<path d="M0 420h800M0 300h800M0 180h800M200 0v500M400 0v500M600 0v500"/></g>',
    '<path d="M80 360c90-20 120-120 230-120 80 0 110 60 190 40 70-18 80-100 180-120" ',
    'fill="none" stroke="#eab308" stroke-width="26" stroke-linecap="round" stroke-opacity=".75"/>',
    '<path d="M80 360c90-20 120-120 230-120 80 0 110 60 190 40 70-18 80-100 180-120" ',
    'fill="none" stroke="#0d0c0b" stroke-width="10" stroke-linecap="round" stroke-dasharray="8 24" stroke-opacity=".8"/>',
    '<circle cx="660" cy="160" r="6" fill="#dc2626"/>',
    '<text x="40" y="470" fill="#78716c" font-family="monospace" font-size="20" letter-spacing="4">IMAGE UNAVAILABLE / FIELD ARCHIVE</text>',
    '</svg>'
  ].join("");

  var FALLBACK = "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(silhouette);
  window.SERPENTIA_FALLBACK = FALLBACK;

  function applyFallback(img) {
    if (!img || img.dataset.fallbackApplied) return;
    img.dataset.fallbackApplied = "1";
    img.src = FALLBACK;
  }
  window.serpentiaFallback = applyFallback;

  function watchImages(root) {
    var images = (root || document).querySelectorAll("img[data-fallback]");
    Array.prototype.forEach.call(images, function (img) {
      img.addEventListener("error", function () { applyFallback(img); });
      if (img.complete && img.naturalWidth === 0) applyFallback(img);
    });
  }

  document.addEventListener("DOMContentLoaded", function () { watchImages(document); });
})();

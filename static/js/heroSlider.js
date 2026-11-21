/* Featured specimen slider — API-driven with server-rendered fallback data. */
(function () {
  "use strict";

  var list = (window.SERPENTIA_FEATURED || []).slice();
  var index = 0;
  var timer = null;
  var frame = document.getElementById("hero-frame");
  var image = document.getElementById("hero-image");

  if (!image || !list.length) return;

  var el = {
    name: document.getElementById("hero-name"),
    scientific: document.getElementById("hero-scientific"),
    length: document.getElementById("hero-length"),
    venom: document.getElementById("hero-venom"),
    counter: document.getElementById("hero-counter"),
    specimen: document.getElementById("hero-index")
  };

  function pad(n) { return n < 10 ? "0" + n : String(n); }

  function render() {
    var snake = list[index];
    if (!snake) return;
    image.dataset.fallbackApplied = "";
    image.src = snake.image_url;
    image.alt = snake.common_name;
    if (el.name) el.name.textContent = snake.common_name;
    if (el.scientific) el.scientific.textContent = snake.scientific_name;
    if (el.length) el.length.textContent = snake.length_cm + " cm";
    if (el.venom) el.venom.textContent = snake.venom_type || "None";
    if (el.counter) el.counter.textContent = pad(index + 1) + " / " + pad(list.length);
    if (el.specimen) el.specimen.textContent = pad(snake.id || index + 1);
    image.style.animation = "none";
    void image.offsetWidth;
    image.style.animation = "";
  }

  function step(delta) {
    index = (index + delta + list.length) % list.length;
    render();
  }

  function stop() { if (timer) { clearInterval(timer); timer = null; } }
  function start() { stop(); timer = setInterval(function () { step(1); }, 6500); }

  document.getElementById("hero-prev").addEventListener("click", function () { step(-1); start(); });
  document.getElementById("hero-next").addEventListener("click", function () { step(1); start(); });

  if (frame) {
    frame.addEventListener("mouseenter", stop);
    frame.addEventListener("mouseleave", start);
  }

  document.addEventListener("keydown", function (event) {
    if (!frame) return;
    var box = frame.getBoundingClientRect();
    if (box.bottom < 0 || box.top > window.innerHeight) return;
    if (event.key === "ArrowLeft") step(-1);
    if (event.key === "ArrowRight") step(1);
  });

  image.addEventListener("error", function () {
    if (window.serpentiaFallback) window.serpentiaFallback(image);
  });

  render();
  start();

  fetch("/api/featured")
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (data && data.results && data.results.length) {
        list = data.results;
        index = 0;
        render();
      }
    })
    .catch(function () { /* server-rendered data stays in charge */ });
})();

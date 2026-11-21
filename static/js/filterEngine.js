/* Instant directory search + filters. Local render is immediate; the JSON API
   is queried in the background to keep the grid authoritative. */
(function () {
  "use strict";

  var initial = window.SERPENTIA_SNAKES || [];
  var active = window.SERPENTIA_ACTIVE || { venom: "All", continent: "All" };
  var total = parseInt(window.SERPENTIA_TOTAL || "100", 10);
  var state = { q: "", venom: active.venom || "All", continent: active.continent || "All", sort: "name" };

  var grid = document.getElementById("snake-grid");
  var count = document.getElementById("result-count");
  var empty = document.getElementById("empty-state");
  var search = document.getElementById("snake-search");
  var sort = document.getElementById("sort-select");
  var controller = null;
  var debounce = null;

  if (!grid) return;

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function matches(snake) {
    var q = state.q.toLowerCase();
    if (state.venom !== "All" && snake.venom_status !== state.venom) return false;
    if (state.continent !== "All" && snake.continent !== state.continent) return false;
    if (!q) return true;
    return [snake.common_name, snake.scientific_name, snake.family, snake.country,
      snake.habitat, snake.color_morphs].join(" ").toLowerCase().indexOf(q) !== -1;
  }

  function sortResults(rows) {
    var copy = rows.slice();
    if (state.sort === "danger") copy.sort(function (a, b) { return b.danger_level - a.danger_level || a.common_name.localeCompare(b.common_name); });
    else if (state.sort === "length") copy.sort(function (a, b) { return b.length_cm - a.length_cm || a.common_name.localeCompare(b.common_name); });
    else copy.sort(function (a, b) { return a.common_name.localeCompare(b.common_name); });
    return copy;
  }

  function tagClass(status) {
    if (status === "Venomous") return "tag--red";
    if (status === "Mildly Venomous") return "tag--amber";
    return "tag--green";
  }

  function cardHtml(s) {
    var id = parseInt(s.id, 10);
    var dots = "";
    for (var n = 1; n <= 5; n++) dots += '<i class="' + (n <= s.danger_level ? "on" : "") + '"></i>';
    return '<a class="snake-card" href="/snake/' + id + '">' +
      '<div class="card-media">' +
        '<img data-fallback src="' + escapeHtml(s.image_url) + '" alt="' + escapeHtml(s.common_name) + '" loading="lazy">' +
        '<span class="tag ' + tagClass(s.venom_status) + '">' + escapeHtml(String(s.venom_status).toUpperCase()) + '</span>' +
        '<span class="card-index">#' + ("00" + id).slice(-3) + '</span>' +
      '</div>' +
      '<div class="card-body">' +
        '<h3>' + escapeHtml(s.common_name) + '</h3>' +
        '<em>' + escapeHtml(s.scientific_name) + '</em>' +
        '<div class="card-meta"><span>' + escapeHtml(s.continent) + '</span>' +
          '<span>' + (parseInt(s.length_cm, 10) / 100).toFixed(1) + ' m</span>' +
          '<span class="danger-dots">' + dots + '</span></div>' +
        '<span class="card-cta">VIEW INFOGRAPHIC →</span>' +
      '</div></a>';
  }

  function render(rows) {
    var list = sortResults(rows.filter(matches));
    grid.innerHTML = list.map(cardHtml).join("");
    if (count) count.textContent = "SHOWING " + list.length + " / " + (total || 100) + " RECORDS";
    if (empty) empty.hidden = list.length !== 0;
    if (window.serpentiaFallback) {
      Array.prototype.forEach.call(grid.querySelectorAll("img[data-fallback]"), function (img) {
        img.addEventListener("error", function () { window.serpentiaFallback(img); });
        if (img.complete && img.naturalWidth === 0) window.serpentiaFallback(img);
      });
    }
  }

  function syncUrl() {
    var params = new URLSearchParams();
    if (state.q) params.set("q", state.q);
    if (state.venom !== "All") params.set("venom", state.venom);
    if (state.continent !== "All") params.set("continent", state.continent);
    if (state.sort !== "name") params.set("sort", state.sort);
    var qs = params.toString();
    history.replaceState(null, "", "/snakes" + (qs ? "?" + qs : ""));
  }

  function fromApi() {
    if (controller) controller.abort();
    controller = new AbortController();
    var params = new URLSearchParams({ venom: state.venom, continent: state.continent, q: state.q, sort: state.sort });
    fetch("/api/snakes?" + params.toString(), { signal: controller.signal })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (data && data.results) {
          // Keep server results as the new local source for instant subsequent filtering.
          initial = data.results;
          render(data.results);
        }
      })
      .catch(function () { /* aborted or offline: local results already shown */ });
  }

  function changed(immediate) {
    render(initial);
    syncUrl();
    if (immediate) fromApi();
    else {
      clearTimeout(debounce);
      debounce = setTimeout(fromApi, 180);
    }
  }

  Array.prototype.forEach.call(document.querySelectorAll(".pill"), function (pill) {
    if (pill.dataset.filter === "venom" && pill.dataset.value === state.venom) pill.classList.add("active");
    if (pill.dataset.filter === "continent" && pill.dataset.value === state.continent) pill.classList.add("active");
    pill.addEventListener("click", function () {
      var kind = pill.dataset.filter;
      state[kind] = pill.dataset.value;
      Array.prototype.forEach.call(document.querySelectorAll('.pill[data-filter="' + kind + '"]'), function (p) {
        p.classList.toggle("active", p === pill);
      });
      changed(true);
    });
  });

  if (search) {
    search.value = state.q;
    search.addEventListener("input", function () {
      state.q = search.value.trim();
      changed(false);
    });
  }

  var clear = document.getElementById("clear-search");
  if (clear) clear.addEventListener("click", function () {
    if (search) search.value = "";
    state.q = "";
    changed(true);
  });

  if (sort) {
    sort.value = state.sort;
    sort.addEventListener("change", function () {
      state.sort = sort.value;
      changed(false);
    });
  }

  render(initial);
})();

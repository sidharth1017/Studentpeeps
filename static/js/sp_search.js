/* Live search: suggestions dropdown (header + home) and full-screen sheet on phones. */
(function () {
  var cfg = window.SP_SEARCH || {};
  var SUGGEST = cfg.suggestUrl, EXPLORE = cfg.exploreUrl;
  if (!SUGGEST || !EXPLORE) return;

  var ICON = function (id, cls) { return '<svg class="ic ' + (cls || '') + '" aria-hidden="true"><use href="#i-' + id + '"/></svg>'; };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var cache = {};

  function fetchSuggest(q) {
    var key = q.toLowerCase();
    if (cache[key]) return Promise.resolve(cache[key]);
    return fetch(SUGGEST + '?q=' + encodeURIComponent(q), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) { return r.json(); })
      .then(function (d) { cache[key] = d; return d; });
  }

  function brandItem(b) {
    var range = b.min && b.max ? '₹' + b.min.toLocaleString('en-IN') + ' – ₹' + b.max.toLocaleString('en-IN') : '';
    var thumb = b.image
      ? '<img src="' + esc(b.image) + '" alt="" loading="lazy">'
      : '<span>' + esc((b.name || '?').charAt(0)) + '</span>';
    return '<a class="sg-i" href="/giftcard/' + encodeURIComponent(b.sku) + '/">' +
      '<span class="mini">' + thumb + '</span>' +
      '<span class="sg-t">' + esc(b.name) + '<small>' + esc(b.category) + '</small></span>' +
      (range ? '<span class="r sg-p">' + range + '</span>' : '') + '</a>';
  }

  function render(q, d) {
    var out = [];
    if (!q) {
      if (d.brands.length) out.push('<div class="sg-h">Trending now</div>' + d.brands.map(brandItem).join(''));
      if (d.categories.length) {
        out.push('<div class="sg-h">Categories</div><div class="sg-chips">' + d.categories.map(function (c) {
          return '<a class="chip" href="' + EXPLORE + '?category=' + encodeURIComponent(c.id) + '">' + esc(c.name) + '</a>';
        }).join('') + '</div>');
      }
      return out.join('');
    }
    if (d.brands.length) out.push('<div class="sg-h">Brands</div>' + d.brands.map(brandItem).join(''));
    if (d.categories.length) {
      out.push('<div class="sg-h">Categories</div>' + d.categories.map(function (c) {
        return '<a class="sg-i" href="' + EXPLORE + '?category=' + encodeURIComponent(c.id) + '">' + ICON('grid') +
          '<span class="sg-t">' + esc(c.name) + '</span><span class="r sg-p">' + c.count + ' brands</span></a>';
      }).join(''));
    }
    if (!d.brands.length && !d.categories.length) {
      out.push('<div class="sg-empty"><b>No brands match “' + esc(q) + '”</b><p class="hint">Check the spelling, or browse by category. We add brands every week.</p></div>');
    } else {
      out.push('<a class="sg-i sg-all" href="' + EXPLORE + '?search=' + encodeURIComponent(q) + '">' + ICON('search') +
        '<span class="sg-t">See all results for “' + esc(q) + '”</span></a>');
    }
    return out.join('');
  }

  /* Wire an input to a results box. */
  function attach(input, box, opts) {
    opts = opts || {};
    var timer = null, seq = 0;

    function show(q) {
      var n = ++seq;
      fetchSuggest(q).then(function (d) {
        if (n !== seq) return; // a newer keystroke is in flight
        box.innerHTML = render(q, d);
        box.classList.remove('hide');
      }).catch(function () { /* leave the form submit as the fallback */ });
    }
    function hide() { box.classList.add('hide'); seq++; }
    function items() { return Array.prototype.slice.call(box.querySelectorAll('.sg-i')); }

    input.setAttribute('autocomplete', 'off');
    input.addEventListener('focus', function () { show(input.value.trim()); });
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { show(input.value.trim()); }, 120);
    });
    input.addEventListener('keydown', function (e) {
      var list = items(), i = list.findIndex(function (x) { return x.classList.contains('on'); });
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (box.classList.contains('hide')) { show(input.value.trim()); return; }
        if (list[i]) list[i].classList.remove('on');
        i = e.key === 'ArrowDown' ? Math.min(list.length - 1, i + 1) : Math.max(0, i - 1);
        if (list[i]) { list[i].classList.add('on'); list[i].scrollIntoView({ block: 'nearest' }); }
      } else if (e.key === 'Enter') {
        if (list[i]) { e.preventDefault(); list[i].click(); }
        else if (!input.form && input.value.trim()) { e.preventDefault(); location.href = EXPLORE + '?search=' + encodeURIComponent(input.value.trim()); }
        // otherwise the surrounding <form> submits to the explore page
      } else if (e.key === 'Escape') {
        hide();
        if (opts.onEscape) opts.onEscape();
      }
    });
    if (!opts.persistent) {
      document.addEventListener('mousedown', function (e) {
        if (!box.contains(e.target) && e.target !== input) hide();
      });
    }
    return { show: show, hide: hide };
  }

  /* Dropdowns under the header search and the home page big search. */
  document.querySelectorAll('.hsearch input[type="search"], .bigsearch input[type="search"]').forEach(function (input) {
    var host = input.closest('.hsearch, .bigsearch');
    var box = document.createElement('div');
    box.className = 'sugg hide';
    box.setAttribute('role', 'listbox');
    host.appendChild(box);
    attach(input, box);
  });

  /* Full-screen search on phones/tablets. */
  var overlay = null;
  function openOverlay() {
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'sg-ov hide';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-label', 'Search gift cards');
      overlay.innerHTML =
        '<div class="sg-ov-h"><form class="msrch" action="' + EXPLORE + '" method="GET">' + ICON('search') +
        '<input id="sq" type="search" name="search" placeholder="Search brands or categories" aria-label="Search gift cards"></form>' +
        '<button type="button" class="btn-q sg-cancel">Cancel</button></div>' +
        '<div class="sg-ov-b sugg-static"></div>';
      document.body.appendChild(overlay);
      var input = overlay.querySelector('#sq'), box = overlay.querySelector('.sg-ov-b');
      var api = attach(input, box, { persistent: true, onEscape: closeOverlay });
      box.classList.remove('hide');
      overlay.querySelector('.sg-cancel').addEventListener('click', closeOverlay);
      overlay._api = api;
    }
    overlay.classList.remove('hide');
    document.documentElement.style.overflow = 'hidden';
    var inp = overlay.querySelector('#sq');
    inp.value = '';
    overlay._api.show('');
    inp.focus();
  }
  function closeOverlay() {
    if (!overlay) return;
    overlay.classList.add('hide');
    document.documentElement.style.overflow = '';
  }
  document.querySelectorAll('.js-open-search').forEach(function (el) {
    el.addEventListener('click', function (e) { e.preventDefault(); openOverlay(); });
  });
})();

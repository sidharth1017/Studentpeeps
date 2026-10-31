/* Live search: suggestions dropdown (header + home) and full-screen sheet on phones. */
(function () {
  var cfg = window.SP_SEARCH || {};
  var SUGGEST = cfg.suggestUrl, EXPLORE = cfg.exploreUrl;
  var MODE = cfg.mode === 'coupons' ? 'coupons' : 'giftcards';
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

  function gcMarkHtml() {
    var url = cfg.markUrl;
    if (url) {
      return '<span class="gc-mark gc-mark-sp" aria-hidden="true"><img src="' + esc(url) + '" alt=""></span>';
    }
    return '<span class="gc-mark" aria-hidden="true">studentpeeps</span>';
  }

  function pkMarkHtml(b) {
    var pal0 = esc(b.pal_0 || '#2442E6');
    var pal1 = esc(b.pal_1 || '#6440E0');
    var initial = esc(String(b.name || '?').charAt(0));
    if (b.logo_url) {
      return '<span class="pk-mark sg-pk-mark" style="--a:' + pal0 + ';--b:' + pal1 + '" aria-hidden="true">' +
        '<img src="' + esc(b.logo_url) + '" alt="" width="72" height="72" loading="lazy" ' +
        'onerror="this.hidden=true;this.parentElement.classList.add(\'is-fallback\');">' +
        '<span class="pk-mark-fallback">' + initial + '</span></span>';
    }
    return '<span class="pk-mark sg-pk-mark is-fallback" style="--a:' + pal0 + ';--b:' + pal1 + '" aria-hidden="true">' +
      '<span class="pk-mark-fallback">' + initial + '</span></span>';
  }

  function brandItem(b) {
    var range = b.min && b.max ? '₹' + b.min.toLocaleString('en-IN') + ' – ₹' + b.max.toLocaleString('en-IN') : '';
    var tile = pkMarkHtml(b);
    var right = '';
    if (b.discount_pct > 0) {
      right = '<span class="r"><span class="off">' + esc(b.discount_label || '') + ' off</span></span>';
    } else if (range) {
      right = '<span class="r sg-p">' + range + '</span>';
    }
    return '<a class="sg-i" href="/giftcard/' + encodeURIComponent(b.sku) + '/">' +
      '<span class="mini">' + tile + '</span>' +
      '<span class="sg-t">' + esc(b.name) + '<small>' + esc(b.category) + '</small></span>' +
      right + '</a>';
  }

  function offerItem(o) {
    var pat = esc(o.pattern || 'p-dots');
    var pal0 = esc(o.pal_0 || '#2442E6');
    var pal1 = esc(o.pal_1 || '#6440E0');
    var bcls = esc(o.brand_size_cls || '');
    var tile;
    if (o.thumbnail_url) {
      tile = '<div class="gc sg-mini sg-mini-photo" aria-hidden="true"><img src="' + esc(o.thumbnail_url) + '" alt=""></div>';
    } else {
      tile =
        '<div class="gc ' + pat + ' sg-mini" style="--a:' + pal0 + ';--b:' + pal1 + '" aria-hidden="true">' +
        '<div class="gc-in sg-mini-in">' +
        '<div class="gc-top"><div>' +
        '<div class="gc-brand ' + bcls + '">' + esc(o.name) + '</div>' +
        '<div class="gc-kind">Coupon</div></div></div>' +
        '<div class="gc-bot"><span></span>' + gcMarkHtml() + '</div>' +
        '</div></div>';
    }
    var right = o.is_exclusive
      ? '<span class="r"><span class="pill a">Exclusive</span></span>'
      : '<span class="r sg-p">Open</span>';
    return '<a class="sg-i" href="' + esc(o.link) + '">' +
      '<span class="mini">' + tile + '</span>' +
      '<span class="sg-t">' + esc(o.name) + '<small>' + esc(o.title || o.category) + '</small></span>' +
      right + '</a>';
  }

  function itemFn(b) {
    return MODE === 'coupons' ? offerItem(b) : brandItem(b);
  }

  function render(q, d) {
    var out = [];
    var itemLabel = MODE === 'coupons' ? 'Offers' : 'Brands';
    var countLabel = MODE === 'coupons' ? 'offers' : 'brands';
    var emptyTitle = MODE === 'coupons'
      ? 'No offers match “' + esc(q) + '”'
      : 'No brands match “' + esc(q) + '”';
    var emptyHint = MODE === 'coupons'
      ? 'Try another spelling or browse by category.'
      : 'Check the spelling, or browse by category. We add brands every week.';

    if (!q) {
      if (d.brands.length) out.push('<div class="sg-h">Trending now</div>' + d.brands.map(itemFn).join(''));
      if (d.categories.length) {
        out.push('<div class="sg-h">Categories</div><div class="sg-chips">' + d.categories.map(function (c) {
          return '<a class="chip" href="' + EXPLORE + '?category=' + encodeURIComponent(c.id) + '">' + esc(c.name) + '</a>';
        }).join('') + '</div>');
      }
      return out.join('');
    }
    if (d.brands.length) out.push('<div class="sg-h">' + itemLabel + '</div>' + d.brands.map(itemFn).join(''));
    if (d.categories.length) {
      out.push('<div class="sg-h">Categories</div>' + d.categories.map(function (c) {
        return '<a class="sg-i" href="' + EXPLORE + '?category=' + encodeURIComponent(c.id) + '">' + ICON('grid') +
          '<span class="sg-t">' + esc(c.name) + '</span><span class="r sg-p">' + c.count + ' ' + countLabel + '</span></a>';
      }).join(''));
    }
    if (!d.brands.length && !d.categories.length) {
      out.push('<div class="sg-empty"><b>' + emptyTitle + '</b><p class="hint">' + emptyHint + '</p></div>');
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
        if (n !== seq) return;
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

  document.querySelectorAll('.hsearch input[type="search"], .bigsearch input[type="search"]').forEach(function (input) {
    var host = input.closest('.hsearch, .bigsearch');
    var box = document.createElement('div');
    box.className = 'sugg hide';
    box.setAttribute('role', 'listbox');
    host.appendChild(box);
    attach(input, box);
  });

  var overlay = null;
  var searchLabel = cfg.searchLabel || 'Search gift cards';
  var placeholder = cfg.placeholder || 'Search brands or categories';

  function openOverlay() {
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'sg-ov hide';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-label', searchLabel);
      overlay.innerHTML =
        '<div class="sg-ov-h"><form class="msrch" action="' + EXPLORE + '" method="GET">' + ICON('search') +
        '<input id="sq" type="search" name="search" placeholder="' + esc(placeholder) + '" aria-label="' + esc(searchLabel) + '"></form>' +
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

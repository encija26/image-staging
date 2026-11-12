/* Bramley House Favourites (custom wishlist). Nov 12 2026.
   Saves live in this browser (localStorage "bhFav"). Known Klaviyo profiles also get an
   "Added to Favourites" event. GA4 gets add_to_wishlist, Meta gets AddToWishlist. */
(function () {
  'use strict';
  if (window.__bhFavLoaded) return; window.__bhFavLoaded = true;
  var CFG = window.BHFAV_CFG || { page: '/pages/favourites', cur: 'USD' };
  var KEY = 'bhFav', ASKED = 'bhFavAsked', MAXN = 200;
  var HEART = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 20.2s-7.2-4.5-7.2-10.1A4.1 4.1 0 0 1 12 7.4a4.1 4.1 0 0 1 7.2 2.7c0 5.6-7.2 10.1-7.2 10.1z"/></svg>';

  /* ---------- storage ---------- */
  function read() { try { var a = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(a) ? a.filter(function (x) { return x && typeof x.h === 'string'; }) : []; } catch (e) { return []; } }
  function write(a) { try { localStorage.setItem(KEY, JSON.stringify(a.slice(0, MAXN))); } catch (e) {} }
  function has(h) { return read().some(function (x) { return x.h === h; }); }
  function count() { return read().length; }

  /* ---------- product data ---------- */
  var cache = {};
  function getProduct(h) {
    if (!cache[h]) cache[h] = fetch('/products/' + encodeURIComponent(h) + '.js', { credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error('nf'); return r.json(); });
    return cache[h];
  }
  function handleFromHref(href) { var m = (href || '').match(/\/products\/([^/?#]+)/); return m ? decodeURIComponent(m[1]) : null; }
  function money(c) { return '$' + (c / 100).toLocaleString('en-US', { minimumFractionDigits: (c % 100 ? 2 : 0), maximumFractionDigits: 2 }); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function img(src, w) { if (!src) return ''; src = src.indexOf('//') === 0 ? 'https:' + src : src; return src + (src.indexOf('?') > -1 ? '&' : '?') + 'width=' + (w || 600); }

  /* ---------- add / remove ---------- */
  function toggle(h, srcEl) {
    if (!h) return;
    if (has(h)) { write(read().filter(function (x) { return x.h !== h; })); sync(); renderPage(); return; }
    var a = read(); a.unshift({ h: h, t: Date.now() }); write(a); sync();
    toast();
    getProduct(h).then(function (p) {
      var v = (p.variants || [])[0] || {};
      var a2 = read(); a2.forEach(function (x) { if (x.h === h) { x.id = p.id; x.v = v.id; x.p = p.price; } }); write(a2);
      report(p, v);
      if (count() >= 2) maybeAsk();
    }).catch(function () {});
  }

  /* ---------- reporting (no emails are sent from here) ---------- */
  function report(p, v) {
    var val = (p.price || 0) / 100, url = location.origin + '/products/' + p.handle;
    try { if (window.klaviyo && klaviyo.track) klaviyo.track('Added to Favourites', { ProductName: p.title, ProductID: String(p.id), Handle: p.handle, URL: url, ImageURL: img(p.featured_image, 800), Price: val, ProductType: p.type || '', Tags: p.tags || [], Preview: !CFG.live }); } catch (e) {}
    try { if (window.gtag) gtag('event', 'add_to_wishlist', { currency: CFG.cur, value: val, items: [{ item_id: String(p.id), item_name: p.title, item_category: p.type || '', price: val }] }); } catch (e) {}
    try { if (window.fbq) fbq('track', 'AddToWishlist', { content_ids: ['shopify_US_' + p.id + '_' + v.id], content_type: 'product_group', content_name: p.title, value: val, currency: CFG.cur }); } catch (e) {}
    try { if (window.clarity) { clarity('event', 'favourite_added'); clarity('set', 'favourited', p.handle); } } catch (e) {}
  }

  /* ---------- hearts on product cards ---------- */
  function decorateCards(root) {
    (root || document).querySelectorAll('.product-card[data-product] .card--product').forEach(function (card) {
      if (card.querySelector('.bhfav-heart')) return;
      var wrap = card.closest('.product-card');
      var link = card.querySelector('a[href*="/products/"]');
      var h = wrap.getAttribute('data-product') || (link && handleFromHref(link.getAttribute('href')));
      if (!h || /gift-card/.test(h)) return;
      var name = (wrap.querySelector('.visually-hidden') || {}).textContent || 'this piece';
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'bhfav-heart'; b.setAttribute('data-bhfav', h); b.setAttribute('data-name', name.trim());
      b.innerHTML = HEART; card.appendChild(b);
    });
  }

  /* ---------- product page button ---------- */
  function decoratePDP() {
    var meta = window.ShopifyAnalytics && ShopifyAnalytics.meta;
    if (!meta || !meta.page || meta.page.pageType !== 'product') return;
    var h = handleFromHref(location.pathname); if (!h) return;
    var add = document.querySelector('.product__info-container button[name="add"], product-info button[name="add"], form[action*="/cart/add"] button[name="add"]');
    if (!add || document.querySelector('.bhfav-pdp')) return;
    var row = document.createElement('div'); row.className = 'bhfav-pdp-row';
    var b = document.createElement('button'); b.type = 'button'; b.className = 'bhfav-pdp'; b.setAttribute('data-bhfav', h);
    b.setAttribute('data-name', (document.querySelector('.product__title') || {}).textContent ? document.querySelector('.product__title').textContent.trim() : 'this piece');
    b.innerHTML = HEART + '<span></span>';
    row.appendChild(b);
    var host = add.closest('.product-form__buttons') || add.parentNode;
    host.parentNode.insertBefore(row, host.nextSibling);
  }

  /* ---------- header link ---------- */
  function decorateHeader() {
    var cart = document.getElementById('cart-icon-bubble');
    if (!cart || document.querySelector('.bhfav-hdr')) return;
    var a = document.createElement('a'); a.className = 'bhfav-hdr header__icon focus-inset'; a.href = CFG.page;
    a.innerHTML = HEART + '<span class="bhfav-count" hidden></span>';
    cart.parentNode.insertBefore(a, cart);
  }

  /* ---------- keep every heart in step ---------- */
  function sync() {
    var set = {}; read().forEach(function (x) { set[x.h] = 1; });
    document.querySelectorAll('[data-bhfav]').forEach(function (b) {
      var on = !!set[b.getAttribute('data-bhfav')], n = b.getAttribute('data-name') || 'this piece';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.setAttribute('aria-label', (on ? 'Remove ' : 'Save ') + n + (on ? ' from' : ' to') + ' Favourites');
      if (b.classList.contains('bhfav-pdp')) b.querySelector('span').textContent = on ? 'Saved to Favourites' : 'Save to Favourites';
    });
    var n = count();
    document.querySelectorAll('.bhfav-hdr').forEach(function (a) {
      var c = a.querySelector('.bhfav-count'); c.textContent = n; c.hidden = n === 0;
      a.setAttribute('aria-label', 'Favourites' + (n ? ', ' + n + (n === 1 ? ' piece' : ' pieces') + ' saved' : ''));
    });
  }

  /* ---------- toast ---------- */
  var tEl, tTimer;
  function toast() {
    if (!tEl) { tEl = document.createElement('div'); tEl.className = 'bhfav-toast'; tEl.setAttribute('role', 'status'); tEl.innerHTML = '<span>Saved to your Favourites</span><a href="' + esc(CFG.page) + '">View list</a>'; document.body.appendChild(tEl); }
    tEl.classList.add('is-on'); clearTimeout(tTimer); tTimer = setTimeout(function () { tEl.classList.remove('is-on'); }, 2600);
  }

  /* ---------- email: keep my list ---------- */
  function shareURL() {
    var hs = read().map(function (x) { return encodeURIComponent(x.h); }).join(',');
    var base = location.origin + CFG.page; return base + (base.indexOf('?') > -1 ? '&' : '?') + 'list=' + hs;
  }
  function identified() { try { return !!(window.klaviyo && klaviyo.isIdentified && klaviyo.isIdentified() === true); } catch (e) { return false; } }
  function maybeAsk(force) {
    if (!force) { try { if (localStorage.getItem(ASKED)) return; } catch (e) { return; } if (identified()) return; }
    try { localStorage.setItem(ASKED, String(Date.now())); } catch (e) {}
    var w = document.createElement('div'); w.className = 'bhfav-sheet-wrap';
    w.innerHTML = '<form class="bhfav-sheet" role="dialog" aria-modal="true" aria-labelledby="bhfavT" novalidate>' +
      '<button type="button" class="bhfav-x" aria-label="Close">&times;</button>' +
      '<p class="bhfav-eb">Your Favourites</p><h2 id="bhfavT">Keep your list for later</h2>' +
      '<p>Add your email and we\'ll send you a link to your Favourites, so you can open your list on any device.</p>' +
      '<label class="bhfav-field">Email address<input type="email" name="email" autocomplete="email" required placeholder="you@example.com"></label>' +
      '<label class="bhfav-check"><input type="checkbox" name="optin"><span>Also email me occasional offers and new arrivals from Bramley House.</span></label>' +
      '<p class="bhfav-err" hidden></p>' +
      '<button type="submit" class="bhfav-go">Keep my list</button>' +
      '<button type="button" class="bhfav-no">No thanks, keep browsing</button>' +
      '<p class="bhfav-fine">Unsubscribe any time. We never share your email.</p></form>';
    document.body.appendChild(w);
    var f = w.querySelector('form'), em = f.querySelector('input[type=email]'), err = f.querySelector('.bhfav-err');
    function close() { w.remove(); document.removeEventListener('keydown', onKey); }
    function onKey(e) { if (e.key === 'Escape') close(); }
    document.addEventListener('keydown', onKey);
    w.addEventListener('click', function (e) { if (e.target === w || e.target.closest('.bhfav-x,.bhfav-no')) close(); });
    setTimeout(function () { em.focus(); }, 30);
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = (em.value || '').trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) { err.textContent = 'Please enter a valid email address.'; err.hidden = false; em.focus(); return; }
      var opt = f.querySelector('input[name=optin]').checked;
      try {
        if (window.klaviyo) {
          klaviyo.identify({ email: v }).then(function () {
            var items = read();
            klaviyo.track('Saved Favourites List', { RestoreURL: shareURL(), Count: items.length, Handles: items.map(function (x) { return x.h; }), WantsOffers: opt, Preview: !CFG.live });
            if (opt && CFG.listId) subscribe(v);
          });
        }
      } catch (x) {}
      f.innerHTML = '<p class="bhfav-eb">Your Favourites</p><h2>Your list is saved</h2><p>Look out for an email with the link to your Favourites.</p><button type="button" class="bhfav-go">Keep browsing</button>';
      f.querySelector('.bhfav-go').addEventListener('click', close);
    });
  }
  function subscribe(email) {
    try {
      fetch('https://a.klaviyo.com/client/subscriptions/?company_id=' + encodeURIComponent(CFG.klaviyo || 'SJkVfD'), {
        method: 'POST', headers: { 'Content-Type': 'application/json', revision: '2024-10-15' },
        body: JSON.stringify({ data: { type: 'subscription', attributes: { custom_source: 'Favourites', profile: { data: { type: 'profile', attributes: { email: email } } } }, relationships: { list: { data: { type: 'list', id: CFG.listId } } } } })
      });
    } catch (e) {}
  }

  /* ---------- Favourites page ---------- */
  var page;
  function renderPage() {
    page = page || document.getElementById('bhfav-page'); if (!page) return;
    var grid = page.querySelector('.bhfav-grid'), empty = page.querySelector('.bhfav-empty'), sub = page.querySelector('[data-bhfav-sub]'), tools = page.querySelector('.bhfav-page__tools');
    var items = read();
    sub.textContent = items.length ? items.length + (items.length === 1 ? ' piece saved' : ' pieces saved') : '';
    empty.hidden = items.length > 0; tools.hidden = items.length === 0;
    grid.innerHTML = items.map(function (x) { return '<div class="bhfav-item" data-h="' + esc(x.h) + '"><div class="card--product"><a class="bhfav-item__ph" href="/products/' + esc(x.h) + '" aria-hidden="true" tabindex="-1"></a></div><h3 class="card__title"><a href="/products/' + esc(x.h) + '">&nbsp;</a></h3><div class="bhfav-item__price">&nbsp;</div></div>'; }).join('');
    items.forEach(function (x) {
      getProduct(x.h).then(function (p) {
        var el = grid.querySelector('.bhfav-item[data-h="' + CSS.escape(x.h) + '"]'); if (!el) return;
        var v = (p.variants || []).filter(function (vv) { return vv.available; })[0] || (p.variants || [])[0] || {};
        el.querySelector('.bhfav-item__ph').innerHTML = p.featured_image ? '<img src="' + esc(img(p.featured_image, 700)) + '" alt="' + esc(p.title) + '" loading="lazy">' : '';
        var ph = el.querySelector('.card--product'), hb = document.createElement('button');
        hb.type = 'button'; hb.className = 'bhfav-heart'; hb.setAttribute('data-bhfav', x.h); hb.setAttribute('data-name', p.title); hb.innerHTML = HEART; ph.appendChild(hb);
        var t = el.querySelector('.card__title a'); t.textContent = p.title; delete t.dataset.bhl;
        var dropped = x.p && p.price < x.p;
        el.querySelector('.bhfav-item__price').innerHTML = money(p.price) + (dropped ? '<span class="bhfav-item__was">' + money(x.p) + '</span>' : '');
        if (dropped) el.insertAdjacentHTML('beforeend', '<span class="bhfav-item__drop">Price lower since you saved it</span>');
        if (p.available && v.id) el.insertAdjacentHTML('beforeend', '<button type="button" class="bhfav-item__add" data-vid="' + v.id + '">Add to cart</button>');
        else el.insertAdjacentHTML('beforeend', '<a class="bhfav-item__add" href="/products/' + esc(x.h) + '">View piece</a>');
        sync();
      }).catch(function () {
        var el = grid.querySelector('.bhfav-item[data-h="' + CSS.escape(x.h) + '"]'); if (el) el.remove();
        write(read().filter(function (y) { return y.h !== x.h; })); sync();
      });
    });
    sync();
  }
  function pageEvents() {
    page = document.getElementById('bhfav-page'); if (!page) return;
    var q = new URLSearchParams(location.search), lst = q.get('list');
    if (lst) {
      var cur = read(), seen = {}; cur.forEach(function (x) { seen[x.h] = 1; });
      lst.split(',').map(function (s) { return decodeURIComponent(s).trim(); }).filter(function (s) { return /^[a-z0-9][a-z0-9-]*$/i.test(s) && !seen[s]; })
        .forEach(function (h) { cur.push({ h: h, t: Date.now() }); seen[h] = 1; });
      write(cur); q.delete('list');
      try { history.replaceState(null, '', location.pathname + (q.toString() ? '?' + q.toString() : '')); } catch (e) {}
    }
    page.addEventListener('click', function (e) {
      var add = e.target.closest('.bhfav-item__add[data-vid]');
      if (add) {
        add.disabled = true; add.textContent = 'Adding';
        fetch('/cart/add.js', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ items: [{ id: +add.getAttribute('data-vid'), quantity: 1 }] }) })
          .then(function (r) { if (!r.ok) throw 0; return fetch('/cart.js'); }).then(function (r) { return r.json(); })
          .then(function (c) { add.outerHTML = '<a class="bhfav-item__add" href="/cart">Added. View cart</a>'; document.querySelectorAll('#cart-icon-bubble .cart-count-bubble span').forEach(function (s) { s.textContent = c.item_count; }); })
          .catch(function () { add.disabled = false; add.textContent = 'Try again'; });
        return;
      }
      if (e.target.closest('[data-bhfav-share]')) {
        var u = shareURL(), btn = e.target.closest('[data-bhfav-share]');
        if (navigator.share) { navigator.share({ title: 'My Bramley House Favourites', url: u }).catch(function () {}); }
        else if (navigator.clipboard) { navigator.clipboard.writeText(u).then(function () { btn.textContent = 'Link copied'; setTimeout(function () { btn.textContent = 'Share my list'; }, 2200); }); }
        return;
      }
      if (e.target.closest('[data-bhfav-email]')) { maybeAsk(true); }
    });
    renderPage();
  }

  /* ---------- wire up ---------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.bhfav-heart,.bhfav-pdp');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();
    toggle(b.getAttribute('data-bhfav'), b);
  }, true);
  window.addEventListener('storage', function (e) { if (e.key === KEY) { sync(); renderPage(); } });

  function run() { decorateHeader(); decorateCards(); decoratePDP(); sync(); }
  function start() {
    run(); pageEvents();
    var pend = false;
    new MutationObserver(function () { if (pend) return; pend = true; requestAnimationFrame(function () { pend = false; run(); }); })
      .observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();

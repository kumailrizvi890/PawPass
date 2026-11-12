/* PawPass pass interactions — 3D tilt, flip, offline badge.
   No fake data: every value on the pass comes from the pet record
   rendered by the server. The badge only reflects navigator.onLine. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Gentle 3D tilt: the pass follows the pointer a little ---- */
  document.querySelectorAll('.pass-scene').forEach(function (scene) {
    var tilt = scene.querySelector('.pass-tilt');
    if (!tilt || reduceMotion) return;
    scene.addEventListener('pointermove', function (event) {
      var rect = scene.getBoundingClientRect();
      var x = (event.clientX - rect.left) / rect.width - 0.5;
      var y = (event.clientY - rect.top) / rect.height - 0.5;
      tilt.style.setProperty('--pp-ry', (x * 8).toFixed(2) + 'deg');
      tilt.style.setProperty('--pp-rx', (-y * 6).toFixed(2) + 'deg');
    });
    scene.addEventListener('pointerleave', function () {
      tilt.style.setProperty('--pp-ry', '0deg');
      tilt.style.setProperty('--pp-rx', '0deg');
    });
  });

  /* ---- Flip the pass: front (status) <-> back (full care record) ---- */
  document.querySelectorAll('[data-flip-pass]').forEach(function (button) {
    button.addEventListener('click', function () {
      var scene = document.querySelector('.pass-scene');
      if (!scene) return;
      var flipped = scene.classList.toggle('flipped');
      button.setAttribute('aria-pressed', String(flipped));
      button.textContent = flipped ? 'Show pass front' : 'Flip pass';
      scene.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' });
    });
  });

  /* ---- Offline-first badge: live connection state, nothing more ---- */
  function renderBadge() {
    var online = navigator.onLine;
    document.querySelectorAll('[data-offline-badge]').forEach(function (badge) {
      badge.classList.toggle('is-offline', !online);
      badge.innerHTML = online
        ? '<span class="dot"></span> Offline-ready pass'
        : '<span class="dot"></span> You are offline &mdash; pass saved on this device';
    });
  }

  window.addEventListener('online', renderBadge);
  window.addEventListener('offline', renderBadge);
  renderBadge();
})();

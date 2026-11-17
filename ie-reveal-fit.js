/* Auto-fit helper for IE SciTech Reveal.js decks - v5 */
/* Add class="ie-auto-fit" to any text container that must not spill  */
(function () {
  function fitElement(el) {
    if (!el || !el.parentElement) return;

    /* Skip elements inside hidden slides to avoid zero-dimension measurements.
       Reveal hides non-current slides with display:none or visibility:hidden.
       Check the closest section ancestor for either condition.              */
    var section = el.closest('section');
    if (section) {
      var style = window.getComputedStyle(section);
      if (style.display === 'none' || style.visibility === 'hidden') return;
    }

    /* Reset to natural size before measuring */
    el.style.setProperty('--fit-scale', '1');
    el.style.width  = '100%';
    el.style.height = '100%';

    var parent = el.parentElement;
    var pw = parent.clientWidth;
    var ph = parent.clientHeight;
    if (!pw || !ph) return;

    var cw = el.scrollWidth;
    var ch = el.scrollHeight;
    if (!cw || !ch) return;

    /* Scale down only, never up, so type stays at its designed size.
       Apply a 1.5% visual margin when shrinking; floor at 0.50.
       Below 0.50 the text is unreadable - split the slide instead.  */
    var raw   = Math.min(pw / cw, ph / ch);
    var scale = raw >= 1 ? 1 : Math.max(0.50, raw * 0.985);
    el.style.setProperty('--fit-scale', String(scale));

    /* Compensate the box for the scale so scaled content still spans the
       frame margin to margin. Without this, a scale of 0.9 leaves a 10 %
       gap on the right and bottom, and tables look narrow. Applies inside a
       fixed safe frame only; split and grid parents size themselves. A wider box can
       reflow content, so re-measure and tighten the scale until it fits.   */
    if (scale < 1 && parent.classList.contains('safe-frame')) {
      for (var i = 0; i < 4; i++) {
        el.style.width  = 'calc(100% / ' + scale + ')';
        el.style.height = 'calc(100% / ' + scale + ')';
        var over = Math.max(el.scrollWidth * scale / pw, el.scrollHeight * scale / ph);
        if (over <= 1.002) break;
        scale = Math.max(0.50, scale / over * 0.995);
        el.style.setProperty('--fit-scale', String(scale));
      }
    }
  }

  function fitAll() {
    document.querySelectorAll('.ie-auto-fit').forEach(fitElement);
  }

  window.IERevealFit = { fitAll: fitAll };

  window.addEventListener('load',   fitAll);
  window.addEventListener('resize', fitAll);

  if (window.Reveal && typeof Reveal.on === 'function') {
    Reveal.on('ready',          fitAll);
    Reveal.on('slidechanged',   fitAll);
    Reveal.on('fragmentshown',  fitAll);
    Reveal.on('fragmenthidden', fitAll);
  }

  if ('ResizeObserver' in window) {
    new ResizeObserver(fitAll).observe(document.body);
  }
})();

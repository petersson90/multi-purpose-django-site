// Follow the visitor's system light/dark setting. Bootstrap 5.3 does not do this by itself.
// Loaded in <head> without defer so the right theme is set before the page is painted.
(function () {
  var query = window.matchMedia('(prefers-color-scheme: dark)');
  function apply() {
    document.documentElement.setAttribute('data-bs-theme', query.matches ? 'dark' : 'light');
  }
  apply();
  query.addEventListener('change', apply);
})();

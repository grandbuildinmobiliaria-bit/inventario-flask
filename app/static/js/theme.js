(function () {
  const STORAGE_KEY = 'inventario-theme';
  const root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    const toggle = document.querySelector('[data-theme-toggle]');
    if (toggle) {
      toggle.textContent = theme === 'dark' ? '☀️ Modo claro' : '🌙 Modo oscuro';
    }
  }

  const saved = localStorage.getItem(STORAGE_KEY);
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(saved || (prefersDark ? 'dark' : 'light'));

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    const current = root.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  });
})();

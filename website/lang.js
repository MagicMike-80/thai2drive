// Thai2Drive marketing site — language switcher
(function () {
  const DEFAULT = 'no';
  const STORAGE_KEY = 't2d-lang';

  function setLang(lang) {
    if (!['no', 'th', 'en'].includes(lang)) lang = DEFAULT;
    document.documentElement.lang = lang;
    try { localStorage.setItem(STORAGE_KEY, lang); } catch {}
    document.querySelectorAll('.lang-switch button').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.setLang === lang);
    });
  }

  // Wire up the language pills
  document.querySelectorAll('.lang-switch button').forEach(btn => {
    btn.addEventListener('click', () => setLang(btn.dataset.setLang));
  });

  // Initial language: saved > browser > default
  let initial = null;
  try { initial = localStorage.getItem(STORAGE_KEY); } catch {}
  if (!initial) {
    const browser = (navigator.language || 'no').toLowerCase();
    if (browser.startsWith('th')) initial = 'th';
    else if (browser.startsWith('en')) initial = 'en';
    else initial = 'no';
  }
  setLang(initial);

  // Google Play link — update when published
  const playUrl = 'https://play.google.com/store/apps/details?id=com.thai2drive.app';
  document.querySelectorAll('#play-store-link, #play-store-link-2').forEach(el => {
    el.href = playUrl;
  });
})();

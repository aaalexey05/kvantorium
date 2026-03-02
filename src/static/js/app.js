(function(){
  const root = document.documentElement;
  const storageKey = 'kv-theme';
  const toggle = document.getElementById('theme-toggle');
  const setTheme = (mode) => {
    root.setAttribute('data-theme', mode);
    localStorage.setItem(storageKey, mode);
  };
  const saved = localStorage.getItem(storageKey);
  if(saved){
    setTheme(saved);
  } else {
    const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    root.setAttribute('data-theme', prefersLight ? 'light' : 'dark');
  }
  if(toggle){
    toggle.addEventListener('click', () => {
      const current = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      setTheme(current);
    });
  }
})();

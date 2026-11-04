document.querySelector('#theme-toggle').addEventListener('click', () => {
    const theme = document.documentElement.dataset.bsTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.bsTheme = theme;
    try { localStorage.setItem('icono-theme', theme); } catch (error) {}
});
document.querySelectorAll('.icono-sidebar nav a').forEach(link => {
    if (new URL(link.href).pathname === location.pathname && !link.hash) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
    }
});

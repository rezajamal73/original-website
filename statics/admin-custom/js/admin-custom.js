// admin-custom/js/admin-custom.js
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.querySelector('[data-lte-toggle="sidebar"]');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // روش ۱: استفاده از کلاس‌های AdminLTE
            document.body.classList.toggle('sidebar-collapse');

            // روش ۲: تغییر مستقیم display برای Jazzmin
            const sidebar = document.querySelector('.app-sidebar, .main-sidebar');
            if (sidebar) {
                if (sidebar.style.display === 'none') {
                    sidebar.style.display = '';
                    sidebar.classList.remove('d-none');
                } else {
                    sidebar.style.display = 'none';
                    sidebar.classList.add('d-none');
                }
            }

            // روش ۳: برای Jazzmin (اگر روش‌های بالا کار نکرد)
            const wrapper = document.querySelector('.app-wrapper');
            if (wrapper) {
                wrapper.classList.toggle('sidebar-open');
            }
        });
    }
});
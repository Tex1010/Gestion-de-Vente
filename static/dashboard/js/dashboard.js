/**
 * Dashboard responsive enhancements
 * - Sidebar toggle on mobile
 * - Touch optimizations
 * - Smooth transitions
 */
(function () {
    'use strict';

    function initDashboard() {
        const sidebar = document.querySelector('.sidebar');
        const topbar = document.querySelector('.topbar');

        if (!sidebar) return;

        // Create hamburger toggle button in topbar
        if (topbar) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'sidebar-toggle';
            toggleBtn.setAttribute('aria-label', 'Menu');
            toggleBtn.setAttribute('type', 'button');
            toggleBtn.innerHTML = '<i class="bi bi-list"></i>';
            
            // Insert at the beginning of topbar-actions or before user-chip
            const topbarActions = topbar.querySelector('.topbar-actions');
            if (topbarActions) {
                topbarActions.insertBefore(toggleBtn, topbarActions.firstChild);
            } else {
                topbar.insertBefore(toggleBtn, topbar.firstChild);
            }

            toggleBtn.addEventListener('click', function () {
                sidebar.classList.toggle('sidebar-open');
                document.body.classList.toggle('sidebar-overlay-active');
            });
        }

        // Create overlay backdrop
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);

        overlay.addEventListener('click', function () {
            sidebar.classList.remove('sidebar-open');
            document.body.classList.remove('sidebar-overlay-active');
        });

        // Close sidebar on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && sidebar.classList.contains('sidebar-open')) {
                sidebar.classList.remove('sidebar-open');
                document.body.classList.remove('sidebar-overlay-active');
            }
        });

        // Close sidebar when a nav link is clicked (on mobile)
        const navLinks = sidebar.querySelectorAll('.sidebar-nav a, .sidebar-footer a');
        navLinks.forEach(function (link) {
            link.addEventListener('click', function () {
                if (window.innerWidth <= 991) {
                    sidebar.classList.remove('sidebar-open');
                    document.body.classList.remove('sidebar-overlay-active');
                }
            });
        });

        // Handle window resize
        let resizeTimer;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function () {
                if (window.innerWidth > 991) {
                    sidebar.classList.remove('sidebar-open');
                    document.body.classList.remove('sidebar-overlay-active');
                }
            }, 250);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDashboard);
    } else {
        initDashboard();
    }
})();
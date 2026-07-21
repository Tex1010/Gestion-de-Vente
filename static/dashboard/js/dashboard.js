/**
 * Dashboard responsive enhancements
 * - Sidebar toggle on mobile (fixed/sticky position)
 * - Logout confirmation modal
 * - Touch optimizations
 * - Smooth transitions
 */
(function () {
    'use strict';

    function initDashboard() {
        const sidebar = document.querySelector('.sidebar');
        const dashboardMain = document.querySelector('.dashboard-main');

        if (!sidebar) return;

        // Create hamburger toggle button in dashboard-main (always visible)
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'sidebar-toggle';
        toggleBtn.setAttribute('aria-label', 'Menu');
        toggleBtn.setAttribute('type', 'button');
        toggleBtn.innerHTML = '<i class="bi bi-list"></i>';
        toggleBtn.id = 'sidebarToggleBtn';
        // Insert at the beginning of dashboard-main
        if (dashboardMain) {
            dashboardMain.insertBefore(toggleBtn, dashboardMain.firstChild);
        }

        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('sidebar-open');
            document.body.classList.toggle('sidebar-overlay-active');
        });

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

        // ===== LOGOUT CONFIRMATION MODAL =====
        initLogoutModal();
    }

    function initLogoutModal() {
        // Use existing modal or create one
        let modalEl = document.getElementById('logoutConfirmModal');
        if (!modalEl) {
            modalEl = document.createElement('div');
            modalEl.className = 'modal fade';
            modalEl.id = 'logoutConfirmModal';
            modalEl.setAttribute('tabindex', '-1');
            modalEl.setAttribute('aria-hidden', 'true');
            modalEl.innerHTML = [
                '<div class="modal-dialog modal-dialog-centered modal-sm">',
                    '<div class="modal-content border-0 shadow-lg" style="border-radius:16px;">',
                        '<div class="modal-body text-center p-4">',
                            '<div class="mb-3">',
                                '<div style="width:64px;height:64px;margin:0 auto;border-radius:50%;background:#fee2e2;display:flex;align-items:center;justify-content:center;">',
                                    '<i class="bi bi-box-arrow-right" style="font-size:1.8rem;color:#ef4444;"></i>',
                                '</div>',
                            '</div>',
                            '<h5 class="fw-bold mb-2">Déconnexion</h5>',
                            '<p class="text-muted mb-4" style="font-size:0.9rem;">Voulez-vous vraiment vous déconnecter ?</p>',
                            '<div class="d-flex gap-2 justify-content-center">',
                                '<button type="button" class="btn btn-outline-secondary px-4 rounded-pill" data-bs-dismiss="modal"><i class="bi bi-x-lg me-1"></i> Annuler</button>',
                                '<a href="#" id="logoutConfirmLink" class="btn btn-danger px-4 rounded-pill"><i class="bi bi-box-arrow-right me-1"></i> Se déconnecter</a>',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>'
            ].join('');
            document.body.appendChild(modalEl);
        }

        // Intercept all logout links
        const linkId = modalEl.querySelector('#logoutConfirmLink') ? 'logoutConfirmLink' : 'logoutConfirmLinkPublic';
        document.querySelectorAll('a[href*="logout"], a[href*="deconnexion"]').forEach(function(link) {
            if (link.getAttribute('data-logout-listener')) return;
            link.setAttribute('data-logout-listener', 'true');
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const modal = new bootstrap.Modal(document.getElementById('logoutConfirmModal'));
                document.getElementById(linkId).href = this.href;
                modal.show();
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDashboard);
    } else {
        initDashboard();
    }
})();
/**
 * Password visibility toggle (eye icon) for all password fields.
 * Automatically converts all password inputs into toggleable fields.
 */
(function () {
    'use strict';

    function initPasswordToggles() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');

        passwordInputs.forEach(function (input) {
            // Skip if already wrapped
            if (input.parentElement && input.parentElement.classList.contains('password-toggle-wrapper')) {
                return;
            }

            // Create wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'password-toggle-wrapper';
            wrapper.style.position = 'relative';
            wrapper.style.display = 'flex';
            wrapper.style.alignItems = 'stretch';

            // Wrap the input
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);

            // Ensure input has proper class
            if (!input.classList.contains('form-control') && !input.classList.contains('form-control-lg')) {
                // Keep existing classes
            }

            // Add padding to the right for the toggle button
            if (input.classList.contains('form-control-lg')) {
                input.style.paddingRight = '3.2rem';
            } else {
                input.style.paddingRight = '2.5rem';
            }

            // Create toggle button
            const toggle = document.createElement('button');
            toggle.type = 'button';
            toggle.className = 'password-toggle-btn';
            toggle.setAttribute('aria-label', 'Afficher/masquer le mot de passe');
            toggle.innerHTML = '<i class="bi bi-eye"></i>';
            toggle.style.cssText = [
                'position: absolute',
                'right: 8px',
                'top: 50%',
                'transform: translateY(-50%)',
                'background: none',
                'border: none',
                'cursor: pointer',
                'padding: 6px',
                'color: #6c757d',
                'z-index: 5',
                'display: flex',
                'align-items: center',
                'justify-content: center',
                'line-height: 1',
            ].join(';');

            // Handle toggle
            toggle.addEventListener('click', function (e) {
                e.preventDefault();
                const isPassword = input.getAttribute('type') === 'password';
                input.setAttribute('type', isPassword ? 'text' : 'password');
                toggle.innerHTML = isPassword
                    ? '<i class="bi bi-eye-slash"></i>'
                    : '<i class="bi bi-eye"></i>';
            });

            wrapper.appendChild(toggle);
        });
    }

    // Run on initial load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPasswordToggles);
    } else {
        initPasswordToggles();
    }

    // Also handle dynamic forms
    if (window.MutationObserver) {
        const observer = new MutationObserver(function () {
            initPasswordToggles();
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }
})();
/**
 * MfalmeBits - Enhanced Main JavaScript
 * High-performance core with advanced appearance functionalities
 * Version 2.1 - Fixed scrollY undefined error
 */

(function() {
    'use strict';

    // ==========================================================================
    // Performance Utilities
    // ==========================================================================

    /**
     * Debounce function for performance optimization
     */
    function debounce(func, wait = 100) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Throttle function for scroll events
     */
    function throttle(func, limit = 100) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * RequestAnimationFrame wrapper for smooth animations
     */
    function smoothAnimation(callback) {
        return function(...args) {
            requestAnimationFrame(() => callback.apply(this, args));
        };
    }

    // ==========================================================================
    // Cached DOM Elements
    // ==========================================================================

    const DOM = {
        body: document.body,
        html: document.documentElement,
        navbar: document.querySelector('.navbar'),
        backToTopBtn: document.querySelector('.back-to-top'),
        mobileMenuBtn: document.querySelector('.mobile-menu-btn'),
        mobileMenu: document.querySelector('.mobile-menu'),
        progressBar: null,
        themeToggle: null
    };

    // ==========================================================================
    // Enhanced Navbar with Smooth Scroll Effect (FIXED)
    // ==========================================================================

    // Create a closure to maintain scroll position state
    const createNavbarScrollHandler = () => {
        let lastScrollY = 0;
        
        return throttle(smoothAnimation(() => {
            const scrollY = window.scrollY || window.pageYOffset;
            
            if (scrollY > 50) {
                DOM.navbar?.classList.add('navbar-scrolled');
                DOM.navbar?.style.setProperty('--scroll-opacity', Math.min(scrollY / 300, 1));
            } else {
                DOM.navbar?.classList.remove('navbar-scrolled');
                DOM.navbar?.style.setProperty('--scroll-opacity', 0);
            }

            // Hide navbar on scroll down, show on scroll up
            if (scrollY > lastScrollY && scrollY > 100) {
                DOM.navbar?.classList.add('navbar-hidden');
            } else {
                DOM.navbar?.classList.remove('navbar-hidden');
            }
            lastScrollY = scrollY;
        }), 50);
    };

    const handleNavbarScroll = createNavbarScrollHandler();
    window.addEventListener('scroll', handleNavbarScroll, { passive: true });

    // ==========================================================================
    // Reading Progress Bar
    // ==========================================================================

    function initProgressBar() {
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress';
        progressBar.innerHTML = '<div class="reading-progress-fill"></div>';
        document.body.appendChild(progressBar);
        DOM.progressBar = progressBar.querySelector('.reading-progress-fill');

        const updateProgress = throttle(() => {
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight - windowHeight;
            if (documentHeight > 0) {
                const scrolled = (window.scrollY / documentHeight) * 100;
                if (DOM.progressBar) {
                    DOM.progressBar.style.width = `${Math.min(scrolled, 100)}%`;
                }
            }
        }, 50);

        window.addEventListener('scroll', updateProgress, { passive: true });
        updateProgress();
    }

    // ==========================================================================
    // Enhanced Back to Top Button with Progress Circle
    // ==========================================================================

    const handleBackToTop = throttle(() => {
        const scrollY = window.scrollY || window.pageYOffset;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight - windowHeight;
        
        if (DOM.backToTopBtn) {
            if (scrollY > 300) {
                DOM.backToTopBtn.classList.add('show');
                if (documentHeight > 0) {
                    const progress = (scrollY / documentHeight) * 100;
                    DOM.backToTopBtn.style.setProperty('--progress', progress);
                }
            } else {
                DOM.backToTopBtn.classList.remove('show');
            }
        }
    }, 50);

    window.addEventListener('scroll', handleBackToTop, { passive: true });

    if (DOM.backToTopBtn) {
        DOM.backToTopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const duration = 800;
            const start = window.scrollY;
            const startTime = performance.now();

            function animation(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Easing function for smooth animation
                const easeInOutCubic = progress < 0.5 
                    ? 4 * progress * progress * progress 
                    : 1 - Math.pow(-2 * progress + 2, 3) / 2;
                
                window.scrollTo(0, start * (1 - easeInOutCubic));
                
                if (progress < 1) {
                    requestAnimationFrame(animation);
                }
            }
            
            requestAnimationFrame(animation);
        });
    }

    // ==========================================================================
    // Enhanced Mobile Menu with Animations
    // ==========================================================================

    if (DOM.mobileMenuBtn) {
        DOM.mobileMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = DOM.mobileMenu?.classList.toggle('show');
            DOM.mobileMenuBtn.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            if (isOpen) {
                DOM.body.style.overflow = 'hidden';
                animateMenuItems();
            } else {
                DOM.body.style.overflow = '';
            }
        });
    }

    function animateMenuItems() {
        const items = DOM.mobileMenu?.querySelectorAll('.nav-link');
        items?.forEach((item, index) => {
            item.style.animation = 'none';
            setTimeout(() => {
                item.style.animation = `slideInRight 0.3s ease forwards ${index * 0.1}s`;
            }, 10);
        });
    }

    // Enhanced click outside handler with touch support
    document.addEventListener('click', (e) => {
        if (DOM.mobileMenu?.classList.contains('show') && 
            !DOM.mobileMenu.contains(e.target) && 
            !DOM.mobileMenuBtn?.contains(e.target)) {
            closeMobileMenu();
        }
    });

    function closeMobileMenu() {
        DOM.mobileMenu?.classList.remove('show');
        DOM.mobileMenuBtn?.classList.remove('active');
        DOM.body.style.overflow = '';
    }

    // ==========================================================================
    // Smooth Scroll with Offset for Fixed Headers
    // ==========================================================================

    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (!href || href === '#') return;
            
            const target = document.querySelector(href);
            
            if (target) {
                e.preventDefault();
                const navbarHeight = DOM.navbar?.offsetHeight || 0;
                const targetPosition = target.getBoundingClientRect().top + window.scrollY - navbarHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Update URL without jumping
                history.pushState(null, '', href);
                
                // Close mobile menu if open
                closeMobileMenu();
            }
        });
    });

    // ==========================================================================
    // Active Navigation Link with Section Detection
    // ==========================================================================

    function setActiveNavLink() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-link');
        
        if (sections.length === 0) {
            // Fallback to path-based detection
            const currentPath = window.location.pathname;
            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href === currentPath || (currentPath === '/' && href === '/')) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
            return;
        }

        const scrollY = window.scrollY + 100;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    const debouncedSetActiveNav = debounce(setActiveNavLink, 100);
    window.addEventListener('scroll', debouncedSetActiveNav, { passive: true });
    document.addEventListener('DOMContentLoaded', setActiveNavLink);

    // ==========================================================================
    // Enhanced Form Validation with Real-time Feedback
    // ==========================================================================

    class FormValidator {
        constructor(form) {
            this.form = form;
            this.inputs = form.querySelectorAll('input, textarea, select');
            this.submitBtn = form.querySelector('[type="submit"]');
            this.init();
        }

        init() {
            this.inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', debounce(() => {
                    this.clearError(input);
                    if (input.value.trim()) {
                        this.validateField(input);
                    }
                }, 300));
                input.addEventListener('focus', () => this.highlightField(input));
            });

            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        validateField(field) {
            const value = field.value.trim();
            let isValid = true;
            let message = '';

            // Required field validation
            if (field.hasAttribute('required') && !value) {
                message = `${this.getFieldLabel(field)} is required`;
                isValid = false;
            }

            // Email validation
            if (isValid && field.type === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    message = 'Please enter a valid email address';
                    isValid = false;
                }
            }

            // Phone validation
            if (isValid && field.type === 'tel' && value) {
                const phoneRegex = /^[\d\s\-\+\(\)]+$/;
                if (!phoneRegex.test(value) || value.length < 10) {
                    message = 'Please enter a valid phone number';
                    isValid = false;
                }
            }

            // URL validation
            if (isValid && field.type === 'url' && value) {
                try {
                    new URL(value);
                } catch {
                    message = 'Please enter a valid URL';
                    isValid = false;
                }
            }

            // Min/Max length validation
            if (isValid && field.hasAttribute('minlength')) {
                const minLength = parseInt(field.getAttribute('minlength'));
                if (value.length < minLength) {
                    message = `Must be at least ${minLength} characters`;
                    isValid = false;
                }
            }

            if (isValid && field.hasAttribute('maxlength')) {
                const maxLength = parseInt(field.getAttribute('maxlength'));
                if (value.length > maxLength) {
                    message = `Must be no more than ${maxLength} characters`;
                    isValid = false;
                }
            }

            // Pattern validation
            if (isValid && field.hasAttribute('pattern') && value) {
                const pattern = new RegExp(field.getAttribute('pattern'));
                if (!pattern.test(value)) {
                    message = field.getAttribute('title') || 'Invalid format';
                    isValid = false;
                }
            }

            if (isValid) {
                this.showSuccess(field);
            } else {
                this.showError(field, message);
            }

            return isValid;
        }

        getFieldLabel(field) {
            const label = field.closest('.form-group')?.querySelector('label');
            return label?.textContent.replace('*', '').trim() || 'This field';
        }

        highlightField(field) {
            field.closest('.form-group')?.classList.add('focused');
        }

        showError(field, message) {
            field.classList.add('error');
            field.classList.remove('success');
            field.closest('.form-group')?.classList.remove('focused');
            
            let errorDiv = field.parentNode.querySelector('.error-message');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                field.parentNode.appendChild(errorDiv);
            }
            
            errorDiv.textContent = message;
            errorDiv.style.animation = 'shake 0.3s ease';
        }

        showSuccess(field) {
            field.classList.remove('error');
            field.classList.add('success');
            this.clearError(field);
        }

        clearError(field) {
            field.classList.remove('error');
            field.closest('.form-group')?.classList.remove('focused');
            const errorDiv = field.parentNode.querySelector('.error-message');
            errorDiv?.remove();
        }

        async handleSubmit(e) {
            e.preventDefault();
            
            let isValid = true;
            this.inputs.forEach(input => {
                if (!this.validateField(input)) {
                    isValid = false;
                }
            });

            if (!isValid) {
                const firstError = this.form.querySelector('.error');
                firstError?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError?.focus();
                return;
            }

            // Show loading state
            this.setLoadingState(true);

            try {
                // Submit form
                const formData = new FormData(this.form);
                const response = await fetch(this.form.action || window.location.href, {
                    method: this.form.method || 'POST',
                    body: formData
                });

                if (response.ok) {
                    if (typeof Toast !== 'undefined') {
                        new Toast('Form submitted successfully!', 'success');
                    }
                    this.form.reset();
                    this.inputs.forEach(input => input.classList.remove('success'));
                } else {
                    throw new Error('Submission failed');
                }
            } catch (error) {
                if (typeof Toast !== 'undefined') {
                    new Toast('Failed to submit form. Please try again.', 'error');
                }
                console.error('Form submission error:', error);
            } finally {
                this.setLoadingState(false);
            }
        }

        setLoadingState(loading) {
            if (this.submitBtn) {
                this.submitBtn.disabled = loading;
                if (loading) {
                    this.submitBtn.dataset.originalText = this.submitBtn.textContent;
                    this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
                } else {
                    this.submitBtn.textContent = this.submitBtn.dataset.originalText || 'Submit';
                }
            }
        }
    }

    // Initialize form validation
    document.querySelectorAll('form.validate').forEach(form => {
        new FormValidator(form);
    });

    // ==========================================================================
    // Advanced Lazy Loading with Blur-Up Effect
    // ==========================================================================

    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                const src = img.dataset.src;
                
                if (src) {
                    // Create temporary image to preload
                    const tempImg = new Image();
                    tempImg.onload = () => {
                        img.src = src;
                        img.classList.add('loaded');
                        
                        // Animate fade-in
                        img.style.animation = 'fadeIn 0.5s ease';
                    };
                    tempImg.onerror = () => {
                        img.classList.add('error');
                        console.error('Failed to load image:', src);
                    };
                    tempImg.src = src;
                    
                    imageObserver.unobserve(img);
                }
            }
        });
    }, {
        rootMargin: '50px',
        threshold: 0.01
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        // Add blur effect while loading
        img.style.filter = 'blur(10px)';
        img.style.transition = 'filter 0.3s ease';
        
        img.addEventListener('load', () => {
            img.style.filter = 'blur(0)';
        });
        
        imageObserver.observe(img);
    });

    // ==========================================================================
    // Enhanced Copy to Clipboard with Animation
    // ==========================================================================

    document.querySelectorAll('[data-copy]').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const text = this.dataset.copy;
            
            try {
                await navigator.clipboard.writeText(text);
                
                // Ripple effect
                createRipple(e, this);
                
                // Show success animation
                const originalHTML = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                this.classList.add('success');
                
                setTimeout(() => {
                    this.innerHTML = originalHTML;
                    this.classList.remove('success');
                }, 2000);
                
                if (typeof Toast !== 'undefined') {
                    new Toast('Copied to clipboard!', 'success', 1500);
                }
            } catch (err) {
                console.error('Failed to copy:', err);
                if (typeof Toast !== 'undefined') {
                    new Toast('Failed to copy to clipboard', 'error');
                }
            }
        });
    });

    // ==========================================================================
    // Ripple Effect for Buttons
    // ==========================================================================

    function createRipple(event, element) {
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    // Add ripple effect to all buttons
    document.querySelectorAll('.btn, button').forEach(btn => {
        if (!btn.hasAttribute('data-no-ripple')) {
            btn.addEventListener('click', (e) => createRipple(e, btn));
        }
    });

    // ==========================================================================
    // Enhanced Toast Notifications with Queue System
    // ==========================================================================

    class Toast {
        static queue = [];
        static isShowing = false;

        constructor(message, type = 'info', duration = 3000) {
            this.message = message;
            this.type = type;
            this.duration = duration;
            
            Toast.queue.push(this);
            if (!Toast.isShowing) {
                this.show();
            }
        }

        show() {
            Toast.isShowing = true;
            
            const toast = document.createElement('div');
            toast.className = `toast toast-${this.type}`;
            toast.innerHTML = `
                <div class="toast-icon">
                    <i class="fas ${this.getIcon()}"></i>
                </div>
                <div class="toast-content">
                    <span class="toast-message">${this.message}</span>
                </div>
                <button class="toast-close" aria-label="Close">
                    <i class="fas fa-times"></i>
                </button>
            `;

            const container = document.querySelector('.toast-container') || this.createContainer();
            container.appendChild(toast);

            // Animate in
            requestAnimationFrame(() => {
                toast.classList.add('toast-show');
            });

            // Close button
            toast.querySelector('.toast-close').addEventListener('click', () => {
                this.hide(toast);
            });

            // Auto hide
            setTimeout(() => {
                this.hide(toast);
            }, this.duration);

            // Add progress bar
            if (this.duration > 0) {
                const progress = document.createElement('div');
                progress.className = 'toast-progress';
                progress.style.animationDuration = `${this.duration}ms`;
                toast.appendChild(progress);
            }
        }

        hide(toast) {
            toast.classList.add('toast-hide');
            setTimeout(() => {
                toast.remove();
                Toast.isShowing = false;
                
                // Show next toast in queue
                Toast.queue.shift();
                if (Toast.queue.length > 0) {
                    Toast.queue[0].show();
                }
            }, 300);
        }

        getIcon() {
            const icons = {
                success: 'fa-check-circle',
                error: 'fa-exclamation-circle',
                warning: 'fa-exclamation-triangle',
                info: 'fa-info-circle'
            };
            return icons[this.type] || icons.info;
        }

        createContainer() {
            const container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
            return container;
        }
    }

    window.Toast = Toast;

    // ==========================================================================
    // Dark Mode Toggle (with error handling)
    // ==========================================================================

    class DarkModeManager {
        constructor() {
            this.theme = localStorage.getItem('theme') || 'light';
            this.init();
        }

        init() {
            this.applyTheme();
            this.createToggle();
        }

        createToggle() {
            const toggle = document.createElement('button');
            toggle.className = 'theme-toggle';
            toggle.setAttribute('aria-label', 'Toggle dark mode');
            toggle.innerHTML = `
                <i class="fas fa-moon"></i>
                <i class="fas fa-sun"></i>
            `;
            
            document.body.appendChild(toggle);
            DOM.themeToggle = toggle;

            toggle.addEventListener('click', () => this.toggleTheme());
        }

        toggleTheme() {
            this.theme = this.theme === 'light' ? 'dark' : 'light';
            this.applyTheme();
            localStorage.setItem('theme', this.theme);
            
            if (typeof Toast !== 'undefined') {
                new Toast(`${this.theme === 'dark' ? 'Dark' : 'Light'} mode activated`, 'info', 1500);
            }
        }

        applyTheme() {
            document.documentElement.setAttribute('data-theme', this.theme);
            if (DOM.themeToggle) {
                DOM.themeToggle.classList.toggle('dark', this.theme === 'dark');
            }
        }
    }

    // Initialize dark mode (only if not already present)
    if (!document.querySelector('.theme-toggle')) {
        new DarkModeManager();
    }

    // ==========================================================================
    // Scroll Animations (Fade In on Scroll)
    // ==========================================================================

    const scrollAnimationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                scrollAnimationObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.fade-in, .slide-in-left, .slide-in-right, .slide-in-up').forEach(el => {
        scrollAnimationObserver.observe(el);
    });

    // ==========================================================================
    // Modal System
    // ==========================================================================

    class Modal {
        constructor(options = {}) {
            this.title = options.title || '';
            this.content = options.content || '';
            this.size = options.size || 'medium';
            this.closeOnBackdrop = options.closeOnBackdrop !== false;
            this.showCloseBtn = options.showCloseBtn !== false;
            this.onClose = options.onClose || null;
            this.create();
        }

        create() {
            this.modal = document.createElement('div');
            this.modal.className = `modal modal-${this.size}`;
            this.modal.innerHTML = `
                <div class="modal-backdrop"></div>
                <div class="modal-dialog">
                    <div class="modal-content">
                        ${this.title ? `
                            <div class="modal-header">
                                <h3 class="modal-title">${this.title}</h3>
                                ${this.showCloseBtn ? '<button class="modal-close" aria-label="Close"><i class="fas fa-times"></i></button>' : ''}
                            </div>
                        ` : ''}
                        <div class="modal-body">
                            ${this.content}
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(this.modal);

            // Event listeners
            if (this.closeOnBackdrop) {
                this.modal.querySelector('.modal-backdrop')?.addEventListener('click', () => this.close());
            }

            this.modal.querySelector('.modal-close')?.addEventListener('click', () => this.close());

            // Keyboard support
            this.handleKeydown = (e) => {
                if (e.key === 'Escape') this.close();
            };
            document.addEventListener('keydown', this.handleKeydown);

            // Show modal
            requestAnimationFrame(() => {
                this.modal.classList.add('show');
                DOM.body.style.overflow = 'hidden';
            });
        }

        close() {
            this.modal.classList.remove('show');
            document.removeEventListener('keydown', this.handleKeydown);
            
            setTimeout(() => {
                this.modal.remove();
                DOM.body.style.overflow = '';
                if (this.onClose) this.onClose();
            }, 300);
        }

        static confirm(message, title = 'Confirm') {
            return new Promise((resolve) => {
                const modal = new Modal({
                    title: title,
                    content: `
                        <p>${message}</p>
                        <div class="modal-actions">
                            <button class="btn btn-secondary" data-action="cancel">Cancel</button>
                            <button class="btn btn-primary" data-action="confirm">Confirm</button>
                        </div>
                    `,
                    size: 'small',
                    closeOnBackdrop: false
                });

                modal.modal.querySelector('[data-action="confirm"]').addEventListener('click', () => {
                    modal.close();
                    resolve(true);
                });

                modal.modal.querySelector('[data-action="cancel"]').addEventListener('click', () => {
                    modal.close();
                    resolve(false);
                });
            });
        }
    }

    window.Modal = Modal;

    // Initialize modals from data attributes
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(trigger.dataset.modal);
            if (target) {
                new Modal({
                    title: target.dataset.title || '',
                    content: target.innerHTML,
                    size: target.dataset.size || 'medium'
                });
            }
        });
    });

    // ==========================================================================
    // Dropdown System
    // ==========================================================================

    document.querySelectorAll('.dropdown').forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (toggle && menu) {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('open');
            });

            // Close on outside click
            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target)) {
                    dropdown.classList.remove('open');
                }
            });
        }
    });

    // ==========================================================================
    // Tabs System
    // ==========================================================================

    document.querySelectorAll('.tabs').forEach(tabGroup => {
        const tabs = tabGroup.querySelectorAll('.tab');
        const contents = tabGroup.querySelectorAll('.tab-content');

        tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                
                tab.classList.add('active');
                if (contents[index]) contents[index].classList.add('active');
            });
        });
    });

    // ==========================================================================
    // Accordion System
    // ==========================================================================

    document.querySelectorAll('.accordion').forEach(accordion => {
        const items = accordion.querySelectorAll('.accordion-item');

        items.forEach(item => {
            const header = item.querySelector('.accordion-header');
            const content = item.querySelector('.accordion-content');

            if (header && content) {
                header.addEventListener('click', () => {
                    const isOpen = item.classList.contains('open');

                    // Close all items if single mode
                    if (accordion.hasAttribute('data-single')) {
                        items.forEach(i => i.classList.remove('open'));
                    }

                    // Toggle current item
                    item.classList.toggle('open', !isOpen);
                });
            }
        });
    });

    // ==========================================================================
    // Tooltip System
    // ==========================================================================

    document.querySelectorAll('[data-tooltip]').forEach(element => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = element.dataset.tooltip;
        
        const position = element.dataset.tooltipPosition || 'top';
        tooltip.classList.add(`tooltip-${position}`);

        element.addEventListener('mouseenter', () => {
            document.body.appendChild(tooltip);
            const rect = element.getBoundingClientRect();
            
            switch(position) {
                case 'top':
                    tooltip.style.left = `${rect.left + rect.width / 2}px`;
                    tooltip.style.top = `${rect.top - 10}px`;
                    break;
                case 'bottom':
                    tooltip.style.left = `${rect.left + rect.width / 2}px`;
                    tooltip.style.top = `${rect.bottom + 10}px`;
                    break;
                case 'left':
                    tooltip.style.left = `${rect.left - 10}px`;
                    tooltip.style.top = `${rect.top + rect.height / 2}px`;
                    break;
                case 'right':
                    tooltip.style.left = `${rect.right + 10}px`;
                    tooltip.style.top = `${rect.top + rect.height / 2}px`;
                    break;
            }
            
            requestAnimationFrame(() => tooltip.classList.add('show'));
        });

        element.addEventListener('mouseleave', () => {
            tooltip.classList.remove('show');
            setTimeout(() => tooltip.remove(), 200);
        });
    });

    // ==========================================================================
    // Loading Overlay
    // ==========================================================================

    window.showLoading = function(message = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'globalLoadingOverlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
        requestAnimationFrame(() => overlay.classList.add('show'));
    };

    window.hideLoading = function() {
        const overlay = document.getElementById('globalLoadingOverlay');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => overlay.remove(), 300);
        }
    };

    // ==========================================================================
    // Keyboard Shortcuts
    // ==========================================================================

    const shortcuts = {
        'ctrl+k': () => {
            const searchInput = document.querySelector('.search-input, [type="search"]');
            searchInput?.focus();
        },
        'ctrl+/': () => {
            if (typeof Modal !== 'undefined') {
                new Modal({
                    title: 'Keyboard Shortcuts',
                    content: `
                        <div class="shortcuts-list">
                            <div class="shortcut-item">
                                <kbd>Ctrl</kbd> + <kbd>K</kbd>
                                <span>Focus Search</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Ctrl</kbd> + <kbd>/</kbd>
                                <span>Show Shortcuts</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Esc</kbd>
                                <span>Close Modal</span>
                            </div>
                        </div>
                    `,
                    size: 'small'
                });
            }
        }
    };

    document.addEventListener('keydown', (e) => {
        const key = `${e.ctrlKey ? 'ctrl+' : ''}${e.key.toLowerCase()}`;
        if (shortcuts[key]) {
            e.preventDefault();
            shortcuts[key]();
        }
    });

    // ==========================================================================
    // Performance Monitoring
    // ==========================================================================

    if ('PerformanceObserver' in window) {
        try {
            const perfObserver = new PerformanceObserver((list) => {
                list.getEntries().forEach((entry) => {
                    if (entry.entryType === 'largest-contentful-paint') {
                        console.log('LCP:', entry.renderTime || entry.loadTime);
                    }
                });
            });
            perfObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        } catch (e) {
            console.debug('PerformanceObserver not supported');
        }
    }

    // ==========================================================================
    // Initialize Progress Bar
    // ==========================================================================

    initProgressBar();

    // ==========================================================================
    // Page Load Complete
    // ==========================================================================

    window.addEventListener('load', () => {
        document.body.classList.add('loaded');
        console.log('MfalmeBits Enhanced v2.1 - Ready! 🚀');
    });

    // ==========================================================================
    // Dashboard Specific Functions
    // ==========================================================================

    if (document.querySelector('.dashboard-content')) {
        console.log('Dashboard mode activated');
    }

})();
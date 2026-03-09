/**
 * MfalmeBits - Premium Animations
 * Inspired by Slider Revolution
 */

(function() {
    'use strict';

    // ==========================================================================
    // Initialize Animations
    // ==========================================================================

    class AnimationManager {
        constructor() {
            this.initScrollReveal();
            this.initParallax();
            this.initTextReveal();
            this.initCounter();
            this.initTypingEffect();
            this.initMagneticButtons();
            this.initTiltEffect();
            this.initParticles();
            this.initScrollProgress();
        }

        // ==========================================================================
        // Scroll Reveal Animations
        // ==========================================================================

        initScrollReveal() {
            const revealElements = document.querySelectorAll('.reveal');
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('revealed');
                        
                        // Stagger children if present
                        const staggerChildren = entry.target.querySelectorAll('.stagger-child');
                        staggerChildren.forEach((child, index) => {
                            child.style.animationDelay = `${index * 0.1}s`;
                            child.classList.add('animate-fade-up');
                        });
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            revealElements.forEach(el => observer.observe(el));
        }

        // ==========================================================================
        // Parallax Effects
        // ==========================================================================

        initParallax() {
            const parallaxElements = document.querySelectorAll('.parallax-bg');
            
            window.addEventListener('scroll', () => {
                const scrollY = window.scrollY;
                
                parallaxElements.forEach(el => {
                    const speed = el.dataset.speed || 0.5;
                    el.style.transform = `translateY(${scrollY * speed}px)`;
                });
            });
        }

        // ==========================================================================
        // Text Reveal Animation
        // ==========================================================================

        initTextReveal() {
            const textRevealElements = document.querySelectorAll('.text-reveal');
            
            textRevealElements.forEach(el => {
                const text = el.textContent;
                const words = text.split(' ');
                
                el.innerHTML = words.map(word => 
                    `<span class="word"><span class="char">${word}</span></span>`
                ).join(' ');
                
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const chars = entry.target.querySelectorAll('.char');
                            chars.forEach((char, index) => {
                                char.style.animation = `textReveal 0.5s ease forwards ${index * 0.02}s`;
                            });
                        }
                    });
                });
                
                observer.observe(el);
            });
        }

        // ==========================================================================
        // Counter Animation
        // ==========================================================================

        initCounter() {
            const counters = document.querySelectorAll('.counter');
            
            counters.forEach(counter => {
                const target = parseInt(counter.dataset.target);
                const duration = parseInt(counter.dataset.duration) || 2000;
                const step = target / (duration / 16);
                let current = 0;
                
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const timer = setInterval(() => {
                                current += step;
                                if (current >= target) {
                                    counter.textContent = target;
                                    clearInterval(timer);
                                } else {
                                    counter.textContent = Math.floor(current);
                                }
                            }, 16);
                        }
                    });
                });
                
                observer.observe(counter);
            });
        }

        // ==========================================================================
        // Typing Effect
        // ==========================================================================

        initTypingEffect() {
            const typingElements = document.querySelectorAll('.typing-effect');
            
            typingElements.forEach(el => {
                const words = el.dataset.words ? JSON.parse(el.dataset.words) : [];
                const typeSpeed = parseInt(el.dataset.typeSpeed) || 100;
                const deleteSpeed = parseInt(el.dataset.deleteSpeed) || 50;
                const delayBetween = parseInt(el.dataset.delayBetween) || 2000;
                
                let wordIndex = 0;
                let charIndex = 0;
                let isDeleting = false;
                
                function type() {
                    const currentWord = words[wordIndex];
                    
                    if (isDeleting) {
                        el.textContent = currentWord.substring(0, charIndex - 1);
                        charIndex--;
                    } else {
                        el.textContent = currentWord.substring(0, charIndex + 1);
                        charIndex++;
                    }
                    
                    if (!isDeleting && charIndex === currentWord.length) {
                        isDeleting = true;
                        setTimeout(type, delayBetween);
                    } else if (isDeleting && charIndex === 0) {
                        isDeleting = false;
                        wordIndex = (wordIndex + 1) % words.length;
                        setTimeout(type, 500);
                    } else {
                        setTimeout(type, isDeleting ? deleteSpeed : typeSpeed);
                    }
                }
                
                type();
            });
        }

        // ==========================================================================
        // Magnetic Buttons
        // ==========================================================================

        initMagneticButtons() {
            const buttons = document.querySelectorAll('.magnetic-btn');
            
            buttons.forEach(btn => {
                btn.addEventListener('mousemove', (e) => {
                    const rect = btn.getBoundingClientRect();
                    const x = e.clientX - rect.left - rect.width / 2;
                    const y = e.clientY - rect.top - rect.height / 2;
                    
                    btn.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
                });
                
                btn.addEventListener('mouseleave', () => {
                    btn.style.transform = 'translate(0, 0)';
                });
            });
        }

        // ==========================================================================
        // Tilt Effect
        // ==========================================================================

        initTiltEffect() {
            const tiltElements = document.querySelectorAll('[data-tilt]');
            
            tiltElements.forEach(el => {
                el.addEventListener('mousemove', (e) => {
                    const rect = el.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    const xPercent = x / rect.width - 0.5;
                    const yPercent = y / rect.height - 0.5;
                    
                    const rotateX = yPercent * 10;
                    const rotateY = xPercent * 10;
                    
                    el.style.transform = `perspective(1000px) rotateX(${-rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
                });
                
                el.addEventListener('mouseleave', () => {
                    el.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
                });
            });
        }

        // ==========================================================================
        // Particles Background
        // ==========================================================================

        initParticles() {
            const particlesContainers = document.querySelectorAll('.particles');
            
            particlesContainers.forEach(container => {
                const particleCount = parseInt(container.dataset.particles) || 50;
                
                for (let i = 0; i < particleCount; i++) {
                    const particle = document.createElement('div');
                    particle.className = 'particle';
                    
                    const size = Math.random() * 5 + 2;
                    const posX = Math.random() * 100;
                    const posY = Math.random() * 100;
                    const delay = Math.random() * 5;
                    const duration = Math.random() * 10 + 10;
                    
                    particle.style.cssText = `
                        width: ${size}px;
                        height: ${size}px;
                        left: ${posX}%;
                        top: ${posY}%;
                        animation-delay: ${delay}s;
                        animation-duration: ${duration}s;
                        opacity: ${Math.random() * 0.3 + 0.1};
                        background: rgba(255, 255, 255, ${Math.random() * 0.3});
                        box-shadow: 0 0 ${size * 2}px rgba(255, 255, 255, 0.3);
                    `;
                    
                    container.appendChild(particle);
                }
            });
        }

        // ==========================================================================
        // Scroll Progress
        // ==========================================================================

        initScrollProgress() {
            const progressBar = document.querySelector('.scroll-progress-bar');
            
            if (progressBar) {
                window.addEventListener('scroll', () => {
                    const winScroll = document.documentElement.scrollTop;
                    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                    const scrolled = (winScroll / height) * 100;
                    
                    progressBar.style.width = scrolled + '%';
                });
            }
        }
    }

    // ==========================================================================
    // Initialize when DOM is ready
    // ==========================================================================

    document.addEventListener('DOMContentLoaded', () => {
        new AnimationManager();
    });

})();
/**
 * MfalmeBits Lazy Loading Module
 */

class LazyLoader {
    constructor() {
        this.observer = null;
        this.images = [];
        this.iframes = [];
        this.backgrounds = [];
        this.init();
    }
    
    init() {
        // Check if IntersectionObserver is supported
        if (!('IntersectionObserver' in window)) {
            this.loadAll();
            return;
        }
        
        // Create observer
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    
                    if (element.tagName === 'IMG') {
                        this.loadImage(element);
                    } else if (element.tagName === 'IFRAME') {
                        this.loadIframe(element);
                    } else if (element.classList.contains('lazy-background')) {
                        this.loadBackground(element);
                    }
                    
                    this.observer.unobserve(element);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });
        
        // Find all lazy elements
        this.findLazyElements();
        this.observeElements();
    }
    
    findLazyElements() {
        // Images
        this.images = document.querySelectorAll('img[data-src], img[data-srcset]');
        
        // Iframes
        this.iframes = document.querySelectorAll('iframe[data-src]');
        
        // Backgrounds
        this.backgrounds = document.querySelectorAll('.lazy-background');
    }
    
    observeElements() {
        this.images.forEach(img => this.observer.observe(img));
        this.iframes.forEach(iframe => this.observer.observe(iframe));
        this.backgrounds.forEach(bg => this.observer.observe(bg));
    }
    
    loadImage(img) {
        // Handle srcset
        if (img.dataset.srcset) {
            img.srcset = img.dataset.srcset;
        }
        
        // Handle src
        if (img.dataset.src) {
            img.src = img.dataset.src;
        }
        
        // Handle sizes
        if (img.dataset.sizes) {
            img.sizes = img.dataset.sizes;
        }
        
        img.classList.add('loaded');
        
        // Emit event
        img.dispatchEvent(new CustomEvent('lazy-loaded', { 
            detail: { element: img } 
        }));
    }
    
    loadIframe(iframe) {
        iframe.src = iframe.dataset.src;
        iframe.classList.add('loaded');
        
        iframe.dispatchEvent(new CustomEvent('lazy-loaded', { 
            detail: { element: iframe } 
        }));
    }
    
    loadBackground(element) {
        if (element.dataset.bg) {
            element.style.backgroundImage = `url(${element.dataset.bg})`;
        }
        
        element.classList.add('loaded');
        
        element.dispatchEvent(new CustomEvent('lazy-loaded', { 
            detail: { element: element } 
        }));
    }
    
    loadAll() {
        // Fallback for browsers without IntersectionObserver
        this.images.forEach(img => this.loadImage(img));
        this.iframes.forEach(iframe => this.loadIframe(iframe));
        this.backgrounds.forEach(bg => this.loadBackground(bg));
    }
    
    refresh() {
        // Reinitialize for dynamically added content
        this.findLazyElements();
        this.observeElements();
    }
}

// Initialize lazy loader
const lazyLoader = new LazyLoader();

// Export for use in other modules
window.lazyLoader = lazyLoader;

/**
 * Progressive Image Loading
 */
class ProgressiveImage {
    constructor() {
        this.init();
    }
    
    init() {
        document.querySelectorAll('img[data-progressive]').forEach(img => {
            const wrapper = document.createElement('div');
            wrapper.className = 'progressive-image';
            
            // Create low quality placeholder
            const placeholder = document.createElement('img');
            placeholder.className = 'progressive-placeholder';
            placeholder.src = img.dataset.placeholder || '';
            
            // Wrap image
            img.parentNode.insertBefore(wrapper, img);
            wrapper.appendChild(placeholder);
            wrapper.appendChild(img);
            
            // Load high quality image
            const highRes = new Image();
            highRes.src = img.dataset.src || img.src;
            
            highRes.onload = () => {
                img.src = highRes.src;
                img.classList.add('loaded');
                placeholder.classList.add('fade-out');
                
                setTimeout(() => {
                    placeholder.remove();
                }, 500);
            };
        });
    }
}

// Initialize progressive images
if (document.querySelector('[data-progressive]')) {
    new ProgressiveImage();
}

/**
 * Video Lazy Loading
 */
class LazyVideo {
    constructor() {
        this.videos = document.querySelectorAll('video[data-src]');
        this.init();
    }
    
    init() {
        if (!('IntersectionObserver' in window)) {
            this.loadAll();
            return;
        }
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadVideo(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '100px'
        });
        
        this.videos.forEach(video => observer.observe(video));
    }
    
    loadVideo(video) {
        if (video.dataset.src) {
            const source = document.createElement('source');
            source.src = video.dataset.src;
            source.type = video.dataset.type || 'video/mp4';
            video.appendChild(source);
        }
        
        // Load poster if exists
        if (video.dataset.poster) {
            video.poster = video.dataset.poster;
        }
        
        video.load();
        video.classList.add('loaded');
        
        video.dispatchEvent(new CustomEvent('lazy-loaded', { 
            detail: { element: video } 
        }));
    }
    
    loadAll() {
        this.videos.forEach(video => this.loadVideo(video));
    }
}

// Initialize lazy videos
if (document.querySelector('video[data-src]')) {
    new LazyVideo();
}

/**
 * Background Image Lazy Loading with Blur-up Effect
 */
class BlurUpBackground {
    constructor() {
        this.init();
    }
    
    init() {
        document.querySelectorAll('[data-blur-up]').forEach(element => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadHighRes(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '50px'
            });
            
            observer.observe(element);
        });
    }
    
    loadHighRes(element) {
        const highResUrl = element.dataset.blurUp;
        
        // Load high-res image
        const img = new Image();
        img.src = highResUrl;
        
        img.onload = () => {
            element.style.backgroundImage = `url(${highResUrl})`;
            element.classList.add('high-res-loaded');
        };
    }
}

// Initialize blur-up backgrounds
if (document.querySelector('[data-blur-up]')) {
    new BlurUpBackground();
}

/**
 * Auto-refresh for dynamic content
 */
document.addEventListener('DOMContentLoaded', () => {
    // Listen for content updates
    document.addEventListener('content-updated', () => {
        if (window.lazyLoader) {
            window.lazyLoader.refresh();
        }
    });
});

/**
 * Performance monitoring for lazy loading
 */
class LazyLoadMonitor {
    constructor() {
        this.loadedCount = 0;
        this.totalCount = document.querySelectorAll('[data-src], [data-srcset], .lazy-background, video[data-src]').length;
        
        document.addEventListener('lazy-loaded', (e) => {
            this.loadedCount++;
            this.updateProgress();
        });
    }
    
    updateProgress() {
        const progress = (this.loadedCount / this.totalCount) * 100;
        
        // Dispatch progress event
        window.dispatchEvent(new CustomEvent('lazy-load-progress', {
            detail: {
                loaded: this.loadedCount,
                total: this.totalCount,
                progress: progress
            }
        }));
        
        if (this.loadedCount === this.totalCount) {
            window.dispatchEvent(new CustomEvent('all-lazy-loaded'));
        }
    }
}

// Initialize monitor
if (document.querySelector('[data-src], [data-srcset], .lazy-background, video[data-src]')) {
    new LazyLoadMonitor();
}
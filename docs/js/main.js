// AlexBET Checker - Main JavaScript

// Initialize Lucide icons
lucide.createIcons();

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Header scroll effect
const header = document.querySelector('.header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        header.style.background = 'rgba(10, 10, 10, 0.95)';
        header.style.boxShadow = '0 4px 24px rgba(0, 0, 0, 0.4)';
    } else {
        header.style.background = 'rgba(10, 10, 10, 0.8)';
        header.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.feature-card, .step, .example-card, .roadmap-item, .faq-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// FAQ Accordion
document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', () => {
        const card = question.parentElement;
        const isActive = card.classList.contains('active');
        
        // Close all FAQs
        document.querySelectorAll('.faq-card').forEach(c => {
            c.classList.remove('active');
        });
        
        // Open clicked FAQ if it wasn't already open
        if (!isActive) {
            card.classList.add('active');
        }
    });
});

// Track CTA clicks (Analytics)
document.querySelectorAll('[href*="whop.com"]').forEach(btn => {
    btn.addEventListener('click', () => {
        // Google Analytics event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'cta_click', {
                'event_category': 'conversion',
                'event_label': 'Whop Sales Page',
                'value': 1
            });
        }
        console.log('CTA clicked: Whop Sales Page');
    });
});

// Track demo views
const demoSection = document.querySelector('.demo');
if (demoSection) {
    const demoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && typeof gtag !== 'undefined') {
                gtag('event', 'demo_view', {
                    'event_category': 'engagement',
                    'event_label': 'Demo Section Viewed'
                });
                demoObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    demoObserver.observe(demoSection);
}

// Mobile menu toggle
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        mobileMenuBtn.classList.toggle('active');
    });
}

// Add active state to nav links based on scroll position
const sections = document.querySelectorAll('section[id]');

window.addEventListener('scroll', () => {
    const scrollY = window.pageYOffset;
    
    sections.forEach(section => {
        const sectionHeight = section.offsetHeight;
        const sectionTop = section.offsetTop - 100;
        const sectionId = section.getAttribute('id');
        const navLink = document.querySelector(`.nav-links a[href="#${sectionId}"]`);
        
        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            navLink?.classList.add('active');
        } else {
            navLink?.classList.remove('active');
        }
    });
});

// Add mobile menu styles dynamically
const style = document.createElement('style');
style.textContent = `
    @media (max-width: 768px) {
        .nav-links.active {
            display: flex;
            flex-direction: column;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: rgba(10, 10, 10, 0.98);
            backdrop-filter: blur(20px);
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
            gap: 16px;
        }
        
        .mobile-menu-btn.active i {
            transform: rotate(90deg);
            transition: transform 0.3s ease;
        }
    }
`;
document.head.appendChild(style);

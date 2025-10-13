// scripts/main.js
document.addEventListener('DOMContentLoaded', function() {
    
    // --- Page Loader Logic ---
    const loader = document.getElementById('loader');
    if (loader) {
        // If a loader exists, wait for the page to be fully loaded (including images)
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.body.classList.add('loaded');
            }, 250); // A brief delay for smoother transition
        });
    } else {
        // If there is no loader, show the content immediately
        document.body.classList.add('loaded');
    }

    // --- Mobile Navigation Toggle ---
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
        });
    }

    // --- NEW & MORE RELIABLE ANIMATION LOGIC ---
    // This targets every element that needs to be animated directly.
    const animatedElements = document.querySelectorAll('.animate-on-load, .animate-on-scroll');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            // When an element comes into view...
            if (entry.isIntersecting) {
                // Add the 'is-visible' class to trigger the CSS animation.
                entry.target.classList.add('is-visible');
                // Stop observing it so the animation only happens once.
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1 // Trigger when 10% of the element is visible
    });

    // Tell the observer to watch each of the animated elements.
    animatedElements.forEach(el => {
        observer.observe(el);
    });

});
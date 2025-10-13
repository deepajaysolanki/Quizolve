document.addEventListener('DOMContentLoaded', function() {
    
    // This function loads a component like the navbar or footer
    const loadComponent = (url, placeholderId, callback) => {
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error(`Failed to load component: ${url}`);
                return response.text();
            })
            .then(data => {
                const placeholder = document.getElementById(placeholderId);
                if (placeholder) placeholder.innerHTML = data;
                if (callback) callback();
            })
            .catch(error => console.error(error));
    };

    // This function runs AFTER the navbar HTML has been loaded
    const initializeNavbar = () => {
        // --- Mobile Menu Toggle Logic ---
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        if (mobileMenuBtn && mobileMenu) {
            mobileMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.toggle('active');
            });
        }

        // --- NEW & CORRECTED LOGIC FOR HIGHLIGHTING THE ACTIVE LINK ---
        const navLinks = document.querySelectorAll('.nav-link, .mobile-link');
        // Get the end part of the current page's URL (e.g., 'about.html')
        const currentPage = window.location.pathname.split('/').pop();

        navLinks.forEach(link => {
            const linkPage = link.getAttribute('href');

            // Remove any existing 'active' class first
            link.classList.remove('active');

            // Handle the homepage case (where currentPage might be 'index.html' or empty)
            if ((currentPage === 'index.html' || currentPage === '') && (linkPage === 'index.html' || linkPage === '/')) {
                link.classList.add('active');
            }
            // Handle all other pages
            else if (linkPage === currentPage) {
                link.classList.add('active');
            }
        });
    };

    // Load the navbar, and once it's done, run the script to make it work
    loadComponent('components/navbar.html', 'navbar-placeholder', initializeNavbar);
    
    // Load the footer
    loadComponent('components/footer.html', 'footer-placeholder');
});
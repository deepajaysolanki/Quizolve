document.addEventListener('DOMContentLoaded', function () {

    // =========================================
    // 1. PAGE  LOGIC
    // =========================================
    const loader = document.getElementById('loader');
    if (loader) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.body.classList.add('loaded');
            }, 250);
        });
    } else {
        document.body.classList.add('loaded');
    }

    // =========================================
    // 2. MOBILE MENU TOGGLE
    // =========================================
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuBtn && mobileMenu) {
        // Clone button to remove any old conflicting event listeners
        const newBtn = mobileMenuBtn.cloneNode(true);
        mobileMenuBtn.parentNode.replaceChild(newBtn, mobileMenuBtn);

        newBtn.addEventListener("click", (e) => {
            e.stopPropagation(); // Prevents "click outside" from closing it immediately
            mobileMenu.classList.toggle("active");
        });
    }

    // =========================================
    // 3. PROFILE DROPDOWN LOGIC
    // =========================================
    function setupDropdown(btnId, menuId) {
        const btn = document.getElementById(btnId);
        const menu = document.getElementById(menuId);

        if (!btn || !menu) return;

        // Clone button to ensure a clean slate
        const newButton = btn.cloneNode(true);
        btn.parentNode.replaceChild(newButton, btn);

        newButton.addEventListener('click', (event) => {
            event.stopPropagation(); // Stop click from bubbling to document

            // Close other open menus (optional, keeps things clean)
            document.querySelectorAll('.profile-dropdown-card.show').forEach(el => {
                if (el !== menu) el.classList.remove('show');
            });

            menu.classList.toggle('show');
        });
    }

    setupDropdown('profile-photo-desktop', 'profile-dropdown-desktop');
    setupDropdown('profile-photo-mobile', 'profile-dropdown-mobile');

    // =========================================
    // 4. GLOBAL "CLICK OUTSIDE" LISTENER
    // =========================================
    document.addEventListener("click", (e) => {
        // A. Close Mobile Menu if clicking outside
        if (mobileMenu && mobileMenu.classList.contains('active')) {
            const btn = document.getElementById('mobile-menu-btn'); // Get the new button ref
            if (!mobileMenu.contains(e.target) && !btn.contains(e.target)) {
                mobileMenu.classList.remove("active");
            }
        }

        // B. Close Profile Dropdowns if clicking outside
        const openDropdowns = document.querySelectorAll('.profile-dropdown-card.show');
        openDropdowns.forEach(menu => {
            const isDesktop = menu.id === 'profile-dropdown-desktop';
            const btnId = isDesktop ? 'profile-photo-desktop' : 'profile-photo-mobile';
            const btn = document.getElementById(btnId);

            if (!menu.contains(e.target) && (!btn || !btn.contains(e.target))) {
                menu.classList.remove("show");
            }
        });
    });

    // =========================================
    // 5. ANIMATION LOGIC 
    // =========================================
    const animatedElements = document.querySelectorAll('.animate-on-load, .animate-on-scroll');

    if (animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animatedElements.forEach(el => {
            observer.observe(el);
        });
    }


    // =========================================
    // 6. TOAST NOTIFICATIONS
    // =========================================

    // --- 1. HANDLE DJANGO MESSAGES (Login/Logout/Errors) ---
    const toast = document.getElementById("toast-box");

    if (toast) {
        // Check if it's a success or error message to set the border color
        const text = toast.innerText.toLowerCase();
        if (text.includes("success") || text.includes("successfully")) {
            toast.style.borderLeft = "5px solid #4CAF50"; // Green
        } else {
            toast.style.borderLeft = "5px solid #f44336"; // Red
        }

        // Auto-hide after 4 seconds
        setTimeout(() => {
            toast.style.opacity = "0";
            setTimeout(() => toast.style.display = "none", 500);
        }, 4000);
    }

    // --- 2. HANDLE 3-DAY PREMIUM SUGGESTION ---
    checkPremiumSuggestion();

    function checkPremiumSuggestion() {
        const FIRST_VISIT_KEY = 'quizolve_first_visit';
        const PREMIUM_DISMISSED_KEY = 'quizolve_premium_dismissed';

        let firstVisit = localStorage.getItem(FIRST_VISIT_KEY);
        const now = new Date().getTime();

        if (!firstVisit) {
            localStorage.setItem(FIRST_VISIT_KEY, now);
        } else {
            const daysPassed = (now - parseInt(firstVisit)) / (1000 * 60 * 60 * 24);

            // Show if 3 days passed OR if you want to test it immediately
            if (daysPassed >= 3 && !localStorage.getItem(PREMIUM_DISMISSED_KEY)) {
                showPremiumToast();
            }
        }
    }

    function showPremiumToast() {
        const premiumToast = document.createElement('div');
        premiumToast.className = 'toast-message premium-toast';
        premiumToast.innerHTML = `
            <div class="toast-content">
                // <div style="display:flex; align-items:center;">
                //     <i class="fas fa-crown" style="color: #FFD700; margin-right:10px;"></i>
                //     <span>Unlock unlimited quizzes!</span>
                // </div>
                <div style="display:flex; align-items:center;">
                    <button onclick="window.location.href='/checkout/'" class="btn-buy">Upgrade</button>
                    <i class="fas fa-times close-toast" onclick="this.closest('.toast-message').remove(); localStorage.setItem('quizolve_premium_dismissed', 'true');"></i>
                </div>
            </div>
        `;
        document.body.appendChild(premiumToast);
    }

    // Call this function on your "Start Quiz" button click
    function startQuizAttempt(event) {
        // A. Check if user is Premium (Optional: checks for a body class or global var)
        // If you render <body class="is-premium"> for paid users, this works automatically.
        const isPremium = document.body.classList.contains('is-premium');
        if (isPremium) return true;

        // B. Setup Local Storage Keys
        const today = new Date().toISOString().split('T')[0]; // "2023-10-27"
        const storageKey = 'quizolve_daily_limit';

        // C. Get Data
        let data = JSON.parse(localStorage.getItem(storageKey)) || { date: today, count: 0 };

        // D. Reset if it's a new day
        if (data.date !== today) {
            data = { date: today, count: 0 };
        }

        // E. STOP if limit reached (Max 3)
        if (data.count >= 3) {
            event.preventDefault(); // Stop the server request
            showLimitToast();       // Show the "Fire" popup
            return false;
        }

        // F. Increment and Save
        data.count++;
        localStorage.setItem(storageKey, JSON.stringify(data));
        return true; // Allow the link to work
    }
});
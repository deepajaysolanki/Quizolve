document.addEventListener("DOMContentLoaded", () => {
    const stats = document.querySelectorAll('.stat-value');

    stats.forEach(stat => {
        // Read the target number from HTML
        const target = +stat.getAttribute('data-target');
        const suffix = stat.getAttribute('data-suffix') || "+"; // Adds '+' or '%'
        
        const duration = 2000; // Animation time (2 seconds)
        const increment = target / (duration / 20); 

        let current = 0;

        const updateCount = () => {
            current += increment;

            if (current < target) {
                // Show increasing number
                stat.innerText = Math.ceil(current).toLocaleString();
                setTimeout(updateCount, 20);
            } else {
                // Animation Done: Show Final Number
                stat.innerText = target.toLocaleString() + suffix;
            }
        };

        updateCount();
    });
});

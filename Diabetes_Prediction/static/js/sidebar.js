document.getElementById("logout-btn").addEventListener("click", function() {
        
    localStorage.clear();
    window.location.replace("http://127.0.0.1:8000/login")

});

document.addEventListener("DOMContentLoaded", () => {
    // 1. Get the exact path the user is currently on (e.g., "/history")
    const currentPath = window.location.pathname;

    // 2. Select all links in your sidebar
    const sidebarLinks = document.querySelectorAll('.sidebar-link');

    // 3. Loop through each link
    sidebarLinks.forEach(link => {
        // Get the href attribute of the link (e.g., "/history")
        const linkPath = link.getAttribute('href');

        // 4. If the link matches the current URL, light it up!
        if (currentPath === linkPath) {
            link.classList.add('active');
        } 
        else {
            link.classList.remove('active'); // Ensure others are turned off
        }
    });
});
(function () {
    function checkAuth() {
        const token = localStorage.getItem("token");

        function redirectToLogin(msg) {
            if (msg) alert(msg);
            localStorage.removeItem("token");
            window.location.replace("/login");
        }

        if (!token) {
            redirectToLogin("Please log in.");
            return;
        }

        try {
            const payload = JSON.parse(atob(token.split(".")[1]));
            
            // 1. Check expiration
            if (payload.exp * 1000 < Date.now()) {
                redirectToLogin("Session expired.");
                return;
            }

            // 2. Check role permission
            if (payload.role !== "admin") {
                alert("Unauthorized access. Admin privileges required.");
                window.location.replace("/home");
                return;
            }
        }
        catch (e) {
            redirectToLogin("Invalid session token.");
        }
    }

    // Run immediately on page script load
    checkAuth();

    // Run on pageshow to catch bfcache / back button transitions
    window.addEventListener("pageshow", function (event) {
        checkAuth();
    });
})();

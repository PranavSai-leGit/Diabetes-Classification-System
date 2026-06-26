document.getElementById("logout-btn").addEventListener("click", function() {
        
    localStorage.clear();
    window.location.replace("http://127.0.0.1:8000/login")

});
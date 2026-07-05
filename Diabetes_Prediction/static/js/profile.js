document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    if (!token || isTokenExpired(token)) {
        localStorage.removeItem("token");
        alert("Session expired.");
        window.location.replace("/login");
}
});
function isTokenExpired(token) {
        const payload = JSON.parse(atob(token.split(".")[1]));

        return payload.exp * 1000 < Date.now();
    }

function redirectToLogin() {
    alert("Session expired. Please log in again.");
    window.location.replace("/login");
}
document.addEventListener("DOMContentLoaded", () => {
    fetchUserProfile();
});

async function fetchUserProfile() {
    const info = document.getElementById("profile-info");

    const [response, predictions_positive, predictions_negative] = await Promise.all([
        fetch("/profile", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        }),

        fetch("/history?page=1&limit=1&status=Diabetic", {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        }),

        fetch("/history?page=1&limit=1&status=Non-Diabetic", {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        })
    ]);

    if(!response.ok){
        throw new Error("Failed to fetch profile data");
    }   

    const data = await response.json();

    // Inject data with wireframe formatting
    info.innerHTML = `
        <div class="info-label">Username</div>
        <div class="info-value">${data.username}</div>
        
        <div class="info-label" style="margin-top: 10px;">Email</div>
        <div class="info-value">${data.email}</div>
    `;

    // Total Positives
    if (predictions_positive.ok) {
        const pred = await predictions_positive.json();
        document.getElementById("total_predictions").textContent = pred.meta.total_predictions;
        document.getElementById("total_positives").textContent = pred.meta.totalItems;
        document.getElementById("average_confidence").textContent = `${(pred.meta.average_confidence*100).toFixed(1)}%`; 
    }
    // Total Negatives
    if (predictions_negative.ok) {
        const pred = await predictions_negative.json();
        document.getElementById("total_negatives").textContent = pred.meta.totalItems
    }
}
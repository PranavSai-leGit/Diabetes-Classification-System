document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    if (!token || isTokenExpired(token)) {
        localStorage.removeItem("token");
        alert("Session expired.");
        window.location.replace("/login");
        return;
    }

    fetchAdminDashboardData();
});

function isTokenExpired(token) {
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.exp * 1000 < Date.now();
    }
    catch (e) {
        return true;
    }
}

function redirectToLogin() {
    alert("Session expired. Please log in again.");
    window.location.replace("/login");
}

async function fetchAdminDashboardData() {
    const activeToken = localStorage.getItem("token");
    if (!activeToken || isTokenExpired(activeToken)) {
        localStorage.removeItem("token");
        redirectToLogin();
        return;
    }

    try {
        const response = await fetch("/admin/dashboard-data", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${activeToken}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem("token");
                redirectToLogin();
                return;
            }
            throw new Error("Failed to fetch dashboard data");
        }

        const data = await response.json();

        // 1. Update Metrics
        document.getElementById("total-users").textContent = data.metrics.total_users;
        document.getElementById("total-predictions").textContent = data.metrics.total_predictions;
        document.getElementById("active-today").textContent = data.metrics.active_users_today;
        document.getElementById("new-users-week").textContent = data.metrics.new_users_this_week;
        document.getElementById("avg-confidence").textContent = `${data.metrics.average_confidence}%`;
        document.getElementById("model-version").textContent = data.metrics.model_version;

        // 2. Render Tables
        populateRecentActivity(data.recent_activity);
        populateRecentPredictions(data.recent_predictions);
        populateRecentUsers(data.recent_users);

        // 3. Render Charts
        renderSignupChart(data.signups_trend);
        renderOutcomeChart(data.outcomes_distribution);

    } catch (error) {
        console.error(error);
        alert("An error occurred while loading dashboard metrics.");
    }
}

// Helper: Robust UTC ISO String Date Parser
function parseUTCDate(isoString) {
    if (!isoString) return new Date(NaN);
    // Check if the ISO string already has a timezone indicator (Z, +, or trailing -offset)
    const hasTimezone = isoString.includes("Z") || isoString.includes("+") || /-\d{2}:\d{2}$/.test(isoString);
    return new Date(hasTimezone ? isoString : isoString + "Z");
}

// Helper: Format ISO timestamp to relative time (e.g. "5 min ago", "2 hr ago", "Yesterday")
function formatRelativeTime(isoString) {
    if (!isoString) return "--";
    const now = new Date();
    const past = parseUTCDate(isoString);
    const diffMs = now - past;

    if (isNaN(diffMs)) return "--";

    const diffSec = Math.max(0, Math.floor(diffMs / 1000));
    const diffMin = Math.floor(diffSec / 60);
    const diffHr = Math.floor(diffMin / 60);
    const diffDays = Math.floor(diffHr / 24);

    if (diffSec < 60) return "Just now";
    if (diffMin < 60) return `${diffMin} min ago`;
    if (diffHr < 24) return `${diffHr} hr ago`;
    if (diffDays === 1) return "Yesterday";
    return `${diffDays} days ago`;
}

// Helper: Format Joined Date (e.g. "Today", "Yesterday", "Jul 6, 2026")
function formatJoinedTime(isoString) {
    if (!isoString) return "--";
    const now = new Date();
    const past = parseUTCDate(isoString);
    
    if (isNaN(past.getTime())) return "--";
    
    if (now.toDateString() === past.toDateString()) {
        return "Today";
    }
    
    const yesterday = new Date();
    yesterday.setDate(now.getDate() - 1);
    if (yesterday.toDateString() === past.toDateString()) {
        return "Yesterday";
    }
    
    return past.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function populateRecentPredictions(predictions) {
    const tbody = document.getElementById("recent-predictions-body");
    tbody.innerHTML = "";

    if (!predictions || predictions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: #94a3b8;">No predictions made yet.</td></tr>`;
        return;
    }

    predictions.forEach(p => {
        const row = document.createElement("tr");
        
        const resultColor = p.prediction === "Diabetic" ? "#f87171" : "#4ade80";
        const relativeTime = formatRelativeTime(p.created_at);

        row.innerHTML = `
            <td>${p.username}</td>
            <td style="color: ${resultColor}; font-weight: bold;">${p.prediction}</td>
            <td>${p.confidence}%</td>
            <td style="color: #94a3b8; font-size: 0.9rem;">${relativeTime}</td>
        `;
        tbody.appendChild(row);
    });
}

function populateRecentUsers(users) {
    const tbody = document.getElementById("recent-users-body");
    tbody.innerHTML = "";

    if (!users || users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: #94a3b8;">No users registered yet.</td></tr>`;
        return;
    }

    users.forEach(u => {
        const row = document.createElement("tr");
        const joinedText = formatJoinedTime(u.created_at);

        row.innerHTML = `
            <td>${u.username}</td>
            <td style="color: #94a3b8; font-size: 0.9rem;">${u.email}</td>
            <td>${joinedText}</td>
        `;
        tbody.appendChild(row);
    });
}

function renderSignupChart(trend) {
    const ctx = document.getElementById("signupChart").getContext("2d");
    
    // Sort trend dates chronological
    trend.sort((a, b) => new Date(a.date) - new Date(b.date));

    const labels = trend.map(t => {
        const d = new Date(t.date);
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    });
    const data = trend.map(t => t.count);

    // Create line gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, "rgba(167, 139, 250, 0.4)");
    gradient.addColorStop(1, "rgba(167, 139, 250, 0.0)");

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Signups',
                data: data,
                borderColor: '#a78bfa',
                borderWidth: 3,
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#a78bfa',
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { 
                        color: '#94a3b8',
                        stepSize: 1,
                        precision: 0
                    }
                }
            }
        }
    });
}

function renderOutcomeChart(distribution) {
    const ctx = document.getElementById("outcomeChart").getContext("2d");
    const diabetic = distribution.diabetic || 0;
    const nondiabetic = distribution.nondiabetic || 0;

    if (diabetic === 0 && nondiabetic === 0) {
        // Render empty state text inside canvas container if no outcomes
        ctx.font = "16px sans-serif";
        ctx.fillStyle = "#94a3b8";
        ctx.textAlign = "center";
        ctx.fillText("No prediction data available yet", 110, 110);
        return;
    }

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Diabetic', 'Non-Diabetic'],
            datasets: [{
                data: [diabetic, nondiabetic],
                backgroundColor: ['rgba(55, 255, 55, 0.68)', 'rgba(233, 42, 42, 0.69)'],
                borderColor: ['rgb(16, 114, 16)', 'rgb(145, 17, 17)'],
                borderRadius: 15,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#e2e8f0', boxWidth: 15 }
                }
            },
            cutout: '65%'
        }
    });
}

function populateRecentActivity(activity) {
    const tbody = document.getElementById("recent-activity-body");
    tbody.innerHTML = "";

    if (!activity || activity.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #94a3b8;">No activity logged yet.</td></tr>`;
        return;
    }

    activity.forEach(log => {
        const row = document.createElement("tr");
        
        let actionText = log.action;
        if (log.action === "update_profile") actionText = "Updated Profile";
        else if (log.action === "delete_user") actionText = "Deleted User";
        else if (log.action === "update_user_role") actionText = "Role Change";
        else if (log.action === "register_user") actionText = "User Registration";
        else if (log.action === "user_login") actionText = "User Login";
        else if (log.action === "admin_login") actionText = "Admin Login";
        else if (log.action === "failed_login_attempt") actionText = "Failed Login Attempt";
        else if (log.action === "create_prediction") actionText = "Created Prediction";

        const relativeTime = formatRelativeTime(log.timestamp);

        row.innerHTML = `
            <td><strong>${log.username}</strong></td>
            <td style="color: #60a5fa; font-weight: 500;">${actionText}</td>
            <td>${log.entity_type || "--"}</td>
            <td style="color: #94a3b8; font-size: 0.9rem;">${relativeTime}</td>
        `;
        tbody.appendChild(row);
    });
}

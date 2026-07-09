document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    function isTokenExpired(token) {
        if (!token)
            return true;

        try {
            const payload = JSON.parse(atob(token.split(".")[1]));
            return payload.exp * 1000 < Date.now();
        }
        catch (e) {
            return true;
        }
    }

    if (!token || isTokenExpired(token)) {
        localStorage.removeItem("token");
        alert("Session expired. Please log in again.");
        window.location.replace("/login");
        return;
    }

    try {
        // Parallel fetch for profile and the dashboard data endpoint
        const [profileRes, dashboardRes] = await Promise.all([
            fetch("/profile", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            }),
            fetch("/dashboard-data", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            })
        ]);

        if (profileRes.ok) {
            const user = await profileRes.json();
            const userInfoEl = document.getElementById("user-info");
            if (userInfoEl) userInfoEl.textContent = `Welcome back, ${user.username}`;
        } else {
            console.error("Failed to fetch profile:", await profileRes.text());
        }

        if (dashboardRes.ok) {
            const data = await dashboardRes.json();
            
            if (data.message === "No data available") {
                const userInfoEl = document.getElementById("user-info");
                if (userInfoEl) userInfoEl.textContent += " (No predictions yet)";
                return;
            }

            // 1. Inference Stats Top Row
            document.getElementById("total_predictions").textContent = data.stats?.total_predictions || 0;
            document.getElementById("average_confidence").textContent = `${data.stats?.average_confidence || 0}%`;
            document.getElementById("total_positives").textContent = data.stats?.total_positives || 0;
            document.getElementById("total_negatives").textContent = data.stats?.total_negatives || 0;

            const positive_percent = data.stats.total_predictions ? ((data.stats.total_positives / data.stats.total_predictions) * 100).toFixed(1) : 0;    
            const negative_percent = data.stats.total_predictions ? ((data.stats.total_negatives / data.stats.total_predictions) * 100).toFixed(1) : 0;

            // 1.5 Initialize the Main Prediction Chart (Doughnut)
            const predictionCanvas = document.getElementById('predictionChart');
            if (predictionCanvas) {
                const predictionCtx = predictionCanvas.getContext('2d');
                
                // Update the center text values
                document.getElementById('center-total').textContent = data.stats?.total_predictions || 0;
                document.getElementById('center-avg').textContent = `${data.stats?.average_confidence || 0}%`;

                new Chart(predictionCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Positive', 'Negative'],
                        datasets: [{
                            data: [positive_percent, negative_percent],
                            backgroundColor: ['rgba(11, 189, 11, 0.8)', 'rgba(241, 29, 29, 0.8)'],
                            borderColor: ['rgb(12, 121, 12)', 'rgb(145, 17, 17)'],
                            borderWidth: 1,
                            borderRadius: 50,
                            cutout: '80%'
                        }]
                    },
                    options: {
                        circumference: 180, 
                        rotation: 270,
                        cutout: '80%',             
                        maintainAspectRatio: false,
                        responsive: true,
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        return ` ${context.raw}%`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // 2. Recent Prediction
            if (data.latest_prediction) {
                document.getElementById("last_prediction").textContent = data.latest_prediction.prediction || "N/A";
                document.getElementById("confidence").textContent = `${data.latest_prediction.confidence || 0}%`;
                
                if (data.latest_prediction.created_at) {
                    let rawDate = data.latest_prediction.created_at;
                    if (rawDate && !rawDate.endsWith("Z") && !rawDate.includes("+")) {
                        rawDate += "Z";
                    }
                    const dateObj = new Date(rawDate);
                    document.getElementById("time-stamp").textContent = dateObj.toLocaleString();
                } else {
                    document.getElementById("time-stamp").textContent = "N/A";
                }
            }

            // 3. Risk Stacked Bar
            setTimeout(() => {
                if (data.risk_scores) {
                    document.getElementById('bar-low').style.width = `${data.risk_scores.low || 0}%`;
                    document.getElementById('bar-med').style.width = `${data.risk_scores.medium || 0}%`;
                    document.getElementById('bar-high').style.width = `${data.risk_scores.high || 0}%`;
                    document.getElementById('label-low').textContent = `${data.risk_scores.low || 0}%`;
                    document.getElementById('label-med').textContent = `${data.risk_scores.medium || 0}%`;
                    document.getElementById('label-high').textContent = `${data.risk_scores.high || 0}%`;
                }
            }, 100);

            // 4. Age Distribution
            setTimeout(() => {
                if (data.age_distribution) {
                    for(let i=1; i<=4; i++) {
                        const val = data.age_distribution[i-1] || 0;
                        const bar = document.getElementById(`age-${i}`);
                        const label = document.getElementById(`age-val-${i}`);
                        if (bar) bar.style.width = `${val}%`;
                        if (label) label.textContent = `${val}%`;
                    }
                }
            }, 200);

            // 5. Glucose by Age
            setTimeout(() => {
                if (data.glucose_by_age) {
                    const maxGluc = 200; 
                    for(let i=1; i<=4; i++) {
                        const val = data.glucose_by_age[i-1] || 0;
                        const bar = document.getElementById(`gluc-${i}`);
                        const label = document.getElementById(`gluc-val-${i}`);
                        if (bar) bar.style.width = `${Math.min((val/maxGluc)*100, 100)}%`;
                        if (label) label.textContent = val;
                    }
                }
            }, 300);

            // 6. BMI Categories
            setTimeout(() => {
                if (data.bmi_distribution) {
                    for(let i=1; i<=3; i++) {
                        const val = data.bmi_distribution[i-1] || 0;
                        const bar = document.getElementById(`bmi-${i}`);
                        const label = document.getElementById(`bmi-val-${i}`);
                        if (bar) bar.style.width = `${val}%`;
                        if (label) label.textContent = `${val}%`;
                    }
                }
            }, 400);

            // 7. Gender Doughnut Chart
            const genderCanvas = document.getElementById('genderChart');
            if (genderCanvas && data.gender_distribution) {
                const genderCtx = genderCanvas.getContext('2d');
                new Chart(genderCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Male', 'Female'],
                        datasets: [{
                            data: data.gender_distribution,
                            backgroundColor: ['rgba(17, 63, 138, 0.8)', 'rgba(184, 19, 101, 0.8)'],
                            borderColor: ['#3b82f6', '#ec4899'],
                            borderWidth: 1,
                            cutout: '75%'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom', labels: { color: '#e2e8f0', padding: 20 } }
                        }
                    }
                });
            }

            // 8. Scatter Plot
            const scatterCanvas = document.getElementById('scatterChart');
            if (scatterCanvas && data.scatter_data) {
                const scatterCtx = scatterCanvas.getContext('2d');
                new Chart(scatterCtx, {
                    type: 'scatter',
                    data: {
                        datasets: [
                            {
                                label: 'Positive',
                                data: data.scatter_data.positive || [],
                                backgroundColor: 'rgba(241, 29, 29, 0.8)',
                                borderColor: '#f87171',
                                pointRadius: 6,
                                pointHoverRadius: 8
                            },
                            {
                                label: 'Negative',
                                data: data.scatter_data.negative || [],
                                backgroundColor: 'rgba(14, 228, 14, 0.8)',
                                borderColor: '#4ade80',
                                pointRadius: 6,
                                pointHoverRadius: 8
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: { 
                                title: { display: true, text: 'Glucose Level (mg/dL)', color: '#94a3b8' },
                                grid: { color: 'rgba(255,255,255,0.05)' },
                                ticks: { color: '#cbd5e1' }
                            },
                            y: {
                                title: { display: false },
                                grid: { color: 'rgba(255,255,255,0.05)' },
                                min: -0.5,
                                max: 1.5,
                                ticks: {
                                    color: '#cbd5e1',
                                    stepSize: 1,
                                    callback: function(value) {
                                        if (value === 1) return 'Positive';
                                        if (value === 0) return 'Negative';
                                        return '';
                                    }
                                }
                            }
                        },
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: function(ctx) {
                                        return `Glucose: ${ctx.raw.x}, Result: ${ctx.raw.y === 1 ? 'Positive' : 'Negative'}`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // 9. Past Predictions Table
            const tbody = document.getElementById('history-table-body');
            if (tbody && data.recent_predictions) {
                tbody.innerHTML = ""; 
                data.recent_predictions.forEach(row => {
                    const tr = document.createElement('tr');
                    const isPos = row.result === 'Positive' || row.result === 'Diabetic' || row.result === '1';
                    const badgeClass = isPos ? 'badge-pos' : 'badge-neg';
                    const displayResult = isPos ? 'Positive' : 'Negative';
                    
                    tr.innerHTML = `
                        <td>${row.age || '-'}</td>
                        <td>${row.bmi || '-'}</td>
                        <td>${row.glucose || '-'}</td>
                        <td><span class="badge ${badgeClass}">${displayResult}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        } else {
            console.error("Dashboard API returned an error:", dashboardRes.status, await dashboardRes.text());
        }
    } catch (err) {
        console.error("Failed to load dashboard data. This is usually a network or server error:", err);
    }
});
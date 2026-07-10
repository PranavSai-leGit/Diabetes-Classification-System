let currentPage = 1;
const limit = 6;
let totalPages = 1;
let currentFilter = "All";
let currentSearch = "";

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    if (!token || isTokenExpired(token)) {
        localStorage.removeItem("token");
        window.location.replace("/login");
    } else {
        fetchHistory(currentPage);
    }
});

function isTokenExpired(token) {
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.exp * 1000 < Date.now();
    } catch(e) {
        return true;
    }
}

let searchTimeout;
function handleSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const inputVal = document.getElementById("search-username").value.trim();
        currentSearch = inputVal;
        currentPage = 1;
        fetchHistory(currentPage);
    }, 300);
}

function renderNoPredictionsFound(msg) {
    const tableBody = document.getElementById("predictions-table-body");
    tableBody.innerHTML = "";
    const pagination = document.getElementById("pagination-controls");
    pagination.style.display = "none";
    const errorMessage = document.getElementById("error-message");
    errorMessage.textContent = msg;
    errorMessage.style.display = "block";
    errorMessage.style.color = "#cbd5e1";
    errorMessage.style.textAlign = "center";
    errorMessage.style.margin = "10%";
}

function applyFilter() {
    const dropdown = document.getElementById("status-filter");
    if (dropdown) {
        currentFilter = dropdown.value;
    }
    currentPage = 1;
    fetchHistory(currentPage);
}

async function fetchHistory(page) {
    const tableBody = document.getElementById("predictions-table-body");
    const loadingMessage = document.getElementById("loading-message");
    const errorMessage = document.getElementById("error-message");
    const paginationControls = document.getElementById("pagination-controls");
    const token = localStorage.getItem("token");

    tableBody.innerHTML = "";
    errorMessage.style.display = "none";
    loadingMessage.style.display = "block";

    try {
        let url = `/admin_predictions?page=${page}&limit=${limit}`;
        if (currentSearch) {
            url += `&search=${encodeURIComponent(currentSearch)}`;
        }
        if (currentFilter !== "All") {
            url += `&status=${encodeURIComponent(currentFilter)}`;
        }
    
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
        });

        if (!response.ok) {
            throw new Error("Failed to fetch history data");
        }

        const result = await response.json();
        
        currentPage = result.meta.currentPage;
        totalPages = result.meta.totalPages;

        loadingMessage.style.display = "none";

        if (result.data.length === 0) {
            paginationControls.style.display = "none";
            errorMessage.textContent = currentSearch ? "No predictions matching that username found" : "No predictions found";
            errorMessage.style.display = "block";
            errorMessage.style.color = "#cbd5e1";
            errorMessage.style.textAlign = "center";
            errorMessage.style.margin = "10%";
            return;
        }

        paginationControls.style.display = "flex";
        const s_no = ((currentPage - 1) * limit) + 1;

        result.data.forEach((record, index) => {
            const row = document.createElement("tr");
            let rawDate = record.created_at;
            
            // Format timestamp safely
            let past;
            if (rawDate) {
                const hasTimezone = rawDate.includes("Z") || rawDate.includes("+") || /-\d{2}:\d{2}$/.test(rawDate);
                past = new Date(hasTimezone ? rawDate : rawDate + "Z");
            } else {
                past = new Date(NaN);
            }
            
            const formattedDate = isNaN(past.getTime()) ? "--" : past.toLocaleString();

            row.innerHTML = `
                <td>${s_no + index}</td>
                <td><strong>${record.username}</strong></td>
                <td>${record.prediction}</td>
                <td>${parseFloat((record.confidence * 100).toFixed(2))}%</td>
                <td>${formattedDate}</td>
            `;
            tableBody.appendChild(row);
        });

        document.getElementById("page-info").textContent = `Page ${currentPage} of ${totalPages}`;
        document.getElementById("prev-btn").disabled = (currentPage === 1);
        document.getElementById("next-btn").disabled = (currentPage === totalPages || totalPages === 0);

    } catch (error) {
        console.error("Error:", error);
        loadingMessage.style.display = "none";
        errorMessage.textContent = "An error occurred while loading history.";
        errorMessage.style.display = "block";
    }
}

function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage >= 1 && newPage <= totalPages) {
        fetchHistory(newPage);
    }
}
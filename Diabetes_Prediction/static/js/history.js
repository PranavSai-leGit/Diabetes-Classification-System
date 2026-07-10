// history.js
let currentPage = 1;
const limit = 6;
let totalPages = 1;
let currentFilter = "All";

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (!token || isTokenExpired(token)) {
        localStorage.removeItem("token");
        window.location.replace("/login");
    } else {
        fetchHistory(currentPage);
    }
});

function isTokenExpired(token) {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
}

function applyFilter() {
    // Make sure you have a <select id="status-filter"> in your HTML!
    const dropdown = document.getElementById("status-filter");
    if (dropdown) {
        currentFilter = dropdown.value;
    }
    currentPage = 1; // Always reset to page 1 when applying a new filter
    fetchHistory(currentPage);
}

async function fetchHistory(page) {
    const tableBody = document.getElementById("history-table-body");
    const loadingMessage = document.getElementById("loading-message");
    const errorMessage = document.getElementById("error-message");
    const paginationControls = document.getElementById("pagination-controls");
    const token = localStorage.getItem("token");

    tableBody.innerHTML = "";
    errorMessage.style.display = "none";
    errorMessage.textContent = "";

    try{
        
        let url = `/history?page=${page}&limit=${limit}`;
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

        // To hide loading message
        loadingMessage.style.display = "none";

        if (result.data.length === 0){
            if (paginationControls) {
                paginationControls.style.display = "none";
            }
            errorMessage.textContent = "No past predictions found";
            errorMessage.style.display = "block";
            errorMessage.style.color = "#cbd5e1";
            errorMessage.style.textAlign = "center";
            errorMessage.style.margin = "10%";
            return;
        }

        if (paginationControls) {
            paginationControls.style.display = "flex";
        }
        s_no = ((currentPage-1) * limit) + 1;

        result.data.forEach((record, index) => {
            const row = document.createElement("tr");
            let rawDate = record.created_at;
            if (rawDate && !rawDate.endsWith("Z") && !rawDate.includes("+")) {
                rawDate += "Z";
            }
            const dateObj = new Date(rawDate);
            const formattedDate = dateObj.toLocaleString();

            row.innerHTML = `
            <td>${s_no + index}</td>
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
        errorMessage.textContent = "An error occurred while loading your history.";
        errorMessage.style.display = "block";
    }
}

function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage >= 1 && newPage <= totalPages) {
        fetchHistory(newPage);
    }
}
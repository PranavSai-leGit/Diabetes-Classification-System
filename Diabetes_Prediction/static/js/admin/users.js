let currentPage = 1;
const limit = 5;
let totalPages = 1;
let currentFilter = "All";
let searchQuery = "";

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (!token || isTokenExpired(token)) {
        localStorage.removeItem("token");
        window.location.replace("/login");
    } else {
        fetchUsers(currentPage);
    }
});

function isTokenExpired(token) {
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.exp * 1000 < Date.now();
    } catch (e) {
        return true;
    }
}

function redirectToLogin() {
    alert("Session expired. Please log in again.");
    window.location.replace("/login");
}

function applyFilter() {
    const dropdown = document.getElementById("status-filter");
    if (dropdown) {
        currentFilter = dropdown.value;
    }
    currentPage = 1;
    fetchUsers(currentPage);
}

let searchTimeout;
function handleSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        searchQuery = document.getElementById("search-username").value.trim();
        currentPage = 1;
        fetchUsers(currentPage);
    }, 300);
}

async function fetchUsers(page) {
    const tableBody = document.getElementById("users-table-body");
    const loadingMessage = document.getElementById("loading-message");
    const errorMessage = document.getElementById("error-message");
    const paginationControls = document.getElementById("pagination-controls");
    const token = localStorage.getItem("token");

    tableBody.innerHTML = "";
    errorMessage.style.display = "none";
    loadingMessage.style.display = "block";

    try {
        let url = `/users?page=${page}&limit=${limit}`;
        if (currentFilter !== "All") {
            url += `&status=${encodeURIComponent(currentFilter)}`;
        }
        if (searchQuery) {
            url += `&search=${encodeURIComponent(searchQuery)}`;
        }

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem("token");
                redirectToLogin();
                return;
            }
            throw new Error("Failed to fetch users");
        }

        const result = await response.json();
        currentPage = result.meta.currentPage;
        totalPages = result.meta.totalPages;

        loadingMessage.style.display = "none";

        if (result.data.length === 0) {
            paginationControls.style.display = "none";
            errorMessage.textContent = "No users found matching requirements.";
            errorMessage.style.display = "block";
            return;
        }

        paginationControls.style.display = "flex";
        const s_no = ((currentPage - 1) * limit) + 1;

        result.data.forEach((record, index) => {
            const row = document.createElement("tr");

            let rawDate = record.created_at;
            let past;
            if (rawDate) {
                const hasTimezone = rawDate.includes("Z") || rawDate.includes("+") || /-\d{2}:\d{2}$/.test(rawDate);
                past = new Date(hasTimezone ? rawDate : rawDate + "Z");
            } else {
                past = new Date(NaN);
            }
            const formattedDate = isNaN(past.getTime()) ? "--" : past.toLocaleDateString("en-GB", {
                day: "2-digit",
                month: "short",
                year: "numeric"
            });

            // Prevent null role crashes
            const userRole = (record.role || 'user').toLowerCase();

            row.innerHTML = `
                <td>${s_no + index}</td>
                <td><strong>${record.username}</strong></td>
                <td>${record.email}</td>
                <td>
                    <select class="role-select" onchange="updateRole(${record.id}, this.value)" style="width: 110px; padding: 6px 10px; border-radius: 12px; background: rgba(30, 49, 112, 0.84); border: 1px solid rgba(255, 255, 255, 0.2); color: #ffffff; outline: none; cursor: pointer; text-align-last: center;">
                        <option      value="user" ${userRole === 'user' ? 'selected' : ''}>USER</option>
                        <option value="admin" ${userRole === 'admin' ? 'selected' : ''}>ADMIN</option>
                    </select>
                </td>
                <td>${formattedDate}</td>
                <td>${record.total_predictions || 0}</td>
                <td style="text-align: center; vertical-align: middle;">
                    <button class="delete-user-btn" onclick="deleteUser(${record.id}, '${record.username}')" title="Delete">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            <line x1="10" y1="11" x2="10" y2="17"></line>
                            <line x1="14" y1="11" x2="14" y2="17"></line>
                        </svg>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });

        document.getElementById("page-info").textContent = `Page ${currentPage} of ${totalPages}`;
        document.getElementById("prev-btn").disabled = (currentPage === 1);
        document.getElementById("next-btn").disabled = (currentPage === totalPages || totalPages === 0);

    } catch (error) {
        console.error("Error fetching users:", error);
        loadingMessage.style.display = "none";
        errorMessage.textContent = "An error occurred while loading users.";
        errorMessage.style.display = "block";
    }
}

async function deleteUser(userId, username) {
    const token = localStorage.getItem("token");
    
    // Prevent delete self client-side check
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        const loggedInAdminId = parseInt(payload.sub);
        if (userId === loggedInAdminId) {
            alert("You cannot delete your own admin account.");
            return;
        }
    } catch (e) {
        console.error("Token decoding error", e);
    }

    if (!confirm(`Are you sure you want to delete user "${username}"? This action is permanent and will delete all associated predictions and logs.`)) {
        return;
    }

    try {
        const response = await fetch(`/users/${userId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert(`User "${username}" successfully deleted.`);
            fetchUsers(currentPage);
        } else {
            const errData = await response.json();
            alert(errData.detail || "Failed to delete user.");
        }
    }
    catch (error) {
        console.error("Delete user error:", error);
        alert("An error occurred while deleting the user.");
    }
}

async function updateRole(userId, newRole) {
    const token = localStorage.getItem("token");
    
    // Prevent self-demotion check client-side
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        const loggedInAdminId = parseInt(payload.sub);
        if (userId === loggedInAdminId && newRole !== "admin") {
            alert("You cannot demote your own admin account.");
            fetchUsers(currentPage);
            return;
        }
    } catch (e) {
        console.error("Token decoding error", e);
    }

    // Dynamic confirmation dialog
    if (!confirm(`Are you sure you want to change this user's role to ${newRole.toUpperCase()}?`)) {
        fetchUsers(currentPage);
        return;
    }

    try {
        const response = await fetch(`/users/${userId}/role`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ role: newRole })
        });

        if (response.ok) {
            alert("User role updated successfully.");
            fetchUsers(currentPage);
        } else {
            const errData = await response.json();
            alert(errData.detail || "Failed to update user role.");
            fetchUsers(currentPage);
        }
    } catch (error) {
        console.error("Update role error:", error);
        alert("An error occurred while updating the role.");
        fetchUsers(currentPage);
    }
}

function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage >= 1 && newPage <= totalPages) {
        fetchUsers(newPage);
    }
}

// Assign to window object to be globally accessible from inline event handlers
window.applyFilter = applyFilter;
window.handleSearch = handleSearch;
window.deleteUser = deleteUser;
window.updateRole = updateRole;
window.changePage = changePage;

const token = localStorage.getItem("token");

document.addEventListener("DOMContentLoaded", async () => {
    if (!token || isTokenExpired(token)) {
        localStorage.removeItem("token");
        alert("Session expired.");
        window.location.replace("/login");
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
    localStorage.removeItem("token");
    window.location.replace("/login");
}

document.addEventListener("DOMContentLoaded", () => {
    fetchUserProfile();

    // Bind event listeners for actions
    const saveBtn = document.getElementById("save-changes-btn");
    if (saveBtn) {
        saveBtn.addEventListener("click", saveChanges);
    }

    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", logout);
    }

    const deleteBtn = document.getElementById("delete-account-btn");
    if (deleteBtn) {
        deleteBtn.addEventListener("click", deleteAccount);
    }

    // Bind toggle password visibility
    const toggleBtn = document.getElementById("toggle");
    const passwordInput = document.getElementById("settings-password");
    const visEl = document.getElementById("vis");
    if (toggleBtn && passwordInput && visEl) {
        toggleBtn.addEventListener("click", () => {
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                visEl.textContent = "visibility";
            } else {
                passwordInput.type = "password";
                visEl.textContent = "visibility_off";
            }
        });
    }
});

async function fetchUserProfile() {
    const activeToken = localStorage.getItem("token");
    if (!activeToken || isTokenExpired(activeToken)) {
        localStorage.removeItem("token");
        redirectToLogin();
        return;
    }

    const info = document.getElementById("profile-info");

    try {
        const [response, predictions_positive, predictions_negative] = await Promise.all([
            fetch("/profile", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${activeToken}`
                }
            }),

            fetch("/history?page=1&limit=1&status=Diabetic", {
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${activeToken}`
                }
            }),

            fetch("/history?page=1&limit=1&status=Non-Diabetic", {
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${activeToken}`
                }
            })
        ]);

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem("token");
                redirectToLogin();
                return;
            }
            throw new Error("Failed to fetch profile data");
        }   

        const data = await response.json();

        // Inject data
        info.innerHTML = `
            <div class="info-label">Username</div>
            <div class="info-value">${data.username}</div>
            
            <div class="info-label" style="margin-top: 10px;">Email</div>
            <div class="info-value">${data.email}</div>
        `;

        const roleBadge = document.getElementById("user-role-badge");
        if (roleBadge) {
            roleBadge.textContent = data.role;
            roleBadge.className = `role-badge ${data.role.toLowerCase()}-role`;
        }
        // Total Positives
        if (predictions_positive.ok) {
            const pred = await predictions_positive.json();
            document.getElementById("total_predictions").textContent = pred.meta.total_predictions;
            document.getElementById("total_positives").textContent = pred.meta.totalItems;
            document.getElementById("average_confidence").textContent = `${(pred.meta.average_confidence * 100).toFixed(1)}%`; 
        }
        // Total Negatives
        if (predictions_negative.ok) {
            const pred = await predictions_negative.json();
            document.getElementById("total_negatives").textContent = pred.meta.totalItems;
        }
    } catch (error) {
        console.error(error);
    }
}

async function saveChanges() {
    const activeToken = localStorage.getItem("token");
    if (!activeToken || isTokenExpired(activeToken)) {
        localStorage.removeItem("token");
        redirectToLogin();
        return;
    }

    const usernameInput = document.getElementById("settings-username").value.trim();
    const emailInput = document.getElementById("settings-email").value.trim();
    const passwordInput = document.getElementById("settings-password").value;

    const errorDiv = document.getElementById("settings-error");
    if (errorDiv) {
        errorDiv.textContent = "";
        errorDiv.style.display = "none";
    }

    const payload = {};
    if (usernameInput)
        payload.username = usernameInput;
    if (emailInput)
        payload.email = emailInput;
    if (passwordInput)
        payload.password = passwordInput;

    if (Object.keys(payload).length === 0) {
        const msg = "Please enter at least one field to change.";
        if (errorDiv) {
            errorDiv.textContent = msg;
            errorDiv.style.display = "block";
        } else {
            alert(msg);
        }
        return;
    }

    // 1. Password validation (at least 8 chars, 1 number, 1 lowercase, 1 uppercase)
    if (passwordInput) {
        if (passwordInput.length < 8) {
            const msg = "Password must be at least 8 characters long.";
            if (errorDiv) {
                errorDiv.textContent = msg;
                errorDiv.style.display = "block";
            } else {
                alert(msg);
            }
            return;
        }
        const hasNumber = /\d/.test(passwordInput);
        const hasLowercase = /[a-z]/.test(passwordInput);
        const hasUppercase = /[A-Z]/.test(passwordInput);
        if (!hasNumber || !hasLowercase || !hasUppercase) {
            const msg = "Password must contain at least one number, one lowercase letter, and one uppercase letter.";
            if (errorDiv) {
                errorDiv.textContent = msg;
                errorDiv.style.display = "block";
            } else {
                alert(msg);
            }
            return;
        }
    }

    // 2. Email validation (allowed domains check)
    if (emailInput) {
        const allowedDomains = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "icloud.com"];
        const emailParts = emailInput.split('@');
        if (emailParts.length !== 2) {
            const msg = "Please enter a valid email address.";
            if (errorDiv) {
                errorDiv.textContent = msg;
                errorDiv.style.display = "block";
            } else {
                alert(msg);
            }
            return;
        }
        const emailDomain = emailParts[1].toLowerCase(); 
        if (!allowedDomains.includes(emailDomain)) {
            const msg = "Please use a valid Gmail, Hotmail, Yahoo, icloud, or Outlook account.";
            if (errorDiv) {
                errorDiv.textContent = msg;
                errorDiv.style.display = "block";
            } else {
                alert(msg);
            }
            return;
        }
    }

    try {
        const res = await fetch("/profile", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${activeToken}`
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert("Profile updated successfully!");
            // Clear inputs
            document.getElementById("settings-username").value = "";
            document.getElementById("settings-email").value = "";
            document.getElementById("settings-password").value = "";
            // Reload info
            fetchUserProfile();
            if (passwordInput) {
                alert("Password changed, Login again")
                redirectToLogin();
            }
        }
        else {
            if (res.status === 401) {
                localStorage.removeItem("token");
                redirectToLogin();
                return;
            }
            const err = await res.json();
            let errMsg = "Failed to update profile";
            if (err.detail) {
                if (Array.isArray(err.detail)) {
                    errMsg = err.detail.map(e => e.msg).join(", ");
                } else {
                    errMsg = err.detail;
                }
            }
            if (errorDiv) {
                errorDiv.textContent = errMsg;
                errorDiv.style.display = "block";
            } else {
                alert(`Error: ${errMsg}`);
            }
        }
    }
    catch (e) {
        console.error(e);
        const msg = "An error occurred. Please try again.";
        if (errorDiv) {
            errorDiv.textContent = msg;
            errorDiv.style.display = "block";
        } else {
            alert(msg);
        }
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.replace("/login");
}

async function deleteAccount() {
    if (!confirm("Are you absolutely sure you want to delete your account? This action is permanent and cannot be undone.")) {
        return;
    }

    const activeToken = localStorage.getItem("token");
    if (!activeToken || isTokenExpired(activeToken)) {
        localStorage.removeItem("token");
        redirectToLogin();
        return;
    }

    try {
        const res = await fetch("/profile", {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${activeToken}`
            }
        });

        if (res.status === 204) {
            alert("Your account has been deleted.");
            localStorage.removeItem("token");
            window.location.replace("/register");
        } else {
            if (res.status === 401) {
                localStorage.removeItem("token");
                redirectToLogin();
                return;
            }
            alert("Failed to delete account. Please try again.");
        }
    } catch (e) {
        console.error(e);
        alert("An error occurred. Please try again.");
    }
}

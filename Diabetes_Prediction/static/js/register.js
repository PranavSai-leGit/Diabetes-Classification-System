document.getElementById("toggle").addEventListener("click", function() {

    const password = document.getElementById("password");
    const vis = document.getElementById("vis");

    if(password.type === "password") {

        password.type = "text";
        vis.textContent = "visibility";
    } 
    else {

        password.type = "password";
        vis.textContent = "visibility_off";
    }

});
document.getElementById("toggle_2").addEventListener("click", function() {

    const password = document.getElementById("confirm-password");
    const vis_2 = document.getElementById("vis_2");

    if(password.type === "password") {

        password.type = "text";
        vis_2.textContent = "visibility";
    } 
    else {

        password.type = "password";
        vis_2.textContent = "visibility_off";
    }

});

document.getElementById("register-form").addEventListener("submit", async (e)=>{

    e.preventDefault();

    const username = document.querySelector("#username").value;
    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;
    const confirm_password = document.querySelector("#confirm-password").value;

    const errorElement = document.getElementById("error-message");
    errorElement.textContent = "";    

    if (password !== confirm_password){
        errorElement.textContent = "Password didn't match. Please try again";
        return;
    }

    const allowedDomains = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "icloud.com"];
    
    const emailParts = email.split('@');
    const emailDomain = emailParts[1].toLowerCase(); 

    if (!allowedDomains.includes(emailDomain)) {
        errorElement.textContent = "Please use a valid Gmail, Hotmail, Yahoo, icloud, or Outlook account.";
        return; // Stop the form from submitting
    }

    const response = await fetch("/register",{
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            email: email,
            password: password
        }),
    });

    const data = await response.json();

    if(!response.ok) {
        errorElement.textContent = data.detail;
        return;
    }
    if(response.ok){
        window.location.replace("http://127.0.0.1:8000/login");
    }

});
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

document.getElementById("register-form").addEventListener("submit", async (e)=>{

    e.preventDefault();

    const username = document.querySelector("#username").value;
    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;

    const errorElement = document.getElementById("error-message");
    errorElement.textContent = "";    

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
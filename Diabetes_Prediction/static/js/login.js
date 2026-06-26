document.getElementById("toggle")
.addEventListener("click", function() {

    const password =
        document.getElementById("password");

    const vis =
        document.getElementById("vis");

    if (password.type === "password") {

        password.type = "text";

        vis.textContent = "visibility";

    } else {

        password.type = "password";

        vis.textContent = "visibility_off";

    }

});

document.getElementById("login-form").addEventListener("submit", async (e)=>{
    
    e.preventDefault();

    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;

    const errorElement = document.getElementById("error-message");
    errorElement.textContent = "";    

    const response = await fetch("/login",{
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            username: email,
            password: password
        })
    });

    const data = await response.json();

    if(!response.ok) {
        errorElement.textContent = data.detail;
        return;
    }

    console.log(data)

    localStorage.setItem(
        "token",
        data.access_token
    );

    if(response.ok){
        window.location.replace("/predict");
    }
});


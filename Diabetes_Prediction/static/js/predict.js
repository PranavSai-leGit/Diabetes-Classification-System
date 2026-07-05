document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    if (!token || isTokenExpired(token)) {
        localStorage.removeItem("token");
        alert("Session expired. Please Login again");
        window.location.replace("/login");
}
});
function isTokenExpired(token) {

        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.exp * 1000 < Date.now();
    }

document.getElementById("predict-form").addEventListener("submit", async (e) => {
    
    e.preventDefault();

    const errorElement = document.getElementById("error-message");
    errorElement.textContent = "";

    const gender = document.querySelector("#gender").value;
    const age = Number(document.querySelector("#age").value);
    const hypertension = Number(document.querySelector('input[name="hypertension"]:checked').value);
    const heart_disease = Number(document.querySelector('input[name="heart_disease"]:checked').value);
    const smoking_history = document.querySelector("#smoking_history").value;
    const bmi = Number(document.querySelector("#bmi").value);
    const HbA1c_level = Number(document.querySelector("#HbA1c_level").value);   
    const blood_glucose_level = Number(document.querySelector("#blood_glucose_level").value);      

    const token = localStorage.getItem("token");

    if(!token){
        window.location.replace("http://127.0.0.1:8000/login");
        alert("Not Authenticated")
        return;
    }

    const response = await fetch("/predict",{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
            gender,
            age,
            hypertension,
            heart_disease,
            smoking_history,
            bmi,
            HbA1c_level,
            blood_glucose_level
        })
    });

    const data = await response.json();

    if (!response.ok) {

        if (Array.isArray(data.detail)) {
            errorElement.textContent = data.detail[0].msg;
        } 

        else {
            errorElement.textContent = data.detail;
        }

        return;
    }
    prediction = document.getElementById("prediction");
    prediction.innerHTML = `<strong>Prediction:</strong> ${data.prediction}<br>
                            <strong>Confidence:</strong> ${(data.confidence * 100).toFixed(2)}%`;


})

document.querySelectorAll('input[type="number"]').forEach(input => {

    input.addEventListener("keydown", e => {
        if (e.key === "-") {
            e.preventDefault();
        }
    });

    input.addEventListener("input", () => {
        if (Number(input.value) < 0) {
            input.value = "";
        }
    });

});

document.getElementById("predict-form").addEventListener("reset", function() {
    prediction = document.getElementById("prediction");
    prediction.innerHTML = "";
})
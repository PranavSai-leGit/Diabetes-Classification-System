document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    if (!token || isTokenExpired(token)) {
        localStorage.removeItem("token");
        alert("Session expired. Please Login again");
        window.location.replace("/login");
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

    if(!token || isTokenExpired(token)){
        localStorage.removeItem("token");
        window.location.replace("/login");
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
        } else {
            errorElement.textContent = data.detail;
        }
        return;
    }
    const predictionBox = document.getElementById("prediction");
    
    // 1. Determine Results Colors
    const resultColor = data.prediction === "Diabetic" ? "#f87171" : "#4ade80";

    // 2. BMI Level Assessment
    let bmiStatus = "Normal";
    let bmiColor = "#4ade80"; // Green
    if (bmi < 18.5) {
        bmiStatus = "Low (Underweight)";
        bmiColor = "#60a5fa"; // Blue
    } else if (bmi >= 25 && bmi < 30) {
        bmiStatus = "High (Overweight)";
        bmiColor = "#fbbf24"; // Yellow
    } else if (bmi >= 30) {
        bmiStatus = "Very High (Obese)";
        bmiColor = "#ef4444"; // Red
    }

    // 3. HbA1c Level Assessment
    let hba1cStatus = "Normal";
    let hba1cColor = "#4ade80";
    if (HbA1c_level >= 5.7 && HbA1c_level < 6.5) {
        hba1cStatus = "Elevated (Prediabetes)";
        hba1cColor = "#fbbf24";
    } else if (HbA1c_level >= 6.5) {
        hba1cStatus = "High (Diabetes Range)";
        hba1cColor = "#ef4444";
    }

    // 4. Glucose Level Assessment
    let glucoseStatus = "Normal";
    let glucoseColor = "#4ade80";
    if (blood_glucose_level >= 100 && blood_glucose_level < 140) {
        glucoseStatus = "Elevated (Borderline High)";
        glucoseColor = "#fbbf24";
    } else if (blood_glucose_level >= 140) {
        glucoseStatus = "High";
        glucoseColor = "#ef4444";
    }

    // 5. Suggestion Logic
    let suggestion = "";
    if (data.prediction === "Diabetic") {
        suggestion = "Consult with a healthcare provider immediately to develop a personalized care plan. Prioritize a low-glycemic index diet, engage in regular cardiovascular exercise, and establish a routine for monitoring your blood glucose levels.";
    } else {
        if (bmi >= 25 && blood_glucose_level >= 100) {
            suggestion = "Your model risk is low, but your BMI and blood glucose are elevated. Incorporate at least 150 minutes of moderate physical activity weekly and reduce refined sugar and carb intake to lower future risks.";
        } else if (bmi >= 25) {
            suggestion = "Your BMI is in the overweight or obese category. Aiming for a modest weight reduction (5-10%) through active lifestyle adjustments and portion control can substantially protect your long-term metabolic health.";
        } else if (blood_glucose_level >= 100 || HbA1c_level >= 5.7) {
            suggestion = "Some of your glycemic markers are slightly elevated. Focus on eating high-fiber foods, reducing sugary drinks, and consult a doctor to perform routine preventive screening.";
        } else {
            suggestion = "Excellent metrics! Maintain your active physical routine, consume a balanced diet rich in whole foods, and schedule annual standard checkups to sustain your healthy status.";
        }
    }

    // 6. Inject HTML layout and display
    predictionBox.innerHTML = `
        <div class="prediction-outcome" style="margin-bottom: 20px; text-align: center;">
            <span style="font-size: 1.1rem; color: #94a3b8; display: block; margin-bottom: 5px;">Risk Assessment</span>
            <span style="font-size: 1.8rem; font-weight: bold; color: ${resultColor};">${data.prediction}</span>
            <span style="display: block; font-size: 0.9rem; color: #94a3b8; margin-top: 5px;">Confidence: ${(data.confidence * 100).toFixed(2)}%</span>
        </div>

        <div class="health-summary" style="border-top: 1px solid rgba(255, 255, 255, 0.1); border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding: 15px 0; margin-bottom: 15px;">
            <h3 style="font-size: 1.1rem; margin-bottom: 12px; color: #ffffff;">Health Indicators Summary</h3>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.95rem;">
                <span style="color: #94a3b8;">BMI (${bmi.toFixed(1)}):</span>
                <span style="font-weight: 600; color: ${bmiColor};">${bmiStatus}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.95rem;">
                <span style="color: #94a3b8;">HbA1c (${HbA1c_level.toFixed(1)}%):</span>
                <span style="font-weight: 600; color: ${hba1cColor};">${hba1cStatus}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 0.95rem;">
                <span style="color: #94a3b8;">Blood Glucose (${blood_glucose_level} mg/dL):</span>
                <span style="font-weight: 600; color: ${glucoseColor};">${glucoseStatus}</span>
            </div>
        </div>

        <div class="suggestion-section">
            <h3 style="font-size: 1.1rem; margin-bottom: 8px; color: #60a5fa;">Personalized Suggestion</h3>
            <p style="font-size: 0.95rem; color: #e2e8f0; line-height: 1.4;">${suggestion}</p>
        </div>
    `;
    predictionBox.style.display = "block";

    // Auto-scroll to the bottom of the container so the user sees the summary
    const container = document.querySelector(".predict-container");
    if (container) {
        setTimeout(() => {
            container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
        }, 100);
    }
});

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
    const predictionBox = document.getElementById("prediction");
    predictionBox.innerHTML = "";
    predictionBox.style.display = "none";
});

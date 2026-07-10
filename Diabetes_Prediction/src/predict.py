import joblib
from pathlib import Path
from src.preprocessing import (
    handling_outliers,
    handle_missing_values,
    feature_engineering,
    encode_features
)
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "artifacts" / "diabetes_model.pkl"
FEATURE_COLUMNS_PATH = BASE_DIR / "artifacts" / "feature_columns.pkl"


model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURE_COLUMNS_PATH)


def preprocess_prediction_data(df):

    df = handle_missing_values(df)

    df = handling_outliers(df, target_column=None)

    df = feature_engineering(df)

    df = encode_features(df, fit=False)

    for col in feature_columns:

        if col not in df.columns:
            df[col] = 0

    df = df[feature_columns]

    return df


def predict(df):

    # Preprocessing input data
    processed_data = preprocess_prediction_data(df)

    # Model predicions
    probability = model.predict_proba(processed_data)
    prediction = int(probability[0][1] >= 0.25)

    return {
        "prediction": "Diabetic" if prediction == 1 else "Non-Diabetic",
        "confidence": float(probability[0][prediction])
    }


if __name__ == "__main__":
    import pandas as pd
    new_data = pd.DataFrame([{
        "gender": "Male",
        "age": 70,
        "hypertension": 1,
        "heart_disease": 1,
        "smoking_history": "current",
        "bmi": 30,
        "HbA1c_level": 6.5,
        "blood_glucose_level": 200
    }])
    print(predict(new_data))

import joblib
from preprocessing import (
    handling_outliers,
    handle_missing_values,
    feature_engineering,
    encode_features
)

model = joblib.load(r"Diabetes_Prediction\models\diabetes_model.pkl")
feature_columns = joblib.load("Diabetes_Prediction/models/feature_columns.pkl")


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
    probability = model.predict_proba(processed_data)[:, 1]
    prediction = (probability >= 0.25).astype(int)

    return {
        "prediction": int(prediction[0]),
        "probability": float(probability[0])
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

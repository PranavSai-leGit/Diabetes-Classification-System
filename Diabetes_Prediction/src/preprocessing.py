# Preprocessing.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from scipy.stats import zscore



def load_data(path: str):
    try:
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        print("Dataset not found")


def preprocess_data(df: pd.DataFrame):

    print(df.head())
    df.info()
    z1 = zscore(df["bmi"])
    z2 = zscore(df["age"])
    df = df[abs(z1) <= 3]
    df = df[abs(z2) <= 3]

    # Removing NULL values
    print(df.isnull().sum())
    df = df.dropna()

    # Removing duplicates
    print("Duplicates: ", df.duplicated().sum())
    df = df.drop_duplicates()

    # Encoding two features
    if "gender" in df.columns:
        gender_encoder = LabelEncoder()
        df["gender"] = gender_encoder.fit_transform(df["gender"])
    X = pd.get_dummies(X,drop_first=True)
    
    # FEATURE ENGINEERING
    if {'blood_glucose_level', 'age'}.issubset(df.columns):
        df["glucose_age"] = (df["blood_glucose_level"]*df["age"])

    if {'HbA1c_level', 'blood_glucose_level'}.issubset(df.columns):
        df["hba1c_glucose"] = (df["HbA1c_level"]*df["blood_glucose_level"])

    if {'bmi', 'HbA1c_level', 'blood_glucose_level'}.issubset(df.columns):
        df["bmi_HbA1c_level_blood_glucose_level"] = (df["blood_glucose_level"]*df["HbA1c_level"]*df["bmi"])


    # Feature and target split
    if "Outcome" in df.columns:
        X = df.drop(columns="Outcome")
        y = df["Outcome"]
    else:
        print("Target columns 'Outcome' not found")

    # Storing processed data
    try:
        df.to_csv(
            "Data/Processed/processed_data.csv",
            index=False
        )
    except Exception as e:
        print(f"Dataset not stored, Error: {e}")

    return X, y

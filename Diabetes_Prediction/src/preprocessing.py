# Preprocessing.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def load_data(path):

    df = pd.read_csv(path)
    return df

def preprocessing_data(df):

    # Removing NULL values
    df = df.dropna()

    # Encoding two features
    gender_encoder = LabelEncoder()
    df["gender"] = gender_encoder.fit_transform(df["gender"])

    smoking_encoder = LabelEncoder()
    df["smoking_history"] = smoking_encoder.fit_transform(df["smoking_history"])

    # Feature and target split
    X = df.drop(columns = "Outcome",axis = 1)
    y = df["Outcome"]

    # Storing processed data
    df.to_csv(
        "Data/Processed/processed_data.csv",
        index=False
    )
    
    return X, y
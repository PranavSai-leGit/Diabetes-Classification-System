from collections import Counter
from utils import load_data

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
os.system("cls")


# Handling missing values

def handle_missing_values(df):

    numeric_cols = df.select_dtypes(include=["number"]).columns

    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    return df


# Removing duplicates

def remove_duplicates(df):

    return df.drop_duplicates()


# Handling Outliers

def handling_outliers(df, target_column):

    numeric_cols = df.select_dtypes(include=["number"]).columns

    # REMOVE TARGET FROM OUTLIER PROCESSING
    numeric_cols = [col for col in numeric_cols if col != target_column]

    for col in numeric_cols:

        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        df[col] = df[col].clip(lower, upper)

    return df


# Encoding

def encode_features(df):

    categorical_cols = df.select_dtypes(include=["object"]).columns

    if len(categorical_cols) > 0:
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    return df


# Feature Engineering

def feature_engineering(df):

    df["BMI_Glucose"] = df["bmi"] * df["blood_glucose_level"]

    df["Age_BMI"] = df["age"] * df["bmi"]

    df["High_Glucose"] = (df["blood_glucose_level"] > 140).astype(int)

    df["Obese"] = (df["bmi"] >= 30).astype(int)

    df["Senior"] = (df["age"] >= 50).astype(int)

    return df


# Feature / Target split

def split_features_target(df, target_column):

    X = df.drop(columns=[target_column])

    y = df[target_column]

    return X, y


# Saving Processed Data

def save_processed_data(df):

    os.makedirs("Data/Processed", exist_ok=True)

    df.to_csv("Data/Processed/processed_data.csv", index=False)


# Master Function

def preprocess_data(df, target_column):

    if target_column not in df.columns:
        raise ValueError("Target column missing")
    
    df = handle_missing_values(df)

    df = remove_duplicates(df)

    df = handling_outliers(df, target_column)

    df = feature_engineering(df)

    df = encode_features(df)

    save_processed_data(df)

    X, y = split_features_target(df, target_column)

    return X, y


if __name__ == "__main__":
    df = load_data('diabetes_prediction_dataset.csv')
    preprocess_data(df, "Outcome")

